#!/usr/bin/python

# external dependencies
from alpaca.data.historical.stock import StockHistoricalDataClient
from alpaca.data.requests import StockBarsRequest, StockLatestQuoteRequest
from alpaca.data.timeframe import TimeFrame
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest, GetOrdersRequest, GetPortfolioHistoryRequest
from alpaca.trading.enums import OrderSide, TimeInForce, QueryOrderStatus
from alpaca.trading.models import TradeAccount, Position
from alpaca.broker.client import BrokerClient
from datetime import datetime
import os
import logging

# internal dependencies
from investmentapp.src.Types.StockExchange import StockExchange
from investmentapp.src.Interfaces.InvestingInterface import InvestingInterface
from investmentapp.src.Types.StockData import StockData
from investmentapp.src.Interfaces.StockIndexDataInterface import StockIndexDataInterface
from dateutil.relativedelta import relativedelta


"""
AlpacaInterface v2

This is a class to encapsulate all interactions between the software and the
Alpaca API

Github: https://github.com/alpacahq/alpaca-py
API reference: https://alpaca.markets/docs/api-references/trading-api/
Python sdk docs: https://alpaca.markets/docs/python-sdk/trading.html#trading
"""
class AlpacaInterface(InvestingInterface):

    def __init__(self: object):

        # no keys required for crypto data
        self.historicalDataAPI = StockHistoricalDataClient(os.getenv("ALPACA_TRADING_KEY_ID"), 
                                                            os.getenv("ALPACA_TRADING_SECRET_KEY"))
        self.tradingAPI = TradingClient(os.getenv("ALPACA_TRADING_KEY_ID"), 
                                        os.getenv("ALPACA_TRADING_SECRET_KEY"), 
                                        paper=True)
        self.brokerAPI = BrokerClient(api_key=os.getenv("ALPACA_TRADING_KEY_ID"),
                                      secret_key=os.getenv("ALPACA_TRADING_SECRET_KEY"), 
                                      api_version="v2",
                                      url_override=os.getenv("ALPACA_TRADING_URL"))
      
        self.devMode = os.getenv("TRADING_DEV_MODE", 'False').lower() == "true"

        self._sortedFullStockCache = []
        self._stockIndexDataInterface = StockIndexDataInterface()
        logging.info(f"AlpacaInterface initialised. devMode={self.devMode} env={os.getenv('TRADING_DEV_MODE', 'False')}")


    """
    `getStockCache`: save list of StockData items, prices and symbols from index
    """
    def getStockCache(self: object) -> 'list[StockData]':
        if not self._sortedFullStockCache:
            indexSymbols = self._stockIndexDataInterface.getIndexSymbols(StockExchange.SP500)
            self._sortedFullStockCache = sorted(self.getStockDataList(indexSymbols), key=lambda x: x.price, reverse=True)
            #logging.debug(f"self._sortedFullStockCache: {self._sortedFullStockCache}")
        return self._sortedFullStockCache


    """
    `buyStock`: buy `quantity` number of `stockSymbol`
    test: None
    """
    def buyStock(self, stockSymbol: str, quantity: int) -> None:
        if self.devMode:
            logging.info(f"buyStock called, devMode={self.devMode} so no order was submitted")
            return
        self._submitOrder(stockSymbol, quantity, OrderSide.BUY)


    """
    `sellStock`: execute sell trade of stock `stockSymbol` for `quantity` units
    """
    def sellStock(self, stockSymbol: str, quantity: int) -> None:
        if self.devMode:
            logging.info(f"sellStock called, devMode={self.devMode} so no order was submitted")
            return
        self._submitOrder(stockSymbol, quantity, OrderSide.SELL)


    """
    `getAvailableFunds`: return any uninvested funds 
    """
    def getAvailableFunds(self: object) -> float:
        return float(self._getAlpacaAccount().cash)


    """
    `getPortfolioValue`: return the value of stocks + uninvested funds
    """
    def getPortfolioValue(self: object) -> float:
        return float(self._getAlpacaAccount().equity)


    """
    `getOpenPositions`: return all positions currently held 
    """
    def getOpenPositions(self: object) -> 'dict[str, int]':
        positions: "list[Position]" = self.tradingAPI.get_all_positions()
        return { position.symbol: int(position.qty) for position in positions }


    """
    `getStockDataList`: return stock data on each stockSymbol in `stockSymbols`
    """
    def getStockDataList(self: object, stockSymbols: 'list[str]') -> 'list[StockData]':
        request = StockLatestQuoteRequest(symbol_or_symbols=stockSymbols)
        stockDataList = self.historicalDataAPI.get_stock_latest_quote(request)
        logging.debug(f"len(stockDataList): {len(stockDataList)}")
        # for symbol, stockData in stockDataList.items():
        #     logging.debug(f"{symbol}: {stockData}")

        return [ StockData(symbol, stockData.bid_price) for symbol, stockData in stockDataList.items() ]



    def openOrdersExist(self):
        request_params = GetOrdersRequest(status=QueryOrderStatus.OPEN, limit=500)
        return len(list(self.tradingAPI.get_orders(filter=request_params)))


    def getLastYearPortfolioPerformance(self):
        outputDict = {}
        if True:
        #try:
            
            request_params = GetPortfolioHistoryRequest(
                period="1A",
                timeframe="1D",
                date_end=datetime.now() - relativedelta(days=3)
            )
            logging.info("getLastYearPortfolioPerformance start")
            
            account_id = self._getAlpacaAccount().id
            data = self.brokerAPI.get_portfolio_history_for_account(account_id=account_id, history_filter=request_params)

            logging.info("getLastYearPortfolioPerformance end")
            
            for index, record in enumerate(data.equity):
                outputDict[data.timestamp[index]] = record

        # except Exception as e:
        #     logging.error(e)
        return outputDict


    """
    `_submitOrder`: submits an order to the alpaca api to buy/sell 
    test: None
    """
    def _submitOrder(self, stockSymbol, quantity, order: OrderSide) -> None:
        # preparing order data
        market_order_data = MarketOrderRequest(
                            symbol=stockSymbol,
                            qty=quantity,
                            side=order,
                            time_in_force=TimeInForce.DAY
                        )

        # Market order
        self.tradingAPI.submit_order(order_data=market_order_data)


    """
    `_getAlpacaAccount`: returns information about the alpaca account associated with the details above
    test: None
    """
    def _getAlpacaAccount(self) -> TradeAccount:
        return self.tradingAPI.get_account()




if __name__ == "__main__":

    # no keys required for crypto data
    client = StockHistoricalDataClient("PKU60BA6H93KCR7YKEL1", "LIcD1MKc6B8XcsMBnKjhUEsUf6sme4XtCOvhIdCm")

    request_params = StockBarsRequest(
                        symbol_or_symbols=["SPY","AAPL"],
                        timeframe=TimeFrame.Day,
                        start=datetime(2022, 9, 1),
                        end=datetime(2022, 9, 3)
                 )

    bars = client.get_stock_bars(request_params)

    # access bars as list - important to note that you must access by symbol key
    # even for a single symbol request - models are agnostic to number of symbols
    trading_client = TradingClient("PKU60BA6H93KCR7YKEL1", "LIcD1MKc6B8XcsMBnKjhUEsUf6sme4XtCOvhIdCm")
    brokerClient = BrokerClient("PKU60BA6H93KCR7YKEL1", "LIcD1MKc6B8XcsMBnKjhUEsUf6sme4XtCOvhIdCm", api_version="v2")


    request_params = GetPortfolioHistoryRequest(
        period="1A",
        timeframe="1D"
    )
    
    data = brokerClient.get_portfolio_history_for_account(account_id="1a859566-ce53-4e12-8a5b-5691623b4c80", history_filter=request_params)
