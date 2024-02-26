import configparser

from definitions import CONFIG_PATH


def load_config():
    conf = configparser.ConfigParser()
    try:
        conf.read(CONFIG_PATH)
    except Exception as e:
        print(f"Error reading config file: {e}")
    return conf
