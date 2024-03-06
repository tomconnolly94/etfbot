#!/venv/bin/python

# external dependencies
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


class DataGrabbingSources(Enum):
    SPY500 = 1, 
    CurrentHoldings = 2,
    PortfolioPerformance = 3


def _normaliseValues(data):
    maxValue = max([ value for value in data.values() if value ])
    normalisedDict = {}

    for key, value in data.items():
        normalisedDict[key] = value/maxValue if value else None
    return normalisedDict


def _getSPY500Data():
    prices = getPricesForStockSymbols(["SPY"])[0]

    sortedDates = sorted(prices.keys())
    startValue = prices[sortedDates[0]]
    endValue = prices[sortedDates[len(prices) - 1]]

    return {
        "startValue": startValue,
        "endValue": endValue,
        "values": _normaliseValues(prices)
    }


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
    startValue = portfolioHistoryTotals[sortedDates[0]]
    endValue = portfolioHistoryTotals[sortedDates[len(sortedDates) - 1]]
    
    return {
        "startValue": startValue,
        "endValue": endValue,
        "values": _normaliseValues(portfolioHistoryTotals)
    }

### wrapper functions to allow threading

def _getCurrentHoldingsPerformanceDataThreadWrapper(results, threadId):
    results[threadId] = _getCurrentHoldingsPerformanceData()

def _getPortfolioPerformanceData():
    portfolioPerformanceData = AlpacaInterface().getLastYearPortfolioPerformance()

    if not portfolioPerformanceData:
        return {}

    sortedDates = sorted(portfolioPerformanceData.keys())
    startValue = portfolioPerformanceData[sortedDates[0]]
    endValue = portfolioPerformanceData[sortedDates[len(portfolioPerformanceData) - 1]]

    return {
        "startValue": startValue,
        "endValue": endValue,
        "values": _normaliseValues(portfolioPerformanceData)
    }

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

    print(f"Running {pythonExecutable} {investmentappDir}/Main.py")
    
    try:
        result = subprocess.run(f'{pythonExecutable} Main.py',
            check=True,
            capture_output=True,
            shell=True, 
            cwd=investmentappDir,
            text=True)
    except Exception as exception:
        print(exception)
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


if __name__ == "__main__":
    print(__file__)
    print(dirname(dirname(dirname(__file__))))
    print(dirname(dirname(dirname(__file__))).replace(".", ""))
