#!/usr/bin/python

# external dependencies

# internal dependencies
from Interfaces.AlpacaInterface import AlpacaInterface
from Interfaces.SP500IndexInterface import SP500IndexInterface


class DataController:

    def __init__(self: object):
        self.sP500IndexInterface = SP500IndexInterface()
        self.alpacaInterface = AlpacaInterface()

    def getIndexSymbolsWithValues(self: object):
        symbols = self.sP500IndexInterface.getIndexSymbols()
        stockPrices = self.alpacaInterface.getStockPrices(symbols)

        return stockPrices

    def getOrderedStockData(self: object):
        symbols = self.sP500IndexInterface.getIndexSymbols()
        stockData = self.alpacaInterface.getStockDataList(symbols)

        return sorted(stockData, key=lambda x: x.latest_trade.p, reverse=True)