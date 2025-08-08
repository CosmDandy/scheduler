import json
from typing import Dict


class LoadSchedule:
    """
    Класс импортирующий config.
    """

    def __init__(self, path) -> None:
        self.path = path

    def load(self):
        with open(self.path, "r", encoding="utf-8") as file:
            return json.load(file)


class LoadConfig:
    def __init__(self, path) -> None:
        self.path = path

    def load(self):
        with open(self.path, "r", encoding="utf-8") as file:
            config = json.load(file)
            grant_id = config["grant_id"]
            api_key = config["api_key"]
            api_uri = config["api_uri"]
            return grant_id, api_key, api_uri
