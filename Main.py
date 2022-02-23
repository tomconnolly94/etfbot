#!/usr/bin/python

# external dependencies
from dotenv import load_dotenv

# internal dependencies
from src.Controllers.InvestmentController import InvestmentController

load_dotenv()

investmentController = InvestmentController()

investmentController.rebalanceInvestments()
