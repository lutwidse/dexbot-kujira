import base64
import logging

from terra_sdk.client.lcd import Wallet
from terra_sdk.client.lcd import LCDClient
from terra_sdk.core.wasm.msgs import MsgExecuteContract
from terra_wrapper.wrapper import TerraWrapper
from orca_dexbot import contract


class Liquidation:
    def __init__(self, _logger, _terra, _wallet, _contract, _wrapper):
        self._logger: logging = _logger
        self._terra: LCDClient = _terra
        self._wallet: Wallet = _wallet
        self._contract: contract = _contract
        self._wrapper: TerraWrapper = _wrapper

    def submit_bid(
        self,
        collateral_token=contract,
        amount=str,
        premium_slot=int,
        ltv=int,
        cumulative_value=str,
    ):
        try:
            # TODO:UST to aUST conversion
            msg = str(
                {
                    "submit_bid": {
                        "premium_slot": premium_slot,
                        "collateral_token": collateral_token,
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
                    sender=self._wallet.key.acc_address,
                    contract=self._contract.ANCHOR_AUST,
                    execute_msg={
                        "send": {
                            "msg": msg,
                            "amount": amount,
                            "contract": self._contract.KUJIRA_ORCA_AUST,
                        }
                    },
                )
            ]
            tx = self._wrapper._create_transaction(msgs)
            self._logger.debug("[submit_bid]", tx)
        except:
            self._logger.debug("[submit_bid]", exc_info=True, stack_info=True)

    def bids_by_user(
        self, collateral_token=str, bidder=str, start_after=int, limit=int
    ) -> dict:
        try:
            query = {
                "bids_by_user": {
                    "collateral_token": collateral_token,
                    "bidder": bidder,
                    "start_after": start_after,
                    "limit": limit,
                }
            }
            self._logger.debug(f"[bids_by_user] : {query}")

            result = self._terra.wasm.contract_query(
                self._contract.KUJIRA_ORCA_AUST, query
            )
            self._logger.debug(f"[bids_by_user] : {result}")
            return result
        except:
            self._logger.debug("[bids_by_user]", exc_info=True, stack_info=True)
