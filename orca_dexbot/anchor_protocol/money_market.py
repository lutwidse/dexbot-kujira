class Overseer:
    def __init__(self, _terra, _contract, _logger):
        self._terra = _terra
        self._contract = _contract
        self._logger = _logger

    def epoch_state(self):
        try:
            query = {"epoch_state": {}}
            result = self._terra.wasm.contract_query(
                self._contract.ANCHOR_MARKET, query
            )
            self._logger.info(result)
            return result
        except:
            self._logger.debug("[_get_cw_token]", stack_info=True)
