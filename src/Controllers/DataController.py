#!/usr/bin/python

# external dependencies

# internal dependencies
from src.Interfaces.AlpacaInterface import AlpacaInterface
from src.Interfaces.SP500IndexInterface import SP500IndexInterface


"""
DataController

This is a class to encapsulate all interactions between the software and the
finsymbols library

"""
class DataController:

    def __init__(self: object):
        self.sP500IndexInterface = SP500IndexInterface()
        self.alpacaInterface = AlpacaInterface()


    """
    `getOrderedStockData`:  returns a sorted list of S&P500 stocks with prices
    """
    def getOrderedStockData(self: object):
        symbols = self.sP500IndexInterface.getIndexSymbols()
        stockData = self.alpacaInterface.getStockDataList(symbols)

        return sorted(stockData, key=lambda x: x.latest_trade.p, reverse=True)