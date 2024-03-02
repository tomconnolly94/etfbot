#!/usr/bin/python

# external dependencies
from dotenv import load_dotenv
import logging

# internal dependencies
from src.Controllers import LoggingController
from src.Controllers.InvestmentController import InvestmentController


def main():

    # load environment
    load_dotenv()

    # intitialise logging module
    LoggingController.initLogging()

    logging.info(f"Program started.")

    # from src.Interfaces.AlpacaInterface import AlpacaInterface
    # from src.Types.StockData import StockData
    # alpacaInterface = AlpacaInterface()

    # stocklist: 'list[StockData]' = alpacaInterface.getStockCache()

    # index = 0
    # for stock in stocklist:
    #     logging.info(f"{index} symbol: {stock.symbol} at {stock.price}")
    #     index += 1
    # return

    # read program config
    

    # run program with general error handling to prevent crashes
    try:
        InvestmentController().rebalanceInvestments()
    except Exception as e:
        logging.error(e)

if __name__ == '__main__':
    main()