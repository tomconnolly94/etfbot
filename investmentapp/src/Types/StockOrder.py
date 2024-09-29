#!/usr/bin/python

"""
StockData

This is a model class to represent a stock within the program

"""

from enum import Enum
from datetime import datetime
import logging
from alpaca.trading.models import Order


class OrderType(Enum):
    SELL = 1
    BUY = 2


class StockOrder:

    def __init__(
        self: object,
        symbol: str,
        price: float,
        quantity: int,
        orderType: OrderType,
        createdDate: datetime,
        filledDate: datetime,
    ):
        self.symbol = symbol
        self.price = price
        self.quantity = quantity
        self.orderType = orderType
        self.createdDate = createdDate
        self.filledDate = filledDate

    def __init__(self: object, alpacaOrder: Order):
        self.symbol = alpacaOrder.symbol
        self.price = alpacaOrder.filled_avg_price
        self.quantity = alpacaOrder.qty
        self.orderType = (
            OrderType.SELL if alpacaOrder.side.name == "SELL" else OrderType.BUY
        )
        self.filledDate = self.createdDate = None
        if hasattr(alpacaOrder, "created_at") and alpacaOrder.created_at:
            self.createdDate = alpacaOrder.created_at.strftime("%d/%m/%Y")

        if hasattr(alpacaOrder, "filled_at") and alpacaOrder.filled_at:
            self.filledDate = alpacaOrder.filled_at.strftime("%d/%m/%Y")

    def __str__(self) -> str:
        return (
            f"StockOrder({self.symbol}, {self.price}, {self.quantity}, "
            f"{self.orderType}, {self.createdDate}, {self.filledDate})"
        )

    def asdict(self) -> dict:
        return {
            "symbol": self.symbol,
            "price": self.price,
            "quantity": self.quantity,
            "orderType": self.orderType.name,
            "createdDate": self.createdDate,
            "filledDate": self.filledDate,
        }

    def isCompleted(self) -> bool:
        return (
            self.symbol
            and self.price
            and self.quantity
            and self.orderType
            and self.createdDate
            and self.filledDate
        )
