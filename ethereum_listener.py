import asyncio
import json
import logging

from websockets import connect

from filter import Filter
from config import ETHERUM_NODE_WS_URI
from all_filters import all_filters, add_new_filter, get_all_filters
import asyncio
import json
from websockets import connect
from web3 import AsyncWeb3
from web3.providers import WebsocketProviderV2

from message_formatter import format_message
from notifier import send_message


# Function to process a block and filter transactions
async def process_block(w3, block):
    logging.info("Processing block " + str(block["number"]))
    logging.debug("Filters: " + str(all_filters))

    for txhash in block["transactions"]:
        tx = await w3.eth.get_transaction(txhash)
        for channel_id, filters in get_all_filters().items():
            for f in filters:
                if f.is_active:
                    if f.match_transaction(tx):
                        # Send a Telegram notification to the channel_id
                        await send_message(f.channel, format_message(tx, f))
                        # Generate new filter if needed
                        if f.generator:
                            new_filter = f.generate_subfilter(tx["from"])
                            add_new_filter(new_filter, channel_id)


async def listen_to_new_blocks(ws_uri, rpc_id=1):
    async with AsyncWeb3.persistent_websocket(WebsocketProviderV2(ws_uri)) as w3:
        subscription_id = await w3.eth.subscribe("newHeads")
        while True:
            async for response in w3.listen_to_websocket():
                block_number = response["number"]
                if block_number % 100 == 0:
                    logging.info("Current block: " + str(block_number))
                    block = await w3.eth.get_block(response["number"])
                    await process_block(w3, block)


def start_listener():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(listen_to_new_blocks(ETHERUM_NODE_WS_URI))
