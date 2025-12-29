import functools

from .state import client


def requires_discord(func):
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        if not client:
            raise RuntimeError(
                "Discord client is not initialised. "
                "This function was called before startup completed."
            )
        return await func(*args, **kwargs)

    return wrapper
