#!/usr/bin/python

# external dependencies
import logging
import math
from src.Strategies.StockChoiceStrategies.StockChoiceStrategy import StockChoiceStrategy

# internal dependencies
from src.Controllers.StockChoiceController import StockChoiceController
from src.Interfaces.AlpacaInterface import AlpacaInterface

"""
InvestmentController

This is a class to control the retrieval and execution of stock trades

"""
class InvestmentController():

    """
    `__init__`: intialise object fields
    """
    def __init__(self: object):
        # class fields
        self._stockChoiceController = StockChoiceController()
        self._alpacaInterface = AlpacaInterface()


    """
    `rebalanceInvestments`: analyse open positions to look for positions to close, and 
                            replace any closed positions with new openings
    """
    def rebalanceInvestments(self):

        # get current positions
        currentPositions = self._alpacaInterface.getOpenPositions()

        logging.info(f"Number of current positions held: {len(currentPositions)}")
        logging.info(f"Current positions - (symbol: index position) {', '.join(f'{stockSymbol}: {self._getPositionInIndex(stockSymbol)}' for stockSymbol in currentPositions.keys())}")

        stockChoiceStrategy: StockChoiceStrategy = self._stockChoiceController.getStockChoiceStrategy()

        # calculate positions to dump
        positionsToSell: 'dict[str, int]' = stockChoiceStrategy.getSellOrders()
        valueOfPositionsToSell = sum(positionsToSell.values())
        logging.info(f"Number of positions that will be closed: {len(positionsToSell)}, total value: {valueOfPositionsToSell}")
        
        # make sales
        for positionKey, positionQuantity in positionsToSell.items():
            self._alpacaInterface.sellStock(positionKey, positionQuantity)
            logging.info(f"Sold {positionQuantity} share{'s' if positionQuantity > 1 else ''} of {positionKey} at {self._getValueOfStock(positionKey)}")

        # evaluate remaining funds
        liquidFunds = self._alpacaInterface.getAvailableFunds()
        positionsToBuy: 'dict[str, int]' = stockChoiceStrategy.getBuyOrders(liquidFunds)
        logging.info(f"Number of positions that will be opened: {len(positionsToBuy)}")
        moneySpent = 0

        # make buys
        for positionKey, positionQuantity in positionsToBuy.items():
            stockValue = self._getValueOfStock(positionKey)
            tradeValue = stockValue * positionQuantity

            logging.info(f"Attempting to buy {positionQuantity} share{'s' if positionQuantity > 1 else ''} of {positionKey} at {stockValue}.")
            self._alpacaInterface.buyStock(positionKey, positionQuantity)
            moneySpent += tradeValue
            logging.info(f"Buy successful, total money spent: {moneySpent}")


    """
    `_getIdealPositions`:   returns a list (symbols and quantities) of the ideal stocks 
                            to invest in based on the portfolio value
    """
    def _getIdealPositions(self: object) -> 'dict[str, int]':
        liquidFunds = self._alpacaInterface.getAvailableFunds()
        totalBuyingPower = self._alpacaInterface.getPortfolioValue() + liquidFunds
        
        logging.info(f"Total buying power: {totalBuyingPower}")
        logging.info(f"Total liquid funds: {liquidFunds}")
        allStockOrders = self._stockChoiceController.getStockOrderNumbers(totalBuyingPower)
        return allStockOrders


    """
    `_getPositionInIndex`: returns the position of a stock in the index by symbol
    """
    def _getPositionInIndex(self: object, stockDataSymbol: str):
        for index, cachedStock in enumerate(self._alpacaInterface.getStockCache()):
            if cachedStock.symbol == stockDataSymbol:
                return index
        return None


    # """
    # `_getValueOfStockList`: take a list of positions, find their value and returns the sum
    # """
    # def _getValueOfStockList(self: object, stockSymbolList: 'dict[str, int]') -> float:
    #     relevantStockDataList: 'list[StockData]' = [ stockData for stockData in self._getStockCache() if stockData.symbol in stockSymbolList.keys() ]
    #     return sum(stockData.price for stockData in relevantStockDataList)


    """
    `_getValueOfStock`: returns the price of a stock from the `StockData` cache
    """
    def _getValueOfStock(self: object, stockSymbol: str) -> float:
        for stock in self._alpacaInterface.getStockCache():
            if stock.symbol == stockSymbol:
                return stock.price
        return None

