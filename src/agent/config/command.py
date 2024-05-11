"""
This Module is in charge of defining commands that are enacted by the agent
"""

import base64
import json
import os
import typing
import uuid


class Node:
    """
    Nodes are sections of an HTML page, often representing
    raw text or HTML elements. They contain data such as type and
    xpath that make it really easy to locate portions of a page
    for later use, such as clicking.
    """

    def __init__(
            self,
            x_path: str,
            node_type: str,
            node_id: str,
            attributes: dict[str, str],
            css: dict[str, str] = None
    ):
        """
        Initializes a Node

        :param _x_path: The path to the node in the html document
        :param _node_type: states the type of the node (element, text, ...)
        :param _node_id: the unique id of the node in the document
        :param _attributes: the html attributes (alt, id, ...)
        :param _css: the css attributes that may be present in the node
        """

        self._x_path = x_path
        self._type = node_type
        self._id = node_id  # pylint: disable=invalid-name
        self._attributes = attributes
        self._css = css

    @property
    def tag(self) -> str:
        """
        The tag of the Node if it is a html element
        :return: the tag name
        """
        if self._type != "Element":
            raise TypeError(
                f"only nodes of type element have tags. this node is of type {self._type}"
            )

        tail = os.path.split(self._x_path)[-1]

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
            data_dict["css_styles"] if data_dict["css_styles"] else None
        )


class BrowserImage:

    def __init__(self, image_path: str):
        self._image_path = image_path

    @property
    def byte_string(self):
        with open(self._image_path, "rb") as file:
            return base64.b64encode(file.read()).decode("utf-8")


class BrowserHtml:

    def __init__(self, html_path: str):
        self._html_path = html_path

    def __str__(self):
        with open(self._html_path, "r") as f:
            return f.read()


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
    """
    Commands for LLM operations
    """

    def __init__(self, message_type: str, message: dict[str, typing.Any]):
        """
        Initializes and LLM command
        :param message_type: type of llm messages
        :param message: the properties if the command is a dictionary
        """
        super().__init__("llm", message_type, message)
        self.message_type = message_type

    def to_dict(self) -> dict:
        return {"message_type": self.message_type, "message": self.params}


class Standard(LLMCommand):
    """
    A Standard LLM command, only text input
    """

    def __init__(self, role: str, content: str):
        """
        Initialize a Standard LLM command with optional parameters

        :param role: The role of the speaker (user).
        :param content: The content of the message
        """
        self.role = role
        self.content = content
        super().__init__("standard", {"role": self.role, "content": self.content})

    @classmethod
    def init_from_dict(cls, command_dict: dict[str, typing.Any]):
        """
        loads Standard LLM command from a python dictionary

        :param command_dict: the dictionary representation of the command
        :return: a Standard LLM command object
        """
        return cls(command_dict["message"]["role"], command_dict["message"]["content"])

    def set_role(self, role: str):
        """
        set the role of the command after it is initialized

        :param role: the tole that will be set for the command object
        """
        self.role = role

    def set_content(self, content: str):
        """
        set the content of the command

        :param content: the content of the message that will be set for the command object
        """
        self.content = content


class Multimodal(LLMCommand):
    """
    A Multimodal LLM command can take input of a text and image type
    """

    def __init__(self, role: str):
        """
        Initialize a Multimodal LLM command

        :param role: generally will be user
        """
        self.content = []
        self.role = role
        super().__init__(
            "multimodal",
            {"role": self.role, "content": self.content},
        )

    @classmethod
    def init_from_dict(cls, command_dict: dict[str, typing.Any]):
        """
        loads Multimodal LLM command from a python dictionary

        :param command_dict: the dictionary representation of the command
        :return: a Multimodal LLM command object
        """
        multimodal_content = cls(command_dict["message"]["role"])
        for content in command_dict["message"]["content"]:
            if content["type"] == "text":
                multimodal_content.add_content(content["type"], content["text"])
            else:
                multimodal_content.add_content(
                    content["type"], content["image_url"]["url"]
                )
        return multimodal_content

    def set_role(self, role: str):
        """
        set the role of the command after it is initialized

        :param role: the tole that will be set for the command object
        """
        self.role = role

    def add_content(self, ctype: str, content: str, b64=False):
        """
        Allows user to add message content of different types
        after initializing the Multimodal LLM command object

        :param b64: Whether the image needs to be base64 encoded
        :param ctype: the type of the message content the user is adding, either text or image_url
        :param content: the actual content that corresponds to the provided type
        """
        content_item = {"type": ctype}
        if ctype == "text":
            content_item["text"] = content
        elif ctype == "image_url":
            if b64:
                with open(content, "rb") as image_file:
                    encoded = base64.b64encode(image_file.read()).decode("utf-8")
                content = f"data:image/{encoded};base64,{encoded}"
            content_item["image_url"] = {"url": content}
        else:
            raise ValueError(
                "Invalid content type. Type must be 'text' or 'image_url'."
            )

        self.content.append(content_item)


class Assistant(LLMCommand):
    """
    An Assistant LLM command, which represents an assistant response in a conversation with a user.
    """

    def __init__(self, role: str, content: str):
        """
        Initialize an Assistant LLM command

        :param role: Assistant
        :param content: The content of the message
        """
        self.role = role
        self.content = content
        super().__init__("assistant", {"role": self.role, "content": self.content})

    @classmethod
    def init_from_dict(cls, command_dict: dict[str, typing.Any]):
        """
        loads Assistant LLM command from a python dictionary

        :param command_dict: the dictionary representation of the command
        :return: an Assistant LLM command object
        """
        return cls(command_dict["message"]["role"], command_dict["message"]["content"])


class Tool(LLMCommand):
    """
    TODO
    A Tool LLM command
    """

    def __init__(self, message: dict[str, typing.Any]):
        """
        Initialize a Tool LLM command

        :param message: The tool message's data as a dictionary
        """
        super().__init__("tool", message)

    @classmethod
    def init_from_dict(cls, command_dict: dict[str, typing.Any]):
        """
        loads Tool LLM command from a python dictionary

        :param command_dict: the dictionary representation of the command
        :return: an Assistant LLM command object
        """
        return cls(command_dict["message"])


# Browser Commands


class BrowserCommand(Command):
    """
    Commands for browser operations
    """

    def __init__(self, command_name: str, params: dict[str, typing.Any]):
        """
        Initializes a browser command

        :param command_name: The name of the browser commands
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

        :param url: A hyperlink to the webpage that you
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
            self, command_name: str, params: dict, file_name: str, snapshot_name: str
    ):
        """
        Initializes a browser file command

        :param command_name: The name of the command
        :param params: the properties of the command as a dictionary
        :param file_name: the name of the file being written to
        :param snapshot_name: the name of the snapshot folder to save
        the data too
        """
        self.file_name = file_name
        self.snapshot_name = snapshot_name

        params["snapshot_name"] = snapshot_name

        super().__init__(command_name, params)

    @property
    def file_path(self) -> str:
        """
        Gets the path to the saved file

        :return: The saved file path
        """
        return os.path.join(
            "./resources", "snapshots", self.snapshot_name, self.file_name
        )

    @property
    def exists(self) -> bool:
        """
        checks whether the file has been written

        :return: a boolean representing the file's existence
        """
        return os.path.exists(self.file_path)


class FullPageScreenshot(BrowserFile):
    """
    A command that takes a screenshot of the entire page
    """

    def __init__(self, quality: int, name: str, snapshot_name: str):
        """
        Initializes a FullPageScreenshot command

        :param quality: The screenshot quality.
        The higher, the better
        :param name: name of the screenshot file
        :param snapshot_name: what snapshot folder to save too
        """

        super().__init__(
            "full_page_screenshot",
            {
                "quality": quality,
                "name": name,
            },
            name,
            snapshot_name,
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
            command_dict["params"]["snapshot_name"],
        )

    @classmethod
    def init_from_json_string(cls, command: str):
        """
        loads the FullPageScreenshot command from a json string

        :param command: the string representation of the command
        :return: a FullPageScreenshot object
        """
        command_dict = json.loads(command)
        return FullPageScreenshot.init_from_dict(command_dict)

    @property
    def file_path(self) -> str:
        """
        Gets the path to the saved file

        :return: The saved file path
        """

        return os.path.join(
            "./resources", "snapshots", self.snapshot_name, "images", self.file_name
        )


class ElementScreenShot(BrowserFile):
    """
    A command that takes a screenshot of a particular element
    """

    def __init__(self, scale: int, selector: str, name: str, snapshot_name: str):
        """
        Initializes a ElementScreenShot command

        :param scale: The size and quality of the image
        :param selector: the xpath selector used to capture the image
        :param name: the name of the image file that will be written in
        :param snapshot_name: the snapshot folder to save the image too
        """
        super().__init__(
            "element_screenshot",
            {
                "scale": scale,
                "name": name,
                "selector": selector,
                "snapshot_name": snapshot_name,
            },
            name,
            snapshot_name,
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
            command_dict["params"]["snapshot_name"],
        )

    @classmethod
    def init_from_json_string(cls, command: str):
        """
        loads the ElementScreenShot command from a json string

        :param command: the string representation of the command
        :return: a ElementScreenShot object
        """
        command_dict = json.loads(command)
        return ElementScreenShot.init_from_dict(command_dict)

    @property
    def file_path(self) -> str:
        """
        Gets the path to the saved file

        :return: The saved file path
        """
        return os.path.join(
            "./resources", "snapshots", self.snapshot_name, "images", self.file_name
        )


class CollectNodes(BrowserFile):
    """
    This Command collects element nodes from a webpage
    """

    def __init__(self, selector: str, snapshot_name: str, wait_ready=False):
        """
        Initializes a CollectNodes command

        :param selector: The css selector that represents the section you want to extract
        :param snapshot_name: the folder to write the data to
        :param wait_ready: whether to wait for the element to appear
        """
        super().__init__(
            "collect_nodes",
            {
                "wait_ready": wait_ready,
                "selector": selector,
                "snapshot_name": snapshot_name,
            },
            "nodeData.json",
            snapshot_name,
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
            command_dict["params"]["snapshot_name"],
            command_dict["params"]["wait_ready"],
        )

    @classmethod
    def init_from_json_string(cls, command: str):
        """
        Loads the CollectNodes command from a json string

        :param command: The string representation of the command
        :return: a CollectNodes object
        """
        command_dict = json.loads(command)
        return CollectNodes.init_from_dict(command_dict)

    def load_json(self, node_path: str | None = None) -> list[Node]:
        """
        Loads the collected file and return a list of nodes

        :param node_path: The path to the node files
        :return: a list of nodes
        """
        if not self.exists:
            raise FileNotFoundError("node json file does not exist")

        node_path = node_path if node_path else self.file_path

        with open(node_path, "r", encoding="utf-8") as file:
            node_json_data = json.load(file)

        node_list = []
        for node in node_json_data:
            node_list.append(Node.from_json(node))

        return node_list


class SaveHtml(BrowserFile):
    """
    Saves HTML to a file
    """

    def __init__(self, snapshot_name: str):
        """
        Initializes a CollectNodes command

        :param snapshot_name: The snapshot to save the html too
        """
        super().__init__(
            "save_html", {"snapshot_name": snapshot_name}, "body.txt", snapshot_name
        )

    @classmethod
    def init_from_dict(cls, command_dict: dict[str, typing.Any]):
        """
        loads the SaveHtml command from a python dictionary

        :param command_dict: the dictionary representation of the command
        :return: a SaveHtml object
        """
        return cls(command_dict["params"]["snapshot_name"])

    @classmethod
    def init_from_json_string(cls, command: str):
        """
        Loads the SaveHtml command from a json string

        :param command: The string representation of command
        :return: a SaveHtml object
        """
        command_dict = json.loads(command)
        return SaveHtml.init_from_dict(command_dict)


class Sleep(BrowserCommand):
    """
    A command that instructs the browser to sleep for a duration
    """

    def __init__(self, seconds: int):
        """
        Initializes a Sleep command

        :param seconds: The sleep duration
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
        return Sleep.init_from_dict(command_dict)


class Click(BrowserCommand):
    """
    A Command that clicks on a portion of the loaded website
    """

    def __init__(self, selector: str, query_type: str):
        """
        Initializes a click command

        :param selector: The value you are using to discriminate your selection
        :param query_type: the type of the selector ex: x_path
        """
        super().__init__("click", {"selector": selector, "query_type": query_type})
        self.selector = selector
        self.query_type = query_type

    @classmethod
    def init_from_dict(cls, command_dict: dict[str, typing.Any]):
        """
        Loads the Click command from a python dictionary

        :param command_dict: The dictionary representation of the command
        :return: a Click object
        """
        return cls(
            command_dict["params"]["selector"], command_dict["params"]["query_type"]
        )

    @classmethod
    def init_from_json_string(cls, command: str):
        """
        Loads the Click command from a json string

        :param command: The string representation of the command
        :return: a Click object
        """
        command_dict = json.loads(command)
        return Click.init_from_dict(command_dict)


def move_file(command: BrowserFile, new_path):
    """
    Helper function that moves files to different areas

    :param command: The command containing a file
    :param new_path: the path to where the file should be written
    """
    f_name = os.path.split(command.file_path)[-1]
    with open(command.file_path, "rb") as file:
        f_bytes = file.read()

    with open(os.path.join(new_path, f_name), "wb") as file2:
        file2.write(f_bytes)


class IterateHtml(BrowserCommand):
    """
    Saves snapshots of a webpage over points in time
    """

    def __init__(self,
                 iterate_limit: int,
                 save_html: bool,
                 save_node: bool,
                 save_full_page_image: bool,
                 pause_time: int = 5000,
                 starting_snapshot: int = 0,
                 snapshot_name: str = "snapshot"):
        """
        Initializes an Iterate Html object

        :param iterate_limit: the max amount of snapshot iterations that can occur
        :param pause_time: the time to sleep between each iteration
        :param starting_snapshot: the snapshot number to start with
        :param snapshot_name: the name of the snapshot directories
        :param save_html: saves the html of the webpage at that point in time
        :param save_node: save the nodes of the snapshot at that time
        :param save_full_page_image: save a screenshot of the entire webpage at that time
        """

        uid_str = "bench_" + str(uuid.uuid4()).replace("-", "")
        self._folder_prefix = snapshot_name + "_" + uid_str
        self._has_nodes = save_node
        self._has_html = save_html
        self._has_image = save_full_page_image

        super().__init__(
            command_name="iterate_html",
            params={
                "iter_limit": iterate_limit,
                "pause_time": pause_time,
                "starting_snapshot": starting_snapshot,
                "snapshot_name": self._folder_prefix,
                "save_html": save_html,
                "save_node": save_node,
                "save_full_page_image": save_full_page_image
            })

    @property
    def exists(self) -> bool:
        """
        whether a snapshots exist or not
        :return:
        """

        return len(self) > 0

    def _collect_resources(self) -> filter:
        dir_list = os.listdir("./resources/snapshots")
        return filter(lambda x: x.startswith(self._folder_prefix), dir_list)

    def __len__(self) -> int:
        """
        :return: Returns the amount of snapshots takes
        """
        if not os.path.isdir("./resources/snapshots"):
            raise NotADirectoryError("snapshots have not been saved")

        return len(list(self._collect_resources()))

    def __getitem__(self, item: int):
        """
        TODO: Make a response obejct with all the specific types present
        update node map
        finish the this method and make this iterable
        based
        :param item: the index of the item you wish to acquire
        :return:
        """

        if len(self) < 0:
            raise NotADirectoryError("snapshots have not been saved")

        return list(self._collect_resources())[item]

    @classmethod
    def init_from_dict(cls, command_dict: dict[str, typing.Any]):
        """
        Loads the Iterate Html object from a dictionary

        :param command_dict:
        :return: an IterateHtml object
        """
        return cls(
            command_dict["iter_limt"],
            command_dict["save_html"],
            command_dict["save_node"],
            command_dict["save_full_page_image"],
            pause_time=command_dict["pause_time"],
            starting_snapshot=command_dict["starting_snapshot"],
            snapshot_name=command_dict["snapshot_name"]
        )

    @classmethod
    def init_from_json_string(cls, command: str):
        """
        Loads the Iterate Html command from a json string

        :param command: The string representation of the command
        :return: a IterateHtml Object
        """
        command_dict = json.loads(command)
        return Click.init_from_dict(command_dict)
