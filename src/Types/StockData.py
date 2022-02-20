#!/usr/bin/python

class StockData:

    def __init__(self: object, symbol: str, stockPrice: int, fundWeighting: float):
        self.symbol = symbol
        self.price = stockPrice
        self.fundWeighting = fundWeighting