from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import tempfile
from typing import Mapping

from apollo_pcie_its_boundary_contract import BoundaryError, Json, JsonValue

def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def load_json(path: Path, reason: str) -> Json:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise BoundaryError(reason) from error
    if not isinstance(value, dict):
        raise BoundaryError(reason)
    return value

def atomic_write(path: Path, payload: Mapping[str, JsonValue]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=path.parent, delete=False) as stream:
        json.dump(payload, stream, indent=2, sort_keys=True)
        stream.write("\n")
        temporary = Path(stream.name)
    os.replace(temporary, path)
