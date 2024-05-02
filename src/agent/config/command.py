"""
This Module is in charge of defining commands that are enacted by the agent
"""

import json
import typing
import os
from typing import Union


class Node:
    """
    Nodes are sections of an HTML page, often representing
    raw text or HTML elements. They contain data such as type and
    xpath that make it really easy to locate portions of a page
    for later use such as clicking.
    """

    def __init__(
        self, x_path: str, node_type: str, node_id: str, attributes: dict[str, str]
    ):
        """
        Initializes a Node

        :param x_path: the path to the node in the html document
        :param node_type: states the type of the node (element, text, ...)
        :param node_id: the unique id of the node in the document
        :param attributes: the html attributes (alt, id, ...)
        """

        self.x_path = x_path
        self.type = node_type
        self.id = node_id
        self.attributes = attributes

    @property
    def tag(self) -> str:
        """
        The tag of the Node if it is a html element
        :return: the tag name
        """
        if self.type != "Element":
            raise TypeError(
                f"only nodes of type element have tags. this node is of type {self.type}"
            )

        tail = os.path.split(self.x_path)[-1]

        if "[" in tail:
            tail = tail.split("[")[0]

        return tail

    @classmethod
    def from_json(cls, data_dict: dict[str, typing.Any]):
        """
        Converts json dictionaries to Node Objects
        :param data_dict: A dictionary representing the json content of the node
        :return:  object representing the json
        """
        return cls(
            data_dict["xpath"],
            data_dict["type"],
            data_dict["id"],
            data_dict["attributes"],
        )


class Command:
    """
    The base class for agent commands
    """

    def __init__(
        self, command_type: str, command_name: str, params: dict[str, typing.Any]
    ):
        """
        Initializes a parent command
        :param command_type: what does the agent request interaction with
        current options are llm and browser
        :param command_name: the name of the code
        :param params: the dictionary content of the param useful for conversion
        """

        self.command_type = command_type
        self.command_name = command_name
        self.params = params

    def to_dict(self) -> dict:
        """
        converts the command to a dictionary useful for conversion
        :return: the command as a dictionary
        """
        return {"command_name": self.command_name, "params": self.params}

    def to_json_string(self):
        """
        returns the dictionary as a json string
        :return: the command as a string
        """
        return json.dumps(self.to_dict())


# LLM Commands


class LLMCommand(Command):
    def __init__(self, message_type: str, message: dict[str, typing.Any]):
        super().__init__("llm", message_type, message)


class Standard(LLMCommand):
    def __init__(self, role: Union[str, None] = None, content: Union[str, None] = None):
        super().__init__("standard", {"role": role, "content": content})

    @classmethod
    def init_from_dict(cls, command_dict: dict[str, typing.Any]):
        return cls(command_dict["message"]["role"], command_dict["message"]["content"])

    def set_role(self, role: str):
        self.message["role"] = role

    def set_content(self, content: str):
        self.message["content"] = content


class Multimodal(LLMCommand):
    def __init__(
        self, role: Union[str, None] = None, content: Union[list[dict], None] = None
    ):
        super().__init__(
            "multimodal",
            {"role": role, "content": content if content is not None else []},
        )

    @classmethod
    def init_from_dict(cls, command_dict: dict[str, typing.Any]):
        return cls(command_dict["message"]["role"], command_dict["message"]["content"])

    def set_role(self, role: str):
        self.message["role"] = role

    def addContent(self, type: str, content: str):
        """
        Example usage:
        multimodal_command = Multimodal(role="user")

        multimodal_command.addContent("text", "This is some text.")
        multimodal_command.addContent("image_url", "https://example.com/image.jpg")
        """
        if type == "text":
            content_item = {"type": type, "text": content}
        elif type == "image_url":
            content_item = {"type": type, "image_url": content}
        else:
            raise ValueError(
                "Invalid content type. Type must be 'text' or 'image_url'."
            )

        self.message["content"].append(content_item)


class Assistant(LLMCommand):
    def __init__(self, role: Union[str, None] = None, content: Union[str, None] = None):
        super().__init__("standard", {"role": role, "content": content})

    @classmethod
    def init_from_dict(cls, command_dict: dict[str, typing.Any]):
        return cls(command_dict["message"]["role"], command_dict["message"]["content"])

    def set_role(self, role: str):
        self.message["role"] = role

    def set_content(self, content: str):
        self.message["content"] = content


class Tool(LLMCommand):
    def __init__(self, message: dict[str, typing.Any]):
        super().__init__("tool", message)

    @classmethod
    def init_from_dict(cls, command_dict: dict[str, typing.Any]):
        return cls(command_dict["message"])


# Browser Commands


class BrowserCommand(Command):
    """
    Commands for browser operations
    """

    def __init__(self, command_name: str, params: dict[str, typing.Any]):
        """
        Initializes a browser command

        :param command_name: the name of the browser command
        :param params: the properties of the command as a dictionary
        """

        super().__init__("browser", command_name, params)


class Navigate(BrowserCommand):
    """
    A command that navigates to the url present
    """

    def __init__(self, url: str):
        """
        Initializes the navigate command

        :param url: a hyperlink to the webpage that you
        wish to navigate too
        """

        self.url = url
        super().__init__("open_web_page", {"url": self.url})

    @classmethod
    def init_from_dict(cls, command_dict: dict[str, typing.Any]):
        """
        loads the navigate command from a python dictionary

        :param command_dict: the dictionary representation of the command
        :return: a Navigate object
        """
        return cls(command_dict["params"]["url"])

    @classmethod
    def init_from_json_string(cls, command: str):
        """
        loads the navigate command from a json string

        :param command: the string representation of the command
        :return: a Navigate object
        """
        command_dict = json.loads(command)
        return Navigate.init_from_dict(command_dict)


class BrowserFile(BrowserCommand):
    """
    A Browser command that saves a file
    """

    def __init__(
        self, command_name: str, params: dict, file_name: str, snap_shot_name: str
    ):
        """
        Initializes a browser file command

        :param command_name: the name of the command
        :param params: the properties of the command as a dictionary
        :param file_name: the name of the file being written to
        :param snap_shot_name: the name of the snapshot folder to save
        the data too
        """
        self.file_name = file_name
        self.snap_shot_name = snap_shot_name

        params["snap_shot_name"] = snap_shot_name

        super().__init__(command_name, params)

    @property
    def file_path(self) -> str:
        """
        Gets the path to the saved file

        :return: the saved file path
        """
        return os.path.join(
            "./resources", "snapshots", self.snap_shot_name, self.file_name
        )

    @property
    def exists(self) -> bool:
        """
        checks whether the file has been written

        :return: a boolean representing the files existence
        """
        return os.path.exists(self.file_path)


class FullPageScreenshot(BrowserFile):
    """
    A command that takes a screenshot of the entire page
    """

    def __init__(self, quality: int, name: str, snap_shot_name: str):
        """
        Initializes a FullPageScreenshot command

        :param quality: the screenshot quality. The higher, the better
        :param name: name of the screenshot file
        :param snap_shot_name: what snapshot folder to save too
        """

        super().__init__(
            "full_page_screenshot",
            {
                "quality": quality,
                "name": name,
            },
            name,
            snap_shot_name,
        )

        self.quality = quality

    @classmethod
    def init_from_dict(cls, command_dict: dict[str, typing.Any]):
        """
        loads the FullPageScreenshot command from a python dictionary

        :param command_dict: the dictionary representation of the command
        :return: a FullPageScreenshot object
        """

        return cls(
            command_dict["params"]["quality"],
            command_dict["params"]["name"],
            command_dict["params"]["snap_shot_name"],
        )

    @classmethod
    def init_from_json_string(cls, command: str):
        """
        loads the FullPageScreenshot command from a json string

        :param command: the string representation of the command
        :return: a FullPageScreenshot object
        """
        command_dict = json.loads(command)
        return Navigate.init_from_dict(command_dict)

    @property
    def file_path(self) -> str:
        """
        Gets the path to the saved file

        :return: the saved file path
        """

        return os.path.join(
            "./resources", "snapshots", self.snap_shot_name, "images", self.file_name
        )


class ElementScreenShot(BrowserFile):
    """
    A command that takes a screenshot of a particular element
    """

    def __init__(self, scale: int, selector: str, name: str, snap_shot_name: str):
        """
        Initializes a ElementScreenShot command

        :param scale: the size and quality of the image
        :param selector: the xpath selector used to capture the image
        :param name: the name of the image file that will be written
        :param snap_shot_name: the snapshot folder to save the image too
        """
        super().__init__(
            "element_screenshot",
            {
                "scale": scale,
                "name": name,
                "selector": selector,
                "snap_shot_name": snap_shot_name,
            },
            name,
            snap_shot_name,
        )

        self.scale = scale

    @classmethod
    def init_from_dict(cls, command_dict: dict[str, typing.Any]):
        """
        loads the ElementScreenShot command from a python dictionary

        :param command_dict: the dictionary representation of the command
        :return: a ElementScreenShot object
        """
        return cls(
            command_dict["params"]["scale"],
            command_dict["params"]["selector"],
            command_dict["params"]["name"],
            command_dict["params"]["snap_shot_name"],
        )

    @classmethod
    def init_from_json_string(cls, command: str):
        """
        loads the ElementScreenShot command from a json string

        :param command: the string representation of the command
        :return: a ElementScreenShot object
        """
        command_dict = json.loads(command)
        return Navigate.init_from_dict(command_dict)

    @property
    def file_path(self) -> str:
        """
        Gets the path to the saved file

        :return: the saved file path
        """
        return os.path.join(
            "./resources", "snapshots", self.snap_shot_name, "images", self.file_name
        )


class CollectNodes(BrowserFile):
    """
    This Command collects element nodes from a webpage
    """

    def __init__(self, selector: str, snap_shot_name: str, wait_ready=False):
        """
        Initializes a CollectNodes command

        :param selector: the css selector representing the section you
         want to extract
        :param snap_shot_name: the folder to write the data too
        :param wait_ready: whether to wait for the element to appear
        """
        super().__init__(
            "collect_nodes",
            {
                "wait_ready": wait_ready,
                "selector": selector,
                "snap_shot_name": snap_shot_name,
            },
            "nodeData.json",
            snap_shot_name,
        )

        self.wait_ready = wait_ready
        self.selector = selector

    @classmethod
    def init_from_dict(cls, command_dict: dict[str, typing.Any]):
        """
        loads the CollectNodes command from a python dictionary

        :param command_dict: the dictionary representation of the command
        :return: a CollectNodes object
        """
        return cls(
            command_dict["params"]["selector"],
            command_dict["params"]["snap_shot_name"],
            command_dict["params"]["wait_ready"],
        )

    @classmethod
    def init_from_json_string(cls, command: str):
        """
        Loads the CollectNodes command from a json string

        :param command: the string representation of the command
        :return: a CollectNodes object
        """
        command_dict = json.loads(command)
        return Navigate.init_from_dict(command_dict)

    def load_json(self, node_path: str | None = None) -> list[Node]:
        """
        Loads the collected file and return a list of nodes

        :param node_path: the path to the node file
        :return: a list of nodes
        """
        if not self.exists:
            raise FileNotFoundError("node json file does not exist")

        node_path = node_path if node_path else self.file_path

        with open(node_path, "r", encoding="utf-8") as f:
            node_json_data = json.load(f)

        node_list = []
        for node in node_json_data:
            node_list.append(Node.from_json(node))

        return node_list


class SaveHtml(BrowserFile):
    """
    Saves HTML to a file
    """

    def __init__(self, snap_shot_name: str):
        """
        Initializes a CollectNodes command

        :param snap_shot_name: the snapshot to save the html too
        """
        super().__init__(
            "save_html", {"snap_shot_name": snap_shot_name}, "body.txt", snap_shot_name
        )

    @classmethod
    def init_from_dict(cls, command_dict: dict[str, typing.Any]):
        """
        loads the SaveHtml command from a python dictionary

        :param command_dict: the dictionary representation of the command
        :return: a SaveHtml object
        """
        return cls(command_dict["params"]["snap_shot_name"])

    @classmethod
    def init_from_json_string(cls, command: str):
        """
        Loads the SaveHtml command from a json string

        :param command: the string representation of the command
        :return: a SaveHtml object
        """
        command_dict = json.loads(command)
        return Navigate.init_from_dict(command_dict)


class Sleep(BrowserCommand):
    """
    A command that instructs the browser to sleep for a duration
    """

    def __init__(self, seconds: int):
        """
        Initializes a Sleep command

        :param seconds: the sleep duration
        """
        super().__init__("sleep", {"seconds": seconds})

        self.seconds = seconds

    @classmethod
    def init_from_dict(cls, command_dict: dict[str, typing.Any]):
        """
        loads the Sleep command from a python dictionary

        :param command_dict: the dictionary representation of the command
        :return: a Sleep object
        """
        return cls(command_dict["params"]["seconds"])

    @classmethod
    def init_from_json_string(cls, command: str):
        """
        loads the Sleep command from a json string

        :param command: the string representation of the command
        :return: a Sleep object
        """
        command_dict = json.loads(command)
        return Navigate.init_from_dict(command_dict)


class Click(BrowserCommand):
    """
    A Command that clicks on a portion of the loaded website
    """

    def __init__(self, selector: str, query_type: str):
        """
        Initializes a click command

        :param selector: the value you are using to discriminate your selection
        :param query_type: the type of the selector ex: x_path
        """
        super().__init__("click", {"selector": selector, "query_type": query_type})
        self.selector = selector
        self.query_type = query_type

    @classmethod
    def init_from_dict(cls, command_dict: dict[str, typing.Any]):
        """
        Loads the Click command from a python dictionary

        :param command_dict: the dictionary representation of the command
        :return: a Click object
        """
        return cls(
            command_dict["params"]["selector"], command_dict["params"]["query_type"]
        )

    @classmethod
    def init_from_json_string(cls, command: str):
        """
        Loads the Click command from a json string

        :param command: the string representation of the command
        :return: a Click object
        """
        command_dict = json.loads(command)
        return Navigate.init_from_dict(command_dict)


def move_file(command: BrowserFile, new_path):
    """
    Helper function that moves files to different areas

    :param command: the command containing a file
    :param new_path: the path to where the file should be written
    """
    f_name = os.path.split(command.file_path)[-1]
    with open(command.file_path, "rb") as f:
        f_bytes = f.read()

    with open(os.path.join(new_path, f_name), "wb") as f2:
        f2.write(f_bytes)
