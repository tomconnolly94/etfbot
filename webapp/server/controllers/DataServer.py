#!/venv/bin/python

# external dependencies
import datetime
import sys
sys.path.append("..") # makes AlpacaInterface accessible
sys.path.append("../investmentapp") # makes AlpacaInterface accessible
from threading import Thread
from enum import Enum
import os
from os.path import dirname
import subprocess
import glob
import logging

# internal dependencies
from server.interfaces.StockPriceHistoryInterface import getPricesForStockSymbols
from investmentapp.src.Interfaces.AlpacaInterface import AlpacaInterface
from investmentapp.src.Interfaces.DatabaseInterface import DatabaseInterface


class DataGrabbingSources(Enum):
    SPY500 = 1, 
    CurrentHoldings = 2,
    PortfolioPerformance = 3

class InvestmentData():
    
    def __init__(self, currentValue, oneMonthPrevValue, oneYearPrevValue, values):
        self.currentValue = currentValue
        self.oneMonthPrevValue = oneMonthPrevValue
        self.oneYearPrevValue = oneYearPrevValue
        self.values = values

    def toDict(self):
        return {
            "currentValue": self.currentValue,
            "oneMonthPrevValue": self.oneMonthPrevValue,
            "oneYearPrevValue": self.oneYearPrevValue,
            "values": self.values
        }

def _getLastYearDates():
    today = datetime.datetime.today()
    return [today - datetime.timedelta(days=x) for x in range(365)]


def _normaliseValues(data):
    maxValue = max([ value for value in data.values() if value ])
    normalisedDict = {}

    for key, value in data.items():
        normalisedDict[key] = value/maxValue if value else None
    return normalisedDict


def _getSPY500Data():
    prices = getPricesForStockSymbols(["SPY"])[0]

    sortedDates = sorted(prices.keys())
    endValue = prices[sortedDates[len(prices) - 1]]
    oneMonthPrevValue = prices[sortedDates[len(sortedDates) - 31]]
    oneYearPrevValue = prices[sortedDates[len(sortedDates) - 365]]
    
    return InvestmentData(endValue, oneMonthPrevValue, oneYearPrevValue, _normaliseValues(prices)).toDict()


def _getSPY500DataThreadWrapper(results, threadId):
    results[threadId] = _getSPY500Data()


def _getCurrentHoldingsPerformanceData():
    stockSymbolList = AlpacaInterface().getOpenPositions().keys()
    portfolioHistoryTotals = {}
    stockHistoryPrices = getPricesForStockSymbols(stockSymbolList)

    if not stockHistoryPrices:
        return {}

    # combine prices of all held stocks for each date 
    for index, stock in enumerate(stockHistoryPrices):
        for date, price in stock.items():

            if not price:
                logging.error(f"Problem: could not retrieve price data for a stock: maybe stock: {list(stockSymbolList)[index]}, index: {index}, date: {date}, price: {price}")
            
            if date in portfolioHistoryTotals and price:
                portfolioHistoryTotals[date] += price
                continue

            portfolioHistoryTotals[date] = price if price else 0 # initialise the dict on the first run

    sortedDates = sorted(portfolioHistoryTotals.keys())
    endValue = portfolioHistoryTotals[sortedDates[len(sortedDates) - 1]]
    oneMonthPrevValue = portfolioHistoryTotals[sortedDates[len(sortedDates) - 31]]
    oneYearPrevValue = portfolioHistoryTotals[sortedDates[len(sortedDates) - 365]]
    
    return InvestmentData(endValue, oneMonthPrevValue, oneYearPrevValue, _normaliseValues(portfolioHistoryTotals)).toDict()


def _getCurrentHoldingsPerformanceDataThreadWrapper(results, threadId):
    results[threadId] = _getCurrentHoldingsPerformanceData()


def _getPortfolioPerformanceData():
    rawPortfolioPerformanceData = DatabaseInterface().getPortfolioValueOverTime()

    # calculate date list
    dateList = _getLastYearDates()

    # create base data of null values
    portfolioPerformanceData = { date.strftime("%Y-%m-%d"): None for date in dateList }

    # overwrite null values with real data
    for rawData in rawPortfolioPerformanceData:
        portfolioPerformanceData[rawData["date"].split(" ")[0]] = float(rawData["value"])

    if not portfolioPerformanceData:
        return {}

    sortedDates = sorted(portfolioPerformanceData.keys())
    endValue = portfolioPerformanceData[sortedDates[len(sortedDates) - 1]]
    oneMonthPrevValue = portfolioPerformanceData[sortedDates[len(sortedDates) - 31]] if portfolioPerformanceData[sortedDates[len(sortedDates) - 31]] else 0
    oneYearPrevValue = portfolioPerformanceData[sortedDates[len(sortedDates) - 365]] if portfolioPerformanceData[sortedDates[len(sortedDates) - 365]] else 0

    return InvestmentData(endValue, oneMonthPrevValue, oneYearPrevValue, _normaliseValues(portfolioPerformanceData)).toDict()


def _getPortfolioPerformanceDataThreadWrapper(results, threadId):
    results[threadId] = _getPortfolioPerformanceData()


def getInvestmentData():

    threads = {}
    results = {
        DataGrabbingSources.SPY500: None,
        DataGrabbingSources.CurrentHoldings: None,
        DataGrabbingSources.PortfolioPerformance: None
    }
    dataGrabbingFunctions = {
        DataGrabbingSources.SPY500: _getSPY500DataThreadWrapper, 
        DataGrabbingSources.CurrentHoldings: _getCurrentHoldingsPerformanceDataThreadWrapper,
        DataGrabbingSources.PortfolioPerformance:  _getPortfolioPerformanceDataThreadWrapper
    }

    for key, wrapperFunction in dataGrabbingFunctions.items():
        threads[key] = Thread(target=wrapperFunction, args=(results, key))
        threads[key].start()

    for thread in threads.values():
        thread.join()

    returnableResults = {}

    for key, value in results.items():
        if value is None:
            logging.warn(f"Source: {key} was removed as it's result was calculated as: {value}")
            continue
        returnableResults[key.name] = value


    return returnableResults


def runInvestmentBalancer():
    projectRoot = dirname(dirname(dirname(os.path.abspath(__file__)))).replace('.', '')
    investmentappDir = os.path.join(projectRoot, os.getenv('INVESTMENTAPP_DIR'))
    pythonExecutable = os.path.join(os.getenv('PYTHON_DIR'), "python3")

    logging.info(f"Running {pythonExecutable} {investmentappDir}/Main.py")
    
    try:
        result = subprocess.run(f'{pythonExecutable} Main.py',
            check=True,
            capture_output=True,
            shell=True, 
            cwd=investmentappDir,
            text=True)
    except Exception as exception:
        logging.error(exception)
        return False
    
    programOutputLogs = []
    
    # collect all logs together
    if os.getenv("ENVIRONMENT") == "production":
        # collect most recent log file from /var/log/etfbot
        list_of_files = glob.glob(os.path.join(projectRoot, os.getenv("INVESTMENT_APP_LOGS_DIR")) + "/*") # * means all if need specific format then *.csv
        latest_file = max(list_of_files, key=os.path.getctime)
        with open(latest_file) as file:
            programOutputLogs = [line.rstrip() for line in file]
    else:
        programOutputLogs = (result.stderr + result.stdout).split("\n")

    return programOutputLogs


def getExcludeList():
    databaseInterface = DatabaseInterface()
    return databaseInterface.getExcludedStockSymbols()


if __name__ == "__main__":
    print(__file__)
    print(dirname(dirname(dirname(__file__))))
    print(dirname(dirname(dirname(__file__))).replace(".", ""))
