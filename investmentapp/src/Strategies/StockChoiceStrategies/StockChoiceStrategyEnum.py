from enum import Enum


class StockChoiceStrategyEnum(Enum):
    LinearWeightingCheapFirst = 1
    LinearWeightingExpensiveFirst = 2
    CustomWeighting = 2
