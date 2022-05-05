import logging
import base64

from .contract import MainnetContract, TestnetContract

from terra_sdk.client.lcd import LCDClient
from terra_sdk.key.mnemonic import MnemonicKey

from terra_sdk.client.lcd.api.tx import CreateTxOptions
from terra_sdk.core.bank import MsgSend
from terra_sdk.core.wasm.msgs import MsgExecuteContract
from terra_sdk.core import Coins, Coin
from terra_sdk.core.broadcast import (
    BlockTxBroadcastResult,
)

COLUMBUS = ["https://lcd.terra.dev", "columbus-5"]
BOMBAY = ["https://bombay-lcd.terra.dev/", "bombay-12"]

logger = logging.getLogger(__name__)
logger.setLevel(level=logging.DEBUG)
handler = logging.FileHandler("debug.log")
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)


class OrcaDexbot:
    def __init__(self, network, mnemonic):
        if network == "mainnet":
            self._terra = LCDClient(COLUMBUS[0], COLUMBUS[1])
            self._contract = MainnetContract()
        elif network == "testnet":
            self._terra = LCDClient(BOMBAY[0], BOMBAY[1])
            self._contract = TestnetContract()
        self._wallet = self._terra.wallet(MnemonicKey(mnemonic=mnemonic))
        self._sequence = self._wallet.sequence()
        self._ACC_ADDRESS = self._wallet.key.acc_address

    def _usd_to_uusd(self, usd) -> str:
        result = str(usd * 1000000)
        logger.info(result)
        return result

    def _get_native_token(self, wallet_address) -> dict:
        try:
            result = self._terra.bank.balance(wallet_address)
            logger.info(result)
            return result
        except:
            logger.debug(stack_info=True)

    def _get_cw_token(self, token_address) -> dict:
        try:
            query = {"balance": {"address": self._ACC_ADDRESS}}
            result = self._terra.wasm.contract_query(token_address, query)
            logger.info(result)
            return result
        except:
            logger.debug("[_get_cw_token]", stack_info=True)

    def _create_transaction(self, msgs) -> BlockTxBroadcastResult:
        try:
            logger.info(msgs)

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
            logger.debug("[_create_transaction]", stack_info=True)

    def test_transaction(self, amount):
        msgs = [
            MsgSend(
                from_address=self._ACC_ADDRESS,
                to_address=self._ACC_ADDRESS,
                amount=Coin("uusd", self._usd_to_uusd(amount)),
            )
        ]
        tx = self.create_transaction(msgs)
        logger.debug(tx)

    def transaction_anchor(self, amount):
        msgs = [
            MsgExecuteContract(
                sender=self._ACC_ADDRESS,
                contract=self._contract.ANCHOR_MARKET,
                execute_msg={"deposit_stable": {}},
                coins=Coins([Coin("uusd", self._usd_to_uusd(amount))]),
            )
        ]
        tx = self.create_transaction(msgs)
        logger.info(tx)

    def transaction_anchor_aust(self, amount, premium_slot, ltv, cumulative_value):
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
                        "amount": self._usd_to_uusd(amount),
                        "contract": self._contract.KUJIRA_ORCA_AUST,
                    }
                },
            )
        ]
        tx = self.create_transaction(msgs)
        logger.info(tx)
