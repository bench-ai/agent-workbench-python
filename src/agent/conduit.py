import base64
import json
import subprocess
from config.operations import Operations, BrowserOperations


class CliError(Exception):
    pass


def load_config(config_path: str) -> list[Operations]:
    """
    converts a json file to a list of operations

    :param config_path: path to the json file
    :return: a list of operations
    """

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

        command_list.append("-b")
        config = json.dumps({"operations": config})

        b64 = base64.b64encode(config.encode('ascii')).decode('utf-8')
        command_list.append(b64)

        console_out = subprocess.run(command_list, capture_output=True, text=True)

        if console_out.stderr != "":
            raise CliError(console_out.stderr)

        if verbose:
            print(console_out.stdout)

        return console_out.stdout
