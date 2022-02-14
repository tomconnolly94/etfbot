#!/usr/bin/python

# external dependencies
import alpaca_trade_api
import os


class AlpacaInterface:

    def __init__(self: object):
        # instantiate REST API
        self.api = alpaca_trade_api.REST(os.getenv("ALPACA_TRADING_KEY_ID"), os.getenv("ALPACA_TRADING_SECRET_KEY"), os.getenv("ALPACA_TRADING_URL"), api_version='v2')

    
    def getStockPrices(self: object, stockSymbols: list):
        stockData = self.api.get_snapshots(stockSymbols)
        stockPrices = {}

        for symbol, data in stockData.items():
            stockPrices[symbol] = data.latest_trade.p

        return stockPrices
