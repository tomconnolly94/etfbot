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

    def generateAYearOfFakeValue(self):
        prices = []

        for stockIndex in range(10):
            
            newStockData = {}
            
            for dateIndex in range(365):

                newStockData[f"date{dateIndex}"] = random.random() * 100
            
            prices.append(newStockData)

        return prices


    @mock.patch("server.controllers.DataServer._normaliseValues")
    @mock.patch("server.controllers.DataServer.getPricesForStockSymbols")
    def test__getSPY500Data(self, getPricesForStockSymbolsMock, _normaliseValuesMock):

        # config fake data
        fakeStockData = self.generateAYearOfFakeValue()
        expectedStockData = {
            "currentValue": sum([value["date364"] for value in fakeStockData ]),
            "oneMonthPrevValue": sum([value["date334"] for value in fakeStockData ]),
            "oneYearPrevValue": sum([value["date0"] for value in fakeStockData ]),
            "values": fakeStockData
        }

        # config mocks
        getPricesForStockSymbolsMock.return_value = fakeStockData
        _normaliseValuesMock.return_value = fakeStockData


        stockData = _getSPY500Data()
        print(stockData)

        self.assertEqual(expectedStockData["currentValue"], stockData["currentValue"])
        self.assertEqual(expectedStockData["oneMonthPrevValue"], stockData["oneMonthPrevValue"])
        self.assertEqual(expectedStockData["oneYearPrevValue"], stockData["oneYearPrevValue"])
    
    
    @mock.patch("server.controllers.DataServer._normaliseValues")
    @mock.patch("server.controllers.DataServer.getPricesForStockSymbols")
    @mock.patch("server.controllers.DataServer.AlpacaInterface")
    def test__getCurrentHoldingsPerformanceData(self, AlpacaInterfaceMock, getPricesForStockSymbolsMock, _normaliseValuesMock):

        # config fake data
        openPositions = {
            "stock1": 10,
            "stock2": 15,
            "stock3": 20,
            "stock4": 50,
            "stock5": 100,
        }
        historicalPositionPrices = self.generateAYearOfFakeValue()

        for index in range(365):
            historicalPositionPrices.append({
                "date1": random.random() * 100,
                "date2": random.random() * 100,
                "date3": random.random() * 100,
                "date4": random.random() * 100
            })

        # config mocks
        AlpacaInterfaceMagicMock = MagicMock()
        AlpacaInterfaceMagicMock.getOpenPositions.return_value = openPositions
        AlpacaInterfaceMock.return_value = AlpacaInterfaceMagicMock
        getPricesForStockSymbolsMock.return_value = historicalPositionPrices
        _normaliseValuesMock.side_effect = lambda input: input

        stockData = _getCurrentHoldingsPerformanceData()

        expectedEndValue = sum([ price["date1"] for price in historicalPositionPrices ])

        self.assertEqual(sum(openPositions.values()), stockData["endValue"])
        self.assertEqual(expectedEndValue, stockData["startValue"])


if __name__ == "__main__":
    unittest.main()