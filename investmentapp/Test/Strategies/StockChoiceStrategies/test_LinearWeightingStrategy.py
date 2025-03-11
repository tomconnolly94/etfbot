#!/usr/bin/python

# external dependencies
import json
import time
import unittest
from unittest import mock
from unittest.mock import MagicMock
import numpy as np
from investmentapp.src.Strategies.StockChoiceStrategies.LinearWeightingStrategy import (
    LinearWeightingStrategy,
)
import random

# internal dependencies
from investmentapp.src.Types.StockData import StockData


class TestCustomWeightingStrategy(unittest.TestCase):

    def _loadStockData(self):

        stockData = []

        with open("Test/TestData/StockDataListRandomPrice.json", "r") as read_file:
            stockDataRaw = json.load(read_file)

            for item in stockDataRaw:
                stockData.append(StockData(item["symbol"], item["price"]))

        return stockData

    def test__getSellOrders(self):
        # configure fake data
        fakeOpenPositions = {"A": 5, "B": 5, "C": 5, "D": 5, "E": 5, "F": 5}
        openPositionListPositions = [295, 300, 350, 399, 400, 450]

        fullStockRange = []
        # config mocks
        AlpacaInterfaceMagicMock = MagicMock()
        AlpacaInterfaceMagicMock.getOpenPositions.return_value = fakeOpenPositions
        AlpacaInterfaceMagicMock.getStockCache.return_value = fullStockRange
        linearWeightingStrategy = LinearWeightingStrategy(AlpacaInterfaceMagicMock)

        for i in range(0, 500):
            if i in openPositionListPositions:
                positionSymbol = list(fakeOpenPositions.keys())[
                    openPositionListPositions.index(i)
                ]
                fullStockRange.append(StockData(positionSymbol, random.randint(0, 9)))
            else:
                fullStockRange.append(StockData(str(i), random.randint(0, 9)))

        positionsToSell = linearWeightingStrategy.getSellOrders()

        self.assertEqual(1, len(positionsToSell))
        self.assertTrue("F" in positionsToSell)

    def test__reorderStockDataListBasedOnExistingPositions(self):

        # config mocks
        AlpacaInterfaceMagicMock = MagicMock()
        linearWeightingStrategy = LinearWeightingStrategy(AlpacaInterfaceMagicMock)

        # inputs
        stockDataList = [
            StockData("stock1", 1),
            StockData("stock2", 2),
            StockData("stock3", 3),
        ]
        existingPositions = {"stock1": 3, "stock3": 1}

        # testable function
        orderedStockDataList: "list[StockData]" = (
            linearWeightingStrategy._reorderStockDataListBasedOnExistingPositions(
                stockDataList, existingPositions
            )
        )

        expectedOrderedStockDataList = [
            StockData("stock2", 2),
            StockData("stock3", 3),
            StockData("stock1", 1),
        ]

        # asserts
        self.assertEqual(len(expectedOrderedStockDataList), len(orderedStockDataList))

        for i, expectedOrderedStockData in enumerate(expectedOrderedStockDataList):
            self.assertEqual(
                expectedOrderedStockData.symbol, orderedStockDataList[i].symbol
            )
            self.assertEqual(
                expectedOrderedStockData.price, orderedStockDataList[i].price
            )

    def test__getBuyingQuantities(self):

        # config mocks
        AlpacaInterfaceMagicMock = MagicMock()
        linearWeightingStrategy = LinearWeightingStrategy(AlpacaInterfaceMagicMock)

        # inputs
        funds = 103
        stockDataList = sorted(
            [
                StockData("A", 10),
                StockData("B", 10),
                StockData("C", 5),
                StockData("D", 5),
                StockData("E", 5),
                StockData("F", 5),
                StockData("G", 5),
                StockData("H", 5),
                StockData("I", 5),
                StockData("J", 5),
            ],
            key=lambda stockData: -stockData.price,
        )

        numberOfSharesToBuy = linearWeightingStrategy._getBuyingQuantities(
            funds, stockDataList
        )

        self.assertEqual(2, numberOfSharesToBuy["A"])
        self.assertEqual(2, numberOfSharesToBuy["B"])
        self.assertEqual(2, numberOfSharesToBuy["C"])
        self.assertEqual(2, numberOfSharesToBuy["D"])
        self.assertEqual(2, numberOfSharesToBuy["E"])
        self.assertEqual(2, numberOfSharesToBuy["F"])
        self.assertEqual(1, numberOfSharesToBuy["G"])
        self.assertEqual(1, numberOfSharesToBuy["H"])
        self.assertEqual(1, numberOfSharesToBuy["I"])
        self.assertEqual(1, numberOfSharesToBuy["J"])


if __name__ == "__main__":
    unittest.main()
