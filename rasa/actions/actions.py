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


# NOTE(Michael): We could use this action to store the name in
#                the TrackerStore (in memory database) or a persitent DB
#                such as MySQL. But we need to store a key-value pair 
#                to identify the user by id eg. (user_id, slotvalue)
class ActionStoreUserName(Action):

     def name(self) -> Text:
         return "action_store_name"
         
     def run(self, dispatcher, tracker, domain):
        username = tracker.get_slot("username")
        print("Sender ID: ", tracker.sender_id)

        return []


class ActionUserName(Action):

     def name(self) -> Text:
         return "action_get_name"

     def run(self, dispatcher, tracker, domain):
        username = tracker.get_slot("username")
        if not username :
            dispatcher.utter_message(" Du hast mir Deinen Namen nicht gesagt.")
        else:
            dispatcher.utter_message(' Du bist {}'.format(username))

        return []

class ActionPrintBahnData(Action):

    def name(self) -> Text:
        return "action_print_bahndata"


    def run(self, dispatcher, tracker, domain):
        """def get_train_details(train_number: int) -> dict:
            url = f"https://bahn.expert/api/hafas/v2/details/{train_number}"
            res = requests.get(url)

            departure = res["departure"]
            platform = departure["platform"]
            scheduled_time = departure["scheduledTime"]
            time = departure["time"]
            delay = departure["delay"]
            # print(platform, scheduled_time, time, delay)
            
            return res.json()"""
        #bahndata = get_train_details(8000105)
        bahndata = requests.get('https://google.com/')
        dispatcher.utter_message('Die Antwort lautet {}'.format(bahndata))

        return []
