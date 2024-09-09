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
from investmentapp.src.Interfaces.DatabaseInterface import DatabaseInterface
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


if __name__ == "__main__":
    main()
