import requests
import logging


logging.basicConfig(format="%(asctime)s %(message)s")


BASE_URL = "https://bahn.expert/api/hafas/v2"



def get_train_data(train_id: str) -> dict:
    res = requests.get(f"{BASE_URL}/details/{train_id}")
    if res.status_code != 200:
        logging.error("[ERROR] Couldn't retrieve train information from train id '{train_id}! Error code {response.status_code}.")
        return -1

    return res.json()


def get_train_data_cleaned(train_id: str) -> dict:
    """ Fetches data from the 'https://bahn.expert/api/hafas/v2/details/{train-id}' endpoint and returns a cleaned json object.

        :arg str train_id: id of train from which to fetch data, e.g. "ICE123"
        :return dict: cleaned json object     
    """

    response = requests.get(f"{BASE_URL}/details/{train_id}")

    if response.status_code != 200:
        logging.error("[ERROR] Couldn't retrieve train information from train id '{train_id}! Error code {response.status_code}.")
        return -1

    response = response.json()

    # remove keys
    response["departure"].pop("reihung", None)
    response["arrival"].pop("reihung", None)
    response.pop("finalDestination", None)
    response.pop("jid", None)
    response.pop("type", None)

    # rename keys
    response["departure"]["actualTime"] = response["departure"].pop("time", None)
    response["arrival"]["actualTime"] = response["arrival"].pop("time", None)
    response["crowdedness"] = response.pop("auslastung")
    response["startStation"] = response.pop("segmentStart", None)
    response["endStation"] = response.pop("segmentDestination", None)

    # add cancle key if not doesn't exist (if it doesn't exist it means it's not cancelled)
    if "cancelled" not in response:
        response["cancelled"] = False

    # add delay key if it doesn't exist (if it doesn't exist it means it's not dealyed)
    if "delay" not in response["departure"]:
        response["departure"]["delay"] = 0
    if "delay" not in response["arrival"]:
        response["arrival"]["delay"] = 0

    # convert travek duration from ms to hours
    response["duration"] = round(response["duration"] / 3.6e+6, 2)

    # move train name and line number to root level
    response["name"] = response["train"]["name"]
    response["line"] = response["train"]["line"]
    response.pop("train", None)

    # remove and rename keys from stop station data
    stops = []
    for station in response["stops"]:
        if "departure" in station:
            station["departure"].pop("reihung", None)
            station["departure"]["actualTime"] = station["departure"].pop("time", None)
            if "delay" not in station["departure"]:
                station["departure"]["delay"] = 0

        if "arrival" in station:
            station["arrival"].pop("reihung", None)
            station["arrival"]["actualTime"] = station["arrival"].pop("time", None)
            if "delay" not in station["arrival"]:
                station["arrival"]["delay"] = 0

        station["station"].pop("coordinates", None)
        station.pop("messages", None)
        station.pop("irisMessages", None)

        station["crowdedness"] = station.pop("auslastung", None)
        stops.append(station)
    response["stops"] = stops

    # collect only the messages without meta information
    messages = []
    for message in response["messages"]:
        messages.append(message["txtN"])
    response["messages"] = messages

    return response



# res = get_train_data("ICE62ßß1")
# print(res)

