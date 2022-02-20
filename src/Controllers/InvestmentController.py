#!/usr/bin/python

# external dependencies
import math

from numpy import number

# internal dependencies
from src.Controllers.DataController import DataController
from src.Types.StockData import StockData


class InvestmentController:

    def __init__(self: object):
        #self.dataController = DataController()
        pass


    # def getOpenPositions(self: object):
    #     openPositions: list = self.alpacaInterface.getOpenPositions()

    #     print(openPositions)


    def getStockOrderNumbers(self: object) -> 'list[StockData]':

        stockDataList = self.generateStockWeightsBasedOnValue(stockDataList)
        funds = 100
        return self.getBuyingQuantities(funds, stockDataList)


    def generateStockWeightsBasedOnValue(self: object, stockDataList: 'list[StockData]') -> 'list[StockData]':

        # order the stockDataList
        stockDataList = sorted(stockDataList, key=lambda x: x.price, reverse=True)

        stockWeights = {}

        for index, stockData in enumerate(stockDataList):
            stockData.fundWeighting = self.getStockWeightBasedOnListIndex(index, len(stockDataList))
        
        return stockWeights


    def getStockWeightBasedOnListIndex(self, stockListIndex, listLength) -> int:
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


    def getBuyingQuantities(self: object, funds: int, stockDataList: 'list[StockData]') -> 'list[StockData]':
        
        numberOfSharesToBuy = {stockData.symbol: 0 for stockData in stockDataList}
        cheapestStockPrice = sorted(stockDataList, key=lambda stockData: stockData.price)[0].price
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

