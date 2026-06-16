from pathlib import Path
from uuid import uuid4

from flask import Blueprint, current_app, render_template, request, send_file, url_for
from werkzeug.utils import secure_filename

from .services.formatters import write_outputs
from .services.transcriber import TranscriptionError, transcribe_audio


bp = Blueprint("stt", __name__)

ALLOWED_EXTENSIONS = {
    ".wav",
    ".mp3",
    ".m4a",
    ".mp4",
    ".ogg",
    ".flac",
    ".aac",
    ".webm",
}


def _is_allowed(filename: str) -> bool:
    return Path(filename).suffix.lower() in ALLOWED_EXTENSIONS


@bp.get("/")
def index():
    return render_template("index.html")


@bp.post("/transcribe")
def transcribe():
    audio_file = request.files.get("audio")
    language = request.form.get("language", "vi").strip() or "vi"

    if audio_file is None or not audio_file.filename:
        return render_template("index.html", error="Chưa chọn file audio/video.")

    if not _is_allowed(audio_file.filename):
        return render_template(
            "index.html",
            error="Định dạng chưa được hỗ trợ. Hãy dùng wav, mp3, m4a, mp4, ogg, flac, aac hoặc webm.",
        )

    job_id = uuid4().hex
    upload_dir = current_app.config["UPLOAD_DIR"] / job_id
    output_dir = current_app.config["OUTPUT_DIR"] / job_id
    upload_dir.mkdir(parents=True, exist_ok=True)
    output_dir.mkdir(parents=True, exist_ok=True)

    safe_name = secure_filename(audio_file.filename)
    input_path = upload_dir / safe_name
    audio_file.save(input_path)

    try:
        result = transcribe_audio(input_path, language=language)
        files = write_outputs(result, output_dir, stem=input_path.stem)
    except TranscriptionError as exc:
        return render_template("index.html", error=str(exc))
    except Exception as exc:  # pragma: no cover - defensive error boundary for UI
        return render_template("index.html", error=f"Không thể bóc băng: {exc}")

    downloads = {
        fmt: url_for("stt.download", job_id=job_id, filename=path.name)
        for fmt, path in files.items()
    }

    return render_template(
        "index.html",
        transcript=result["text"],
        chunks=result["chunks"],
        downloads=downloads,
        language=language,
        filename=safe_name,
    )


@bp.get("/downloads/<job_id>/<filename>")
def download(job_id: str, filename: str):
    file_path = current_app.config["OUTPUT_DIR"] / job_id / secure_filename(filename)
    if not file_path.exists():
        return render_template("index.html", error="Không tìm thấy file kết quả."), 404
    return send_file(file_path, as_attachment=True)
