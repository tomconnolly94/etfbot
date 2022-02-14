import requests
import os
from dotenv import load_dotenv
from Controllers.DataController import DataController

from Interfaces.AlpacaInterface import AlpacaInterface
from Interfaces.SP500IndexInterface import SP500IndexInterface

load_dotenv()

dataController = DataController()

dataController.getIndexSymbolsWithValues()