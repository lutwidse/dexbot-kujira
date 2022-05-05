import logging

from terra_sdk.client.lcd import LCDClient
from terra_sdk.key.mnemonic import MnemonicKey

from terra_sdk.core.fee import Fee
from terra_sdk.core.bank import MsgSend
from terra_sdk.client.lcd.api.tx import CreateTxOptions

from terra_sdk.core.broadcast import (
    BlockTxBroadcastResult,
)

COLUMBUS = ['https://lcd.terra.dev', 'columbus-5']
BOMBAY = ['https://bombay-lcd.terra.dev/', 'bombay-12']

logger = logging.getLogger(__name__)
logger.setLevel(level=logging.DEBUG)
handler = logging.FileHandler('debug.log')
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

class OrcaDexbot():
    def __init__(self, network, mnemonic):
        if network == 'mainnet':
            self.terra = LCDClient(COLUMBUS[0], COLUMBUS[1])
        elif network == 'testnet':
            self.terra = LCDClient(BOMBAY[0], BOMBAY[1])
        self.wallet = self.terra.wallet(MnemonicKey(mnemonic=mnemonic))

    def usd_to_uusd(self, usd) -> str:
        return str(usd*1000000) + 'uusd'

    def create_transaction(self, msgs) -> BlockTxBroadcastResult:
        tx = self.wallet.create_and_sign_tx(CreateTxOptions(
            msgs=msgs,
        ))
        result = self.terra.tx.broadcast(tx)
        return result
    
    def test_transaction(self, amount):
        from_address = self.wallet.key.acc_address
        to_address = self.wallet.key.acc_address
        msgs=[MsgSend(
            from_address=from_address,
            to_address=to_address,
            amount=amount
            )]
        tx = self.create_transaction(msgs)
        logger.debug(tx)