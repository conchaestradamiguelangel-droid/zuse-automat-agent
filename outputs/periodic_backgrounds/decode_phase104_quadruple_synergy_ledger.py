from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import math
import struct
from pathlib import Path
from typing import Any, Iterator


def canonical_words_sha256(words: list[int]) -> str:
    payload = json.dumps(words, separators=(",", ":")).encode("ascii")
    return hashlib.sha256(payload).hexdigest()


def load_manifest(path: Path) -> dict[str, Any]:
    manifest = json.loads(path.read_text(encoding="utf-8"))
    required = {
        "byte_order",
        "record_format",
        "record_size",
        "record_count",
        "ledger_size",
        "ledger_sha256",
        "flag_bits",
        "reserved_bits",
        "segments",
    }
    missing = required - set(manifest)
    if missing:
        raise ValueError(f"Manifest is missing fields: {sorted(missing)}")
    if manifest["byte_order"] != "little-endian":
        raise ValueError("Only little-endian ledgers are supported")
    record = struct.Struct(manifest["record_format"])
    if not manifest["record_format"].startswith("<") or record.size != int(
        manifest["record_size"]
    ):
        raise ValueError("Manifest record layout is inconsistent")
    validate_segments(manifest)
    return manifest


def validate_segments(manifest: dict[str, Any]) -> None:
    offset = 0
    for expected_index, segment in enumerate(manifest["segments"]):
        words = [int(word) for word in segment["ordered_words"]]
        if words != sorted(set(words)) or any(not 0 <= word <= 255 for word in words):
            raise ValueError("Segment words must be sorted unique uint8 values")
        if int(segment["stratum_index"]) != expected_index:
            raise ValueError("Segment indices are not contiguous")
        if canonical_words_sha256(words) != segment["ordered_words_sha256"]:
            raise ValueError("Segment ordered-word digest mismatch")
        count = math.comb(len(words), 4)
        if count != int(segment["record_count"]):
            raise ValueError("Segment combination count mismatch")
        if int(segment["record_offset"]) != offset:
            raise ValueError("Segment record offsets are not contiguous")
        offset += count
    if offset != int(manifest["record_count"]):
        raise ValueError("Segment records do not reconcile with the manifest")


def validate_ledger(path: Path, manifest: dict[str, Any]) -> None:
    expected_size = int(manifest["record_count"]) * int(manifest["record_size"])
    if expected_size != int(manifest["ledger_size"]):
        raise ValueError("Manifest ledger-size arithmetic is inconsistent")
    if path.stat().st_size != expected_size:
        raise ValueError("Ledger file size does not match manifest")
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    if digest != manifest["ledger_sha256"]:
        raise ValueError("Ledger SHA-256 does not match manifest")


def decode_flags(mask: int, manifest: dict[str, Any]) -> dict[str, Any]:
    decoded = {
        name: bool(mask & (1 << int(bit)))
        for name, bit in sorted(
            manifest["flag_bits"].items(), key=lambda item: int(item[1])
        )
    }
    decoded["internal_edge_count"] = mask & 0b111
    decoded["reserved_bits_nonzero"] = bool(
        mask & sum(1 << int(bit) for bit in manifest["reserved_bits"])
    )
    return decoded


def decode_rows(path: Path, manifest: dict[str, Any]) -> Iterator[dict[str, Any]]:
    validate_ledger(path, manifest)
    record = struct.Struct(manifest["record_format"])
    record_index = 0
    with path.open("rb") as handle:
        for segment in manifest["segments"]:
            words = [int(word) for word in segment["ordered_words"]]
            for quartet in itertools.combinations(words, 4):
                raw = handle.read(record.size)
                if len(raw) != record.size:
                    raise ValueError(f"Truncated record at index {record_index}")
                (flags,) = record.unpack(raw)
                yield {
                    "record_index": record_index,
                    "stratum_index": int(segment["stratum_index"]),
                    "quartet": list(quartet),
                    "flags": flags,
                    "decoded_flags": decode_flags(flags, manifest),
                }
                record_index += 1
        if handle.read(1):
            raise ValueError("Ledger contains trailing bytes")
    if record_index != int(manifest["record_count"]):
        raise ValueError("Decoded record count does not match manifest")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Decode the Fase-105 quartet ledger")
    parser.add_argument("ledger", type=Path)
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--limit", type=int, default=None)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    manifest = load_manifest(args.manifest)
    for index, row in enumerate(decode_rows(args.ledger, manifest)):
        if args.limit is not None and index >= args.limit:
            break
        print(json.dumps(row, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
