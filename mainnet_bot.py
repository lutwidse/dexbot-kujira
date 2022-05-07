import os
import logging
from schedule import run_pending, every, repeat
import time
from orca_dexbot import OrcaDexbot

logger = logging.getLogger(__name__)
logger.setLevel(level=logging.INFO)
handler = logging.FileHandler("bot.log")
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)

dexbot = OrcaDexbot("mainnet", os.environ["MAINNET_MNEMONIC"])
wallet_address = dexbot.get_wallet_address()
BLUNA_CONTRACT = dexbot.get_bluna_contract()
AUST_CONTRACT = dexbot.get_aust_contract()


def get_bids():
    try:
        return dexbot.bids_by_user(dexbot.get_bluna_contract(), wallet_address, 0, 30)
    except:
        logger.info("[Bot] Error [get_bids]", exc_info=True, stack_info=True)


def get_claimable_bids(bids):
    try:
        claimable_bids = []
        for bid in bids["bids"]:
            if bid["proxied_bid"] is None:
                continue

            idx = bid["idx"]
            pending_liquidated_collateral = bid["proxied_bid"][
                "pending_liquidated_collateral"
            ]
            if int(pending_liquidated_collateral) > 0:
                claimable_bids.append(idx)
                return claimable_bids
    except:
        logger.info("[Bot] Error [get_claimable_bids]", exc_info=True, stack_info=True)


@repeat(
    every(1).minute,
    amount_threshold=5,
    premium=3,
    borrow_limit_threshold=99,
    at_risk_collateral_threshold=1,
)
def bot(
    auto_kujira=True,
    auto_claim=True,
    amount_threshold=int,
    premium=int,
    borrow_limit_threshold=int,
    at_risk_collateral_threshold=int,
):
    try:
        if auto_kujira:
            native_token = dexbot.get_native_token(wallet_address)
            ust_balance = int(native_token[0].get("uusd").amount)

            amount_threshold = dexbot.denom_conversion(amount_threshold)
            if ust_balance > amount_threshold * 1.2:
                deposit_ust = str(ust_balance - amount_threshold)
                logger.info("[Bot] Deposit {deposit_ust} UST to Anchor")
                dexbot.deposit_stable(deposit_ust)
                logger.info("[Bot] Deposited")

                aust_balance = dexbot.get_cw_token(AUST_CONTRACT).get("balance")
                logger.info("[Bot] aUST : {aust_balance}")
                dexbot.submit_bid(
                    amount=aust_balance,
                    collateral_token=dexbot.get_bluna_contract(),
                    premium_slot=premium,
                    ltv=borrow_limit_threshold,
                    cumulative_value=dexbot.denom_conversion(
                        at_risk_collateral_threshold * 1000000, is_str=True
                    ),
                )

        if auto_claim:
            bids = get_bids()
            claimable_bids = get_claimable_bids(bids)
            if len(claimable_bids) > 0:
                logger.info(f"[Bot] Found claimable bids")
                dexbot.claim_liquidations(claimable_bids)
                logger.info(f"[Bot] Claimed")

                bluna_balance = dexbot.get_cw_token(BLUNA_CONTRACT).get("balance")
                bluna_balance = str(bluna_balance)
                logger.info(f"[Bot] bLUNA : {bluna_balance}")

                logger.info(f"[Bot] Swap {bluna_balance} bLUNA to LUNA")
                dexbot.swap_bluna_to_luna(bluna_balance)
                logger.info(f"[Bot] Swapped")

                native_token = dexbot.get_native_token(wallet_address)
                luna_balance = str(native_token[0].get("uluna").amount)
                logger.info(f"[Bot] Swap {luna_balance} LUNA to UST")
                dexbot.swap_luna_to_ust(luna_balance)
                logger.info(f"[Bot] Swapped")
    except:
        logger.info("[Bot] Error", exc_info=True, stack_info=True)

if __name__ == "__main__":
    logger.info("[Bot] Start")
    while True:
        run_pending()
        time.sleep(1)
