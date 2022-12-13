from typing import Any, Text, Dict, List
from pyparsing import nestedExpr
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
import re
import json

from .api_functions import get_train_data, write_json, prettify_time



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
    

class ActionStoreTrainData(Action):
     def name(self) -> Text:
        return "action_store_train_data"
         
     def run(self, dispatcher, tracker, domain):
        # get latest message sent by user
        current_state = tracker.current_state()
        latest_message = current_state["latest_message"]["text"]
        
        # find the train id provided by the user using regex, if not found stop function
        regex_result = re.findall("((ECE|ICE|EC|IC|RE|THA|RJ|FLX|HBX|WB|D|EN|NJ|DN|IRE|MEX|RE|FEX|RB|S)(\s|)(\d{1,5}))", latest_message.upper())
        special_trains = {"train":["RE", "RB", "S"], 
                          "RE":{
                              "Baden-Württemberg":{},
                              "Bayern":{},
                              "Berlin":{},
                              "Brandenburg":{},
                              "Bremen":{},
                              "Hamburg":{},
                              "Hessen":{},
                              "Mecklenburg-Vorpommern":{},
                              "Niedersachsen":{},
                              "Nordrhein-Westfalen":{},
                              "Rheinland-Pfalz":{},
                              "Saarland":{},
                              "Sachsen":{},
                              "Sachsen-Anhalt":{},
                              "Schleswig-Holstein":{},
                              "Thüringen":{},
                              }, 
                          "RB":{
                              "Baden-Württemberg":{},
                              "Bayern":{},
                              "Berlin":{},
                              "Brandenburg":{},
                              "Bremen":{},
                              "Hamburg":{},
                              "Hessen":{},
                              "Mecklenburg-Vorpommern":{},
                              "Niedersachsen":{},
                              "Nordrhein-Westfalen":{},
                              "Rheinland-Pfalz":{},
                              "Saarland":{},
                              "Sachsen":{},
                              "Sachsen-Anhalt":{},
                              "Schleswig-Holstein":{},
                              "Thüringen":{},
                              },
                          "S":{
                              "Baden-Württemberg":{},
                              "Bayern":{},
                              "Berlin":{},
                              "Brandenburg":{},
                              "Bremen":{},
                              "Hamburg":{},
                              "Hessen":{},
                              "Mecklenburg-Vorpommern":{},
                              "Niedersachsen":{},
                              "Nordrhein-Westfalen":{},
                              "Rheinland-Pfalz":{},
                              "Saarland":{},
                              "Sachsen":{},
                              "Sachsen-Anhalt":{},
                              "Schleswig-Holstein":{},
                              "Thüringen":{},
                              }
                          }
        if len(regex_result) > 0:
            if regex_result[0][1] in special_trains["train"]:
                print(f"This is the special train: {regex_result[0][1]}")
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