#!/usr/bin/python

# external dependencies
from enum import Enum


class StockExchange(Enum):
    NASDAQ = 1
    SP500 = 2
    AMEX = 3
    NYSE = 4
    FTSE100 = 5
