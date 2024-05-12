"""
Tests for command.py
"""

import os
import shutil
import pytest
from agent.config.command import (
    Command,
    LLMCommand,
    _Standard,
    _Multimodal,
    _Assistant,
    BrowserCommand,
    _Navigate,
    BrowserFile,
    _FullPageScreenshot,
    _ElementScreenShot,
    _CollectNodes,
    _SaveHtml,
    _Sleep,
    _Click,
    move_file,
)

# Sample test data
standard_command_data = {"role": "user", "content": "Hello, world!"}


def test_command_init():
    """
    Function to test initialization of Command
    """
    command = Command("llm", "test_command", {"param": "value"})
    assert command.command_type == "llm"
    assert command.command_name == "test_command"
    assert command.params == {"param": "value"}


def test_command_to_dict():
    """
    Function to test conversion of Command to dictionary
    """
    command = Command("llm", "test_command", {"param": "value"})
    assert command.to_dict() == {
        "command_name": "test_command",
        "params": {"param": "value"},
    }


def test_command_to_json_string():
    """
    Function to test conversion of Command to JSON string
    """
    command = Command("llm", "test_command", {"param": "value"})
    assert (
        command.to_json_string()
        == '{"command_name": "test_command", "params": {"param": "value"}}'
    )


def test_llm_command_init():
    """
    Function to test initialization of LLM Command
    """
    llm_command = LLMCommand("standard", {"message": "value"})
    assert llm_command.command_type == "llm"
    assert llm_command.command_name == "standard"
    assert llm_command.params == {"message": "value"}


def test_llm_command_to_dict():
    """
    Function to test conversion of LLM Command to dictionary
    """
    llm_command = LLMCommand("standard", {"message_param": "value"})
    assert llm_command.to_dict() == {
        "message_type": "standard",
        "message": {"message_param": "value"},
    }


def test_browser_command_init():
    """
    Function to test initialization of Browser Command
    """
    browser_command = BrowserCommand("test_command", {"param": "value"})
    assert browser_command.command_type == "browser"
    assert browser_command.command_name == "test_command"
    assert browser_command.params == {"param": "value"}


def test_browser_command_to_dict():
    """
    Function to test conversion of Browser Command to dictionary
    """
    browser_command = BrowserCommand("test_command", {"param": "value"})
    assert browser_command.to_dict() == {
        "command_name": "test_command",
        "params": {"param": "value"},
    }


def test_browser_command_to_json_string():
    """
    Function to test conversion of Browser Command to JSON string
    """
    browser_command = BrowserCommand("test_command", {"param": "value"})
    assert (
        browser_command.to_json_string()
        == '{"command_name": "test_command", "params": {"param": "value"}}'
    )


def test_standard_init():
    """
    Function to test initialization of Standard LLM Command
    """
    standard_command = _Standard("user", "Hello, world!")
    assert standard_command.role == "user"
    assert standard_command.content == "Hello, world!"


def test_standard_init_from_dict():
    """
    Function to test initialization of Standard LLM Command from dictionary
    """
    standard_command = _Standard.init_from_dict(
        {"message": {"role": "user", "content": "Hello"}}
    )
    assert standard_command.role == "user"
    assert standard_command.content == "Hello"


def test_standard_set_role():
    """
    Function to test set role of Standard LLM Command
    """
    standard_command = _Standard("", "Hello, world!")
    standard_command.set_role("user")
    assert standard_command.role == "user"


def test_standard_set_content():
    """
    Function to test set content of Standard LLM Command
    """
    standard_command = _Standard("user", "")
    standard_command.set_content("Hello")
    assert standard_command.content == "Hello"


multimodal_command_data = {
    "message": {
        "role": "user",
        "content": [
            {"type": "text", "text": "Hello"},
            {
                "type": "image_url",
                "image_url": {"url": "https://example.com/image.jpg"},
            },
        ],
    }
}


def test_multimodal_init():
    """
    Function to test initialization of Multimodal LLM Command
    """
    multimodal_command = _Multimodal("user")
    assert multimodal_command.role == "user"
    assert not multimodal_command.content


def test_multimodal_init_from_dict():
    """
    Function to test initialization of Multimodal LLM Command from dictionary
    """
    multimodal_command = _Multimodal.init_from_dict(multimodal_command_data)
    assert multimodal_command.role == "user"
    assert len(multimodal_command.content) == 2
    assert multimodal_command.content[0]["type"] == "text"
    assert multimodal_command.content[0]["text"] == "Hello"
    assert multimodal_command.content[1]["type"] == "image_url"
    assert (
        multimodal_command.content[1]["image_url"]["url"]
        == "https://example.com/image.jpg"
    )


def test_multimodal_set_role():
    """
    Function to test set role of Multimodal LLM Command
    """
    multimodal_command = _Multimodal("")
    multimodal_command.set_role("user")
    assert multimodal_command.role == "user"


def test_multimodal_add_content_text():
    """
    Function to test add content of Multimodal LLM Command
    """
    multimodal_command = _Multimodal("user")
    multimodal_command.add_content("text", "Hello")
    assert len(multimodal_command.content) == 1
    assert multimodal_command.content[0]["type"] == "text"
    assert multimodal_command.content[0]["text"] == "Hello"


def test_multimodal_add_content_image_url():
    """
    Function to test add content of Multimodal LLM Command
    """
    multimodal_command = _Multimodal("user")
    multimodal_command.add_content("image_url", "https://example.com/image.jpg")
    assert len(multimodal_command.content) == 1
    assert multimodal_command.content[0]["type"] == "image_url"
    assert (
        multimodal_command.content[0]["image_url"]["url"]
        == "https://example.com/image.jpg"
    )


# Sample test data
assistant_command_data = {
    "message": {"role": "assistant", "content": "Hello, how can I assist you?"}
}


def test_assistant_init():
    """
    Function to test initialization of Assistant LLM Command
    """
    assistant_command = _Assistant("assistant", "Hello, how can I assist you?")
    assert assistant_command.role == "assistant"
    assert assistant_command.content == "Hello, how can I assist you?"


def test_assistant_init_from_dict():
    """
    Function to test initialization of Assistant LLM Command from dictionary
    """
    assistant_command = _Assistant.init_from_dict(assistant_command_data)
    assert assistant_command.role == "assistant"
    assert assistant_command.content == "Hello, how can I assist you?"


navigate_command_data = {"params": {"url": "https://example.com"}}


def test_navigate_init():
    """
    Function to test initialization of Navigate LLM Command
    """
    navigate_command = _Navigate("https://example.com")
    assert navigate_command.url == "https://example.com"
    assert navigate_command.command_type == "browser"
    assert navigate_command.command_name == "open_web_page"
    assert navigate_command.params == {"url": "https://example.com"}


def test_navigate_init_from_dict():
    """
    Function to test initialization of Navigate LLM Command from dictionary
    """
    navigate_command = _Navigate.init_from_dict(navigate_command_data)
    assert navigate_command.url == "https://example.com"
    assert navigate_command.command_type == "browser"
    assert navigate_command.command_name == "open_web_page"
    assert navigate_command.params == {"url": "https://example.com"}


def test_navigate_init_from_json_string():
    """
    Function to test initialization of Navigate LLM Command from JSON string
    """
    navigate_command_json = (
        '{"command_name": "open_web_page", "params": {"url": "https://example.com"}}'
    )
    navigate_command = _Navigate.init_from_json_string(navigate_command_json)
    assert navigate_command.url == "https://example.com"
    assert navigate_command.command_type == "browser"
    assert navigate_command.command_name == "open_web_page"
    assert navigate_command.params == {"url": "https://example.com"}


@pytest.fixture
def sample_browser_file():
    """
    Function to create sample browser file fixture for BrowserFile tests
    :return: BrowserFile object
    """
    return BrowserFile("save_file", {"param": "value"}, "test.txt", "snapshot")


# pylint: disable= W0621
def test_browser_file_initialization(sample_browser_file):
    """
    Function to test initialization of BrowserFile object
    :param sample_browser_file: A BrowserFile object
    """
    assert sample_browser_file.command_name == "save_file"
    assert sample_browser_file.params == {
        "param": "value",
        "snapshot_name": "snapshot",
    }
    assert sample_browser_file._file_name == "test.txt"
    assert sample_browser_file._snapshot_name == "snapshot"


def test_file_path(sample_browser_file):
    """
    Function to test the file path created for a BrowserFile object
    :param sample_browser_file: A BrowserFile object
    """
    assert sample_browser_file.file_path == "./resources/snapshots/snapshot/test.txt"


def test_exists(sample_browser_file, tmpdir):
    """
    Function to test a function that checks if a filepath for BrowserFile object exists
    :param sample_browser_file: A BrowserFile object
    :param tmpdir: A temporary directory
    """
    file_path = tmpdir.join("test.txt")
    with open(file_path, "w", encoding="utf-8") as f:
        f.write("Test content")
    sample_browser_file._file_name = "test.txt"
    sample_browser_file._snapshot_name = str(tmpdir)
    assert sample_browser_file.exists


def test_not_exists(sample_browser_file, tmpdir):
    """
    Function to test a function that checks if a filepath for BrowserFile object exists
    :param sample_browser_file: A BrowserFile object
    :param tmpdir: A temporary directory
    """
    sample_browser_file._file_name = "nonexistent.txt"
    sample_browser_file._snapshot_name = str(tmpdir)
    assert not sample_browser_file.exists


@pytest.fixture
def sample_full_page_screenshot():
    """
    Function to create sample full-page screenshot fixture for BrowserFile tests
    """
    return _FullPageScreenshot(90, "full_page_screenshot.png", "snapshot")


def test_full_page_screenshot_initialization(sample_full_page_screenshot):
    """
    Function to test initialization of FullPageScreenshot object
    :param sample_full_page_screenshot: A FullPageScreenshot object
    """
    assert sample_full_page_screenshot.command_name == "full_page_screenshot"
    assert sample_full_page_screenshot.params == {
        "quality": 90,
        "name": "full_page_screenshot.png",
        "snapshot_name": "snapshot",
    }
    assert sample_full_page_screenshot._file_name == "full_page_screenshot.png"
    assert sample_full_page_screenshot._snapshot_name == "snapshot"


def test_full_page_screenshot_file_path(sample_full_page_screenshot):
    """
    Function to test the file path created for a FullPageScreenshot object
    :param sample_full_page_screenshot: A FullPageScreenshot object
    """
    assert (
        sample_full_page_screenshot.file_path
        == "./resources/snapshots/snapshot/images/full_page_screenshot.png"
    )


def test_full_page_screenshot_init_from_dict():
    """
    Function to test initialization of FullPageScreenshot from dictionary
    """
    command_dict = {
        "command_name": "full_page_screenshot",
        "params": {
            "quality": 90,
            "name": "full_page_screenshot.png",
            "snapshot_name": "snapshot",
        },
    }
    full_page_screenshot = _FullPageScreenshot.init_from_dict(command_dict)
    assert full_page_screenshot.command_name == "full_page_screenshot"
    assert full_page_screenshot.params == {
        "quality": 90,
        "name": "full_page_screenshot.png",
        "snapshot_name": "snapshot",
    }
    assert full_page_screenshot._file_name == "full_page_screenshot.png"
    assert full_page_screenshot._snapshot_name == "snapshot"


def test_full_page_screenshot_init_from_json_string():
    """
    Function to test initialization of FullPageScreenshot from json string
    """
    command_json = (
        '{"command_name": "full_page_screenshot", '
        '"params": {"quality": 90, '
        '"name": "full_page_screenshot.png", '
        '"snapshot_name": "snapshot"}}'
    )
    full_page_screenshot = _FullPageScreenshot.init_from_json_string(command_json)
    assert full_page_screenshot.command_name == "full_page_screenshot"
    assert full_page_screenshot.params == {
        "quality": 90,
        "name": "full_page_screenshot.png",
        "snapshot_name": "snapshot",
    }
    assert full_page_screenshot._file_name == "full_page_screenshot.png"
    assert full_page_screenshot._snapshot_name == "snapshot"


@pytest.fixture
def sample_element_screenshot():
    """
    Function to create sample element screenshot fixture for BrowserFile tests
    """
    return _ElementScreenShot(
        2, "//div[@id='element']", "element_screenshot.png", "snapshot"
    )


def test_element_screenshot_initialization(sample_element_screenshot):
    """
    Function to test initialization of ElementScreenshot object
    :param sample_element_screenshot: An ElementScreenshot object
    """
    assert sample_element_screenshot.command_name == "element_screenshot"
    assert sample_element_screenshot.params == {
        "scale": 2,
        "name": "element_screenshot.png",
        "selector": "//div[@id='element']",
        "snapshot_name": "snapshot",
    }
    assert sample_element_screenshot._file_name == "element_screenshot.png"
    assert sample_element_screenshot._snapshot_name == "snapshot"


def test_element_screenshot_file_path(sample_element_screenshot):
    """
    Function to test the file path created for a ElementScreenshot object
    :param sample_element_screenshot: An ElementScreenshot object
    """
    assert (
        sample_element_screenshot.file_path
        == "./resources/snapshots/snapshot/images/element_screenshot.png"
    )


def test_element_screenshot_init_from_dict():
    """
    Function to test initialization of ElementScreenshot from dictionary
    """
    command_dict = {
        "command_name": "element_screenshot",
        "params": {
            "scale": 2,
            "name": "element_screenshot.png",
            "selector": "//div[@id='element']",
            "snapshot_name": "snapshot",
        },
    }
    element_screenshot = _ElementScreenShot.init_from_dict(command_dict)
    assert element_screenshot.command_name == "element_screenshot"
    assert element_screenshot.params == {
        "scale": 2,
        "name": "element_screenshot.png",
        "selector": "//div[@id='element']",
        "snapshot_name": "snapshot",
    }
    assert element_screenshot._file_name == "element_screenshot.png"
    assert element_screenshot._snapshot_name == "snapshot"


def test_element_screenshot_init_from_json_string():
    """
    Function to test initialization of ElementScreenshot from json string
    """
    command_json = (
        '{"command_name": "element_screenshot", '
        '"params": {"scale": 2, '
        '"name": "element_screenshot.png", '
        '"selector": "//div[@id=\'element\']", '
        '"snapshot_name": "snapshot"}}'
    )
    element_screenshot = _ElementScreenShot.init_from_json_string(command_json)
    assert element_screenshot.command_name == "element_screenshot"
    assert element_screenshot.params == {
        "scale": 2,
        "name": "element_screenshot.png",
        "selector": "//div[@id='element']",
        "snapshot_name": "snapshot",
    }
    assert element_screenshot._file_name == "element_screenshot.png"
    assert element_screenshot._snapshot_name == "snapshot"


@pytest.fixture
def sample_collect_nodes():
    """
    Function to create sample collect nodes fixture for BrowserFile tests
    """
    return _CollectNodes("//div[@class='container']", "snapshot")


def test_collect_nodes_initialization(sample_collect_nodes):
    """
    Function to test initialization of Collect Nodes object
    :param sample_collect_nodes: A Collect Nodes object
    """
    assert sample_collect_nodes.command_name == "collect_nodes"
    assert sample_collect_nodes.params == {
        "selector": "//div[@class='container']",
        "snapshot_name": "snapshot",
        "wait_ready": False,
    }
    assert sample_collect_nodes._file_name == "nodeData.json"
    assert sample_collect_nodes._snapshot_name == "snapshot"


def test_collect_nodes_file_path(sample_collect_nodes):
    """
    Function to test the file path created for a Collect Nodes object
    :param sample_collect_nodes: A Collect Nodes object
    """
    assert (
        sample_collect_nodes.file_path == "./resources/snapshots/snapshot/nodeData.json"
    )


def test_collect_nodes_init_from_dict():
    """
    Function to test initialization of Collect Nodes object from dictionary
    """
    command_dict = {
        "command_name": "collect_nodes",
        "params": {
            "selector": "//div[@class='container']",
            "snapshot_name": "snapshot",
            "wait_ready": False,
        },
    }
    collect_nodes = _CollectNodes.init_from_dict(command_dict)
    assert collect_nodes.command_name == "collect_nodes"
    assert collect_nodes.params == {
        "selector": "//div[@class='container']",
        "snapshot_name": "snapshot",
        "wait_ready": False,
    }
    assert collect_nodes._file_name == "nodeData.json"
    assert collect_nodes._snapshot_name == "snapshot"


def test_collect_nodes_init_from_json_string():
    """
    Function to test initialization of Collect Nodes object from json string
    """
    command_json = (
        '{"command_name": '
        '"collect_nodes", '
        '"params": {"selector": "//div[@class=\'container\']", '
        '"snapshot_name": "snapshot", "wait_ready": false}}'
    )
    collect_nodes = _CollectNodes.init_from_json_string(command_json)
    assert collect_nodes.command_name == "collect_nodes"
    assert collect_nodes.params == {
        "selector": "//div[@class='container']",
        "snapshot_name": "snapshot",
        "wait_ready": False,
    }
    assert collect_nodes._file_name == "nodeData.json"
    assert collect_nodes._snapshot_name == "snapshot"


@pytest.fixture
def sample_save_html():
    """
    Function to create sample save html fixture for BrowserFile tests
    :return: A Save HTML object
    """
    return _SaveHtml("snapshot")


def test_save_html_initialization(sample_save_html):
    """
    Function to test initialization of Save HTML object
    :param sample_save_html: A Save HTML object
    """
    assert sample_save_html.command_name == "save_html"
    assert sample_save_html.params == {"snapshot_name": "snapshot"}
    assert sample_save_html._file_name == "body.txt"
    assert sample_save_html._snapshot_name == "snapshot"


def test_save_html_init_from_dict():
    """
    Function to test initialization of Save HTML object from dictionary
    """
    command_dict = {
        "command_name": "save_html",
        "params": {"snapshot_name": "snapshot"},
    }
    save_html = _SaveHtml.init_from_dict(command_dict)
    assert save_html.command_name == "save_html"
    assert save_html.params == {"snapshot_name": "snapshot"}
    assert save_html._file_name == "body.txt"
    assert save_html._snapshot_name == "snapshot"


def test_save_html_init_from_json_string():
    """
    Function to test initialization of Save HTML object from json string
    """
    command_json = (
        '{"command_name": "save_html", "params": {"snapshot_name": "snapshot"}}'
    )
    save_html = _SaveHtml.init_from_json_string(command_json)
    assert save_html.command_name == "save_html"
    assert save_html.params == {"snapshot_name": "snapshot"}
    assert save_html._file_name == "body.txt"
    assert save_html._snapshot_name == "snapshot"


@pytest.fixture
def sample_sleep():
    """
    Function to create sample sleep fixture for BrowserFile tests
    """
    return _Sleep(5)


def test_sleep_initialization(sample_sleep):
    """
    Function to test initialization of Sleep object
    :param sample_sleep: A Sleep object
    """
    assert sample_sleep.command_name == "sleep"
    assert sample_sleep.params == {"seconds": 5}
    assert sample_sleep.seconds == 5


def test_sleep_init_from_dict():
    """
    Function to test initialization of Sleep object from dictionary
    """
    command_dict = {"command_name": "sleep", "params": {"seconds": 5}}
    sleep = _Sleep.init_from_dict(command_dict)
    assert sleep.command_name == "sleep"
    assert sleep.params == {"seconds": 5}
    assert sleep.seconds == 5


def test_sleep_init_from_json_string():
    """
    Function to test initialization of Sleep object from json string
    """
    command_json = '{"command_name": "sleep", "params": {"seconds": 5}}'
    sleep = _Sleep.init_from_json_string(command_json)
    assert sleep.command_name == "sleep"
    assert sleep.params == {"seconds": 5}
    assert sleep.seconds == 5


@pytest.fixture
def sample_click():
    """
    Function to create sample click fixture for BrowserFile tests
    :return: A Click object
    """
    return _Click("//button[@id='submit']", "xpath")


def test_click_initialization(sample_click):
    """
    Function to test initialization of Click object
    :param sample_click: A Click object
    """
    assert sample_click.command_name == "click"
    assert sample_click.params == {
        "selector": "//button[@id='submit']",
        "query_type": "xpath",
    }
    assert sample_click.selector == "//button[@id='submit']"
    assert sample_click.query_type == "xpath"


def test_click_init_from_dict():
    """
    Function to test initialization of Click object from dictionary
    """
    command_dict = {
        "command_name": "click",
        "params": {"selector": "//button[@id='submit']", "query_type": "xpath"},
    }
    click = _Click.init_from_dict(command_dict)
    assert click.command_name == "click"
    assert click.params == {"selector": "//button[@id='submit']", "query_type": "xpath"}
    assert click.selector == "//button[@id='submit']"
    assert click.query_type == "xpath"


def test_click_init_from_json_string():
    """
    Function to test initialization of Click object from json string
    """
    command_json = (
        '{"command_name": "click", '
        '"params": {"selector": "//button[@id=\'submit\']", '
        '"query_type": "xpath"}}'
    )
    click = _Click.init_from_json_string(command_json)
    assert click.command_name == "click"
    assert click.params == {"selector": "//button[@id='submit']", "query_type": "xpath"}
    assert click.selector == "//button[@id='submit']"
    assert click.query_type == "xpath"


class TestMoveFile:
    """
    Class to test move_file function
    """

    @pytest.fixture(scope="class")
    def snapshot_file(self):
        """
        Function to test initialization of SnapshotFile object
        :return: A SnapshotFile object
        """
        snapshot_path = os.path.join("resources", "snapshots", "snapshot", "body.txt")
        os.makedirs(os.path.dirname(snapshot_path), exist_ok=True)
        with open(snapshot_path, "w", encoding="utf-8") as file:
            file.write("Sample HTML content")

        return snapshot_path

    def test_create_snapshot_file(self, snapshot_file):
        """
        Function that tests the creation of a SnapshotFile object
        :param snapshot_file: A SnapshotFile object
        """
        assert os.path.exists(snapshot_file)

    def test_move_file(self):
        """
        Function that tests move_file function
        :return:
        """
        new_path = os.path.join("resources", "snapshots", "moved")
        os.makedirs(new_path, exist_ok=True)
        save_html_command = _SaveHtml("snapshot")
        move_file(save_html_command, new_path)
        new_file_path = os.path.join(new_path, "body.txt")
        assert os.path.exists(new_file_path)
        with open(new_file_path, "r", encoding="utf-8") as file:
            assert file.read() == "Sample HTML content"

    def test_delete_file(self):
        """
        Function that tests the deletion of a SnapshotFile object
        """
        resources_directory = os.path.join("resources")
        assert os.path.exists(resources_directory)
        shutil.rmtree(resources_directory)
        assert not os.path.exists(resources_directory)
