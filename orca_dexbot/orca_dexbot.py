import logging
import base64

from .contract import Contract

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
        elif network == "testnet":
            self._terra = LCDClient(BOMBAY[0], BOMBAY[1])
        self._wallet = self._terra.wallet(MnemonicKey(mnemonic=mnemonic))
        self._sequence = self._wallet.sequence()
        self._ACC_ADDRESS = self._wallet.key.acc_address
        self._contract = Contract()

    def _usd_to_uusd(self, usd) -> str:
        return str(usd * 1000000)

    def create_transaction(self, msgs) -> BlockTxBroadcastResult:
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

    def test_transaction(self, amount):
        msgs = [
            MsgSend(
                from_address=self._ACC_ADDRESS,
                to_address=self._ACC_ADDRESS,
                amount=Coin("uusd", amount),
            )
        ]
        tx = self.create_transaction(msgs)
        logger.debug(tx)

    def test_transaction_anchor(self, amount):
        msgs = [
            MsgExecuteContract(
                sender=self._ACC_ADDRESS,
                contract=self._contract.TESTNET_ANCHOR_MARKET,
                execute_msg={"deposit_stable": {}},
                coins=Coins([Coin("uusd", amount)]),
            )
        ]
        tx = self.create_transaction(msgs)
        logger.debug(tx)

    def test_transaction_anchor_aust(self, amount, premium_slot, ltv, cumulative_value):
        msg = str(
            {
                "submit_bid": {
                    "premium_slot": premium_slot,
                    "collateral_token": self._contract.TESTNET_ANCHOR_BLUNA,
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
                contract=self._contract.TESTNET_ANCHOR_AUST,
                execute_msg={
                    "send": {
                        "msg": msg,
                        "amount": amount,
                        "contract": self._contract.TESTNET_KUJIRA_ORCA_AUST,
                    }
                },
            )
        ]
        tx = self.create_transaction(msgs)
        logger.debug(tx)
