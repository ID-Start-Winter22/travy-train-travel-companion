import json
import requests
import logging

from api_functions import get_train_data, load_json, write_json


def send_chatbot_message(conversation_id: str, intent_to_trigger: str, output_channel: str="latest") -> None:
    """ Triggers intent in order to automatically notify the user with the changed train data.
        :param str conversation_id: id of rasa conversation
        :param str intent_to_trigger: intent which need to get triggered in order to send a message
        :param str output_channel: channel to which the message should get send, default: lastest channel
    """

    trigger_intent_endpoint = f"http://localhost:5005/conversations/{conversation_id}/trigger_intent?output_channel={output_channel}"
    body = {
        "name": intent_to_trigger
    }
    
    res = requests.post(trigger_intent_endpoint, data=body)
    if res.status_code != 200:
        logging.error("[ERROR] Couldn't notify user with conservation id '{conversation_id}! Error code {response.status_code}.")
        return -1



def check_train_changes(user_data_path: str) -> None:
    """ Iterates over all conversations and check if data about the associated trains changed,
        if so, update the entries and notify the users.
        :param str user_data_path: path to the user data JSON file
    """

    # read user data JSON file
    user_data = load_json(user_data_path)

    # iterate over all train-user data and get train id
    for conversation_id in user_data:
        current_train_data = user_data[conversation_id]
        train_id = current_train_data["trainId"]

        # if the train was already cancelled, skip the train, TODO: delete entries of cancelled trains instead of skipping them
        if current_train_data["cancelled"]:
            continue

        # get data from train id
        new_train_data = get_train_data(train_id)

        # check if the train got cancelled
        if new_train_data["cancelled"]:
            current_train_data["cancelled"] = new_train_data["cancelled"]

            message = f"Achtung! Dein Zug fällt aus!"
            send(message)
            continue

        # check if the departure time changed
        if new_train_data["departure"]["time"] != current_train_data["actualDepartureTime"]:
            new_departure_time = new_train_data["departure"]["time"]
            departure_delay = new_train_data["departure"]["delay"]
            current_train_data["actualDepartureTime"] = new_departure_time
            current_train_data["departureDelay"] = departure_delay

            message = f"Achtung! Dein Zug hat um {departure_delay} Minuten Verspätung!\nNeue Abfahrtszeit: {new_departure_time}."
            send(message)

        # check if the arrival time changed
        if new_train_data["arrival"]["time"] != current_train_data["actualArrivalTime"]:
            new_arrival_time = new_train_data["arrival"]["time"]
            arrival_delay = new_train_data["arrival"]["delay"]
            current_train_data["actualArrivalTime"] = new_arrival_time
            current_train_data["arrivalDelay"] = arrival_delay

            message = f"Achtung! Dein Zug kommt {arrival_delay} Minuten später an!\nNeue Ankunftszeit: {new_arrival_time}."
            send(message)

        # check if the platorm changed
        if new_train_data["departure"]["platform"] != current_train_data["platform"]:
            new_platform = new_train_data["departure"]["platform"]
            current_train_data["platform"] = new_platform

            message = f"Achtung! Dein Gleis hat sich geändert.\nNeuer Gleis: {new_platform}."
            send(message)


