from .swap import Swap

class Astroport(Swap):
    def __init__(self, _logger, _terra, _wallet, _contract, _wrapper):
        super(Astroport, self).__init__(_logger, _terra, _wallet, _contract, _wrapper)

