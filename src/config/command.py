import json
import typing


class Command:
    def __init__(
            self,
            command_type: str,
            command_name: str,
            params: dict[str, typing.Any]
    ):
        self.command_type = command_type
        self.command_name = command_name
        self.params = params

    def to_dict(self):
        return {
            "command_name": self.command_name,
            "params": self.params
        }

    def to_json_string(self):
        return json.dumps(self.to_dict())


class BrowserCommand(Command):
    def __init__(self, command_name: str, params: dict[str, typing.Any]):
        super().__init__(
            'config',
            command_name,
            params
        )


class Navigate(BrowserCommand):
    def __init__(self, url: str):
        self.url = url

        super().__init__(
            "open_web_page",
            {"url": self.url}
        )

    @classmethod
    def init_from_dict(cls, command_dict: dict[str, typing.Any]):
        return cls(command_dict["params"]["url"])

    @classmethod
    def init_from_json_string(cls, command: str):
        command_dict = json.loads(command)
        return Navigate.init_from_dict(command_dict)