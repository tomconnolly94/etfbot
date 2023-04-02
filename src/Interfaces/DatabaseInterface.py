#!/usr/bin/python

# external dependencies
import apsw

# internal dependencies


"""
DatabaseInterface

This is a class to encapsulate all interactions between the software and the
Alpaca API
"""
class DatabaseInterface():

    def __init__(self: object):
        # Open existing read-write (exception if it doesn't exist)
        self.db_connection = apsw.Connection("db/etfbot.db", flags=apsw.SQLITE_OPEN_READWRITE)
        self.excluded_stock_symbols_table_name = "excluded_stock_symbols"

    """
    `getExcludedStockSymbols`: save list of StockData items, prices and symbols from index
    """
    def getExcludedStockSymbols(self):

        for row in self.db_connection.execute(f"select * from {self.excluded_stock_symbols_table_name}"):
            print(row)
    

if __name__ == '__main__':
    databaseInterface = DatabaseInterface()
    databaseInterface.getExcludedStockSymbols()
