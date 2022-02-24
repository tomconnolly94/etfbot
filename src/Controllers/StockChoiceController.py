#!/usr/bin/python

# external dependencies
import math

# internal dependencies
from src.Types.StockData import StockData


class StockChoiceController:

    def __init__(self: object):
        pass


    def getStockOrderNumbers(self: object, stockDataList: 'list[StockData]', availableFunds: int) -> 'dict[str, int]':

        stockWeights = self._generateStockWeightsBasedOnValue(stockDataList)
        return self._getBuyingQuantities(availableFunds, stockWeights)


    def _generateStockWeightsBasedOnValue(self: object, stockDataList: 'list[StockData]') -> 'list[StockData]':

        # order the stockDataList
        stockDataList = sorted(stockDataList, key=lambda x: x.price, reverse=True)

        for index, stockData in enumerate(stockDataList):
            stockData.fundWeighting = self._getStockWeightBasedOnListIndex(index, len(stockDataList))
        
        return stockDataList


    def _getStockWeightBasedOnListIndex(self, stockListIndex, listLength) -> int:
        relativeIndex = stockListIndex / listLength

        numberOfItemsInTenPercent = listLength / 10

        divisionWeights = [32, 22, 14, 10, 8, 6, 4, 2, 1.5, .5]

        for index, divisionWeight in enumerate(divisionWeights):
            if relativeIndex < (index + 1) / 10:
                return divisionWeight / numberOfItemsInTenPercent


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


    def storeTotalUnusedFunds(self: object, totalUnusedFunds:float):
        print(totalUnusedFunds)


    def _getBuyingQuantities(self: object, funds: float, stockDataList: 'list[StockData]') -> 'list[StockData]':
        
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

        self.storeTotalUnusedFunds(funds)

        return numberOfSharesToBuy

