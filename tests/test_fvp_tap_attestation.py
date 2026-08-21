from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys

import pytest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts/test"))

from run_test_fvp_tap_attestation import (  # noqa: E402
    AttestationState,
    attestation_is_fresh,
    write_attestation,
)


def _state(path: Path) -> AttestationState:
    payload = b"root-owned-state\n"
    path.write_bytes(payload)
    return AttestationState(
        state_sha256=hashlib.sha256(payload).hexdigest(),
        pid=42,
        start_time="123",
        nonce="a" * 32,
        argv_sha256="b" * 64,
        nft_semantic_digest="c" * 64,
    )


def test_root_attestation_round_trip_binds_all_current_identity_fields(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # Given: the exact state digest and root verifier output at time 1000.
    state_path = tmp_path / "state"
    receipt_path = tmp_path / "attestation"
    state = _state(state_path)
    monkeypatch.setattr("run_test_fvp_tap_attestation._metadata", lambda _path: (0, 0o644))

    # When: root writes then the runner validates the fresh receipt.
    write_attestation(receipt_path, state, issued_at=1000)
    result = attestation_is_fresh(receipt_path, state_path, state, now=1001)

    # Then: the unchanged root state and every identity field bind successfully.
    assert result


@pytest.mark.parametrize(
    "mutation",
    [
        {"issued_at": 600},
        {"issued_at": 2000},
        {"pid": 43},
        {"nonce": "d" * 32},
        {"argv_sha256": "d" * 64},
        {"state_sha256": "d" * 64},
        {"unknown": "replay"},
    ],
)
def test_stale_or_drifted_attestation_fails_closed(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    mutation: dict[str, int | str],
) -> None:
    # Given: a valid receipt with one replay, clock, state, or identity mutation.
    state_path = tmp_path / "state"
    receipt_path = tmp_path / "attestation"
    state = _state(state_path)
    write_attestation(receipt_path, state, issued_at=1000)
    data = json.loads(receipt_path.read_text(encoding="utf-8"))
    data.update(mutation)
    receipt_path.write_text(json.dumps(data), encoding="utf-8")
    monkeypatch.setattr("run_test_fvp_tap_attestation._metadata", lambda _path: (0, 0o644))

    # When: the unprivileged runner reads the receipt at time 1001.
    result = attestation_is_fresh(receipt_path, state_path, state, now=1001)

    # Then: no stale, future, replayed, or drifted attestation can pass.
    assert not result


@pytest.mark.parametrize("metadata", [(1000, 0o644), (0, 0o600)])
def test_foreign_owned_or_nonpublic_attestation_fails_closed(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    metadata: tuple[int, int],
) -> None:
    # Given: a byte-identical receipt whose ownership or mode is not trusted.
    state_path = tmp_path / "state"
    receipt_path = tmp_path / "attestation"
    state = _state(state_path)
    write_attestation(receipt_path, state, issued_at=1000)
    monkeypatch.setattr("run_test_fvp_tap_attestation._metadata", lambda _path: metadata)

    # When: the unprivileged runner evaluates the receipt freshness boundary.
    result = attestation_is_fresh(receipt_path, state_path, state, now=1001)

    # Then: only root-owned exactly-0644 receipts are trusted.
    assert not result


def test_changed_root_state_invalidates_an_unchanged_attestation(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # Given: a valid receipt created before the root state changes.
    state_path = tmp_path / "state"
    receipt_path = tmp_path / "attestation"
    state = _state(state_path)
    write_attestation(receipt_path, state, issued_at=1000)
    state_path.write_text("changed-root-state\n", encoding="utf-8")
    monkeypatch.setattr("run_test_fvp_tap_attestation._metadata", lambda _path: (0, 0o644))

    # When: the runner observes the same receipt against the changed state.
    result = attestation_is_fresh(receipt_path, state_path, state, now=1001)

    # Then: state drift blocks before any runtime launch.
    assert not result
