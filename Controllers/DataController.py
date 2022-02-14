#!/usr/bin/python

# external dependencies
import alpaca_trade_api
import os
import finsymbols
import requests

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
        for stockSymbol, stockPrice in stockPrices.items():
            print(f"{stockSymbol} is at {stockPrice}")
