#!/usr/bin/python

# external dependencies
from dotenv import load_dotenv
import logging

# internal dependencies
from src.Controllers import LoggingController
from src.Controllers.InvestmentController import InvestmentController

load_dotenv()

#intitialise logging module
LoggingController.initLogging()


logging.info(f"Program started.")

# run program
InvestmentController().rebalanceInvestments()
