#!/usr/bin/python

# external dependencies
import finsymbols


class SP500IndexInterface:

    def __init__(self: object):
        pass


    def getIndexSymbols(self: object):
        sp500 = finsymbols.get_sp500_symbols()
        symbols = [item["symbol"].replace("\n", "") for item in sp500]
        return symbols