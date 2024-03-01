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
        super().__init__(self._alpacaInterface)
        if not hasattr(self, '_reverseStockDataList'):
            self._reverseStockDataList = False


    """
    `getBuyOrders`: returns a dictionary of stock symbols mapped to the number of shares of that stock to buy  
    test: LinearWeightingStrategy.test_getBuyOrders
    """
    def getBuyOrders(self: object, availableFunds: int, existingPositions: 'dict[str, int]') -> 'dict[str, int]':
        stockDataList = self._getStockRangeIdeal()
        if self._reverseStockDataList:
            stockDataList.reverse()
        stockDataList = self._reorderStockDataListBasedOnExistingPositions(stockDataList, existingPositions)
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
        
    
    def _reorderStockDataListBasedOnExistingPositions(self, stockDataList: 'list[StockData]', existingPositions: 'dict[str, int]'):

        # sortedSymbols = sorted(existingPositions.keys(), key=lambda k: existingPositions[k])

        # return sortedSymbols
        
        largestExistingPositionSize: int = 0
        positionSizeMap: 'dict[int, list[StockData]]' = {}
        reorderedStockList: 'list[StockData]' = []

        for stockData in stockDataList:

            positionSize = 0
            if stockData.symbol not in existingPositions:
                positionSize = 0
            else:
                positionSize = existingPositions[stockData.symbol]

            if positionSize > largestExistingPositionSize:
                largestExistingPositionSize = positionSize

            if positionSize not in positionSizeMap:
                positionSizeMap[positionSize] = []

            positionSizeMap[positionSize].append(stockData)
        
        # concat lists in order of their position size
        for i in range(largestExistingPositionSize + 1):
            if i not in positionSizeMap: continue
            reorderedStockList += positionSizeMap[i]

        return reorderedStockList


    """
    `_getStockRangeIdeal`:  returns a limited list (StockData) of the ideal stocks to 
                            invest in based on the filter function provided
    """
    def _getStockRangeIdeal(self: object) -> 'list[StockData]':
        filterFunction = lambda stockDataList : stockDataList[self._idealStockRangeIndexStart:self._idealStockRangeIndexEnd]
        return super()._getStockRange(filterFunction)


    def _getBuyingQuantities(self: object, funds: float, stockDataList: 'list[StockData]') -> 'dict[str, int]':
        
        buyingQuantities = {}

        while True:

            ordersAddedOnThisLoop = 0

            for stock in stockDataList:
                logging.debug(f"stock: {stock.symbol}: {stock.price}")
                logging.debug(f"funds: {funds}")

                

                if funds < stock.price: continue

                logging.debug(f"funds > stock.price")

                # import sys
                # sys.exit()

                if stock.symbol not in buyingQuantities:
                    buyingQuantities[stock.symbol] = 1
                else:
                    buyingQuantities[stock.symbol] += 1
                ordersAddedOnThisLoop += 1
                funds = funds - stock.price
            
            if ordersAddedOnThisLoop == 0:
                return buyingQuantities
