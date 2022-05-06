import logging

from .contract import MainnetContract, TestnetContract
from .anchor_protocol.money_market import Overseer
from .anchor_protocol.liquidation import Liquidation
from terra_wrapper.wrapper import TerraWrapper

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
        if network == 'mainnet':
            self._terra = LCDClient(COLUMBUS[0], COLUMBUS[1])
            self._contract = MainnetContract()
        elif network == 'testnet':
            self._terra = LCDClient(BOMBAY[0], BOMBAY[1])
            self._contract = TestnetContract()

        self._wallet = self._terra.wallet(MnemonicKey(mnemonic=mnemonic))
        self._sequence = self._wallet.sequence()

        self._wrapper = TerraWrapper(logger, self._terra, self._wallet, self._sequence)
        self._overseer = Overseer(logger, self._terra, self._contract)
        self._liquidation = Liquidation(
            logger, self._terra, self._wallet, self._contract, self._wrapper
        )

    def _usd_uusd_conversion(self, usd, is_usd=True, is_str=False, is_need_prefix=False) -> any:
        if is_usd:
            result = usd * 1000000
        else:
            result = usd / 1000000
        if is_str:
            result = str(result)
        if is_need_prefix:
            result = result + 'uusd'
        logger.info('[_usd_uusd_conversion]', result)
        return result

    def _get_native_token(self, wallet_address) -> dict:
        try:
            result = self._terra.bank.balance(wallet_address)
            logger.info('[_get_native_token]', result)
            return result
        except:
            logger.debug('[_get_native_token]', exc_info=True, stack_info=True)

    def _get_cw_token(self, token_address) -> dict:
        try:
            query = {"balance": {"address": self._wallet.key.acc_address}}
            result = self._terra.wasm.contract_query(token_address, query)
            logger.info('[_get_cw_token]', result)
            return result
        except:
            logger.debug('[_get_cw_token]', exc_info=True, stack_info=True)

    def _create_transaction(self, msgs) -> BlockTxBroadcastResult:
        try:
            logger.info('[_create_transaction]', msgs)

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
            logger.debug('[_create_transaction]', stack_info=True)

    def test_transaction(self, amount):
        msgs = [
            MsgSend(
                from_address=self._wallet.key.acc_address,
                to_address=self._wallet.key.acc_address,
                amount=Coins([Coin("uusd", self._usd_uusd_conversion(amount))]),
            )
        ]
        tx = self._wrapper._create_transaction(msgs)
        logger.debug('[test_transaction]', tx)

    def transaction_anchor(self, amount):
        msgs = [
            MsgExecuteContract(
                sender=self._wallet.key.acc_address,
                contract=self._contract.ANCHOR_MARKET,
                execute_msg={"deposit_stable": {}},
                coins=Coins([Coin("uusd", self._usd_uusd_conversion(amount))]),
            )
        ]
        tx = self._wrapper._create_transaction(msgs)
        logger.info('[transaction_anchor]', tx)

    def transaction_anchor_aust(self, amount, premium_slot, ltv, cumulative_value):
        cumulative_value *= 1000000
        self._liquidation.submit_bid(self._usd_uusd_conversion(amount, is_str=True), premium_slot, ltv, self._usd_uusd_conversion(cumulative_value, is_str=True))
