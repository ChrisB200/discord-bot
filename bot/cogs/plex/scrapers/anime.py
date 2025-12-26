from typing import List

import requests
from bs4 import BeautifulSoup, Tag


class NyaaScraper:
    BASE_URL = "https://nyaa.si"

    def __init__(self):
        self.session = requests.session()

    def search(self, series):
        params = {"f": 0, "c": "0_0", "q": series}
        r = self.session.get(self.BASE_URL, params=params)
        r.raise_for_status()
        return r.text

    def parse_table(self, html: str):
        soup = BeautifulSoup(html, "html.parser")
        table = soup.select("table")
        return table[0]

    def parse_rows(self, table: List[Tag]):
        rows = table.select("tr")
        parsed_rows = []
        for row in rows:
            cols = row.select("td")
            if len(cols) == 0:
                continue
            name = self.get_name(cols)
            magnet = self.get_magnet_link(cols)
            seeders = self.get_seeders(cols)
            size = self.get_size(cols)
            if not name or not magnet:
                continue
            parsed_rows.append(
                {"name": name, "magnet": magnet, "seeders": seeders, "size": size}
            )

        return parsed_rows

    def get_name(self, cols: List[Tag]):
        for col in cols:
            span = col.attrs.get("colspan")
            if span == 2 or span == "2":
                elements = col.select("a")
                for e in elements:
                    title = e.attrs.get("title")
                    if title and not "comments" in title and not "comment" in title:
                        return e.attrs.get("title")

    def get_magnet_link(self, cols: List[Tag]):
        if not len(cols) > 2:
            return None

        magnet_col = cols[2]
        magnet_anchor = magnet_col.select("a")[1]
        magnet = magnet_anchor.attrs.get("href")
        return magnet

    def get_seeders(self, cols: List[Tag]):
        seeder_col = cols[5]
        seeders = seeder_col.text.strip()
        return seeders

    def get_size(self, cols: List[Tag]):
        size_col = cols[3]
        size = size_col.text.strip()
        return size

    def scrape_nyaa(self, series):
        page = self.search(series)
        table = self.parse_table(page)
        rows = self.parse_rows(table)

        return rows

    def format_content(self, rows, limit=10):
        string = ""
        for count, row in enumerate(rows[:limit]):
            string = f"{string}{count + 1}. {row['name']}\n"

        return string
