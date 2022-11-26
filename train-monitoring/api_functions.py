import requests
import logging
import json
import os


logging.basicConfig(format="%(asctime)s %(message)s")


BASE_URL = "https://bahn.expert/api/journeys/v1"



def get_train_data(train_id: str) -> dict:
    res = requests.get(f"{BASE_URL}/details/{train_id}")
    if res.status_code != 200:
        logging.error("[ERROR] Couldn't retrieve train information from train id '{train_id}! Error code {response.status_code}.")
        return -1

    return res.json()


def write_json(file_path: str, key: str, content: dict) -> None:
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

# res = get_train_data("ICE62ßß1")
# print(res)

