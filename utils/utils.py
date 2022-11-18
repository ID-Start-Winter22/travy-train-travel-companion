import json


def load_json(file_path: str) -> dict:
    with open(file_path, "r") as f:
        return json.load(f)


def write_json(file_path: str, content: dict) -> None:
    with open(file_path, "w") as f:
        json.dump(content, f, indent=4)