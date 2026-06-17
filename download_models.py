#!/usr/bin/env python3
"""Download PhoWhisper models into the local models/ directory."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

try:
    from huggingface_hub import snapshot_download
except ModuleNotFoundError:  # pragma: no cover - depends on local environment
    print(
        "Missing dependency: huggingface_hub. Run `pip install -r requirements.txt` "
        "or use this project's venv before running the script.",
        file=sys.stderr,
    )
    raise SystemExit(1)


PHOWHISPER_MODELS = {
    "tiny": "vinai/PhoWhisper-tiny",
    "base": "vinai/PhoWhisper-base",
    "small": "vinai/PhoWhisper-small",
    "medium": "vinai/PhoWhisper-medium",
    "large": "vinai/PhoWhisper-large",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Download PhoWhisper models from Hugging Face into ./models.",
    )
    parser.add_argument(
        "models",
        nargs="*",
        choices=sorted(PHOWHISPER_MODELS),
        help="Model sizes to download. Defaults to all PhoWhisper models.",
    )
    parser.add_argument(
        "--output-dir",
        default="models",
        type=Path,
        help="Directory where model folders will be stored. Default: models",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Download even if the target model directory already exists.",
    )
    return parser.parse_args()


def download_model(size: str, repo_id: str, output_dir: Path, force: bool) -> Path:
    target_dir = output_dir / repo_id.split("/")[-1]

    if target_dir.exists() and any(target_dir.iterdir()) and not force:
        print(f"Skip {repo_id}: {target_dir} already exists. Use --force to download again.")
        return target_dir

    print(f"Downloading {repo_id} -> {target_dir}")
    snapshot_download(
        repo_id=repo_id,
        local_dir=target_dir,
        local_dir_use_symlinks=False,
    )
    print(f"Done {size}: {target_dir}")
    return target_dir


def main() -> None:
    args = parse_args()
    output_dir = args.output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    selected_sizes = args.models or list(PHOWHISPER_MODELS)
    for size in selected_sizes:
        download_model(size, PHOWHISPER_MODELS[size], output_dir, args.force)

    print(f"Finished. Models are in: {output_dir}")


if __name__ == "__main__":
    main()
