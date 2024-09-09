import json
import os

from Types.ProgramConfiguration import ProgramConfiguration

# global
global programConfiguration


def getInstance():
    if not programConfiguration:
        programConfiguration = ProgramConfiguration()
    return programConfiguration


class ConfigurationController:

    def __init__(self):
        self.configFileName = "data/input.json"

        config = ConfigurationController.getConfigFileContents(os.getenv("CONFIG_FILE"))

        self.programConfiguration = ProgramConfiguration(
            config["stockExchange"],
            config["exchangeRangeTopIndex"],
            config["exchangeRangeBottomIndex"],
            config["divisionWeights"],
        )

    @classmethod
    def getConfigFileContents(self, fileName):
        with open(fileName) as fileHandle:
            return json.loads(fileHandle.read())
