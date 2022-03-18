#!/usr/bin/python

# external dependencies
import math

# internal dependencies
from src.Types.StockData import StockData

"""
StockChoiceController

This is a class to contain numerical information about how funds are distributed 
among stocks

"""
class StockChoiceController:

    def __init__(self: object):
        pass


    """
    `getStockOrderNumbers`: returns a dictionary of stock symbols mapped to the number of shares of that stock to buy  
    test: TestStockChoiceController.test_getStockOrderNumbers
    """
    def getStockOrderNumbers(self: object, stockDataList: 'list[StockData]', availableFunds: int) -> 'dict[str, int]':
        stockWeights = self._generateStockWeightsBasedOnValue(stockDataList)
        return self._getBuyingQuantities(availableFunds, stockWeights)


    """
    `_generateStockWeightsBasedOnValue`:    returns a list of StockData objects complete with `fundWeighting` 
                                            fields indicating the weighting that should be placed on this 
                                            stock based on the value of that stock.
    test: TestStockChoiceController.test__generateStockWeightsBasedOnValue
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
    test: TestStockChoiceController.test__getStockWeightBasedOnListIndex
    """
    def _getStockWeightBasedOnListIndex(self, stockListIndex, listLength) -> int:
        relativeIndex = stockListIndex / listLength

        numberOfItemsInTenPercent = listLength / 10

        divisionWeights = [32, 22, 14, 10, 8, 6, 4, 2, 1.5, .5]

        for index, divisionWeight in enumerate(divisionWeights):
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

        return numberOfSharesToBuy

