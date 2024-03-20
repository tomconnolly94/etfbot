#!/venv/bin/python

# external dependencies
import json
from unittest.mock import MagicMock
from server.test.testUtilities import FakeFile
import unittest
import mock
import random

# internal dependencies
from server.controllers.DataServer import _normaliseValues, _getSPY500Data, _getCurrentHoldingsPerformanceData


class Test_DataServer(unittest.TestCase):

    def test__normaliseValues(self):

        #config fake data
        fakeData = {
            "key1": 1,
            "key2": 2,
            "key3": 3,
            "key4": 4,
            "key5": 5
        }
        expectedNormalisedValues = {
            "key1": 0.2,
            "key2": 0.4,
            "key3": 0.6,
            "key4": 0.8,
            "key5": 1
        }

        normalisedValues = _normaliseValues(fakeData)

        self.assertEqual(expectedNormalisedValues, normalisedValues)


    def _generateFakeStockPositions(self, numberOfStocks=10):
        stockPositions = {}

        for stockIndex in range(numberOfStocks):
            stockPositions[f"stock{stockIndex}"] = random.random() * 150

        return stockPositions


    def _generateAYearOfFakeValue(self, numberOfStocks=10):
        prices = []

        for stockIndex in range(numberOfStocks):
            newStockData = {}
            
            for dateIndex in range(365):
                newStockData[dateIndex] = random.random() * 150
            
            prices.append(newStockData)

        return prices


    @mock.patch("server.controllers.DataServer._normaliseValues")
    @mock.patch("server.controllers.DataServer.getPricesForStockSymbols")
    def test__getSPY500Data(self, getPricesForStockSymbolsMock, _normaliseValuesMock):

        # config fake data
        fakeStockData = self._generateAYearOfFakeValue(1)
        expectedStockData = {
            "currentValue": fakeStockData[0][364], #sum([value[364] for value in fakeStockData ]),
            "oneMonthPrevValue": fakeStockData[0][334], #sum([value[334] for value in fakeStockData ]),
            "oneYearPrevValue": fakeStockData[0][0], #sum([value[0] for value in fakeStockData ]),
            "values": fakeStockData[0]
        }

        # config mocks
        getPricesForStockSymbolsMock.return_value = fakeStockData
        _normaliseValuesMock.return_value = fakeStockData


        stockData = _getSPY500Data()

        self.assertEqual(expectedStockData["currentValue"], stockData["currentValue"])
        self.assertEqual(expectedStockData["oneMonthPrevValue"], stockData["oneMonthPrevValue"])
        self.assertEqual(expectedStockData["oneYearPrevValue"], stockData["oneYearPrevValue"])
    
    
    @mock.patch("server.controllers.DataServer._normaliseValues")
    @mock.patch("server.controllers.DataServer.getPricesForStockSymbols")
    @mock.patch("server.controllers.DataServer.AlpacaInterface")
    def test__getCurrentHoldingsPerformanceData(self, AlpacaInterfaceMock, getPricesForStockSymbolsMock, _normaliseValuesMock):

        # config fake data
        openPositions = self._generateFakeStockPositions()
        historicalPositionPrices = self._generateAYearOfFakeValue()
        for positionIndex, positionHistory in enumerate(historicalPositionPrices):
            positionHistory[364] = openPositions[list(openPositions.keys())[positionIndex]]

        # config mocks
        AlpacaInterfaceMagicMock = MagicMock()
        AlpacaInterfaceMagicMock.getOpenPositions.return_value = openPositions
        AlpacaInterfaceMock.return_value = AlpacaInterfaceMagicMock
        getPricesForStockSymbolsMock.return_value = historicalPositionPrices
        _normaliseValuesMock.side_effect = lambda input: input

        stockData = _getCurrentHoldingsPerformanceData()

        expectedYearPrevValue = sum([ price[0] for price in historicalPositionPrices ])
        expectedMonthPrevValue = sum([ price[334] for price in historicalPositionPrices ])

        self.assertEqual(sum(openPositions.values()), stockData["currentValue"])
        self.assertEqual(expectedYearPrevValue, stockData["oneYearPrevValue"])
        self.assertEqual(expectedMonthPrevValue, stockData["oneMonthPrevValue"])
    
    
    @mock.patch("server.controllers.DataServer._normaliseValues")
    @mock.patch("server.controllers.DataServer.getPricesForStockSymbols")
    @mock.patch("server.controllers.DataServer.AlpacaInterface")
    def test__getPortfolioPerformanceData(self, AlpacaInterfaceMock, getPricesForStockSymbolsMock, _normaliseValuesMock):

        # config fake data
        openPositions = self._generateFakeStockPositions()
        historicalPositionPrices = self._generateAYearOfFakeValue()
        for positionIndex, positionHistory in enumerate(historicalPositionPrices):
            positionHistory[364] = openPositions[list(openPositions.keys())[positionIndex]]

        # config mocks
        AlpacaInterfaceMagicMock = MagicMock()
        AlpacaInterfaceMagicMock.getOpenPositions.return_value = openPositions
        AlpacaInterfaceMock.return_value = AlpacaInterfaceMagicMock
        getPricesForStockSymbolsMock.return_value = historicalPositionPrices
        _normaliseValuesMock.side_effect = lambda input: input

        stockData = _getCurrentHoldingsPerformanceData()

        expectedYearPrevValue = sum([ price[0] for price in historicalPositionPrices ])
        expectedMonthPrevValue = sum([ price[334] for price in historicalPositionPrices ])

        self.assertEqual(sum(openPositions.values()), stockData["currentValue"])
        self.assertEqual(expectedYearPrevValue, stockData["oneYearPrevValue"])
        self.assertEqual(expectedMonthPrevValue, stockData["oneMonthPrevValue"])


if __name__ == "__main__":
    unittest.main()