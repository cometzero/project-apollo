from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

import pytest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/test/capture_gic720ae_source_state.py"


@pytest.fixture
def capture_inputs(tmp_path: Path) -> tuple[Path, Path]:
    # An isolated host fixture exercises the CLI without historical build inputs.
    script = tmp_path / "workspace/scripts/test" / SCRIPT.name
    script.parent.mkdir(parents=True)
    shutil.copyfile(SCRIPT, script)
    config = tmp_path / "workspace/build/conf"
    config.mkdir(parents=True)
    for name in ("local.conf", "bblayers.conf", "templateconf.cfg"):
        (config / name).write_text(f"# host test fixture: {name}\n", encoding="utf-8")
    snapshot = tmp_path / "snapshot"
    snapshot.mkdir()
    records = b""
    for field in ("head", "index", "status"):
        value = f"host test fixture: {field}\n".encode()
        records += b"\0".join((
            b"meta", b"qemu", field.encode(), str(len(value)).encode(),
            hashlib.sha256(value).hexdigest().encode(),
        )) + b"\0"
    (snapshot / "snapshot.records").write_bytes(records)
    (snapshot / "manifest.sha256").write_text(
        f"{hashlib.sha256(records).hexdigest()}  snapshot.records\n", encoding="ascii"
    )
    return script, snapshot


def run_capture(script: Path, snapshot: Path, output: Path, *args: str):
    return subprocess.run(
        [sys.executable, str(script), "--pristine-snapshot", str(snapshot),
         "--output", str(output), *args],
        cwd=script.parents[2],
        env={**os.environ, "PATH": ""},
        check=False, text=True, capture_output=True,
    )


def test_capture_records_verified_pristine_repository_inputs_when_snapshot_is_valid(
    tmp_path: Path, capture_inputs: tuple[Path, Path],
) -> None:
    script, snapshot = capture_inputs
    output = tmp_path / "source-state.json"
    archive = tmp_path / "pristine-archive"

    result = run_capture(script, snapshot, output, "--archive-pristine-to", str(archive))

    assert result.returncode == 0, result.stderr
    report = json.loads(output.read_text(encoding="utf-8"))
    assert report["pristine"]["record_count"] == 3
    assert set(report["repositories"]["qemu"]) == {"head", "index", "status"}
    for name in ("snapshot.records", "manifest.sha256"):
        assert (archive / name).read_bytes() == (snapshot / name).read_bytes()
        assert (archive / name).stat().st_mode & 0o777 == 0o400


def test_capture_rejects_symlinked_pristine_manifest_when_snapshot_is_untrusted(
    tmp_path: Path, capture_inputs: tuple[Path, Path],
) -> None:
    script, snapshot = capture_inputs
    manifest = snapshot / "manifest.sha256"
    original = tmp_path / "manifest.sha256"
    manifest.rename(original)
    manifest.symlink_to(original)
    output = tmp_path / "rejected.json"

    result = run_capture(script, snapshot, output)

    assert result.returncode == 2
    assert json.loads(output.read_text(encoding="utf-8"))["reason"] == "invalid_input"


def test_verify_reports_only_qemu_head_when_canonical_fixture_has_that_drift(
    tmp_path: Path, capture_inputs: tuple[Path, Path],
) -> None:
    script, snapshot = capture_inputs
    expected_path = tmp_path / "baseline.json"
    baseline = run_capture(script, snapshot, expected_path)
    assert baseline.returncode == 0, baseline.stderr
    expected = json.loads(expected_path.read_text(encoding="utf-8"))
    expected["repositories"]["qemu"]["head"] = "0" * 64
    expected["expected_changed_fields"] = ["repositories.qemu.head"]
    expected_path.write_text(json.dumps(expected), encoding="utf-8")
    output = tmp_path / "negative.json"

    result = run_capture(
        script, snapshot, output, "--verify-only", "--expected-input", str(expected_path),
        "--assert-only-changed-field", "repositories.qemu.head",
    )

    assert result.returncode == 1
    assert json.loads(output.read_text(encoding="utf-8"))["changed_fields"] == [
        "repositories.qemu.head"
    ]


def test_capture_rejects_modified_snapshot_records(
    tmp_path: Path, capture_inputs: tuple[Path, Path],
) -> None:
    script, snapshot = capture_inputs
    (snapshot / "snapshot.records").write_bytes(b"tampered\0")
    output = tmp_path / "tampered.json"

    result = run_capture(script, snapshot, output)

    assert result.returncode == 2
    assert json.loads(output.read_text(encoding="utf-8"))["reason"] == "input_changed"


def test_capture_rejects_missing_snapshot(
    tmp_path: Path, capture_inputs: tuple[Path, Path],
) -> None:
    script, _ = capture_inputs
    output = tmp_path / "missing.json"

    result = run_capture(script, tmp_path / "absent", output)

    assert result.returncode == 2
    assert json.loads(output.read_text(encoding="utf-8"))["reason"] == "missing_input"
