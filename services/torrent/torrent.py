import re

from .client import get_client


def get_magnet_hash(magnet: str):
    match = re.search(r"btih:([A-Fa-f0-9]+)", magnet)
    return match.group(1).lower() if match else None


def add_magnet_link(magnet_link: str, category=None):
    qbt = get_client()
    qbt.torrents.add(urls=magnet_link, category=category)


def get_progress():
    qbt = get_client()
    torrents = []
    for t in qbt.torrents_info():
        torrents.append([t.name, t.progress * 100])
    return torrents


def get_torrent_by_hash(hash: str):
    qbt = get_client()

    for t in qbt.torrents_info():
        if t.hash == hash:
            return t

    return None
