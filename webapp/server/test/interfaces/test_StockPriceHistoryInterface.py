#!/venv/bin/python

# external dependencies
import unittest
import mock

# internal dependencies
from webapp.server.interfaces.StockPriceHistoryInterface import (
    _buildGetPricesUrls,
    _parsePriceData,
    _parseCompanyNameData
)
from webapp.server.test.testUtilities import FakeFile


class Test_StockPriceHistoryInterface(unittest.TestCase):

    def test__buildGetPricesUrls(self):

        # config fake data
        fakeSymbols = ["symbol1", "symbol2"]

        pricesUrls = _buildGetPricesUrls(fakeSymbols)

        self.assertTrue(fakeSymbols[0] in pricesUrls[0])
        self.assertTrue(
            "https://query2.finance.yahoo.com/v8/finance/chart" in pricesUrls[0]
        )
        self.assertTrue("period1=" in pricesUrls[0])
        self.assertTrue(fakeSymbols[1] in pricesUrls[1])
        self.assertTrue(
            "https://query2.finance.yahoo.com/v8/finance/chart" in pricesUrls[1]
        )
        self.assertTrue("period2" in pricesUrls[1])

    def test__parsePriceData(self):

        # config fake data
        fakePriceData = {
            "chart": {
                "result": [
                    {
                        "timestamp": [
                            "fakeTimestamp1",
                            "fakeTimestamp2",
                            "fakeTimestamp3",
                        ],
                        "indicators": {
                            "quote": [
                                {"close": ["fakeClose1", "fakeClose2", "fakeClose3"]}
                            ]
                        },
                        "meta": {"symbol": "fakeSymbol1"},
                    }
                ]
            }
        }
        fakeUrl = "http://my.com/fake/url"

        priceData = _parsePriceData((fakeUrl, fakePriceData))

        expectedKeys = ["fakeTimestamp1", "fakeTimestamp2", "fakeTimestamp3"]
        expectedValues = ["fakeClose1", "fakeClose2", "fakeClose3"]

        self.assertEqual(3, len(priceData))
        self.assertEqual(expectedKeys, list(priceData.keys()))
        self.assertEqual(expectedValues, list(priceData.values()))


    def test__parseCompanyNameData(self):


        # config fake data
        fakeSymbol = "fakeSymbol1"
        fakeCompanyName = "fakeCompanyName1"
        fakePriceData = {
            "chart": {
                "result": [
                    {
                        "timestamp": [
                            "fakeTimestamp1",
                            "fakeTimestamp2",
                            "fakeTimestamp3",
                        ],
                        "indicators": {
                            "quote": [
                                {"close": ["fakeClose1", "fakeClose2", "fakeClose3"]}
                            ]
                        },
                        "meta": {
                            "symbol": fakeSymbol,
                            "longName": fakeCompanyName
                        },
                    }
                ]
            }
        }

        companyNameData = _parseCompanyNameData((f"https://query2.finance.yahoo.com/v8/finance/chart/{fakeSymbol}?period1=1741046400&period2=1741046400", fakePriceData))

        expectedCompanyNameData = {
            "symbol": fakeSymbol,
            "companyName": fakeCompanyName,
        }

        self.assertEqual(expectedCompanyNameData, companyNameData)
