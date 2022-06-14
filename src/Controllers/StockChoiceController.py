#!/usr/bin/python

# external dependencies
from src.Interfaces.StockChoiceStrategies.CustomWeightingStrategy import CustomWeightingStrategy
from abc import ABC

# internal dependencies

"""
StockChoiceController

This is a class to allow the software to change its stock choice strategy

"""
class StockChoiceController(ABC):

    def __init__(self: object):
        self.stockChoiceStrategy = CustomWeightingStrategy()
        pass

    def getStockOrderNumbers(self, totalFunds: int):
        return self.stockChoiceStrategy.getStockOrderNumbers(totalFunds)