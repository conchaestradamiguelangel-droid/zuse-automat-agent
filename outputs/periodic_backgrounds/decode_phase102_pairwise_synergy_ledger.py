from __future__ import annotations

import argparse
import hashlib
import json
import struct
from pathlib import Path
from typing import Any, Iterator


def load_manifest(path: Path) -> dict[str, Any]:
    manifest = json.loads(path.read_text(encoding="utf-8"))
    required = {
        "byte_order",
        "record_format",
        "record_size",
        "record_count",
        "ledger_size",
        "ledger_sha256",
        "fields",
        "flag_bits",
    }
    missing = required - set(manifest)
    if missing:
        raise ValueError(f"Manifest is missing fields: {sorted(missing)}")
    if manifest["byte_order"] != "little-endian":
        raise ValueError("Only little-endian ledgers are supported")
    record = struct.Struct(manifest["record_format"])
    if not manifest["record_format"].startswith("<"):
        raise ValueError("Record format does not declare little-endian order")
    if record.size != int(manifest["record_size"]):
        raise ValueError("Manifest record size disagrees with struct format")
    return manifest


def validate_ledger(path: Path, manifest: dict[str, Any]) -> None:
    expected_size = int(manifest["record_size"]) * int(manifest["record_count"])
    if expected_size != int(manifest["ledger_size"]):
        raise ValueError("Manifest ledger-size arithmetic is inconsistent")
    if path.stat().st_size != expected_size:
        raise ValueError("Ledger file size does not match manifest")
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    if digest != manifest["ledger_sha256"]:
        raise ValueError("Ledger SHA-256 does not match manifest")


def decode_flags(mask: int, flag_bits: dict[str, int]) -> dict[str, bool]:
    return {
        name: bool(mask & (1 << int(bit)))
        for name, bit in sorted(flag_bits.items(), key=lambda item: int(item[1]))
    }


def decode_rows(path: Path, manifest: dict[str, Any]) -> Iterator[dict[str, Any]]:
    validate_ledger(path, manifest)
    record = struct.Struct(manifest["record_format"])
    names = [field["name"] for field in manifest["fields"]]
    if len(names) != len(record.unpack(b"\0" * record.size)):
        raise ValueError("Manifest field count disagrees with struct format")
    with path.open("rb") as handle:
        for record_index in range(int(manifest["record_count"])):
            raw = handle.read(record.size)
            if len(raw) != record.size:
                raise ValueError(f"Truncated record at index {record_index}")
            values = dict(zip(names, record.unpack(raw), strict=True))
            flag_mask = int(values.pop("flags"))
            yield {
                "record_index": record_index,
                **values,
                "flags": flag_mask,
                "decoded_flags": decode_flags(flag_mask, manifest["flag_bits"]),
            }
        if handle.read(1):
            raise ValueError("Ledger contains trailing bytes")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Decode the Fase-103 pairwise-synergy ledger")
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
