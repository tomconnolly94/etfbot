#!/usr/bin/python

# external dependencies

# internal dependencies
from Controllers.StockChoiceController import StockChoiceController
from Interfaces.AlpacaInterface import AlpacaInterface
from Interfaces.SP500IndexInterface import SP500IndexInterface
from Types.StockData import StockData


class InvestmentController:

    def __init__(self: object):
        # class fields
        self.idealStockRangeIndexStart = 300
        self.idealStockRangeIndexEnd = 400
        self._sortedFullStockCache = []
        self.stockChoiceController = StockChoiceController()
        self.alpacaInterface = AlpacaInterface()
        self.sp500IndexInterface = SP500IndexInterface()


    def _getIdealPositions(self: object) -> 'dict[str, int]':
        idealStockRange = self._getStockRangeIdeal()
        portfolioValue = self.alpacaInterface.getPortfolioValue()
        allStockOrders = self.stockChoiceController.getStockOrderNumbers(idealStockRange, portfolioValue)
        idealPositions = dict(filter(lambda entry: entry[1] > 0, allStockOrders.items()))
        return idealPositions


    def _getStockRangeIdeal(self: object) -> 'list[StockData]':
        if not self._sortedFullStockCache:
            self._refreshStockCache()
        return self._sortedFullStockCache[self.idealStockRangeIndexStart:self.idealStockRangeIndexEnd]


    def _refreshStockCache(self: object) -> None:
        stockSymbols = self.sp500IndexInterface.getIndexSymbols()
        stockDataList = self.alpacaInterface.getStockDataList(stockSymbols)
        self._sortedFullStockCache = sorted(stockDataList, key=lambda x: x.price, reverse=True)


    def _getStockRangeDontSell(self: object) -> 'list[StockData]':
        if not self._sortedFullStockCache:
            self._refreshStockCache()
        return self._sortedFullStockCache[:self.idealStockRangeIndexEnd]


    # temp debug funcs
    def _getPositionInIndex(self: object, stockDataSymbol: str):
        for index, cachedStock in enumerate(self._sortedFullStockCache):
            if cachedStock.symbol == stockDataSymbol:
                return index
        return None


    def _printPositions(self: object, positions: 'dict[str, int]'):
        for positionSymbol in positions.keys():
            print(f"{positionSymbol}: {self._getPositionInIndex(positionSymbol)}")

    
    def _getPositionsToSell(self: object, currentPositions: 'dict[str, int]') -> 'dict[str, int]':
        dontSellStockRange = [ stockData.symbol for stockData in self._getStockRangeDontSell() ]
        positions = dict(filter(lambda entry: entry[0] not in dontSellStockRange, currentPositions.items()))

        self._printPositions(currentPositions)
        self._printPositions(positions)

        return positions


    def _getPositionsToBuy(self: object, currentPositions: 'dict[str, int]', valueOfPositionsToSell: float) -> 'dict[str, int]':
        idealPositionsToBuy = dict(filter(lambda entry: entry.symbol not in currentPositions, self._getStockRangeIdeal()))
        runningPositionsTotalValue = 0
        actualPositionsToBuy = {}

        for stockData in idealPositionsToBuy:
            runningPositionsTotalValue += stockData.price
            if runningPositionsTotalValue <= valueOfPositionsToSell:
                actualPositionsToBuy[stockData.symbol] = 1
            else:
                break

        return actualPositionsToBuy


    def _getValueOfStockList(self: object, stockSymbolList: 'dict[str, int]') -> float:
        relevantStockDataList: 'list[StockData]' = [ stockData for stockData in self._sortedFullStockCache if stockData.symbol in stockSymbolList.keys() ]
        return sum(stockData.price for stockData in relevantStockDataList)


    def rebalanceInvestments(self):

        # get current positions
        currentPositions = self.alpacaInterface.getOpenPositions()

        # calculate trades that should be made to turn current position into ideal position
        positionsToSell = self._getPositionsToSell(currentPositions)
        valueOfPositionsToSell: float = self._getValueOfStockList(positionsToSell)
        positionsToBuy = {}
        if valueOfPositionsToSell > 0:
            positionsToBuy = self._getPositionsToBuy(currentPositions, valueOfPositionsToSell)

        # make trades
        for positionKey, positionQuantity in positionsToSell.items():
            self.alpacaInterface.sellStock(positionKey, positionQuantity)

        for positionKey, positionQuantity in positionsToBuy.items():
            self.alpacaInterface.buyStock(positionKey, positionQuantity)
