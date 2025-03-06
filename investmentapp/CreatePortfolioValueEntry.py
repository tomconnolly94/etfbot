#!/usr/bin/python

# external dependencies
from dotenv import load_dotenv
import logging
import sys, os


# internal dependencies
sys.path.append(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)  # make webapp and common sub projects accessible
from investmentapp.src.Interfaces.AlpacaInterface import AlpacaInterface
from investmentapp.src.Interfaces.DatabaseInterface import TIME_PERIOD, DatabaseInterface
from common import LoggingController



def getOwnedSymbolsAndQuantities(orders):

    symbolQuantityOwned = {}

    for order in orders:

        if order["symbol"] not in symbolQuantityOwned:
            symbolQuantityOwned[order["symbol"]] = 0

        if(order["buySell"] == "BUY"):
            symbolQuantityOwned[order["symbol"]] += order["orderQuantity"]

        if(order["buySell"] == "SELL"):
            symbolQuantityOwned[order["symbol"]] -= order["orderQuantity"]

    return symbolQuantityOwned



def addInternalPaperTradingDailyValues(databaseInterface: DatabaseInterface):

    strategyIds = databaseInterface.getInternalPaperTradingStrategyIds()
    for strategyId in strategyIds:
        # get list of symbols that are "owned", known because most recent order is a "BUY"
        ordersForStrategy = databaseInterface.getOrdersByStrategy(strategyId)
        logging.info(f"strategyId: {strategyId} - symbols: {ordersForStrategy}")
        ownedSymbolsAndQuantities = getOwnedSymbolsAndQuantities(ordersForStrategy)
        logging.info(f"ownedSymbolsAndQuantities: {ownedSymbolsAndQuantities}")

        # get value of quantity of symbol owned
        currentStockPrices = { stockData.symbol: stockData.price 
                     for stockData in 
                     AlpacaInterface().getStockDataList(ownedSymbolsAndQuantities.keys()) }
        logging.info(f"currentStockPrices: {currentStockPrices}")

        ownedSymbolsAndValues = {}
        for symbol, quantity in ownedSymbolsAndQuantities.items():
            ownedSymbolsAndValues[symbol] = currentStockPrices[symbol] * quantity

        logging.info(f"ownedSymbolsAndValues: {ownedSymbolsAndValues}")
        totalStrategyValue = sum(ownedSymbolsAndValues.values())

        logging.info(f"strategyId: {strategyId}, value: {totalStrategyValue}")
        databaseInterface.addTodaysInternalPortfolioValues(totalStrategyValue, strategyId)

        logging.info(f"databaseInterface.addTodaysExternalPortfolioValue finished.")


def main():

    load_dotenv()

    # intitialise logging module
    LoggingController.initLogging()

    logging.info(f"Program started.")

    # deal with external paper trading
    portfolioValue = AlpacaInterface().getPortfolioValue()
    logging.info(f"portfolioValue: {portfolioValue}")
    databaseInterface = DatabaseInterface()
    # databaseInterface.addTodaysExternalPortfolioValue(portfolioValue)

    # deal with internal paper trading strategies
    addInternalPaperTradingDailyValues(databaseInterface)


if __name__ == "__main__":
    main()
