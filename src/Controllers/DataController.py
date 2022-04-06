#!/usr/bin/python

# external dependencies

# internal dependencies
from src.Types.StockExchange import StockExchange
from src.Interfaces.AlpacaInterface import AlpacaInterface
from src.Interfaces.StockIndexDataInterface import StockIndexDataInterface


"""
DataController

This is a class to encapsulate all interactions between the software and the
finsymbols library

"""
class DataController:

    def __init__(self: object):
        self.stockIndexDataInterface = StockIndexDataInterface()
        self.alpacaInterface = AlpacaInterface()


    """
    `getOrderedStockData`:  returns a sorted list of S&P500 stocks with prices
    """
    def getOrderedStockData(self: object):
        symbols = self.stockIndexDataInterface.getIndexSymbols(StockExchange.NASDAQ)
        stockData = self.alpacaInterface.getStockDataList(symbols)

        return sorted(stockData, key=lambda x: x.price, reverse=True)