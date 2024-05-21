import typing
import inspect
import json


def check_docstring_format(func: typing.Callable):
    """
    Check if a function's docstring is in the correct format.

    :param func: The function to check.
    """
    docstring = func.__doc__

    if not docstring:
        raise ValueError("Function does not have a docstring.")

    lines = docstring.strip().split('\n')

    description_lines = []
    param_lines = []
    expected_params = [f":param {param}: " for param in inspect.signature(func).parameters]
    expected_params.extend([":return:", ":rtype:"])

    for line in lines:
        line = line.strip()
        if not line.startswith(":param") and not line.startswith(":return") and not line.startswith(":rtype"):
            description_lines.append(line)
        else:
            param_lines.append(line)

    # Check if there are any description lines
    if not description_lines:
        raise ValueError("Docstring is missing a description.")

    # Check if each param line is in the expected format
    for param in expected_params:
        if not any(param in line for line in param_lines):
            raise ValueError(f"Parameter line missing expected substring: '{param}'.")

    return description_lines, param_lines


def get_function_info(func: typing.Callable) -> dict:
    """
    Get description, parameters, and name from the docstring of a function.

    :param func: The function to check.

    Returns:
        dict: A dictionary containing the name, description, and parameters of the function.
    """

    def python_type_to_json_schema_type(python_type):
        """
        Converts Python types to JSON Schema types.

        :param python_type: The Python type.

        Returns:
            str: The JSON Schema type.
        """
        type_map = {
            str: "string",
            int: "integer",
            float: "number",
            bool: "boolean",
            list: "array",
            dict: "object",
            type(None): "null"
        }
        return type_map.get(python_type, "string")

    if not inspect.isfunction(func):
        raise TypeError("Input must be a function.")

    info = {'name': func.__name__, 'description': None, 'parameters': None}
    description_lines, param_lines = check_docstring_format(func)

    description = ' '.join(description_lines).strip()
    info['description'] = description

    parameters = {}
    descriptions = {}
    for line in param_lines:
        line = line.strip()
        if line.startswith(":param"):
            parts = line.split(':', 2)
            p_name = parts[1].split(' ', 1)[1].strip()
            p_desc = parts[2].strip() if len(parts) > 2 else None
            descriptions[p_name] = p_desc
    annotations = getattr(func, '__annotations__', {})
    for param_name, param_type in annotations.items():
        if param_name != 'return':  # Exclude return type
            parameters[param_name] = {"type": python_type_to_json_schema_type(param_type),
                                      "description": descriptions.get(param_name, None)}
    if parameters:
        info['parameters'] = parameters
    return info


def convert_to_schema(function_info):
    """
    Convert function information into a schema.

    Args:
        function_info (dict): A dictionary containing the name, description, and parameters of the function.

    Returns:
        dict: A json_schema representing the function.
    """
    json_schema = {
        "type": "function",
        "function": {
            "name": function_info['name'],
            "description": function_info['description'],
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    }

    if function_info['parameters']:
        for param_name, param_info in function_info['parameters'].items():
            json_schema['function']['parameters']['properties'][param_name] = {
                "type": param_info['type'],
                "description": param_info['description']
            }
            json_schema['function']['parameters']['required'].append(param_name)

    return json_schema
