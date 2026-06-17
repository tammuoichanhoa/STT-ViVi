import warnings
import wave
from pathlib import Path
from time import perf_counter
from threading import Lock

import numpy as np
import torchaudio
from transformers import pipeline

from app.runtime import application_root


warnings.filterwarnings(
    "ignore",
    message="The input name `inputs` is deprecated.*",
    category=FutureWarning,
)

BASE_DIR = application_root()
MODEL_DIR = BASE_DIR / "models"
AVAILABLE_MODEL_SIZES = ("tiny", "small", "base", "medium", "large")
DEFAULT_MODEL_SIZE = "small"

_transcribers = {}
_transcriber_lock = Lock()


class TranscriptionError(RuntimeError):
    pass


def _is_missing_ffmpeg_error(exc: Exception) -> bool:
    return "ffmpeg was not found" in str(exc).lower()


def _load_wav_with_stdlib(path: Path) -> dict:
    with wave.open(str(path), "rb") as wav_file:
        if wav_file.getcomptype() != "NONE":
            raise TranscriptionError(
                "File wav đang dùng codec nén. Hãy chuyển sang PCM wav hoặc cài ffmpeg."
            )

        channels = wav_file.getnchannels()
        sample_width = wav_file.getsampwidth()
        sampling_rate = wav_file.getframerate()
        frame_count = wav_file.getnframes()
        frames = wav_file.readframes(frame_count)

    if not frames:
        raise TranscriptionError("File audio không có dữ liệu âm thanh.")

    if sample_width == 1:
        audio = (np.frombuffer(frames, dtype=np.uint8).astype(np.float32) - 128) / 128
    elif sample_width == 2:
        audio = np.frombuffer(frames, dtype="<i2").astype(np.float32) / 32768
    elif sample_width == 3:
        raw = np.frombuffer(frames, dtype=np.uint8).reshape(-1, 3)
        signed = (
            raw[:, 0].astype(np.int32)
            | (raw[:, 1].astype(np.int32) << 8)
            | (raw[:, 2].astype(np.int32) << 16)
        )
        signed = np.where(signed & 0x800000, signed | ~0xFFFFFF, signed)
        audio = signed.astype(np.float32) / 8388608
    elif sample_width == 4:
        audio = np.frombuffer(frames, dtype="<i4").astype(np.float32) / 2147483648
    else:
        raise TranscriptionError(
            f"File wav có sample width {sample_width} byte chưa được hỗ trợ. Hãy cài ffmpeg."
        )

    if channels > 1:
        audio = audio.reshape(-1, channels).mean(axis=1)

    return {"array": audio.astype(np.float32, copy=False), "sampling_rate": sampling_rate}


def _load_audio_for_pipeline(path: Path) -> dict:
    if path.suffix.lower() == ".wav":
        try:
            return _load_wav_with_stdlib(path)
        except wave.Error as exc:
            raise TranscriptionError(
                "Không đọc được file wav. Hãy kiểm tra file có hợp lệ không hoặc cài ffmpeg."
            ) from exc

    try:
        waveform, sampling_rate = torchaudio.load(str(path))
    except Exception as exc:  # pragma: no cover - depends on local codecs/backend
        raise TranscriptionError(
            "Không đọc được file audio vì máy chưa có ffmpeg. "
            "Với wav/flac, hãy kiểm tra file có hợp lệ không. "
            "Với mp3/mp4/m4a/aac/webm, hãy cài ffmpeg hoặc torchcodec rồi chạy lại."
        ) from exc

    if waveform.numel() == 0:
        raise TranscriptionError("File audio không có dữ liệu âm thanh.")

    if waveform.ndim == 2 and waveform.shape[0] > 1:
        waveform = waveform.mean(dim=0)
    else:
        waveform = waveform.squeeze(0)

    return {
        "array": waveform.detach().cpu().float().numpy(),
        "sampling_rate": sampling_rate,
    }


def _call_transcriber(transcriber, audio_input, language: str):
    try:
        return transcriber(
            dict(audio_input) if isinstance(audio_input, dict) else audio_input,
            return_timestamps=True,
            generate_kwargs={"language": language},
        )
    except TypeError:
        return transcriber(
            dict(audio_input) if isinstance(audio_input, dict) else audio_input,
            generate_kwargs={"language": language},
        )


def get_model_options() -> list[dict]:
    return [
        {
            "size": size,
            "label": f"PhoWhisper {size}",
            "path": MODEL_DIR / f"PhoWhisper-{size}",
            "available": (MODEL_DIR / f"PhoWhisper-{size}").is_dir(),
        }
        for size in AVAILABLE_MODEL_SIZES
    ]


def _resolve_model_path(model_size: str) -> Path:
    size = (model_size or DEFAULT_MODEL_SIZE).strip().lower()
    if size not in AVAILABLE_MODEL_SIZES:
        raise TranscriptionError(
            "Model không hợp lệ. Hãy chọn một trong: tiny, base, small, medium, large."
        )

    model_path = MODEL_DIR / f"PhoWhisper-{size}"
    if not model_path.is_dir():
        raise TranscriptionError(
            f"Chưa có model local: {model_path}. Hãy chạy `python download_models.py {size}` trước."
        )

    return model_path


def _get_transcriber(model_size: str):
    model_path = _resolve_model_path(model_size)
    cache_key = model_path.name

    if cache_key in _transcribers:
        return _transcribers[cache_key]

    with _transcriber_lock:
        if cache_key not in _transcribers:
            try:
                _transcribers[cache_key] = pipeline(
                    "automatic-speech-recognition",
                    model=str(model_path),
                    tokenizer=str(model_path),
                    feature_extractor=str(model_path),
                    device=-1,
                )
            except Exception as exc:  # pragma: no cover - depends on local runtime/model cache
                raise TranscriptionError(
                    f"Không thể tải model local {model_path}. Kiểm tra thư mục model và môi trường Python."
                ) from exc

    return _transcribers[cache_key]


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


def transcribe_audio(
    audio_path: str | Path,
    language: str = "vi",
    model_size: str = DEFAULT_MODEL_SIZE,
) -> dict:
    path = Path(audio_path)
    if not path.exists():
        raise TranscriptionError(f"Không tìm thấy file: {path}")

    inference_started_at = perf_counter()

    try:
        transcriber = _get_transcriber(model_size)

        try:
            result = _call_transcriber(transcriber, str(path), language)
        except Exception as exc:
            if not _is_missing_ffmpeg_error(exc):
                raise TranscriptionError(f"Model không xử lý được file {path.name}: {exc}") from exc

            try:
                audio_input = _load_audio_for_pipeline(path)
                result = _call_transcriber(transcriber, audio_input, language)
            except TranscriptionError:
                raise
            except Exception as fallback_exc:
                raise TranscriptionError(
                    f"Model không xử lý được file {path.name}: {fallback_exc}"
                ) from fallback_exc
    finally:
        inference_elapsed_seconds = perf_counter() - inference_started_at

    text = (result.get("text") or "").strip()
    if not text:
        raise TranscriptionError("Model không trả về nội dung transcript.")

    chunks = _normalize_chunks(result.get("chunks"), text)
    return {
        "text": text,
        "chunks": chunks,
        "language": language,
        "model_size": model_size,
        "source": path.name,
        "inference_seconds": round(inference_elapsed_seconds, 3),
    }
