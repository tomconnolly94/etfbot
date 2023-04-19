#!/usr/bin/python

# external dependencies
import unittest
from unittest import mock
from unittest.mock import MagicMock

# internal dependencies
from src.Strategies.StockChoiceStrategies.StockChoiceStrategy import StockChoiceStrategy
from src.Types.StockData import StockData

class TestCustomWeightingStrategy(unittest.TestCase):


    @mock.patch("src.Interfaces.DatabaseInterface.DatabaseInterface.getExcludedStockSymbols")
    def test__getStockRange(self, getExcludedStockSymbolsMock):
        
        # configure fake data
        fakeStockList = [ StockData("fakeStockSymbol1", 10), StockData("fakeStockSymbol2", 20), StockData("fakeStockSymbol3", 30) ]
        filterFunction = lambda list: list[1:]

        # configure mocks
        fakeStockListInterface = MagicMock()
        fakeStockListInterface.getStockCache.return_value = fakeStockList
        getExcludedStockSymbolsMock.return_value = "fakeStockSymbol3"

        # concrete class to allow testing the abstract class
        class TestStockChoiceStrategy(StockChoiceStrategy):

            def getBuyOrders(self, quantity: int, existingPositions: 'dict[str, int]') -> 'dict[str, int]':
                pass

            def getSellOrders(self, quantity: int) -> 'list[str]':
                pass

        # run testable function
        actualStockRange = TestStockChoiceStrategy(fakeStockListInterface)._getStockRange(filterFunction)

        # asserts
        self.assertEquals(1, len(actualStockRange))
        self.assertEquals(fakeStockList[1].symbol, actualStockRange[0].symbol)
        fakeStockListInterface.getStockCache.assert_called()


if __name__ == '__main__':
    unittest.main()
