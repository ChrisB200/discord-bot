from flask import Blueprint, jsonify, request

from bot import client, send_dm
from scripts.redis import redis
from scripts.torrent import get_torrent_by_hash

routes = Blueprint("routes", __name__)


@routes.post("/torrent/completed")
def completed_torrent():
    hash = request.json.get("hash")

    if not hash:
        return jsonify("Missing hash"), 400

    user_id = int(redis.get(hash))

    if not user_id:
        return jsonify("Could not get user id from hash"), 400

    torrent = get_torrent_by_hash(hash)

    if not torrent:
        redis.delete(hash)
        return jsonify("could not get torrent from hash"), 400

    redis.delete(hash)

    message = f"{torrent.name} has completed downloading"

    client.loop.create_task(send_dm(user_id, message))
    return jsonify("success"), 200
