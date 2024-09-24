#!/usr/bin/python

# external dependencies
from dotenv import load_dotenv
import logging
import sys, os

# internal dependencies
sys.path.append(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)  # make webapp and common sub projects accessible
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
        logging.info(f"Program executed successfully.")
    except Exception as exception:
        logging.error(exception)
        errorString = exception
        logging.info(f"Program executed with errors.")

    # send email notification with the log and any unhandled exceptions
    MailInterface().sendInvestmentAppSummaryMail(success=False if errorString else True)
    logging.info(f"Program ended.")


if __name__ == "__main__":
    main()
