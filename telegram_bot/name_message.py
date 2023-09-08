import datetime

from telegram_menu import (
    BaseMessage,
    MenuButton,
    TelegramMenuSession,
    NavigationHandler,
    ButtonType,
)

from telegram_bot.navigation_handler import BotNavigationHandler


class NameMessage(BaseMessage):
    LABEL = "New Filter Name"

    def __init__(
        self,
        navigation: BotNavigationHandler,
    ) -> None:
        """Init ThirdMenuMessage class."""
        super().__init__(
            navigation,
            NameMessage.LABEL,
            notification=False,
            expiry_period=datetime.timedelta(seconds=30),
            input_field="Name of the filter",  # use '<disable>' to leave the input field empty
        )

    def update(self) -> str:
        """Update message content."""
        return "Enter Filter Name"

    async def text_input(self, text: str) -> None:
        self.get_button("Filter Name").label = (
            "✅ Filter Name: " + text if text else "Filter Name"
        )
        self.navigation.filter.name = text
