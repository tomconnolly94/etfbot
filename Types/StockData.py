#!/usr/bin/python

# external dependencies
from alpaca_trade_api.entity_v2 import TradeV2

class StockData:

    def __init__(self: object, symbol: str, stockInfo: TradeV2):
        self.symbol = symbol
        self.price = stockInfo.p