#!/usr/bin/python

# external dependencies
import alpaca_trade_api
from alpaca_trade_api.entity import Position
import os

from numpy import number


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

    def getStockPrices(self: object, stockSymbols: list):
        stockData: dict = self.getStockData(stockSymbols)
        stockPrices: dict = {}

        for symbol, data in stockData.items():
            print(f"{symbol}: {data}")
            stockPrices[symbol] = data.latest_trade.p

        return stockPrices

    def getStockDataList(self: object, stockSymbols: 'list[str]') -> dict:
        stockData: dict = self.api.get_snapshots(stockSymbols)

        return [ stockDataItem[1] for stockDataItem in stockData.items() ]

    def buyStock(self, stockSymbol: str, quantity: number):
        self._submitOrder(stockSymbol, quantity, "buy")
    
    def sellStock(self, stockSymbol: str, quantity: number):
        self._submitOrder(stockSymbol, quantity, "sell")

    def getOpenPositions(self: object) -> 'list[Position]':
        return self.api.list_positions()