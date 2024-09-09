#!/usr/bin/python

# external dependencies
from abc import ABC, abstractmethod
from typing import Callable, List
import logging

# internal dependencies
from investmentapp.src.Types.StockData import StockData
from investmentapp.src.Interfaces.DatabaseInterface import DatabaseInterface


"""
StockChoiceStrategy

This is a an 'interface' for all stock choice strategies

"""


class StockChoiceStrategy(ABC):

    def __init__(self, stockListInterface):
        if stockListInterface:
            self._stockListInterface = stockListInterface
        pass

    """
    `getBuyOrders`: get numbers of each stock to be ordered according to the strategy
    """

    @abstractmethod
    def getBuyOrders(
        self, quantity: int, existingPositions: "dict[str, int]"
    ) -> "dict[str, int]":
        pass

    """
    `getSellOrders`: get numbers of each stock to be ordered according to the strategy
    """

    @abstractmethod
    def getSellOrders(self, quantity: int) -> "list[str]":
        pass

    """
    `getStockRange`: gets a full list of stock on exchange and applies the filterfunction
                    returning the result
    """

    def _getStockRange(
        self, filterFunction: Callable[[List[StockData]], List[StockData]]
    ) -> List[StockData]:
        filteredStockList = filterFunction(self._stockListInterface.getStockCache())
        excludedStockSymbolList = DatabaseInterface().getExcludedStockRecords()
        filteredStockList = [
            stock
            for stock in filteredStockList
            if stock.symbol not in excludedStockSymbolList
        ]
        return filteredStockList
