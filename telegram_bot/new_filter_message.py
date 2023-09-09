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
from filter_manager import all_filters
from helpers import safe_int_parse, safe_float_parse
from telegram_bot.name_message import NameMessage
from telegram_bot.navigation_handler import BotNavigationHandler
from telegram.ext._callbackcontext import CallbackContext
from telegram.ext._utils.types import BD, BT, CD, UD
from enum import Enum
from web3 import Web3


FIELDS = {
    "NAME": "NAME",
    "FROM": "FROM",
    "TO": "TO",
    "MIN": "MIN",
    "MAX": "MAX",
    "FRESH": "FRESH",
}


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
        self.selected = FIELDS["NAME"]
        self.navigation.send_message(f"Enter name for the filter")
        return "Enter Filter Name"

    def new_from_address(self) -> str:
        self.selected = FIELDS["FROM"]
        self.navigation.send_message(f"Enter from address for the filter")
        return "Enter From Address"

    def new_to_address(self) -> str:
        self.selected = FIELDS["TO"]
        self.navigation.send_message(f"Enter to address for the filter")
        return "Enter To Address"

    def new_min_value(self) -> str:
        self.selected = FIELDS["MIN"]
        self.navigation.send_message(f"Enter Min Value for the filter")
        return "Enter Min Value"

    def new_max_value(self) -> str:
        self.selected = FIELDS["MAX"]
        self.navigation.send_message(f"Enter Max Value for the filter")
        return "Enter Max Value"

    def new_freshness(self) -> str:
        self.selected = FIELDS["FRESH"]
        self.navigation.send_message(f"Enter Freshness for the filter")
        return "Enter Freshness"

    def confirm(self) -> str:
        ####TODO add filter to the array and update ethereum listener
        self.navigation.send_message(f"<b>Added</b><br/>")
        # self.navigation.send_message(f"<b>Added</b><br/>{self.navigation.filter}")
        return "Done"

    async def text_input(
        self, text: str, context: Optional[CallbackContext[BT, UD, CD, BD]] = None
    ) -> None:
        selected = self.selected
        self.selected = None
        if selected is None:
            await self.navigation.send_message("Select the field to update first")
            return
        elif selected == FIELDS["NAME"]:
            if len(all_filters) > 0 and any(
                filter.name.upper() == text.upper() for filter in all_filters
            ):
                await self.navigation.send_message("Name already exists")
                return
            self.navigation.filter.name = text
        elif selected == FIELDS["FROM"]:
            if Web3.is_address(text):
                self.navigation.filter.from_address = text
                self.navigation.filter.to_address = None
            else:
                await self.navigation.send_message("Invalid address")
                return
        elif selected == FIELDS["TO"]:
            if Web3.is_address(text):
                self.navigation.filter.from_address = None
                self.navigation.filter.to_address = text
            else:
                await self.navigation.send_message("Invalid address")
                return
        elif selected == FIELDS["MIN"]:
            value = safe_float_parse(text)
            if value:
                self.navigation.filter.min_value = value
            else:
                await self.navigation.send_message("Invalid number")
                return
        elif selected == FIELDS["MAX"]:
            value = safe_float_parse(text)
            if value:
                self.navigation.filter.max_value = value
            else:
                await self.navigation.send_message("Invalid number")
                return
        elif selected == FIELDS["FRESH"]:
            value = safe_int_parse(text)
            if value:
                self.navigation.filter.freshness = value
            else:
                await self.navigation.send_message("Invalid number")
                return
        await self.navigation.send_message(f"{selected} updated")
        await self.navigation.edit_message(self)

    async def app_update_display(self) -> None:
        """Update message content when callback triggered."""
        if await self.edit_message():
            self.is_alive()

    def update(self) -> str:
        self.keyboard = [
            [
                MenuButton(
                    label="✅ Name: " + self.navigation.filter.name
                    if self.navigation.filter.name
                    else "Filter Name",
                    callback=self.new_name,
                    btype=ButtonType.MESSAGE,
                )
            ],
            [
                MenuButton(
                    label="✅ Tx From: " + self.navigation.filter.from_address
                    if self.navigation.filter.from_address
                    else "Filter from_address",
                    callback=self.new_from_address,
                )
            ],
            [
                MenuButton(
                    label="✅ Tx To: " + self.navigation.filter.to_address
                    if self.navigation.filter.to_address
                    else "Filter to_address",
                    callback=self.new_to_address,
                )
            ],
            [
                MenuButton(
                    label=f"Min Eth: {str(self.navigation.filter.min_value)}",
                    callback=self.new_min_value,
                ),
                MenuButton(
                    label=f"Max Eth: {str(self.navigation.filter.max_value)}",
                    callback=self.new_max_value,
                ),
                MenuButton(
                    label=f"Fresh: {str(self.navigation.filter.freshness)}",
                    callback=self.new_freshness,
                ),
            ],
            [
                MenuButton(
                    label="🆗 Confirm and Start Filter",
                    callback=self.confirm,
                ),
            ],
        ]
        return "Select the field of the filter to edit with buttons, then confirm to start the filter"
