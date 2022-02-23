#!/usr/bin/python

# external dependencies

# internal dependencies
from Controllers.StockChoiceController import StockChoiceController
from Interfaces.AlpacaInterface import AlpacaInterface
from Interfaces.SP500IndexInterface import SP500IndexInterface
from Types.StockData import StockData


class InvestmentController:

    def __init__(self: object):
        self.stockChoiceController = StockChoiceController()
        self.alpacaInterface = AlpacaInterface()
        self.sp500IndexInterface = SP500IndexInterface()


    def _getIdealPositions(self: object) -> 'dict[str, int]':
        stockSymbols = self.sp500IndexInterface.getIndexSymbols()
        stockDataList = self.alpacaInterface.getStockDataList(stockSymbols)
        top100Stocks = sorted(stockDataList, key=lambda x: x.price, reverse=True)[300:400]
        portfolioValue = self.alpacaInterface.getPortfolioValue()
        allStockOrders = self.stockChoiceController.getStockOrderNumbers(top100Stocks, portfolioValue)
        idealPositions = dict(filter(lambda entry: entry[1] > 0, allStockOrders.items()))
        return idealPositions

    
    def _getPositionsToSell(self: object, currentPositions: 'dict[str, int]', idealPositions: 'dict[str, int]') -> 'dict[str, int]':
        return dict(filter(lambda entry: entry[0] not in idealPositions, currentPositions.items()))


    def _getPositionsToBuy(self: object, currentPositions: 'dict[str, int]', idealPositions: 'dict[str, int]') -> 'dict[str, int]':
        return dict(filter(lambda entry: entry[0] not in currentPositions, idealPositions.items()))


    def rebalanceInvestments(self):

        # get current positions
        currentPositions = self.alpacaInterface.getOpenPositions()

        # get ideal positions
        idealPositions: 'dict[str, int]' = self._getIdealPositions()

        # calculate trades that should be made to turn current position into ideal position
        positionsToSell = self._getPositionsToSell(currentPositions, idealPositions)
        positionsToBuy = self._getPositionsToBuy(currentPositions, idealPositions)

        # make trades
        for positionKey, positionQuantity in positionsToSell.items():
            self.alpacaInterface.sellStock(positionKey, positionQuantity)

        for positionKey, positionQuantity in positionsToBuy.items():
            self.alpacaInterface.buyStock(positionKey, positionQuantity)





    # def spendFunds(self):
    #     stockSymbols = self.sp500IndexInterface.getIndexSymbols()
    #     stockDataList = self.alpacaInterface.getStockDataList(stockSymbols)
    #     top100Stocks = sorted(stockDataList, key=lambda x: x.price, reverse=True)[300:400]
    #     availableFunds = float(self.alpacaInterface.getAvailableFunds())
    #     stockBuyingQuantities: 'dict[str, int]' = self.stockChoiceController.getStockOrderNumbers(top100Stocks, availableFunds)

    #     for symbol, quantity in stockBuyingQuantities.items():
    #         if quantity > 0:
    #             self.alpacaInterface.buyStock(symbol, quantity)
