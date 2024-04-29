import json
import typing
import os


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


class LLMCommand(Command):
    def __init__(self, message_type: str, message: dict[str, typing.Any]):
        super().__init__(
            'llm',
            message_type,
            message
        )

class Standard(LLMCommand):
    def __init__(self, message:  dict[str, typing.Any]):
        super().__init__(
            'standard', 
            message)
    
    @classmethod
    def init_from_dict(cls, command_dict: dict[str, typing.Any]):
        return cls(command_dict)

class Multimodal(LLMCommand):
    def __init__(self, message:  dict[str, typing.Any]):
        super().__init__(
            'multimodal', 
            message)
    
    @classmethod
    def init_from_dict(cls, command_dict: dict[str, typing.Any]):
        return cls(command_dict)

class Assistant(LLMCommand):
    def __init__(self, message:  dict[str, typing.Any]):
        super().__init__(
            'assistant', 
            message)
    
    @classmethod
    def init_from_dict(cls, command_dict: dict[str, typing.Any]):
        return cls(command_dict)

class Tool(LLMCommand):
    def __init__(self, message:  dict[str, typing.Any]):
        super().__init__(
            'tool', 
            message)
    
    @classmethod
    def init_from_dict(cls, command_dict: dict[str, typing.Any]):
        return cls(command_dict)

class BrowserCommand(Command):
    def __init__(self, command_name: str, params: dict[str, typing.Any]):
        super().__init__(
            'browser',
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


class BrowserFile(BrowserCommand):
    def __init__(self, command_name: str, params: dict, file_name: str, snap_shot_name: str):
        self.file_name = file_name
        self.snap_shot_name = snap_shot_name

        params["snap_shot_name"] = snap_shot_name

        super().__init__(
            command_name,
            params
        )

    @property
    def image_path(self) -> str:
        return os.path.join("./resources", self.snap_shot_name, self.file_name)

    @property
    def exists(self):
        return os.path.exists(self.image_path)


class FullPageScreenshot(BrowserFile):
    def __init__(self, quality: int, name: str, snap_shot_name: str):
        super().__init__(
            "full_page_screenshot",
            {
                "quality": quality,
                "name": name,
            },
            name,
            snap_shot_name
        )

        self.quality = quality

    @classmethod
    def init_from_dict(cls, command_dict: dict[str, typing.Any]):
        return cls(
            command_dict["params"]["quality"],
            command_dict["params"]["name"],
            command_dict["params"]["snap_shot_name"],
        )

    @classmethod
    def init_from_json_string(cls, command: str):
        command_dict = json.loads(command)
        return Navigate.init_from_dict(command_dict)


class ElementScreenShot(BrowserFile):

    def __init__(self, scale: int, selector: str, name: str, snap_shot_name: str):
        super().__init__(
            "element_screenshot",
            {
                "scale": scale,
                "name": name,
                "selector": selector,
                "snap_shot_name": snap_shot_name
            },
            name,
            snap_shot_name
        )

        self.scale = scale

    @classmethod
    def init_from_dict(cls, command_dict: dict[str, typing.Any]):
        return cls(
            command_dict["params"]["scale"],
            command_dict["params"]["selector"],
            command_dict["params"]["name"],
            command_dict["params"]["snap_shot_name"],
        )

    @classmethod
    def init_from_json_string(cls, command: str):
        command_dict = json.loads(command)
        return Navigate.init_from_dict(command_dict)


class CollectNodes(BrowserFile):

    def __init__(self, selector: str, snap_shot_name: str, wait_ready=False):
        super().__init__(
            "collect_nodes",
            {
                "wait_ready": wait_ready,
                "selector": selector,
                "snap_shot_name": snap_shot_name
            },
            "nodeData.json",
            snap_shot_name
        )

        self.wait_ready = wait_ready
        self.selector = selector

    @classmethod
    def init_from_dict(cls, command_dict: dict[str, typing.Any]):
        return cls(
            command_dict["params"]["selector"],
            command_dict["params"]["snap_shot_name"],
            command_dict["params"]["wait_ready"],
        )

    @classmethod
    def init_from_json_string(cls, command: str):
        command_dict = json.loads(command)
        return Navigate.init_from_dict(command_dict)


class SaveHtml(BrowserFile):

    def __init__(self, snap_shot_name: str):
        super().__init__(
            "save_html",
            {
                "snap_shot_name": snap_shot_name
            },
            "body.txt",
            snap_shot_name
        )

    @classmethod
    def init_from_dict(cls, command_dict: dict[str, typing.Any]):
        return cls(
            command_dict["params"]["snap_shot_name"]
        )

    @classmethod
    def init_from_json_string(cls, command: str):
        command_dict = json.loads(command)
        return Navigate.init_from_dict(command_dict)


class Sleep(BrowserCommand):

    def __init__(self, seconds: int):
        super().__init__(
            "sleep",
            {
                "seconds": seconds
            }
        )

        self.seconds = seconds

    @classmethod
    def init_from_dict(cls, command_dict: dict[str, typing.Any]):
        return cls(
            command_dict["params"]["seconds"]
        )

    @classmethod
    def init_from_json_string(cls, command: str):
        command_dict = json.loads(command)
        return Navigate.init_from_dict(command_dict)


class Click(BrowserCommand):

    def __init__(self, selector: str, query_type: str):
        super().__init__(
            "click",
            {
                "selector": selector,
                "query_type": query_type
            }
        )

        self.selector = selector
        self.query_type = query_type

    @classmethod
    def init_from_dict(cls, command_dict: dict[str, typing.Any]):
        return cls(
            command_dict["params"]["selector"],
            command_dict["params"]["query_type"]
        )

    @classmethod
    def init_from_json_string(cls, command: str):
        command_dict = json.loads(command)
        return Navigate.init_from_dict(command_dict)
