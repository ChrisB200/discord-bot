import math
import re

import discord
from discord.ext import commands

from ...scripts.torrent import add_magnet_link, get_progress
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
        """Base plex command"""
        await ctx.send("Available subcommands: organise, test, etc.")

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
                description="Use .download <number> to download\n\n".join(
                    description_lines
                ),
                color=discord.Color.blurple(),
            )
            embed.set_footer(
                text=f"Page {len(pages)+1} / {math.ceil(len(rows)/chunk_size)}"
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
        await self._scrape(ctx, "anime", series)

    @plex.command(aliases=["am", "anime-movie", "anime-movies"])
    async def anime_movies(self, ctx, *, series: str):
        await self._scrape(ctx, "anime-movies", series)

    @plex.command(aliases=["show", "tv-shows", "shows"])
    async def tv(self, ctx, *, series: str):
        await self._scrape(ctx, "tv-shows", series)

    @plex.command(aliases=["film", "films", "movie"])
    async def movies(self, ctx, *, series: str):
        await self._scrape(ctx, "movies", series)

    @plex.command()
    async def download(self, ctx, *, id):
        last_results = self.last_results.get(ctx.author.id)["rows"]
        if not last_results:
            return await ctx.send("Must search for a show, movie or anime first")

        try:
            id = int(id) - 1

            if id > len(last_results) - 1 or id <= 0:
                return await ctx.send(f"Must be between 1 and {len(last_results)}")

            result = last_results[id]

            add_magnet_link(
                result.get("magnet"), self.last_results.get(
                    ctx.author.id)["type"]
            )
        except Exception:
            return await ctx.send("An error has occured")

        await ctx.send(f"Began downloading: {result.get('name')}")

    @plex.command()
    async def progress(self, ctx):
        torrents = get_progress()
        if not torrents:
            return await ctx.send("Nothing is currently downloading")

        description_lines = []
        for t in torrents:
            description_lines.append(f"{t[0]}: {t[1]}%")

        embed = discord.Embed(
            title="Download Progress",
            description="\n".join(description_lines),
            color=discord.Color.blurple(),
        )

        await ctx.send(embed=embed)


async def setup(client):
    print("attempting to load plex cog")
    await client.add_cog(Plex(client))
