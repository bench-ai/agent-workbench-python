
# Agent Workbench Python Wrapper

The Agent Workbench Python Wrapper is a Python package that provides a set of classes and methods for constructing agents tailored to specific tasks. This wrapper simplifies the process of building agents that interact with web browsers or language models by offering a convenient and easy-to-use interface.

## Installation
First you must install the agent workbench itself following the instructions from https://github.com/bench-ai/agent-workbench.git

You can install the Agent Workbench Python Wrapper using pip:

```bash
pip install git https://github.com/bench-ai/agent-workbench-python.git
````

## Usage

### Commands
The `Command` module includes all the commands you can implement for browser and llm operations. Here's how you can use it:

### Browser Commands
Browser Commands can be initialized either by passing in arguments to a new BrowserCommand object, or by initializing from a dictionary in the correct format.

##### - Navigate Command
Initializing with arguments:
 - Arguments: 
   - url: The url for the webpage to open
```python
from agent.config.command import Navigate
# Navigate to a webpage
navigate_command = Navigate("https://example.com")
```
Initializing with a dictionary:
```python 
from agent.config.command import Navigate
navigate_command_dict = {
    "command_name": "open_web_page",
    "params": {"url": "https://example.com"}
}
navigate_command = Navigate.init_from_dict(navigate_command_dict)
```

##### - FullPageScreenshot Command
Initializing with arguments:
 - Arguments: 
   - quality: quality of the image, higher = better
   - name: name of the screenshot file
   - snap_shot_name: what snapshot folder to save too
```python
from agent.config.command import FullPageScreenshot
# Take a full page screenshot
full_page_screenshot_command = FullPageScreenshot(quality=80, name="example_page", snap_shot_name="<location")
```
Initializing with a dictionary:
```python 
from agent.config.command import FullPageScreenshot
full_page_screenshot_command_dict = {
        "command_name": "full_page_screenshot",
        "params": {
            "quality": 90,
            "name": "full_page_screenshot.png",
            "snap_shot_name": "snapshot",
        }
    }
full_page_screenshot_command = FullPageScreenshot.init_from_dict(full_page_screenshot_command_dict)
```
##### - Element Screenshot Command
Initializing with arguments:
 - Arguments: 
   - scale: The size and quality of the image
   - selector: the xpath selector used to capture the image
   - name: the name of the image file that will be written in
   - snap_shot_name: the snapshot folder to save the image too
```python
from agent.config.command import ElementScreenShot
# Take a screenshot of a specific element
element_screenshot_command = ElementScreenShot(scale=2, selector="<css selector>", name="<example_name>", snap_shot_name="<location>")
```
Initializing with a dictionary:
```python 
from agent.config.command import ElementScreenShot
Element_screenshot_command_dict = {
        "command_name": "element_screenshot",
          "params": {
            "scale":2,
            "name": "element.png",
            "selector": "<selector for the element to capture>",
            "snap_shot_name": "s1"
        }
    }
element_screenshot_command = ElementScreenShot.init_from_dict(Element_screenshot_command_dict)
```
##### - CollectNodes Command
Initializing with arguments:
 - Arguments: 
   - selector: The css selector that represents the section you want to extract
   - snap_shot_name: the folder to write the data to
   - wait_ready: whether to wait for the element to appear, defaults to False
```python
from agent.config.command import CollectNodes
# Collect nodes (elements) from a webpage
collect_nodes_command = CollectNodes(selector="<css selector>", snap_shot_name="snapshot_1")
```
Initializing with a dictionary:
```python 
from agent.config.command import CollectNodes
collect_nodes_command_dict = {
        "command_name": "collect_nodes",
          "params": {
            "selector":"body",
            "wait_ready": 'false',
            "snap_shot_name": "s1"
        }
    }
collect_nodes_command = CollectNodes.init_from_dict(collect_nodes_command_dict)
```
##### - SaveHtml Command
Initializing with arguments:
 - Arguments:
   - snap_shot_name: The snapshot to save the html too
```python
from agent.config.command import SaveHtml
# Save HTML content to a file
save_html_command  = SaveHtml(snap_shot_name="snapshot_1")
```
Initializing with a dictionary:
```python 
from agent.config.command import SaveHtml
save_html_command_dict = {
        "command_name": "save_html",
          "params": {
            "snap_shot_name": "s1"
        }
    }
save_html_command = SaveHtml.init_from_dict(save_html_command_dict)
```
##### - Sleep Command
Initializing with arguments:
 - Arguments:
   - seconds: The sleep duration
```python
from agent.config.command import Sleep

# Sleep for a specified duration
sleep_command = Sleep(seconds=5)
```
Initializing with a dictionary:
```python 
from agent.config.command import Sleep
sleep_command_dict = {
        "command_name": "sleep",
          "params": {
            "seconds": 1
        }
    }
sleep_command = Sleep.init_from_dict(sleep_command_dict)
```

##### - Click Command
Initializing with arguments:
 - Arguments:
   - selector: The value you are using to discriminate your selection
   - query_type: the type of the selector ex: x_path
```python
from agent.config.command import Click
# Click on a particular element on the webpage
click_command = Click(selector="<css selector>", query_type="xpath")
```
Initializing with a dictionary:
```python 
from agent.config.command import Click
click_dict = {
        "command_name": "click",
        "params": {
            "selector": "//button[@id='submit']", 
            "query_type": "xpath"
        }
    }
click_command = Click.init_from_dict(click_dict)
```

### LLM Commands
LLM Commands can be initialized either by passing in arguments to a new LLMComand object, or by initializing from a dictionary in the correct format.
##### - Standard LLM Commands
Initializing with arguments:
 - Arguments:
   - role: the role of the message to the LLM (generally will be 'user')
   - content: the content of the message to send to the LLM
```python
from agent.config.command import Standard
# These commands are standard text based prompts to the model selected
standard_command = Standard(role="user", content="Can you be a helpful assistant?")
```
Initializing with a dictionary:
```python
from agent.config.command import Standard
# These commands are standard text based prompts to the model selected
standard_command_dict = {
    "message": {
        "role": "user",
        "content": "can you be a helpful assistant?"
    }
}
standard_command = Standard.init_from_dict(standard_command_dict)
```

##### - Multimodal LLM Command
Initializing with arguments:
 - Arguments:
   - role: the role of the message to the LLM (generally will be 'user')
```python
from agent.config.command import Multimodal
# These commands allow users to engineer prompts for multimodal models 
explain_image = Multimodal('user')
explain_image.add_content('text', "explain what is happening in this image")
explain_image.add_content("image_url", "<path to image or image url>" , True)
```
Initializing with a dictionary:
```python
from agent.config.command import Multimodal
multimodal_command_dict = {
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
multimodal_command = Multimodal.init_from_dict(multimodal_command_dict)
```
#####  - Assistant LLM Commands
Initializing with arguments:
 - Arguments:
   - role: the role of the message from the LLM (will be 'assistant' for assistant commands)
   - content: the content of the message to send to the LLM
```python
from agent.config.command import Assistant
# These commands represent responses from LLMs which users can access to 
# construct continuous conversations with a model
assistant_command = Assistant(role="assistant", content="<response form LLM>")
```
Initializing with a dictionary:
```python
from agent.config.command import Assistant
assistant_command_data = {
    "message": {"role": "assistant", "content": "<response from LLM>"}
}
assistant_command = Assistant.init_from_dict(assistant_command_data)
```
## Operations
The `Operation` module allows you to create operation objects. Operation objects are lists of either browser commands or llm commands to be executed. Here's how you can implement them.

### Browser Operations

The `BrowserOperations` class allows you to construct operations that involve interacting with web browsers. Below is an example of how to use it:
- Conduit Arguments:
  - operations: a list of Operation objects


- Arguments:
   - headless: Sets if you wish to visually see the agent operate on the browser
   - timeout: the maxtime the browser operation can operate for


```python
from agent.config.operation import BrowserOperations
from agent.config.command import Navigate, FullPageScreenshot
from agent.conduit import Conduit

# Create a BrowserOperations instance
browser_ops = BrowserOperations(headless=True, timeout=30)

# Add commands to the operation
browser_ops.append(Navigate("https://example.com"))
browser_ops.append(FullPageScreenshot(quality=80, name="example_page", snap_shot_name= "example_name"))

#running the Browser Operations list
agent = Conduit([browser_ops])
agent.run(verbose = True)
```

### LLM Operations

The `LLMOperations` class is designed for making requests to Language Model APIs. Here's how you can use it:
- Conduit Arguments:
  - operations: a list of Operation objects

- LLMOperations Arguments:
   - try_limit: the number of times the user wants a request to be tried by the agent if it is not able to get a response on the first try
   - timeout: the amount of time the user wants the agent to allow for a response to be received from a model before requesting again
   - max_tokens: the maximum number of words the user wants the model's response to be
   - llm_settings: a list of LLMSettings objects defining the settings for the different LLMs the user wants the agent to switch between (OpenAISettings, ...)
   - workflow_type: the type of agentic workflow the user wants the agent to implement (use chat_completion)


- OpenAISettings Arguments:
   - name: the name of the api
   - api_key:  key for the api
   - model: the specific OpenAI model the user wants to use (e.g., gpt-3.5-turbo)
   - temperature: the temperature the user wants the model to use (0.0 - 2.0)

```python
from agent.config.operation import LLMOperations, OpenAISettings
from agent.config.command import Standard
from agent.conduit import Conduit

# Define LLM settings
openai_settings = OpenAISettings(
    name="OpenAI", api_key="<your_api_key>", model="gpt-3.5-turbo", temperature=0.7
)

# Create LLM operations
llm_ops = LLMOperations(
    try_limit=3,
    timeout=60,
    max_tokens=500,
    llm_settings=[openai_settings],
    workflow_type="chat_completion",
)

# Add LLM commands to the operation
llm_ops.append(Standard(role="user", content="Hello, how are you?"))

#running the LLM Operations list
agent = Conduit([llm_ops])
agent.run(verbose = True)
```
