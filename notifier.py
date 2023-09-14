# notifier.py
from telegram.ext import Updater, CommandHandler
from telegram import Bot

from config import TELEGRAM_BOT_API

from telegram import Update

bot = Bot(TELEGRAM_BOT_API)


# Function to send Telegram notification (stub)
async def send_message(channel, messages):
    # If messages is a single string, make it a one-item list
    if isinstance(messages, str):
        messages = [messages]

    # Initialize an empty chunk and its character count
    current_chunk = ""
    current_chunk_size = 0

    # Loop over the list of messages
    for msg in messages:
        msg_size = len(msg)

        # Check if an individual message exceeds 4096 characters
        if msg_size > 4096:
            # Here you can decide how to handle this situation.
            # For example, you could raise an exception or split the message into valid parts.
            raise ValueError("A single message exceeds the 4096 character limit.")

        # If adding this message won't exceed the 4096 character limit, append it to the current chunk
        if current_chunk_size + msg_size <= 4096:
            current_chunk += msg
            current_chunk_size += msg_size
        else:
            # Send the current chunk and reset it
            await bot.send_message(channel, current_chunk, parse_mode="HTML")
            current_chunk = msg
            current_chunk_size = msg_size

    # Send any remaining characters in the last chunk
    if current_chunk:
        await bot.send_message(channel, current_chunk, parse_mode="HTML")
