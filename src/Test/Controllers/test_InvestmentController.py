#!/usr/bin/python

# external dependencies
import json
import unittest
from unittest import mock
import matplotlib.pyplot as plt; plt.rcdefaults()
import numpy as np
import matplotlib.pyplot as plt

# internal dependencies
from src.Controllers.InvestmentController import InvestmentController
from Types.StockData import StockData

class TestInvestmentController(unittest.TestCase):

    @mock.patch("src.Controllers.InvestmentController.logging")
    @mock.patch("src.Controllers.InvestmentController.InvestmentController._alpacaInterface.getOpenPositions")
    def test_rebalanceInvestments(self, getOpenPositionsMock, loggingMock):
        # configure fake data
        fakeOpenPositions = ["fakeOpenPosition1", "fakeOpenPosition2"]

        # configure mocks
        getOpenPositionsMock.return_value = fakeOpenPositions

        # run testable function
        InvestmentController().rebalanceInvestments()

        # asserts
        getOpenPositionsMock.assert_called()
        self.assertEquals(6, loggingMock.call_count)


if __name__ == '__main__':
    unittest.main()
