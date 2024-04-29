import base64
import json
import subprocess
from src.config.operations import Operations, BrowserOperations, LLMOperations


class CliError(Exception):
    pass


def load_config(config_path: str) -> list[Operations]:
    with open(config_path, "r") as f:
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
                    raise Exception(f"{opt['type']} is not a valid operation type")
        
        op_list = browser_list + llm_list
        return op_list


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

    def run(self, verbose=False) -> str:
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
