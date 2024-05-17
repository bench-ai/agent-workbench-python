"""
This module is in charge of sending and executing commands through the Agent CLI
"""
import json
import os
import subprocess
import tempfile
import time
import uuid

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
            ["agent", "version"], capture_output=True, text=True, check=True
        )

        response: str = version.stdout

        if verbose:
            print(response)

        if response.startswith("Version"):
            return response

        raise ValueError("Agent CLI not found")

    @staticmethod
    def remove_session(session_id: str):
        rem = subprocess.run(
            ["agent", "session", "rm", session_id], capture_output=True, text=True, check=True
        )

        response: str = rem.stderr

        if len(response) > 0:
            raise EnvironmentError("Agent CLI not found")

    @staticmethod
    def remove_all():
        rem = subprocess.run(
            ["agent", "session", "-rf", "rm"], capture_output=True, text=True, check=True
        )

        response: str = rem.stderr

        if len(response) > 0:
            raise EnvironmentError("Agent CLI not found")

    @staticmethod
    def list_sessions() -> list[str]:
        sess = subprocess.run(
            ["agent", "session", "ls"], capture_output=True, text=True, check=True
        )

        response: str = sess.stdout
        sess_list: list[str] = (response
                                .replace("[", "")
                                .replace("]", "")
                                .replace("\n", "")
                                .split(", "))

        if sess_list[0] == "":
            return []

        return sess_list

    def run(self, verbose=False) -> str:
        """
        Runs the config

        :param verbose: prints the stdout
        :return: the stdout
        """
        command_list = ["agent", "run"]

        config_dict = self.config.to_dict()

        tf = tempfile.NamedTemporaryFile(suffix=".json", mode="w+")

        json.dump(config_dict, tf)
        tf.flush()

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


class LiveConduit:

    def __init__(self,
                 config: Creator,
                 session_lifetime: int,
                 headless: bool = False,
                 command_lifetime: str | bool = None):
        self._session_lifetime = session_lifetime
        self._headless = headless
        self._command_lifetime = command_lifetime
        self._config = config

    def __enter__(self):
        command_list = ["agent", "live", self._config.get_session_id(), str(self._session_lifetime)]
        subprocess.Popen(
            command_list
        )

        if os.getenv("BENCHAI-SAVEDIR"):
            save_path = os.getenv("BENCHAI-SAVEDIR")
        else:
            save_path = os.path.join(os.path.expanduser("~"), ".cache", "benchai")

        pth = os.path.join(
            save_path, "agent", "sessions", self._config.get_session_id(), "commands"
        )

        while not os.path.isdir(pth):
            time.sleep(1)

    def __exit__(self, exception_type, exception_value, traceback):
        print("exited")
