from __future__ import annotations

import hashlib
from pathlib import Path

import pytest

from scripts.test import gic720ae_pcie_irq_validation_contract as contract
from scripts.test import gic720ae_pcie_irq_validation_execution as execution
from scripts.test import gic720ae_pcie_irq_validation_provenance as provenance
from scripts.test import gic720ae_pcie_irq_validation_workflow as workflow

ROOT = Path(__file__).resolve().parents[1]
GATE = (
    ROOT
    / ".omo/evidence/apollo-gic-its/final/F2/cycle2/integration-current"
    / "fvp-reference-gate-current.json"
)
PROFILE = (
    ROOT
    / ".omo/evidence/apollo-gic-its/final/F2/cycle2/integration-current"
    / "canonical-profile-v4/manifest.json"
)
AUDIT_RELATIVE = Path("run/ap-map-audit.json")


def write_script(path: Path, source: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(source, encoding="utf-8")


def provenance_closure(binary: Path) -> contract.JsonObject:
    digest: contract.JsonObject = {"sha256": "0" * 64, "size": 0}
    repository: contract.JsonObject = {
        "path": "/tmp/repository",
        "head": "0" * 40,
        "scope_paths": ["scope"],
        "expected_state": "DIRTY_ALLOWED",
        "staged_diff": dict(digest),
        "worktree_diff": dict(digest),
        "untracked_manifest_sha256": "0" * 64,
        "untracked_sources": [],
        "status_entries": [],
    }
    return {
        "schema_version": 1,
        "status": "PASS",
        "closure_state": "PRE_AUDIT",
        "fvp_qualification": "UNSUPPORTED",
        "files": {
            f"fixture_{index}": {
                "path": f"/tmp/fixture-{index}",
                "sha256": "0" * 64,
                "size": 1,
            }
            for index in range(20)
        },
        "repositories": {
            name: dict(repository)
            for name in (
                "superproject",
                "linux",
                "trusted_firmware_a",
                "scp_firmware",
                "meta_hsoc_bsp",
                "qbox_platform",
                "qbox_core",
                "qemu",
            )
        },
        "qbox_binary": provenance.binary_identity(binary),
        "ap_memory_map_audit": {"status": "NOT_RUN"},
        "command_order": list(provenance.COMMANDS),
    }


def prepare_execute(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    audit_source: str,
) -> tuple[contract.RunConfig, contract.JsonObject]:
    write_script(tmp_path / "local_build.sh", "#!/bin/sh\nexit 0\n")
    (tmp_path / "local_build.sh").chmod(0o755)
    write_script(
        tmp_path / "scripts/test/audit_qbox_apollo_ap_memory_map.py",
        audit_source,
    )
    task9 = tmp_path / "scripts/test/run_gic720ae_pcie_irq_validation_task9.py"
    write_script(task9, "raise SystemExit(23)\n")
    task10 = tmp_path / "scripts/test/run_gic720ae_pcie_irq_validation_task10.py"
    write_script(task10, "raise SystemExit(29)\n")
    binary = tmp_path / "build/local-apollo-qvp/work/qbox-platform/platforms-vp"
    write_script(binary, "qbox-binary\n")
    config = contract.RunConfig(GATE, PROFILE, tmp_path / "run", None, None, 10, binary)
    monkeypatch.setattr(contract, "ROOT", tmp_path)
    monkeypatch.setattr(workflow, "TASK9_ADAPTER", task9)
    monkeypatch.setattr(workflow, "TASK10_ADAPTER", task10)
    monkeypatch.setattr(provenance, "assert_unchanged", lambda _config, _expected: None)
    return config, provenance_closure(binary)


@pytest.mark.parametrize(
    "audit_source",
    (
        "raise SystemExit(0)\n",
        "from pathlib import Path\nimport sys\nPath(sys.argv[-1]).write_text('{bad')\n",
        "from pathlib import Path\nimport sys\nPath(sys.argv[-1]).write_text('[]')\n",
        'from pathlib import Path\nimport sys\nPath(sys.argv[-1]).write_text(\'{"check": "coverage"}\')\n',
        'from pathlib import Path\nimport sys\nPath(sys.argv[-1]).write_text(\'{"passed": "true"}\')\n',
        "from pathlib import Path\nimport sys\nPath(sys.argv[-1]).write_text('{\"passed\": false}')\n",
    ),
)
def test_ap_map_audit_failure_stops_before_task9(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    audit_source: str,
) -> None:
    # Given: QBox builds but the canonical AP-map audit is absent or invalid.
    config, closure = prepare_execute(tmp_path, monkeypatch, audit_source)

    # When: full execution reaches the post-build AP-map boundary.
    returncode = execution.execute(config, closure)

    # Then: a schema-valid failure precedes every Task9 process boundary.
    payload = contract.load_object(config.run_root / "result.json", "test_result")
    contract.validate_schema(payload, contract.RESULT_SCHEMA, "test_result_schema")
    phase_values = payload.get("phases")
    assert isinstance(phase_values, list)
    phases: dict[str, contract.JsonValue] = {
        str(row["name"]): row["status"]
        for item in phase_values
        if isinstance(item, dict)
        for row in (item,)
    }
    qbox = contract.object_value(payload.get("qbox"), "test_qbox")
    assert returncode == 1
    assert phases["ap_memory_map_audit"] == "FAIL"
    assert phases["task9_qualification"] == "NOT_RUN"
    assert payload["task9"] == {"status": "NOT_RUN", "artifacts": {}}
    assert payload["task10"] == {"status": "NOT_RUN"}
    assert qbox["started"] is False
    assert not (config.run_root / "task9-process.json").exists()


def test_successful_ap_map_audit_is_bound_before_later_failure(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # Given: a fresh semantically passing audit and a later failing Task9 adapter.
    source = (
        "from pathlib import Path\n"
        "import sys\n"
        'Path(sys.argv[-1]).write_text(\'{"passed": true, "fresh": true}\\n\')\n'
    )
    config, closure = prepare_execute(tmp_path, monkeypatch, source)

    # When: the orchestrator completes the audit then observes Task9 rc=23.
    returncode = execution.execute(config, closure)

    # Then: both result and provenance bind the exact canonical audit bytes.
    audit = tmp_path / AUDIT_RELATIVE
    payload = contract.load_object(config.run_root / "result.json", "test_result")
    emitted = contract.load_object(
        config.run_root / "provenance.json", "test_provenance"
    )
    expected = {
        "path": str(audit.resolve()),
        "sha256": hashlib.sha256(audit.read_bytes()).hexdigest(),
        "size": audit.stat().st_size,
    }
    assert returncode == 1
    assert payload["ap_memory_map_audit"] == {"status": "PASS", "artifact": expected}
    assert emitted["ap_memory_map_audit"] == expected


def test_build_only_generates_and_binds_fresh_ap_map_audit(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    # Given: build-only mode with a real child audit that writes a PASS document.
    source = (
        "from pathlib import Path\n"
        "import sys\n"
        'Path(sys.argv[-1]).write_text(\'{"passed": true, "fresh": true}\\n\')\n'
    )
    config, closure = prepare_execute(tmp_path, monkeypatch, source)
    output = tmp_path / "evidence/provenance.json"
    config = contract.RunConfig(
        config.gate,
        config.profile,
        config.run_root,
        output,
        None,
        config.timeout,
        config.qbox_binary,
    )
    monkeypatch.setattr(provenance, "build", lambda _config: closure)

    # When: build-only completes its real build and audit children.
    returncode = execution.build_only(config, closure)

    # Then: the canonical path is fresh and the emitted provenance hash-binds it.
    stdout = capsys.readouterr().out
    audit = tmp_path / AUDIT_RELATIVE
    emitted = contract.load_object(output, "test_provenance")
    binding = emitted["ap_memory_map_audit"]
    assert returncode == 0
    assert "status=BUILD_ONLY" in stdout
    assert "full_qualification=false" in stdout
    assert contract.load_object(audit, "test_audit")["passed"] is True
    assert binding == {
        "path": str(audit.resolve()),
        "sha256": hashlib.sha256(audit.read_bytes()).hexdigest(),
        "size": audit.stat().st_size,
    }
    assert output.with_suffix(".audit.log").is_file()
    assert output.with_suffix(".audit-process.json").is_file()
    assert output.with_suffix(".build.log").is_file()
    assert output.with_suffix(".build-process.json").is_file()
    assert not (output.parent / "task9-process.json").exists()
    assert workflow.PHASES[3:] == (
        "qbox_build",
        "ap_memory_map_audit",
        "task9_qualification",
        "task10_comparison",
        "cleanup_audit",
        "atomic_final_result",
    )


def test_build_only_cannot_accept_stale_preexisting_audit(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # Given: a stale success-looking audit and a child that emits no replacement.
    config, closure = prepare_execute(tmp_path, monkeypatch, "raise SystemExit(0)\n")
    stale = tmp_path / AUDIT_RELATIVE
    write_script(stale, '{"passed": true, "generation": "stale"}\n')
    output = tmp_path / "evidence/provenance.json"
    config = contract.RunConfig(
        config.gate,
        config.profile,
        config.run_root,
        output,
        None,
        config.timeout,
        config.qbox_binary,
    )
    monkeypatch.setattr(provenance, "build", lambda _config: closure)

    # When/Then: build-only removes stale state and fails without fresh output.
    with pytest.raises(contract.ValidationError, match="ap_memory_map_audit_json"):
        execution.build_only(config, closure)
    assert not stale.exists()
