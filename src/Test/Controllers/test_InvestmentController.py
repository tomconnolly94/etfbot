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
    @mock.patch("src.Interfaces.AlpacaInterface.AlpacaInterface.getAvailableFunds")
    @mock.patch("src.Controllers.InvestmentController.InvestmentController._getIdealPositions")
    @mock.patch("src.Controllers.InvestmentController.logging.info")
    @mock.patch("src.Controllers.InvestmentController.InvestmentController._getPositionInIndex")
    @mock.patch("src.Interfaces.AlpacaInterface.AlpacaInterface.getOpenPositions")
    def test_rebalanceInvestments(self,
        getOpenPositionsMock,
        _getPositionInIndexMock,
        loggingMock,
        _getIdealPositionsMock,
        getAvailableFundsMock,
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
        fakeAvailableFunds = 100
        idealPositions = {
            "idealPosition1": 5,
            "idealPosition2": 7
        }

        # configure mocks
        getOpenPositionsMock.return_value = fakeOpenPositions
        _getPositionInIndexMock.side_effect = fakePositionsInIndex
        _getIdealPositionsMock.return_value = idealPositions
        getAvailableFundsMock.return_value = fakeAvailableFunds
        _getValueOfStockMock.return_value = 10

        # run testable function
        InvestmentController().rebalanceInvestments()

        # asserts
        getOpenPositionsMock.assert_called()
        self.assertEquals(8, loggingMock.call_count)
        getAvailableFundsMock.assert_called()

        sellStockMock.assert_has_calls([ mock.call(key, value) for key, value in fakeOpenPositions.items() ])
        buyStockMock.assert_has_calls([mock.call(key, value) for key, value in idealPositions.items() ])
        self.assertEquals(4, _getValueOfStockMock.call_count)
        _getValueOfStockMock.assert_has_calls([
            mock.call(list(fakeOpenPositions.keys())[0]),
            mock.call(list(fakeOpenPositions.keys())[1]),
            mock.call(list(idealPositions.keys())[0]),
            mock.call(list(idealPositions.keys())[1])
        ])

        loggingMock.assert_has_calls([
            mock.call("Number of current positions held: 2"),
            mock.call("Current positions - (symbol: index position) fakeOpenPosition1: 3, fakeOpenPosition2: 6"),
            mock.call(f"Number of positions that should be closed: {len(fakeOpenPositions)}"),
            mock.call(f"Number of positions that should be opened: {len(idealPositions)}"),
            mock.call("Sold 10 shares of fakeOpenPosition1 at 10"),
            mock.call("Sold 15 shares of fakeOpenPosition2 at 10"),
            mock.call("Bought 5 shares of idealPosition1 at 10. Money spent: 50"),
            mock.call("Bought 7 shares of idealPosition2 at 10. Money spent: 120"),
        ])


if __name__ == '__main__':
    unittest.main()
