import os
import threading
import webbrowser

from app import create_app


app = create_app()


def _open_browser() -> None:
    webbrowser.open("http://127.0.0.1:5000")


if __name__ == "__main__":
    if os.environ.get("STT_VI_OPEN_BROWSER", "1") == "1":
        threading.Timer(1.0, _open_browser).start()

    try:
        from waitress import serve
    except ModuleNotFoundError:
        app.run(host="127.0.0.1", port=5000, debug=False)
    else:
        serve(app, host="127.0.0.1", port=5000, threads=4)
