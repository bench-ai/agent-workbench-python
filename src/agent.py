import json
import subprocess
from config.operations import Operations


def load_json(config_path) -> list[Operations]:
    with open(config_path, "r") as f:
        data = json.load(f)

        operations = data["operations"]

class Agent:

    def __init__(self, config: list[Operations]):

        '''
        TODO: Accept from path
        '''
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

        if is_json_string:
            command_list.append("-j")
            config = json.dumps(config)

        command_list.append(config)

        console_out: str = subprocess.run(command_list, capture_output=True, text=True).stdout

        if verbose:
            print(console_out)

        return console_out
