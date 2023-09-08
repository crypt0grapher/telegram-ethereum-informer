from typing import List


class Filter:
    def __init__(
        self,
        chat_id: int,
        name: str = "",
        from_address: str = None,
        to_address: str = None,
        min_value: int = 0.01,
        max_value: int = 10,
        freshness: int = 3,
        functions: List[str] = None,
        channel: str = "",
        generator: bool = False,
        sub_filter_ids: List[int] = None,
    ):
        self.chat_id = chat_id
        self.name = name
        self.from_address = from_address
        self.to_address = to_address
        self.min_value = min_value
        self.max_value = max_value
        self.freshness = freshness
        self.functions = functions
        self.channel = channel
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
