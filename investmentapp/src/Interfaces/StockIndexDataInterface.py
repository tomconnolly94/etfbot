#!/usr/bin/python

# external dependencies
import finsymbols

from investmentapp.src.Types.StockExchange import StockExchange


"""
StockIndexDataInterface

This is a class to encapsulate all interactions between the software and the
finsymbols library

"""
class StockIndexDataInterface:

    def __init__(self: object):
        self._stockExchangesUSA = [ StockExchange.NASDAQ, StockExchange.SP500, StockExchange.AMEX, StockExchange.NYSE ]
        self._stockExchangesUK = [ StockExchange.FTSE100 ]
        pass


    """
    `getIndexSymbols`: returns a list of symbols in the S&P500 index - needs work, only sp500 is an index
    """
    def getIndexSymbols(self: object, stockExchange: StockExchange) -> 'list[str]':
        if stockExchange == StockExchange.NASDAQ:
            return self.__processFinSymbolsResults(finsymbols.get_nasdaq_symbols())
        if stockExchange == StockExchange.SP500:
            return self.__processFinSymbolsResults(finsymbols.get_sp500_symbols())
        if stockExchange == StockExchange.AMEX:
            return self.__processFinSymbolsResults(finsymbols.get_amex_symbols())
        if stockExchange == StockExchange.NYSE:
            return self.__processFinSymbolsResults(finsymbols.get_nyse_symbols())
        if stockExchange == StockExchange.FTSE100:
            raise NotImplementedError("FTSE 100 Stock Index data not connected yet")
        
    
    """
    `__processFinSymbolsResults`: processes the raw data from finsymbols into a list of stock symbols 
    """
    def __processFinSymbolsResults(self, input):
        return [item["symbol"].replace("\n", "") for item in input]
