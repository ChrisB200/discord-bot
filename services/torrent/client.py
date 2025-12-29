import logging

import qbittorrentapi
from qbittorrentapi.exceptions import Forbidden403Error, LoginFailed

from config.settings import Q_HOST, Q_PASSWORD, Q_USERNAME

logger = logging.getLogger(__name__)

_qbt_client: qbittorrentapi.Client | None = None


def get_client() -> qbittorrentapi.Client:
    global _qbt_client

    if _qbt_client is not None:
        return _qbt_client

    logger.info("Initialising qBittorrent client")

    client = qbittorrentapi.Client(
        host=Q_HOST,
        username=Q_USERNAME,
        password=Q_PASSWORD,
    )

    try:
        client.auth_log_in()
        logger.info("Successfully authenticated with qBittorrent")

    except LoginFailed as e:
        logger.error("Failed to authenticate with qBittorrent")
        raise RuntimeError("qBittorrent login failed") from e

    except Forbidden403Error as e:
        logger.error("qBittorrent authentication forbidden (403)")
        raise RuntimeError("qBittorrent access forbidden") from e

    _qbt_client = client
    return _qbt_client
