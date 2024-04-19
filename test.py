import json
from src.config.command import Navigate
from src.agent import Agent


if __name__ == '__main__':
    n = Navigate("https://www.bench-ai.com")

    navigateJson = n.to_json_string()

    print(navigateJson)

    print(Navigate.init_from_json_string(navigateJson).to_dict())
