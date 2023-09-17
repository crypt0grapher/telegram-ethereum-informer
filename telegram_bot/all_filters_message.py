from typing import Optional, List

from telegram_menu import (
    BaseMessage,
    MenuButton,
    TelegramMenuSession,
    NavigationHandler,
    ButtonType,
)

from telegram.ext._callbackcontext import CallbackContext
from telegram.ext._utils.types import BD, BT, CD, UD

from filter import Filter
from all_filters import (
    all_filters,
    remove_filter,
    get_filters_by_chat_id,
    get_filter_by_name,
)
from helpers import find_by_name
from notifier import send_message
from telegram_bot.navigation_handler import BotNavigationHandler
from telegram_bot.new_filter_message import NewFilterMessage


class AllFiltersMessage(BaseMessage):
    """Options app message, show an example of a button with inline buttons."""

    LABEL = "Filters"
    page_starts_with = 0
    page_size = 19

    def __init__(
        self,
        navigation: BotNavigationHandler,
    ) -> None:
        super().__init__(navigation, AllFiltersMessage.LABEL, inlined=True)

    async def edit(self, args) -> str:
        self.navigation.filter = args[0].copy()
        remove_filter(args[0].name, self.navigation.chat_id)
        await self.navigation.select_menu_button("New")
        return "Press 'Confirm and Start Filter' to add the filter back to the list once you are done editing it"

    async def view(self, args) -> str:
        filter = get_filter_by_name(self.navigation.chat_id, args[0].name)
        filter_details = str(filter)
        # await send_message(self.navigation.chat_id, filter_details)
        return filter_details

    async def toggle(
        self,
        args,
    ) -> str:
        filter_selected = args[0]
        filter_selected.is_active = not filter_selected.is_active
        await self.navigation.edit_message(self)
        return "Filter updated"

    async def delete(self, args) -> str:
        remove_filter(args[0].name, self.navigation.chat_id)
        await self.navigation.edit_message(self)
        return self.update()

    def update(self) -> str:
        filters = get_filters_by_chat_id(self.navigation.chat_id)
        self.keyboard = []
        if len(filters) == 0:
            return "No filters added yet"
        i = 1

        current_page_filters = filters[
            self.page_starts_with : self.page_starts_with + self.page_size
        ]

        for filter in current_page_filters:
            self.keyboard.append(
                [
                    MenuButton(
                        label=filter.name + " ✏️",
                        callback=self.edit,
                        btype=ButtonType.MESSAGE,
                        args=[filter],
                    ),
                    MenuButton(
                        label=f"{i:02d} 👀",
                        callback=self.view,
                        btype=ButtonType.MESSAGE,
                        args=[filter],
                    ),
                    MenuButton(
                        label=f"{i:02d} 🔴  ▶️"
                        if not filter.is_active
                        else f"{i:02d} 🟢  ⏸️",
                        callback=self.toggle,
                        btype=ButtonType.NOTIFICATION,
                        args=[filter],
                    ),
                    MenuButton(
                        label=f"{i:02d} ❌",
                        callback=self.delete,
                        btype=ButtonType.NOTIFICATION,
                        args=[filter],
                    ),
                ]
            )
            i += 1

        if (
            len(current_page_filters) == self.page_size
            and len(filters) > self.page_size
        ):
            self.page_starts_with += self.page_size
        else:
            self.page_starts_with = 0
        return f"Filters: {self.page_starts_with+1} - {self.page_starts_with + len(current_page_filters) } of {len(filters)}"
