from pathlib import Path


def _format_timestamp(seconds: float | None) -> str:
    if seconds is None:
        return "00:00:00,000"

    total_milliseconds = int(seconds * 1000)
    hours, remainder = divmod(total_milliseconds, 3_600_000)
    minutes, remainder = divmod(remainder, 60_000)
    secs, milliseconds = divmod(remainder, 1000)
    return f"{hours:02}:{minutes:02}:{secs:02},{milliseconds:03}"


def build_srt(chunks: list[dict]) -> str:
    entries = []

    for index, chunk in enumerate(chunks, start=1):
        start = chunk.get("start")
        end = chunk.get("end")
        if start is None and end is None:
            start = 0.0
            end = max(3.0, len(chunk.get("text", "").split()) * 0.45)
        elif end is None and start is not None:
            end = start + max(3.0, len(chunk.get("text", "").split()) * 0.45)

        entries.append(
            "\n".join(
                [
                    str(index),
                    f"{_format_timestamp(start)} --> {_format_timestamp(end)}",
                    chunk.get("text", "").strip(),
                ]
            )
        )

    return "\n\n".join(entries).strip() + "\n"


def write_outputs(result: dict, output_dir: str | Path, stem: str) -> dict[str, Path]:
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    txt_path = output_dir / f"{stem}.txt"
    srt_path = output_dir / f"{stem}.srt"
    json_path = output_dir / f"{stem}.json"

    txt_path.write_text(result["text"].strip() + "\n", encoding="utf-8")
    srt_path.write_text(build_srt(result["chunks"]), encoding="utf-8")
    json_path.write_text(_to_json(result), encoding="utf-8")

    return {"txt": txt_path, "srt": srt_path, "json": json_path}


def _to_json(result: dict) -> str:
    import json

    return json.dumps(result, ensure_ascii=False, indent=2)
