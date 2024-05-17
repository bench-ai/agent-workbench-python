import uuid
from .operation import Operation, _BrowserOperations, _LLMOperations, LLMSettings


class Creator:

    def __init__(self,
                 session_id: str | None = None,
                 live: bool = False):

        self._session_id = ""
        if not session_id:
            self._session_id = str(uuid.uuid4())
        else:
            self._session_id = session_id

        self._operations: list[Operation] = []
        self._live = live

    def get_session_id(self) -> str:
        return self._session_id

    @property
    def live(self) -> bool:
        return self._live

    def reset(self, session_id: str | None = None):
        self._session_id = ""
        if not session_id:
            self._session_id = str(uuid.uuid4())
        else:
            self._session_id = session_id

        self._operations = []
        return self

    def new_llm_operation(self,
                          try_limit: int,
                          timeout: int,
                          max_tokens: int,
                          llm_settings: list[LLMSettings],
                          workflow_type: str) -> _LLMOperations:

        llm_op = _LLMOperations(
            try_limit,
            timeout,
            max_tokens,
            llm_settings,
            workflow_type,
            self._session_id
        )

        self._operations.append(llm_op)
        return llm_op

    def new_browser_operation(self,
                              headless: bool = False,
                              timeout: None | int = None) -> _BrowserOperations:

        brow_op = _BrowserOperations(
            self._session_id,
            headless=headless,
            timeout=timeout,
            live=self._live)

        self._operations.append(brow_op)
        return brow_op

    def to_dict(self) -> dict:
        ret_dict = {
            "session_id": self._session_id,
            "operations": [opt.to_dict() for opt in self._operations]
        }

        return ret_dict

    @classmethod
    def load_from_dict(cls, data_dict: dict):

        operations = data_dict["operations"]
        session_id = data_dict["session_id"]
        creator = Creator(session_id)

        for opt in operations:
            match opt["type"]:
                case "browser":
                    creator.load_browser_operations(opt)
                case "llm":
                    creator.load_llm_operations(opt)
                case _:
                    raise TypeError(f"{opt['type']} is not a valid operation type")

        return creator

    def load_llm_operations(self, data_dict: dict):
        """
        takes in a python dictionary and identifies what type of
        LLM Command is being described by the dictionary
        appends an object of that type to a list of LLM Operations

        :params data_dict: python dictionary representing an LLM Command
        """
        llm_opts = _LLMOperations(
            try_limit=data_dict["settings"]["try_limit"],
            timeout=data_dict["settings"]["timeout"],
            max_tokens=data_dict["settings"]["max_tokens"],
            llm_settings=[
                LLMSettings(**llm_setting)
                for llm_setting in data_dict["settings"]["llm_settings"]
            ],
            workflow_type=data_dict["settings"]["workflow"]["workflow_type"],
            session_name=self._session_id
        )

        for command in data_dict["command_list"]:

            match command["message_type"]:
                case "standard":
                    llm_opts.add_standard_command(command["message"]["role"],
                                                  command["message"]["content"])
                case "multimodal":
                    multimodal_content = llm_opts.add_multimodal_command(command["message"]["role"])
                    for content in command["message"]["content"]:
                        if content["type"] == "text":
                            multimodal_content.add_content(content["type"], content["text"])
                        else:
                            multimodal_content.add_content(
                                content["type"], content["image_url"]["url"]
                            )
                case "assistant":
                    llm_opts.add_assistant_command(command["message"]["role"], command["message"]["content"])
                case _:
                    raise TypeError(
                        f"{command['command_name']} is not a valid LLM command"
                    )

        self._operations.append(llm_opts)

    def load_browser_operations(self, data_dict: dict):
        """
        Constructs a Browser Operation based on a config dictionary

        :param data_dict: A dictionary representing the config
        :return: A BrowserOperation
        """
        browser_opts = _BrowserOperations(self._session_id, **data_dict["settings"])

        for command in data_dict["command_list"]:

            match command["command_name"]:
                case "open_web_page":
                    browser_opts.add_navigate_command(command["params"]["url"])
                case "full_page_screenshot":
                    browser_opts.add_full_screenshot_command(
                        command["params"]["quality"],
                        command["params"]["name"],
                        command["params"]["snapshot_name"],
                    )
                case "element_screenshot":
                    browser_opts.add_element_screenshot_command(
                        command["params"]["scale"],
                        command["params"]["selector"],
                        command["params"]["name"],
                        command["params"]["snapshot_name"],
                    )
                case "collect_nodes":
                    browser_opts.add_collect_nodes(
                        command["params"]["selector"],
                        command["params"]["snapshot_name"],
                        command["params"]["wait_ready"],
                        command["params"]["recurse"],
                        command["params"]["prepopulate"],
                        command["params"]["get_styles"],
                    )
                case "save_html":
                    browser_opts.add_html(command["params"]["snapshot_name"])
                case "sleep":
                    browser_opts.add_sleep(command["params"]["seconds"])
                case "click":
                    browser_opts.add_click(command["params"]["selector"],
                                           command["params"]["query_type"])
                case "iterate_html":
                    browser_opts.add_iterate_html(**command["params"])
                case _:
                    raise TypeError(
                        f"{command['command_name']} is not a valid browser command"
                    )

        self._operations.append(browser_opts)

