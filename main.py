# main.py

import threading
from telegram_bot import start_bot
from ethereum_listener import start_listener
import logging

if __name__ == "__main__":
    logging.basicConfig(level=logging.NOTSET)
    logging.info("Starting bot...")

    # Create threads
    ethereum_thread = threading.Thread(target=start_listener)

    # Start threads
    ethereum_thread.start()
    start_bot()
    ethereum_thread.join()
