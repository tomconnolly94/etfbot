#!/usr/bin/python

# external dependencies
import logging
import math

# internal dependencies
from src.Interfaces.AlpacaInterface import AlpacaInterface
from src.Strategies.StockChoiceStrategies.StockChoiceStrategy import StockChoiceStrategy
from src.Types.StockData import StockData

"""
CustomWeightingStrategy

This is a StockChoiceStrategy that takes a custom weighting configuration and a range of stocks and reccomends stock based on applying the configuration to the stock range
The strategy is as follows:
    * Use all available funds to buy stock that is placed between position 300 and 400 in the S&P index 
    * Sell stock that rises above position 300 or below position 400 in the S&P index
    * Weight the purchases (according to `self._divisionWeights`) allocating more money for stock closer to position 300
"""
class CustomWeightingStrategy(StockChoiceStrategy):

    def __init__(self):
        # class fields
        self._idealStockRangeIndexStart = 300
        self._idealStockRangeIndexEnd = 400
        self._divisionWeights = [32, 22, 14, 10, 8, 6, 4, 2, 1.5, .5]
        self._alpacaInterface = AlpacaInterface()


    """
    `getStockOrderNumbers`: returns a dictionary of stock symbols mapped to the number of shares of that stock to buy  
    test: TestStockChoiceController.test_getStockOrderNumbers
    """
    def getBuyOrders(self: object, availableFunds: int) -> 'dict[str, int]':
        stockDataList = self._getStockRangeIdeal()
        stockWeights = self._generateStockWeightsBasedOnValue(stockDataList)
        return self._getBuyingQuantities(availableFunds, stockWeights)


    """
    `_getStockRangeIdeal`:  returns a limited list (StockData) of the ideal stocks to 
                            invest in
    """
    def _getStockRangeIdeal(self: object) -> 'list[StockData]':
        return self._alpacaInterface.getStockCache()[self._idealStockRangeIndexStart:self._idealStockRangeIndexEnd]


    """
    `_generateStockWeightsBasedOnValue`:    returns a list of StockData objects complete with `fundWeighting` 
                                            fields indicating the weighting that should be placed on this 
                                            stock based on the value of that stock.
    test: TestStockChoiceController.test_generateStockWeightsBasedOnValue
    """
    def _generateStockWeightsBasedOnValue(self: object, stockDataList: 'list[StockData]') -> 'list[StockData]':
        # order the stockDataList
        stockDataList = sorted(stockDataList, key=lambda x: x.price, reverse=True)

        for index, stockData in enumerate(stockDataList):
            stockData.fundWeighting = self._getStockWeightBasedOnListIndex(index, len(stockDataList))
        
        return stockDataList


    """
    `_getStockWeightBasedOnListIndex`:  returns a percentage of the fund that should be placed on the stock at 
                                        index `stockListIndex`, based on its position in the index
    test: TestStockChoiceController.test_getStockWeightBasedOnListIndex
    """
    def _getStockWeightBasedOnListIndex(self, stockListIndex, listLength) -> int:
        relativeIndex = stockListIndex / listLength

        numberOfItemsInTenPercent = listLength / 10

        for index, divisionWeight in enumerate(self._divisionWeights):
            if relativeIndex < (index + 1) / 10:
                return divisionWeight / numberOfItemsInTenPercent

        # weighting matrix
        #
        # | index position | share of fund | running total | 
        # |________________|_______________|_______________|
        # |      0-10      |      32%      |      32%      |
        # |     11-20      |      22%      |      54%      |
        # |     21-30      |      14%      |      68%      |
        # |     31-40      |      10%      |      78%      |
        # |     41-50      |       8%      |      86%      |
        # |     51-60      |       6%      |      92%      |
        # |     61-70      |       4%      |      96%      |
        # |     71-80      |       2%      |      98%      |
        # |     81-90      |     1.5%      |    99.5%      |
        # |    91-100      |     0.5%      |     100%      |


    """
    `_getStockWeightBasedOnListIndex`:  returns a dictionary of stock symbols mapped to the number of 
                                        shares of that stock to buy, based on the available funds and the 
                                        pre-caclulated fund weightings
    test: TestStockChoiceController.test_getBuyingQuantities
    """
    def _getBuyingQuantities(self: object, funds: float, stockDataList: 'list[StockData]') -> 'dict[str, int]':
        numberOfSharesToBuy = {stockData.symbol: 0 for stockData in stockDataList}
        totalFunds = funds
        numberOfNewOrders = 0

        # get stock orders based on weightings
        for stockData in stockDataList:
            # calculate how many new shares to attain
            fundsAvailableForThisStock = totalFunds * (stockData.fundWeighting / 100)
            newSharesToBuy = math.floor(fundsAvailableForThisStock / stockData.price)

            # update totals
            fundsToBeSpentOnThisStock = newSharesToBuy * stockData.price
            if newSharesToBuy:
                numberOfNewOrders += 1 
            numberOfSharesToBuy[stockData.symbol] += newSharesToBuy
            funds -= fundsToBeSpentOnThisStock

        # use up the remainder with linearly assigned stock orders 
        for stockData in stockDataList:
            if stockData.price > funds:
                continue
            
            numberOfSharesToBuy[stockData.symbol] += 1
            funds = funds - stockData.price


        if self._verifyOrderAffordability(stockDataList, totalFunds, numberOfSharesToBuy):
            return numberOfSharesToBuy
        return None

    def _getStockDataBySymbol(self: object, symbol: str, stockDataList: 'list[StockData]') -> StockData:

        for stockData in stockDataList:
            if stockData.symbol == symbol:
                return stockData

    def _verifyOrderAffordability(self: object, stockDataList: 'list[StockData]', totalFunds: float, numberOfSharesToBuy: 'dict[str, int]') -> bool:

        stockValue = 0

        for symbol, quantity in numberOfSharesToBuy.items():
            stockData: StockData = self._getStockDataBySymbol(symbol, stockDataList)
            stockValue += stockData.price * quantity

        if totalFunds < stockValue:
            logging.error("Not enough money to buy stock!")
            return False
        return True
