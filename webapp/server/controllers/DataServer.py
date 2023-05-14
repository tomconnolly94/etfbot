#!/venv/bin/python

# external dependencies
import sys
import os
sys.path.append("..")
sys.path.append("../investmentapp")

# internal dependencies
from server.interfaces.StockPriceHistoryInterface import getPrices
from investmentapp.src.Interfaces.AlpacaInterface import AlpacaInterface


def _normaliseValues(data):
    maxValue = max(data.values())
    normalisedDict = {}

    for key, value in data.items():
        normalisedDict[key] = value/maxValue
    return normalisedDict


def getSPY500Data():
    return _normaliseValues(getPrices("SPY"))


def getCurrentHoldingsPerformanceData():
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


def getPortfolioPerformanceData():

    portfolioPerformanceData = AlpacaInterface().getLastYearPortfolioPerformance()
    print(portfolioPerformanceData)

    return _normaliseValues(portfolioPerformanceData)


def getInvestmentData():

    data = {
        "spy500Performance": getSPY500Data(),
        "currentHoldingsPerformance": getCurrentHoldingsPerformanceData(),
        "portfolioPerformance": getPortfolioPerformanceData()
    }
    return data
