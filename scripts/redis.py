from redis import Redis

from .config import REDIS_HOST, REDIS_PASSWORD, REDIS_PORT

redis = Redis(
    host=REDIS_HOST, port=REDIS_PORT, password=REDIS_PASSWORD, decode_responses=True
)
