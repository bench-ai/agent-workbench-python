from src.agent import load_config, Agent


if __name__ == '__main__':
    config = load_config("./config.json")
    a = Agent(config)
    a.run(verbose=True)
