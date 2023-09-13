import datetime
import time

from filter import Operation
from helpers import safe_bignumber_to_float


def format_message(tx, f):
    if not tx or not f:
        return ""
    filter_name = f.name
    amount = safe_bignumber_to_float(tx["value"]) if "value" in tx else 0.0
    hash = tx["hash"].hex()
    hash_with_link = f'<a href="https://etherscan.io/tx/{hash}">{hash}</a>'
    current_message = (
        filter_name
        + "\n"
        + "block: "
        + str(tx["blockNumber"])
        + "\n"
        + f.operation.value
        + "\n"
        + "tx hash: "
        + hash_with_link
        + "\n"
        + "from: "
        + tx["from"]
        + "\n"
        + "to: "
        + tx["to"]
        + "\n"
        + "value: "
        + str(amount)
        + " ETH\n"
    )
    if f.operation == Operation.BuyToken:
        token = tx["input"].hex()[10:74]
        current_message += "token: " + token + "\n"
    return current_message
