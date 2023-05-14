#!/venv/bin/python

# external dependencies
import sys
sys.path.append("..") # makes AlpacaInterface accessible
sys.path.append("../investmentapp") # makes AlpacaInterface accessible
from threading import Thread
from enum import Enum

# internal dependencies
from server.interfaces.StockPriceHistoryInterface import getPrices
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
    return _normaliseValues(getPrices("SPY"))


def _getSPY500DataThreadWrapper(results, threadId):
    results[threadId] = _getSPY500Data()


def _getCurrentHoldingsPerformanceData():
    stockSymbolList = AlpacaInterface().getOpenPositions().keys()
    portfolioHistoryTotals = {}

    for stockSymbol in stockSymbolList:
        stockPrices: 'dict[int, float]' = getPrices(stockSymbol)

        if not stockPrices:
            continue

        for date, price in stockPrices.items():
            if date in portfolioHistoryTotals:
                portfolioHistoryTotals[date] += price
                continue

            portfolioHistoryTotals[date] = price # initialise the dict on the first run

    return _normaliseValues(portfolioHistoryTotals)


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

    for key, value in dataGrabbingFunctions.items():
        threads[key] = Thread(target=value, args=(results, key))
        threads[key].start()

    for thread in threads.values():
        thread.join()

    return { key.name: value for key, value in results.items() }

