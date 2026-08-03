#!/usr/bin/env python3
from __future__ import annotations

import argparse
from dataclasses import dataclass
from datetime import UTC, datetime
import hashlib
import json
from pathlib import Path
import shutil
import stat
import sys
from typing import Final
from zoneinfo import ZoneInfo


ROOT: Final = Path(__file__).resolve().parents[2]
SNAPSHOT_FILES: Final = ("manifest.sha256", "snapshot.records")
CONFIG_FILES: Final = ("build/conf/local.conf", "build/conf/bblayers.conf", "build/conf/templateconf.cfg")
KST: Final = ZoneInfo("Asia/Seoul")


type JsonValue = None | bool | int | float | str | list[JsonValue] | dict[str, JsonValue]
type JsonObject = dict[str, JsonValue]


@dataclass(frozen=True, slots=True)
class InputError(RuntimeError):
    reason: str
    detail: str

    def __str__(self) -> str:
        return self.detail


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def read_regular(path: Path) -> bytes:
    try:
        before = path.lstat()
    except FileNotFoundError as exc:
        raise InputError("missing_input", f"missing required input: {path}") from exc
    if stat.S_ISLNK(before.st_mode) or not stat.S_ISREG(before.st_mode):
        raise InputError("invalid_input", f"required input is not a regular non-symlink file: {path}")
    data = path.read_bytes()
    after = path.lstat()
    if (before.st_dev, before.st_ino, before.st_size, before.st_mtime_ns) != (
        after.st_dev,
        after.st_ino,
        after.st_size,
        after.st_mtime_ns,
    ):
        raise InputError("input_changed", f"input changed while reading: {path}")
    return data


def parse_pristine(snapshot: Path) -> tuple[dict[str, dict[str, str]], dict[str, int | str], dict[str, bytes]]:
    try:
        directory = snapshot.lstat()
    except FileNotFoundError as exc:
        raise InputError("missing_input", f"missing pristine snapshot: {snapshot}") from exc
    if stat.S_ISLNK(directory.st_mode) or not stat.S_ISDIR(directory.st_mode):
        raise InputError("invalid_input", f"pristine snapshot is not a directory: {snapshot}")
    entries = {entry.name for entry in snapshot.iterdir()}
    if entries != set(SNAPSHOT_FILES):
        raise InputError("invalid_input", "pristine snapshot has unexpected entries")
    files = {name: read_regular(snapshot / name) for name in SNAPSHOT_FILES}
    manifest = files["manifest.sha256"]
    try:
        digest, filename = manifest.decode("ascii").strip().split("  ", 1)
    except ValueError as exc:
        raise InputError("invalid_input", "invalid pristine manifest format") from exc
    if filename != "snapshot.records" or len(digest) != 64 or any(char not in "0123456789abcdef" for char in digest):
        raise InputError("invalid_input", "invalid pristine manifest contents")
    records = files["snapshot.records"]
    if sha256(records) != digest:
        raise InputError("input_changed", "pristine manifest hash does not match snapshot.records")
    fields = records.split(b"\0")
    if fields[-1] != b"":
        raise InputError("invalid_input", "pristine records do not end with a NUL byte")
    repositories: dict[str, dict[str, str]] = {}
    record_count = 0
    index = 0
    while index < len(fields) - 1:
        kind = fields[index]
        width = 5 if kind == b"meta" else 8 if kind == b"path" else 0
        if width == 0 or index + width > len(fields) - 1:
            raise InputError("invalid_input", "malformed pristine record")
        record = fields[index : index + width]
        if kind == b"meta":
            repo, field, size, value_sha = (item.decode("ascii") for item in record[1:])
            if field not in {"head", "index", "status"} or not size.isdecimal() or len(value_sha) != 64:
                raise InputError("invalid_input", "malformed pristine repository metadata")
            repositories.setdefault(repo, {})[field] = value_sha
        index += width
        record_count += 1
    if not repositories or any(set(values) != {"head", "index", "status"} for values in repositories.values()):
        raise InputError("invalid_input", "pristine repository metadata is incomplete")
    return repositories, {"format_version": 1, "record_count": record_count, "records_sha256": digest, "manifest_sha256": sha256(manifest)}, files


def yocto_configuration() -> dict[str, dict[str, int | str]]:
    return {
        path.name: {"path": relative, "sha256": sha256(data), "bytes": len(data), "value": data.decode("utf-8")}
        for relative in CONFIG_FILES
        for path in [ROOT / relative]
        for data in [read_regular(path)]
    }


def fast_models() -> dict[str, list[dict[str, str]]]:
    executable = shutil.which("FVP_Zena_CSS_Cfg2")
    if executable is None:
        return {"executables": [], "images": []}
    path = Path(executable).resolve()
    return {"executables": [{"path": str(path), "sha256": sha256(read_regular(path))}], "images": []}


def capture(snapshot: Path) -> tuple[JsonObject, dict[str, bytes]]:
    repositories, pristine, files = parse_pristine(snapshot)
    return {
        "format_version": 1,
        "captured_at_kst": datetime.now(KST).isoformat(timespec="seconds"),
        "pristine": pristine,
        "repositories": repositories,
        "yocto_configuration": yocto_configuration(),
        "fast_models": fast_models(),
    }, files


def archive_pristine(destination: Path, files: dict[str, bytes]) -> None:
    if destination.exists() or destination.is_symlink():
        raise InputError("invalid_output", f"pristine archive destination already exists: {destination}")
    destination.mkdir(parents=True)
    for name in SNAPSHOT_FILES:
        path = destination / name
        path.write_bytes(files[name])
        path.chmod(0o400)
    destination.chmod(0o500)


def normalize(value: JsonValue) -> JsonValue:
    if not isinstance(value, dict):
        return value
    return {key: normalize(item) for key, item in value.items() if key not in {"captured_at_kst", "expected_changed_fields"}}


def differences(expected: JsonValue, actual: JsonValue, prefix: str = "") -> list[str]:
    if isinstance(expected, dict) and isinstance(actual, dict):
        keys = set(expected) | set(actual)
        return [field for key in sorted(keys) for field in differences(expected.get(key), actual.get(key), f"{prefix}.{key}".lstrip("."))]
    return [] if expected == actual else [prefix]


def expected_input(path: Path) -> JsonObject:
    try:
        raw = json.loads(read_regular(path).decode("utf-8"))
    except json.JSONDecodeError as exc:
        raise InputError("invalid_expected_input", f"invalid expected input JSON: {path}") from exc
    if not isinstance(raw, dict) or not isinstance(raw.get("expected_changed_fields"), list):
        raise InputError("invalid_expected_input", "expected input lacks expected_changed_fields")
    return raw


def write_json(path: Path, value: JsonValue) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Capture verified Apollo GIC-720AE source inputs without running FVP.")
    parser.add_argument("--pristine-snapshot", type=Path, required=True)
    parser.add_argument("--archive-pristine-to", type=Path)
    parser.add_argument("--verify-only", action="store_true")
    parser.add_argument("--expected-input", type=Path)
    parser.add_argument("--assert-only-changed-field")
    parser.add_argument("--output", type=Path, required=True)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(sys.argv[1:] if argv is None else argv)
    try:
        state, files = capture(args.pristine_snapshot)
        if args.archive_pristine_to is not None:
            archive_pristine(args.archive_pristine_to, files)
        if args.verify_only:
            if args.expected_input is None or args.assert_only_changed_field is None:
                raise InputError("invalid_arguments", "--verify-only requires --expected-input and --assert-only-changed-field")
            expected = expected_input(args.expected_input)
            changed = differences(normalize(expected), normalize(state))
            report = {**state, "reason": "input_changed" if changed else "inputs_match", "changed_fields": changed}
            write_json(args.output, report)
            if changed != [args.assert_only_changed_field] or expected["expected_changed_fields"] != changed:
                print(json.dumps({"reason": report["reason"], "changed_fields": changed}, sort_keys=True), file=sys.stderr)
                return 1
            print(json.dumps({"reason": report["reason"], "changed_fields": changed}, sort_keys=True), file=sys.stderr)
            return 1
        write_json(args.output, state)
        print(json.dumps({"status": "pass", "output": str(args.output)}, sort_keys=True))
        return 0
    except InputError as exc:
        report = {"format_version": 1, "reason": exc.reason, "detail": exc.detail}
        write_json(args.output, report)
        print(json.dumps(report, sort_keys=True), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
