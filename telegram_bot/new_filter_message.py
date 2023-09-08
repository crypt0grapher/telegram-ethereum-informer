import datetime
import logging
from typing import Optional, List

from telegram_menu import (
    BaseMessage,
    MenuButton,
    TelegramMenuSession,
    NavigationHandler,
    ButtonType,
)

from filter import Filter
from helpers import safe_int_parse, safe_float_parse
from telegram_bot.name_message import NameMessage
from telegram_bot.navigation_handler import BotNavigationHandler
from telegram.ext._callbackcontext import CallbackContext
from telegram.ext._utils.types import BD, BT, CD, UD


class NewFilterMessage(BaseMessage):
    """Options app message, show an example of a button with inline buttons."""

    LABEL = "New Filter"

    def __init__(
        self,
        navigation: BotNavigationHandler,
    ) -> None:
        super().__init__(
            navigation,
            NewFilterMessage.LABEL,
            inlined=True,
            notification=False,
            # expiry_period=datetime.timedelta(seconds=10),
            input_field="New Filter",
            home_after=True,
        )
        self.selected = None
        navigation.filter = Filter(navigation.chat_id)

    def new_name(self) -> str:
        self.selected = "Name"
        self.navigation.send_message(f"Enter name for filter")
        return "Enter Filter Name"

    def new_from_address(self) -> str:
        self.selected = "From"
        self.navigation.send_message(f"Enter from address for filter")
        return "Enter From Address"

    def new_to_address(self) -> str:
        self.selected = "To"
        self.navigation.send_message(f"Enter to address for filter")
        return "Enter To Address"

    def new_min_value(self) -> str:
        self.selected = "Min Value"
        self.navigation.send_message(f"Enter Min Value for filter")
        return "Enter Min Value"

    def new_max_value(self) -> str:
        self.selected = "Max Value"
        self.navigation.send_message(f"Enter Max Value for filter")
        return "Enter Max Value"

    def new_freshness(self) -> str:
        self.selected = "Freshness"
        self.navigation.send_message(f"Enter Freshness for filter")
        return "Enter Freshness"

    def confirm(self) -> str:
        ####TODO add filter to the array and update ethereum listener
        self.navigation.send_message(f"<b>Added</b><br/>")
        # self.navigation.send_message(f"<b>Added</b><br/>{self.navigation.filter}")
        return "Done"

    async def text_input(
        self, text: str, context: Optional[CallbackContext[BT, UD, CD, BD]] = None
    ) -> None:
        if self.selected is None:
            await self.navigation.send_message("Select the field to update first")
            return
        elif self.selected == "Name":
            self.navigation.filter.name = text
        elif self.selected == "From":
            self.navigation.filter.from_address = text
        elif self.selected == "To":
            self.navigation.filter.to_address = text
        elif self.selected == "Min Value":
            value = safe_float_parse(text)
            if safe_float_parse(text):
                self.navigation.filter.min_value = value
        elif self.selected == "Max Value":
            value = safe_float_parse(text)
            if safe_float_parse(text):
                self.navigation.filter.max_value = value
        elif self.selected == "Freshness":
            value = safe_int_parse(text)
            if safe_int_parse(text):
                self.navigation.filter.freshness = value

        await self.navigation.send_message(f"{self.selected} updated")
        await self.navigation.edit_message(self)

    async def app_update_display(self) -> None:
        """Update message content when callback triggered."""
        if await self.edit_message():
            self.is_alive()

    def update(self) -> str:
        self.keyboard = [
            [
                MenuButton(
                    label="✅ Filter Name: " + self.navigation.filter.name
                    if self.navigation.filter.name
                    else "Filter Name",
                    callback=self.new_name,
                    btype=ButtonType.MESSAGE,
                )
            ],
            [
                MenuButton(
                    label="✅ Filter from_address: "
                    + self.navigation.filter.from_address
                    if self.navigation.filter.from_address
                    else "Filter from_address",
                    callback=self.new_from_address,
                )
            ],
            [
                MenuButton(
                    label="✅ Filter to_address: " + self.navigation.filter.to_address
                    if self.navigation.filter.to_address
                    else "Filter to_address",
                    callback=self.new_to_address,
                )
            ],
            [
                MenuButton(
                    label="✅ Filter min_value: " + str(self.navigation.filter.min_value)
                    if self.navigation.filter.min_value
                    else "Filter min_value",
                    callback=self.new_min_value,
                )
            ],
            [
                MenuButton(
                    label="✅ Filter max_value: " + str(self.navigation.filter.max_value)
                    if self.navigation.filter.max_value
                    else "Filter max_value",
                    callback=self.new_max_value,
                )
            ],
            [
                MenuButton(
                    label="✅ Filter freshness: " + str(self.navigation.filter.freshness)
                    if self.navigation.filter.freshness
                    else "Filter freshness",
                    callback=self.new_freshness,
                )
            ],
            [
                MenuButton(
                    label="🆗Start Filter",
                    callback=self.confirm,
                ),
            ],
        ]
        return (
            "Select the field of the filter to edit\nthen confirm to start the filter"
        )
