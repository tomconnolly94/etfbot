#!/usr/bin/python

# external dependencies
import alpaca_trade_api
from alpaca_trade_api.entity import Position
import os

from numpy import number

from Types.StockData import StockData


class AlpacaInterface:

    def __init__(self: object):
        # instantiate REST API
        self.api = alpaca_trade_api.REST(os.getenv("ALPACA_TRADING_KEY_ID"), os.getenv("ALPACA_TRADING_SECRET_KEY"), os.getenv("ALPACA_TRADING_URL"), api_version='v2')
    

    def _submitOrder(self, stockSymbol, quantity, order):
        self.api.submit_order(
            symbol=stockSymbol, 
            qty=quantity, 
            side=order
        )


    def _getAlpacaAccount(self):
        return self.api.get_account()

    def getAvailableFunds(self):
        return float(self._getAlpacaAccount().cash)


    def getPortfolioValue(self):
        return float(self._getAlpacaAccount().equity)


    def getStockDataList(self: object, stockSymbols: 'list[str]') -> dict:
        stockSnapShots: dict = self.api.get_snapshots(stockSymbols)
        return [ StockData(symbol, snapshot.latest_trade.p) for symbol, snapshot in stockSnapShots.items() ]


    def buyStock(self, stockSymbol: str, quantity: number):
        self._submitOrder(stockSymbol, quantity, "buy")
    

    def sellStock(self, stockSymbol: str, quantity: number):
        self._submitOrder(stockSymbol, quantity, "sell")


    def getOpenPositions(self: object) -> 'list[Position]':
        positions = self.api.list_positions()
        return { position.symbol: int(position.qty) for position in positions }