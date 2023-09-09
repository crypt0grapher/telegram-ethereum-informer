from typing import List

from enum import Enum


class Operation(Enum):
    Deployment = "Deployment"
    BuyToken = "BuyToken"
    ETHTransfer = "ETHTransfer"


class Generator:
    def __init__(self, operation, parent, channel):
        self.operation = operation
        self.parent = parent
        self.channel = channel


class Filter:
    def __init__(
        self,
        chat_id: int,
        name: str = "",
        from_address: str = None,
        to_address: str = None,
        min_value: float = 0.01,
        max_value: float = 10.0,
        freshness: int = 3,
        channel: str = "",
        generator: bool = False,
        generator_options: Generator = Generator(Operation.BuyToken, None, None),
        generator_channel: str = "",
        sub_filter_ids: List[int] = None,
    ):
        self.chat_id = chat_id
        self.name = name
        self.from_address = from_address
        self.to_address = to_address
        self.min_value = min_value
        self.max_value = max_value
        self.freshness = freshness
        self.channel = channel if channel else chat_id
        self.generator_options = generator_options
        self.generator_channel = generator_channel if generator_channel else chat_id
        self.generator = generator
        self.sub_filter_ids = sub_filter_ids

    def __str__(self):
        return (
            f"'<strong>{self.name}'</strong>:\n"
            f"{'from' if self.from_address else 'to'} {self.from_address if self.from_address else self.to_address}"
            f" {f'freshness of sender: {self.freshness} txs max,' if self.freshness > 0 else ''} min {self.min_value}, max {self.max_value}\n"
        )

    def __repr__(self):
        return self.__str__()

    def __eq__(self, other):
        return self.name == other.name
