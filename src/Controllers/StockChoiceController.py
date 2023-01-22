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
        # self._stockChoiceStrategy = CustomWightingStrategy()
        self._stockChoiceStrategy = LinearWeightingStrategy()
        pass

    def getStockChoiceStrategy(self: object):
        return self._stockChoiceStrategy
