"""
This module is in charge of sending and executing commands through the Agent CLI
"""

import json
import subprocess
from .config.operations import Operations, BrowserOperations, LLMOperations


def load_config(config_path: str) -> list[Operations]:
    """
    converts a json file to a list of operations

    :param config_path: path to the json file
    :return: a list of operations
    """

    with open(config_path, "r", encoding="utf-8") as f:
        data = json.load(f)

        operations = data["operations"]

        browser_list = []
        llm_list = []

        for opt in operations:
            match opt["type"]:
                case "browser":
                    browser_list.append(BrowserOperations.load(opt))
                case "llm":
                    llm_list.append(LLMOperations.load(opt))
                case _:
                    raise TypeError(f"{opt['type']} is not a valid operation type")

        op_list = browser_list + llm_list
        return op_list


class Conduit:
    """
    Class based interface for the agent cli
    """

    def __init__(self, config: list[Operations]):
        """
        :param config: The list of operations to execute
        """
        self.config = config

    @classmethod
    def version(cls, verbose=False) -> str:
        """
        Returns the version of the Agent CLI
        :param verbose: prints the version to the console
        :return:
        """
        v = subprocess.run(
            ["config", "version"], capture_output=True, text=True, check=True
        )

        response: str = v.stdout

        if verbose:
            print(response)

        if response.startswith("Version"):
            return response

        raise ValueError("Agent CLI not found")

    def run(self, verbose=False) -> str:
        """
        Runs the config

        :param verbose: print the stdout
        :return: the stdout
        """
        command_list = ["agent", "run"]

        config = []
        for operation in self.config:
            config.append(operation.to_dict())

        with open("./temp-config.json", "w", encoding="utf-8") as f:
            json.dump({"operations": config}, f)

        command_list.append("./temp-config.json")
        console_out = subprocess.run(
            command_list, capture_output=True, text=True, check=True
        )

        if verbose:
            print(console_out.stdout)

        return console_out.stdout
