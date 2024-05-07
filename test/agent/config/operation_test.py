import pytest
from agent.config.operation import Operation, BrowserOperations, LLMSettings, OpenAISettings, LLMOperations
from agent.config.command import Command, Navigate


@pytest.fixture
def operation():
    return Operation("test_operation")


def test_operation_creation(operation):
    assert operation.op_type == "test_operation"


def test_operation_append_valid_command(operation):
    command = Command("test_operation", "command_name", {"params_key": "params_value"})
    operation.append(command)
    assert len(operation) == 1


def test_operation_to_dict(operation):
    command1 = Command("test_operation", "command_name", {"params_key": "params_value"})
    command2 = Command("test_operation", "command_name", {"params_key": "params_value"})
    operation.append(command1)
    operation.append(command2)
    expected_dict = {
        "type": "test_operation",
        "settings": {},
        "command_list": [command1.to_dict(), command2.to_dict()]
    }
    assert operation.to_dict() == expected_dict


def test_operation_to_json_string(operation):
    command1 = Command("test_operation", "command_name", {"params_key": "params_value"})
    command2 = Command("test_operation", "command_name", {"params_key": "params_value"})
    operation.append(command1)
    operation.append(command2)
    expected_json_string = ('{"type": "test_operation", "settings": {}, "command_list": [{"command_name": '
                            '"command_name", "params": {"params_key": "params_value"}}, {"command_name": '
                            '"command_name", "params": {"params_key": "params_value"}}]}')
    assert operation.to_json_string() == expected_json_string


@pytest.fixture
def browser_operation():
    return BrowserOperations()


def test_browser_operation_creation(browser_operation):
    assert browser_operation.op_type == "browser"
    assert browser_operation.headless is False


def test_browser_operation_append_valid_command(browser_operation):
    command = Navigate("https://example.com")
    browser_operation.append(command)
    assert len(browser_operation) == 1


def test_get_settings(browser_operation):
    assert browser_operation.get_settings() == {"headless": False}


def test_get_settings_with_headless():
    browser_op = BrowserOperations(headless=True)
    assert browser_op.get_settings() == {"headless": True}


def test_browser_operation_load_fps(browser_operation):
    data_dict = {
        "type": "browser",
        "settings": {"headless": True},
        "command_list": [
            {"command_name": "full_page_screenshot",
             "params": {"quality": 90, "name": "fullpage.png", "snap_shot_name": "s1"}}
        ],
    }
    browser_op = browser_operation.load(data_dict)
    assert len(browser_op) == 1


def test_browser_operation_load_owp(browser_operation):
    data_dict = {
        "type": "browser",
        "settings": {"headless": True},
        "command_list": [
            {
                "command_name": "open_web_page",
                "params": {
                    "url": "https://www.centerramd.live/"
                }
            }
        ],
    }
    browser_op = browser_operation.load(data_dict)
    assert len(browser_op) == 1


def test_browser_operation_load_es(browser_operation):
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
                    "snap_shot_name": "s1"
                }
            }
        ],
    }
    browser_op = browser_operation.load(data_dict)
    assert len(browser_op) == 1


def test_browser_operation_load_cn(browser_operation):
    data_dict = {
        "type": "browser",
        "settings": {"headless": True},
        "command_list": [
            {
                "command_name": "collect_nodes",
                "params": {
                    "selector": "body",
                    "wait_ready": "false",
                    "snap_shot_name": "s1"
                }
            }
        ],
    }
    browser_op = browser_operation.load(data_dict)
    assert len(browser_op) == 1


def test_browser_operation_load_save(browser_operation):
    data_dict = {
        "type": "browser",
        "settings": {"headless": True},
        "command_list": [
            {
                "command_name": "save_html",
                "params": {
                    "snap_shot_name": "s1"
                }
            }
        ],
    }
    browser_op = browser_operation.load(data_dict)
    assert len(browser_op) == 1


def test_browser_operation_load_sleep(browser_operation):
    data_dict = {
        "type": "browser",
        "settings": {"headless": True},
        "command_list": [
            {
                "command_name": "sleep",
                "params": {
                    "seconds": 1
                }
            }
        ],
    }
    browser_op = browser_operation.load(data_dict)
    assert len(browser_op) == 1


def test_browser_operation_load_click(browser_operation):
    data_dict = {
        "type": "browser",
        "settings": {"headless": True},
        "command_list": [
            {
                "command_name": "click",
                "params": {
                    "selector": "some_selector",
                    "query_type": "some_query_type"
                }
            }
        ],
    }
    browser_op = browser_operation.load(data_dict)
    assert len(browser_op) == 1


def test_browser_operation_load_with_invalid_command():
    data_dict = {
        "type": "browser",
        "settings": {"headless": False},
        "command_list": [
            {"command_name": "invalid_command"},
        ],
    }
    with pytest.raises(TypeError):
        BrowserOperations.load(data_dict)


@pytest.fixture
def llm_settings():
    return LLMSettings("OpenAI", "api_key")


def test_llm_settings_initialization():
    llm_settings = LLMSettings("OpenAI", "api_key")
    assert llm_settings["name"] == "OpenAI"
    assert llm_settings["api_key"] == "api_key"


def test_llm_settings_invalid_name():
    with pytest.raises(TypeError):
        LLMSettings(None, "api_key")


def test_llm_settings_invalid_api_key():
    with pytest.raises(TypeError):
        LLMSettings("OpenAI", None)


def test_llm_settings_invalid_type_name():
    with pytest.raises(TypeError):
        # pylint: disable=E1123
        LLMSettings(123, "api_key")  # type: ignore


def test_llm_settings_invalid_type_api_key():
    with pytest.raises(TypeError):
        # pylint: disable=E1123
        LLMSettings("OpenAI", 123)  # type: ignore


@pytest.fixture
def openai_settings():
    return OpenAISettings("OpenAI", "api_key", "gpt-3.5-turbo", 0.7)


def test_openai_settings_initialization(openai_settings):
    assert openai_settings["name"] == "OpenAI"
    assert openai_settings["api_key"] == "api_key"
    assert openai_settings["model"] == "gpt-3.5-turbo"
    assert openai_settings["temperature"] == 0.7


def test_openai_settings_invalid_model():
    with pytest.raises(TypeError):
        # pylint: disable=E1123
        OpenAISettings("OpenAI", "api_key", 123, 0.7)  # type: ignore


def test_openai_settings_invalid_temperature():
    with pytest.raises(TypeError):
        # pylint: disable=E1123
        OpenAISettings("OpenAI", "api_key", "gpt-3.5-turbo", "temperature")  # type: ignore


@pytest.fixture
def llm_operations():
    llm_settings = [LLMSettings("OpenAI", "api_key")]
    return LLMOperations(3, 30, 1000, llm_settings, "workflow_type")


def test_llm_operations_initialization(llm_operations):
    assert llm_operations.settings["try_limit"] == 3
    assert llm_operations.settings["max_tokens"] == 1000
    assert len(llm_operations.settings["llm_settings"]) == 1
    assert llm_operations.settings["workflow"]["workflow_type"] == "workflow_type"


def test_llm_operations_get_settings(llm_operations):
    settings = llm_operations.get_settings()
    assert settings["try_limit"] == 3
    assert settings["max_tokens"] == 1000
    assert len(settings["llm_settings"]) == 1
    assert settings["workflow"]["workflow_type"] == "workflow_type"


def test_llm_operation_standard(llm_operations):
    data_dict = {
      "type": "llm",
      "settings":
      {
        "try_limit": 3,
        "timeout": 30,
        "max_tokens": 300,
        "llm_settings":
        [
          {
            "name": "OpenAI",
            "api_key": "someKey",
            "model": "gpt-3.5-turbo",
            "temperature": 1.1
          }
        ],
        "workflow":
        {
          "workflow_type": "chat_completion"
        }
      },
      "command_list":
      [
        {
          "message_type": "standard",
          "message": {
            "role": "user",
            "content": "You are a helpful assistant."
          }
        }
      ]
    }
    llm_op = llm_operations.load(data_dict)
    assert len(llm_op) == 1


def test_llm_operation_multimodal(llm_operations):
    data_dict = {
      "type": "llm",
      "settings":
      {
        "try_limit": 3,
        "timeout": 30,
        "max_tokens": 300,
        "llm_settings":
        [
          {
            "name": "OpenAI",
            "api_key": "someKey",
            "model": "gpt-3.5-turbo",
            "temperature": 1.1
          }
        ],
        "workflow":
        {
          "workflow_type": "chat_completion"
        }
      },
      "command_list":
      [
        {
          "message_type": "multimodal",
          "message": {
            "role": "user",
            "content": [{"type": "text", "text": "some text"}]
          }
        }
      ]
    }
    llm_op = llm_operations.load(data_dict)
    assert len(llm_op) == 1


def test_llm_operation_assistant(llm_operations):
    data_dict = {
      "type": "llm",
      "settings":
      {
        "try_limit": 3,
        "timeout": 30,
        "max_tokens": 300,
        "llm_settings":
        [
          {
            "name": "OpenAI",
            "api_key": "someKey",
            "model": "gpt-3.5-turbo",
            "temperature": 1.1
          }
        ],
        "workflow":
        {
          "workflow_type": "chat_completion"
        }
      },
      "command_list":
      [
        {
          "message_type": "assistant",
          "message": {
            "role": "assistant",
            "content": "Hello."
          }
        }
      ]
    }
    llm_op = llm_operations.load(data_dict)
    assert len(llm_op) == 1


def test_llm_operation_load_with_invalid_command():
    data_dict = {
        "type": "llm",
        "settings": {"headless": False},
        "command_list": [
            {"command_name": "invalid_command"},
        ],
    }
    with pytest.raises(TypeError):
        BrowserOperations.load(data_dict)
