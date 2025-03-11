#!/usr/bin/python

# external dependencies
import logging

# internal dependencies
from investmentapp.src.Interfaces.InvestingInterface import InvestingInterface
from investmentapp.src.Strategies.StockChoiceStrategies.StockChoiceStrategy import (
    StockChoiceStrategy,
)
from investmentapp.src.Controllers.StockChoiceController import (
    StockChoiceController,
)
from investmentapp.src.Strategies.StockChoiceStrategies.StockChoiceStrategyEnum import (
    StockChoiceStrategyEnum,
)

"""
InvestmentController

This is a class to control the retrieval and execution of stock trades

"""


class InvestmentController:
    """
    `__init__`: intialise object fields
    """

    def __init__(self: object,
                 strategyName: str,
                 stockChoiceStrategy: StockChoiceStrategyEnum,
                 investingInterface: InvestingInterface):
        # class fields
        self._stockChoiceController: StockChoiceController = StockChoiceController(stockChoiceStrategy, investingInterface)
        self._investingInterface: InvestingInterface = investingInterface
        self._strategyName: str = strategyName

    """
    `rebalanceInvestments`: analyse open positions to look for positions to close, and 
                            replace any closed positions with new openings
    """

    def rebalanceInvestments(self):

        # get current positions
        currentPositions: "dict[str, int]" = (
            self._investingInterface.getOpenPositions()
        )

        logging.info(
            f"Number of current positions held: {len(currentPositions)}"
        )
        logging.info(
            f"Current positions - (symbol: index position) {', '.join(f'{stockSymbol}: {self._getPositionInIndex(stockSymbol)}' for stockSymbol in currentPositions.keys())}"
        )

        if self._investingInterface.openOrdersExist():
            logging.info(
                f"Open orders exist, no new trading will occur until these orders have been filled."
            )
            return

        stockChoiceStrategy: StockChoiceStrategy = (
            self._stockChoiceController.getStockChoiceStrategy()
        )

        # calculate positions to dump
        stockSymbolsToSell: "list[str]" = stockChoiceStrategy.getSellOrders()
        stockSymbolsToSellOriginalLength = len(stockSymbolsToSell)

        stockSymbolsToSell = stockSymbolsToSell[:10]
        logging.info(
            f"Number of positions that can be sold {stockSymbolsToSellOriginalLength}"
        )
        logging.info(
            f"Number of positions that will be closed: {len(stockSymbolsToSell)}"
        )

        # make sales
        for stockSymbol in stockSymbolsToSell:
            positionQuantity = currentPositions[stockSymbol]
            self._investingInterface.sellStock(
                stockSymbol, currentPositions[stockSymbol]
            )
            del currentPositions[stockSymbol]
            logging.info(
                f"Sold {positionQuantity} share{'s' if positionQuantity > 1 else ''} of {stockSymbol} at {self._getValueOfStock(stockSymbol)}"
            )

        # evaluate remaining funds
        liquidFunds = self._investingInterface.getAvailableFunds()
        positionsToBuy: "dict[str, int]" = stockChoiceStrategy.getBuyOrders(
            liquidFunds, currentPositions
        )

        logging.info(f"Available funds for new investments: {liquidFunds}")
        logging.info(
            f"Number of positions that will be opened: {len(positionsToBuy)}"
        )
        moneySpent = 0

        # make buys
        for positionKey, positionQuantity in positionsToBuy.items():
            stockValue = self._getValueOfStock(positionKey)
            tradeValue = stockValue * positionQuantity

            logging.info(
                f"Attempting to buy {positionQuantity} share{'s' if positionQuantity > 1 else ''} of {positionKey} at {stockValue}."
            )
            self._investingInterface.buyStock(positionKey, positionQuantity)
            moneySpent += tradeValue
            logging.info(f"Buy successful, total money spent: {moneySpent}")

    """
    `_getPositionInIndex`: returns the position of a stock in the index by symbol
    """

    def _getPositionInIndex(self: object, stockDataSymbol: str):
        for index, cachedStock in enumerate(
            self._investingInterface.getStockCache()
        ):
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
        for stock in self._investingInterface.getStockCache():
            if stock.symbol == stockSymbol:
                return stock.price
        return None
