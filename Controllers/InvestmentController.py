#!/usr/bin/python

# external dependencies
from alpaca_trade_api.entity_v2 import SnapshotV2

# internal dependencies
from Controllers.DataController import DataController
from Interfaces.AlpacaInterface import AlpacaInterface


class InvestmentController:

    def __init__(self: object):
        self.alpacaInterface = AlpacaInterface()
        self.dataController = DataController()

    def assignStockWeights(stockList: list):
        pass

    def getOpenPositions(self):
        openPositions: list = self.alpacaInterface.getOpenPositions()

        print(openPositions)

    def generateDesiredStockWeightings(self):

        stocks = self.dataController.getOrderedStockData()
        for stock in stocks[0:10]:
            print(stock.__dict__)