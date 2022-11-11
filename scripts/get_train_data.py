import requests



def get_train_details(train_number: int) -> dict:
    url = f"https://bahn.expert/api/hafas/v2/details/{train_number}"
    res = requests.get(url)

    """departure = res["departure"]
    platform = departure["platform"]
    scheduled_time = departure["scheduledTime"]
    time = departure["time"]
    delay = departure["delay"]
    # print(platform, scheduled_time, time, delay)
    """

    return res.json()
