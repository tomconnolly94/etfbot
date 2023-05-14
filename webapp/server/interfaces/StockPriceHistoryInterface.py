#!/venv/bin/python

# external dependencies
import datetime
import json
import urllib

# internal dependencies

    
def getPrices(symbol):
    timestampNow = (datetime.datetime.now() - datetime.timedelta(days=1)).strftime("%s")
    timestampOneYearAgo = (datetime.datetime.now() - datetime.timedelta(weeks=52)).strftime("%s")

    url = f"https://query2.finance.yahoo.com/v8/finance/chart/{urllib.parse.quote(symbol)}?period1={timestampOneYearAgo}&period2={timestampNow}&interval=1d&events=history"

    reqResponse = urllib.request.urlopen(url)
    rawData = json.loads(reqResponse.read().decode('utf-8'))
    try:
        labels = rawData["chart"]["result"][0]["timestamp"]
        values = rawData["chart"]["result"][0]["indicators"]["quote"][0]["close"]
        dataDict = {}

        for index, label in enumerate(labels):
            dataDict[label] = values[index]
        return dataDict
    except KeyError as exception:
        print(f"Exception occured when parsing data for {symbol} with url {url}. Problematic key: ", exception)
        return {}