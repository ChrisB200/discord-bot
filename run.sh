#!/usr/bin/env bash
set -e

cd /home/pi/code/discord-bot

exec /home/pi/.local/bin/poetry run python main.py
