#!/usr/bin/python

# external dependencies
import alpaca_trade_api
from alpaca_trade_api.entity import Account, PortfolioHistory
import os
import logging
import json

# internal dependencies
from src.Types.StockExchange import StockExchange
from src.Interfaces.InvestingInterface import InvestingInterface
from src.Types.StockData import StockData
from src.Interfaces.StockIndexDataInterface import StockIndexDataInterface


"""
AlpacaInterface

This is a class to encapsulate all interactions between the software and the
Alpaca API
"""
class AlpacaInterface(InvestingInterface):

    def __init__(self: object):
        # instantiate REST API
        self.api = alpaca_trade_api.REST(os.getenv("ALPACA_TRADING_KEY_ID"), os.getenv("ALPACA_TRADING_SECRET_KEY"), os.getenv("ALPACA_TRADING_URL"), api_version='v2')
        self.devMode = os.getenv("TRADING_DEV_MODE", 'False').lower() == "true"

        self._sortedFullStockCache = []
        self._stockIndexDataInterface = StockIndexDataInterface()


    """
    `getStockCache`: save list of StockData items, prices and symbols from index
    """
    def getStockCache(self: object) -> 'list[StockData]':
        if not self._sortedFullStockCache:
            indexSymbols = self._stockIndexDataInterface.getIndexSymbols(StockExchange.SP500)
            self._sortedFullStockCache = sorted(self.getStockDataList(indexSymbols), key=lambda x: x.price, reverse=True)
        return self._sortedFullStockCache


    """
    `buyStock`: buy `quantity` number of `stockSymbol`
    test: None
    """
    def buyStock(self, stockSymbol: str, quantity: int) -> None:
        self._submitOrder(stockSymbol, quantity, "buy")
    

    """
    `sellStock`: sell `quantity` number of `stockSymbol`
    test: None
    """
    def sellStock(self, stockSymbol: str, quantity: int) -> None:
        self._submitOrder(stockSymbol, quantity, "sell")


    """
    `getAvailableFunds`: returns the uninvested money associated with the account
    test: None
    """
    def getAvailableFunds(self) -> float:
        return float(self._getAlpacaAccount().cash)


    """
    `getPortfolioValue`: returns the current value of the open positions for the account
    test: None
    """
    def getPortfolioValue(self) -> float:
        return float(self._getAlpacaAccount().equity)


    """
    `getOpenPositions`: returns a dictionary of stock symbols mapped to quantities representing
    test: None
                        the open positions held on the account
    """
    def getOpenPositions(self: object) -> 'dict[str, int]':
        positions = self.api.list_positions()
        return { position.symbol: int(position.qty) for position in positions }


    """
    `getStockDataList`: returns a list of 'StockData` objects with prices based on the provided
    test: None
                        list of stock symbols
    """
    def getStockDataList(self: object, stockSymbols: 'list[str]') -> 'list[StockData]':
        stockSnapShots: dict = self.api.get_snapshots(stockSymbols)
        return [ StockData(symbol, snapshot.latest_trade.p) for symbol, snapshot in stockSnapShots.items() ]


    def openOrdersExist(self):
        return len(list(self.api.list_orders(status="open", limit=500)))


    def getLastYearPortfolioPerformance(self):
        outputDict = {}
        try:
            data: PortfolioHistory = self.api.get_portfolio_history(period="1A", timeframe="1D")

            for index, record in enumerate(data.equity):
                outputDict[data.timestamp[index]] = record
            f = open("dump.txt", "a")
            f.write(json.dumps(outputDict))
            f.close()
        except Exception as e:
            logging.error("EXCEPTION EXCEPTION")
            logging.error(e)
        return outputDict


    """
    `_submitOrder`: submits an order to the alpaca api to buy/sell 
    test: None
    """
    def _submitOrder(self, stockSymbol, quantity, order) -> None:
        if self.devMode: return
        self.api.submit_order(
            symbol=stockSymbol, 
            qty=quantity, 
            side=order
        )


    """
    `_getAlpacaAccount`: returns information about the alpaca account associated with the details above
    test: None
    """
    def _getAlpacaAccount(self) -> Account:
        return self.api.get_account()
