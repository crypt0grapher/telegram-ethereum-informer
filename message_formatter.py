import datetime
import time

from helpers import safe_bignumber_to_float


def format_message(tx, f):
    filter_name = f.name
    amount = safe_bignumber_to_float(tx["value"])
    dt_object = datetime.datetime.fromtimestamp(
        int(tx["timeStamp"]) if tx["timeStamp"] else time.time()
    )
    print(dt_object.strftime("%Y-%m-%d %H:%M:%S"))

    hash = tx["hash"].hex()
    hash_with_link = f'<a href="https://etherscan.io/tx/{hash}">{hash}</a>'
    current_message = (
        filter.name
        + "\n"
        + "block: "
        + tx["blockNumber"]
        + "\n"
        + "timestamp: "
        + tx["timeStamp"]
        + " ("
        + dt_object.strftime("%Y-%m-%d %H:%M:%S")
        + ")"
        + "\n"
        + "gas price: "
        + tx["gasPrice"]
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
        + "tx count: "
        + "\n\n"
    )
    return current_message
