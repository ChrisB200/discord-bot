import asyncio

import discord
from discord.client import Client
from discord.ext import commands

from scripts.config import ACCESS_TOKEN, ENVIRONMENT

from .cogs import load_cogs

intents = discord.Intents.default()
intents.message_content = True

prefix = "."
if ENVIRONMENT in {"dev", "development"}:
    prefix = "!"

client = commands.Bot(command_prefix="!", intents=intents)

AUTOROLE_ID = 1453930078965600347


async def send_dm(user_id: int, message: str):
    user = await client.fetch_user(user_id)
    await user.send(message)


@client.event
async def on_member_join(member: discord.Member):
    print(member)
    print("hello")
    role = member.guild.get_role(AUTOROLE_ID)
    if role:
        await member.add_roles(role, reason="Autorole on join")


@client.event
async def on_ready():
    await client.change_presence(
        status=discord.Status.online, activity=discord.Game("Online")
    )
    print("Bot is online")


@client.command()
async def load(ctx, extension):
    await client.load_extension(f"bot.cogs.{extension}.{extension}")


@client.command()
async def unload(ctx, extension):
    await client.unload_extension(f"bot.cogs.{extension}.{extension}")


@client.command()
async def reload(ctx, extension):
    await client.unload_extension(f"bot.cogs.{extension}.{extension}")
    await client.load_extension(f"bot.cogs.{extension}.{extension}")


def run_bot():
    asyncio.run(load_cogs(client))
    client.run(ACCESS_TOKEN)
