

from ast import Raise


class ProgramConfiguration:

    def __init__(self, stockIndex, exchangeRangeTopIndex, exchangeRangeBottomIndex, divisionWeights):
        self.stockIndex = stockIndex
        self.exchangeRangeTopIndex = exchangeRangeTopIndex
        self.exchangeRangeBottomIndex = exchangeRangeBottomIndex
        if ProgramConfiguration.validateDivisionWeights(divisionWeights):
            self.divisionWeights = divisionWeights
        else:
            raise Exception("divisonWeights validation failed, please provide a list of 10 values which sum to 100")

    @classmethod
    def validateDivisionWeights(self, divisionWeights):
        divisionWeightsValid = True

        divisionWeightsValid = len(divisionWeights) == 10
        divisionWeightsValid = sum(divisionWeights) == 100

        return divisionWeightsValid