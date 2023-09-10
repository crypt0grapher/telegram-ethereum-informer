# main.py

import threading

from all_filters import load_filters_from_file
from telegram_bot import start_bot
from ethereum_listener import start_listener
import logging

if __name__ == "__main__":
    logging.basicConfig(level=logging.NOTSET)
    logging.info("Starting bot...")

    # Create threads
    ethereum_thread = threading.Thread(target=start_listener)

    # Start threads
    load_filters_from_file()
    ethereum_thread.start()
    start_bot()

    ethereum_thread.join()
