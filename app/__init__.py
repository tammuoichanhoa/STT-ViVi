from flask import Flask

from .runtime import ensure_runtime_dirs, resource_root

BASE_DIR = resource_root()


def create_app() -> Flask:
    runtime_dirs = ensure_runtime_dirs()
    app = Flask(
        __name__,
        template_folder=str(BASE_DIR / "templates"),
        static_folder=str(BASE_DIR / "static"),
    )
    app.config["MAX_CONTENT_LENGTH"] = 200 * 1024 * 1024
    app.config["SECRET_KEY"] = "stt-vi-dev"
    app.config["UPLOAD_DIR"] = runtime_dirs["upload_dir"]
    app.config["OUTPUT_DIR"] = runtime_dirs["output_dir"]
    app.config["RUNTIME_DIR"] = runtime_dirs["root"]

    from .routes import bp

    app.register_blueprint(bp)
    return app
