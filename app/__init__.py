from pathlib import Path

from flask import Flask


BASE_DIR = Path(__file__).resolve().parent.parent


def create_app() -> Flask:
    app = Flask(
        __name__,
        template_folder=str(BASE_DIR / "templates"),
        static_folder=str(BASE_DIR / "static"),
    )
    app.config["MAX_CONTENT_LENGTH"] = 200 * 1024 * 1024
    app.config["SECRET_KEY"] = "stt-vi-dev"
    app.config["UPLOAD_DIR"] = BASE_DIR / "uploads"
    app.config["OUTPUT_DIR"] = BASE_DIR / "outputs"

    app.config["UPLOAD_DIR"].mkdir(exist_ok=True)
    app.config["OUTPUT_DIR"].mkdir(exist_ok=True)

    from .routes import bp

    app.register_blueprint(bp)
    return app
