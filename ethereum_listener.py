import asyncio
import json
from websockets import connect

from filter import Filter
from config import ETHERUM_NODE_WS_URI
from all_filters import all_filters


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

                w3 = Web3(Web3.HTTPProvider(ws_uri.replace("wss", "https")))
                block = w3.eth.get_block(block_number, True)
                process_block(block)


def start_listener():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(listen_to_new_blocks(ETHERUM_NODE_WS_URI))


# Starts the listener
if __name__ == "__main__":
    start_listener()
