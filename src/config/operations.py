import json
import typing
from command import Command, Navigate


class Operations(list):

    def __init__(
            self,
            op_type: str,
            timeout=None | int,
    ):
        if not (timeout and (0 <= timeout <= 32767)):
            raise Exception(f"timeout must be between 0 and 32767, got {timeout}")

        super().__init__()

        self.op_type = op_type
        self.timeout = timeout

    def append(self, command: Command):

        if command.command_type == self.op_type:
            super().append(command)
        else:
            raise Exception(f"cannot append command of type {self.op_type}")

    def get_settings(self) -> dict:
        return {"timeout": self.timeout} if self.timeout else {}

    def to_dict(self) -> dict[str, typing.Any]:
        op_dict = {
            "type": self.op_type,
            "settings": self.get_settings(),
            "command_list": [com.to_dict() for com in self]
        }

        return op_dict

    def to_json_string(self) -> str:
        return json.dumps(self.to_dict())


class BrowserOperations(Operations):

    def __init__(self,
                 headless: bool = False,
                 timeout=None | int):
        super().__init__("config", timeout)

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
                case _:
                    raise Exception(f"{command['command_name']} is not a valid browser command")

            browser_opts.append(initialized_command)
