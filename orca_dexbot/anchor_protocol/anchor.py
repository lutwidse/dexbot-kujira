from .money_market import Overseer, Market
from .liquidation import Liquidation


class Anchor(Liquidation, Overseer, Market):
    def __init__(self, _logger, _terra, _wallet, _contract, _wrapper):
        super(Anchor, self).__init__(_logger, _terra, _wallet, _contract, _wrapper)

