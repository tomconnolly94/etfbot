#!/usr/bin/python

# external dependencies
import alpaca_trade_api
from alpaca_trade_api.entity import Account
import os

# internal dependencies
from src.Interfaces.InvestingInterface import InvestingInterface
from src.Types.StockData import StockData


"""
AlpacaInterface

This is a class to encapsulate all interactions between the software and the
Alpaca API
"""
class AlpacaInterface(InvestingInterface):

    def __init__(self: object):
        # instantiate REST API
        self.api = alpaca_trade_api.REST(os.getenv("ALPACA_TRADING_KEY_ID"), os.getenv("ALPACA_TRADING_SECRET_KEY"), os.getenv("ALPACA_TRADING_URL"), api_version='v2')
        self.devMode = True

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


    def showAllAvailableStocks(self):
        active_assets = self.api.list_assets(status='active')
        return active_assets