import logging

from terra_sdk.client.lcd import LCDClient
from terra_sdk.client.lcd import Wallet
from terra_sdk.core import Coins, Coin
from orca_dexbot import contract
from terra_wrapper.wrapper import TerraWrapper


class Overseer(object):
    def __init__(self, _logger, _terra, _contract):
        self._logger: logging = _logger
        self._terra: LCDClient = _terra
        self._contract: contract = _contract

    def epoch_state(self):
        try:
            query = {"epoch_state": {}}
            result = self._terra.wasm.contract_query(
                self._contract.ANCHOR_MARKET, query
            )
            self._logger.debug(f"[_get_cw_token] : {result}")

            return result
        except:
            self._logger.debug("[_get_cw_token]", exc_info=True, stack_info=True)


class Market(object):
    def __init__(self, _logger, _wallet, _contract, _wrapper):
        self._logger: logging = _logger
        self._wallet: Wallet = _wallet
        self._contract: contract = _contract
        self._wrapper: TerraWrapper = _wrapper

    def deposit_stable(self, amount):
        try:
            msgs = self._wrapper._create_msg_execute_contract(
                    self._contract.ANCHOR_MARKET,
                    {"deposit_stable": {}},
                    Coins([Coin("uusd", amount)]),
                )
            
            self._logger.debug(f"[transaction_anchor] : {msgs}")

            tx = self._wrapper._create_transaction(msgs)
            self._logger.debug(f"[transaction_anchor] : {tx}")
        except:
            self._logger.debug("[transaction_anchor]", exc_info=True, stack_info=True)
