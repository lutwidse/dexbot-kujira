import os
from orca_dexbot import OrcaDexbot

dexbot = OrcaDexbot("testnet", os.environ["TESTNET_MNEMONIC"])
dexbot.test_transaction(dexbot.usd_to_uusd(1))