# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


# This is a simple example for a custom action which utters "Hello World!"

from typing import Any, Text, Dict, List
from pyparsing import nestedExpr

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
import requests


class ActionPrintTrainId(Action):
    def name(self) -> Text:
        return "action_print_train_id"

    def run(self, dispatcher, tracker, domain):
        number = tracker.get_slot("train_id")
        if not number:
            dispatcher.utter_message("Ich kenne deinen Zug noch nicht.")
        else:
            dispatcher.utter_message(' Dein Zug ist {}'.format(number))

        return []
    

class ActionStoreTrainId(Action):

     def name(self) -> Text:
         return "action_store_train_id"
         
     def run(self, dispatcher, tracker, domain):
        number = tracker.get_slot("train_id")
        print("Sender ID: ", tracker.sender_id)

        return []

