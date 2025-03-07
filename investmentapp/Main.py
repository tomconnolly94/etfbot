#!/usr/bin/python

# external dependencies
from dotenv import load_dotenv
import logging
import sys, os
import traceback

# internal dependencies
sys.path.append(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)  # make webapp and common sub projects accessible
from common import LoggingController
from investmentapp.src.Controllers.InvestmentController import (
    InvestmentController,
)
from investmentapp.src.Interfaces.MailInterface import MailInterface
from investmentapp.src.Interfaces.InternalPaperTradingInterface import InternalPaperTradingInterface
from investmentapp.src.Interfaces.AlpacaInterface import AlpacaInterface
from investmentapp.src.Strategies.StockChoiceStrategies.StockChoiceStrategyEnum import StockChoiceStrategyEnum


def main():

    # load environment
    load_dotenv()

    # intitialise logging module
    LoggingController.initLogging()

    logging.info(f"Program started.")

    errorString = ""

    strategyConfig = {
        # "Alpaca": { 
        #     "investingInterface": AlpacaInterface(), 
        #     "investingStrategy": StockChoiceStrategyEnum.LinearWeightingCheapFirst 
        # },
        "3": { 
            "investingInterface": InternalPaperTradingInterface("3"), 
            "investingStrategy": StockChoiceStrategyEnum.LinearWeightingCheapFirst 
        }
    }

    for strategyName, strategyDetail in strategyConfig.items():
        logging.info(f"Executing strategy={strategyName}")

        # run program with general error handling to prevent crashes
        try:
            InvestmentController(strategyName, strategyDetail["investingStrategy"], strategyDetail["investingInterface"]).rebalanceInvestments()
        except Exception as exception:
            errorString = (
                "Exception occured during program run ("
                "caught by generic exception handler):"
                f"\n{traceback.format_exc()}".rstrip()
            )
            logging.error(errorString)
        
        logging.info(f"Finished strategy={strategyName}")

    # send email notification with the log and any unhandled exceptions
    # MailInterface().sendInvestmentAppSummaryMail(
    #     success=False if errorString else True
    # )
    logging.info(f"Program ended.")


if __name__ == "__main__":
    main()
