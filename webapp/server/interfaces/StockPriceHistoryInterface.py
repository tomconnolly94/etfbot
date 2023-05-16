#!/venv/bin/python

# external dependencies
import datetime
import aiohttp
import asyncio

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
        return dataDict
    except KeyError as exception:
        symbol = baseObject["meta"]["symbol"]
        print(f"Exception occured when parsing data for {symbol}. Problematic key: ", exception)
        return {}
    

async def _getPriceDataForUrlListOld(urls):

    stockHistoryPrices = []
    
    async with aiohttp.ClientSession() as session:
        for url in urls:
            print(f"url req sent: {url}")
            async with session.get(url) as response:

                print(f"url response received: {url}")
                priceData = await response.json()
                parsedPriceData = _parsePriceData(priceData)
                stockHistoryPrices.append(parsedPriceData)
    return stockHistoryPrices


async def get(session: aiohttp.ClientSession, url) -> dict:
    response = await session.request('GET', url=url)
    priceData = await response.json()
    parsedPriceData = _parsePriceData(priceData)
    return parsedPriceData


async def _getPriceDataForUrlList(urls):
    async with aiohttp.ClientSession() as session:
        tasks = []
        for url in urls:
            tasks.append(get(session=session, url=url))

        data = []
        for task in asyncio.as_completed(tasks, timeout=10):
            # get the next result
            data.append(await task)
        
        #data = await asyncio.gather(*tasks, return_exceptions=True)
        return data


def getPricesForStockSymbols(symbols):
    try: 
        return asyncio.run(_getPriceDataForUrlList(_buildGetPricesUrls(symbols)))
    except Exception as exception:
        print(exception)