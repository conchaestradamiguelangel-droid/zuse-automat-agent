from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any, Iterator


def raw_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_manifest(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if value.get("format") != "canonical-jsonl-one-model-per-line":
        raise ValueError("Unsupported QUBO model format")
    if not value.get("integer_coefficients"):
        raise ValueError("QUBO coefficients are not declared integer")
    return value


def validate_models(path: Path, manifest: dict[str, Any]) -> None:
    if path.stat().st_size != int(manifest["models_size"]):
        raise ValueError("QUBO models size mismatch")
    if raw_sha256(path) != manifest["models_sha256"]:
        raise ValueError("QUBO models SHA-256 mismatch")


def iter_models(path: Path, manifest: dict[str, Any]) -> Iterator[dict[str, Any]]:
    validate_models(path, manifest)
    count = 0
    with path.open("r", encoding="utf-8", newline="") as handle:
        for line in handle:
            if not line.endswith("\n"):
                raise ValueError("QUBO JSONL line is not newline terminated")
            model = json.loads(line)
            if model["variables"]["total_count"] != (
                model["variables"]["x_count"] + model["variables"]["z_count"]
            ):
                raise ValueError("QUBO variable count mismatch")
            yield model
            count += 1
    if count != int(manifest["model_count"]):
        raise ValueError("QUBO model count mismatch")


def main() -> None:
    parser = argparse.ArgumentParser(description="Decode Fase 107 QUBO JSONL models")
    parser.add_argument("models", type=Path)
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--limit", type=int)
    args = parser.parse_args()
    manifest = load_manifest(args.manifest)
    for index, model in enumerate(iter_models(args.models, manifest)):
        if args.limit is not None and index >= args.limit:
            break
        print(json.dumps(model, sort_keys=True))


if __name__ == "__main__":
    main()
