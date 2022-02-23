#!/usr/bin/python

class StockData:

    def __init__(self: object, symbol: str, stockPrice: int = 0, fundWeighting: float = 0.0):
        self.symbol = symbol
        self.price = stockPrice
        self.fundWeighting = fundWeighting