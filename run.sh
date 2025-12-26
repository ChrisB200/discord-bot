#!/usr/bin/env bash
/home/pi/.local/bin/poetry install
exec /home/pi/.local/bin/poetry run python main.py
