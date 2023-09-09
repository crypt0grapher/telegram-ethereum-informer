import asyncio
from websockets import connect
from web3 import Web3
import json
import requests

from config import ETHERUM_NODE_WS_URI
from your_filter_module import (
    Filter,
    Generator,
    all_filters,
)  # import your actual Filter class and global filter list

# Cache for the most recent blocks
block_cache = []
BLOCK_CACHE_SIZE = 3


# Mock-up function to send a message via Telegram
def send_telegram_message(channel, message):
    # Implement your actual Telegram sending logic here
    pass


# Function to process a block
def process_block(block):
    global block_cache

    # Add the new block to the cache
    block_cache.append(block)

    # Trim the block cache to the last BLOCK_CACHE_SIZE elements
    block_cache = block_cache[-BLOCK_CACHE_SIZE:]

    # Apply each filter to the new block
    for f in all_filters:
        # Filter transactions
        for tx in block["transactions"]:
            from_address = tx["from"]
            to_address = tx["to"]
            value = tx["value"]

            if (
                f.from_address == from_address or f.to_address == to_address
            ) and f.min_value <= Web3.fromWei(value, "ether") <= f.max_value:
                # Transaction matches filter
                send_telegram_message(
                    f.channel, f"Transaction detected that matches filter {f.name}"
                )

                # Check if this filter is a generator
                if f.generator:
                    # Generate a new filter based on this one
                    new_filter = Filter(
                        chat_id=f.chat_id,
                        name=f"{f.name}_gen",
                        from_address=from_address,
                        to_address=to_address,
                        min_value=f.min_value,
                        max_value=f.max_value,
                        freshness=f.freshness,
                        operation=f.operation,
                        channel=f.generator_options.channel,
                    )
                    all_filters.append(new_filter)


# Function to update listener based on changes in the filters array
def update_filters():
    global all_filters
    pass


async def listen_to_new_blocks(ws_uri, rpc_id=1):
    async with connect(ws_uri) as ws:
        # Subscribe to new blocks
        payload = json.dumps(
            {"id": rpc_id, "method": "eth_subscribe", "params": ["newHeads"]}
        )
        await ws.send(payload)

        # Listen for new blocks
        while True:
            response = await ws.recv()
            block_data = json.loads(response).get("params", {}).get("result", {})
            if block_data:
                block_number_hex = block_data.get("number")
                block_number = int(block_number_hex, 16)

                w3 = Web3(Web3.HTTPProvider(ws_uri))  # Replace with your HTTPProvider
                block = w3.eth.get_block(block_number, True)
                process_block(block)


def start_listener():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(listen_to_new_blocks(ETHERUM_NODE_WS_URI))


if __name__ == "__main__":
    start_listener()
