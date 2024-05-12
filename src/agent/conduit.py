"""
This module is in charge of sending and executing commands through the Agent CLI
"""
import json
import subprocess
import tempfile

from .config.creator import Creator


class Conduit:
    """
    Class based interface for the agent cli
    """

    def __init__(
            self,
            config: Creator,
    ):
        """
        :param config: the config object with all the execution details
        """
        self.config = config

    @staticmethod
    def version(verbose=False) -> str:
        """
        Returns the version of the Agent CLI
        :param verbose: prints the version to the console
        :return:
        """
        version = subprocess.run(
            ["config", "version"], capture_output=True, text=True, check=True
        )

        response: str = version.stdout

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

        config_dict = self.config.to_dict()

        tf = tempfile.NamedTemporaryFile(suffix=".json")

        json.dump(config_dict, tf)

        command_list.append(tf.name)
        console_out = subprocess.run(
            command_list, capture_output=True, text=True, check=False
        )

        tf.close()
        if console_out.stderr != "":
            raise EnvironmentError(console_out.stderr)

        if verbose:
            print(console_out.stdout)

        return console_out.stdout
