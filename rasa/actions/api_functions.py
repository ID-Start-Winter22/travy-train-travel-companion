import requests
import logging
import json
import os
from dateutil import parser
from datetime import date, timedelta
import locale
from fuzzywuzzy import fuzz


locale.getlocale()
locale.setlocale(locale.LC_TIME, "de_DE.UTF-8")

logging.basicConfig(format="%(asctime)s %(message)s")


# old endpoint: BASE_URL = "https://bahn.expert/api/journeys/v1"
BASE_URL = "https://bahn.expert/api/hafas/v2"


def get_train_data(train_id: str) -> dict:
    res = requests.get(f"{BASE_URL}/details/{train_id}")
    if res.status_code != 200:
        print(res.reason)
        logging.error(f"[ERROR] Couldn't retrieve train information from train id '{train_id}! Error code {res.status_code}.")
        return -1

    return res.json()


def write_json(file_path: str, key: str, content: dict) -> None:
    if key == None:
        with open(file_path, "w") as f:
            json.dump(content, f, indent=4)
        return

    previous_content = {}
    if os.path.getsize(file_path) > 0:
        with open(file_path, "r") as f:
            previous_content = json.load(f)

    previous_content[key] = content
    with open(file_path, "w") as f:
        json.dump(previous_content, f, indent=4)


def load_json(file_path: str) -> dict:
    with open(file_path, "r") as f:
        return json.load(f)


def prettify_time(time: str) -> str:
    time = parser.parse(time)

    time_date = time.strftime("%Y-%m-%d")
    today = date.today()
    tomorrow = today + timedelta(days=1)
    date_tomorrow = tomorrow.strftime("%Y-%m-%d")
    date_today = today.strftime("%Y-%m-%d")

    if time_date == date_today:
        time_day_and_time = time.strftime("Heute (%d.%m.%Y) um %H:%M Uhr")
        return time_day_and_time
    elif time_date == date_tomorrow:
        time_day_and_time = time.strftime("Morgen (%d.%m.%Y) um %H:%M Uhr")
        return time_day_and_time
    else:    
        time_day_and_time = time.strftime("%A (%d.%m.%Y) um %H:%M Uhr")
        return time_day_and_time
    

def get_station_from_message(train_stops: dict, message: str, threshold: float) -> list[str]:
    found, station_scores = False, {}
    for stop in train_stops:
        station_name = stop["station"]["title"]
        fuzzy_score = fuzz.partial_ratio(station_name, message)

        if fuzzy_score > threshold * 100:
            found = True

        station_scores[station_name] = fuzzy_score

    if not found:
        return -1

    return [(k, v) for k, v in station_scores.items() if v == max(station_scores.values())]



def get_start_stop_stations(train_data: dict, start_station: str, stop_station: str) -> list[str]:
    all_fuzzy_scores_start, all_fuzzy_scores_stop = {}, {}
    for stop in train_data["stops"]:
        station_name = stop["station"]["title"]
        fuzzy_score_start = fuzz.partial_ratio(station_name, start_station)
        fuzzy_score_stop = fuzz.partial_ratio(station_name, stop_station)

        all_fuzzy_scores_start[station_name] = fuzzy_score_start
        all_fuzzy_scores_stop[station_name] = fuzzy_score_stop

    max_start = [(k, v) for k, v in all_fuzzy_scores_start.items() if v == max(all_fuzzy_scores_start.values())]
    max_stop = [(k, v) for k, v in all_fuzzy_scores_stop.items() if v == max(all_fuzzy_scores_stop.values())]

    return max_start, max_stop


"""train_data = get_train_data("ICE123")
# start_station, stop_station = get_start_stop_stations(train_data, "Arnhem", "Frankfurt")
station = get_station_from_message(train_data, "dfgdgdf Frankfurt gdfgdfg d gfflgdgfdg flughafen dfg dg dfgdf")
print(station)
"""