import logging

from discord.ext.commands import (ExtensionAlreadyLoaded, ExtensionFailed,
                                  ExtensionNotFound, NoEntryPointError)

from .guards import requires_discord
from .state import client

logger = logging.getLogger(__name__)


class ExtensionResult:
    LOADED = "loaded"
    UNLOADED = "unloaded"
    RELOADED = "reloaded"
    ALREADY_LOADED = "already_loaded"
    NOT_LOADED = "not_loaded"
    NOT_FOUND = "not_found"
    NO_ENTRYPOINT = "no_entrypoint"
    FAILED = "failed"


@requires_discord
async def load_extension(ext: str) -> str:
    try:
        await client.load_extension(ext)
        logger.info("Loaded extension: %s", ext)
        return ExtensionResult.LOADED

    except ExtensionAlreadyLoaded:
        logger.warning("Extension already loaded: %s", ext)
        return ExtensionResult.ALREADY_LOADED

    except ExtensionNotFound:
        logger.error("Extension not found: %s", ext)
        return ExtensionResult.NOT_FOUND

    except NoEntryPointError:
        logger.error("Extension missing setup(): %s", ext)
        return ExtensionResult.NO_ENTRYPOINT

    except ExtensionFailed:
        logger.exception("Extension failed to load: %s", ext)
        return ExtensionResult.FAILED


@requires_discord
async def unload_extension(ext: str) -> str:
    try:
        await client.unload_extension(ext)
        logger.info("Unloaded extension: %s", ext)
        return ExtensionResult.UNLOADED

    except ExtensionNotFound:
        logger.warning("Extension not loaded: %s", ext)
        return ExtensionResult.NOT_LOADED

    except Exception:
        logger.exception("Unexpected error unloading extension: %s", ext)
        return ExtensionResult.FAILED


@requires_discord
async def reload_extension(ext: str) -> str:
    unload_result = await unload_extension(ext)

    if unload_result not in {
        ExtensionResult.UNLOADED,
        ExtensionResult.NOT_LOADED,
    }:
        return unload_result

    load_result = await load_extension(ext)

    if load_result == ExtensionResult.LOADED:
        return ExtensionResult.RELOADED

    return load_result
