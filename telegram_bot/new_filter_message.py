import asyncio
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

import filter
from filter import Filter
from all_filters import add_new_filter, is_unique_name
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
    "CHANNEL": "CHANNEL",
    "GENERATOR_CHANNEL": "GENERATOR_CHANNEL",
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

    def new_channel(self) -> str:
        self.selected = FIELDS["CHANNEL"]
        self.navigation.send_message(f"Enter channel to notify in")
        return "Enter Channel"

    def new_generator_channel(self) -> str:
        self.selected = FIELDS["GENERATOR_CHANNEL"]
        self.navigation.send_message(
            f"Enter channel for generated filters to notify in"
        )
        return "Enter Channel"

    def toggle_generator(self) -> str:
        self.navigation.filter.generator = not self.navigation.filter.generator
        return self.update()

    def set_generator_buytoken_operation(self) -> str:
        self.navigation.filter.generator_options.operation = filter.Operation.BuyToken
        return "Updated"

    def set_generator_ethtransfer_operation(self) -> str:
        self.navigation.filter.generator_options.operation = (
            filter.Operation.ETHTransfer
        )
        return "Updated"

    def set_generator_deployment_operation(self) -> str:
        self.navigation.filter.generator_options.operation = filter.Operation.Deployment
        return "Updated"

    def set_buytoken_operation(self) -> str:
        self.navigation.filter.operation = filter.Operation.BuyToken
        return "Updated"

    def set_ethtransfer_operation(self) -> str:
        self.navigation.filter.operation = filter.Operation.ETHTransfer
        return "Updated"

    def set_deployment_operation(self) -> str:
        self.navigation.filter.operation = filter.Operation.Deployment
        return "Updated"

    async def confirm(self) -> str:
        if self.navigation.filter.is_correct():
            if not is_unique_name(self.navigation.filter.name, self.navigation.chat_id):
                await self.navigation.send_message("Filter already exists")
                return "Filter already exists"
            add_new_filter(self.navigation.filter, self.navigation.chat_id)
            # del self.navigation.filter
            self.navigation.filter = Filter(self.navigation.chat_id)
            await self.navigation.send_message(f"Filter started")
            return "Filter started"
        else:
            await self.navigation.send_message("Filter details are not complete")
            return "Fill in the details first"

    async def text_input(
        self, text: str, context: Optional[CallbackContext[BT, UD, CD, BD]] = None
    ) -> None:
        selected = self.selected
        self.selected = None
        if selected is None:
            await self.navigation.send_message("Select the field to update first")
            return
        elif selected == FIELDS["NAME"]:
            if not is_unique_name(selected, self.navigation.chat_id):
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
            if value and value > 0:
                if value > self.navigation.filter.max_value:
                    await self.navigation.send_message(
                        "Minimum filter value should be less or equal than maximum value"
                    )
                    return
                else:
                    self.navigation.filter.min_value = value
            else:
                await self.navigation.send_message("Invalid number")
                return
        elif selected == FIELDS["MAX"]:
            value = safe_float_parse(text)
            if value and value > 0:
                if value < self.navigation.filter.min_value:
                    await self.navigation.send_message(
                        "Maximum filter value should be greater or equal than than minimum value"
                    )
                    return
                else:
                    self.navigation.filter.max_value = value

            else:
                await self.navigation.send_message("Invalid number")
                return
        elif selected == FIELDS["FRESH"]:
            value = safe_int_parse(text)
            if value and value > 0:
                self.navigation.filter.freshness = value
            else:
                await self.navigation.send_message("Invalid number")
                return
        elif selected == FIELDS["CHANNEL"]:
            if await self.navigation.has_access_to_channel(text):
                self.navigation.filter.channel = text
            else:
                await self.navigation.send_message(
                    "Invalid channel or the bot has no access to it. Add the bot to the chat and try again."
                )
                return
        elif selected == FIELDS["GENERATOR_CHANNEL"]:
            if await self.navigation.has_access_to_channel(text):
                self.navigation.filter.generator_channel = text
            else:
                await self.navigation.send_message(
                    "Invalid channel or the bot has no access to it"
                )
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
                    else "Name",
                    callback=self.new_name,
                    btype=ButtonType.MESSAGE,
                )
            ],
            [
                MenuButton(
                    label="✅ Tx From: " + self.navigation.filter.from_address
                    if self.navigation.filter.from_address
                    else "From",
                    callback=self.new_from_address,
                )
            ],
            [
                MenuButton(
                    label="✅ Tx To: " + self.navigation.filter.to_address
                    if self.navigation.filter.to_address
                    else "To",
                    callback=self.new_to_address,
                )
            ],
            [
                MenuButton(
                    label=f"✅{filter.Operation.Deployment.value}"
                    if filter.Operation.Deployment == self.navigation.filter.operation
                    else filter.Operation.Deployment.value,
                    callback=self.set_deployment_operation,
                ),
                MenuButton(
                    label=f"✅{filter.Operation.BuyToken.value}"
                    if filter.Operation.BuyToken == self.navigation.filter.operation
                    else filter.Operation.BuyToken.value,
                    callback=self.set_buytoken_operation,
                ),
                MenuButton(
                    label=f"✅{filter.Operation.ETHTransfer.value}"
                    if filter.Operation.ETHTransfer == self.navigation.filter.operation
                    else filter.Operation.ETHTransfer.value,
                    callback=self.set_ethtransfer_operation,
                ),
            ],
            [
                MenuButton(
                    label="Min Eth: "
                    + str(self.navigation.filter.min_value).replace(".", "•"),
                    callback=self.new_min_value,
                ),
                MenuButton(
                    label="Max Eth: "
                    + str(self.navigation.filter.max_value).replace(".", "•"),
                    callback=self.new_max_value,
                ),
                MenuButton(
                    label=f"Fresh: {self.navigation.filter.freshness}",
                    callback=self.new_freshness,
                ),
            ],
            [
                MenuButton(
                    label=f"Notification channel Id: {self.navigation.filter.channel}",
                    callback=self.new_channel,
                )
            ],
            [
                MenuButton(
                    label="Generate wallet filters: :white_check_mark: Yes"
                    if self.navigation.filter.generator
                    else "Generate wallet filters: :x: No",
                    callback=self.toggle_generator,
                )
            ],
        ]

        if self.navigation.filter.is_correct():
            self.keyboard.append(
                [
                    MenuButton(
                        label="👍 Confirm and Start Filter",
                        callback=self.confirm,
                    )
                ]
            )

        if self.navigation.filter.generator:
            self.keyboard.extend(
                [
                    [
                        MenuButton(
                            label="Wallet filter Channel Id: "
                            + str(self.navigation.filter.generator_channel),
                            callback=self.new_generator_channel,
                        )
                    ],
                    [
                        MenuButton(
                            label=f"✅Generate {filter.Operation.Deployment.value}"
                            if filter.Operation.Deployment
                            == self.navigation.filter.generator_options.operation
                            else f"Generate {filter.Operation.Deployment.value}",
                            callback=self.set_generator_deployment_operation,
                        ),
                        MenuButton(
                            label=f"✅Generate {filter.Operation.BuyToken.value}"
                            if filter.Operation.BuyToken
                            == self.navigation.filter.generator_options.operation
                            else f"Generate {filter.Operation.BuyToken.value}",
                            callback=self.set_generator_buytoken_operation,
                        ),
                        MenuButton(
                            label=f"✅Generate {filter.Operation.ETHTransfer.value}"
                            if filter.Operation.ETHTransfer
                            == self.navigation.filter.generator_options.operation
                            else f"Generate {filter.Operation.ETHTransfer.value}",
                            callback=self.set_generator_ethtransfer_operation,
                        ),
                    ],
                ]
            )

        return "Select the field of the filter to edit with buttons, then confirm to start the filter"
