import asyncio
import datetime
from pathlib import Path
from typing import List, Union, TypedDict, Coroutine, Callable, Any, Optional
from telegram.ext import Updater, CommandHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram_menu import (
    BaseMessage,
    MenuButton,
    TelegramMenuSession,
    NavigationHandler,
    ButtonType,
)

from config import TELEGRAM_BOT_API, g_bot_is_running
import logging

__raw_url__ = "https://raw.githubusercontent.com/mevellea/telegram_menu/master"

from telegram_bot.all_filters_message import AllFiltersMessage
from telegram_bot.navigation_handler import BotNavigationHandler
from telegram_bot.new_filter_message import NewFilterMessage

KeyboardContent = List[Union[str, List[str]]]
UpdateCallback = Union[Callable[[Any], None], Coroutine[Any, Any, None]]
KeyboardTester = TypedDict("KeyboardTester", {"buttons": int, "output": List[int]})

UnitTestDict = TypedDict(
    "UnitTestDict", {"description": str, "input": str, "output": str}
)
TypePackageLogger = TypedDict("TypePackageLogger", {"package": str, "level": int})

ROOT_FOLDER = Path(__file__).parent.parent


class ActionAppMessage(BaseMessage):
    """Single action message."""

    LABEL = "action"

    def __init__(self, navigation: BotNavigationHandler) -> None:
        """Init ActionAppMessage class."""
        super().__init__(
            navigation,
            ActionAppMessage.LABEL,
            expiry_period=datetime.timedelta(seconds=1),
            inlined=True,
            home_after=True,
        )
        self.shared_content: str = ""

    def update(self) -> str:
        """Update message content."""
        content = f"[{self.shared_content}]" if self.shared_content else ""
        return f"<code>Action! {content}</code>"


class SystemAppMessage(BaseMessage):
    """Options app message, show an example of a button with inline buttons."""

    LABEL = "options"

    def __init__(
        self,
        navigation: BotNavigationHandler,
        update_callback: Optional[List[UpdateCallback]] = None,
    ) -> None:
        """Init OptionsAppMessage class."""
        super().__init__(navigation, SystemAppMessage.LABEL, inlined=True)

        self.play_pause = True
        if isinstance(update_callback, list):
            update_callback.append(self.app_update_display)

    async def app_update_display(self) -> None:
        """Update message content when callback triggered."""
        self._toggle_play_button()
        if await self.edit_message():
            self.is_alive()

    def kill_message(self) -> None:
        """Kill the message after this callback."""
        self._toggle_play_button()

    def action_button(self) -> str:
        """Execute an action and return notification content."""
        self._toggle_play_button()
        return "option selected!"

    def text_button(self) -> str:
        """Display any text data."""
        self._toggle_play_button()
        data: KeyboardContent = [["text1", "value1"], ["text2", "value2"]]
        return format_list(data)

    def sticker_default(self) -> str:
        """Display the default sticker."""
        self._toggle_play_button()
        return f"{__raw_url__}/resources/stats_default.webp"

    def picture_default(self) -> str:
        """Display the default picture."""
        self._toggle_play_button()
        return "invalid_picture_path"

    def picture_button(self) -> str:
        """Display a local picture."""
        self._toggle_play_button()
        return (ROOT_FOLDER / "resources" / "packages.png").resolve().as_posix()

    def picture_button2(self) -> str:
        """Display a picture from a remote url."""
        self._toggle_play_button()
        return f"{__raw_url__}/resources/classes.png"

    def _toggle_play_button(self) -> None:
        """Toggle the first button between play and pause mode."""
        self.play_pause = not self.play_pause

    @staticmethod
    def action_poll(poll_answer: str) -> None:
        """Display poll answer."""
        logging.info(f"Answer is {poll_answer}")

    def update(self) -> str:
        """Update message content."""
        poll_question = "Select one option:"
        poll_choices = [":play_button: Option " + str(x) for x in range(6)]
        play_pause_button = (
            ":play_button: Start" if g_bot_is_running else ":pause_button: Stop"
        )
        self.keyboard = [
            [
                MenuButton(
                    play_pause_button,
                    callback=self.sticker_default,
                    btype=ButtonType.STICKER,
                ),
                MenuButton(
                    ":twisted_rightwards_arrows:",
                    callback=self.picture_default,
                    btype=ButtonType.PICTURE,
                ),
                MenuButton(
                    ":chart_with_upwards_trend:",
                    callback=self.picture_button,
                    btype=ButtonType.PICTURE,
                ),
                MenuButton(
                    ":chart_with_downwards_trend:",
                    callback=self.picture_button2,
                    btype=ButtonType.PICTURE,
                ),
            ]
        ]
        self.add_button(":door:", callback=self.text_button, btype=ButtonType.MESSAGE)
        self.add_button(":speaker_medium_volume:", callback=self.action_button)
        self.add_button(
            ":question:",
            self.action_poll,
            btype=ButtonType.POLL,
            args=[poll_question, poll_choices],
        )
        return "Ethereum mainnet connected 🟢"


class StartMessage(BaseMessage):
    LABEL = "start"

    def __init__(
        self,
        navigation: BotNavigationHandler,
    ) -> None:
        super().__init__(navigation, StartMessage.LABEL)
        # define menu buttons
        system = SystemAppMessage(navigation)
        self.add_button(label="All Filters", callback=AllFiltersMessage(navigation))
        self.add_button(label="Wallets Found", callback=AllFiltersMessage(navigation))
        self.add_button(label="Add Filter", callback=NewFilterMessage(navigation))
        self.add_button(label="Status", callback=system)

    def update(self) -> str:
        return (
            "Welcome to Crypto Farmers Ethereum Informer Bot\nSet up filters and get notifications about "
            "transactions with every new block"
        )


def start_bot():
    TelegramMenuSession(TELEGRAM_BOT_API).start(
        start_message_class=StartMessage,
        navigation_handler_class=BotNavigationHandler,
    )


def format_list(args_array: KeyboardContent) -> str:
    """Format array of strings in html, first element bold."""
    content = ""
    for line in args_array:
        if not isinstance(line, list):
            content += f"<b>{line}</b>"
            continue
        if line[0]:
            content += f"<b>{line[0]}</b>"
            if line[1]:
                content += ": "
        if line[1]:
            content += line[1]
        content += "\n"
    return content
