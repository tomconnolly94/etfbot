#!/usr/bin/python

# external dependencies
from typing import Dict
import apsw
import sys
from enum import Enum
from datetime import datetime
import os

# internal dependencies


class EXCLUDED_STOCK_SYMBOLS_TABLE_COLUMN_TITLE(Enum):
    SYMBOL = 1
    REASON = 2
    STOCK_EXCHANGE = 3

class PORTFOLIO_VALUE_BY_DATE_TABLE_COLUMN_TITLE(Enum):
    DATE = 1
    VALUE = 2


"""
DatabaseInterface

This is a class to encapsulate all interactions between the software and the
Alpaca API
"""
class DatabaseInterface():

    def __init__(self: object):
        # Open existing read-write (exception if it doesn't exist)
        dbFile = f"{os.getenv('DB_DIR')}/etfbot.db"
        print(dbFile)
        self.db_connection = apsw.Connection(f"{os.getenv('DB_DIR')}/etfbot.db", flags=apsw.SQLITE_OPEN_READWRITE)

        # table names
        self.EXCLUDED_STOCK_SYMBOLS_TABLE_NAME = "excluded_stock_symbols"
        self.PORTFOLIO_VALUE_BY_DATE_TABLE_NAME = "portfolio_value_by_date"

        # table field values, these maps help decouple the script from the db schema
        self.EXCLUDED_STOCK_SYMBOLS_TABLE_COLUMN_MAP: Dict[EXCLUDED_STOCK_SYMBOLS_TABLE_COLUMN_TITLE, str] = {
            EXCLUDED_STOCK_SYMBOLS_TABLE_COLUMN_TITLE.SYMBOL: "symbol",
            EXCLUDED_STOCK_SYMBOLS_TABLE_COLUMN_TITLE.REASON: "reason",
            EXCLUDED_STOCK_SYMBOLS_TABLE_COLUMN_TITLE.STOCK_EXCHANGE: "stock_exchange"
        } 
        self.PORTFOLIO_VALUE_BY_DATE_TABLE_COLUMN_MAP: Dict[PORTFOLIO_VALUE_BY_DATE_TABLE_COLUMN_TITLE, str] = {
            PORTFOLIO_VALUE_BY_DATE_TABLE_COLUMN_TITLE.DATE: "date",
            PORTFOLIO_VALUE_BY_DATE_TABLE_COLUMN_TITLE.VALUE: "value"
        }

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

    """
    `getPortfolioValueOverTime`: get the list of excluded stock symbol records from the database file
    """
    def getPortfolioValueOverTime(self):    
        return [ { "date": record[0], "value": record[1] } for record in self.db_connection.execute(f"SELECT * FROM {self.PORTFOLIO_VALUE_BY_DATE_TABLE_NAME}") ]

    """
    `getPortfolioValueForToday`: get the list of excluded stock symbol records from the database file
    """
    def _todayHasAPortfolioValue(self):
        todaysDate = datetime.today().strftime('%Y-%m-%d')
        return len([ record for record in self.db_connection.execute(f"SELECT value from {self.PORTFOLIO_VALUE_BY_DATE_TABLE_NAME} WHERE date LIKE '{todaysDate}%'") ]) > 0

    """
    `addTodaysPortfolioValue`: get the list of excluded stock symbol records from the database file
    """
    def addTodaysPortfolioValue(self, portfolioValue: int):

        if self._todayHasAPortfolioValue():
            return

        query = (f"INSERT INTO '{self.PORTFOLIO_VALUE_BY_DATE_TABLE_NAME}'"
                 f"('{self.PORTFOLIO_VALUE_BY_DATE_TABLE_COLUMN_MAP[PORTFOLIO_VALUE_BY_DATE_TABLE_COLUMN_TITLE.DATE]}', "
                 f"'{self.PORTFOLIO_VALUE_BY_DATE_TABLE_COLUMN_MAP[PORTFOLIO_VALUE_BY_DATE_TABLE_COLUMN_TITLE.VALUE]}') "
                 f"VALUES(datetime('now', 'localtime'), '{portfolioValue}');"
        )
        self.db_connection.execute(query)



if __name__ == '__main__':
    databaseInterface = DatabaseInterface()
    if len(sys.argv) == 4: # use this to add a new record quickly, usage: `python src/Interfaces/DatabaseInterface.py <symbol> <reason> <stock-exchange>``
        databaseInterface.addExcludedStockSymbol(str(sys.argv[1]), sys.argv[2], sys.argv[3])
    
        stockSymbols = databaseInterface.getExcludedStockSymbols()

        for stockSymbol in stockSymbols:
            print(stockSymbol)

    elif len(sys.argv) == 2: # use this to add a new record quickly, usage: `python src/Interfaces/DatabaseInterface.py <todays-value>``
        databaseInterface.addTodaysPortfolioValue(str(sys.argv[1]))
    
        portfolioValueOverTime = databaseInterface.getPortfolioValueOverTime()

        for pValue in portfolioValueOverTime:
            print(f"date: {pValue['date']} - value: {pValue['value']}")

    else:
        print(databaseInterface.getPortfolioValueForToday())

