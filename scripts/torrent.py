import re

import qbittorrentapi

from .config import Q_HOST, Q_PASSWORD, Q_USERNAME

qbt = qbittorrentapi.Client(
    host=Q_HOST, username=Q_USERNAME, password=Q_PASSWORD)

try:
    qbt.auth_log_in()
except Exception as e:
    print("login failed", e)


def get_magnet_hash(magnet: str):
    match = re.search(r"btih:([A-Fa-f0-9]+)", magnet)
    return match.group(1).lower() if match else None


def add_magnet_link(magnet_link: str, category=None):
    qbt.torrents.add(urls=magnet_link, category=category)


def get_progress():
    torrents = []
    for t in qbt.torrents_info():
        torrents.append([t.name, t.progress * 100])
    return torrents


def get_torrent_by_hash(hash: str):
    for t in qbt.torrents_info():
        return t if t.hash == hash else None
