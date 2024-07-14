#!/venv/bin/python

# external dependencies
import datetime
import aiohttp
import asyncio
import logging

# internal dependencies

    
def _buildGetPricesUrls(symbols):
    timestampNow = (datetime.datetime.now() - datetime.timedelta(days=1)).strftime("%s")
    timestampOneYearAgo = (datetime.datetime.now() - datetime.timedelta(weeks=52)).strftime("%s")
    return [ f"https://query2.finance.yahoo.com/v8/finance/chart/{symbol}?period1={timestampOneYearAgo}&period2={timestampNow}&interval=1d&events=history" 
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
        logging.error(f"Exception occured when parsing data for {symbol}. Problematic key: ", exception)
        return {}


async def _makeUrlRequest(session: aiohttp.ClientSession, url) -> dict:
    response = await session.request('GET', url=url)
    return await response.json()


async def _getPriceDataForUrlList(urls):
    async with aiohttp.ClientSession() as session:
        tasks = []
        for url in urls:
            tasks.append(_makeUrlRequest(session=session, url=url))

        data = []
        for task in asyncio.as_completed(tasks, timeout=10):
            # await the url request, parse the response for price data and append it to `data`
            data.append(_parsePriceData(await task))

        return data


def getPricesForStockSymbols(symbols):
    try:
        return asyncio.run(_getPriceDataForUrlList(_buildGetPricesUrls(symbols)))
    except Exception as exception:
        logging.error(exception)