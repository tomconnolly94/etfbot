#!/usr/bin/python

# external dependencies
from alpaca.data.historical.stock import StockHistoricalDataClient
from alpaca.data.requests import StockLatestQuoteRequest
from alpaca.trading.requests import (
    MarketOrderRequest,
    GetOrdersRequest,
)
from alpaca.trading.enums import OrderSide, TimeInForce, QueryOrderStatus
from alpaca.trading.models import TradeAccount, Position
from alpaca.common.exceptions import APIError
from requests.exceptions import HTTPError
import os
import logging
import sys


# internal dependencies
sys.path.append(
    os.path.dirname(
        os.path.dirname(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        )
    )
)  # make webapp and common sub projects accessible
from investmentapp.src.Interfaces.InternalPaperTradingClient import InternalPaperTradingClient
from investmentapp.src.Types.StockOrder import StockOrder
from investmentapp.src.Interfaces.DatabaseInterface import DatabaseInterface
from investmentapp.src.Types.StockExchange import StockExchange
from investmentapp.src.Interfaces.InvestingInterface import InvestingInterface
from investmentapp.src.Types.StockData import StockData
from investmentapp.src.Interfaces.StockIndexDataInterface import (
    StockIndexDataInterface,
)


"""
AlpacaInterface v2

This is a class to encapsulate all interactions between the software and the
Alpaca API

Github: https://github.com/alpacahq/alpaca-py
API reference: https://alpaca.markets/docs/api-references/trading-api/
Python sdk docs: https://alpaca.markets/docs/python-sdk/trading.html#trading
"""


class InternalPaperTradingInterface(InvestingInterface):

    def __init__(self: object, strategyId: str):

        # no keys required for crypto data
        self.historicalDataAPI = StockHistoricalDataClient(
            os.getenv("ALPACA_TRADING_KEY_ID"),
            os.getenv("ALPACA_TRADING_SECRET_KEY"),
        )

        self.devMode = os.getenv("TRADING_DEV_MODE", "False").lower() == "true"

        self._sortedFullStockCache = []
        self._stockIndexDataInterface = StockIndexDataInterface()
        self._databaseInterface = DatabaseInterface()
        self.tradingAPI = InternalPaperTradingClient(self._databaseInterface, strategyId)
        logging.info(
            f"InternalPaperTradingInterface initialised. devMode={self.devMode} env={os.getenv('TRADING_DEV_MODE', 'False')}"
        )

    """
    `getStockCache`: save list of StockData items, prices and symbols from index
    """

    def getStockCache(self: object) -> "list[StockData]":
        if not self._sortedFullStockCache:
            indexSymbols = self._stockIndexDataInterface.getIndexSymbols(
                StockExchange.SP500
            )
            self._sortedFullStockCache = sorted(
                self.getStockDataList(indexSymbols),
                key=lambda x: x.price,
                reverse=True,
            )
            # logging.debug(f"self._sortedFullStockCache: {self._sortedFullStockCache}")
        return self._sortedFullStockCache

    """
    `buyStock`: buy `quantity` number of `stockSymbol`
    test: None
    """

    def buyStock(self, stockSymbol: str, quantity: int) -> None:
        self._submitOrder(stockSymbol, quantity, OrderSide.BUY)

    """
    `sellStock`: execute sell trade of stock `stockSymbol` for `quantity` units
    """

    def sellStock(self, stockSymbol: str, quantity: int) -> None:
        self._submitOrder(stockSymbol, quantity, OrderSide.SELL)

    """
    `getAvailableFunds`: return any uninvested funds
    """

    def getAvailableFunds(self: object) -> float:
        return float(self._getAlpacaAccount().cash)

    """
    `getPortfolioValue`: return the value of stocks + uninvested funds
    """

    def getPortfolioValue(self: object) -> float:
        return float(self._getAlpacaAccount().equity)

    """
    `getOpenPositions`: return all positions currently held
    """

    def getOpenPositions(self: object) -> "dict[str, int]":
        positions: "list[Position]" = self.tradingAPI.get_all_positions()
        return {position.symbol: int(position.qty) for position in positions}

    """
    `getStockDataList`: return stock data on each stockSymbol in `stockSymbols`
    """

    def getStockDataList(
        self: object, stockSymbols: "list[str]"
    ) -> "list[StockData]":
        request = StockLatestQuoteRequest(symbol_or_symbols=stockSymbols)
        stockDataList = self.historicalDataAPI.get_stock_latest_quote(request)
        logging.info(f"Retrieved stock data for {len(stockDataList)} stocks")
        logging.debug(f"Stock symbols: {stockDataList.keys()}")

        return [
            StockData(symbol, stockData.bid_price)
            for symbol, stockData in stockDataList.items()
        ]

    def openOrdersExist(self):
        request_params = GetOrdersRequest(
            status=QueryOrderStatus.OPEN, limit=500
        )
        return len(list(self.tradingAPI.get_orders(filter=request_params)))

    """
    `getAllOrders`: get all finalised order records
    test: None
    """

    def getAllOrders(
        self, earliestTimestamp, latestTimestamp
    ) -> list[StockOrder]:
        get_orders_data = GetOrdersRequest(
            status=QueryOrderStatus.CLOSED,
            limit=500,
            direction="asc",
            after=earliestTimestamp,
            until=latestTimestamp,
        )

        return [
            StockOrder(order)
            for order in self.tradingAPI.get_orders(filter=get_orders_data)
        ]

    """
    `_submitOrder`: submits an order to the alpaca api to buy/sell
    test: None
    """

    def _submitOrder(self, stockSymbol, quantity, orderType: OrderSide) -> bool:

        if self.devMode:
            logging.info(
                f"_submitOrder ({orderType.name}) called for symbol={stockSymbol} quantity={quantity} , devMode={self.devMode} so no order was submitted"
            )
            return
        
        logging.info(f"_submitOrder ({orderType.name}) ({orderType}) called for symbol={stockSymbol} quantity={quantity}")

        # preparing order data
        market_order_data = MarketOrderRequest(
            symbol=stockSymbol,
            qty=quantity,
            side=orderType,
            time_in_force=TimeInForce.DAY,
        )

        # submit market order
        try:
            return self.tradingAPI.submit_order(order_data=market_order_data)
        except (HTTPError, APIError) as error:
            logging.error(f"self.tradingAPI.submit_order failed. stockSymbol={stockSymbol} quantity={quantity} orderType={orderType} error={error}")               
            return False

    """
    `_getAlpacaAccount`: returns information about the alpaca account associated with the details above
    test: None
    """

    def _getAlpacaAccount(self) -> TradeAccount:
        return self.tradingAPI.get_account()


if __name__ == "__main__":
    pass
