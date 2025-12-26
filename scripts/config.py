import os

from dotenv import load_dotenv

load_dotenv()

ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
REDIS_HOST = os.getenv("REDIS_HOST")
REDIS_PORT = os.getenv("REDIS_PORT")
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD")
ENVIRONMENT = os.getenv("ENVIRONMENT")
Q_HOST = os.getenv("Q_HOST")
Q_USERNAME = os.getenv("Q_USERNAME")
Q_PASSWORD = os.getenv("Q_PASSWORD")
