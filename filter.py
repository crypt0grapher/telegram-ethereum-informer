from typing import List


class Filter:
    def __init__(self,
                 id: int,
                 user_id: str,
                 name: str,
                 from_address: str,
                 to_address: str,
                 min_value: float,
                 max_value: float,
                 freshness: int,
                 functions: List[str],
                 channel: str,
                 generator: bool,
                 sub_filter_ids: List[int]):
        self.id = id
        self.user_id = user_id
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