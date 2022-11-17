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

class ActionPrintTraindata(Action):

    def name(self) -> Text:
        return "action_print_traindata"


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
        #traindata = get_train_details(8000105)
        #traindata = requests.get('https://google.com/')
        #dispatcher.utter_message('Die Antwort lautet {}'.format(traindata))
        number = tracker.get_slot("train_id")
        if not number :
            dispatcher.utter_message("Ich kenne deinen Zug noch nicht.")
        else:
            dispatcher.utter_message(' Dein Zug ist {}'.format(number))

        return []
    
class ActionStoreTraindata(Action):

     def name(self) -> Text:
         return "action_store_traindata"
         
     def run(self, dispatcher, tracker, domain):
        username = tracker.get_slot("train_id")
        print("Sender ID: ", tracker.sender_id)

        return []

