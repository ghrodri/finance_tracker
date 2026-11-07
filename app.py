import threading
import webbrowser

from dash import Dash

import callbacks  # noqa: F401  (registers the callbacks)
from config import DB_PATH
from db import init_db
from layouts import serve_layout

app = Dash(__name__, suppress_callback_exceptions=True, title="Wealth Tracker")
app.layout = serve_layout
init_db()


def main(host="127.0.0.1", port=8050, open_browser=True):
    if open_browser:
        threading.Timer(1.2, lambda: webbrowser.open(f"http://{host}:{port}")).start()
    print(f"Wealth Tracker running at http://{host}:{port} (database: {DB_PATH})")
    app.run(host=host, port=port, debug=False)


if __name__ == "__main__":
    main()
