import logging
import os

import discord
from discord.ext import commands
from discord.ext.commands import (ExtensionAlreadyLoaded, ExtensionFailed,
                                  ExtensionNotFound, NoEntryPointError)

from config.logging import setup_logger
from config.settings import ACCESS_TOKEN, ENVIRONMENT
from services.discord import state

setup_logger("bot", "bot.logs")
logger = logging.getLogger(__name__)


async def load_cogs(client):
    base_path = "bot/cogs"

    for entry in os.listdir(base_path):
        full_path = os.path.join(base_path, entry)

        if not os.path.isdir(full_path):
            continue

        module_path = os.path.join(full_path, f"{entry}.py")
        if not os.path.exists(module_path):
            continue

        ext = f"bot.cogs.{entry}.{entry}"

        try:
            await client.load_extension(ext)
            logger.info("Loaded cog: %s", ext)

        except ExtensionAlreadyLoaded:
            logger.warning("Cog already loaded: %s", ext)

        except ExtensionNotFound:
            logger.error("Cog not found: %s", ext)

        except NoEntryPointError:
            logger.error("Cog missing setup(): %s", ext)

        except ExtensionFailed:
            logger.exception("Cog failed to load: %s", ext)
        except Exception:
            logger.exception("Unexpected error loading cog: %s", ext)
            raise


class Bot(commands.Bot):
    async def setup_hook(self):
        await load_cogs(self)


def setup_client():
    intents = discord.Intents.default()
    intents.message_content = True

    prefix = "."
    if ENVIRONMENT in {"dev", "development"}:
        prefix = "!"

    client = Bot(command_prefix=prefix, intents=intents)

    return client


client = setup_client()
state.client = client


async def send_dm(user_id: int, message: str):
    user = await client.fetch_user(user_id)
    await user.send(message)


@client.event
async def on_ready():
    await client.change_presence(
        status=discord.Status.online, activity=discord.Game("Online")
    )
    print("Bot is online")


def run_bot():
    client.run(ACCESS_TOKEN)
