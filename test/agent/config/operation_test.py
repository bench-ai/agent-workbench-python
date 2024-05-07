import pytest
from src.agent.config.operation import Operation, BrowserOperations
from src.agent.config.command import Command, Navigate


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
    return BrowserOperations(headless=True)


def test_browser_operation_creation(browser_operation):
    assert browser_operation.op_type == "browser"
    assert browser_operation.headless is True


def test_browser_operation_append_valid_command(browser_operation):
    command = Navigate("https://example.com")
    browser_operation.append(command)
    assert len(browser_operation) == 1
