import requests
import logging
import json
import os
from dateutil import parser 
from datetime import date, timedelta
import locale 

locale.getlocale()
locale.setlocale(locale.LC_TIME, "de_DE.UTF-8")

logging.basicConfig(format="%(asctime)s %(message)s")


# old endpoint: BASE_URL = "https://bahn.expert/api/journeys/v1"
BASE_URL = "https://bahn.expert/api/hafas/v2"


def get_train_data(train_id: str) -> dict:
    res = requests.get(f"{BASE_URL}/details/{train_id}")
    if res.status_code != 200:
        logging.error("[ERROR] Couldn't retrieve train information from train id '{train_id}! Error code {response.status_code}.")
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
    time = parser.parse(time) + timedelta(hours=1)

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
