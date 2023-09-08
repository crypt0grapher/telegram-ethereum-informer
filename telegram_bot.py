import asyncio

from telegram.ext import Updater, CommandHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram_menu import BaseMessage, TelegramMenuSession, NavigationHandler

from config import TELEGRAM_BOT_API
import logging


class MyNavigationHandler(NavigationHandler):
    """Example of navigation handler, extended with a custom "Back" command."""

    async def goto_back(self) -> int:
        """Do Go Back logic."""
        return await self.select_menu_button("Back")


class SecondMenuMessage(BaseMessage):
    """Second menu, create an inlined button."""

    LABEL = "action"

    def __init__(self, navigation: NavigationHandler) -> None:
        """Init SecondMenuMessage class."""
        super().__init__(navigation, StartMessage.LABEL, inlined=True)

        # 'run_and_notify' function executes an action and return a string as Telegram notification.
        self.add_button(label="Action", callback=self.run_and_notify)

    def update(self) -> str:
        """Update message content."""
        # emoji can be inserted with a keyword enclosed with ::
        # list of emojis can be found at this link: https://www.webfx.com/tools/emoji-cheat-sheet/
        return ":warnings: Second message"

    @staticmethod
    def run_and_notify() -> str:
        """Update message content."""
        return "This is a notification"


class StartMessage(BaseMessage):
    LABEL = "start"

    def __init__(self, navigation: NavigationHandler) -> None:
        """Init StartMessage class."""
        super().__init__(navigation, StartMessage.LABEL)
        second_menu = SecondMenuMessage(navigation)
        self.add_button(label="Second menu", callback=second_menu)

    def update(self) -> str:
        """Update message content."""
        return "Hello, world!"


def start_bot():
    TelegramMenuSession(TELEGRAM_BOT_API).start(
        start_message_class=StartMessage,
        navigation_handler_class=MyNavigationHandler,
    )
