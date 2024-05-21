"""
This module handles processing operations which are sequences of commands
"""

import json
import os
import typing
import uuid
from typing import Union

from .command import (
    Command,
    _Navigate,
    _FullPageScreenshot,
    _ElementScreenShot,
    _CollectNodes,
    _Sleep,
    _Click,
    _Standard,
    _Multimodal,
    _Assistant,
    _SaveHtml,
    _IterateHtml,
    CommandError,
)

from ..miscellaneous.paths import get_live_session_path, get_save_path


class Operation(list):
    """
    Am Operation is a list of commands
    """

    def __init__(
            self,
            op_type: str,
            session_name: str,
            timeout: None | int = None,
            live=False
    ):
        """
        initializes an Operation

        :param op_type: The type of all the commands
        :param session_name: the name of the current session
        :param timeout: the max time the operation should run for
        :param live: True means the operation is part of a live session
        """

        # if timeout and not 0 <= timeout <= 32767:
        #     raise IndexError(f"timeout must be between 0 and 32767, got {timeout}")

        super().__init__()

        self.op_type = op_type
        self.timeout = timeout
        self._session_name = session_name
        self._live = live

    def append(self, command: Command):
        """
        appends a command to the operation if the type is appropriate
        :param command: The command to append
        """
        if command.command_type != self.op_type:
            raise TypeError(f"cannot append command of type {command.command_type}")

        super().append(command)

    def get_settings(self) -> dict:
        """
        gets the settings of the operations

        :return: The settings dict
        """
        return {"timeout": self.timeout} if self.timeout else {}

    def to_dict(self) -> dict[str, typing.Any]:
        """
        converts the operation to a dictionary
        :return: operation as a dictionary
        """

        op_dict = {
            "type": self.op_type,
            "settings": self.get_settings(),
            "command_list": [com.to_dict() for com in self],
        }

        return op_dict

    def to_json_string(self) -> str:
        """
        converts the operation to a json string

        :return: an operation string
        """
        return json.dumps(self.to_dict())

    def _started(self) -> bool:
        """
        True if the session has started (only applicable to live sessions). Useful because users may
        try to send commands to a session before it even goes live.
        :return:
        """

        pth = os.path.join(
            get_live_session_path(self._session_name), "commands"
        )

        return os.path.isdir(pth)

    def _exited(self) -> bool:
        """
        :return: True if the session has ended
        """
        from .session import InvalidSessionError

        if not self._live:
            raise InvalidSessionError("session is not live, cannot check if session exited")

        if not self._started():
            raise InvalidSessionError("session has not started")

        pth = os.path.join(get_live_session_path(self._session_name), "exit.txt")
        return os.path.exists(pth)

    def _get_live_session_path(self, dir_name: str) -> str:
        if not self._live:
            raise NotADirectoryError(f"{dir_name} directory only exists for live sessions")

        return os.path.join(
            get_live_session_path(self._session_name),
            dir_name
        )

    @property
    def response_dir(self) -> str:
        return self._get_live_session_path("responses")

    @property
    def command_dir(self) -> str:
        return self._get_live_session_path("commands")

    def _response_session_path(self, uid: uuid.UUID):
        return self._session_name + "/" + "responses" + "/" + str(uid)

    def _check_command_status(self, uid: uuid.UUID):
        err_path = os.path.join(get_save_path(), self._response_session_path(uid), "err.txt")
        success_path = os.path.join(get_save_path(), self._response_session_path(uid), "success.txt")

        if os.path.exists(err_path):
            with open(err_path, "r") as f:
                raise CommandError(f.read())

        return os.path.exists(success_path)

    def _process(self,
                 command: (
                         _Navigate | _FullPageScreenshot | _SaveHtml | _CollectNodes | _ElementScreenShot | _Click | _Sleep),
                 uid: uuid.UUID,
                 command_type="browser") -> (
            _Navigate | _FullPageScreenshot | _SaveHtml | _CollectNodes | _ElementScreenShot | _Click | _Sleep):

        if not self._live:
            self.append(command)
        else:
            if self._exited():
                raise ConnectionError("session has already exited")

            pth = os.path.join(self.command_dir, str(uid) + ".json.tmp")

            with open(pth, "w") as f:
                data_dict = {
                    "type": command_type,
                    "command_list": [
                        command.to_dict(),
                    ]
                }

                json.dump(data_dict, f)

            final_pth = os.path.join(self.command_dir, str(uid) + ".json")
            os.rename(pth, final_pth)

            while not self._check_command_status(uid):
                pass

        return command


class _BrowserOperations(Operation):
    """
    An operation that holds and processes browser commands
    """

    def __init__(self,
                 session_name: str,
                 headless: bool = False,
                 timeout: None | int = None,
                 live=False):
        """
        Initializes a Browser Operation

        :param headless: Sets if you wish to visually see the agent operate on the browser
        :param timeout: the maxtime the browser operation can operate for
        """
        super().__init__("browser", session_name, timeout, live=live)

        self.headless = headless
        self._session_name = session_name
        self._live = live

    def get_settings(self) -> dict:
        """
        Gets the settings of the operation
        :return: a dict representing the operations
        """
        settings = super().get_settings()
        settings["headless"] = self.headless
        return settings

    def add_navigate_command(self, url: str) -> _Navigate:
        uid = uuid.uuid4()
        return super()._process(_Navigate(url), uid)

    def add_full_screenshot_command(self, quality: int, name: str, snapshot_name: str) -> _FullPageScreenshot:
        uid = uuid.uuid4()
        return super()._process(
            _FullPageScreenshot(super()._response_session_path(uid), quality, name, snapshot_name),
            uid
        )

    def add_element_screenshot_command(
            self,
            scale: int,
            selector: str,
            name: str,
            snapshot_name: str) -> _ElementScreenShot:
        uid = uuid.uuid4()
        return super()._process(
            _ElementScreenShot(super()._response_session_path(uid), scale, selector, name, snapshot_name),
            uid
        )

    def add_collect_nodes(self,
                          selector: str,
                          snapshot_name: str,
                          recurse: bool = True,
                          prepopulate: bool = True,
                          get_styles: bool = True) -> _CollectNodes:
        uid = uuid.uuid4()
        cn = _CollectNodes(
            selector,
            snapshot_name,
            super()._response_session_path(uid),
            recurse,
            prepopulate,
            get_styles)
        return self._process(
            cn, uid
        )

    def add_html(self,
                 snapshot_name: str) -> _SaveHtml:
        uid = uuid.uuid4()
        cah = _SaveHtml(super()._response_session_path(uid), snapshot_name)
        return super()._process(cah, uid)

    def add_sleep(self,
                  sleep: int):
        cs = _Sleep(sleep)
        uid = uuid.uuid4()
        return super()._process(cs, uid)

    def add_click(self,
                  selector: str,
                  query_type: str):
        cc = _Click(selector, query_type)
        uid = uuid.uuid4()
        return super()._process(cc, uid)

    def add_iterate_html(self,
                         iterate_limit: int,
                         save_html: bool,
                         save_node: bool,
                         save_full_page_image: bool,
                         pause_time: int = 500,
                         snapshot_name: str = "snapshot",
                         image_quality=10):

        ic = _IterateHtml(super()._session_name,
                          iterate_limit,
                          save_html,
                          save_node,
                          save_full_page_image,
                          pause_time,
                          image_quality,
                          snapshot_name)

        if super()._live:
            raise TypeError("cannot use the iterate html command during a live session")

        self.append(ic)
        return ic


class LLMSettings(dict):
    """
    A dictionary subclass for the settings of an LLM.
    """

    def __init__(
            self, name: Union[str, None] = None, api_key: Union[str, None] = None, **kwargs
    ):
        # pylint: disable=W0613
        """
        Initializes the LLMSettings dictionary with the name of the LLM and the api key

        :param name: The name of the LLM (OpenAI, Gemini, etc.)
        :param: api_key: the api key needed to access the LLM api
        :param kwargs: additional keyword arguments
        """
        super().__init__()
        if not isinstance(name, str):
            raise TypeError("Name must be a string.")
        if not isinstance(api_key, str):
            raise TypeError("API key must be a string.")
        self.update({"name": name, "api_key": api_key})


class OpenAISettings(LLMSettings):
    """
    A subclass of LLMSettings that is a dictionary of settings unique to OpenAi's api
    """

    def __init__(
            self,
            api_key: Union[str, None] = None,
            model: Union[str, None] = None,
            temperature: float = 1.0,
    ):
        """
        Initializes the OPENAI_Settings object
        :param api_key:  key for the api
        :param model: the specific OpenAI model the user wants to use (e.g., gpt-3.5-turbo)
        :param temperature: the temperature the user wants the model to use
        """
        super().__init__("OpenAI", api_key)
        if not isinstance(model, str):
            raise TypeError("Model must be a string.")
        if not isinstance(temperature, float):
            raise TypeError("Temperature must be a float.")

        self._allowed_keys = {"name", "api_key", "model", "temperature"}
        self.update(
            {
                "name": "OpenAI",
                "api_key": api_key,
                "model": model,
                "temperature": temperature,
            }
        )

    # makes sure that all keys added to openai settings are valid keys
    def __setitem__(self, key, value):
        """
        Overrides set item method from dict, so we can ensure only allowed keys get added.
        If an invalid key is tried to be added, it will raise a
            KeyError with a message saying which key was invalid.

        :param key: The key the user wants to add to the dict
        :param value: the value the user wants to give the key
        """
        if key not in self._allowed_keys:
            raise KeyError(
                f"Invalid key: '{key}'. Only {', '.join(self._allowed_keys)} keys are allowed."
            )
        super().__setitem__(key, value)


class _LLMOperations(Operation):
    """
    Subclass of Operations specifically designed for making requests for LLM Commands.
    """

    def __init__(  # pylint: disable=too-many-arguments
            self,
            try_limit: int,
            timeout: int,
            max_tokens: int,
            llm_settings: list[LLMSettings],
            session_name: str,
            live: bool = False
    ):
        """
        Initializes the LLMOperations

        :param try_limit: the number of times the user wants a request to be
            tried by the agent if it is not able to get a response on the first try
        :param timeout: the amount of time the user wants the agent to allow
            for a response to be received from a model before requesting again
        :param max_tokens: the maximum number of words the user wants the model's response to be
        :param llm_settings: a list of LLMSettings objects defining the settings
            for the different LLMs the user wants the agent to switch between
        :param session_name: the name of the session
        """
        super().__init__("llm", session_name, timeout, live=live)
        self.settings = {
            "try_limit": try_limit,
            "max_tokens": max_tokens,
            "llm_settings": llm_settings,
        }

        self._session_name = session_name

    def execute(self) -> _Assistant:

        uid = uuid.uuid4()

        if not self._live:
            raise TypeError("not a live session")

        if self._exited():
            raise ConnectionError("session has already exited")

        data_dict = self.to_dict()
        pth = os.path.join(self.command_dir, str(uid) + ".json.tmp")

        with open(pth, "w") as f:
            json.dump(data_dict, f)

        final_pth = os.path.join(self.command_dir, str(uid) + ".json")
        os.rename(pth, final_pth)

        while not self._check_command_status(uid):
            pass

        save_path = os.path.join(self.response_dir, str(uid), "completion.json")
        with open(save_path, "r") as f:
            response = json.load(f)
            a_mess: dict = response["message_list"][-1]["message"]

        return _Assistant(a_mess["role"], a_mess["content"], a_mess.get("tool_calls"))

    def get_settings(self) -> dict:
        """
        gets the settings for the LLM Operations
        """
        settings = super().get_settings()
        settings.update(self.settings)
        return settings

    def add_standard_command(self, role: str, content: str) -> _Standard:
        command = _Standard(role, content)
        self.append(command)
        return command

    def add_multimodal_command(self, role) -> _Multimodal:
        command = _Multimodal(role)
        self.append(command)
        return command

    def add_assistant_command(self, role: str, content: str) -> _Assistant:
        command = _Assistant(role, content)
        self.append(command)
        return command

    def add_response(self, com: _Assistant):
        self.append(com)
