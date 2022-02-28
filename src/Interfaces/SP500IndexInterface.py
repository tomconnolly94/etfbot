#!/usr/bin/python

# external dependencies
import finsymbols


"""
SP500IndexInterface

This is a class to encapsulate all interactions between the software and the
finsymbols library

"""
class SP500IndexInterface:

    def __init__(self: object):
        pass


    """
    `getIndexSymbols`: returns a list of symbols in the S&P500 index 
    """
    def getIndexSymbols(self: object) -> 'list[str]':
        sp500 = finsymbols.get_sp500_symbols()
        symbols = [item["symbol"].replace("\n", "") for item in sp500]
        return symbols
        