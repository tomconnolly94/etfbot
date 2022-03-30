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

    # read program config
    

    # run program
    InvestmentController().rebalanceInvestments()

main()