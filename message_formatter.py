import datetime
import logging
import time

from filter import Operation, Filter
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
        address = f.match_buy_token(tx)
        current_message += (
            f'token: <a href="https://etherscan.io/address/{address}">{address}</a>\n'
        )
    logging.debug("Message: " + current_message)
    return current_message + "\n"
