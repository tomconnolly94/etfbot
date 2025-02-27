#!/venv/bin/python

# external dependencies
import datetime
from dateutil import tz
import aiohttp
import asyncio
import logging

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
    try:
        return asyncio.run(
            _getDataForUrlList(_buildGetPricesUrls(symbols), _parsePriceData)
        )
    except Exception as exception:
        logging.error(exception)


def getCompanyNamesForStockSymbols(symbols):
    try:
        return asyncio.run(
            _getDataForUrlList(
                _buildGetCompanyNamesUrls(symbols), _parseCompanyNameData
            )
        )
    except Exception as exception:
        logging.error(exception)


def getStockExchangesForStockSymbol(stockSymbol: str):
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


def _parsePriceData(priceData):

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


def _parseCompanyNameData(priceData):

    try:
        return {
            "symbol": priceData["chart"]["result"][0]["meta"]["symbol"],
            "companyName": priceData["chart"]["result"][0]["meta"]["longName"],
        }
    except KeyError as exception:
        symbol = priceData["chart"]["result"][0]["meta"]["symbol"]
        logging.error(
            f"Exception occured when parsing companyName data for {symbol}. error: ",
            exception,
        )
        return {}


def _parseStockExchangeData(priceData):
    logging.error(3)
    try:
        return {
            "symbol": priceData["chart"]["result"][0]["meta"]["symbol"],
            "stockExchange": priceData["chart"]["result"][0]["meta"][
                "fullExchangeName"
            ],
        }
    except KeyError as exception:
        symbol = priceData["chart"]["result"][0]["meta"]["symbol"]
        logging.error(
            f"Exception occured when parsing stockExchange data for {symbol}. error: ",
            exception,
        )
        return {}


async def _makeUrlRequest(session: aiohttp.ClientSession, url) -> dict:
    logging.info(f"StockPriceHistoryInferace making request with _makeUrlRequest url={url}")
    response = await session.request("GET", url=url)
    try:
        return await response.json()
    except aiohttp.client_exceptions.ContentTypeError as exception:
        logging.error(f"response={response}")
        logging.exception(exception)
        return {}
    except Exception as exception:
        logging.exception(exception)
        return {}


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
