import json
import requests
import logging
import json

from api_functions import get_train_data, load_json, write_json

logging.basicConfig(format="%(asctime)s %(message)s")


def trigger_chatbot_message(conversation_id: str, train_entity_type: str, train_entity_value: str, output_channel: str="latest") -> None:
    """ Triggers intent in order to automatically notify the user with the changed train data.
        :param str conversation_id: id of rasa conversation
        :param str output_channel: channel to which the message should get send, default: lastest channel
    """

    trigger_intent_endpoint = f"http://localhost:5005/conversations/{conversation_id}/trigger_intent?output_channel={output_channel}"
    body = {
        "name": "notify_train_data_change",
        "entities": {
            "train_entity_type": train_entity_type,
            "train_entity_value": train_entity_value
        }
    }
    
    res = requests.post(trigger_intent_endpoint, data=json.dumps(body))

    if res.status_code != 200:
        logging.error(f"[ERROR] Couldn't notify user with conservation id '{conversation_id}! Error code {res.status_code}, reason: {res.reason}")
        return -1



def check_train_changes(user_data_path: str) -> None:
    """ Iterates over all conversations and check if data about the associated trains changed,
        if so, update the entries and notify the users.
        :param str user_data_path: path to the user data JSON file
    """

    logging.info("[INFO] checking train data changes.")

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
        if "cancelled" in new_train_data:
            current_train_data["cancelled"] = new_train_data["cancelled"]

            trigger_chatbot_message(conversation_id, "cancellation", "")
            continue

        # check if the departure time changed
        if new_train_data["departure"]["time"] != current_train_data["actualDepartureTime"]:    
            new_departure_time = new_train_data["departure"]["time"]
            departure_delay = new_train_data["departure"]["delay"]
            current_train_data["actualDepartureTime"] = new_departure_time
            current_train_data["departureDelay"] = departure_delay

            # combine delay in minutes with time into one string
            departure_delay = f"{departure_delay};{new_departure_time}"

            trigger_chatbot_message(conversation_id, "departure_delay", departure_delay)

        # check if the arrival time changed
        if new_train_data["arrival"]["time"] != current_train_data["actualArrivalTime"]:
            new_arrival_time = new_train_data["arrival"]["time"]
            arrival_delay = new_train_data["arrival"]["delay"]
            current_train_data["actualArrivalTime"] = new_arrival_time
            current_train_data["arrivalDelay"] = arrival_delay

            # combine delay in minutes with time into one string
            arrival_delay = f"{arrival_delay};{new_arrival_time}"

            trigger_chatbot_message(conversation_id, "arrival_delay", arrival_delay)


        # check if the platorm changed
        if new_train_data["departure"]["platform"] != current_train_data["platform"]:
            new_platform = new_train_data["departure"]["platform"]
            current_train_data["platform"] = new_platform

            trigger_chatbot_message(conversation_id, "platform_change", new_platform)

        # store updated user-train entry
        write_json(user_data_path, conversation_id, current_train_data)



check_train_changes("../data/user_data.json")