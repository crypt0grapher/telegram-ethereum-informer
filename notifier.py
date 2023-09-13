# notifier.py
from telegram.ext import Updater, CommandHandler
from telegram import Bot

from config import TELEGRAM_BOT_API

from telegram import Update

bot = Bot(TELEGRAM_BOT_API)


# Function to send Telegram notification (stub)
async def send_message(channel, message):
    if len(message) > 4096:
        for i in range(0, len(message), 4096):
            await bot.send_message(channel, message[i : i + 4096], parse_mode="HTML")
    else:
        await bot.send_message(channel, message, parse_mode="HTML")
