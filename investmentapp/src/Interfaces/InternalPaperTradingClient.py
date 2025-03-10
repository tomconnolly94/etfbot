#!/usr/bin/python

# external dependencies
import logging
from alpaca.trading.models import Position

# internal dependencies
from investmentapp.src.Interfaces import DatabaseInterface
from investmentapp.src.Interfaces.AlpacaInterface import AlpacaInterface
from alpaca.trading.requests import (
    MarketOrderRequest,
    GetOrdersRequest,
)
from alpaca.trading.enums import OrderSide, TimeInForce, QueryOrderStatus

from investmentapp.src.Types.StockOrder import OrderType, StockOrder

class InternalPaperTradingClient():

    def __init__(self, databaseInterface: DatabaseInterface, strategyId: str):
        self._databaseInterface = databaseInterface
        self._strategyId = strategyId

    def get_all_positions(self):
        positions = []

        ordersByStrategy = self._databaseInterface.getInternalPaperTradingOrdersByStrategy(self._strategyId)
        symbolsAndQuantities = self.getOwnedSymbolsAndQuantities(ordersByStrategy)

        for symbol, quantity in symbolsAndQuantities.items():
            position = Position(asset_id="abcdabcdabcdabcdabcdabcdabcdabcd",
                                symbol=symbol,
                                exchange="NYSE",
                                asset_class="us_equity",
                                avg_entry_price="0",
                                qty=str(int(quantity)),
                                side="long",
                                cost_basis="fakeCostBasis")
            positions.append(position)

        return positions

    def get_orders(self, filter: GetOrdersRequest):
        if filter.status == QueryOrderStatus.OPEN:
            return [] # we never have open orders because an "order" is a db record
        elif filter.status == QueryOrderStatus.CLOSED:
            return [
                StockOrder(order["symbol"],
                    float(order["transactionValue"]),
                    int(order["orderQuantity"]),
                    OrderType.BUY if order["buySell"] == "BUY" else OrderType.SELL,
                    order["date"],
                    order["date"])
                for order in self._databaseInterface.getInternalPaperTradingOrdersByStrategy(self._strategyId)
            ]

    def submit_order(self, order_data: MarketOrderRequest):

        stockPrice = AlpacaInterface().getStockDataList([order_data.symbol])[0].price

        buyInstruction = "buy" # TODO: should be OrderType.BUY

        # create new order value
        if not self._databaseInterface.createNewInternalPaperTradingOrder(
            self._strategyId,
            order_data.symbol,
            stockPrice,
            "BUY" if order_data.side == buyInstruction else "SELL",
            order_data.qty):
            logging.error("Something went wrong in _databaseInterface.createNewInternalPaperTradingOrder, returning early")
            return

        # update strategy cash value
        posNegMultiplier = -1 if order_data.side == buyInstruction else 1
        newCashValue = self.get_account().cash + (posNegMultiplier * stockPrice * order_data.qty)
        self._databaseInterface.updateInternalPaperTradingAccountCash(self._strategyId, newCashValue)

        logging.info(f"InternalPaperTradingClient::submit_order finished newCashValue={newCashValue}")


    def get_account(self):

        class InternalPaperTradingAccount:

            def __init__(self, strategyCash, strategyEquity, strategyId):
                self.id = f"InternalPaperTradingAccount-strategy-{strategyId}"
                self.cash = strategyCash
                self.equity = strategyEquity

            def __repr__(self):
                return f"InternalPaperTradingAccount(id='{self.id}', cash={self.cash}, equity={self.equity})"


        strategyCash = self._databaseInterface.getInternalPaperTradingAccountCash(self._strategyId)
        strategyEquity = self.getTotalStockValue()

        return InternalPaperTradingAccount(strategyCash, strategyEquity, self._strategyId)


    def getOwnedSymbolsAndQuantities(self, orders):

        symbolQuantityOwned = {}

        for order in orders:

            if order["symbol"] not in symbolQuantityOwned:
                symbolQuantityOwned[order["symbol"]] = 0

            if(order["buySell"] == "BUY"):
                symbolQuantityOwned[order["symbol"]] += order["orderQuantity"]

            if(order["buySell"] == "SELL"):
                symbolQuantityOwned[order["symbol"]] -= order["orderQuantity"]

        return symbolQuantityOwned


    def getTotalStockValue(self):
        ordersForStrategy = self._databaseInterface.getInternalPaperTradingOrdersByStrategy(self._strategyId)
        ownedSymbolsAndQuantities = self.getOwnedSymbolsAndQuantities(ordersForStrategy)
        symbols = ownedSymbolsAndQuantities.keys()

        if len(symbols) == 0:
            return 0

        currentStockPrices = { stockData.symbol: stockData.price
                    for stockData in
                    AlpacaInterface().getStockDataList(ownedSymbolsAndQuantities.keys()) }
        logging.info(f"currentStockPrices: {currentStockPrices}")

        ownedSymbolsAndValues = {}
        for symbol, quantity in ownedSymbolsAndQuantities.items():
            ownedSymbolsAndValues[symbol] = currentStockPrices[symbol] * quantity

        # logging.info(f"ownedSymbolsAndValues: {ownedSymbolsAndValues}")
        return sum(ownedSymbolsAndValues.values())
