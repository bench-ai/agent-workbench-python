import json
import os.path
import typing
import uuid
from .operation import Operation, _BrowserOperations, _LLMOperations, LLMSettings
from ..miscellaneous.paths import get_live_session_path


class InvalidSessionError(Exception):
    """
    raise this exception when sessions are used incorrectly
    """
    pass


class Session:
    """
    Manages the workbench session.
    """

    def __init__(self,
                 s_id: str | None = None,
                 live: bool = False,
                 headless: bool = False,
                 session_lifetime=32_766,
                 command_lifetime=5000):

        """
        Initializes a creator object

        :param s_id: an optional session id to assign to the session, useful for location sessions
        :param live: allows users to interact with the browser dynamically, allocating new commands as
        long browser / LLM session is running
        :param headless: dictates whether the browser session will be headless
        :param session_lifetime: the lifetime of the session in milliseconds
        :param command_lifetime: how long a command should run for. Only applies to LLMs if not live. Applies to all
        commands if it is live. Time is in milliseconds
        """

        if command_lifetime < 0:
            raise ValueError("command_lifetime must be greater than 0ms, since command will never run")

        self._session_lifetime = session_lifetime // 1000

        if (self._session_lifetime * 1000) < command_lifetime:
            raise ValueError("command_lifetime cannot be longer than session lifetime")

        self._command_lifetime = command_lifetime
        self._session_lifetime = session_lifetime
        self._headless = headless

        self._id = ""
        if not s_id:
            self._id = str(uuid.uuid4())
        else:
            self._id = s_id

        self._operations: list[Operation] = []
        self._live = live

    def get_session_id(self) -> str:
        """
        :return: the current session id
        """
        return self._id

    @property
    def headless(self):
        """
        True if the session is headless
        :return: the headless status
        """
        return self._headless

    @property
    def live(self) -> bool:
        """
        True if the session type is live (only applicable to live sessions)
        :return: the session status
        """
        return self._live

    @property
    def session_lifetime(self):
        """
        :return: The lifetime of the session in seconds
        """
        return self._session_lifetime

    @property
    def command_lifetime(self):
        """
        :return: The command lifetime in ms
        """
        return self._command_lifetime

    @property
    def exited(self) -> bool:
        """
        :return: True if the session has ended
        """
        if not self._live:
            raise InvalidSessionError("session is not live, cannot check if session exited")

        if not self._started():
            raise InvalidSessionError("session has not started")

        pth = os.path.join(get_live_session_path(self._id), "exit.txt")
        return os.path.exists(pth)

    def _started(self) -> bool:
        """
        True if the session has started (only applicable to live sessions). Useful because users may
        try to send commands to a session before it even goes live.
        :return:
        """

        pth = os.path.join(
            get_live_session_path(self._id), "commands"
        )

        return os.path.isdir(pth)

    def end_live_session(self) -> None:
        """
        ends a live session
        """

        if not self._live:
            raise InvalidSessionError("cannot end a non live session")

        if self.exited:
            return

        # writes the exit command signaling the live session to terminate
        exit_path = os.path.join(
            get_live_session_path(self._id), "commands", str(uuid.uuid4()) + "exit.json.tmp")

        save_path = os.path.join(
            get_live_session_path(self._id), "commands", str(uuid.uuid4()) + "exit.json")

        with open(exit_path, "w") as f:
            json.dump({
                "type": "exit",
            }, f)

        """
        the golang agent workbench reads the file too fast. This causes issues because it reads the file
        before it has finished being written too. Since the go workbench will only read files that end with .json
        we rename it to .json after we are done dumping data. This signals the file is ready to read.
        """

        os.rename(exit_path, save_path)

    def new_llm_operation(self,
                          try_limit: int,
                          max_tokens: int,
                          llm_settings: list[LLMSettings],
                          tools: list[typing.Callable] = None,
                          tool_choice: str = None) -> _LLMOperations:

        """
        Adds a LLM operation to the session. Allows users to send llm commands.

        :param tool_choice: selector for tools
        :param tools: list of tool functions
        :param try_limit: how many times we should retry the request using exponential backoff
        :param max_tokens: the max amount of tokens the model can output
        :param llm_settings: a list of LLMs to run the request on, it will start with the first LLM if that fails,
        it will proceed to the rest
        :return: a llm operation object
        """

        if self._live:
            llm_op = _LLMOperations(
                try_limit,
                self.command_lifetime,
                max_tokens,
                tools,
                tool_choice,
                llm_settings,
                self._id,
                live=self._live
            )
        else:
            llm_op = _LLMOperations(
                try_limit,
                self._session_lifetime,
                max_tokens,
                tools,
                tool_choice,
                llm_settings,
                self._id,
                live=self._live
            )

        self._operations.append(llm_op)
        return llm_op

    def new_browser_operation(self) -> _BrowserOperations:

        """
        Adds a Browser operation to the session. Allows users to send browser commands.
        :return: a browser operation object
        """

        brow_op = _BrowserOperations(
            self._id,
            headless=self._headless,
            timeout=self._session_lifetime,
            live=self._live)

        self._operations.append(brow_op)
        return brow_op

    def to_dict(self) -> dict:
        ret_dict = {
            "session_id": self._id,
            "operations": [opt.to_dict() for opt in self._operations]
        }

        return ret_dict
