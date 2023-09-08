from typing import List, Union

class User:
    def __init__(self,
                 name: str,
                 telegram_id: str,
                 telegram_username: str,
                 channels: List[str]):
        self.name = name
        self.telegram_id = telegram_id
        self.telegram_username = telegram_username
        self.channels = channels