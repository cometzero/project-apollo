from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import subprocess
import sys

import pytest


ROOT = Path(__file__).resolve().parents[1]
HELPER = ROOT / "scripts/run/gic720ae_operation_manifest.py"
SCHEMA = ROOT / "tests/schemas/gic720ae-linux-probe-commands.schema.json"
MANIFEST = ROOT / "tests/commands/gic720ae-linux-probe.yaml"


def load_helper():
    spec = importlib.util.spec_from_file_location(HELPER.stem, HELPER)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_operation_manifest_serializes_only_literal_guest_commands() -> None:
    helper = load_helper()
    operations = helper.load_operations(MANIFEST, SCHEMA)
    module = Path("/lib/modules/6.12.0/extra/gic720ae_test.ko")
    serialized = [
        helper.serialize_operation(operation, module_path=module)
        for operation in operations
    ]
    assert serialized[0] == [
        b"insmod /lib/modules/6.12.0/extra/gic720ae_test.ko target_cpu=1\n"
    ]
    assert serialized[1] == [
        b"tee /sys/kernel/debug/gic720ae_test/control\n", b"ipi 1\n", b"\x04"
    ]
    assert serialized[3] == [b"cat /proc/interrupts\n"]
    assert serialized[-1] == [b"rmmod gic720ae_test\n"]


@pytest.mark.parametrize("payload", (">", "$(id)", ";", "unknown"))
def test_operation_manifest_rejects_unsafe_input_before_command(
    tmp_path: Path, payload: str,
) -> None:
    helper = load_helper()
    attacker = tmp_path / "attacker.yaml"
    attacker.write_text(
        "version: 1\noperations:\n"
        f"  - op: read\n    path: /proc/interrupts{payload}\n",
        encoding="utf-8",
    )
    with pytest.raises(helper.ManifestError):
        helper.load_operations(attacker, SCHEMA)


@pytest.mark.parametrize(
    "module",
    (
        Path("/tmp/gic720ae_test.ko"),
        Path("/lib/modules/6.12.0/extra/gic720ae_test.ko;touch-pwned"),
        Path("relative/gic720ae_test.ko"),
    ),
)
def test_operation_manifest_rejects_unproven_or_shell_like_module_path(
    module: Path,
) -> None:
    # Given: an otherwise valid, typed insmod operation.
    helper = load_helper()
    operation = helper.load_operations(MANIFEST, SCHEMA)[0]

    # When: its module source is not the fixed guest module role path.
    # Then: no guest payload is serialized.
    with pytest.raises(helper.ManifestError):
        helper.serialize_operation(operation, module_path=module)


def test_linux_probe_negative_fixtures_keep_unrelated_probe_separate(
    tmp_path: Path,
) -> None:
    runner = ROOT / "scripts/test/run_gic720ae_linux_probe.py"
    wrong = subprocess.run(
        [
            sys.executable, str(runner), "--self-test-negative",
            str(ROOT / "tests/fixtures/gic720ae/linux-wrong-affinity.json"),
            "--out-dir", str(tmp_path / "wrong"),
        ],
        cwd=ROOT, check=False,
    )
    assert wrong.returncode != 0
    wrong_result = json.loads(
        (tmp_path / "wrong/linux-probe-result.json").read_text()
    )
    assert wrong_result["reason"] == "wrong_target_cpu"
    unrelated = subprocess.run(
        [
            sys.executable, str(runner), "--self-test-negative",
            str(
                ROOT
                / "tests/fixtures/gic720ae/linux-unrelated-probe-missing.json"
            ),
            "--out-dir", str(tmp_path / "unrelated"),
        ],
        cwd=ROOT, check=False,
    )
    assert unrelated.returncode == 0
    unrelated_result = json.loads(
        (tmp_path / "unrelated/linux-probe-result.json").read_text()
    )
    assert set(unrelated_result["gic_rows"].values()) == {"PASS"}
    assert unrelated_result["unrelated_probe"] == "BLOCKED"


def test_linux_probe_negative_fixture_rejects_marker_only_success(
    tmp_path: Path,
) -> None:
    # Given: an incomplete negative fixture that carries no observable rows.
    fixture = tmp_path / "marker-only.json"
    fixture.write_text('{"present": false}\n', encoding="utf-8")
    runner = ROOT / "scripts/test/run_gic720ae_linux_probe.py"

    # When: the fixture-only probe is evaluated.
    result = subprocess.run(
        [
            sys.executable, str(runner), "--self-test-negative", str(fixture),
            "--out-dir", str(tmp_path / "result"),
        ],
        cwd=ROOT,
        check=False,
    )

    # Then: a marker/absence alone cannot be accepted as GIC probe success.
    assert result.returncode != 0
    payload = json.loads(
        (tmp_path / "result/linux-probe-result.json").read_text()
    )
    assert payload["reason"] == "malformed_fixture"
