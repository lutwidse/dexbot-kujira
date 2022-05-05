import os
from orca_dexbot import OrcaDexbot

dexbot = OrcaDexbot("testnet", os.environ["TESTNET_MNEMONIC"])
# dexbot.test_transaction(dexbot.usd_to_uusd(1))
dexbot.test_transaction_anchor_aust(
    dexbot.usd_to_uusd(1), 1, 99, dexbot.usd_to_uusd(1000000)
)
