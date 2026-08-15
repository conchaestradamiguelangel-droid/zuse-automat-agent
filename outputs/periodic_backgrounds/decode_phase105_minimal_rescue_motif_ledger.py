from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any, Iterator


def load_manifest(path: Path) -> dict[str, Any]:
    manifest = json.loads(path.read_text(encoding="utf-8"))
    required = {"record_size", "record_count", "ledger_size", "ledger_sha256", "motif_ids", "segments", "encoding"}
    missing = required - set(manifest)
    if missing:
        raise ValueError(f"Manifest missing fields: {sorted(missing)}")
    if int(manifest["record_size"]) != 1 or int(manifest["record_count"]) != int(manifest["ledger_size"]):
        raise ValueError("Geometry manifest record arithmetic is inconsistent")
    validate_segments(manifest)
    return manifest


def validate_segments(manifest: dict[str, Any]) -> None:
    offset = 0
    for segment in manifest["segments"]:
        if int(segment["geometry_record_offset"]) != offset:
            raise ValueError("Geometry segment offsets are not contiguous")
        if int(segment["cardinality"]) not in (2, 3, 4):
            raise ValueError("Unsupported cardinality")
        offset += int(segment["record_count"])
    if offset != int(manifest["record_count"]):
        raise ValueError("Geometry segment counts do not reconcile")


def validate_ledger(path: Path, manifest: dict[str, Any]) -> None:
    if path.stat().st_size != int(manifest["ledger_size"]):
        raise ValueError("Geometry ledger size mismatch")
    if hashlib.sha256(path.read_bytes()).hexdigest() != manifest["ledger_sha256"]:
        raise ValueError("Geometry ledger SHA-256 mismatch")


def decode_byte(value: int, manifest: dict[str, Any]) -> dict[str, Any]:
    if value & 0x80:
        raise ValueError("Reserved geometry bit is nonzero")
    motif_id = value & 0x0F
    inverse = {int(identifier): name for name, identifier in manifest["motif_ids"].items()}
    if motif_id not in inverse:
        raise ValueError("Unknown motif id")
    return {"motif_id": motif_id, "motif": inverse[motif_id], "internal_edge_count": (value >> 4) & 0x07}


def decode_rows(path: Path, manifest: dict[str, Any]) -> Iterator[dict[str, Any]]:
    validate_ledger(path, manifest)
    with path.open("rb") as handle:
        global_index = 0
        for segment in manifest["segments"]:
            for local_index in range(int(segment["record_count"])):
                raw = handle.read(1)
                if len(raw) != 1:
                    raise ValueError("Truncated geometry ledger")
                yield {
                    "global_record_index": global_index,
                    "local_record_index": local_index,
                    "cardinality": int(segment["cardinality"]),
                    "source_name": segment["source_name"],
                    "stratum_index": int(segment["stratum_index"]),
                    **decode_byte(raw[0], manifest),
                }
                global_index += 1
        if handle.read(1):
            raise ValueError("Geometry ledger has trailing bytes")


def main() -> int:
    parser = argparse.ArgumentParser(description="Decode the Fase-106 outcome-blind motif ledger")
    parser.add_argument("ledger", type=Path)
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--limit", type=int)
    args = parser.parse_args()
    manifest = load_manifest(args.manifest)
    for index, row in enumerate(decode_rows(args.ledger, manifest)):
        if args.limit is not None and index >= args.limit:
            break
        print(json.dumps(row, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
