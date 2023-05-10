#!/usr/bin/python

# external dependencies
import json
import time
import unittest
from unittest import mock
import matplotlib.pyplot as plt
import numpy as np
from src.Strategies.StockChoiceStrategies.CustomWeightingStrategy import CustomWeightingStrategy

# internal dependencies
from src.Types.StockData import StockData

class TestCustomWeightingStrategy(unittest.TestCase):

    def _loadStockData(self):

        stockData = []

        with open("Test/TestData/StockDataListRandomPrice.json", "r") as read_file:
            stockDataRaw = json.load(read_file)

            for item in stockDataRaw:
                stockData.append(StockData(item["symbol"], item["price"]))
        
        return stockData

    @mock.patch("src.Strategies.StockChoiceStrategies.CustomWeightingStrategy.CustomWeightingStrategy._getBuyingQuantities")
    @mock.patch("src.Strategies.StockChoiceStrategies.CustomWeightingStrategy.CustomWeightingStrategy._generateStockWeightsBasedOnValue")
    @mock.patch("src.Strategies.StockChoiceStrategies.CustomWeightingStrategy.CustomWeightingStrategy._getStockRangeIdeal")
    def test_getStockOrderNumbers(self, _getStockRangeIdealMock, _generateStockWeightsBasedOnValueMock, _getBuyingQuantitiesMock):
        
        # configure fake data
        fakeStockWeights = {"fakeStockWeight": 1}
        fakeStockOrderNumbers = {"fakeStockWeight": 1}
        fakeStockDataList = [ "fakeStockData1", "fakeStockData2" ]
        fakeAvailableFunds = 100

        # configure mocks
        _getStockRangeIdealMock.return_value = fakeStockDataList
        _generateStockWeightsBasedOnValueMock.return_value = fakeStockWeights
        _getBuyingQuantitiesMock.return_value = fakeStockOrderNumbers

        # run testable function
        actualStockOrderNumbers = CustomWeightingStrategy().getBuyOrders(fakeAvailableFunds)

        # asserts
        self.assertEquals(fakeStockOrderNumbers, actualStockOrderNumbers)
        _getStockRangeIdealMock.assert_called()
        _generateStockWeightsBasedOnValueMock.assert_called_with(fakeStockDataList)
        _getBuyingQuantitiesMock.assert_called_with(fakeAvailableFunds, fakeStockWeights)



    def test__getStockWeightBasedOnListIndex(self):
        customWeightingStrategy = CustomWeightingStrategy()

        stockWeight = customWeightingStrategy._getStockWeightBasedOnListIndex(0, 100)
        self.assertEquals(3.2, stockWeight)
        
        stockWeight = customWeightingStrategy._getStockWeightBasedOnListIndex(1, 100)
        self.assertEquals(3.2, stockWeight)
        
        stockWeight = customWeightingStrategy._getStockWeightBasedOnListIndex(10, 100)
        self.assertEquals(2.2, stockWeight)

        stockWeight = customWeightingStrategy._getStockWeightBasedOnListIndex(11, 100)
        self.assertEquals(2.2, stockWeight)

        stockWeight = customWeightingStrategy._getStockWeightBasedOnListIndex(20, 100)
        self.assertEquals(1.4, stockWeight)
        
        stockWeight = customWeightingStrategy._getStockWeightBasedOnListIndex(4, 10)
        self.assertEquals(8, stockWeight)
        
        stockWeight = customWeightingStrategy._getStockWeightBasedOnListIndex(6, 10)
        self.assertEquals(4, stockWeight)

        stockWeight = customWeightingStrategy._getStockWeightBasedOnListIndex(1, 10)
        self.assertEquals(22, stockWeight)
        
        stockWeight = customWeightingStrategy._getStockWeightBasedOnListIndex(1, 20)
        self.assertEquals(16, stockWeight)


    def test__generateStockWeightsBasedOnValue(self):
        customWeightingStrategy = CustomWeightingStrategy()

        stockData = self._loadStockData()

        stockWeights = customWeightingStrategy._generateStockWeightsBasedOnValue(stockData)

        stockWeightTotal = 0

        for value in stockWeights:
            stockWeightTotal += value.fundWeighting

        self.assertEquals(100, round(stockWeightTotal))


    def test__getBuyingQuantities(self):
        customWeightingStrategy = CustomWeightingStrategy()

        # inputs 
        funds = 100
        stockDataList = sorted([
            StockData("0-10%", 12, 30),
            StockData("11-20%", 7, 20), # 50
            StockData("21-30%", 5, 15), # 65
            StockData("31-40%", 4, 12), # 77
            StockData("41-50%", 3.5, 8),# 85
            StockData("51-60%", 3, 6),  # 91
            StockData("61-70%", 2, 4),  # 95
            StockData("71-80%", 1, 3),  # 98
            StockData("81-90%", 0.5, 1),# 99
            StockData("91-100%", 0.2, 1) # 100
        ], key=lambda stockData: -stockData.price)

        numberOfSharesToBuy = customWeightingStrategy._getBuyingQuantities(funds, stockDataList)

        self.assertEquals(3, numberOfSharesToBuy["0-10%"]) #    28   2
        self.assertEquals(2, numberOfSharesToBuy["11-20%"]) # 12 40   8 extra
        self.assertEquals(3, numberOfSharesToBuy["21-30%"]) # 14 54   1
        self.assertEquals(3, numberOfSharesToBuy["31-40%"]) # 10 64   2
        self.assertEquals(2, numberOfSharesToBuy["41-50%"]) #  6 70   2
        self.assertEquals(2, numberOfSharesToBuy["51-60%"]) #  6 76   0
        self.assertEquals(2, numberOfSharesToBuy["61-70%"]) #3.5 79.5 .5 extra
        self.assertEquals(4, numberOfSharesToBuy["71-80%"]) #  3 82.5 0 
        self.assertEquals(2, numberOfSharesToBuy["81-90%"]) #  1 83.5 0
        self.assertEquals(5, numberOfSharesToBuy["91-100%"]) #  1 84.5 0
                                                # leftover: 15.5


        # show bar graph of investment weights
        objects = numberOfSharesToBuy.keys()
        y_pos = np.arange(len(stockDataList))
        value = [stockData.price * numberOfSharesToBuy[stockData.symbol] for stockData in stockDataList]
        numSharesPerStock = [numberOfSharesToBuy[stockData.symbol] for stockData in stockDataList]
        
        # draw graph
        plt.rcdefaults()
        plt.bar(y_pos, value, align='center', alpha=0.5)
        plt.bar(y_pos, numSharesPerStock, align='center', alpha=0.5)
        plt.xticks(y_pos, objects)
        plt.ylabel('Value')
        plt.title('Investment weightings')

        def close_event():
            plt.close()

        fig = plt.figure()
        timer = fig.canvas.new_timer(interval = 2000) #creating a timer object and setting an interval of 3000 milliseconds
        timer.add_callback(close_event)

        plt.show(block=False)
        plt.pause(3)
        plt.close()



if __name__ == '__main__':
    unittest.main()
