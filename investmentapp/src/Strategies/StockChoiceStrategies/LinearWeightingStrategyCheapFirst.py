#!/usr/bin/python

# external dependencies

# internal dependencies
from investmentapp.src.Strategies.StockChoiceStrategies.LinearWeightingStrategy import LinearWeightingStrategy

"""
LinearWeightingStrategy

This is a StockChoiceStrategy that takes an ordered list of stocks applies a custom range limitation and buys one of each, looping to the start of the list until the available funds are depleted.

"""
class LinearWeightingStrategyCheapFirst(LinearWeightingStrategy):

    def __init__(self):
        self._reverseStockDataList = True
        super().__init__()

