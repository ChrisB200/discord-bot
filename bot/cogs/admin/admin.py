import logging

from discord.ext import commands

from services.discord import (ExtensionResult, load_extension,
                              reload_extension, unload_extension)

logger = logging.getLogger(__name__)


class Admin(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command()
    async def load(self, ctx, extension: str):
        ext = f"bot.cogs.{extension}.{extension}"
        result = await load_extension(ext)

        messages = {
            ExtensionResult.LOADED: f"Loaded `{extension}`",
            ExtensionResult.ALREADY_LOADED: f"`{extension}` is already loaded",
            ExtensionResult.NOT_FOUND: f"Cog `{extension}` not found",
            ExtensionResult.NO_ENTRYPOINT: f"Cog `{extension}` has no setup()",
            ExtensionResult.FAILED: f"Failed to load `{extension}` (see logs)",
        }

        await ctx.send(messages.get(result, "Unknown error occurred"))

    @commands.command()
    async def unload(self, ctx, extension: str):
        ext = f"bot.cogs.{extension}.{extension}"
        result = await unload_extension(ext)

        messages = {
            ExtensionResult.UNLOADED: f"Unloaded `{extension}`",
            ExtensionResult.NOT_LOADED: f"`{extension}` is not loaded",
            ExtensionResult.FAILED: f"Failed to unload `{extension}` (see logs)",
        }

        await ctx.send(messages.get(result, "Unknown error occurred"))

    @commands.command()
    async def reload(self, ctx, extension: str):
        ext = f"bot.cogs.{extension}.{extension}"
        result = await reload_extension(ext)

        messages = {
            ExtensionResult.RELOADED: f"Reloaded `{extension}`",
            ExtensionResult.NOT_FOUND: f"Cog `{extension}` not found",
            ExtensionResult.NO_ENTRYPOINT: f"Cog `{extension}` has no setup()",
            ExtensionResult.FAILED: f"Failed to reload `{extension}` (see logs)",
        }

        await ctx.send(messages.get(result, "Unknown error occurred"))


async def setup(bot: commands.Bot):
    await bot.add_cog(Admin(bot))
