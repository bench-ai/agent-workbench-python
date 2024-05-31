"""
This module is in charge of sending and executing commands through the Agent CLI
"""
import json
import requests
import os
import subprocess
import tempfile
import time
from .config.session import Session
from .miscellaneous.paths import get_live_session_path


def version(verbose=False) -> str:
    """
    returns the version of the Agent CLI

    :param verbose: prints the version to the console
    :return:
    """

    ver = subprocess.run(
        ["agent", "version"], capture_output=True, text=True, check=True
    )

    response: str = ver.stdout

    if verbose:
        print(response)

    if response.startswith("Version"):
        return response

    raise ValueError("Agent CLI not found")


def remove_session(session_id: str) -> None:
    """
    removes a session based on session_id

    :param session_id:
    :return:
    """
    rem = subprocess.run(
        ["agent", "session", "rm", session_id], capture_output=True, text=True, check=True
    )

    response: str = rem.stderr

    if len(response) > 0:
        raise EnvironmentError("Agent CLI not found")


def remove_all() -> None:
    """
    removes all sessions
    :return:
    """
    rem = subprocess.run(
        ["agent", "session", "-rf", "rm"], capture_output=True, text=True, check=True
    )

    response: str = rem.stderr

    if len(response) > 0:
        raise EnvironmentError("Agent CLI not found")


def list_all_sessions() -> list[str]:
    """
    :return: the list of all the saved session names
    """
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


class Conduit:
    """
    Class based interface for the agent cli
    """

    def __init__(
            self,
            config: Session,
    ):
        """
        :param config: the config object with all the execution details
        """
        self.config = config

    def run(self, verbose=False) -> str:
        """
        Runs the config

        :param verbose: Bool for if the stdout should be printed
        :return: the stdout
        """
        command_list = ["agent", "run"]
        if os.getenv("BENCHAI_AGENT_PATH"):
            command_list = [os.getenv("BENCHAI_AGENT_PATH"), "run"]

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
                 config: Session):
        self._session_lifetime = config.session_lifetime
        self._headless = config.headless
        self._config = config
        self.process = None

    def __enter__(self):
        command_list = ["agent", "live"]
        command_list += ["-h"] if self._headless else []
        command_list += ["-life", str(self._config.command_lifetime)] if self._config.command_lifetime else []
        command_list += [self._config.get_session_id(), str(self._session_lifetime)]

        self.process = subprocess.Popen(
            command_list
        )

        pth = os.path.join(
            get_live_session_path(self._config.get_session_id()), "commands"
        )

        while not os.path.isdir(pth):
            time.sleep(1)

    def __exit__(self, exception_type, exception_value, traceback):
        self._config.end_live_session()
