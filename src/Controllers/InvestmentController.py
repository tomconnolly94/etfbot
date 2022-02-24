#!/usr/bin/python

# external dependencies

# internal dependencies
from src.Controllers.StockChoiceController import StockChoiceController
from src.Interfaces.AlpacaInterface import AlpacaInterface
from src.Interfaces.SP500IndexInterface import SP500IndexInterface
from src.Types.StockData import StockData

"""
InvestmentController

This is a class to control investment decisions

"""
class InvestmentController:

    """
    `__init__`: intialise object fields
    """
    def __init__(self: object):
        # class fields
        self.idealStockRangeIndexStart = 300
        self.idealStockRangeIndexEnd = 400
        self._sortedFullStockCache = []
        self.stockChoiceController = StockChoiceController()
        self.alpacaInterface = AlpacaInterface()
        self.sp500IndexInterface = SP500IndexInterface()


    """
    `_getIdealPositions`: get a list (symbols and quantities) of the ideal stocks to invest in based on the portfolio value
    """
    def _getIdealPositions(self: object) -> 'dict[str, int]':
        idealStockRange = self._getStockRangeIdeal()
        portfolioValue = self.alpacaInterface.getPortfolioValue()
        allStockOrders = self.stockChoiceController.getStockOrderNumbers(idealStockRange, portfolioValue)
        idealPositions = dict(filter(lambda entry: entry[1] > 0, allStockOrders.items()))
        return idealPositions


    """
    `_getStockRangeIdeal`: get a limited list (StockData) of the ideal stocks to invest in
    """
    def _getStockRangeIdeal(self: object) -> 'list[StockData]':
        if not self._sortedFullStockCache:
            self._refreshStockCache()
        return self._sortedFullStockCache[self.idealStockRangeIndexStart:self.idealStockRangeIndexEnd]


    """
    `_refreshStockCache`: save list of StockData items, prices and symbols from index
    """
    def _refreshStockCache(self: object) -> None:
        stockSymbols = self.sp500IndexInterface.getIndexSymbols()
        stockDataList = self.alpacaInterface.getStockDataList(stockSymbols)
        self._sortedFullStockCache = sorted(stockDataList, key=lambda x: x.price, reverse=True)


    """
    `_getStockRangeDontSell`: get a list of StockData items that fall in or above the "ideal" stock range
    """
    def _getStockRangeDontSell(self: object) -> 'list[StockData]':
        if not self._sortedFullStockCache:
            self._refreshStockCache()
        return self._sortedFullStockCache[:self.idealStockRangeIndexEnd]


    ########## debug funcs ##########

    """
    `_getPositionInIndex`: get position of a stock in the index by symbol
    """
    def _getPositionInIndex(self: object, stockDataSymbol: str):
        for index, cachedStock in enumerate(self._sortedFullStockCache):
            if cachedStock.symbol == stockDataSymbol:
                return index
        return None


    """
    `_printPositions`: pretty print symbols and index positions
    """
    def _printPositions(self: object, positions: 'dict[str, int]'):
        for positionSymbol in positions.keys():
            print(f"{positionSymbol}: {self._getPositionInIndex(positionSymbol)}")

    ########## debug funcs ##########


    """
    `_getPositionsToSell`: get dict of symbols and quantities of open positions that should be closed
    """
    def _getPositionsToSell(self: object, currentPositions: 'dict[str, int]') -> 'dict[str, int]':
        dontSellStockRange = [ stockData.symbol for stockData in self._getStockRangeDontSell() ]
        positions = dict(filter(lambda entry: entry[0] not in dontSellStockRange, currentPositions.items()))

        self._printPositions(currentPositions)
        self._printPositions(positions)

        return positions


    """
    `_getPositionsToBuy`: get dict of symbols and quantities of open positions that should be opened with the available funds
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
    `_getValueOfStockList`: take a list of positions, find their value and return the sum
    """
    def _getValueOfStockList(self: object, stockSymbolList: 'dict[str, int]') -> float:
        relevantStockDataList: 'list[StockData]' = [ stockData for stockData in self._sortedFullStockCache if stockData.symbol in stockSymbolList.keys() ]
        return sum(stockData.price for stockData in relevantStockDataList)


    """
    `rebalanceInvestments`: analyse open positions to look for positions to close, and replace any closed positions with new openings
    """
    def rebalanceInvestments(self):

        # get current positions
        currentPositions = self.alpacaInterface.getOpenPositions()

        # calculate trades that should be made to turn current position into ideal position
        positionsToSell = self._getPositionsToSell(currentPositions)
        valueOfPositionsToSell: float = self._getValueOfStockList(positionsToSell)
        availableFunds = self.alpacaInterface.getAvailableFunds()
        totalBuyingPower = valueOfPositionsToSell + availableFunds
        positionsToBuy = {}

        if totalBuyingPower > 0:
            positionsToBuy = self._getPositionsToBuy(currentPositions, totalBuyingPower)

        # make trades
        for positionKey, positionQuantity in positionsToSell.items():
            self.alpacaInterface.sellStock(positionKey, positionQuantity)

        for positionKey, positionQuantity in positionsToBuy.items():
            self.alpacaInterface.buyStock(positionKey, positionQuantity)
