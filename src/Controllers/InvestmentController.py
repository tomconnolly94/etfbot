#!/usr/bin/python

# external dependencies
import logging

# internal dependencies
from src.Controllers.DataController import DataController
from src.Controllers.StockChoiceController import StockChoiceController
from src.Interfaces.AlpacaInterface import AlpacaInterface
from src.Types.StockData import StockData

"""
InvestmentController

This is a class to control investment decisions

"""
class InvestmentController():

    """
    `__init__`: intialise object fields
    """
    def __init__(self: object):
        # class fields
        self._idealStockRangeIndexStart = 300
        self._idealStockRangeIndexEnd = 400
        self._sortedFullStockCache = []
        self._stockChoiceController = StockChoiceController()
        self._alpacaInterface = AlpacaInterface()
        self._dataController = DataController()


    """
    `rebalanceInvestments`: analyse open positions to look for positions to close, and 
                            replace any closed positions with new openings
    """
    def rebalanceInvestments(self):

        # get current positions
        currentPositions = self._alpacaInterface.getOpenPositions()

        logging.info(f"Number of current positions held: {len(currentPositions)}")
        logging.info(f"Current positions - (symbol: index position) {', '.join(f'{stockSymbol}: {self._getPositionInIndex(stockSymbol)}' for stockSymbol in currentPositions.keys())}")

        # calculate trades that should be made to turn current position into ideal position
        positionsToSell = self._getPositionsToSell(currentPositions)
        logging.info(f"Number of positions that should be closed: {len(positionsToSell)}")
        
        valueOfPositionsToSell: float = self._getValueOfStockList(positionsToSell)
        availableFunds = self._alpacaInterface.getAvailableFunds()
        totalBuyingPower = valueOfPositionsToSell + availableFunds
        positionsToBuy = {}

        if totalBuyingPower > 0:
            positionsToBuy = self._getPositionsToBuy(currentPositions, totalBuyingPower)
            logging.info(f"Number of positions that should be opened: {len(positionsToBuy)}")

        # make trades
        for positionKey, positionQuantity in positionsToSell.items():
            self._alpacaInterface.sellStock(positionKey, positionQuantity)
            logging.info(f"Sold {positionQuantity} share{'s' if positionQuantity > 1 else ''} of {positionKey} at {self._getValueOfStock(positionKey)}")

        for positionKey, positionQuantity in positionsToBuy.items():
            self._alpacaInterface.buyStock(positionKey, positionQuantity)
            logging.info(f"Bought {positionQuantity} share{'s' if positionQuantity > 1 else ''} of {positionKey} at {self._getValueOfStock(positionKey)}")



    def getExchanges(self):

        available_stocks = self._alpacaInterface.showAllAvailableStocks()
        exchanges = []

        for stock in available_stocks:
            if stock.exchange not in exchanges:
                exchanges.append(stock.exchange)
                if stock.symbol[-1] == "L":
                    print(stock)

        print(exchanges)

        return


    """
    `_getIdealPositions`:   returns a list (symbols and quantities) of the ideal stocks 
                            to invest in based on the portfolio value
    """
    def _getIdealPositions(self: object) -> 'dict[str, int]':
        idealStockRange = self._getStockRangeIdeal()
        portfolioValue = self._alpacaInterface.getPortfolioValue()
        allStockOrders = self._stockChoiceController.getStockOrderNumbers(idealStockRange, portfolioValue)
        idealPositions = dict(filter(lambda entry: entry[1] > 0, allStockOrders.items()))
        return idealPositions


    """
    `_getStockRangeIdeal`:  returns a limited list (StockData) of the ideal stocks to 
                            invest in
    """
    def _getStockRangeIdeal(self: object) -> 'list[StockData]':
        return self._getStockCache()[self._idealStockRangeIndexStart:self._idealStockRangeIndexEnd]


    """
    `_getStockCache`: save list of StockData items, prices and symbols from index
    """
    def _getStockCache(self: object) -> None:
        if not self._sortedFullStockCache:
            stockDataList = self._dataController.getOrderedStockData()
            self._sortedFullStockCache = sorted(stockDataList, key=lambda x: x.price, reverse=True)
        return self._sortedFullStockCache


    """
    `_getStockRangeDontSell`:   returns a list of StockData items that fall in or above 
                                the "ideal" stock range
    """
    def _getStockRangeDontSell(self: object) -> 'list[StockData]':
        return self._getStockCache()[:self._idealStockRangeIndexEnd]


    ########## debug funcs ##########

    """
    `_getPositionInIndex`: returns the position of a stock in the index by symbol
    """
    def _getPositionInIndex(self: object, stockDataSymbol: str):
        for index, cachedStock in enumerate(self._getStockCache()):
            if cachedStock.symbol == stockDataSymbol:
                return index
        return None


    ########## debug funcs ##########


    """
    `_getPositionsToSell`:  returns a dict of symbols and quantities of open positions 
                            that should be closed
    """
    def _getPositionsToSell(self: object, currentPositions: 'dict[str, int]') -> 'dict[str, int]':
        dontSellStockRange = [ stockData.symbol for stockData in self._getStockRangeDontSell() ]
        positions = dict(filter(lambda entry: entry[0] not in dontSellStockRange, currentPositions.items()))
        return positions


    """
    `_getPositionsToBuy`:   returns a dict of symbols and quantities of open positions 
                            that should be opened with the available funds
    """
    def _getPositionsToBuy(self: object, currentPositions: 'dict[str, int]', availableFunds: float) -> 'dict[str, int]':
        idealPositionsToBuy = list(filter(lambda entry: entry.symbol not in currentPositions, self._getStockRangeIdeal()))
        runningPositionsTotalValue = 0
        actualPositionsToBuy = {}

        for stockData in idealPositionsToBuy:
            runningPositionsTotalValue += stockData.price
            if runningPositionsTotalValue <= availableFunds:
                actualPositionsToBuy[stockData.symbol] = 1

        return actualPositionsToBuy


    """
    `_getValueOfStockList`: take a list of positions, find their value and returns the sum
    """
    def _getValueOfStockList(self: object, stockSymbolList: 'dict[str, int]') -> float:
        relevantStockDataList: 'list[StockData]' = [ stockData for stockData in self._getStockCache() if stockData.symbol in stockSymbolList.keys() ]
        return sum(stockData.price for stockData in relevantStockDataList)


    """
    `_getValueOfStock`: returns the price of a stock from the `StockData` cache
    """
    def _getValueOfStock(self: object, stockSymbol: str) -> float:
        for stock in self._getStockCache():
            if stock.symbol == stockSymbol:
                return stock.price
            else:
                return None

