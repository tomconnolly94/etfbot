#!/usr/bin/python

"""
StockData

This is a model class to represent a stock within the program

"""
class StockData:

    def __init__(self: object, symbol: str, stockPrice: int = 0, fundWeighting: float = 0.0):
        self.symbol = symbol
        self.price = stockPrice
        self.fundWeighting = fundWeighting
