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
from telegram_bot.telegram_bot import UpdateCallback


class AllFiltersMessage(BaseMessage):
    """Options app message, show an example of a button with inline buttons."""

    LABEL = "All Filters"

    def __init__(
        self,
        navigation: BotNavigationHandler,
        update_callback: Optional[List[UpdateCallback]] = None,
    ) -> None:
        super().__init__(navigation, AllFiltersMessage.LABEL, inlined=True)

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
        for filter in all_filters:
            self.add_button(filter.name, callback=self.filter)
        self.add_button(":door:", callback=self.text_button, btype=ButtonType.MESSAGE)
        self.add_button(":speaker_medium_volume:", callback=self.action_button)
        self.add_button(
            ":question:",
            self.action_poll,
            btype=ButtonType.POLL,
            args=[poll_question, poll_choices],
        )
        return "Status updated!"
