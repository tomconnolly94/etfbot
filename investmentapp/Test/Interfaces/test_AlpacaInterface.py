#!/usr/bin/python

# external dependencies
import itertools
import unittest
from unittest import mock
from unittest.mock import MagicMock
from alpaca.trading.enums import OrderSide
from alpaca.common.exceptions import APIError

# internal dependencies
from investmentapp.src.Interfaces.AlpacaInterface import AlpacaInterface


class TestAlpacaInterface(unittest.TestCase):

    @mock.patch("investmentapp.src.Interfaces.AlpacaInterface.DatabaseInterface")
    @mock.patch("investmentapp.src.Interfaces.AlpacaInterface.StockIndexDataInterface")
    @mock.patch("investmentapp.src.Interfaces.AlpacaInterface.StockHistoricalDataClient")
    @mock.patch("investmentapp.src.Interfaces.AlpacaInterface.BrokerClient")
    @mock.patch("investmentapp.src.Interfaces.AlpacaInterface.TradingClient")
    def test__submitOrder_passes(self, 
                                  tradingClientMock, 
                                  BrokerClientMock, 
                                  StockHistoricalDataClientMock, 
                                  StockIndexDataInterfaceMock, 
                                  DatabaseInterfaceMock):

        # configure fake data
        stockSymbol = "fakeStockSymbol"
        quantity = 2
        orderType = OrderSide.BUY

        # configure mocks
        tradingClientMock = MagicMock
        BrokerClientMock = MagicMock
        StockHistoricalDataClientMock = MagicMock

        # run testable function
        alpacaInterface = AlpacaInterface()
        alpacaInterface.devMode = False
        result = alpacaInterface._submitOrder(stockSymbol, quantity, orderType)

        # asserts
        self.assertTrue(result)
        alpacaInterface.tradingAPI.submit_order.assert_called_once()

    @mock.patch("investmentapp.src.Interfaces.AlpacaInterface.DatabaseInterface")
    @mock.patch("investmentapp.src.Interfaces.AlpacaInterface.StockIndexDataInterface")
    @mock.patch("investmentapp.src.Interfaces.AlpacaInterface.StockHistoricalDataClient")
    @mock.patch("investmentapp.src.Interfaces.AlpacaInterface.BrokerClient")
    @mock.patch("investmentapp.src.Interfaces.AlpacaInterface.TradingClient")
    def test__submitOrder_failsWithAPIError(self, 
                                  tradingClientMock, 
                                  BrokerClientMock, 
                                  StockHistoricalDataClientMock, 
                                  StockIndexDataInterfaceMock, 
                                  DatabaseInterfaceMock):

        # configure fake data
        stockSymbol = "fakeStockSymbol"
        quantity = 2
        orderType = OrderSide.BUY

        # configure mocks
        tradingClientMock = MagicMock
        BrokerClientMock = MagicMock
        StockHistoricalDataClientMock = MagicMock
        alpacaInterface = AlpacaInterface()
        alpacaInterface.devMode = False
        alpacaInterface.tradingAPI.submit_order.side_effect = APIError("test failure")

        # run testable function
        result = alpacaInterface._submitOrder(stockSymbol, quantity, orderType)

        # asserts
        self.assertFalse(result)
        alpacaInterface.tradingAPI.submit_order.assert_called_once()


if __name__ == "__main__":
    unittest.main()
