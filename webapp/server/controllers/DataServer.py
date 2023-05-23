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

# internal dependencies
from server.interfaces.StockPriceHistoryInterface import getPricesForStockSymbols
from investmentapp.src.Interfaces.AlpacaInterface import AlpacaInterface


class DataGrabbingSources(Enum):
    SPY500 = 1, 
    CurrentHoldings = 2,
    PortfolioPerformance = 3


def _normaliseValues(data):
    maxValue = max(data.values())
    normalisedDict = {}

    for key, value in data.items():
        normalisedDict[key] = value/maxValue
    return normalisedDict


def _getSPY500Data():
    prices = getPricesForStockSymbols(["SPY"])
    return _normaliseValues(prices[0])


def _getSPY500DataThreadWrapper(results, threadId):
    results[threadId] = _getSPY500Data()


def _getCurrentHoldingsPerformanceData():
    stockSymbolList = AlpacaInterface().getOpenPositions().keys()
    portfolioHistoryTotals = {}
    
    stockHistoryPrices = getPricesForStockSymbols(stockSymbolList)

    if not stockHistoryPrices:
        return {}

    # combine prices of all held stocks for each date 
    for stock in stockHistoryPrices:
        for date, price in stock.items():
            if date in portfolioHistoryTotals:
                portfolioHistoryTotals[date] += price
                continue

            portfolioHistoryTotals[date] = price # initialise the dict on the first run

    return _normaliseValues(portfolioHistoryTotals)

### wrapper functions to allow threading

def _getCurrentHoldingsPerformanceDataThreadWrapper(results, threadId):
    results[threadId] = _getCurrentHoldingsPerformanceData()

def _getPortfolioPerformanceData():
    return _normaliseValues(AlpacaInterface().getLastYearPortfolioPerformance())

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

    return { key.name: value for key, value in results.items() }


def runInvestmentBalancer():
    investmentappDir = os.path.join(dirname(dirname(dirname(os.path.abspath(__file__)))).replace('.', ''), os.getenv('INVESTMENTAPP_DIR'))
    pythonExecutable = os.path.join(os.getenv('PYTHON_DIR') + "python3")

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
    
    # collect all logs together
    programOutputLogs = (result.stderr + result.stdout).split("\n")

    for log in programOutputLogs:
        print("investmentapp - ", log)

    return programOutputLogs


if __name__ == "__main__":
    print(__file__)
    print(dirname(dirname(dirname(__file__))))
    print(dirname(dirname(dirname(__file__))).replace(".", ""))
