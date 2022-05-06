from .money_market import Overseer, Market
from .liquidation import Liquidation

class Anchor():
    def __init__(self, _logger, _terra, _wallet, _contract, _wrapper):
        self._overseer = Overseer(_logger, _terra, _contract)
        self._market = Market(_logger, _wallet, _contract)
        self._liquidation = Liquidation(_logger, _terra, _wallet, _contract, _wrapper)