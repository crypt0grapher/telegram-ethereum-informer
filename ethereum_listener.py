import asyncio
import json
import logging

from websockets import connect

from filter import Filter, Operation
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
    logging.info(
        "Processing block "
        + str(block["number"])
        + ", filters num: "
        + str(len(all_filters))
    )
    logging.debug("Filters: " + str(all_filters))
    if "transactions" in block:
        if isinstance(block["transactions"], list):
            current_blocks_messages = {}
            for txhash in block["transactions"]:
                tx = await w3.eth.get_transaction(txhash)
                if isinstance(get_all_filters(), dict):
                    all_filters_frozen_for_the_loop = get_all_filters()
                    for channel_id, filters in all_filters_frozen_for_the_loop.items():
                        for f in filters:
                            if f.is_active:
                                if f.match_transaction(tx):
                                    if (
                                        f.freshness
                                        and f.from_address
                                        and f.operation == Operation.ETHTransfer
                                    ):
                                        logging.debug(
                                            f"Filter {f.name}, tx matched, checking nonce"
                                        )
                                        nonce = await w3.eth.get_transaction_count(
                                            tx["to"]
                                        )
                                        nonce = (
                                            nonce
                                            if isinstance(nonce, int)
                                            else nonce.get("nonce", 0)
                                        )
                                        if nonce > f.freshness:
                                            continue
                                    # web3.eth.get_transaction_count
                                    # Send a Telegram notification to the channel_id
                                    logging.debug("Nonce ok, sending message")
                                    if f.channel not in current_blocks_messages:
                                        current_blocks_messages[f.channel] = []
                                    current_blocks_messages[f.channel].append(
                                        format_message(tx, f)
                                    )
                                    # Generate new filter if needed
                                    if f.generator:
                                        logging.debug(
                                            "The filter is generator, generating new filter"
                                        )
                                        new_filter = f.generate_subfilter(tx["to"])
                                        if any(
                                            new_filter == f
                                            for f in all_filters_frozen_for_the_loop[
                                                channel_id
                                            ]
                                        ):
                                            logging.info(
                                                "Filter already exists, not adding"
                                            )
                                        else:
                                            add_new_filter(new_filter, channel_id)
                                            current_blocks_messages[f.channel].append(
                                                "New filter generated: '"
                                                + str(new_filter.name)
                                                + "'\nFrom: "
                                                + (tx["to"])
                                            )

            logging.debug("Block processed, sending messages found")
            for (
                destination_channel_id,
                current_channel_messages,
            ) in current_blocks_messages.items():
                if current_channel_messages:
                    try:
                        await send_message(
                            destination_channel_id, current_channel_messages
                        )
                    except Exception as e:
                        await send_message(
                            channel_id,
                            "Error sending message: "
                            + str(e)
                            + "message was: "
                            + str(current_channel_messages),
                        )
                        logging.error("Error sending message: " + str(e))


async def listen_to_new_blocks(ws_uri, rpc_id=1):
    async with AsyncWeb3.persistent_websocket(WebsocketProviderV2(ws_uri)) as w3:
        subscription_id = await w3.eth.subscribe("newHeads")
        while True:
            async for response in w3.listen_to_websocket():
                logging.debug(f"Type of response: {type(response)}, value: {response}")
                if "number" in response:
                    block_number = response["number"]
                    block = await w3.eth.get_block(block_number)
                    await process_block(w3, block)


def start_listener():
    while True:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(
                listen_to_new_blocks(ETHERUM_NODE_WS_URI or "ws://127.0.0.1:8546")
            )
        except Exception as e:
            logging.error("Error in start_listener: " + str(e))
            loop.close()
            continue
