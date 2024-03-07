#!/venv/bin/python

# external dependencies
import json
from unittest.mock import MagicMock
from server.test.testUtilities import FakeFile
import unittest
import mock

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


    @mock.patch("server.controllers.DataServer._normaliseValues")
    @mock.patch("server.controllers.DataServer.getPricesForStockSymbols")
    def test__getSPY500Data(self, getPricesForStockSymbolsMock, _normaliseValuesMock):

        # config fake data
        fakeStockData = {
            "stock1": 10,
            "stock2": 15,
            "stock3": 20,
            "stock4": 50,
            "stock5": 100,
        }
        expectedStockData = {
            "startValue": 10,
            "endValue": 100,
            "values": fakeStockData
        }

        # config mocks
        getPricesForStockSymbolsMock.return_value = [fakeStockData]
        _normaliseValuesMock.return_value = fakeStockData


        stockData = _getSPY500Data()

        self.assertEqual(expectedStockData, stockData)
    
    
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
        historicalPositionPrices = [
            { "date1": 2, "date2": 7, "date3": 3, "date4": 10 },
            { "date1": 12, "date2": 15, "date3": 6, "date4": 15 },
            { "date1": 24, "date2": 14, "date3": 17, "date4": 20 },
            { "date1": 21, "date2": 18, "date3": 58, "date4": 50 },
            { "date1": 76, "date2": 1, "date3": 38, "date4": 100 },
        ]
        expectedReturnValue = {
            'startValue': 135, 
            'endValue': 195, 
            'values': {'date1': 135, 'date2': 55, 'date3': 122, 'date4': 195}}

        # config mocks
        AlpacaInterfaceMagicMock = MagicMock()
        AlpacaInterfaceMagicMock.getOpenPositions.return_value = openPositions
        AlpacaInterfaceMock.return_value = AlpacaInterfaceMagicMock
        getPricesForStockSymbolsMock.return_value = historicalPositionPrices
        _normaliseValuesMock.side_effect = lambda input: input

        stockData = _getCurrentHoldingsPerformanceData()

        expectedEndValue = sum([ price["date1"] for price in historicalPositionPrices ])

        self.assertEqual(stockData["endValue"], sum(openPositions.values()))
        self.assertEqual(stockData["startValue"], expectedEndValue)


if __name__ == "__main__":
    unittest.main()