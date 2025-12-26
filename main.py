from threading import Thread

from bot import run_bot
from server import create_app


def run_flask():
    app = create_app()
    app.run(host="0.0.0.0", port=9000, debug=False)


if __name__ == "__main__":
    flask_thread = Thread(target=run_flask, daemon=True)
    flask_thread.start()

    run_bot()
