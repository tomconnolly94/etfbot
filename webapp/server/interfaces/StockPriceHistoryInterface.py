#!/venv/bin/python

# external dependencies
import datetime
from dateutil import tz
import aiohttp
import asyncio
import logging
import re

# internal dependencies


def getTimestampForStartOfToday():
    now = datetime.datetime.now()
    return datetime.datetime(now.year, now.month, now.day, tzinfo=tz.tzutc()).strftime(
        "%s"
    )


def getTimestampForStartOfYesterday():
    yday = datetime.datetime.now() - datetime.timedelta(days=1)
    return datetime.datetime(
        yday.year, yday.month, yday.day, tzinfo=tz.tzutc()
    ).strftime("%s")


def getPricesForStockSymbols(symbols):
    logging.info("Running StockPriceHistoryInterface/py::getPricesForStockSymbols")
    try:
        data = asyncio.run(
            _getDataForUrlList(_buildGetPricesUrls(symbols), _parsePriceData)
        )
        return data
    except Exception as exception:
        logging.error(exception)
        return {}


def getCompanyNamesForStockSymbols(symbols):
    logging.info("Running StockPriceHistoryInterface/py::getCompanyNamesForStockSymbols")
    try:
        return asyncio.run(
            _getDataForUrlList(
                _buildGetCompanyNamesUrls(symbols), _parseCompanyNameData
            )
        )
    except Exception as exception:
        logging.exception(exception)


def getStockExchangesForStockSymbol(stockSymbol: str):
    logging.info("Running StockPriceHistoryInterface/py::getStockExchangesForStockSymbol")
    try:
        stockExchangeData = asyncio.run(
            _getDataForUrlList(
                _buildGetCompanyNamesUrls([stockSymbol]), _parseStockExchangeData
            )
        )
        if not stockExchangeData[0] or "stockExchange" not in stockExchangeData[0]:
            return False

        return stockExchangeData[0]["stockExchange"]
    except Exception as exception:
        logging.error(exception)


def _buildGetPricesUrls(symbols):
    timestampStartOfToday = getTimestampForStartOfToday()
    timestampOneYearAgo = (
        datetime.datetime.now() - datetime.timedelta(days=365)
    ).strftime("%s")
    logging.info(
        f"stock price query =https://query2.finance.yahoo.com/v8/finance/chart/<symbol>?period1={timestampOneYearAgo}&period2={timestampStartOfToday}&interval=1d&events=history"
    )
    return [
        f"https://query2.finance.yahoo.com/v8/finance/chart/{symbol}?period1={timestampOneYearAgo}&period2={timestampStartOfToday}&interval=1d&events=history"
        for symbol in symbols
    ]


def _buildGetCompanyNamesUrls(symbols):
    timestampStartOfToday = (
        getTimestampForStartOfYesterday()
    )  # specifiying two "now" timestamps reduce the size of the returned data
    return [
        f"https://query2.finance.yahoo.com/v8/finance/chart/{symbol}?period1={timestampStartOfToday}&period2={timestampStartOfToday}"
        for symbol in symbols
    ]


def _parsePriceData(urlAndPriceData):

    url = urlAndPriceData[0]
    priceData = urlAndPriceData[1]

    try:
        baseObject = priceData["chart"]["result"][0]

        labels = baseObject["timestamp"]
        values = baseObject["indicators"]["quote"][0]["close"]
        dataDict = {}

        for index, label in enumerate(labels):
            dataDict[label] = values[index]
            if not values[index]:
                logging.error(
                    f"Error found in _parsePriceData, symbol={baseObject['meta']['symbol']} "
                    f"index={index} lenValues={len(values)} values={values}"
                )
        return dataDict
    except KeyError as exception:
        try:
            symbol = baseObject["meta"]["symbol"]
            logging.error(
                f"Exception occured when parsing price data for {symbol}. error: ",
                exception,
            )
        except TypeError as exception:
            logging.error(
                f"Exception occured when parsing price data={priceData}. error: ",
                exception,
            )
        
        return {}


def _parseCompanyNameData(urlAndPriceData):

    url = urlAndPriceData[0]
    priceData = urlAndPriceData[1]

    try:
        return {
            "symbol": priceData["chart"]["result"][0]["meta"]["symbol"],
            "companyName": priceData["chart"]["result"][0]["meta"]["longName"],
        }
    except (KeyError, TypeError) as exception:
        logging.error(
            f"Exception occured when parsing companyName data in _parseCompanyNameData. error: ")

        stockSymbolRegexPattern = "https:\/\/query2\.finance\.yahoo\.com\/v8\/finance\/chart\/(\w+)?" # dependent on yahoo
        stockSymbol = re.search(stockSymbolRegexPattern, url).group(1)

        return {
            "symbol": stockSymbol,
            "companyName": "-",
        }


def _parseStockExchangeData(urlAndPriceData):

    url = urlAndPriceData[0]
    priceData = urlAndPriceData[1]
    try:
        return {
            "symbol": priceData["chart"]["result"][0]["meta"]["symbol"],
            "stockExchange": priceData["chart"]["result"][0]["meta"][
                "fullExchangeName"
            ],
        }
    except KeyError as exception:
        logging.error(f"Exception occured when parsing stockExchange data for in _parseStockExchangeData. error: ")
        return {}


async def _makeUrlRequest(session: aiohttp.ClientSession, url) -> dict:
    logging.info(f"StockPriceHistoryInferace making request with _makeUrlRequest url={url}")
    
    # Initialize a semaphore object with a limit of 3 (max 3 downloads concurrently)
    limit = asyncio.Semaphore(2)
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36'
    }

    async with limit:
        logging.error(f"Request being made with headers={headers} to url={url}")
        response = await session.request("GET", url=url, headers=headers)

        try:
            responseJson = await response.json()
            return (url, responseJson)
        except aiohttp.client_exceptions.ContentTypeError as exception:
            logging.error(f"response={response}")
            return { "success": True }
        except Exception as exception:
            logging.exception(exception)
            return {}


async def  _getDataForUrlList(urls, dataProcessingFunction):
    connector = aiohttp.TCPConnector(limit=1)
    async with aiohttp.ClientSession(connector=connector) as session:
        tasks = []
        logging.info(f"num of urls={len(urls)}")
        for url in urls:
            tasks.append(_makeUrlRequest(session=session, url=url))

        data = []
        for task in asyncio.as_completed(tasks, timeout=10):
            # await the url request, parse the response using the dataProcessingFunction and append it to `data`
            taskResult = await task
            if not taskResult:
                logging.error(f"Task failed in _getDataForUrlList, skipping taskResult={taskResult}")
            data.append(dataProcessingFunction(taskResult))
                

        return data
    