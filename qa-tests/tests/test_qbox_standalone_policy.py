from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path

import pytest

from apollo_validation import qbox_entry
from apollo_validation.root_cli import parse_root_args
from apollo_validation.provenance import JsonValue


@dataclass(frozen=True, slots=True)
class FakeProvenance:
    profile_id: str

    def as_json(self) -> dict[str, JsonValue]:
        return {"profile_id": self.profile_id}


def test_only_platform_devices_is_standalone() -> None:
    requires = getattr(qbox_entry, "profile_requires_fvp_reference", None)

    assert callable(requires)
    assert requires("platform-devices") is False
    assert requires("pfdi") is True
    assert requires("platform-device") is True
    assert requires("platform-devices-extra") is True
    assert requires("unknown") is True


def test_platform_devices_without_reference_reaches_context(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    context_calls: list[str] = []
    monkeypatch.setattr(qbox_entry, "_validate_request", lambda *_args: None)
    monkeypatch.setattr(
        qbox_entry,
        "prepare_selection",
        lambda _root, options: (None, options),
    )
    monkeypatch.setattr(
        qbox_entry,
        "_write_qbox_context",
        lambda _root, options, _run_dir: context_calls.append(
            options.test_profile or ""
        )
        or 0,
    )
    monkeypatch.setattr(qbox_entry, "run_qbox_category", lambda *_args: 0)
    monkeypatch.setattr(qbox_entry, "_print_result", lambda *_args: 0)

    result = qbox_entry.run_qbox_root(
        tmp_path,
        [
            "--machine",
            "apollo-qvp",
            "--test-profile",
            "platform-devices",
            "--dry-run",
        ],
    )

    assert result == 0
    assert context_calls == ["platform-devices"]


def test_standalone_context_records_provenance_without_fake_reference(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    captured: dict[str, JsonValue] = {}
    options = parse_root_args(
        [
            "--machine",
            "apollo-qvp",
            "--test-profile",
            "platform-devices",
        ]
    )
    monkeypatch.setattr(
        qbox_entry,
        "inspect_context",
        lambda *_args: {"status": "pass"},
    )
    monkeypatch.setattr(
        qbox_entry,
        "_profile_provenance",
        lambda *_args: FakeProvenance("platform-devices"),
    )

    def capture_inputs(
        _root: Path,
        run_dir: Path,
        context: dict[str, JsonValue],
    ) -> Path:
        captured.update(context)
        path = run_dir / "evidence/input-manifest.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(context), encoding="utf-8")
        return path

    monkeypatch.setattr(qbox_entry, "capture_run_inputs", capture_inputs)
    run_dir = tmp_path / "build/tests/qbox-platform-standalone"

    result = qbox_entry._write_qbox_context(tmp_path, options, run_dir)

    assert result == 0
    assert captured["comparison_mode"] == "standalone"
    assert captured["test_profile"] == "platform-devices"
    assert "accepted_fvp_reference" not in captured
    assert captured["provenance"] == {"profile_id": "platform-devices"}
