import asyncio
from websockets import connect
from web3 import Web3
import json

from config import ETHERUM_NODE_WS_URI


# Mock-up of a Filter class and global filter list
class Filter:
    def __init__(self, name, from_address, to_address):
        self.name = name
        self.from_address = from_address
        self.to_address = to_address


filter_list = []  # This would be your global filter list

# Cache for the most recent blocks
block_cache = []
BLOCK_CACHE_SIZE = 3


# Function to process a block
def process_block(block):
    global block_cache

    # Add the new block to the cache
    block_cache.append(block)

    # Trim the block cache to the last BLOCK_CACHE_SIZE elements
    block_cache = block_cache[-BLOCK_CACHE_SIZE:]

    # Apply each filter to the new block
    for f in filter_list:
        # Implement your logic to filter transactions based on Filter objects
        pass


# Function to update listener based on changes in the filters array
def update_filters(new_filters):
    global filter_list
    filter_list = new_filters


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
                print(f"New block: {block_number}")

                w3 = Web3(Web3.HTTPProvider(ws_uri))  # Replace with your HTTPProvider
                block = w3.eth.get_block(block_number, True)
                process_block(block)


def start_listener():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(listen_to_new_blocks(ETHERUM_NODE_WS_URI))
