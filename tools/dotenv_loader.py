import os

from dotenv import load_dotenv

from definitions import DOTENV_PATH


def load_env():
    load_dotenv(DOTENV_PATH)


def reload_env():
    os.environ.clear()
    load_dotenv(DOTENV_PATH)
