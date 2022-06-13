#!/usr/bin/python

# external dependencies
from abc import ABC, abstractmethod

# internal dependencies

"""
StockChoiceStrategy

This is a an 'interface' for all stock choice strategies

"""
class StockChoiceStrategy(ABC):

    @abstractmethod
    def __init__():
        pass


    """
    `getStockOrderNumbers`: get numbers of each stock to be ordered according to the strategy
    """
    @abstractmethod
    def getStockOrderNumbers(self, stockSymbol: str, quantity: int) -> 'dict[str, int]':
        pass