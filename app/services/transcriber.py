import warnings
from pathlib import Path
from threading import Lock

from transformers import pipeline


warnings.filterwarnings(
    "ignore",
    message="The input name `inputs` is deprecated.*",
    category=FutureWarning,
)

MODEL_NAME = "vinai/PhoWhisper-small"

_transcriber = None
_transcriber_lock = Lock()


class TranscriptionError(RuntimeError):
    pass


def _get_transcriber():
    global _transcriber

    if _transcriber is not None:
        return _transcriber

    with _transcriber_lock:
        if _transcriber is None:
            try:
                _transcriber = pipeline(
                    "automatic-speech-recognition",
                    model=MODEL_NAME,
                    device=-1,
                )
            except Exception as exc:  # pragma: no cover - depends on local runtime/model cache
                raise TranscriptionError(
                    f"Không thể tải model {MODEL_NAME}. Kiểm tra môi trường Python và model cache."
                ) from exc

    return _transcriber


def _normalize_chunks(raw_chunks, fallback_text: str):
    normalized = []

    for index, chunk in enumerate(raw_chunks or []):
        timestamp = chunk.get("timestamp") or (None, None)
        start, end = timestamp if len(timestamp) == 2 else (None, None)
        text = (chunk.get("text") or "").strip()
        if not text:
            continue

        normalized.append(
            {
                "id": index + 1,
                "start": float(start) if start is not None else None,
                "end": float(end) if end is not None else None,
                "text": text,
            }
        )

    if normalized:
        return normalized

    return [
        {
            "id": 1,
            "start": None,
            "end": None,
            "text": fallback_text.strip(),
        }
    ]


def transcribe_audio(audio_path: str | Path, language: str = "vi") -> dict:
    path = Path(audio_path)
    if not path.exists():
        raise TranscriptionError(f"Không tìm thấy file: {path}")

    transcriber = _get_transcriber()

    try:
        result = transcriber(
            str(path),
            return_timestamps=True,
            generate_kwargs={"language": language},
        )
    except TypeError:
        result = transcriber(
            str(path),
            generate_kwargs={"language": language},
        )
    except Exception as exc:
        raise TranscriptionError(f"Model không xử lý được file {path.name}: {exc}") from exc

    text = (result.get("text") or "").strip()
    if not text:
        raise TranscriptionError("Model không trả về nội dung transcript.")

    chunks = _normalize_chunks(result.get("chunks"), text)
    return {
        "text": text,
        "chunks": chunks,
        "language": language,
        "source": path.name,
    }
