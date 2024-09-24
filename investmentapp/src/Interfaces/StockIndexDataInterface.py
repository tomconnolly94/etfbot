#!/usr/bin/python

# external dependencies
import finsymbols

from investmentapp.src.Types.StockExchange import StockExchange


"""
StockIndexDataInterface

This is a class to encapsulate all interactions between the software and the
finsymbols library

"""

import bs4 as bs
import requests


class StockIndexDataInterface:

    def __init__(self: object):
        self._stockExchangesUSA = [
            StockExchange.NASDAQ,
            StockExchange.SP500,
            StockExchange.AMEX,
            StockExchange.NYSE,
        ]
        self._stockExchangesUK = [StockExchange.FTSE100]
        pass

    """
    `getIndexSymbols`: returns a list of symbols in the S&P500 index - needs work, only sp500 is an index
    """

    def getIndexSymbols(self: object, stockExchange: StockExchange) -> "list[str]":

        if stockExchange == StockExchange.NASDAQ:
            raise NotImplementedError("NASDAQ Stock Index data not connected yet")
        if stockExchange == StockExchange.SP500:
            return self._getSPY500TickerSymbols()
        if stockExchange == StockExchange.AMEX:
            raise NotImplementedError("AMEX Stock Index data not connected yet")
        if stockExchange == StockExchange.NYSE:
            raise NotImplementedError("NYSE Stock Index data not connected yet")
        if stockExchange == StockExchange.FTSE100:
            raise NotImplementedError("FTSE 100 Stock Index data not connected yet")

    """
    `_getSPY500TickerSymbols`: accesses wikipdia for the list of symbols in the SPY500 
    """

    def _getSPY500TickerSymbols(self):
        resp = requests.get("https://en.wikipedia.org/wiki/List_of_S%26P_500_companies")
        soup = bs.BeautifulSoup(resp.text, "lxml")
        table = soup.find("table", {"id": "constituents"})
        numRowsToTrim = 1
        symbolColumnNum = 0
        tickers = []

        for row in table.findAll("tr")[numRowsToTrim:]:
            ticker = row.findAll("td")[symbolColumnNum].text
            tickers.append(ticker.rstrip())

        return tickers
