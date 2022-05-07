import logging, base64
from terra_sdk.client.lcd import Wallet
from terra_sdk.core import Coins, Coin
from terra_wrapper.wrapper import TerraWrapper
from orca_dexbot import contract

class Swap:
    def __init__(self, _logger, _wallet, _contract, _wrapper):
        self._logger: logging = _logger
        self._wallet: Wallet = _wallet
        self._contract: contract = _contract
        self._wrapper: TerraWrapper = _wrapper

    def swap_bluna_to_luna(self, amount, max_spread="0.005"):
        try:
            msg = str({"swap": {"max_spread": max_spread}}).replace("'", '"')
            msg = base64.b64encode(msg.encode()).decode("ascii")
            
            msgs = [
                self._wrapper._create_msg_execute_contract(
                    contract=self._contract.ANCHOR_BLUNA,
                    execute_msg={
                        "send": {
                            "msg": msg,
                            "amount": amount,
                            "contract": self._contract.ASTROPORT_BLUNA_LUNA,
                        }
                    },
                )
            ]
            self._logger.debug(f"[swap_bluna_to_luna] : {msgs}")

            tx = self._wrapper._create_transaction(msgs)
            self._logger.debug(f"[swap_bluna_to_luna] : {tx}")
        except:
            self._logger.debug(
                "[swap_bluna_to_luna]",
                exc_info=True,
                stack_info=True,
            )

    def swap_luna_to_ust(self, amount, max_spread="0.005"):
        try:
            msg = {
                "swap": {
                    "max_spread": max_spread,
                    "offer_asset": {
                        "info": {"native_token": {"denom": "uluna"}},
                        "amount": amount,
                    },
                }
            }

            msgs = [
                self._wrapper._create_msg_execute_contract(
                    contract=self._contract.ASTROPORT_LUNA_UST,
                    execute_msg=msg,
                    coins=Coins([Coin("uluna", amount)]),
                )
            ]
            self._logger.debug(f"[swap_luna_to_ust] : {msgs}")

            tx = self._wrapper._create_transaction(msgs)
            self._logger.debug(f"[swap_luna_to_ust] : {tx}")
        except:
            self._logger.debug(
                "[swap_luna_to_ust]",
                exc_info=True,
                stack_info=True,
            )