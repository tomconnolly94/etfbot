#!/usr/bin/python

# external dependencies
from dotenv import load_dotenv
import logging
import sys, os

# internal dependencies
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) # make webapp and common sub projects accessible
from common import LoggingController
from investmentapp.src.Controllers.InvestmentController import InvestmentController
from investmentapp.src.Interfaces.MailInterface import MailInterface

def main():

    # load environment
    load_dotenv()

    # intitialise logging module
    LoggingController.initLogging()

    logging.info(f"Program started.")

    errorString = ""

    # run program with general error handling to prevent crashes
    try:
        InvestmentController().rebalanceInvestments()
    except Exception as exception:
        logging.error(exception)
        errorString = exception

    # send email notification with the log and any unhandled exceptions
    MailInterface().sendInvestmentAppSummaryMail(success=False if errorString else True)

if __name__ == '__main__':
    main()