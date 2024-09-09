#!/venv/bin/python

# external dependencies
import unittest
import mock

# internal dependencies
from webapp.server.interfaces.StockPriceHistoryInterface import (
    _buildGetPricesUrls,
    _parsePriceData,
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

        priceData = _parsePriceData(fakePriceData)

        expectedKeys = ["fakeTimestamp1", "fakeTimestamp2", "fakeTimestamp3"]
        expectedValues = ["fakeClose1", "fakeClose2", "fakeClose3"]

        self.assertEqual(3, len(priceData))
        self.assertEqual(expectedKeys, list(priceData.keys()))
        self.assertEqual(expectedValues, list(priceData.values()))
