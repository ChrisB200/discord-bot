import math
import re

import discord
from discord.ext import commands

from scripts.redis import redis
from scripts.torrent import add_magnet_link, get_magnet_hash, get_progress

from .scrapers.anime import NyaaScraper
from .scrapers.knaben import Knaben
from .views import PaginatorView

media_types = {
    "anime": "anime",
    "anime-movie": "anime-movies",
    "tv": "tv-shows",
    "film": "movies",
    "films": "movies",
    "shows": "tv-shows",
    "show": "tv-shows",
    "movie": "movies",
    "movies": "movies",
    "tv-shows": "tv-shows",
    "anime-movies": "anime-movies",
}


class Plex(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.anime = NyaaScraper()
        self.knaben = Knaben()
        self.last_results = {}

    @commands.group(invoke_without_command=True)
    async def plex(self, ctx):
        """Scrape and download media for Plex."""
        await ctx.invoke(ctx.bot.get_command("help"), "plex")

    @plex.command(name="help")
    async def plex_help(self, ctx):
        """Show help for Plex commands."""
        embed = discord.Embed(
            title="📺 Plex Commands",
            color=discord.Color.blurple(),
            description="Available subcommands:",
        )

        plex_cmd = ctx.bot.get_command("plex")

        for cmd in plex_cmd.commands:
            aliases = ", ".join(cmd.aliases) if cmd.aliases else "None"
            embed.add_field(
                name=f".plex {cmd.name}",
                value=f"{cmd.help or 'No description'}\nAliases: `{aliases}`",
                inline=False,
            )

        await ctx.send(embed=embed)

    async def _scrape(self, ctx, media_type: str, series: str):
        if media_type in {"anime", "anime-movie"}:
            rows = self.anime.scrape_nyaa(series)
        else:
            rows = self.knaben.search(series)

        if not rows or rows == []:
            await ctx.send(f"No results found for `{series}`.")
            return

        chunk_size = 10
        pages = []

        for i in range(0, len(rows), chunk_size):
            chunk = rows[i: i + chunk_size]
            description_lines = []

            for j, row in enumerate(chunk, start=i + 1):
                pretty_name = re.sub(r"(1080p|720p|2160p)",
                                     r"**\1**", row["name"])
                description_lines.append(
                    f"**{j}.** 🎞️ {pretty_name}\n"
                    f"  💾 `{row['size']}` | 🌱 `{row['seeders']}` seeders"
                )

            embed = discord.Embed(
                title=f"🔍 Results for '{series}'",
                description="\n\n".join(description_lines),
                color=discord.Color.blurple(),
            )
            embed.set_footer(
                text=f"Use .download <number> to begin downloading\nPage {len(pages)+1} / {math.ceil(len(rows)/chunk_size)}"
            )
            pages.append(embed)

        self.last_results[ctx.author.id] = {
            "rows": rows,
            "type": media_type,
        }

        view = PaginatorView(ctx, pages)
        view.message = await ctx.send(embed=pages[0], view=view)

    @plex.command(aliases=["a"])
    async def anime(self, ctx, *, series: str):
        """Search for anime"""
        await self._scrape(ctx, "anime", series)

    @plex.command(aliases=["am", "anime-movie", "anime-movies"])
    async def anime_movies(self, ctx, *, series: str):
        """Search for anime movies"""
        await self._scrape(ctx, "anime-movies", series)

    @plex.command(aliases=["show", "tv-shows", "shows"])
    async def tv(self, ctx, *, series: str):
        """Search for tv shows"""
        await self._scrape(ctx, "tv-shows", series)

    @plex.command(aliases=["film", "films", "movie"])
    async def movies(self, ctx, *, series: str):
        """Search for movies"""
        await self._scrape(ctx, "movies", series)

    @plex.command()
    async def download(self, ctx, *, id):
        """Download a result by its number from the last search"""
        last_results = self.last_results.get(ctx.author.id)["rows"]
        if not last_results:
            return await ctx.send("Must search for a show, movie or anime first")

        try:
            id = int(id) - 1

            if id > len(last_results) - 1 or id < 0:
                return await ctx.send(f"Must be between 1 and {len(last_results)}")

            result = last_results[id]
            magnet = result.get("magnet")
            user = self.last_results.get(ctx.author.id)
            hash = get_magnet_hash(magnet)
            media_type = user.get("type")

            add_magnet_link(magnet, media_type)
            redis.set(hash, ctx.author.id)
        except Exception as e:
            print(str(e))
            return await ctx.send("An error has occurred")

        await ctx.send(
            f"Began downloading: {result.get('name')}\n use .progress to check its progress"
        )

    @plex.command()
    async def progress(self, ctx):
        """Get the progress of all media currently downloading"""
        torrents = get_progress()
        if not torrents:
            return await ctx.send("Nothing is currently downloading")

        description_lines = []
        for i, t in enumerate(torrents):
            description_lines.append(f"{i}. {t[0]}: **{round(float(t[1]))}%**")

        embed = discord.Embed(
            title="Download Progress",
            description="\n".join(description_lines),
            color=discord.Color.blurple(),
        )

        await ctx.send(embed=embed)


async def setup(client):
    print("attempting to load plex cog")
    await client.add_cog(Plex(client))
