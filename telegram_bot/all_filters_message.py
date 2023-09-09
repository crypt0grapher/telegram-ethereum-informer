from typing import Optional, List

from telegram_menu import (
    BaseMessage,
    MenuButton,
    TelegramMenuSession,
    NavigationHandler,
    ButtonType,
)

from filter_manager import all_filters
from helpers import find_by_name
from telegram_bot.navigation_handler import BotNavigationHandler
from telegram_bot.new_filter_message import NewFilterMessage


class AllFiltersMessage(BaseMessage):
    """Options app message, show an example of a button with inline buttons."""

    LABEL = "All Filters"

    def __init__(
        self,
        navigation: BotNavigationHandler,
    ) -> None:
        super().__init__(navigation, AllFiltersMessage.LABEL, inlined=True)

    def edit(self, button: MenuButton) -> str:
        self.navigation.filter = all_filters[button.label]
        NewFilterMessage(self.navigation)
        return "Filter updated"

    async def toggle(self, button: MenuButton) -> str:
        filter = find_by_name(button.label)
        filter.is_active = not filter.is_active
        await self.navigation.edit_message(self)
        return "Filter updated"

    async def delete(self, button: MenuButton) -> str:
        self.navigation.filter = all_filters[button.label]
        all_filters.remove(self.navigation.filter)
        await self.navigation.edit_message(self)
        return "Filter deleted"

    def update(self) -> str:
        if len(all_filters) == 0:
            return "No filters added yet"

        for filter in all_filters:
            self.keyboard.append(
                [
                    MenuButton(
                        label=filter.name,
                        callback=self.edit,
                        btype=ButtonType.MESSAGE,
                    ),
                    MenuButton(
                        label="▶️" if filter.is_active else "⏸️",
                        callback=self.toggle,
                        btype=ButtonType.NOTIFICATION,
                    ),
                    MenuButton(
                        label="❌",
                        callback=self.delete,
                        btype=ButtonType.NOTIFICATION,
                    ),
                ]
            )
        return "Selet a filter"
