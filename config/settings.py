import os

from dotenv import load_dotenv

load_dotenv()


def load_env(key: str, fallback: str = None):
    value = os.getenv(key, fallback)
    if not value:
        raise RuntimeError(f"Required env variable {key} is not set")
    return value


ACCESS_TOKEN = load_env("ACCESS_TOKEN")
REDIS_HOST = load_env("REDIS_HOST")
REDIS_PORT = load_env("REDIS_PORT", 6379)
REDIS_PASSWORD = load_env("REDIS_PASSWORD")
ENVIRONMENT = load_env("ENVIRONMENT")
Q_HOST = load_env("Q_HOST")
Q_USERNAME = load_env("Q_USERNAME")
Q_PASSWORD = load_env("Q_PASSWORD")
