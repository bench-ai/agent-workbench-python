import json
import typing
from typing import Union
from .command import (
    Command,
    Navigate,
    FullPageScreenshot,
    ElementScreenShot,
    CollectNodes,
    SaveHtml,
    Sleep,
    Click,
    Standard,
    Multimodal,
    Assistant,
    Tool,
)


class Operations(list):
    def __init__(
        self,
        op_type: str,
        timeout: None | int = None,
    ):

        if timeout and not (0 <= timeout <= 32767):
            raise Exception(f"timeout must be between 0 and 32767, got {timeout}")

        super().__init__()

        self.op_type = op_type
        self.timeout = timeout

    def append(self, command: Command):

        if command.command_type == self.op_type:
            super().append(command)
        else:
            raise Exception(f"cannot append command of type {command.command_type}")

    def get_settings(self) -> dict:
        return {"timeout": self.timeout} if self.timeout else {}

    def to_dict(self) -> dict[str, typing.Any]:
        op_dict = {
            "type": self.op_type,
            "settings": self.get_settings(),
            "command_list": [com.to_dict() for com in self],
        }

        return op_dict

    def to_json_string(self) -> str:
        return json.dumps(self.to_dict())


class BrowserOperations(Operations):
    def __init__(self, headless: bool = False, timeout: None | int = None):
        super().__init__("browser", timeout)

        self.headless = headless

    def get_settings(self) -> dict:
        super().get_settings()["headless"] = self.headless
        return super().get_settings()

    @classmethod
    def load(cls, data_dict: dict):
        browser_opts = cls(**data_dict["settings"])

        for command in data_dict["command_list"]:

            match command["command_name"]:
                case "open_web_page":
                    initialized_command = Navigate.init_from_dict(command)
                case "full_page_screenshot":
                    initialized_command = FullPageScreenshot.init_from_dict(command)
                case "element_screenshot":
                    initialized_command = ElementScreenShot.init_from_dict(command)
                case "collect_nodes":
                    initialized_command = CollectNodes.init_from_dict(command)
                case "save_html":
                    initialized_command = SaveHtml.init_from_dict(command)
                case "sleep":
                    initialized_command = Sleep.init_from_dict(command)
                case "click":
                    initialized_command = Click.init_from_dict(command)
                case _:
                    raise Exception(
                        f"{command['command_name']} is not a valid browser command"
                    )

            browser_opts.append(initialized_command)

        return browser_opts


class LLMSettings(dict):
    """
    A dictionary subclass for the settings of an LLM.
    """

    def __init__(self, name: Union[str, None] = None, api_key: Union[str, None] = None):
        """
        Initializes the LLMSettings dictionary with the name of the LLM and the api key

        :param name: the name of the LLM (OpenAI, Gemini, etc.)
        :api_key: the api key needed to access the LLM api
        """
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
        name: Union[str, None] = None,
        api_key: Union[str, None] = None,
        model: Union[str, None] = None,
        temperature: float = 1.0,
    ):
        """
        Initializes the OPENAI_Settings object
        :param name: the name of the api
        :param api_key: the api key for the api
        :param model: the specific OpenAI model the user wants to use (eg. gpt-3.5-turbo)
        :param temperature: the temperature the user wants the model to use
        """
        super().__init__(name, api_key)
        if not isinstance(model, str):
            raise TypeError("Model must be a string.")
        if not isinstance(temperature, float):
            raise TypeError("Temperature must be a float.")

        self._allowed_keys = {"name", "api_key", "model", "temperature"}
        self.update(
            {
                "name": name,
                "api_key": api_key,
                "model": model,
                "temperature": temperature,
            }
        )

    # makes sure that all keys added to openai settings are valid keys
    def __setitem__(self, key, value):
        """
        Overrides set item method from dict so we can ensure only allowed keys get added.
        If an invalid key is tried to be added it will raise a KeyError with a message saying which key was invalid.

        :param key: the key the user wants to add to the dict
        :param value: the value the user wants to give the key
        """
        if key not in self._allowed_keys:
            raise KeyError(
                f"Invalid key: '{key}'. Only {', '.join(self._allowed_keys)} keys are allowed."
            )
        super().__setitem__(key, value)


class LLMOperations(Operations):
    """
    Subclass of Operations specifically designed for making requests for LLM Commands.
    """

    def __init__(
        self,
        try_limit: int,
        timeout: int,
        max_tokens: int,
        llm_settings: list[LLMSettings],
        workflow_type: str,
    ):
        """
        Initializes the LLMOperations

        :param try_limit: the number of times the user wants a request to be tried by the agent if it is not able to get a response on the first try
        :param timeout: the ammount of time the user wants the agent to allow for a response to be recieved from a model before requesting again
        :param max_tokens: the maximum number of words the user wants the model's response to be
        :param llm_settings: a list of LLMSettings objects defineing the settings for the different LLMs the user wants the agent to swwitch between
        :param workflow_type: the type of agentic workflow the user wants the agent to implement
        """
        super().__init__("llm", timeout)
        self.settings = {
            "try_limit": try_limit,
            "max_tokens": max_tokens,
            "llm_settings": llm_settings,
            "workflow": {"workflow_type": workflow_type},
        }

    def get_settings(self):
        """
        gets the settings for the LLM Operations
        """
        settings = super().get_settings()
        settings.update(self.settings)
        return settings

    @classmethod
    def load(cls, data_dict: dict):
        """
        takes in a python dictionary and identifies what type of LLM Command is being desribed by the deictionary
        appends an object of that type to a list of LLM Operations

        :params data_dict: python dictionary represeanting an LLM Command
        """
        llm_opts = cls(**data_dict["settings"])

        for command in data_dict["command_list"]:

            match command["message_type"]:
                case "standard":
                    initialized_command = Standard.init_from_dict(command)
                case "multimodal":
                    initialized_command = Multimodal.init_from_dict(command)
                case "assistant":
                    initialized_command = Assistant.init_from_dict(command)
                case "tool":
                    initialized_command = Tool.init_from_dict(command)
                case _:
                    raise Exception(
                        f"{command['command_name']} is not a valid browser command"
                    )

            llm_opts.append(initialized_command)

        return llm_opts
