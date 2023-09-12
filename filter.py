from typing import List
from enum import Enum

from helpers import safe_bignumber_to_float


class Operation(Enum):
    Deployment = "Deployment"
    BuyToken = "BuyToken"
    ETHTransfer = "ETHTransfer"


class Generator:
    def __init__(self, operation, parent, channel):
        self.operation = operation
        self.parent = parent
        self.channel = channel

    def to_json(self):
        return {
            "operation": self.operation.value,
            "parent": self.parent,
            "channel": self.channel,
        }

    @classmethod
    def from_json(cls, json_data):
        return cls(
            Operation(json_data["operation"]), json_data["parent"], json_data["channel"]
        )


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
        operation: Operation = Operation.ETHTransfer,
        channel: str = "",
        generator: bool = False,
        generator_options: Generator = Generator(Operation.BuyToken, None, None),
        generator_channel: str = "",
        is_active: bool = True,
        sub_filter_ids: List[int] = None,
        parent=None,
    ):
        self.chat_id = chat_id
        self.name = name
        self.from_address = from_address
        self.to_address = to_address
        self.min_value = min_value
        self.max_value = max_value
        self.operation = operation
        self.freshness = freshness
        self.channel = channel if channel else chat_id
        self.generator_options = generator_options
        self.generator_channel = generator_channel if generator_channel else chat_id
        self.generator = generator
        self.is_active = is_active
        self.sub_filter_ids = sub_filter_ids
        self.next_sub_filter_id = 1
        self.parent = parent

    def to_json(self):
        return {
            "chat_id": self.chat_id,
            "name": self.name,
            "from_address": self.from_address,
            "to_address": self.to_address,
            "min_value": self.min_value,
            "max_value": self.max_value,
            "operation": self.operation.value,
            "freshness": self.freshness,
            "channel": self.channel,
            "generator": self.generator,
            "generator_options": self.generator_options.to_json(),
            "generator_channel": self.generator_channel,
            "is_active": self.is_active,
            "sub_filter_ids": self.sub_filter_ids,
        }

    @classmethod
    def from_json(cls, json_data):
        return cls(
            json_data["chat_id"],
            json_data["name"],
            json_data["from_address"],
            json_data["to_address"],
            json_data["min_value"],
            json_data["max_value"],
            json_data["freshness"],
            Operation(json_data["operation"]),
            json_data["channel"],
            json_data["generator"],
            Generator.from_json(json_data["generator_options"]),
            json_data["generator_channel"],
            json_data["is_active"],
            json_data["sub_filter_ids"],
        )

    def is_correct(self):
        if self.from_address and self.to_address:
            return False
        if self.min_value < 0 or self.max_value < 0:
            return False
        if self.min_value > self.max_value:
            return False
        if self.freshness < 0:
            return False
        return (
            self.chat_id
            and self.name
            and (self.from_address or self.to_address)
            and self.min_value
            and self.max_value
            and self.freshness
            and self.channel
        )

    def __str__(self):
        return str(self.to_json())

    def __repr__(self):
        return self.__str__()

    def __eq__(self, other):
        return self.name == other.name

    def copy(self):
        return Filter(
            self.chat_id,
            self.name,
            self.from_address,
            self.to_address,
            self.min_value,
            self.max_value,
            self.freshness,
            self.operation,
            self.channel,
            self.generator,
            self.generator_options,
            self.generator_channel,
            self.is_active,
            self.sub_filter_ids,
        )

    def generate_subfilter(self, address: str):
        name = f"{self.name}_{str(self.next_sub_filter_id)}"
        self.next_sub_filter_id += 1
        subfilter = Filter(
            self.chat_id,
            name,
            from_address=address,
            to_address=None,
            min_value=0.00001,
            max_value=10000,
            operation=self.generator_options.operation,
            channel=self.generator_options.channel,
            parent=self.name,
        )
        if self.sub_filter_ids == None:
            self.sub_filter_ids = []
        self.sub_filter_ids.append(name)
        return subfilter

    def __del__(self):
        if self.parent and self.parent.sub_filter_ids:
            self.parent.sub_filter_ids.remove(self.name)
            self.parent = None

    def match_deployment(self, tx):
        return tx["to"] == None and tx["value"] == 0

    def match_eth_transfer(self, tx):
        address = self.to_address if self.to_address else self.from_address
        return (
            tx["to" if self.to_address else "from"].lower() == address.lower()
            and self.min_value <= safe_bignumber_to_float(tx["value"]) <= self.max_value
        )

    def match_buy_token(self, tx):
        return tx["input"].hex().startswith("0x7ff36ab5") or tx[
            "input"
        ].hex().startswith("0x38ed1739")

    def match_transaction(self, tx):
        if "from" not in tx:
            return False
        if self.operation == Operation.Deployment:
            return self.match_deployment(tx)
        elif self.operation == Operation.BuyToken:
            return self.match_buy_token(tx)
        elif self.operation == Operation.ETHTransfer:
            return self.match_eth_transfer(tx)
        else:
            return False
