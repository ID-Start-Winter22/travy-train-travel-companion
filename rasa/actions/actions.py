from typing import Any, Text, Dict, List
from pyparsing import nestedExpr

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from .api_functions import get_train_data
import re

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
        # old entity extraction using rasa, didn't work, gonna delete soon I swear
        # train_id = tracker.get_slot("train_id")
        # train_id = next(tracker.get_latest_entity_values("train_id"), None)

        # get latest message sent by user
        current_state = tracker.current_state()
        latest_message = current_state["latest_message"]["text"]
        
        # find the train id provided by the user using regex, if not found stop function
        regex_result = re.findall("((ECE|ICE|EC|IC|RE|THA|RJ|FLX|HBX|WB|D|EN|NJ|DN|IRE|MEX|RE|FEX|RB|S)(\s|)(\d{1,5}))", latest_message)
        if len(regex_result) > 0:
            train_id = regex_result[0][0]
        else:
            dispatcher.utter_message("Tut mit leid, ich habe nicht verstanden welchen Zug du nehmen möchtest!")
            return []

        # fetch data from bahn.expert given the train id
        train_data = get_train_data(train_id)

        # if the train is not found, tell user
        if train_data == -1:
            dispatcher.utter_message(f"Tut mir leid, ich konnte den Zug '{train_id}' nicht finden!")
        else:
            response_message = f"Alles klar, ich informiere dich über den Zug '{train_data['train']['name']}'!\nZugdaten:\n" \
                                f" Von: {train_data['segmentStart']['title']}\n" \
                                f" Nach: {train_data['segmentDestination']['title']}\n" \
                                f" Abfahrtszeit: {train_data['departure']['scheduledTime']}\n" \
                                f" Ankunftszeit: {train_data['arrival']['scheduledTime']}\n"

            if "platform" in train_data["departure"]:
                response_message += f" Gleis: {train_data['departure']['platform']}"

            dispatcher.utter_message(response_message)

        # TODO store initial data

        return []

