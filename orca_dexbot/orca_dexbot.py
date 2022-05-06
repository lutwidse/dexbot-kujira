import logging

import base64
from terra_sdk.core.wasm.msgs import MsgExecuteContract

from .contract import MainnetContract, TestnetContract
from .anchor_protocol.anchor import Anchor
from terra_wrapper.wrapper import TerraWrapper

from terra_sdk.client.lcd import LCDClient
from terra_sdk.key.mnemonic import MnemonicKey

from terra_sdk.client.lcd.api.tx import CreateTxOptions
from terra_sdk.core.bank import MsgSend
from terra_sdk.core import Coins, Coin
from terra_sdk.core.broadcast import (
    BlockTxBroadcastResult,
)

COLUMBUS = ["https://lcd.terra.dev", "columbus-5"]
BOMBAY = ["https://bombay-lcd.terra.dev/", "bombay-12"]


class OrcaDexbot(Anchor):
    def __init__(self, network, mnemonic):

        self._logger = logging.getLogger(__name__)
        self._logger.setLevel(level=logging.DEBUG)
        handler = logging.FileHandler("debug.log")
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        handler.setFormatter(formatter)
        self._logger.addHandler(handler)

        if network == "mainnet":
            self._terra = LCDClient(COLUMBUS[0], COLUMBUS[1])
            self._contract = MainnetContract()
        elif network == "testnet":
            self._terra = LCDClient(BOMBAY[0], BOMBAY[1])
            self._contract = TestnetContract()

        self._wallet = self._terra.wallet(MnemonicKey(mnemonic=mnemonic))
        self._sequence = self._wallet.sequence()

        self._wrapper = TerraWrapper(self._logger, self._terra, self._wallet, self._sequence)
        self._anchor = Anchor(
            self._logger, self._terra, self._wallet, self._sequence, self._wrapper
        )

    def usd_uusd_conversion(
        self, usd, is_usd=True, is_str=False, is_need_prefix=False
    ) -> any:
        if is_usd:
            result = usd * 1000000
        else:
            result = usd / 1000000
        if is_str:
            result = str(result)
        if is_need_prefix:
            result = result + "uusd"
        self._logger.info(f"[usd_uusd_conversion] : {result}")
        return result

    def get_native_token(self, wallet_address) -> Coins:  # (Coins, dict):
        try:
            result = self._terra.bank.balance(wallet_address)
            self._logger.info(f"[get_native_token] : {result}")
            return result
        except:
            self._logger.debug("[get_native_token]", exc_info=True, stack_info=True)

    def get_cw_token(self, token_address) -> dict:
        try:
            query = {"balance": {"address": self._wallet.key.acc_address}}
            result = self._terra.wasm.contract_query(token_address, query)
            self._logger.info(f"[get_cw_token] : {result}")
            return result
        except:
            self._logger.debug("[get_cw_token]", exc_info=True, stack_info=True)

    def get_bluna_contract(self) -> str:
        return self._contract.ANCHOR_BLUNA

    def _create_transaction(self, msgs) -> BlockTxBroadcastResult:
        try:
            self._logger.info("[_create_transaction]", msgs)

            tx = self._wallet.create_and_sign_tx(
                CreateTxOptions(
                    msgs=msgs,
                    gas="auto",
                    fee_denoms="uusd",
                    gas_adjustment=2,
                    sequence=self._sequence,
                )
            )
            self._sequence = self._sequence + 1
            result = self._terra.tx.broadcast(tx)
            return result
        except:
            self._logger.debug("[_create_transaction]", stack_info=True)

    def transaction_test(self, amount):
        msgs = [
            MsgSend(
                from_address=self._wallet.key.acc_address,
                to_address=self._wallet.key.acc_address,
                amount=Coins([Coin("uusd", amount)]),
            )
        ]
        tx = self._wrapper._create_transaction(msgs)
        self._logger.debug(f"[transaction_test] : {tx}")

    def transaction_anchor_deposit(self, amount):
        self.deposit_stable(amount)

    def transaction_kujira_bid(
        self, amount, premium_slot, collateral_token, ltv, cumulative_value
    ):
        self.submit_bid(amount, premium_slot, collateral_token, ltv, cumulative_value)

    def transaction_kujira_claim_bids(self, collateral_token, bids):
        self._anchor._liquidation.claim_liquidations(collateral_token, bids)
