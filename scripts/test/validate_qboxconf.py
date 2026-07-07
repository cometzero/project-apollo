#!/usr/bin/env python3
from __future__ import annotations

import argparse
from dataclasses import dataclass
import json
from pathlib import Path, PurePosixPath
import sys
from typing import Final


JsonScalar = str | int | float | bool | None
JsonValue = JsonScalar | list[str] | list["JsonValue"] | dict[str, "JsonValue"]

REQUIRED_PROVIDER_FIELDS: Final = ("name", "bindir", "libdir", "module_dir", "data_dir")
REQUIRED_SYSROOT_FIELDS: Final = ("components_dir", "recipe_sysroot_native")
SAFE_RELATIVE_FIELDS: Final = ("exe", "config")


@dataclass(frozen=True, slots=True)
class MissingRequired:
    id: str
    path: str
    kind: str
    reason: str

    def to_json(self) -> dict[str, JsonValue]:
        return {"id": self.id, "path": self.path, "kind": self.kind, "reason": self.reason}


@dataclass(frozen=True, slots=True)
class Check:
    name: str
    missing: tuple[MissingRequired, ...]
    details: dict[str, JsonValue]

    def to_json(self) -> dict[str, JsonValue]:
        status = "pass" if not self.missing else "fail"
        return {"name": self.name, "status": status, "details": self.details}


def missing(item_id: str, path: str, kind: str, reason: str) -> MissingRequired:
    return MissingRequired(item_id, path, kind, reason)


def load_qboxconf(path: Path) -> tuple[dict[str, JsonValue] | None, Check]:
    try:
        loaded = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        item = missing("qboxconf:file", path.as_posix(), "file", "qboxconf file is missing")
        return None, Check("json", (item,), {"path": path.as_posix()})
    except PermissionError:
        item = missing("qboxconf:read", path.as_posix(), "file", "qboxconf file is not readable")
        return None, Check("json", (item,), {"path": path.as_posix()})
    except json.JSONDecodeError as error:
        item = missing("json:malformed", path.as_posix(), "json", f"invalid JSON: {error.msg}")
        return None, Check("json", (item,), {"path": path.as_posix(), "line": error.lineno, "column": error.colno})
    if isinstance(loaded, dict):
        return loaded, Check("json", (), {"path": path.as_posix()})
    item = missing("schema:root", path.as_posix(), "schema", "qboxconf root must be a JSON object")
    return None, Check("json", (item,), {"path": path.as_posix()})


def field_value(data: dict[str, JsonValue], key: str) -> JsonValue | None:
    return data.get(key)


def string_map(data: dict[str, JsonValue] | None, field: str) -> dict[str, str]:
    value = field_value(data, field) if data is not None else None
    if not isinstance(value, dict):
        return {}
    return {key: item for key, item in value.items() if isinstance(key, str) and isinstance(item, str)}


def required_section_fields(
    data: dict[str, JsonValue] | None,
    section: str,
    fields: tuple[str, ...],
) -> Check:
    values = string_map(data, section)
    missing_items = [
        missing(f"{section}:{field}", f"{section}.{field}", section, "required string field is missing")
        for field in fields
        if not values.get(field)
    ]
    return Check(section, tuple(missing_items), {"required": list(fields), "present": sorted(values)})


def is_safe_relative_path(value: str) -> bool:
    path = PurePosixPath(value)
    if path.is_absolute():
        return False
    if value == "":
        return False
    if "\x00" in value:
        return False
    return ".." not in path.parts


def check_relative_field(data: dict[str, JsonValue] | None, field: str) -> MissingRequired | None:
    value = field_value(data, field) if data is not None else None
    if not isinstance(value, str) or not is_safe_relative_path(value):
        return missing(f"path:{field}", field, "path", "field must be a safe relative path")
    return None


def check_images(data: dict[str, JsonValue] | None) -> tuple[MissingRequired, ...]:
    value = field_value(data, "images") if data is not None else None
    if value is None:
        return ()
    if not isinstance(value, dict):
        return (missing("schema:images", "images", "schema", "images must be a JSON object"),)
    missing_items: list[MissingRequired] = []
    for key, item in value.items():
        if not isinstance(key, str):
            continue
        if not isinstance(item, str) or not is_safe_relative_path(item):
            missing_items.append(missing(f"path:images:{key}", f"images.{key}", "path", "image artifact must be a safe relative path"))
    return tuple(missing_items)


def check_optional_string_maps(data: dict[str, JsonValue] | None) -> tuple[MissingRequired, ...]:
    missing_items: list[MissingRequired] = []
    for field in ("env",):
        value = field_value(data, field) if data is not None else None
        if value is None:
            continue
        if not isinstance(value, dict):
            missing_items.append(missing(f"schema:{field}", field, "schema", f"{field} must be a JSON object"))
            continue
        for key, item in value.items():
            if not isinstance(key, str) or not isinstance(item, str):
                missing_items.append(missing(f"schema:{field}:{key}", f"{field}.{key}", "schema", f"{field} values must be strings"))
    return tuple(missing_items)


def check_data_list(data: dict[str, JsonValue] | None) -> tuple[MissingRequired, ...]:
    value = field_value(data, "data") if data is not None else None
    if value is None:
        return ()
    if not isinstance(value, list):
        return (missing("schema:data", "data", "schema", "data must be a JSON array"),)
    bad_indexes = [
        missing(f"schema:data:{index}", f"data.{index}", "schema", "data entries must be strings")
        for index, item in enumerate(value)
        if not isinstance(item, str)
    ]
    return tuple(bad_indexes)


def check_shape(data: dict[str, JsonValue] | None) -> Check:
    missing_items: list[MissingRequired] = []
    for field in SAFE_RELATIVE_FIELDS:
        item = check_relative_field(data, field)
        if item is not None:
            missing_items.append(item)
    missing_items.extend(check_images(data))
    missing_items.extend(check_data_list(data))
    missing_items.extend(check_optional_string_maps(data))
    return Check("shape", tuple(missing_items), {"safe_relative_fields": list(SAFE_RELATIVE_FIELDS)})


def check_paths(data: dict[str, JsonValue] | None) -> Check:
    provider = string_map(data, "provider")
    sysroot = string_map(data, "sysroot")
    values = {
        "provider.bindir": provider.get("bindir", ""),
        "provider.libdir": provider.get("libdir", ""),
        "provider.module_dir": provider.get("module_dir", ""),
        "provider.data_dir": provider.get("data_dir", ""),
        "sysroot.components_dir": sysroot.get("components_dir", ""),
        "sysroot.recipe_sysroot_native": sysroot.get("recipe_sysroot_native", ""),
    }
    missing_items = [
        missing(f"path:{key}", key, "path", "provider and sysroot paths must be absolute")
        for key, value in values.items()
        if value and not Path(value).is_absolute()
    ]
    return Check("paths", tuple(missing_items), {"absolute_fields": sorted(values)})


def validate_qboxconf(path: Path) -> dict[str, JsonValue]:
    resolved = path.resolve()
    data, json_check = load_qboxconf(resolved)
    checks = (
        json_check,
        required_section_fields(data, "provider", REQUIRED_PROVIDER_FIELDS),
        required_section_fields(data, "sysroot", REQUIRED_SYSROOT_FIELDS),
        check_shape(data),
        check_paths(data),
    )
    missing_items = [item for check in checks for item in check.missing]
    return {
        "status": "pass" if not missing_items else "fail",
        "qboxconf": str(resolved),
        "missing_required": [item.to_json() for item in missing_items],
        "checks": [check.to_json() for check in checks],
    }


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate a QBox .qboxconf JSON file.")
    parser.add_argument("--qboxconf", required=True, type=Path, help=".qboxconf JSON file")
    parser.add_argument("--output", required=True, type=Path, help="JSON report output path")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(sys.argv[1:] if argv is None else argv)
    result = validate_qboxconf(args.qboxconf)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return 0 if result["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
