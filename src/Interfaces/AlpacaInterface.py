#!/usr/bin/python

# external dependencies
import alpaca_trade_api
from alpaca_trade_api.entity import Account
import os

# internal dependencies
from src.Interfaces.InvestingInterface import InvestingInterface
from src.Types.StockData import StockData


class AlpacaInterface(InvestingInterface):

    def __init__(self: object):
        # instantiate REST API
        self.api = alpaca_trade_api.REST(os.getenv("ALPACA_TRADING_KEY_ID"), os.getenv("ALPACA_TRADING_SECRET_KEY"), os.getenv("ALPACA_TRADING_URL"), api_version='v2')
    

    def _submitOrder(self, stockSymbol, quantity, order) -> None:
        self.api.submit_order(
            symbol=stockSymbol, 
            qty=quantity, 
            side=order
        )


    def _getAlpacaAccount(self) -> Account:
        return self.api.get_account()


    def getAvailableFunds(self) -> float:
        return float(self._getAlpacaAccount().cash)


    def getPortfolioValue(self) -> float:
        return float(self._getAlpacaAccount().equity)


    def getStockDataList(self: object, stockSymbols: 'list[str]') -> 'list[StockData]':
        stockSnapShots: dict = self.api.get_snapshots(stockSymbols)
        return [ StockData(symbol, snapshot.latest_trade.p) for symbol, snapshot in stockSnapShots.items() ]


    def buyStock(self, stockSymbol: str, quantity: int) -> None:
        self._submitOrder(stockSymbol, quantity, "buy")
    

    def sellStock(self, stockSymbol: str, quantity: int) -> None:
        self._submitOrder(stockSymbol, quantity, "sell")


    def getOpenPositions(self: object) -> 'dict[str, int]':
        positions = self.api.list_positions()
        return { position.symbol: int(position.qty) for position in positions }