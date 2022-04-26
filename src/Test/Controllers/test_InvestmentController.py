#!/usr/bin/python

# external dependencies
import unittest
from unittest import mock
import matplotlib.pyplot as plt; plt.rcdefaults()

# internal dependencies
from src.Controllers.InvestmentController import InvestmentController

class TestInvestmentController(unittest.TestCase):

    @mock.patch("src.Controllers.InvestmentController.InvestmentController._getValueOfStock")
    @mock.patch("src.Interfaces.AlpacaInterface.AlpacaInterface.buyStock")
    @mock.patch("src.Interfaces.AlpacaInterface.AlpacaInterface.sellStock")
    @mock.patch("src.Controllers.InvestmentController.InvestmentController._getPositionsToBuy")
    @mock.patch("src.Interfaces.AlpacaInterface.AlpacaInterface.getAvailableFunds")
    @mock.patch("src.Controllers.InvestmentController.InvestmentController._getValueOfStockList")
    @mock.patch("src.Controllers.InvestmentController.InvestmentController._getPositionsToSell")
    @mock.patch("src.Controllers.InvestmentController.logging.info")
    @mock.patch("src.Controllers.InvestmentController.InvestmentController._getPositionInIndex")
    @mock.patch("src.Interfaces.AlpacaInterface.AlpacaInterface.getOpenPositions")
    def test_rebalanceInvestments(self,
        getOpenPositionsMock,
        _getPositionInIndexMock,
        loggingMock,
        _getPositionsToSellMock,
        _getValueOfStockListMock,
        getAvailableFundsMock,
        _getPositionsToBuyMock,
        sellStockMock,
        buyStockMock,
        _getValueOfStockMock
        ):

        # configure fake data
        fakeOpenPositions = {
            "fakeOpenPosition1": 10, 
            "fakeOpenPosition2": 15
        }
        fakePositionsInIndex = [ 3, 6 ]
        fakePositionsToSell = {
            "fakePositionToSell1": 2, 
            "fakePositionToSell2": 4 
        }
        fakeValueOfStockList = 100
        fakeAvailableFunds = 10
        fakePositionsToBuy = {
            "fakePositionToBuy1": 5,
            "fakePositionToBuy2": 7
        }

        # configure mocks
        getOpenPositionsMock.return_value = fakeOpenPositions
        _getPositionInIndexMock.side_effect = fakePositionsInIndex
        _getPositionsToSellMock.return_value = fakePositionsToSell
        _getValueOfStockListMock.return_value = fakeValueOfStockList
        getAvailableFundsMock.return_value = fakeAvailableFunds
        _getPositionsToBuyMock.return_value = fakePositionsToBuy
        _getValueOfStockMock.return_value = 10

        # run testable function
        InvestmentController().rebalanceInvestments()

        # asserts
        getOpenPositionsMock.assert_called()
        self.assertEquals(8, loggingMock.call_count)
        _getPositionsToSellMock.assert_called_with(fakeOpenPositions)
        _getValueOfStockListMock.assert_called_with(fakePositionsToSell)
        getAvailableFundsMock.assert_called()
        _getPositionsToBuyMock.assert_called_with(fakeOpenPositions, fakeValueOfStockList + fakeAvailableFunds)
        sellStockMock.assert_has_calls([
            mock.call("fakePositionToSell1", 2),
            mock.call("fakePositionToSell2", 4)
        ])
        buyStockMock.assert_has_calls([
            mock.call("fakePositionToBuy1", 5),
            mock.call("fakePositionToBuy2", 7)
        ])
        self.assertEquals(4, _getValueOfStockMock.call_count)
        _getValueOfStockMock.assert_has_calls([
            mock.call("fakePositionToSell1"),
            mock.call("fakePositionToSell2"),
            mock.call("fakePositionToBuy1"),
            mock.call("fakePositionToBuy2")
        ])

        loggingMock.assert_has_calls([
            mock.call("Number of current positions held: 2"),
            mock.call("Current positions - (symbol: index position) fakeOpenPosition1: 3, fakeOpenPosition2: 6"),
            mock.call(f"Number of positions that should be closed: {len(fakePositionsToSell)}"),
            mock.call(f"Number of positions that should be opened: {len(fakePositionsToBuy)}"),
            mock.call("Sold 2 shares of fakePositionToSell1 at 10"),
            mock.call("Sold 4 shares of fakePositionToSell2 at 10"),
            mock.call("Bought 5 shares of fakePositionToBuy1 at 10"),
            mock.call("Bought 7 shares of fakePositionToBuy2 at 10"),
        ])


if __name__ == '__main__':
    unittest.main()
