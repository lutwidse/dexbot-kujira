import base64
import logging
from terra_sdk.client.lcd import LCDClient
from terra_sdk.core.wasm.msgs import MsgExecuteContract
from terra_wrapper.wrapper import TerraWrapper
from orca_dexbot import contract


class Liquidation:
    def __init__(self, _logger, _terra, _contract, _wrapper):
        self._logger: logging = _logger
        self._terra: LCDClient = _terra
        self._contract: contract = _contract
        self._wrapper: TerraWrapper = _wrapper

    def submit_bid(self, amount, premium_slot, ltv, cumulative_value):
        # TODO:UST to aUST conversion
        msg = str(
            {
                "submit_bid": {
                    "premium_slot": premium_slot,
                    "collateral_token": self._contract.ANCHOR_BLUNA,
                    "strategy": {
                        "activate_at": {
                            "ltv": ltv,
                            "cumulative_value": cumulative_value,
                        },
                        "deactivate_at": {
                            "ltv": ltv,
                            "cumulative_value": cumulative_value,
                        },
                    },
                }
            }
        ).replace("'", '"')
        msg = base64.b64encode(msg.encode()).decode("ascii")

        msgs = [
            MsgExecuteContract(
                sender=self._ACC_ADDRESS,
                contract=self._contract.ANCHOR_AUST,
                execute_msg={
                    "send": {
                        "msg": msg,
                        "amount": self._usd_uusd_conversion(amount),
                        "contract": self._contract.KUJIRA_ORCA_AUST,
                    }
                },
            )
        ]
        tx = self._wrapper._create_transaction(msgs)
        self._logger.info(tx)
