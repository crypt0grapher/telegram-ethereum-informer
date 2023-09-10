# notifier.py
from telegram.ext import Updater, CommandHandler

from config import TELEGRAM_BOT_API


# Function to send Telegram notification (stub)
def send_message(channel, message):
    updater = Updater(TELEGRAM_BOT_API)
    updater.bot.send_message(channel, message, parse_mode="HTML")
    updater.stop()
