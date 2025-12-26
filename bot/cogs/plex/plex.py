import math
import re

import discord
from discord.ext import commands

from ...scripts.torrent import add_magnet_link
from .scrapers.anime import NyaaScraper
from .scrapers.knaben import Knaben
from .views import PaginatorView

media_types = {
    "anime": "anime",
    "anime-movie": "anime-movies",
    "tv": "tv-shows",
    "movie": "movies",
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

    @plex.command()
    async def scrape(self, ctx, media_type: str, *, series: str):
        """Scrape Nyaa for anime and show paginated results"""
        media_type = media_types.get(media_type.lower())
        if not media_type:
            await ctx.send("Incorrect media type")

        if "anime" in media_type:
            rows = self.anime.scrape_nyaa(series)
        else:
            rows = self.knaben.search(series)

        if not rows:
            await ctx.send(f"No results found for `{series}`.")
            return

        chunk_size = 10
        pages = []
        for i in range(0, len(rows), chunk_size):
            chunk = rows[i: i + chunk_size]
            description_lines = []

            for j, row in enumerate(chunk, start=i + 1):
                name = row["name"]
                seeders = row["seeders"]
                size = row["size"]
                pretty_name = re.sub(r"(1080p|720p|2160p)", r"**\1**", name)
                description_lines.append(
                    f"**{j}.** 🎞️ {pretty_name}\n"
                    f"  💾 `{size}` | 🌱 `{seeders}` seeders"
                )

            embed = discord.Embed(
                title=f"🔍 Results for '{series}'",
                description="\n\n".join(description_lines),
                color=discord.Color.blurple(),
            )
            embed.set_footer(
                text=f"Page {len(pages)+1} / {math.ceil(len(rows)/chunk_size)}"
            )
            pages.append(embed)

        self.last_results[ctx.author.id] = {"rows": rows, "type": media_type}

        # create paginator view (imported from your .views)
        view = PaginatorView(ctx, pages)
        view.message = await ctx.send(embed=pages[0], view=view)

    @plex.command()
    async def download(self, ctx, *, id):
        last_results = self.last_results.get(ctx.author.id)["rows"]
        if not last_results:
            return await ctx.send("Must scrape first")

        result = last_results[int(id) - 1]

        add_magnet_link(
            result.get("magnet"), self.last_results.get(ctx.author.id)["type"]
        )

        await ctx.send("success")


async def setup(client):
    print("attempting to load plex cog")
    await client.add_cog(Plex(client))
