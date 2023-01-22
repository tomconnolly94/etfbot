#!/usr/bin/python

# external dependencies
import itertools
import unittest
from unittest import mock
import matplotlib.pyplot as plt

# internal dependencies
from src.Strategies.StockChoiceStrategies.StockChoiceStrategy import StockChoiceStrategy; plt.rcdefaults()
from src.Controllers.InvestmentController import InvestmentController

class TestInvestmentController(unittest.TestCase):

    @mock.patch("src.Controllers.InvestmentController.InvestmentController._getValueOfStock")
    @mock.patch("src.Interfaces.AlpacaInterface.AlpacaInterface.buyStock")
    @mock.patch("src.Interfaces.AlpacaInterface.AlpacaInterface.sellStock")
    @mock.patch("src.Interfaces.AlpacaInterface.AlpacaInterface.getAvailableFunds")
    @mock.patch("src.Controllers.StockChoiceController.StockChoiceController.getStockChoiceStrategy")
    @mock.patch("src.Controllers.InvestmentController.logging.info")
    @mock.patch("src.Controllers.InvestmentController.InvestmentController._getPositionInIndex")
    @mock.patch("src.Interfaces.AlpacaInterface.AlpacaInterface.getOpenPositions")
    def test_rebalanceInvestments(self,
        getOpenPositionsMock,
        _getPositionInIndexMock,
        loggingMock,
        getStockChoiceStrategyMock,
        getAvailableFundsMock,
        sellStockMock,
        buyStockMock,
        _getValueOfStockMock
        ):

        # configure fake data
        fakeOpenPositions = {
            "fakeOpenPosition1": 10, 
            "fakeOpenPosition2": 15,
            "fakeOpenPosition3": 20
        }
        fakePositionsInIndex = [ 3, 6, 7 ]
        fakeAvailableFunds = 100
        fakeBuyOrders = {
            "fakeBuyOrder1": 10,
            "fakeBuyOrder2": 15
        }
        fakeSellOrders = {
            "fakeOpenPosition1": 10, 
            "fakeOpenPosition2": 15
        }

        class FakeStockChoiceStrategy(StockChoiceStrategy):
            
            def __init__(self, buyOrders, sellOrders):
                self.buyOrders = buyOrders
                self.sellOrders = sellOrders

            def getBuyOrders(self, availableFunds):
                return self.buyOrders

            def getSellOrders(self):
                return self.sellOrders


        # configure mocks
        getOpenPositionsMock.return_value = fakeOpenPositions
        _getPositionInIndexMock.side_effect = fakePositionsInIndex
        getStockChoiceStrategyMock.return_value = FakeStockChoiceStrategy(fakeBuyOrders, fakeSellOrders)
        getAvailableFundsMock.return_value = fakeAvailableFunds
        _getValueOfStockMock.return_value = 10

        # run testable function
        InvestmentController().rebalanceInvestments()

        # asserts
        getOpenPositionsMock.assert_called()
        self.assertEquals(10, loggingMock.call_count)
        getAvailableFundsMock.assert_called()

        sellStockMock.assert_has_calls([ 
            mock.call(list(fakeOpenPositions.keys())[0], list(fakeOpenPositions.values())[0]), 
            mock.call(list(fakeOpenPositions.keys())[1], list(fakeOpenPositions.values())[1])
        ])
        buyStockMock.assert_has_calls([mock.call(key, value) for key, value in fakeBuyOrders.items() ])
        self.assertEquals(4, _getValueOfStockMock.call_count)
        _getValueOfStockMock.assert_has_calls([
            mock.call(list(fakeSellOrders.keys())[0]),
            mock.call(list(fakeSellOrders.keys())[1]),
            mock.call(list(fakeBuyOrders.keys())[0]),
            mock.call(list(fakeBuyOrders.keys())[1])
        ])

        loggingMock.assert_has_calls([
            mock.call(f"Number of current positions held: {len(fakeOpenPositions)}"),
            mock.call("Current positions - (symbol: index position) fakeOpenPosition1: 3, fakeOpenPosition2: 6, fakeOpenPosition3: 7"),
            mock.call(f"Number of positions that will be closed: {len(fakeSellOrders)}, total value: {sum(list(fakeSellOrders.values()))}"),
            mock.call("Sold 10 shares of fakeOpenPosition1 at 10"),
            mock.call("Sold 15 shares of fakeOpenPosition2 at 10"),
            mock.call(f"Number of positions that will be opened: {len(fakeBuyOrders)}"),
            mock.call("Attempting to buy 10 shares of fakeBuyOrder1 at 10."),
            mock.call("Buy successful, total money spent: 100"),
            mock.call("Attempting to buy 15 shares of fakeBuyOrder2 at 10."),
            mock.call("Buy successful, total money spent: 250")
        ])


if __name__ == '__main__':
    unittest.main()
