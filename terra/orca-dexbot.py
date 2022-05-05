from terra_sdk.client.lcd import LCDClient
from terra_sdk.key.mnemonic import MnemonicKey

from terra_sdk.core.fee import Fee
from terra_sdk.core.bank import MsgSend
from terra_sdk.client.lcd.api.tx import CreateTxOptions

import os

COLUMBUS = ["https://lcd.terra.dev", "columbus-5"]
BOMBAY = ["https://bombay-lcd.terra.dev/", "bombay-12"]

mk = MnemonicKey(mnemonic=os.environ["TESTNET_MNEMONIC"])
terra = LCDClient(BOMBAY[0], BOMBAY[1])
wallet = terra.wallet(mk)

from_address = wallet.key.acc_address
to_address = wallet.key.acc_address

tx = wallet.create_and_sign_tx(CreateTxOptions(
    msgs=[MsgSend(
        from_address=from_address,
        to_address=to_address,
        amount="1000000uusd"
    )],
    memo="test transaction!",
    fee=Fee(200000, "1000000uusd")
))

result = terra.tx.broadcast(tx)
print(result)