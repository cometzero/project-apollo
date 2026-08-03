from __future__ import annotations

from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/test/capture_gic720ae_source_state.py"
PRISTINE = Path("/tmp/gic720ae-pristine-axqumhu0")
DRIFT = ROOT / "tests/fixtures/gic720ae/source-state-drift.json"


def test_capture_records_verified_pristine_repository_inputs_when_snapshot_is_valid(
    tmp_path: Path,
) -> None:
    # Given: the controller-owned immutable pristine snapshot.
    output = tmp_path / "source-state.json"
    archive = tmp_path / "pristine-archive"

    # When: the source-state producer is invoked through its CLI.
    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "--pristine-snapshot",
            str(PRISTINE),
            "--archive-pristine-to",
            str(archive),
            "--output",
            str(output),
        ],
        cwd=ROOT,
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    # Then: the verified baseline is emitted and faithfully archived.
    assert result.returncode == 0, result.stderr
    assert output.is_file()
    assert (archive / "snapshot.records").read_bytes() == (PRISTINE / "snapshot.records").read_bytes()
    assert (archive / "manifest.sha256").read_bytes() == (PRISTINE / "manifest.sha256").read_bytes()


def test_capture_rejects_symlinked_pristine_manifest_when_snapshot_is_untrusted(
    tmp_path: Path,
) -> None:
    # Given: a snapshot directory with a symlink instead of an immutable manifest.
    snapshot = tmp_path / "snapshot"
    snapshot.mkdir()
    (snapshot / "snapshot.records").write_bytes(b"")
    (snapshot / "manifest.sha256").symlink_to(PRISTINE / "manifest.sha256")
    output = tmp_path / "rejected.json"

    # When: the CLI consumes the untrusted snapshot.
    result = subprocess.run(
        [sys.executable, str(SCRIPT), "--pristine-snapshot", str(snapshot), "--output", str(output)],
        cwd=ROOT,
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    # Then: it fails closed with a machine-readable invalid-input reason.
    assert result.returncode == 2
    assert '"reason": "invalid_input"' in output.read_text(encoding="utf-8")


def test_verify_reports_only_qemu_head_when_canonical_fixture_has_that_drift(
    tmp_path: Path,
) -> None:
    # Given: the canonical source state with only the QEMU head deliberately changed.
    output = tmp_path / "negative.json"

    # When: verify-only compares it to the current pristine source inputs.
    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "--pristine-snapshot",
            str(PRISTINE),
            "--verify-only",
            "--expected-input",
            str(DRIFT),
            "--assert-only-changed-field",
            "repositories.qemu.head",
            "--output",
            str(output),
        ],
        cwd=ROOT,
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    # Then: it returns the specified drift and no unrelated field.
    assert result.returncode == 1
    assert '"changed_fields": ["repositories.qemu.head"]' in result.stderr
