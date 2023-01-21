#!/usr/bin/python

# external dependencies
from src.Strategies.StockChoiceStrategies.CustomWeightingStrategy import CustomWeightingStrategy
from src.Strategies.StockChoiceStrategies.LinearWeightingStrategy import LinearWeightingStrategy

# internal dependencies

"""
StockChoiceController

This is a class to allow the software to change its stock choice strategy

"""
class StockChoiceController():

    def __init__(self: object):
        self.stockChoiceStrategy = LinearWeightingStrategy()
        pass

    def getStockOrderNumbers(self, totalFunds: int):
        return self.stockChoiceStrategy.getStockOrderNumbers(totalFunds)