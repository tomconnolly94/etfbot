#!/usr/bin/python

# external dependencies
from typing import Dict
import apsw
import sys
from enum import Enum

# internal dependencies


class EXCLUDED_STOCK_SYMBOLS_TABLE_COLUMN_TITLE(Enum):
    SYMBOL = 1
    REASON = 2
    STOCK_EXCHANGE = 3


"""
DatabaseInterface

This is a class to encapsulate all interactions between the software and the
Alpaca API
"""
class DatabaseInterface():

    def __init__(self: object):
        # Open existing read-write (exception if it doesn't exist)
        self.db_connection = apsw.Connection("db/etfbot.db", flags=apsw.SQLITE_OPEN_READWRITE)
        self.EXCLUDED_STOCK_SYMBOLS_TABLE_NAME = "excluded_stock_symbols"
        self.EXCLUDED_STOCK_SYMBOLS_TABLE_COLUMN_MAP: Dict[EXCLUDED_STOCK_SYMBOLS_TABLE_COLUMN_TITLE, str] = {
            EXCLUDED_STOCK_SYMBOLS_TABLE_COLUMN_TITLE.SYMBOL: "symbol",
            EXCLUDED_STOCK_SYMBOLS_TABLE_COLUMN_TITLE.REASON: "reason",
            EXCLUDED_STOCK_SYMBOLS_TABLE_COLUMN_TITLE.STOCK_EXCHANGE: "stock_exchange"
        } # map helps decouple the script from the db schema


    """
    `getExcludedStockSymbols`: get the list of excluded stock symbol records from the database file
    """
    def getExcludedStockSymbols(self):    
        return [ record[0] for record in self.db_connection.execute(f"SELECT * FROM {self.EXCLUDED_STOCK_SYMBOLS_TABLE_NAME}") ]

    """
    `addExcludedStockSymbol`: get the list of excluded stock symbol records from the database file
    """
    def addExcludedStockSymbol(self, symbol: str, reason: str, stockExchange: str):
        query = (f"INSERT INTO '{self.EXCLUDED_STOCK_SYMBOLS_TABLE_NAME}'"
                 f"('{self.EXCLUDED_STOCK_SYMBOLS_TABLE_COLUMN_MAP[EXCLUDED_STOCK_SYMBOLS_TABLE_COLUMN_TITLE.SYMBOL]}', "
                 f"'{self.EXCLUDED_STOCK_SYMBOLS_TABLE_COLUMN_MAP[EXCLUDED_STOCK_SYMBOLS_TABLE_COLUMN_TITLE.REASON]}', "
                 f"'{self.EXCLUDED_STOCK_SYMBOLS_TABLE_COLUMN_MAP[EXCLUDED_STOCK_SYMBOLS_TABLE_COLUMN_TITLE.STOCK_EXCHANGE]}') "
                 f"VALUES('{symbol}', '{reason}', '{stockExchange}');"
        )
        self.db_connection.execute(query)



if __name__ == '__main__':
    databaseInterface = DatabaseInterface()
    if len(sys.argv) == 4: # use this to add a new record quickly, usage: `python src/Interfaces/DatabaseInterface.py <symbol> <reason> <stock-exchange>``
        databaseInterface.addExcludedStockSymbol(str(sys.argv[1]), sys.argv[2], sys.argv[3])
    
    stockSymbols = databaseInterface.getExcludedStockSymbols()

    for stockSymbol in stockSymbols:
        print(stockSymbol)

