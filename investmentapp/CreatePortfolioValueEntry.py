#!/usr/bin/python

# external dependencies
from dotenv import load_dotenv
import logging


# internal dependencies
from src.Interfaces.AlpacaInterface import AlpacaInterface
from src.Interfaces.DatabaseInterface import DatabaseInterface
from common import LoggingController


def main():

    load_dotenv()

    # intitialise logging module
    LoggingController.initLogging()

    logging.info(f"Program started.")

    # create AlpacaInterface
    alpacaInterface = AlpacaInterface()
    portfolioValue = alpacaInterface.getPortfolioValue()
    logging.info(f"portfolioValue: {portfolioValue}")

    databaseInterface = DatabaseInterface()
    databaseInterface.addTodaysPortfolioValue(portfolioValue)


if __name__ == '__main__':
    main()