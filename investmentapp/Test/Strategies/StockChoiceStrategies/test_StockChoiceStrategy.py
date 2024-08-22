#!/usr/bin/python

# external dependencies
import unittest
from unittest import mock
from unittest.mock import MagicMock

# internal dependencies
from src.Strategies.StockChoiceStrategies.StockChoiceStrategy import StockChoiceStrategy
from src.Types.StockData import StockData

class TestCustomWeightingStrategy(unittest.TestCase):


    @mock.patch("src.Strategies.StockChoiceStrategies.StockChoiceStrategy.DatabaseInterface")
    def test__getStockRange(self, DatabaseInterfaceMock):
        
        # configure fake data
        fakeStockList = [ StockData("fakeStockSymbol1", 10), StockData("fakeStockSymbol2", 20), StockData("fakeStockSymbol3", 30) ]
        filterFunction = lambda list: list[1:]

        # configure mocks
        fakeStockListInterface = MagicMock()
        fakeStockListInterface.getStockCache.return_value = fakeStockList
        DatabaseInterfaceMagicMock = MagicMock()
        DatabaseInterfaceMagicMock.getExcludedStockRecords.return_value = "fakeStockSymbol3"
        DatabaseInterfaceMock.return_value = DatabaseInterfaceMagicMock

        # concrete class to allow testing the abstract class
        class TestStockChoiceStrategy(StockChoiceStrategy):

            #concrete implementations are needed
            def getBuyOrders(self, quantity: int, existingPositions: 'dict[str, int]') -> 'dict[str, int]':
                pass

            def getSellOrders(self, quantity: int) -> 'list[str]':
                pass

        # run testable function
        actualStockRange = TestStockChoiceStrategy(fakeStockListInterface)._getStockRange(filterFunction)

        # asserts
        self.assertEqual(1, len(actualStockRange))
        self.assertEqual(fakeStockList[1].symbol, actualStockRange[0].symbol)
        fakeStockListInterface.getStockCache.assert_called()


if __name__ == '__main__':
    unittest.main()
