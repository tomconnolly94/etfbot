#!/usr/bin/python

# external dependencies
from investmentapp.src.Strategies.StockChoiceStrategies.StockChoiceStrategy import StockChoiceStrategy
from investmentapp.src.Strategies.StockChoiceStrategies.CustomWeightingStrategy import CustomWeightingStrategy
from investmentapp.src.Strategies.StockChoiceStrategies.StockChoiceStrategyEnum import StockChoiceStrategyEnum
from investmentapp.src.Strategies.StockChoiceStrategies.LinearWeightingStrategyCheapFirst import LinearWeightingStrategyCheapFirst
from investmentapp.src.Strategies.StockChoiceStrategies.LinearWeightingStrategyExpensiveFirst import LinearWeightingStrategyExpensiveFirst

# internal dependencies

"""
StockChoiceController

This is a class to allow the software to change its stock choice strategy

"""
class StockChoiceController():

    stockChoiceStrategyMap: 'dict[StockChoiceStrategyEnum, StockChoiceStrategy]' = {
        StockChoiceStrategyEnum.LinearWeightingCheapFirst: LinearWeightingStrategyCheapFirst,
        StockChoiceStrategyEnum.LinearWeightingExpensiveFirst: LinearWeightingStrategyExpensiveFirst,
        StockChoiceStrategyEnum.CustomWeighting: CustomWeightingStrategy
    }

    def __init__(self: object, stockChoiceStrategy: StockChoiceStrategyEnum):
        self._stockChoiceStrategy = self.stockChoiceStrategyMap[stockChoiceStrategy]()
        pass

    def getStockChoiceStrategy(self: object):
        return self._stockChoiceStrategy
