#!/usr/bin/python

# external dependencies
import itertools
import unittest
from unittest import mock
from unittest.mock import MagicMock

# internal dependencies
from investmentapp.src.Strategies.StockChoiceStrategies.StockChoiceStrategy import (
    StockChoiceStrategy,
)
from investmentapp.src.Controllers.InvestmentController import InvestmentController


class TestInvestmentController(unittest.TestCase):

    @mock.patch(
        "investmentapp.src.Controllers.InvestmentController.InvestmentController._getValueOfStock"
    )
    @mock.patch(
        "investmentapp.src.Controllers.InvestmentController.StockChoiceController"
    )
    @mock.patch("investmentapp.src.Controllers.InvestmentController.logging.info")
    @mock.patch(
        "investmentapp.src.Controllers.InvestmentController.InvestmentController._getPositionInIndex"
    )
    def test_rebalanceInvestments(
        self,
        _getPositionInIndexMock,
        loggingMock,
        StockChoiceControllerMock,
        _getValueOfStockMock,
    ):

        # configure fake data
        fakeOpenPositions = {
            "fakeOpenPosition1": 10,
            "fakeOpenPosition2": 15,
            "fakeOpenPosition3": 20,
        }
        # fakeOpenPositionsOriginal is necesary for comparison purposes as fakeOpenPositions is mutable and changed
        # during `InvestmentController().rebalanceInvestments()`
        fakeOpenPositionsOriginal = fakeOpenPositions.copy()

        fakePositionsInIndex = [3, 6, 7]
        fakeAvailableFunds = 100
        fakeBuyOrders = {"fakeBuyOrder1": 10, "fakeBuyOrder2": 15}
        fakeSellOrders = ["fakeOpenPosition1", "fakeOpenPosition2"]
        fakeStrategyName = "fakeStrategyName"
        stockChoiceStrategy = "stockChoiceStrategy"

        class FakeStockChoiceStrategy(StockChoiceStrategy):

            def __init__(self, buyOrders, sellOrders):
                self.buyOrders = buyOrders
                self.sellOrders = sellOrders

            def getBuyOrders(self, availableFunds, existingPositions: "dict[str, int]"):
                return self.buyOrders

            def getSellOrders(self):
                return self.sellOrders

        # configure mocks
        AlpacaInterfaceMagicMock = MagicMock()
        AlpacaInterfaceMagicMock.getOpenPositions.return_value = fakeOpenPositions
        AlpacaInterfaceMagicMock.getAvailableFunds.return_value = fakeAvailableFunds
        AlpacaInterfaceMagicMock.openOrdersExist.return_value = False
        fakeInvestingInterface = AlpacaInterfaceMagicMock
        _getPositionInIndexMock.side_effect = fakePositionsInIndex
        StockChoiceControllerMagicMock = MagicMock()
        StockChoiceControllerMagicMock.getStockChoiceStrategy.return_value = (
            FakeStockChoiceStrategy(fakeBuyOrders, fakeSellOrders)
        )
        StockChoiceControllerMock.return_value = StockChoiceControllerMagicMock
        _getValueOfStockMock.return_value = 10

        # run testable function
        InvestmentController(fakeStrategyName, stockChoiceStrategy, fakeInvestingInterface).rebalanceInvestments()

        # asserts
        AlpacaInterfaceMagicMock.getOpenPositions.assert_called()
        AlpacaInterfaceMagicMock.openOrdersExist.assert_called()
        self.assertEqual(12, loggingMock.call_count)
        AlpacaInterfaceMagicMock.getAvailableFunds.assert_called()

        AlpacaInterfaceMagicMock.sellStock.assert_has_calls(
            [
                mock.call(
                    list(fakeOpenPositionsOriginal.keys())[0],
                    list(fakeOpenPositionsOriginal.values())[0],
                ),
                mock.call(
                    list(fakeOpenPositionsOriginal.keys())[1],
                    list(fakeOpenPositionsOriginal.values())[1],
                ),
            ]
        )
        AlpacaInterfaceMagicMock.buyStock.assert_has_calls(
            [mock.call(key, value) for key, value in fakeBuyOrders.items()]
        )
        self.assertEqual(4, _getValueOfStockMock.call_count)
        _getValueOfStockMock.assert_has_calls(
            [
                mock.call(fakeSellOrders[0]),
                mock.call(fakeSellOrders[1]),
                mock.call(list(fakeBuyOrders.keys())[0]),
                mock.call(list(fakeBuyOrders.keys())[1]),
            ]
        )

        loggingMock.assert_has_calls(
            [
                mock.call(
                    f"Number of current positions held: {len(fakeOpenPositionsOriginal)}"
                ),
                mock.call(
                    "Current positions - (symbol: index position) fakeOpenPosition1: 3, fakeOpenPosition2: 6, fakeOpenPosition3: 7"
                ),
                mock.call(
                    f"Number of positions that can be sold {len(fakeSellOrders)}"
                ),
                mock.call(
                    f"Number of positions that will be closed: {len(fakeSellOrders)}"
                ),
                mock.call("Sold 10 shares of fakeOpenPosition1 at 10"),
                mock.call("Sold 15 shares of fakeOpenPosition2 at 10"),
                mock.call(f"Available funds for new investments: {fakeAvailableFunds}"),
                mock.call(
                    f"Number of positions that will be opened: {len(fakeBuyOrders)}"
                ),
                mock.call("Attempting to buy 10 shares of fakeBuyOrder1 at 10."),
                mock.call("Buy successful, total money spent: 100"),
                mock.call("Attempting to buy 15 shares of fakeBuyOrder2 at 10."),
                mock.call("Buy successful, total money spent: 250"),
            ]
        )


if __name__ == "__main__":
    unittest.main()
