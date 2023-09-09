from telegram_menu import (
    BaseMessage,
    MenuButton,
    TelegramMenuSession,
    NavigationHandler,
    ButtonType,
)

from filter import Filter
from telegram import Bot, Chat
from apscheduler.schedulers.base import BaseScheduler


class BotNavigationHandler(NavigationHandler):
    """Example of navigation handler, extended with a custom "Back" command."""

    def __init__(self, bot: Bot, chat: Chat, scheduler: BaseScheduler):
        super().__init__(bot, chat, scheduler)
        self.filter = Filter(self.chat_id)

    async def goto_back(self) -> int:
        self.filter: Filter = Filter(super().chat_id)
        """Do Go Back logic."""
        return await self.select_menu_button("Back")
