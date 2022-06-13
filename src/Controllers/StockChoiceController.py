#!/usr/bin/python

# external dependencies
from src.Interfaces.StockChoiceStrategies.CustomWeightingStrategy import CustomWeightingStrategy
from abc import ABC

# internal dependencies

"""
StockChoiceController

This is a class to contain numerical information about how funds are distributed 
among stocks

"""
class StockChoiceController(ABC):

    def __init__(self: object):
        self.stockChoiceStrategy = CustomWeightingStrategy()
        pass

    def getStockOrderNumbers(self, totalFunds: int):
        return self.stockChoiceStrategy.getStockOrderNumbers(totalFunds)