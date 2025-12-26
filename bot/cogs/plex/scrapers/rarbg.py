import asyncio
import os
import time
from typing import List

import qbittorrentapi
from playwright.async_api import (Browser, Locator, Page, async_playwright,
                                  expect)

HOST = "http://100.67.188.42:8080"
USERNAME = os.getenv("Q_USERNAME")
PASSWORD = os.getenv("Q_PASSWORD")

qbt = qbittorrentapi.Client(host=HOST, username="admin", password="adminadmin")

try:
    qbt.auth_log_in()
except Exception as e:
    print("login failed", e)


def ensure_category(name: str, save_path: str | None = None):
    categories = qbt.torrents_categories()

    if name not in categories:
        qbt.torrents_create_category(
            category=name,
            save_path=save_path,  # optional
        )


def add_magnet_link(magnet_link: str):
    qbt.torrents.add(urls=magnet_link)
    return "success"


BASE_URL = "https://rarbglite.github.io/"


class RarBGScraper:
    def __init__(self, pw, browser: Browser, page: Page):
        self.pw = pw
        self.browser = browser
        self.page = page

    @classmethod
    async def create(cls):
        pw = await async_playwright().start()
        browser = await pw.chromium.launch(headless=False)
        page = await browser.new_page()
        await page.goto(BASE_URL)

        return cls(pw, browser, page)

    async def fill_search_bar(self, text: str):
        input_box = self.page.locator("input#query").first
        search_button = self.page.locator("button#btn").first
        await input_box.fill(text)
        await search_button.click()

    async def close(self):
        await self.browser.close()
        await self.pw.stop()

    async def is_searching(self):
        status = self.page.locator("span#status").first
        status_text = await status.text_content()

        if "so far" in status_text:
            return True

        return False

    async def get_results_count(self):
        try:
            status = self.page.locator("span#status").first
            status_text = await status.text_content()
            count = status_text.split(",")[1]
            count = count.split(" ")[1]

            if count == 0:
                return None

            return count
        except Exception:
            return None

    async def get_search_results(self, prev_count=None):
        results_container = self.page.locator("div#target").first
        results = results_container.locator("li")

        is_searching = await self.is_searching()

        while is_searching:
            is_searching = await self.is_searching()
            print("Waiting")
            time.sleep(0.5)

        results = await results.all()
        return results

    async def parse_results(self, results):
        parsed = []
        for result in results:
            name = await result.locator("a").first.text_content()
            magnet = await result.locator("a").first.get_attribute("href")
            size = await result.locator("b").last.text_content()
            imdb = result.locator("b").filter(has_text="tt").first
            imdb = await imdb.text_content()
            parsed.append(
                {"name": name, "magnet": magnet, "size": float(size), "imdb": imdb}
            )
        return parsed

    async def find_best_copies(self, parsed):
        found = []
        imdb = []
        for media in parsed:
            if (
                media["size"] < 15
                and "1080p" in media["name"]
                and media["imdb"] not in imdb
            ):
                found.append(media)
                imdb.append(media["imdb"])
        return found

    async def scrape(self, media: str):
        await self.fill_search_bar(media)
        results = await self.get_search_results()
        parsed = await self.parse_results(results)
        await self.close()
        return parsed

    async def scrape_list(self, media_list: List[str]):
        for media in media_list:
            await self.fill_search_bar(media)
            print(media)

        results = await self.get_search_results()
        parsed = await self.parse_results(results)
        found = await self.find_best_copies(parsed)

        for i in found:
            print(f"{i['name']}")

        await self.close()
        return found


async def main():
    scraper = await RarBGScraper.create()
    movies = [
        # Already confirmed earlier
        "tt8864596",  # Transformers One (2024)
        # Newly confirmed
        # Zoolander (2001) 🎬 — Ben Stiller comedy film  [oai_citation:0‡IMDb](https://www.imdb.com/title/tt0196229/?utm_source=chatgpt.com)
        "tt0196229",
        # Vanilla Sky (2001) — Tom Cruise sci-fi drama  [oai_citation:1‡IMDb](https://www.imdb.com/fr/title/tt0259711/plotsummary/?utm_source=chatgpt.com)
        "tt0259711",
        # Memento (2000) — Nolan thriller  [oai_citation:2‡IMDb](https://www.imdb.com/search/title/?genres=thriller&groups=top_250&sort=year%2Casc&utm_source=chatgpt.com)
        "tt0209144",
        # Memories of Murder (2003) — Korean crime drama  [oai_citation:3‡IMDb](https://www.imdb.com/list/ls003358413/copy/?utm_source=chatgpt.com)
        "tt0353969",
        # Example: Justice for All (1997)
        # Justice for All (1997) — “The New Adventures of Robin Hood” aka Justice for All  [oai_citation:4‡IMDb](https://www.imdb.com/title/tt0659254/mediaviewer/rm2560644608/?utm_source=chatgpt.com)
        "tt0659254",
    ]

    results = await scraper.scrape_list(movies)
    response = int(input("is that good? "))
    if response == 1:
        for result in results:
            add_magnet_link(result["magnet"])


asyncio.run(main())
