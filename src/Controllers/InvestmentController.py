#!/usr/bin/python

# external dependencies
import logging

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

        # calculate ideal positions
        idealPositions: 'dict[str, int]' = self._getIdealPositions()

        # calculate positions to dump
        positionsToSell = { position[0]: position[1] for position in currentPositions.items() if position[0] not in idealPositions.keys() }
        valueOfPositionsToSell = sum(positionsToSell.values())

        positionsToBuy = { position[0]: position[1] for position in idealPositions.items() if position[0] not in currentPositions.keys() }

        logging.info(f"Number of positions that should be closed: {len(positionsToSell)}")
        logging.info(f"Number of positions that should be opened: {len(positionsToBuy)}")
        
        # make trades
        for positionKey, positionQuantity in positionsToSell.items():
            self._alpacaInterface.sellStock(positionKey, positionQuantity)
            logging.info(f"Sold {positionQuantity} share{'s' if positionQuantity > 1 else ''} of {positionKey} at {self._getValueOfStock(positionKey)}")

        moneySpent = 0
        moneyAvailable = valueOfPositionsToSell + self._alpacaInterface.getAvailableFunds()

        for positionKey, reccomendedPositionQuantity in positionsToBuy.items():
            stockValue = self._getValueOfStock(positionKey)

            # clamp the quantity to buy as much of the stock as possible up to the reccomended amount
            positionQuantity = max(0, min(moneyAvailable/stockValue, reccomendedPositionQuantity))
            tradeValue = stockValue * positionQuantity

            if tradeValue > moneyAvailable: # check if purchasing this stock would overspend funds
                break

            self._alpacaInterface.buyStock(positionKey, positionQuantity)
            moneyAvailable -= tradeValue
            moneySpent += tradeValue
            logging.info(f"Bought {positionQuantity} share{'s' if positionQuantity > 1 else ''} of {positionKey} at {stockValue}. Money spent: {moneySpent}")


    """
    `_getIdealPositions`:   returns a list (symbols and quantities) of the ideal stocks 
                            to invest in based on the portfolio value
    """
    def _getIdealPositions(self: object) -> 'dict[str, int]':
        totalBuyingPower = self._alpacaInterface.getPortfolioValue() + self._alpacaInterface.getAvailableFunds()
        
        logging.info(f"Total buying power: {totalBuyingPower}")
        allStockOrders = self._stockChoiceController.getStockOrderNumbers(totalBuyingPower)
        return allStockOrders


    """
    `_getPositionInIndex`: returns the position of a stock in the index by symbol
    """
    def _getPositionInIndex(self: object, stockDataSymbol: str):
        for index, cachedStock in enumerate(self._getStockCache()):
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

