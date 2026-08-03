#!/usr/bin/env python3

from __future__ import annotations

import json
from pathlib import Path
import re
from typing import Any

import jsonschema
import yaml


class ManifestError(ValueError):
    pass


GUEST_MODULE_PATH = re.compile(
    r"^/lib/modules/[^/]+/extra/gic720ae_test\.ko$"
)


def load_operations(manifest_path: Path, schema_path: Path) -> list[dict[str, Any]]:
    try:
        manifest = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
        jsonschema.Draft202012Validator.check_schema(schema)
        jsonschema.validate(manifest, schema)
    except (
        OSError,
        ValueError,
        yaml.YAMLError,
        jsonschema.exceptions.ValidationError,
        jsonschema.exceptions.SchemaError,
    ) as error:
        raise ManifestError("invalid_operation_manifest") from error
    if not isinstance(manifest, dict) or not isinstance(manifest["operations"], list):
        raise ManifestError("invalid_operation_manifest")
    return manifest["operations"]


def serialize_operation(
    operation: dict[str, Any], *, module_path: Path,
) -> list[bytes]:
    op = operation["op"]
    if op == "insmod":
        if not GUEST_MODULE_PATH.fullmatch(module_path.as_posix()):
            raise ManifestError("module_path_not_provenance_resolved")
        cpu = operation["args"]["target_cpu"]
        return [f"insmod {module_path} target_cpu={cpu}\n".encode()]
    if op == "write":
        path = operation["path"]
        return [f"tee {path}\n".encode(), operation["value"].encode(), b"\x04"]
    if op == "read":
        return [f"cat {operation['path']}\n".encode()]
    if op == "rmmod":
        return [b"rmmod gic720ae_test\n"]
    raise ManifestError("unknown_operation")
