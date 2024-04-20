import json
import subprocess
from config.operations import Operations, BrowserOperations


def load_config(config_path: str) -> list[Operations]:
    with open(config_path, "r") as f:
        data = json.load(f)

        operations = data["operations"]

        browser_list = []

        for opt in operations:
            match opt["type"]:
                case "browser":
                    browser_list.append(BrowserOperations.load(opt))
                case _:
                    raise Exception(f"{opt['type']} is not a valid operation type")

        return browser_list


class Agent:

    def __init__(self, config: list[Operations]):
        self.config = config

    @classmethod
    def version(cls, verbose=False) -> str:
        """
        Returns the version of the Agent CLI
        :param verbose: prints the version to the console
        :return:
        """
        v = subprocess.run(
            ["config", "version"],
            capture_output=True,
            text=True)

        response: str = v.stdout

        if verbose:
            print(response)

        if response.startswith("Version"):
            return response
        else:
            raise ValueError("Agent CLI not found")

    def run(self, is_json_string=False, verbose=False) -> str:
        command_list = ["config", "run"]

        config = []
        for operation in self.config:
            config.append(operation.to_dict())

        if is_json_string:
            command_list.append("-j")
            config = json.dumps(config)

        command_list.append(config)

        console_out: str = subprocess.run(command_list, capture_output=True, text=True).stdout

        if verbose:
            print(console_out)

        return console_out
