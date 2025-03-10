#!/usr/bin/python

# external dependencies
from typing import Dict
import apsw
import sys
from enum import Enum
import datetime
import os
import logging
import traceback

# internal dependencies


class EXCLUDED_STOCK_SYMBOLS_TABLE_COLUMN_TITLE(Enum):
    SYMBOL = "symbol"
    REASON = "reason"
    STOCK_EXCHANGE = "stock_exchange"


class PORTFOLIO_VALUE_BY_DATE_TABLE_COLUMN_TITLE(Enum):
    DATE = "date"
    VALUE = "value"


class INTERNAL_PAPER_PORTFOLIO_VALUE_BY_DATE_TABLE_COLUMN_TITLE(Enum):
    DATE = "date"
    VALUE = "value"
    STRATEGY_ID = "strategy_id"
    
class INTERNAL_PAPER_TRANSACTIONS_TABLE_COLUMN_TITLE(Enum):
    SYMBOL = "symbol"
    TRANSACTION_VALUE = "transaction_value"
    BUY_SELL = "buy_sell"
    DATE = "date"
    STRATEGY_ID = "strategy_id"
    ORDER_QUANTITY =" order_quantity"

    
class INTERNAL_PAPER_ACCOUNTS_TABLE_COLUMN_TITLE(Enum):
    STRATEGY_ID = "strategy_id"
    CASH = "cash"


class TIME_PERIOD(Enum):
    YEAR = 1
    MONTH = 2
    DAY = 3


"""
DatabaseInterface

This is a class to encapsulate all interactions between the software and the
Alpaca API
"""


class DatabaseInterface:

    def __init__(self: object):
        # Open existing read-write (exception if it doesn't exist)
        dbFile = f"{os.getenv('DB_DIR')}/etfbot.db"
        self.db_connection = apsw.Connection(
            dbFile, flags=apsw.SQLITE_OPEN_READWRITE
        )

        # table names
        self.EXCLUDED_STOCK_SYMBOLS_TABLE_NAME = "excluded_stock_symbols"
        self.PORTFOLIO_VALUE_BY_DATE_TABLE_NAME = "portfolio_value_by_date"
        self.INTERNAL_PAPER_PORTFOLIO_VALUE_BY_DATE_TABLE_NAME = "internal_paper_portfolio_value_by_date"
        self.INTERNAL_PAPER_TRANSACTIONS_TABLE_NAME = "internal_paper_transactions"
        self.INTERNAL_PAPER_ACCOUNTS_TABLE_NAME = "internal_paper_accounts"

    """
    `removeExcludeListItem`: get the list of excluded stock symbol records from the database file
    """

    def removeExcludeListItem(self, stockSymbol: str):
        logging.info(f"Attempting to remove {stockSymbol} from excludeList")
        return self.db_connection.execute(
            f"DELETE FROM {self.EXCLUDED_STOCK_SYMBOLS_TABLE_NAME} "
            f"WHERE {EXCLUDED_STOCK_SYMBOLS_TABLE_COLUMN_TITLE.SYMBOL.value} == '{stockSymbol}';"
        )

    """
    `getExcludedStockRecords`: get the list of excluded stock symbol records from the database file
    """

    def getExcludedStockRecords(self):
        return self.db_connection.execute(
            f"SELECT * FROM {self.EXCLUDED_STOCK_SYMBOLS_TABLE_NAME}"
        )

    """
    `getExcludedStockSymbol`: get a specific excluded stock symbol record from the database file
    """

    def getExcludedStockRecord(self, stockSymbol: str):
        return self.db_connection.execute(
            f"SELECT * FROM {self.EXCLUDED_STOCK_SYMBOLS_TABLE_NAME} WHERE "
            f"'{EXCLUDED_STOCK_SYMBOLS_TABLE_COLUMN_TITLE.SYMBOL.value}' == '{stockSymbol}'"
        )

    """
    `addExcludedStockSymbol`: get the list of excluded stock symbol records from the database file
    """

    def addExcludedStockSymbol(
        self, stockSymbol: str, reason: str, stockExchange: str
    ):
        if list(self.getExcludedStockRecord(stockSymbol)):
            logging.info(f"{stockSymbol} is already in the excludeList")
            return False
        query = (
            f"INSERT INTO {self.EXCLUDED_STOCK_SYMBOLS_TABLE_NAME}"
            f"('{EXCLUDED_STOCK_SYMBOLS_TABLE_COLUMN_TITLE.SYMBOL.value}', "
            f"'{EXCLUDED_STOCK_SYMBOLS_TABLE_COLUMN_TITLE.REASON.value}', "
            f"'{EXCLUDED_STOCK_SYMBOLS_TABLE_COLUMN_TITLE.STOCK_EXCHANGE.value}') "
            f"VALUES('{stockSymbol}', '{reason}', '{stockExchange}');"
        )
        self.db_connection.execute(query)
        logging.info(f"{stockSymbol} added to the excludeList")
        return True

    """
    `getPortfolioValueOverTime`: get the values over time of the external paper trading strategy 
    """

    def getPortfolioValueOverTime(
        self, timePeriod: TIME_PERIOD = TIME_PERIOD.YEAR
    ):
        timePeriodTimeDeltaMap = {
            TIME_PERIOD.YEAR: datetime.timedelta(days=365),
            TIME_PERIOD.MONTH: datetime.timedelta(days=31),
            TIME_PERIOD.DAY: datetime.timedelta(days=1),
        }

        today = datetime.datetime.today()
        startDate = (today - timePeriodTimeDeltaMap[timePeriod]).strftime(
            "%Y-%m-%d"
        )
        return [
            {"date": record[0], "value": record[1]}
            for record in self.db_connection.execute(
                f"SELECT * FROM {self.PORTFOLIO_VALUE_BY_DATE_TABLE_NAME} WHERE date > {startDate}"
            )
        ]

    """
    `getInternalPaperTradingValueOverTime`: get the values over time of an internal paper trading strategy 
    """

    def getInternalPaperTradingValueOverTime(
        self, 
        strategyId,
        timePeriod: TIME_PERIOD = TIME_PERIOD.YEAR
    ):
        timePeriodTimeDeltaMap = {
            TIME_PERIOD.YEAR: datetime.timedelta(days=365),
            TIME_PERIOD.MONTH: datetime.timedelta(days=31),
            TIME_PERIOD.DAY: datetime.timedelta(days=1),
        }

        today = datetime.datetime.today()
        startDate = (today - timePeriodTimeDeltaMap[timePeriod]).strftime(
            "%Y-%m-%d"
        ) + " 00:00:00"

        return [
            {"date": record[0], "value": record[1]}
            for record in self.db_connection.execute(
                f"SELECT * FROM '{self.INTERNAL_PAPER_PORTFOLIO_VALUE_BY_DATE_TABLE_NAME}' WHERE date > '{startDate}' AND strategy_id == '{strategyId}'"
            )
        ]
    
    """
    `addTodaysInternalPortfolioValues`: insert into the db a portfolio value for a specific internal paper strategy 
    """

    def addTodaysInternalPortfolioValues(self, portfolioValue: int, strategy_id: int):
        
        todaysDate = datetime.datetime.today().strftime("%Y-%m-%d")
        if len([record
            for record in self.db_connection.execute(
                f"SELECT value from {self.INTERNAL_PAPER_PORTFOLIO_VALUE_BY_DATE_TABLE_NAME} WHERE date LIKE '{todaysDate}%' and strategy_id={int(strategy_id)}"
            )]) > 0:
            logging.info("record already exists, skipping insert")
            return

        query = (
            f"INSERT INTO '{self.INTERNAL_PAPER_PORTFOLIO_VALUE_BY_DATE_TABLE_NAME}' "
            f"('{INTERNAL_PAPER_PORTFOLIO_VALUE_BY_DATE_TABLE_COLUMN_TITLE.DATE.value}', "
            f"'{INTERNAL_PAPER_PORTFOLIO_VALUE_BY_DATE_TABLE_COLUMN_TITLE.VALUE.value}', "
            f"'{INTERNAL_PAPER_PORTFOLIO_VALUE_BY_DATE_TABLE_COLUMN_TITLE.STRATEGY_ID.value}') "
            f"VALUES('{todaysDate}', '{portfolioValue}', {int(strategy_id)});"
        )
        return self._executeWriteQuery(query=query)

    
    """
    `getInternalPaperTradingStrategyIds`: get a list of all strategyIds currently in use 
    """

    def getInternalPaperTradingStrategyIds(self):

        query = (
            f"select {INTERNAL_PAPER_ACCOUNTS_TABLE_COLUMN_TITLE.STRATEGY_ID.value} from {self.INTERNAL_PAPER_ACCOUNTS_TABLE_NAME};"
        )
    
        return [
            int(record[0])
            for record in self.db_connection.execute(query)
        ]
    
    """
    `getInternalPaperTradingOrdersByStrategy`: get a list of all symbols owned by a specific strategy 
    """

    def getInternalPaperTradingOrdersByStrategy(self, strategyId: int):

        query = (
            f"SELECT symbol, transaction_value, buy_sell, date, order_quantity FROM {self.INTERNAL_PAPER_TRANSACTIONS_TABLE_NAME} WHERE strategy_id={strategyId} ORDER BY date DESC;"
        )

        return [
            { 
                "symbol": record[0],
                "transactionValue": record[1],
                "buySell": record[2],
                "date": record[3],
                "orderQuantity": record[4],
            } 
            for record in self.db_connection.execute(query)
        ]

    """
    `createNewInternalPaperTradingOrder`: create new order for a symbol in a strategy at a price and quantity 
    """

    def createNewInternalPaperTradingOrder(self, 
                                           strategyId: int, 
                                           symbol, 
                                           transactionValue, 
                                           buySell,
                                           orderQuantity, 
                                           date = datetime.datetime.today().strftime("%Y-%m-%d")):

        query = (
            f"INSERT INTO {self.INTERNAL_PAPER_TRANSACTIONS_TABLE_NAME} "
            f"({INTERNAL_PAPER_TRANSACTIONS_TABLE_COLUMN_TITLE.SYMBOL.value}, "
            f"{INTERNAL_PAPER_TRANSACTIONS_TABLE_COLUMN_TITLE.TRANSACTION_VALUE.value}, "
            f"{INTERNAL_PAPER_TRANSACTIONS_TABLE_COLUMN_TITLE.BUY_SELL.value}, " 
            f"{INTERNAL_PAPER_TRANSACTIONS_TABLE_COLUMN_TITLE.DATE.value}, "
            f"{INTERNAL_PAPER_TRANSACTIONS_TABLE_COLUMN_TITLE.STRATEGY_ID.value}, "
            f"{INTERNAL_PAPER_TRANSACTIONS_TABLE_COLUMN_TITLE.ORDER_QUANTITY.value}) "
            f"VALUES ('{symbol}', {transactionValue}, '{buySell}', '{date}', {strategyId}, {orderQuantity});"
        )

        return self._executeWriteQuery(str(query))
    
    "INSERT INTO internal_paper_transactions (symbol, transaction_value, buy_sell, date,  order_quantity) VALUES (ENPH, 58.69, SELL, 2025-03-06, 3, 1.0) WHERE strategy_id=3;"

    """
    `getInternalPaperTradingAccountCash`: get cash value on the account for a strategyId
    """

    def getInternalPaperTradingAccountCash(self, strategyId: int):

        query = (
            f"SELECT " 
            f"{INTERNAL_PAPER_ACCOUNTS_TABLE_COLUMN_TITLE.CASH.value} "
            f"FROM {self.INTERNAL_PAPER_ACCOUNTS_TABLE_NAME} "
            f"WHERE {INTERNAL_PAPER_ACCOUNTS_TABLE_COLUMN_TITLE.STRATEGY_ID.value}={strategyId} "
        )

        logging.debug(f"getInternalPaperTradingAccountCash query={query}")

        rawResult = list(self.db_connection.execute(query))

        if len(rawResult) < 1 or len(rawResult[0]) < 1:
            logging.error(f"Something went wrong when accessing account cash for strategy={strategyId} with query={query}")
            return -1
        
        result = rawResult[0][0]
        logging.info(f"result: {result}")

        return result

    """
    `updateInternalPaperTradingAccountCash`: get cash value on the account for a strategyId
    """

    def updateInternalPaperTradingAccountCash(self, strategyId: int, newCashValue: float):

        query = (
            f"UPDATE {self.INTERNAL_PAPER_ACCOUNTS_TABLE_NAME} " 
            f"SET {INTERNAL_PAPER_ACCOUNTS_TABLE_COLUMN_TITLE.CASH.value} = {newCashValue} "
            f"WHERE {INTERNAL_PAPER_ACCOUNTS_TABLE_COLUMN_TITLE.STRATEGY_ID.value} = {strategyId} "
        )

        logging.debug(f"updateInternalPaperTradingAccountCash query={query}")

        return self._executeWriteQuery(query)

    """
    `_tableHasAValueForToday`: return true if there is a portfolioValue for today in the specified table
    """

    def _tableHasAValueForToday(self, table_name: str):
        todaysDate = datetime.datetime.today().strftime("%Y-%m-%d")
        return (
            len(
                [
                    record
                    for record in self.db_connection.execute(
                        f"SELECT value from {table_name} WHERE date LIKE '{todaysDate}%'"
                    )
                ]
            )
            > 0
        )

    """
    `addTodaysExternalPortfolioValue`: get the list of excluded stock symbol records from the database file
    """

    def addTodaysExternalPortfolioValue(self, portfolioValue: int):

        if self._tableHasAValueForToday(self.PORTFOLIO_VALUE_BY_DATE_TABLE_NAME):
            return

        query = (
            f"INSERT INTO '{self.PORTFOLIO_VALUE_BY_DATE_TABLE_NAME}'"
            f"('{PORTFOLIO_VALUE_BY_DATE_TABLE_COLUMN_TITLE.DATE.value}', "
            f"'{PORTFOLIO_VALUE_BY_DATE_TABLE_COLUMN_TITLE.VALUE.value}') "
            f"VALUES(datetime('now', 'localtime'), '{portfolioValue}');"
        )
        return self._executeWriteQuery(query=query)

    """
    `executeQuery`: execute database query with handling for common errors and consistent logging
    """

    def _executeWriteQuery(
        self,
        query: str,
    ):
        try:
            self.db_connection.execute(query)
            return True
        except apsw.SQLError:
            logging.error(
                f"Problem with database SQL query={query} exception:"
                f"\n{traceback.format_exc()}".rstrip()
            )
            return False


if __name__ == "__main__":
    databaseInterface = DatabaseInterface()
    if (
        len(sys.argv) == 4
    ):  # use this to add a new record quickly, usage: `python src/Interfaces/DatabaseInterface.py <symbol> <reason> <stock-exchange>``
        databaseInterface.addExcludedStockSymbol(
            str(sys.argv[1]), sys.argv[2], sys.argv[3]
        )

        stockRecords = databaseInterface.getExcludedStockRecords()

        for stockRecord in stockRecords:
            print(stockRecord)

    elif (
        len(sys.argv) == 2
    ):  # use this to add a new record quickly, usage: `python src/Interfaces/DatabaseInterface.py <todays-value>``
        databaseInterface.addTodaysExternalPortfolioValue(str(sys.argv[1]))

        portfolioValueOverTime = databaseInterface.getPortfolioValueOverTime()

        for pValue in portfolioValueOverTime:
            print(f"date: {pValue['date']} - value: {pValue['value']}")

    else:
        print(databaseInterface.getPortfolioValueForToday())
