import logging

from .anchor_protocol.anchor import Anchor
from orca_dexbot.astroport.astroport import Astroport

from .contract import MainnetContract, TestnetContract
from terra_wrapper.wrapper import TerraWrapper

from terra_sdk.client.lcd import LCDClient
from terra_sdk.key.mnemonic import MnemonicKey

from terra_sdk.core.bank import MsgSend
from terra_sdk.core import Coins, Coin

COLUMBUS = ["https://lcd.terra.dev", "columbus-5"]
BOMBAY = ["https://bombay-lcd.terra.dev/", "bombay-12"]


class OrcaDexbot(Anchor, Astroport):
    def __init__(self, network, mnemonic):

        self._logger = logging.getLogger(__name__)
        self._logger.setLevel(level=logging.DEBUG)
        handler = logging.FileHandler("debug.log")
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        handler.setFormatter(formatter)
        self._logger.addHandler(handler)

        # We should not change the contract.py to be inheritable to prevent human error. You will potentially lose funds if there's no double-check.
        # Therefore contract address in anchor_protocol, astroport is set by default as well.
        if network == "mainnet":
            self._terra = LCDClient(COLUMBUS[0], COLUMBUS[1])
            self._contract = MainnetContract()
        elif network == "testnet":
            self._terra = LCDClient(BOMBAY[0], BOMBAY[1])
            self._contract = TestnetContract()

        # TODO: Save mnemonic securely on local with bcrypt
        self._wallet = self._terra.wallet(MnemonicKey(mnemonic=mnemonic))
        self._sequence = self._wallet.sequence()

        self._wrapper = TerraWrapper(
            self._logger, self._terra, self._wallet, self._sequence
        )

    def denom_conversion(
        self, amount, multiply=True, is_str=False, is_need_prefix=False
    ) -> any:
        if multiply:
            result = round(int(amount) * 1000000)
        else:
            result = round(int(amount) / 1000000)
        if is_str:
            result = str(result)
        if is_need_prefix:
            result = result + "uusd"
        self._logger.info(f"[denom_conversion] : {result}")
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

    def get_wallet_address(self) -> str:
        return self._wallet.key.acc_address

    def get_bluna_contract(self) -> str:
        return self._contract.ANCHOR_BLUNA
    
    def get_aust_contract(self) -> str:
        return self._contract.ANCHOR_AUST

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