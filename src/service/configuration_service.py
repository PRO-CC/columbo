import json
from typing import Dict


class Configuration:

    configuration: Dict[str, any]

    def __init__(self):
        file = open("config.json", "r")
        self.configuration = json.load(file)
        file.close()

    def get_value(self, path: str) -> any:
        path = path.split(".")
        value = None

        for index, key in enumerate(path):
            if index == 0:
                value = self.configuration[key]
            else:
                if key.isnumeric():
                    value = value[int(key)]
                else:
                    value = value[key]

        return value


config = Configuration()
