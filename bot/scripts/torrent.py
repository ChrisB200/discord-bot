import os

import qbittorrentapi

HOST = os.getenv("Q_HOST")
USERNAME = os.getenv("Q_USERNAME")
PASSWORD = os.getenv("Q_PASSWORD")

qbt = qbittorrentapi.Client(host=HOST, username=USERNAME, password=PASSWORD)

try:
    qbt.auth_log_in()
except Exception as e:
    print("login failed", e)


def add_magnet_link(magnet_link: str, category=None):
    qbt.torrents.add(urls=magnet_link, category=category)
    return "success"


def get_progress():
    torrents = []
    for t in qbt.torrents_info():
        torrents.append([t.name, t.progress * 100])
    return torrents
