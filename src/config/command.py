import json
import typing
import os


class Node:
    def __init__(
            self,
            x_path: str,
            node_type: str,
            node_id: str,
            attributes: dict[str, str]
    ):

        self.x_path = x_path
        self.type = node_type
        self.id = node_id
        self.attributes = attributes

    @property
    def tag(self):
        if self.type != "Element":
            raise Exception(f"only nodes of type element have tags. this node is of type {self.type}")

        tail = os.path.split(self.x_path)[-1]

        if "[" in tail:
            tail = tail.split("[")[0]

        return tail

    @classmethod
    def from_json(cls, data_dict: dict[str, typing.Any]):

        return cls(
            data_dict["xpath"],
            data_dict["type"],
            data_dict["id"],
            data_dict["attributes"],
        )


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
    def file_path(self) -> str:
        return os.path.join("./resources", "snapshots", self.snap_shot_name, self.file_name)

    @property
    def exists(self):
        return os.path.exists(self.file_path)


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

    @property
    def file_path(self) -> str:
        return os.path.join("./resources", "snapshots", self.snap_shot_name, "images", self.file_name)


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

    @property
    def file_path(self) -> str:
        return os.path.join("./resources", "snapshots", self.snap_shot_name, "images", self.file_name)


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

    def load_json(self, node_path: str | None = None) -> list[Node]:
        if not self.exists:
            raise Exception("node json file does not exist")

        node_path = node_path if node_path else self.file_path

        with open(node_path) as f:
            node_json_data = json.load(f)

        node_list = []
        for node in node_json_data:
            node_list.append(Node.from_json(node))

        return node_list


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


def move_file(command: BrowserFile, new_path):
    f_name = os.path.split(command.file_path)[-1]
    with open(command.file_path, "rb") as f:
        f_bytes = f.read()

    with open(os.path.join(new_path, f_name), "wb") as f2:
        f2.write(f_bytes)
