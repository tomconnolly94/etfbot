#!/usr/bin/python

# external dependencies
import os
from trading_ig.rest import IGService

# internal dependencies
# from investmentapp.src.Interfaces.InvestingInterface import InvestingInterface


"""
IGInterface

This is a class to encapsulate all interactions between the software and the
gi.com API

"""
# class IGInterface(InvestingInterface):
class IGInterface():

    def __init__(self: object):
        # instantiate REST API
        #self.api = IGService(os.getenv("IG_TRADING_USERNAME"), os.getenv("IG_TRADING_PASSWORD"), os.getenv("IG_TRADING_API_KEY"))
        self.api = IGService("tconnolly94", "1j9W3niN3k6c7vDP9f2K", "73b400a08d46a714755198e65614887ef6b40270", "DEMO")
        self.api.create_session()
    

    """
    `_submitOrder`: submits an order to the alpaca api to buy/sell 
    """
    def _submitOrder(self, stockSymbol, quantity, order) -> None:
        self.api.submit_order(
            symbol=stockSymbol, 
            qty=quantity, 
            side=order
        )


    """
    `_getAlpacaAccount`: returns information about the alpaca account associated with the details above
    """
    # def _getAlpacaAccount(self) -> Account:
    #     return self.api.get_account()


    """
    `buyStock`: buy `quantity` number of `stockSymbol`
    """
    # def buyStock(self, stockSymbol: str, quantity: int) -> None:
    def buyStock(self) -> None:
        resp = self.api.create_open_position(
            currency_code='GBP',
            direction='BUY',
            epic='CS.D.USCGC.TODAY.IP',
            order_type='MARKET',
            expiry='DFB',
            force_open='false',
            guaranteed_stop='false',
            size=0.5, level=None,
            limit_distance=None,
            limit_level=None,
            quote_id=None,
            stop_level=None,
            stop_distance=None,
            trailing_stop=None,
            trailing_stop_increment=None)
    

    """
    `sellStock`: sell `quantity` number of `stockSymbol`
    """
    # def sellStock(self, stockSymbol: str, quantity: int) -> None:
    #     self._submitOrder(stockSymbol, quantity, "sell")


    # """
    # `getAvailableFunds`: returns the uninvested money associated with the account
    # """
    # def getAvailableFunds(self) -> float:
    #     return float(self._getAlpacaAccount().cash)


    # """
    # `getPortfolioValue`: returns the current value of the open positions for the account
    # """
    # def getPortfolioValue(self) -> float:
    #     return float(self._getAlpacaAccount().equity)


    # """
    # `getOpenPositions`: returns a dictionary of stock symbols mapped to quantities representing
    #                     the open positions held on the account
    # """
    # def getOpenPositions(self: object) -> 'dict[str, int]':
    #     positions = self.api.list_positions()
    #     return { position.symbol: int(position.qty) for position in positions }


    # """
    # `getStockDataList`: returns a list of 'StockData` objects with prices based on the provided 
    #                     list of stock symbols
    # """
    # def getStockDataList(self: object, stockSymbols: 'list[str]') -> 'list[StockData]':
    #     stockSnapShots: dict = self.api.get_snapshots(stockSymbols)
    #     return [ StockData(symbol, snapshot.latest_trade.p) for symbol, snapshot in stockSnapShots.items() ]




if __name__ == '__main__':
    igInterface = IGInterface()
    igInterface.buyStock()
