import asyncio
import json
import logging

from websockets import connect

from filter import Filter
from config import ETHERUM_NODE_WS_URI
from all_filters import all_filters, add_new_filter
import asyncio
import json
from websockets import connect
from web3 import Web3

from message_formatter import format_message
from notifier import send_message


# Function to process a block and filter transactions
def process_block(block):
    for tx in block["transactions"]:
        for channel_id, filters in all_filters.items():
            for f in filters:
                if f.is_active:  # Only process active filters
                    # Check if this transaction matches the filter
                    if f.match_transaction(tx):
                        # Send a Telegram notification to the channel_id
                        send_message(f.channel, format_message(tx, f))
                        # Generate new filter if needed
                        if f.generator:
                            new_filter = f.generate_new_filter(tx)
                            add_new_filter(new_filter, channel_id)


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
                logging.debug(f"New block: {block_number}")
                w3 = Web3(Web3.WebsocketProvider(ws_uri))
                block = w3.eth.getBlock(block_number, True)
                process_block(block)


def start_listener():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(listen_to_new_blocks(ETHERUM_NODE_WS_URI))
