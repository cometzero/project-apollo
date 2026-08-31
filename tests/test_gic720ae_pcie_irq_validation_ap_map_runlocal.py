from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
import json
from pathlib import Path

import pytest

from scripts.test import gic720ae_pcie_irq_validation_ap_map as ap_map
from scripts.test import gic720ae_pcie_irq_validation_contract as contract
from scripts.test import gic720ae_pcie_irq_validation_provenance as provenance
from scripts.test import gic720ae_pcie_irq_validation_workflow as workflow


def run_config(root: Path, name: str) -> contract.RunConfig:
    return contract.RunConfig(
        root / "gate.json",
        root / "profile.json",
        root / name,
        None,
        None,
        10,
        root / "platforms-vp",
    )


def write_coverage(run_root: Path, audit: Path) -> None:
    payload = {
        "passed": True,
        "ap_9_1_1_memory_map": {
            "passed": True,
            "audit_path": str(audit),
        },
    }
    run_root.mkdir(parents=True)
    for mode in ("msix", "intx"):
        (run_root / f"{mode}-coverage-audit.json").write_text(
            json.dumps(payload), encoding="utf-8"
        )


def provenance_base(binary: Path) -> contract.JsonObject:
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


def test_task11_ap_map_path_is_inside_run_config_root(tmp_path: Path) -> None:
    # Given: one Task11 configuration with an isolated evidence root.
    config = run_config(tmp_path, "run-a")

    # When: Task11 resolves the AP-map receipt path.
    actual = workflow.ap_map_audit_path(config)

    # Then: the receipt belongs to that run, never the shared build tree.
    assert actual == config.run_root / "ap-map-audit.json"


def test_distinct_run_configs_do_not_alias_ap_map_receipt(tmp_path: Path) -> None:
    # Given: two Task11 runs that may execute concurrently.
    first = run_config(tmp_path, "run-a")
    second = run_config(tmp_path, "run-b")

    # When: their AP-map receipt identities are resolved.
    first_path = workflow.ap_map_audit_path(first)
    second_path = workflow.ap_map_audit_path(second)

    # Then: each identity is rooted in its own immutable run closure.
    assert first_path == first.run_root / "ap-map-audit.json"
    assert second_path == second.run_root / "ap-map-audit.json"
    assert first_path != second_path


def test_task11_passes_exact_ap_map_identity_to_task9(tmp_path: Path) -> None:
    # Given: a validated AP-map artifact owned by one Task11 run.
    config = run_config(tmp_path, "run-a")
    config.run_root.mkdir()
    audit = config.run_root / "ap-map-audit.json"
    audit.write_text('{"passed": true}\n', encoding="utf-8")
    artifact = ap_map.task11_artifact(config.run_root, audit)

    # When: Task11 constructs the real Task9 adapter boundary.
    command = workflow.task9_command(config, artifact)

    # Then: path, hash, and size are passed as one immutable identity.
    assert command[command.index("--ap-map-audit") + 1] == str(artifact.path)
    assert command[command.index("--ap-map-audit-sha256") + 1] == artifact.sha256
    assert command[command.index("--ap-map-audit-size") + 1] == str(artifact.size)


def test_concurrent_audit_children_keep_receipts_run_local(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # Given: two run roots, a real child seam, and a historical global receipt.
    audit_script = tmp_path / "scripts/test/audit_qbox_apollo_ap_memory_map.py"
    audit_script.parent.mkdir(parents=True)
    audit_script.write_text(
        "from pathlib import Path\n"
        "import sys\n"
        "Path(sys.argv[-1]).write_text('{\"passed\": true}\\n')\n",
        encoding="utf-8",
    )
    historical = tmp_path / "build/qbox-apollo-qvp/ap-map-9-1-1/ap-map-audit.json"
    historical.parent.mkdir(parents=True)
    historical.write_text('{"passed": true, "historical": true}\n', encoding="utf-8")
    before = historical.read_bytes()
    configs = (run_config(tmp_path, "run-a"), run_config(tmp_path, "run-b"))
    monkeypatch.setattr(contract, "ROOT", tmp_path)
    for config in configs:
        config.run_root.mkdir()
        workflow.prepare_ap_map_audit(config)

    # When: both audit subprocesses execute concurrently.
    def execute(config: contract.RunConfig) -> ap_map.ApMapArtifact:
        child = workflow.run_child(
            workflow.ap_map_audit_command(config),
            config.run_root / "audit.log",
            config.timeout,
            config.run_root / "audit-process.json",
        )
        workflow.require_child(child, "ap_memory_map_audit")
        return workflow.validate_ap_map_audit(
            config, workflow.ap_map_audit_path(config)
        )

    with ThreadPoolExecutor(max_workers=2) as pool:
        artifacts = tuple(pool.map(execute, configs))

    # Then: immutable identities differ and the historical receipt is untouched.
    assert artifacts[0].path != artifacts[1].path
    assert all(
        artifact.path.parent == config.run_root
        for artifact, config in zip(artifacts, configs, strict=True)
    )
    assert historical.read_bytes() == before


def test_task9_artifacts_reject_ap_map_outside_expected_run_root(
    tmp_path: Path,
) -> None:
    # Given: coverage that cites a passing AP-map receipt owned by another run.
    task9_root = tmp_path / "run-a/task9"
    external = tmp_path / "run-b/ap-map-audit.json"
    external.parent.mkdir(parents=True)
    external.write_text('{"passed": true}\n', encoding="utf-8")
    expected = task9_root.parent / "ap-map-audit.json"
    expected.parent.mkdir(parents=True)
    expected.write_text('{"passed": true}\n', encoding="utf-8")
    write_coverage(task9_root, external)

    # When/Then: Task11 rejects the external receipt instead of rebinding it.
    with pytest.raises(contract.ValidationError, match="task9_ap_map_path"):
        workflow.task9_artifacts(task9_root)


def test_stale_global_pass_cannot_become_task11_provenance(
    tmp_path: Path,
) -> None:
    # Given: a success-looking historical global receipt and a new Task11 run.
    config = run_config(tmp_path, "run-a")
    stale = tmp_path / "build/qbox-apollo-qvp/ap-map-9-1-1/ap-map-audit.json"
    stale.parent.mkdir(parents=True)
    stale.write_text('{"passed": true, "generation": "stale"}\n', encoding="utf-8")
    base = provenance_base(config.qbox_binary)

    # When: the old receipt is offered to the provenance binding boundary.
    artifact = ap_map.load(stale, tmp_path, "stale_ap_map")

    # Then: it cannot be represented as this run's immutable artifact.
    with pytest.raises(contract.ValidationError, match="ap_memory_map_audit_path"):
        provenance.bind_ap_map_audit(base, config, artifact)


def test_canonical_bound_frozen_provenance_accepts_preaudit_base(
    tmp_path: Path,
) -> None:
    # Given: canonical frozen provenance carrying a run-local audit binding.
    config = run_config(tmp_path, "run-a")
    config.qbox_binary.write_text("qbox\n", encoding="utf-8")
    config.run_root.mkdir()
    audit = config.run_root / "ap-map-audit.json"
    audit.write_text('{"passed": true}\n', encoding="utf-8")
    base = provenance_base(config.qbox_binary)
    artifact = ap_map.task11_artifact(config.run_root, audit)
    bound = provenance.bind_ap_map_audit(base, config, artifact)
    frozen = config.run_root / "provenance.json"
    provenance.atomic_write(frozen, bound)

    # When: preflight compares its intentionally pre-audit base closure.
    provenance.compare_frozen(base, frozen, config.run_root)

    # Then: the deferred artifact remains exact once the fresh audit is bound.
    provenance.compare_frozen(bound, frozen, config.run_root)


def test_noncanonical_bound_frozen_provenance_fails_preaudit(
    tmp_path: Path,
) -> None:
    # Given: semantically identical bound provenance with byte-level drift.
    config = run_config(tmp_path, "run-a")
    config.qbox_binary.write_text("qbox\n", encoding="utf-8")
    config.run_root.mkdir()
    audit = config.run_root / "ap-map-audit.json"
    audit.write_text('{"passed": true}\n', encoding="utf-8")
    base = provenance_base(config.qbox_binary)
    artifact = ap_map.task11_artifact(config.run_root, audit)
    bound = provenance.bind_ap_map_audit(base, config, artifact)
    frozen = config.run_root / "provenance.json"
    frozen.write_bytes(provenance.canonical_bytes(bound) + b"\n")

    # When/Then: preflight rejects noncanonical bytes before any build child.
    with pytest.raises(contract.ValidationError, match="frozen_provenance_bytes"):
        provenance.compare_frozen(base, frozen, config.run_root)


def test_build_only_output_rejects_traversal_and_symlink(
    tmp_path: Path,
) -> None:
    # Given: traversal syntax and a symlinked build-only evidence parent.
    target = tmp_path / "target"
    target.mkdir()
    link = tmp_path / "link"
    link.symlink_to(target, target_is_directory=True)

    # When/Then: neither path can reach a build or audit child boundary.
    with pytest.raises(contract.ValidationError, match="output_path"):
        contract.validate_output_path(tmp_path / "root/../escape/provenance.json")
    with pytest.raises(contract.ValidationError, match="output_path_symlink"):
        contract.validate_output_path(link / "provenance.json")
