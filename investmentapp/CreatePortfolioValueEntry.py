#!/usr/bin/python

# external dependencies
from dotenv import load_dotenv
import logging
import sys, os


# internal dependencies
sys.path.append(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)  # make webapp and common sub projects accessible
from investmentapp.src.Interfaces.InternalPaperTradingClient import InternalPaperTradingClient
from investmentapp.src.Interfaces.AlpacaInterface import AlpacaInterface
from investmentapp.src.Interfaces.DatabaseInterface import DatabaseInterface
from common import LoggingController


def addInternalPaperTradingDailyValues(databaseInterface: DatabaseInterface):

    strategyIds = databaseInterface.getInternalPaperTradingStrategyIds()
    for strategyId in strategyIds:
        totalStrategyValue = InternalPaperTradingClient(databaseInterface, strategyId).getTotalStockValue()

        logging.info(f"strategyId: {strategyId}, value: {totalStrategyValue}")
        databaseInterface.addTodaysInternalPortfolioValues(totalStrategyValue, strategyId)

        logging.info(f"InternalPaperTrading strategy={strategyId} portfolioValue={totalStrategyValue}.")


def main():

    load_dotenv()

    # intitialise logging module
    LoggingController.initLogging()

    logging.info(f"Program started.")

    # deal with external paper trading
    portfolioValue = AlpacaInterface().getPortfolioValue()
    logging.info(f"Alpaca portfolioValue={portfolioValue}")
    databaseInterface = DatabaseInterface()
    databaseInterface.addTodaysExternalPortfolioValue(portfolioValue)

    # deal with internal paper trading strategies
    addInternalPaperTradingDailyValues(databaseInterface)


if __name__ == "__main__":
    main()
