from typing import Optional, List

from telegram_menu import (
    BaseMessage,
    MenuButton,
    TelegramMenuSession,
    NavigationHandler,
    ButtonType,
)

from filter_manager import all_filters
from telegram_bot.navigation_handler import BotNavigationHandler


class AllFiltersMessage(BaseMessage):
    """Options app message, show an example of a button with inline buttons."""

    LABEL = "All Filters"

    def __init__(
        self,
        navigation: BotNavigationHandler,
    ) -> None:
        super().__init__(navigation, AllFiltersMessage.LABEL, inlined=True)

    def update(self) -> str:
        if len(all_filters) == 0:
            return "No filters added yet"
        for filter in all_filters:
            self.add_button(filter.name, btype=ButtonType.MESSAGE, new_row=True)
        return "Selet a filter"
