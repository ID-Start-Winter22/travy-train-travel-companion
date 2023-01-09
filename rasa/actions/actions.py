from typing import Any, Text, Dict, List
from pyparsing import nestedExpr
from rasa_sdk import Action, Tracker, FormValidationAction
from rasa_sdk.events import SlotSet, FollowupAction
from rasa_sdk.executor import CollectingDispatcher
import re
import json

from .api_functions import get_train_data, write_json, load_json, prettify_time, get_station_from_message



class ActionPrintTrainId(Action):
    def name(self) -> Text:
        return "action_print_train_id"

    def run(self, dispatcher, tracker, domain):
        number = tracker.get_slot("train_id")
        if not number:
            dispatcher.utter_message("Ich kenne deinen Zug noch nicht.")
        else:
            dispatcher.utter_message("Dein Zug ist {}.".format(number))

        return []
   

class ActionReadTrainId(Action):
    def name(self) -> Text:
        return "action_read_train_id"

    def run(self, dispatcher, tracker, domain):
        # get latest message sent by user
        current_state = tracker.current_state()
        latest_message = current_state["latest_message"]["text"]
        
        # find the train id provided by the user using regex, if not found stop function
        regex_result = re.findall("((ECE|ICE|EC|IC|RE|THA|RJ|FLX|HBX|WB|D|EN|NJ|DN|IRE|MEX|RE|FEX|RB|S)(\s|)(\d{1,5}))", latest_message.upper())
        special_trains = {
            "train": ["RE", "RB", "S"],
        }

        if len(regex_result) > 0:
            if regex_result[0][1] in special_trains["train"]:
                dispatcher.utter_message(f"{regex_result[0][0]} ist eine Zuglinie, kein Zug. Zur Zeit habe ich dazu leider keine Informationen.")
                return []
            else:
                train_id = regex_result[0][0]
        else:
            dispatcher.utter_message("Tut mit leid, ich habe nicht verstanden welchen Zug du nehmen möchtest!")
            return []

        # fetch data from bahn.expert given the train id
        train_data = get_train_data(train_id)

        # if the train is not found, tell user
        if train_data == -1:
            dispatcher.utter_message(f"Tut mir leid, ich konnte den Zug {train_id} nicht finden!")
            return []

        # check if train is already cancelled
        cancelled = False
        if "cancelled" in train_data:
            if train_data["cancelled"]:
                cancelled = True
                dispatcher.utter_message(f"Oje! Dein Zug {train_id} fällt aus!")
                return []

        # create inital train data object and store all stops
        initial_train_data = {
            "trainId": train_id,
            "from": "",
            "to": "",
            "departureTime": "",
            "arrivalTime": "",
            "platform": "",
            "actualDepartureTime": "",
            "actualArrivalTime": "",
            "departureDelay": "",
            "arrivalDelay": "",
            "cancelled": cancelled,
            "stopStationNames": list(map(lambda station: station["station"]["title"], train_data["stops"])),
            "stops": train_data["stops"]
        }

        # store user and train data
        write_json("../data/user_data.json", tracker.sender_id, initial_train_data)

        return [SlotSet("departure_station", None), SlotSet("arrival_station", None), FollowupAction("stations_form")]

class ActionReturnStations(Action):
    def name(self) -> Text:
        return "action_return_stations"

    def run(self, dispatcher, tracker, domain):
        train_data = load_json("../data/user_data.json")
        if tracker.sender_id not in train_data:
            response_message = "Du hast noch keinen Zug gewählt, daher habe ich noch keine Stationen."
        else:
            response_message = "Folgende Stationen gibt es auf der Strecke:\n"
            response_message += ", ".join(train_data[tracker.sender_id]["stopStationNames"])

        dispatcher.utter_message(response_message)
        return []
   
    pass



class ValidateStationsForm(FormValidationAction):
    def name(self) -> Text:
        return "validate_stations_form"

    def confirm_train_data(self, train_data: dict, dispatcher) -> None:
        response_message = f"Alles klar, ich informiere dich über den Zug **{train_data['trainId']}**! Zugdaten:\n" \
                        f" **Von:** {train_data['from']}\n" \
                        f" **Nach:** {train_data['to']}\n" \
                        f" **Abfahrtszeit:** {prettify_time(train_data['departureTime'])}\n" \
                        f" **Ankunftszeit:** {prettify_time(train_data['arrivalTime'])}\n" \
                        f" **Gleis:** {train_data['platform']}\n"

        # answer user
        dispatcher.utter_message(response_message)

        # check if the train got cancelled and notify the user
        if train_data["cancelled"]:
            dispatcher.utter_message(f"**Achtung!** Der Zug {train_data['trainId']} fällt aus!")
            return

        about_changes_message = ""

        # check if there is a delay and nofity the user
        departure_delay = ""
        if train_data["departureDelay"]:
            departure_delay = train_data["departureDelay"]
            if departure_delay > 0:
                about_changes_message += f"**Abfahrtsverzögerung:** {departure_delay} Minuten! Neue Abfahrtszeit: {prettify_time(train_data['actualDepartureTime'])}.\n"
        
        arrival_delay = ""
        if train_data["arrivalDelay"]:
            arrival_delay = train_data["arrivalDelay"]
            if arrival_delay > 0:
                about_changes_message += f"**Ankunftsverzögerung:** {arrival_delay} Minuten! Neue Ankunftszeit: {prettify_time(train_data['actualArrivalTime'])}.\n"
        
        if len(about_changes_message) > 0:
                dispatcher.utter_message(about_changes_message)



    def validate_departure_station(self, slot_value: Any, dispatcher: CollectingDispatcher, tracker: Tracker, domain) -> Dict[Text, Any]:
        if slot_value == None:
            return { "departure_station": None }

        if tracker.latest_message['intent'].get('name') == "which_train_stations":
            response_message = "Folgende Stationen gibt es auf der Strecke:\n"
            train_data = load_json("../data/user_data.json")[tracker.sender_id]
            response_message += ", ".join(train_data["stopStationNames"])
            dispatcher.utter_message(response_message)
            return { "departure_station": None }

        train_data = load_json("../data/user_data.json")[tracker.sender_id]

        # get list of the possible station names and confidences the user could have meant (optimal only one station in list)
        departure_station_name = get_station_from_message(train_data["stops"], slot_value, threshold=0.6)

        # if it's -1 it means that the station name the user provided hasn't been found
        if departure_station_name == -1:

            # check if the user wanted to stop the process
            if tracker.latest_message['intent'].get('name') == "abort":
                dispatcher.utter_message(f"Okay! Du kannst gerne noch einmal versuchen mir deinen Zug mitzuteilen!")
                return { "requested_slot": None }

            dispatcher.utter_message(f"Hm, ich habe keine Station mit den Namen '{slot_value}' gefunden!.")
            return { "departure_station": None }

        # if more than one station was found, ask the user to specify which one s/he meant
        if len(departure_station_name) > 1:
            dispatcher.utter_message(f"Ich habe {len(departure_station_name)} ähnliche Stationen gefunden:\n \
                                    {', '.join([station_name[0] for station_name in departure_station_name])}.\n \
                                    Bitte sag mir den genaueren Namen der Station!")
            return { "departure_station": None }
        
        # get the station the user wanted
        departure_station_name = departure_station_name[0][0]

        # check if the station where the user wants to enter the train is the endstation and tell the user that it's not possible
        if train_data["stopStationNames"].index(departure_station_name) == len(train_data["stopStationNames"]) - 1:
            dispatcher.utter_message(f"Hm, die Station {departure_station_name} ist die Endstation, also kannst du dort nicht einsteigen.")
            return { "departure_station": None }

        # get the data about the station
        stop_data = list(filter(lambda station: station["station"]["title"] == departure_station_name, train_data["stops"]))[0]
        train_data["from"] = departure_station_name
        train_data["departureTime"] = stop_data["departure"]["scheduledTime"]
        train_data["actualDepartureTime"] = stop_data["departure"]["time"]

        if "platform" in stop_data["departure"]:
            train_data["platform"] = stop_data["departure"]["platform"]

        if "delay" in stop_data["departure"]:
            train_data["departureDelay"] = stop_data["departure"]["delay"]

        if "cancelled" in stop_data["departure"]:
            train_data["cancelled"] = stop_data["departure"]["cancelled"]

        write_json("../data/user_data.json", tracker.sender_id, train_data)

        return { "departure_station": slot_value }

    def validate_arrival_station(self, slot_value: Any, dispatcher: CollectingDispatcher, tracker: Tracker, domain) -> Dict[Text, Any]:
        if slot_value == None:
            return { "departure_station": None }

        if tracker.latest_message['intent'].get('name') == "which_train_stations":
            response_message = "Folgende Stationen gibt es auf der Strecke:\n"
            train_data = load_json("../data/user_data.json")[tracker.sender_id]
            response_message += ", ".join(train_data["stopStationNames"])
            dispatcher.utter_message(response_message)
            return { "arrival_station": None }

        train_data = load_json("../data/user_data.json")[tracker.sender_id]
    
        # get list of the possible station names and confidences the user could have meant (optimal only one station in list)
        arrival_station_name = get_station_from_message(train_data["stops"], slot_value, threshold=0.6)
    
        # if it's -1 it means that the station name the user provided hasn't been found
        if arrival_station_name == -1:

            # check if the user wanted to stop the process
            if tracker.latest_message['intent'].get('name') == "abort":
                dispatcher.utter_message(f"Okay! Du kannst gerne noch einmal versuchen mir deinen Zug mitzuteilen!")
                return { "requested_slot": None }

            dispatcher.utter_message(f"Hm, ich habe keine Station mit den Namen '{slot_value}' gefunden!")
            return { "arrival_station": None }

        # if more than one station was found, ask the user to specify which one s/he meant
        if len(arrival_station_name) > 1:
            dispatcher.utter_message(f"Ich habe {len(arrival_station_name)} ähnliche Stationen gefunden:\n \
                                    {', '.join([station_name[0] for station_name in arrival_station_name])}\n \
                                    Bitte sag mir den genaueren Namen der Station!")
            return { "arrival_station": None }
        
        # get the station the user wanted
        arrival_station_name = arrival_station_name[0][0]

        # check if the station where the user wants to leave the train is the start-station and tell the user that it's not possible
        if train_data["stopStationNames"].index(arrival_station_name) == 0:
            dispatcher.utter_message(f"Hm, die Station {arrival_station_name} ist die erste Station des Zuges, also kannst du dort nicht aussteigen.")
            return { "arrival_station": None }

        # check if the station where the user wants to leave the train is the same as the one s/he wants to enter and tell the user that it's not possible
        if train_data["stopStationNames"].index(arrival_station_name) == train_data["stopStationNames"].index(train_data["from"]):
            dispatcher.utter_message(f"Hm, du kannst nicht in der selben Station ein- und aussteigen!")
            return { "arrival_station": None }

        # check if the station where the user wants to leave the train is before the station s/he wants to enter and tell the user that it's not possible
        if train_data["stopStationNames"].index(arrival_station_name) < train_data["stopStationNames"].index(train_data["from"]):
            dispatcher.utter_message(f"Hm, die Station in der du aussteigen willst liegt vor der Station in der du einsteigst. Bitte gib die Stationen in richtiger Reihenfolge an!")
            return { "arrival_station": None }

        # get the data about the station
        stop_data = list(filter(lambda station: station["station"]["title"] == arrival_station_name, train_data["stops"]))[0]
        train_data["to"] = arrival_station_name
        train_data["arrivalTime"] = stop_data["arrival"]["scheduledTime"]
        train_data["actualArrivalTime"] = stop_data["arrival"]["time"]

        if "delay" in stop_data["arrival"]:
            train_data["arrivalDelay"] = stop_data["arrival"]["delay"]

        # save initial train information
        write_json("../data/user_data.json", tracker.sender_id, train_data)

        # if everything was successful, send message to the user confirming the train data
        self.confirm_train_data(train_data, dispatcher)

        return { "arrival_station": slot_value }



class ActionToTrigger(Action):
     def name(self) -> Text:
        return "action_train_data_change"
         
     def run(self, dispatcher, tracker, domain):
        train_entity_type = tracker.get_slot("train_entity_type")
        train_entity_value = tracker.get_slot("train_entity_value")

        if train_entity_type == "departure_delay":
            departure_delay, new_departure_time = train_entity_value.split(";")
            dispatcher.utter_message(f"**Achtung!** Dein Zug verspätet sich um {departure_delay} Minuten.\nNeue Abfahrtszeit: {prettify_time(new_departure_time)}.")

        elif train_entity_type == "arrival_delay":
            arrival_delay, new_arrival_time = train_entity_value.split(";")
            dispatcher.utter_message(f"**Achtung!** Deine Zugreise verlängert sich um {arrival_delay} Minuten.\nNeue Ankunftszeit: {prettify_time(new_arrival_time)}.")

        elif train_entity_type == "platform_change":
            dispatcher.utter_message(f"**Achtung!** Dein Gleis hat sich geändert.\nNeues Gleis: {train_entity_value}.")

        elif train_entity_type == "cancellation":
            dispatcher.utter_message(f"**Achtung!** Dein Zug fällt aus!")


 
"""
class ActionStoreTrainData(Action):
     def name(self) -> Text:
        return "action_store_train_data"
         
     def run(self, dispatcher, tracker, domain):
        # get latest message sent by user
        current_state = tracker.current_state()
        latest_message = current_state["latest_message"]["text"]
        
        # find the train id provided by the user using regex, if not found stop function
        regex_result = re.findall("((ECE|ICE|EC|IC|RE|THA|RJ|FLX|HBX|WB|D|EN|NJ|DN|IRE|MEX|RE|FEX|RB|S)(\s|)(\d{1,5}))", latest_message.upper())
        special_trains = ["RE", "RB", "S"]
        if len(regex_result) > 0:
            if regex_result[0][1] in special_trains:
                dispatcher.utter_message(f"{regex_result[0][0]} ist eine Zuglinie. Zur Zeit habe ich dazu leider keine Informationen.")
                return []
            else: train_id = regex_result[0][0]
        else:
            dispatcher.utter_message("Tut mit leid, ich habe nicht verstanden welchen Zug du nehmen möchtest!")
            return []

        # fetch data from bahn.expert given the train id
        train_data = get_train_data(train_id)

        # if the train is not found, tell user
        if train_data == -1:
            dispatcher.utter_message(f"Tut mir leid, ich konnte den Zug {train_id} nicht finden!")
            return []

        response_message = f"Alles klar, ich informiere dich über den Zug **{train_data['train']['name']}**! Zugdaten:\n" \
                            f" **Von:** {train_data['segmentStart']['title']}\n" \
                            f" **Nach:** {train_data['segmentDestination']['title']}\n" \
                            f" **Abfahrtszeit:** {prettify_time(train_data['departure']['scheduledTime'])}\n" \
                            f" **Ankunftszeit:** {prettify_time(train_data['arrival']['scheduledTime'])}\n"

        # check if 'platform' is in request body and append to message
        platform = ""
        if "platform" in train_data["departure"]:
            platform = train_data["departure"]["platform"]
            response_message += f" **Gleis:** {platform}\n"

        # answer user
        dispatcher.utter_message(response_message)

        # check if the train got cancelled and notify the user
        cancelled = False
        if "cancelled" in train_data:
            if train_data["cancelled"]:
                cancelled = True
                dispatcher.utter_message(f"Oje! Dein Zug {train_id} fällt aus!")
                return []

        about_changes_message = ""

        # check if 'delay' is in request body and append to message
        departure_delay, arrival_delay = "", ""
        if "delay" in train_data["departure"]:
            departure_delay = train_data["departure"]["delay"]
            if departure_delay > 0:
                about_changes_message += f"**Abfahrtsverzögerung:** {departure_delay} Minuten! Neue Abfahrtszeit: {prettify_time(train_data['departure']['time'])}.\n"
            
        if "delay" in train_data["arrival"]:
            arrival_delay = train_data["arrival"]["delay"]
            if arrival_delay > 0:
                about_changes_message += f"**Ankunftsverzögerung:** {arrival_delay} Minuten! Neue Ankunftszeit: {prettify_time(train_data['arrival']['time'])}.\n"
        
        if len(about_changes_message) > 0:
            dispatcher.utter_message(about_changes_message)

        # collect all important data from reuqest body
        cleaned_train_data = {
            "trainId": train_id,
            "from": train_data["segmentStart"]["title"],
            "to": train_data["segmentDestination"]["title"],
            "departureTime": train_data["departure"]["scheduledTime"],
            "arrivalTime": train_data["arrival"]["scheduledTime"],
            "platform": platform,
            "actualDepartureTime": train_data["departure"]["time"],
            "actualArrivalTime": train_data["arrival"]["time"],
            "departureDelay": departure_delay,
            "arrivalDelay": arrival_delay,
            "cancelled": cancelled,
        }

        # store user and train data
        write_json("../data/user_data.json", tracker.sender_id, cleaned_train_data)

        return []
"""



""" TO BE DELETED
class ActionReadStation(Action):
    def name(self) -> Text:
        return "action_read_station"

    def run(self, dispatcher, tracker, domain):
        # get latest message sent by user
        dispatcher.utter_message("Super!")
        return []
        current_state = tracker.current_state()
        latest_message = current_state["latest_message"]["text"]
        
        train_data = load_json("../data/user_data.json")[tracker.sender_id]
        station_name = get_station_from_message(train_data["stops"], latest_message)[0]
        stop_data = filter(lambda station: station["station"]["title"] == station_name, train_data["stops"])

        if train_data["departureStation"] != "":            
            train_data["from"] = station_name
            train_data["departureTime"] = stop_data["departure"]["scheduledTime"]
            train_data["actualDepartureTime"] = stop_data["departure"]["time"]

            if "platform" in train_data["departure"]:
                train_data["platform"] = stop_data["departure"]["platform"]

            if "delay" in train_data["arrival"]:
                train_data["departureDelay"] = stop_data["departure"]["delay"]

            write_json("../data/user_data.json", tracker.sender_id, train_data)

            dispatcher.utter_message("Und wo steigst du aus?")
        else:            
            train_data["to"] = station_name
            train_data["arrivalTime"] = stop_data["arrival"]["scheduledTime"]
            train_data["actualArrivalTime"] = stop_data["arrival"]["time"]

            if "delay" in train_data["arrival"]:
                train_data["arrivalDelay"] = stop_data["arrival"]["delay"]

            write_json("../data/user_data.json", tracker.sender_id, train_data)

            response_message = f"Alles klar, ich informiere dich über den Zug **{train_data['trainId']}**! Zugdaten:\n" \
                            f" **Von:** {train_data['from']}\n" \
                            f" **Nach:** {train_data['to']}\n" \
                            f" **Abfahrtszeit:** {prettify_time(train_data['departureTime']['scheduledTime'])}\n" \
                            f" **Ankunftszeit:** {prettify_time(train_data['arrivalTime']['scheduledTime'])}\n" \
                            f" **Glies:** {train_data['platform']}\n"

            # answer user
            dispatcher.utter_message(response_message)

            # check if the train got cancelled and notify the user
            if train_data["cancelled"]:
                dispatcher.utter_message(f"Oje! Dein Zug {train_data['trainId']} fällt aus!")
                return []

            about_changes_message = ""

            # check if there is a delay and nofity the user
            departure_delay, arrival_delay = "", ""
            if train_data["departureDelay"]:
                departure_delay = train_data["departureDelay"]
                if departure_delay > 0:
                    about_changes_message += f"**Abfahrtsverzögerung:** {departure_delay} Minuten! Neue Abfahrtszeit: {prettify_time(train_data['departure']['time'])}.\n"
                
            if train_data["arrivalDelay"]:
                arrival_delay = train_data["departureDelay"]
                if arrival_delay > 0:
                    about_changes_message += f"**Ankunftsverzögerung:** {arrival_delay} Minuten! Neue Ankunftszeit: {prettify_time(train_data['arrival']['time'])}.\n"
            
            if len(about_changes_message) > 0:
                dispatcher.utter_message(about_changes_message)


class ActionReadStations(Action):
    def name(self) -> Text:
        return "action_read_stations"

    def run(self, dispatcher, tracker, domain):
        # get latest message sent by user
        # current_state = tracker.current_state()
        # latest_message = current_state["latest_message"]["text"]
        dispatcher.utter_message("Got it!")

        train_data = load_json("../data/user_data.json")[tracker.sender_id]

        # set departure information
        given_departure_station_name = tracker.get_slot("departure_station")
        departure_station_name = get_station_from_message(train_data["stops"], given_departure_station_name)[0]

        stop_data = filter(lambda station: station["station"]["title"] == departure_station_name, train_data["stops"])

        train_data["from"] = departure_station_name
        train_data["departureTime"] = stop_data["departure"]["scheduledTime"]
        train_data["actualDepartureTime"] = stop_data["departure"]["time"]

        if "platform" in train_data["departure"]:
            train_data["platform"] = stop_data["departure"]["platform"]

        if "delay" in train_data["arrival"]:
            train_data["departureDelay"] = stop_data["departure"]["delay"]

        # set arrival information
        given_arrival_station_name = tracker.get_slot("arrival_station")
        arrival_station_name = get_station_from_message(train_data["stops"], given_arrival_station_name)[0]

        stop_data = filter(lambda station: station["station"]["title"] == arrival_station_name, train_data["stops"])

        train_data["to"] = arrival_station_name
        train_data["arrivalTime"] = stop_data["arrival"]["scheduledTime"]
        train_data["actualArrivalTime"] = stop_data["arrival"]["time"]

        if "delay" in train_data["arrival"]:
            train_data["arrivalDelay"] = stop_data["arrival"]["delay"]

        # save initial train information
        write_json("../data/user_data.json", tracker.sender_id, train_data)

        response_message = f"Alles klar, ich informiere dich über den Zug **{train_data['trainId']}**! Zugdaten:\n" \
                        f" **Von:** {train_data['from']}\n" \
                        f" **Nach:** {train_data['to']}\n" \
                        f" **Abfahrtszeit:** {prettify_time(train_data['departureTime']['scheduledTime'])}\n" \
                        f" **Ankunftszeit:** {prettify_time(train_data['arrivalTime']['scheduledTime'])}\n" \
                        f" **Glies:** {train_data['platform']}\n"

        # answer user
        dispatcher.utter_message(response_message)

        # check if the train got cancelled and notify the user
        if train_data["cancelled"]:
            dispatcher.utter_message(f"Oje! Dein Zug {train_data['trainId']} fällt aus!")
            return []

        about_changes_message = ""

        # check if there is a delay and nofity the user
        departure_delay, arrival_delay = "", ""
        if train_data["departureDelay"]:
            departure_delay = train_data["departureDelay"]
            if departure_delay > 0:
                about_changes_message += f"**Abfahrtsverzögerung:** {departure_delay} Minuten! Neue Abfahrtszeit: {prettify_time(train_data['departure']['time'])}.\n"
            
        if train_data["arrivalDelay"]:
            arrival_delay = train_data["departureDelay"]
            if arrival_delay > 0:
                about_changes_message += f"**Ankunftsverzögerung:** {arrival_delay} Minuten! Neue Ankunftszeit: {prettify_time(train_data['arrival']['time'])}.\n"
        
        if len(about_changes_message) > 0:
                dispatcher.utter_message(about_changes_message)"""


