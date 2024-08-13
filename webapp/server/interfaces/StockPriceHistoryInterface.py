#!/venv/bin/python

# external dependencies
import datetime
import aiohttp
import asyncio
import logging

# internal dependencies

def getTimestampNow():
    return (datetime.datetime.now() - datetime.timedelta(days=1)).strftime("%s")


def getPricesForStockSymbols(symbols):
    try:
        return asyncio.run(_getDataForUrlList(_buildGetPricesUrls(symbols), _parsePriceData))
    except Exception as exception:
        logging.error(exception)


def getCompanyNamesForStockSymbols(symbols):
    try:
        return asyncio.run(_getDataForUrlList(_buildGetCompanyNamesUrls(symbols), _parseCompanyNameData))
    except Exception as exception:
        logging.error(exception)


def validateSymbol(stockSymbol: str):
    companyNames = getCompanyNamesForStockSymbols([stockSymbol])
    logging.info(companyNames)
    if companyNames:
        return True
    return False

    
def _buildGetPricesUrls(symbols):
    timestampNow = getTimestampNow()
    timestampOneYearAgo = (datetime.datetime.now() - datetime.timedelta(weeks=52)).strftime("%s")
    return [ f"https://query2.finance.yahoo.com/v8/finance/chart/{symbol}?period1={timestampOneYearAgo}&period2={timestampNow}&interval=1d&events=history" 
            for symbol in symbols ]

    
def _buildGetCompanyNamesUrls(symbols):
    timestampNow = getTimestampNow() # specifiying two "now" timestamps reduce the size of the returned data
    return [ f"https://query2.finance.yahoo.com/v8/finance/chart/{symbol}?period1={timestampNow}&period2={timestampNow}" 
            for symbol in symbols ]


def _parsePriceData(priceData):

    try:
        baseObject = priceData["chart"]["result"][0]

        labels = baseObject["timestamp"]
        values = baseObject["indicators"]["quote"][0]["close"]
        dataDict = {}

        for index, label in enumerate(labels):
            dataDict[label] = values[index]
            if not values[index]:
                logging.error(f"Error found in _parsePriceData, symbol: {baseObject['meta']['symbol']}")
        return dataDict
    except KeyError as exception:
        symbol = baseObject["meta"]["symbol"]
        logging.error(f"Exception occured when parsing price data for {symbol}. Problematic key: {symbol} error: ", exception)
        return {}
    

def _parseCompanyNameData(priceData):

    try:
        return { 
            "symbol": priceData["chart"]["result"][0]["meta"]["symbol"],
            "companyName": priceData["chart"]["result"][0]["meta"]["longName"]
        }
    except KeyError as exception:
        symbol = priceData["chart"]["result"][0]["meta"]["symbol"]
        logging.error(f"Exception occured when parsing companyName data for {symbol}. Problematic key: {symbol} error: ", exception)
        return {}


async def _makeUrlRequest(session: aiohttp.ClientSession, url) -> dict:
    response = await session.request('GET', url=url)
    return await response.json()


async def _getDataForUrlList(urls, dataProcessingFunction):
    async with aiohttp.ClientSession() as session:
        tasks = []
        for url in urls:
            tasks.append(_makeUrlRequest(session=session, url=url))

        data = []
        for task in asyncio.as_completed(tasks, timeout=10):
            # await the url request, parse the response for price data and append it to `data`
            data.append(dataProcessingFunction(await task))

        return data
