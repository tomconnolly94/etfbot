#!/usr/bin/python

# external dependencies
import logging
import math

# internal dependencies
from src.Interfaces.AlpacaInterface import AlpacaInterface
from src.Strategies.StockChoiceStrategies.StockChoiceStrategy import StockChoiceStrategy
from src.Types.StockData import StockData

"""
LinearWeightingStrategy

This is a StockChoiceStrategy that takes an ordered list of stocks applies a custom range limitation and buys one of each, looping to the start of the list until the available funds are depleted.

"""
class LinearWeightingStrategy(StockChoiceStrategy):

    def __init__(self):
        # class fields
        self._idealStockRangeIndexStart = 300
        self._idealStockRangeIndexEnd = 400
        self._divisionWeights = [32, 22, 14, 10, 8, 6, 4, 2, 1.5, .5]
        self._alpacaInterface = AlpacaInterface()
        if not hasattr(self, '_reverseStockDataList'):
            self._reverseStockDataList = False


    """
    `getBuyOrders`: returns a dictionary of stock symbols mapped to the number of shares of that stock to buy  
    test: LinearWeightingStrategy.test_getBuyOrders
    """
    def getBuyOrders(self: object, availableFunds: int) -> 'dict[str, int]':
        stockDataList = self._getStockRangeIdeal()
        if self._reverseStockDataList:
            stockDataList.reverse()
        return self._getBuyingQuantities(availableFunds, stockDataList)


    """
    `getSellOrders`: returns a dictionary of stock symbols mapped to the number of shares of that stock to buy  
    test: TestStockChoiceController.test_getSellOrders
    """
    def getSellOrders(self: object) -> 'list[str]':
        stockCurrentlyOwned: 'dict[str, int]' = self._alpacaInterface.getOpenPositions()
        fullStockRange: 'list[StockData]' = self._alpacaInterface.getStockCache()

        return [ stockSymbol for stockSymbol in list(stockCurrentlyOwned.keys())
            if self.getPositionInStockDataList(stockSymbol, fullStockRange) > self._idealStockRangeIndexEnd]

    
    def getPositionInStockDataList(self, stockSymbol: str, stockDataList: list[StockData]):

        index = 0

        for stock in stockDataList:
            if stockSymbol == stock.symbol: 
                return index
            index += 1
        return 999
        


    """
    `_getStockRangeIdeal`:  returns a limited list (StockData) of the ideal stocks to 
                            invest in
    """
    def _getStockRangeIdeal(self: object) -> 'list[StockData]':
        return self._alpacaInterface.getStockCache()[self._idealStockRangeIndexStart:self._idealStockRangeIndexEnd]


    def _getBuyingQuantities(self: object, funds: float, stockDataList: 'list[StockData]') -> 'dict[str, int]':
        
        buyingQuantities = {}

        while True:

            ordersAddedOnThisLoop = 0

            for stock in stockDataList:

                if funds < stock.price: continue

                if stock.symbol not in buyingQuantities:
                    buyingQuantities[stock.symbol] = 1
                else:
                    buyingQuantities[stock.symbol] += 1
                ordersAddedOnThisLoop += 1
                funds = funds - stock.price
            
            if ordersAddedOnThisLoop == 0:
                return buyingQuantities
