#!/usr/bin/python

# external dependencies
from abc import ABC, abstractmethod

"""
InvestingInterface

Provides a structure for classes that will interact with investing APIs

"""
class InvestingInterface(ABC):


    """
    `buyStock`: execute buy trade of stock `stockSymbol` for `quantity` units
    """
    @abstractmethod
    def buyStock(self, stockSymbol: str, quantity: int) -> None:
        pass


    """
    `sellStock`: execute sell trade of stock `stockSymbol` for `quantity` units
    """
    @abstractmethod
    def sellStock(self, stockSymbol: str, quantity: int) -> None:
        pass


    """
    `getAvailableFunds`: return any uninvested funds 
    """
    @abstractmethod
    def getAvailableFunds(self) -> float:
        pass


    """
    `getPortfolioValue`: return the value of stocks + uninvested funds
    """
    @abstractmethod
    def getPortfolioValue(self) -> float:
        pass


    """
    `getOpenPositions`: return all positions currently held 
    """
    @abstractmethod
    def getOpenPositions(self: object) -> 'dict[str, int]':
        pass



    """
    `getStockDataList`: return stock data on each stockSymbol in `stockSymbols`
    """
    @abstractmethod
    def getStockDataList(self: object, stockSymbols: 'list[str]') -> dict:
        pass