"""
Tests for operation.py
"""

import pytest
from agent.config.operation import (
    Operation,
    _BrowserOperations,
    LLMSettings,
    OpenAISettings,
    LLMOperations,
)
from agent.config.command import Command, _Navigate


# pylint: disable= W0621
@pytest.fixture
def operation():
    """
    Function that creates the operation fixture for operation tests
    :return: An operation object
    """
    return Operation("test_operation")


def test_operation_creation(operation):
    """
    Function that tests the creation of a new operation object
    :param operation:
    """
    assert operation.op_type == "test_operation"


def test_operation_append_valid_command(operation):
    """
    Function that tests the appending of a valid operation object
    :param operation: An operation object
    """
    command = Command("test_operation", "command_name", {"params_key": "params_value"})
    operation.append(command)
    assert len(operation) == 1


def test_operation_to_dict(operation):
    """
    Function that tests the conversion of a valid operation object
    :param operation: An operation object
    """
    command1 = Command("test_operation", "command_name", {"params_key": "params_value"})
    command2 = Command("test_operation", "command_name", {"params_key": "params_value"})
    operation.append(command1)
    operation.append(command2)
    expected_dict = {
        "type": "test_operation",
        "settings": {},
        "command_list": [command1.to_dict(), command2.to_dict()],
    }
    assert operation.to_dict() == expected_dict


def test_operation_to_json_string(operation):
    """
    Function that tests the conversion of a valid operation object to JSON string
    :param operation: An operation object
    """
    command1 = Command("test_operation", "command_name", {"params_key": "params_value"})
    command2 = Command("test_operation", "command_name", {"params_key": "params_value"})
    operation.append(command1)
    operation.append(command2)
    expected_json_string = (
        '{"type": "test_operation", '
        '"settings": {}, '
        '"command_list": [{"command_name": "command_name", '
        '"params": {"params_key": "params_value"}}, {"command_name": '
        '"command_name", "params": {"params_key": "params_value"}}]}'
    )
    assert operation.to_json_string() == expected_json_string


@pytest.fixture
def browser_operation():
    """
    Function that creates a browser operation fixture for operation tests
    :return: A BrowserOperations object
    """
    return _BrowserOperations()


def test_browser_operation_creation(browser_operation):
    """
    Function that tests the creation of a new browser operation object
    :param browser_operation: A BrowserOperations object
    """
    assert browser_operation.op_type == "browser"
    assert browser_operation.headless is False


def test_browser_operation_append_valid_command(browser_operation):
    """
    Function that tests the appending of a valid browser operation object
    :param browser_operation: A BrowserOperations object
    """
    command = _Navigate("https://example.com")
    browser_operation.append(command)
    assert len(browser_operation) == 1


def test_get_settings(browser_operation):
    """
    Function that tests the getting settings of a browser operation object
    :param browser_operation: A BrowserOperations object
    """
    assert browser_operation.get_settings() == {"headless": False}


def test_get_settings_with_headless():
    """
    Function that tests the getting settings of a
    browser operation object when headless is True
    """
    browser_op = _BrowserOperations(headless=True)
    assert browser_op.get_settings() == {"headless": True}


def test_browser_operation_load_fps(browser_operation):
    """
    Function that tests the loading of a full page screenshot command
    :param browser_operation: A BrowserOperations object
    """
    data_dict = {
        "type": "browser",
        "settings": {"headless": True},
        "command_list": [
            {
                "command_name": "full_page_screenshot",
                "params": {
                    "quality": 90,
                    "name": "fullpage.png",
                    "snap_shot_name": "s1",
                },
            }
        ],
    }
    browser_op = browser_operation.load(data_dict)
    assert len(browser_op) == 1


def test_browser_operation_load_owp(browser_operation):
    """
    Function that tests the loading of an open webpage command
    :param browser_operation: A BrowserOperations object
    """
    data_dict = {
        "type": "browser",
        "settings": {"headless": True},
        "command_list": [
            {
                "command_name": "open_web_page",
                "params": {"url": "https://www.centerramd.live/"},
            }
        ],
    }
    browser_op = browser_operation.load(data_dict)
    assert len(browser_op) == 1


def test_browser_operation_load_es(browser_operation):
    """
    Function that tests the loading of an element screenshot command
    :param browser_operation: A BrowserOperations object
    """
    data_dict = {
        "type": "browser",
        "settings": {"headless": True},
        "command_list": [
            {
                "command_name": "element_screenshot",
                "params": {
                    "scale": 2,
                    "name": "element.png",
                    "selector": "(//img[@class='thumb-image loaded'])[5]",
                    "snap_shot_name": "s1",
                },
            }
        ],
    }
    browser_op = browser_operation.load(data_dict)
    assert len(browser_op) == 1


def test_browser_operation_load_cn(browser_operation):
    """
    Function that tests the loading of a collect nodes command
    :param browser_operation: A BrowserOperations object
    """
    data_dict = {
        "type": "browser",
        "settings": {"headless": True},
        "command_list": [
            {
                "command_name": "collect_nodes",
                "params": {
                    "selector": "body",
                    "wait_ready": "false",
                    "snap_shot_name": "s1",
                },
            }
        ],
    }
    browser_op = browser_operation.load(data_dict)
    assert len(browser_op) == 1


def test_browser_operation_load_save(browser_operation):
    """
    Function that tests the loading of a save html command
    :param browser_operation: A BrowserOperations object
    """
    data_dict = {
        "type": "browser",
        "settings": {"headless": True},
        "command_list": [
            {"command_name": "save_html", "params": {"snap_shot_name": "s1"}}
        ],
    }
    browser_op = browser_operation.load(data_dict)
    assert len(browser_op) == 1


def test_browser_operation_load_sleep(browser_operation):
    """
    Function that tests the loading of a sleep command
    :param browser_operation: A BrowserOperations object
    """
    data_dict = {
        "type": "browser",
        "settings": {"headless": True},
        "command_list": [{"command_name": "sleep", "params": {"seconds": 1}}],
    }
    browser_op = browser_operation.load(data_dict)
    assert len(browser_op) == 1


def test_browser_operation_load_click(browser_operation):
    """
    Function that tests the loading of a click command
    :param browser_operation: A BrowserOperations object
    """
    data_dict = {
        "type": "browser",
        "settings": {"headless": True},
        "command_list": [
            {
                "command_name": "click",
                "params": {
                    "selector": "some_selector",
                    "query_type": "some_query_type",
                },
            }
        ],
    }
    browser_op = browser_operation.load(data_dict)
    assert len(browser_op) == 1


def test_browser_operation_load_with_invalid_command(browser_operation):
    """
    Function that tests the loading of an invalid command
    """
    data_dict = {
        "type": "browser",
        "settings": {"headless": False},
        "command_list": [
            {"command_name": "invalid_command"},
        ],
    }
    with pytest.raises(TypeError):
        browser_operation.load(data_dict)


@pytest.fixture
def llm_settings():
    """
    Function that creates an LLMSettings fixture for LLMSettings tests
    :return: An LLMSettings object
    """
    return LLMSettings("OpenAI", "api_key")


def test_llm_settings_initialization():
    """
    Function that tests the initialization of an LLMSettings object
    """
    llm_settings = LLMSettings("OpenAI", "api_key")
    assert llm_settings["name"] == "OpenAI"
    assert llm_settings["api_key"] == "api_key"


def test_llm_settings_invalid_name():
    """
    Function that tests the initialization of an LLMSettings object with an invalid name
    """
    with pytest.raises(TypeError):
        LLMSettings(None, "api_key")


def test_llm_settings_invalid_api_key():
    """
    Function that tests the initialization of an LLMSettings object with an invalid api key
    """
    with pytest.raises(TypeError):
        LLMSettings("OpenAI", None)


def test_llm_settings_invalid_type_name():
    """
    Function that tests the initialization of an LLMSettings object with an invalid type name
    """
    with pytest.raises(TypeError):
        # pylint: disable=E1123
        LLMSettings(123, "api_key")  # type: ignore


def test_llm_settings_invalid_type_api_key():
    """
    Function thst tests the initialization of an LLMSettings object with an invalid type api key
    """
    with pytest.raises(TypeError):
        # pylint: disable=E1123
        LLMSettings("OpenAI", 123)  # type: ignore


@pytest.fixture
def openai_settings():
    """
    Function that creates an OpenAISettings fixture for OpenAISettings tests
    :return: An OpenAISettings object
    """
    return OpenAISettings("OpenAI", "api_key", "gpt-3.5-turbo", 0.7)


def test_openai_settings_initialization(openai_settings):
    """
    Function that tests the initialization of an OpenAISettings object
    :param openai_settings: An OpenAISettings object
    """
    assert openai_settings["name"] == "OpenAI"
    assert openai_settings["api_key"] == "api_key"
    assert openai_settings["model"] == "gpt-3.5-turbo"
    assert openai_settings["temperature"] == 0.7


def test_openai_settings_invalid_model():
    """
    Function that tests the initialization of an OpenAISettings object with an invalid model
    """
    with pytest.raises(TypeError):
        # pylint: disable=E1123
        OpenAISettings("OpenAI", "api_key", 123, 0.7)  # type: ignore


def test_openai_settings_invalid_temperature():
    """
    Function that tests the initialization of an OpenAISettings object with an invalid temperature
    """
    with pytest.raises(TypeError):
        # pylint: disable=E1123
        OpenAISettings("OpenAI", "api_key", "gpt-3.5-turbo", "temperature")  # type: ignore


@pytest.fixture
def llm_operations():
    """
    Function that creates an LLMOperations fixture for LLMOperations tests
    :return: An LLMOperations object
    """
    llm_settings = [LLMSettings("OpenAI", "api_key")]
    return LLMOperations(3, 30, 1000, llm_settings, "workflow_type")


def test_llm_operations_initialization(llm_operations):
    """
    Function that tests the initialization of an LLMOperations object
    :param llm_operations: An LLMOperations object
    """
    assert llm_operations.settings["try_limit"] == 3
    assert llm_operations.settings["max_tokens"] == 1000
    assert len(llm_operations.settings["llm_settings"]) == 1
    assert llm_operations.settings["workflow"]["workflow_type"] == "workflow_type"


def test_llm_operations_get_settings(llm_operations):
    """
    Function that tests the get settings function of an LLMOperations object
    :param llm_operations: An LLMOperations object
    """
    settings = llm_operations.get_settings()
    assert settings["try_limit"] == 3
    assert settings["max_tokens"] == 1000
    assert len(settings["llm_settings"]) == 1
    assert settings["workflow"]["workflow_type"] == "workflow_type"


def test_load_llm_operation_standard(llm_operations):
    """
    Function that tests the loading of a Standard LLM command  object
    :param llm_operations: An LLMOperations object
    """
    data_dict = {
        "type": "llm",
        "settings": {
            "try_limit": 3,
            "timeout": 30,
            "max_tokens": 300,
            "llm_settings": [
                {
                    "name": "OpenAI",
                    "api_key": "someKey",
                    "model": "gpt-3.5-turbo",
                    "temperature": 1.1,
                }
            ],
            "workflow": {"workflow_type": "chat_completion"},
        },
        "command_list": [
            {
                "message_type": "standard",
                "message": {"role": "user", "content": "You are a helpful assistant."},
            }
        ],
    }
    llm_op = llm_operations.load(data_dict)
    assert len(llm_op) == 1


def test_load_llm_operation_multimodal(llm_operations):
    """
    Function that tests the loading of a Multimodal LLM command  object
    :param llm_operations: An LLMOperations object
    :return:
    """
    data_dict = {
        "type": "llm",
        "settings": {
            "try_limit": 3,
            "timeout": 30,
            "max_tokens": 300,
            "llm_settings": [
                {
                    "name": "OpenAI",
                    "api_key": "someKey",
                    "model": "gpt-3.5-turbo",
                    "temperature": 1.1,
                }
            ],
            "workflow": {"workflow_type": "chat_completion"},
        },
        "command_list": [
            {
                "message_type": "multimodal",
                "message": {
                    "role": "user",
                    "content": [{"type": "text", "text": "some text"}],
                },
            }
        ],
    }
    llm_op = llm_operations.load(data_dict)
    assert len(llm_op) == 1


def test_load_llm_operation_assistant(llm_operations):
    """
    Function that tests the loading of an Assistant LLM command  object
    :param llm_operations: An LLMOperations object
    """
    data_dict = {
        "type": "llm",
        "settings": {
            "try_limit": 3,
            "timeout": 30,
            "max_tokens": 300,
            "llm_settings": [
                {
                    "name": "OpenAI",
                    "api_key": "someKey",
                    "model": "gpt-3.5-turbo",
                    "temperature": 1.1,
                }
            ],
            "workflow": {"workflow_type": "chat_completion"},
        },
        "command_list": [
            {
                "message_type": "assistant",
                "message": {"role": "assistant", "content": "Hello."},
            }
        ],
    }
    llm_op = llm_operations.load(data_dict)
    assert len(llm_op) == 1


def test_llm_operation_load_with_invalid_command():
    """
    Function that tests the loading of an LLM command object with an invalid command
    """
    data_dict = {
        "type": "llm",
        "settings": {"headless": False},
        "command_list": [
            {"command_name": "invalid_command"},
        ],
    }
    with pytest.raises(TypeError):
        _BrowserOperations.load(data_dict)
