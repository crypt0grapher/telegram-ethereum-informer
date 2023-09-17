from typing import List
from enum import Enum
from web3 import Web3
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
            "next_sub_filter_id": self.next_sub_filter_id,
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
            json_data["next_sub_filter_id"],
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
        return (
            self.from_address == other.from_address
            and self.to_address == other.to_address
            and self.min_value == other.min_value
            and self.max_value == other.max_value
            and self.operation == other.operation
            and self.freshness == other.freshness
            and self.channel == other.channel
        )

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
        )

    def generate_subfilter(self, from_address: str):
        name = f"{self.name}_{str(self.next_sub_filter_id)}"
        self.next_sub_filter_id += 1
        subfilter = Filter(
            self.chat_id,
            name,
            from_address,
            to_address=None,
            min_value=0.00001,
            max_value=10000,
            operation=self.generator_options.operation,
            channel=self.generator_options.channel,
            parent=self,
        )
        return subfilter

    def match_deployment(self, tx):
        return tx["to"] == None and tx["value"] == 0

    def match_eth_transfer(self, tx):
        address = self.to_address if self.to_address else self.from_address
        return (
            tx["to" if self.to_address else "from"].lower() == address.lower()
            and self.min_value <= safe_bignumber_to_float(tx["value"]) <= self.max_value
        )

    def match_buy_token(self, tx, w3=Web3()):
        if tx.get("from") != self.from_address:
            return False
        weth_address = "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2"
        usdc_address = "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48"
        usdt_address = "0xdAC17F958D2ee523a2206206994597C13D831ec7"
        abi = [
            {
                "inputs": [
                    {
                        "internalType": "uint256",
                        "name": "amountOutMin",
                        "type": "uint256",
                    },
                    {
                        "internalType": "address[]",
                        "name": "path",
                        "type": "address[]",
                    },
                    {"internalType": "address", "name": "to", "type": "address"},
                    {"internalType": "uint256", "name": "deadline", "type": "uint256"},
                ],
                "name": "swapExactETHForTokens",
                "outputs": [
                    {
                        "internalType": "uint256[]",
                        "name": "amounts",
                        "type": "uint256[]",
                    }
                ],
                "stateMutability": "payable",
                "type": "function",
            },
            {
                "inputs": [
                    {"internalType": "uint256", "name": "amountIn", "type": "uint256"},
                    {
                        "internalType": "uint256",
                        "name": "amountOutMin",
                        "type": "uint256",
                    },
                    {
                        "internalType": "address[]",
                        "name": "path",
                        "type": "address[]",
                    },
                    {"internalType": "address", "name": "to", "type": "address"},
                    {"internalType": "uint256", "name": "deadline", "type": "uint256"},
                ],
                "name": "swapExactTokensForTokens",
                "outputs": [
                    {
                        "internalType": "uint256[]",
                        "name": "amounts",
                        "type": "uint256[]",
                    }
                ],
                "stateMutability": "nonpayable",
                "type": "function",
            },
        ]
        input_data = tx["input"].hex()
        if not input_data.startswith("0x7ff36ab5") and not input_data.startswith(
            "0x38ed1739"
        ):
            return None
        contract = w3.eth.contract(address=tx["to"], abi=abi)
        func_obj, func_params = contract.decode_function_input(tx["input"])
        pair = [func_params["path"][0], func_params["path"][-1]]

        is_eth_transfer = tx.get("value", 0) > 0
        if pair[1] in [weth_address, usdc_address, usdt_address] or is_eth_transfer:
            return pair[0]

    def match_transaction(self, tx):
        if not hasattr(tx, "from"):
            return False
        if self.operation == Operation.Deployment:
            return self.match_deployment(tx)
        elif self.operation == Operation.BuyToken:
            return self.match_buy_token(tx)
        elif self.operation == Operation.ETHTransfer:
            return self.match_eth_transfer(tx)
        else:
            return False
