#!/usr/bin/python

# external dependencies
import json
import unittest
from unittest import mock
import matplotlib.pyplot as plt; plt.rcdefaults()
import numpy as np
import matplotlib.pyplot as plt

# internal dependencies
from src.Controllers.InvestmentController import InvestmentController
from Types.StockData import StockData

class TestInvestmentController(unittest.TestCase):

    def _loadStockData(self):

        stockData = []

        with open("src/Test/TestData/StockDataListRandomPrice.json", "r") as read_file:
            stockDataRaw = json.load(read_file)

            for item in stockDataRaw:
                stockData.append(StockData(item["symbol"], item["price"]))
        
        return stockData

    def test_auditDumpCompleteDir(self):
        investmentController = InvestmentController()

        
        stockWeight = investmentController.getStockWeightBasedOnListIndex(0, 100)
        self.assertEquals(3.2, stockWeight)
        
        stockWeight = investmentController.getStockWeightBasedOnListIndex(1, 100)
        self.assertEquals(3.2, stockWeight)
        
        stockWeight = investmentController.getStockWeightBasedOnListIndex(10, 100)
        self.assertEquals(2.2, stockWeight)

        stockWeight = investmentController.getStockWeightBasedOnListIndex(11, 100)
        self.assertEquals(2.2, stockWeight)

        stockWeight = investmentController.getStockWeightBasedOnListIndex(20, 100)
        self.assertEquals(1.4, stockWeight)
        
        stockWeight = investmentController.getStockWeightBasedOnListIndex(4, 10)
        self.assertEquals(8, stockWeight)
        
        stockWeight = investmentController.getStockWeightBasedOnListIndex(6, 10)
        self.assertEquals(4, stockWeight)

        stockWeight = investmentController.getStockWeightBasedOnListIndex(1, 10)
        self.assertEquals(22, stockWeight)
        
        stockWeight = investmentController.getStockWeightBasedOnListIndex(1, 20)
        self.assertEquals(16, stockWeight)


    def test_generateStockWeightsBasedOnValue(self):
        investmentController = InvestmentController()

        stockData = self._loadStockData()

        stockWeights = investmentController.generateStockWeightsBasedOnValue(stockData)

        stockWeightTotal = 0

        for value in stockWeights.values():
            stockWeightTotal += value

        self.assertEquals(100, round(stockWeightTotal))


    @mock.patch("src.Controllers.InvestmentController.InvestmentController.storeTotalUnusedFunds")
    def test_getBuyingQuantities(self, storeTotalUnusedFundsMock):
        investmentController = InvestmentController()

        # inputs 
        funds = 100
        stockDataList = sorted([
            StockData("A", 12, 30),
            StockData("B", 7, 20), # 50
            StockData("C", 5, 15), # 65
            StockData("D", 4, 12), # 77
            StockData("E", 3.5, 8),# 85
            StockData("F", 3, 6),  # 91
            StockData("G", 2, 4),  # 95
            StockData("H", 1, 3),  # 98
            StockData("I", 0.5, 1),# 99
            StockData("J", 0.2, 1) # 100
        ], key=lambda stockData: -stockData.price)

        numberOfSharesToBuy = investmentController.getBuyingQuantities(funds, stockDataList)

        self.assertEquals(3, numberOfSharesToBuy["A"]) #    28   2
        self.assertEquals(2, numberOfSharesToBuy["B"]) # 12 40   8 extra
        self.assertEquals(3, numberOfSharesToBuy["C"]) # 14 54   1
        self.assertEquals(3, numberOfSharesToBuy["D"]) # 10 64   2
        self.assertEquals(2, numberOfSharesToBuy["E"]) #  6 70   2
        self.assertEquals(2, numberOfSharesToBuy["F"]) #  6 76   0
        self.assertEquals(2, numberOfSharesToBuy["G"]) #3.5 79.5 .5 extra
        self.assertEquals(4, numberOfSharesToBuy["H"]) #  3 82.5 0 
        self.assertEquals(2, numberOfSharesToBuy["I"]) #  1 83.5 0
        self.assertEquals(5, numberOfSharesToBuy["J"]) #  1 84.5 0
                                                # leftover: 15.5

        storeTotalUnusedFundsMock.assert_called_with(0)

        # show bar graph of investment weights
        objects = numberOfSharesToBuy.keys()
        y_pos = np.arange(len(stockDataList))
        value = [stockData.price * numberOfSharesToBuy[stockData.symbol] for stockData in stockDataList]
        numSharesPerStock = [numberOfSharesToBuy[stockData.symbol] for stockData in stockDataList]

        plt.bar(y_pos, value, align='center', alpha=0.5)
        plt.bar(y_pos, numSharesPerStock, align='center', alpha=0.5)
        plt.xticks(y_pos, objects)
        plt.ylabel('Value')
        plt.title('Investment weightings')

        plt.show()


if __name__ == '__main__':
    unittest.main()
