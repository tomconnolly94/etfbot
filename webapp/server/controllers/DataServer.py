#!/venv/bin/python

# external dependencies
import sys
import os
sys.path.append("..")
sys.path.append("../investmentapp")
print(sys.path)

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


def getPortfolioData():
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

    print(portfolioHistoryTotals)

    return _normaliseValues(portfolioHistoryTotals)


def getInvestmentData():

    data = {
        "spy500": getSPY500Data(),
        "portfolio": getPortfolioData()
    }
    return data
