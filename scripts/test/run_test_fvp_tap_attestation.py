from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import os
from pathlib import Path
import time
from typing import Final


VERSION: Final = 1
TTL_SECONDS: Final = 300
FUTURE_SKEW_SECONDS: Final = 5
FIELDS: Final = frozenset(
    {
        "version", "issued_at", "state_sha256", "pid", "start_time",
        "nonce", "argv_sha256", "nft_semantic_digest",
    }
)


@dataclass(frozen=True, slots=True)
class AttestationState:
    state_sha256: str
    pid: int
    start_time: str
    nonce: str
    argv_sha256: str
    nft_semantic_digest: str

    def as_json(self, issued_at: int) -> dict[str, int | str]:
        return {
            "version": VERSION,
            "issued_at": issued_at,
            "state_sha256": self.state_sha256,
            "pid": self.pid,
            "start_time": self.start_time,
            "nonce": self.nonce,
            "argv_sha256": self.argv_sha256,
            "nft_semantic_digest": self.nft_semantic_digest,
        }


def _metadata(path: Path) -> tuple[int, int]:
    data = path.stat()
    return data.st_uid, data.st_mode & 0o777


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_attestation(path: Path, state: AttestationState, issued_at: int | None = None) -> None:
    timestamp = int(time.time()) if issued_at is None else issued_at
    temporary = path.with_name(f"{path.name}.{os.getpid()}.tmp")
    temporary.write_text(
        json.dumps(state.as_json(timestamp), sort_keys=True) + "\n",
        encoding="utf-8",
    )
    os.chmod(temporary, 0o644)
    os.replace(temporary, path)


def attestation_is_fresh(
    path: Path,
    state_path: Path,
    state: AttestationState,
    now: int | None = None,
) -> bool:
    timestamp = int(time.time()) if now is None else now
    try:
        owner, mode = _metadata(path)
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, OSError, json.JSONDecodeError):
        return False
    if owner != 0 or mode != 0o644 or not isinstance(payload, dict):
        return False
    if set(payload) != FIELDS:
        return False
    issued_at = payload.get("issued_at")
    if type(issued_at) is not int or issued_at > timestamp + FUTURE_SKEW_SECONDS:
        return False
    if timestamp - issued_at > TTL_SECONDS:
        return False
    try:
        current_hash = _sha256(state_path)
    except OSError:
        return False
    return payload == state.as_json(issued_at) and current_hash == state.state_sha256
