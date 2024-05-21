
# Agent Workbench Python

A python wrapper for the [Agent Workbench](https://github.com/bench-ai/agent-workbench.git) by Bench AI. The Agent workbench 
helps you create browser automation scripts powered by LLMs. 

Examples of things you can make using the Agent Workbench
- Automatic Job Applier
- Webscraping and data collection
- Web testing


## What we use it for
- test websites for accessibility issues 
- make website more accessible

## How does it work?

In the backend this code will send requests to the [Bench AI agent workbench](https://github.com/bench-ai/agent-workbench.git).
Communication takes place through pub sub framework based on the existence of json files. The json files represent individual
commands for the browser or LLM, or a sequence of commands.

There are two modes you can run the workbench in. The first is live mode, live mode allows users to interact with the 
browser dynamically, allocating new commands as the browser / LLM session is running. This mode is ideal when making
bots.

Regular mode requires the user to predetermine the commands they want to use. This mode is best for consistent repeatable
actions, such as scraping manuals

We provide two services. Browser and LLMs.
- The browser lets users interact with the browser: you can click on elements, take screenshots, collect html ...
- The LLM service, currently only works with open-ai, but will soon work with all major LLMs (anything on Olama, anthropic ...) We provide features such as 
  - exponential backoff
  - easy tool calling
  - multimodal integration
  - unified api

## Design Choice Questions
Why is the backend written in GO? 
- In the future when we want to allow users to run multiple browser sessions in parallel
using a framework that enables that like chromedp will show its efficacy.

Will you provide resources to simplify creating agentic workflows?
- Maybe right now we believe that need is fulfilled by other libraries

## Requirements
- Google Chrome
- python 3.10

## Installation
You can install the Agent Workbench Python Wrapper using pip:

### Nightly
```shell
pip install git https://github.com/bench-ai/agent-workbench-python.git
````

### PyPi
```shell
# coming soon
```

### Build from source

1) Install latest version of the [Bench AI agent workbench](https://github.com/bench-ai/agent-workbench.git) from source
2) Install Poetry

```shell
git clone https://github.com/bench-ai/agent-workbench.git
poetry install . # needed for testing
```

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
from agent.config.command import _Navigate

# Navigate to a webpage
navigate_command = _Navigate("https://example.com")
```
Initializing with a dictionary:

```python 
from agent.config.command import _Navigate

navigate_command_dict = {
    "command_name": "open_web_page",
    "params": {"url": "https://example.com"}
}
navigate_command = _Navigate.init_from_dict(navigate_command_dict)
```

##### - FullPageScreenshot Command
Initializing with arguments:
 - Arguments: 
   - quality: quality of the image, higher = better
   - name: name of the screenshot file
   - snap_shot_name: what snapshot folder to save too

```python
from agent.config.command import _FullPageScreenshot

# Take a full page screenshot
full_page_screenshot_command = _FullPageScreenshot(quality=80, name="example_page", snap_shot_name="<location>")
```
Initializing with a dictionary:

```python 
from agent.config.command import _FullPageScreenshot

full_page_screenshot_command_dict = {
    "command_name": "full_page_screenshot",
    "params": {
        "quality": 90,
        "name": "full_page_screenshot.png",
        "snap_shot_name": "snapshot",
    }
}
full_page_screenshot_command = _FullPageScreenshot.init_from_dict(full_page_screenshot_command_dict)
```
##### - Element Screenshot Command
Initializing with arguments:
 - Arguments: 
   - scale: The size and quality of the image
   - selector: the xpath selector used to capture the image
   - name: the name of the image file that will be written in
   - snap_shot_name: the snapshot folder to save the image too

```python
from agent.config.command import _ElementScreenShot

# Take a screenshot of a specific element
element_screenshot_command = _ElementScreenShot(scale=2, selector="<css selector>", name="<example_name>",
                                                snap_shot_name="<location>")
```
Initializing with a dictionary:

```python 
from agent.config.command import _ElementScreenShot

Element_screenshot_command_dict = {
    "command_name": "element_screenshot",
    "params": {
        "scale": 2,
        "name": "element.png",
        "selector": "<selector for the element to capture>",
        "snap_shot_name": "s1"
    }
}
element_screenshot_command = _ElementScreenShot.init_from_dict(Element_screenshot_command_dict)
```
##### - CollectNodes Command
Initializing with arguments:
 - Arguments: 
   - selector: The css selector that represents the section you want to extract
   - snap_shot_name: the folder to write the data to
   - wait_ready: whether to wait for the element to appear, defaults to False

```python
from agent.config.command import _CollectNodes

# Collect nodes (elements) from a webpage
collect_nodes_command = _CollectNodes(selector="<css selector>", snap_shot_name="snapshot_1")
```
Initializing with a dictionary:

```python 
from agent.config.command import _CollectNodes

collect_nodes_command_dict = {
    "command_name": "collect_nodes",
    "params": {
        "selector": "body",
        "wait_ready": 'false',
        "snap_shot_name": "s1"
    }
}
collect_nodes_command = _CollectNodes.init_from_dict(collect_nodes_command_dict)
```
##### - SaveHtml Command
Initializing with arguments:
 - Arguments:
   - snap_shot_name: The snapshot to save the html too

```python
from agent.config.command import _SaveHtml

# Save HTML content to a file
save_html_command = _SaveHtml(snap_shot_name="snapshot_1")
```
Initializing with a dictionary:

```python 
from agent.config.command import _SaveHtml

save_html_command_dict = {
    "command_name": "save_html",
    "params": {
        "snap_shot_name": "s1"
    }
}
save_html_command = _SaveHtml.init_from_dict(save_html_command_dict)
```
##### - Sleep Command
Initializing with arguments:
 - Arguments:
   - seconds: The sleep duration

```python
from agent.config.command import _Sleep

# Sleep for a specified duration
sleep_command = _Sleep(ms=5)
```
Initializing with a dictionary:

```python 
from agent.config.command import _Sleep

sleep_command_dict = {
    "command_name": "sleep",
    "params": {
        "seconds": 1
    }
}
sleep_command = _Sleep.init_from_dict(sleep_command_dict)
```

##### - Click Command
Initializing with arguments:
 - Arguments:
   - selector: The value you are using to discriminate your selection
   - query_type: the type of the selector ex: x_path

```python
from agent.config.command import _Click

# Click on a particular element on the webpage
click_command = _Click(selector="<css selector>", query_type="xpath")
```
Initializing with a dictionary:

```python 
from agent.config.command import _Click

click_dict = {
    "command_name": "click",
    "params": {
        "selector": "//button[@id='submit']",
        "query_type": "xpath"
    }
}
click_command = _Click.init_from_dict(click_dict)
```

### LLM Commands
LLM Commands can be initialized either by passing in arguments to a new LLMComand object, or by initializing from a dictionary in the correct format.
##### - Standard LLM Commands
Initializing with arguments:
 - Arguments:
   - role: the role of the message to the LLM (generally will be 'user')
   - content: the content of the message to send to the LLM

```python
from agent.config.command import _Standard

# These commands are standard text based prompts to the model selected
standard_command = _Standard(role="user", content="Can you be a helpful assistant?")
```
Initializing with a dictionary:

```python
from agent.config.command import _Standard

# These commands are standard text based prompts to the model selected
standard_command_dict = {
    "message": {
        "role": "user",
        "content": "can you be a helpful assistant?"
    }
}
standard_command = _Standard.init_from_dict(standard_command_dict)
```

##### - Multimodal LLM Command
Initializing with arguments:
 - Arguments:
   - role: the role of the message to the LLM (generally will be 'user')

```python
from agent.config.command import _Multimodal

# These commands allow users to engineer prompts for multimodal models 
explain_image = _Multimodal('user')
explain_image.add_content('text', "explain what is happening in this image")
explain_image.add_content("image_url", "<path to image or image url>", True)
```
Initializing with a dictionary:

```python
from agent.config.command import _Multimodal

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
multimodal_command = _Multimodal.init_from_dict(multimodal_command_dict)
```
#####  - Assistant LLM Commands
Initializing with arguments:
 - Arguments:
   - role: the role of the message from the LLM (will be 'assistant' for assistant commands)
   - content: the content of the message to send to the LLM

```python
from agent.config.command import _Assistant

# These commands represent responses from LLMs which users can access to 
# construct continuous conversations with a model
assistant_command = _Assistant(role="assistant", content="<response form LLM>")
```
Initializing with a dictionary:

```python
from agent.config.command import _Assistant

assistant_command_data = {
    "message": {"role": "assistant", "content": "<response from LLM>"}
}
assistant_command = _Assistant.init_from_dict(assistant_command_data)
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
from agent.config.operation import _BrowserOperations
from agent.config.command import _Navigate, _FullPageScreenshot
from agent.conduit import Conduit

# Create a BrowserOperations instance
browser_ops = _BrowserOperations(headless=True, timeout=30)

# Add commands to the operation
browser_ops.append(_Navigate("https://example.com"))
browser_ops.append(_FullPageScreenshot(quality=80, name="example_page", snap_shot_name="example_name"))

# running the Browser Operations list
agent = Conduit([browser_ops])
agent.run(verbose=True)
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
from agent.config.command import _Standard
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
llm_ops.append(_Standard(role="user", content="Hello, how are you?"))

# running the LLM Operations list
agent = Conduit([llm_ops])
agent.run(verbose=True)
```
