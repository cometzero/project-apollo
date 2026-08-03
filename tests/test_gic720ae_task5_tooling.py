from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor

import jsonschema
import yaml


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts/test"
FIXTURES = ROOT / "tests/fixtures/gic720ae"
SCHEMAS = ROOT / "tests/schemas"


def run_tool(name: str, *arguments: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPTS / name), *arguments],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
        timeout=30,
    )


def load_tool(name: str):
    path = SCRIPTS / name
    sys.path.insert(0, str(SCRIPTS))
    spec = importlib.util.spec_from_file_location(path.stem, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_feature_matrix_empty_overlay_is_blocked(tmp_path: Path) -> None:
    output = tmp_path / "audit.json"
    result = run_tool(
        "audit_gic720ae_feature_matrix.py",
        "--matrix",
        "doc/validation/gic-720ae/feature-matrix.yaml",
        "--schema",
        "tests/schemas/gic720ae-feature-matrix.schema.json",
        "--status-overlay",
        "tests/fixtures/gic720ae/feature-status-empty.json",
        "--status-schema",
        "tests/schemas/gic720ae-feature-status-overlay.schema.json",
        "--evidence-root",
        str(tmp_path),
        "--output",
        str(output),
    )
    assert result.returncode == 0, result.stderr
    audit = json.loads(output.read_text(encoding="utf-8"))
    assert audit["criteria_unchanged"] is True
    assert audit["active_rows"] > 0
    assert audit["status_counts"] == {"BLOCKED": audit["active_rows"]}


def test_status_builder_content_address_and_rejects_bad_name(tmp_path: Path) -> None:
    source_state = tmp_path / "source-state.json"
    source_state.write_text('{"source_state_sha":"' + "1" * 64 + '"}\n')
    output_dir = tmp_path / "overlay"
    result = run_tool(
        "build_gic720ae_feature_status_overlay.py",
        "--domain",
        "all",
        "--phase",
        "pre_freeze",
        "--criteria",
        "doc/validation/gic-720ae/feature-matrix.yaml",
        "--source-state",
        str(source_state),
        "--plan",
        ".omo/plans/apollo-gic720ae-implementation.md",
        "--schema",
        "tests/schemas/gic720ae-feature-status-overlay.schema.json",
        "--output-dir",
        str(output_dir),
    )
    assert result.returncode == 0, result.stderr
    overlay = next(output_dir.glob("feature-status-*.json"))
    digest = hashlib.sha256(overlay.read_bytes()).hexdigest()
    assert overlay.name == f"feature-status-{digest}.json"
    mismatched = output_dir / f"feature-status-{'0' * 64}.json"
    mismatched.write_bytes(overlay.read_bytes())
    bad = run_tool(
        "audit_gic720ae_feature_matrix.py",
        "--matrix",
        "doc/validation/gic-720ae/feature-matrix.yaml",
        "--schema",
        "tests/schemas/gic720ae-feature-matrix.schema.json",
        "--status-overlay",
        str(mismatched),
        "--status-schema",
        "tests/schemas/gic720ae-feature-status-overlay.schema.json",
        "--evidence-root",
        str(tmp_path),
        "--output",
        str(tmp_path / "bad.json"),
    )
    assert bad.returncode != 0


def test_all_task5_json_schemas_are_deterministic() -> None:
    for path in sorted(SCHEMAS.glob("gic720ae-*.schema.json")):
        schema = json.loads(path.read_text(encoding="utf-8"))
        jsonschema.Draft202012Validator.check_schema(schema)
        assert schema.get("$schema") == "https://json-schema.org/draft/2020-12/schema"


def test_final_qualification_rejects_stale_and_marker_only(tmp_path: Path) -> None:
    cases = (
        ("stale-final-input.json", "stale_input"),
        ("final-marker-only.json", "insufficient_stimulus"),
        ("final-fvp-hash-mismatch.json", "stale_evidence"),
    )
    for fixture, reason in cases:
        output = tmp_path / fixture
        result = run_tool(
            "run_gic720ae_final_qualification.py",
            "--self-test",
            "--fixture",
            str(FIXTURES / fixture),
            "--schema",
            str(SCHEMAS / "gic720ae-final-qualification.schema.json"),
            "--output",
            str(output),
        )
        assert result.returncode != 0
        assert json.loads(output.read_text(encoding="utf-8"))["reason"] == reason


def test_required_negative_contracts(tmp_path: Path) -> None:
    cases = (
        (
            "verify_gic720ae_independent_review_receipt.py",
            "reviewer-participated.json",
            "reviewer_not_independent",
            ["--receipt-schema", str(SCHEMAS / "gic720ae-reviewer-receipt.schema.json")],
        ),
        (
            "verify_gic720ae_ledger_chain.py",
            "ledger-chain-broken.json",
            "broken_ledger_chain",
            ["--schema", str(SCHEMAS / "gic720ae-ledger-chain.schema.json")],
        ),
        (
            "capture_gic720ae_runtime_input_closure.py",
            "runtime-input-missing-leaf.json",
            "unowned_runtime_input",
            ["--schema", str(SCHEMAS / "gic720ae-runtime-input-closure.schema.json")],
        ),
    )
    for script, fixture, reason, extra in cases:
        output = tmp_path / f"{script}.json"
        result = run_tool(
            script,
            "--self-test-negative",
            str(FIXTURES / fixture),
            *extra,
            "--output",
            str(output),
        )
        assert result.returncode != 0
        assert json.loads(output.read_text(encoding="utf-8"))["reason"] == reason


def test_prompts_and_command_manifest_are_immutable_contracts() -> None:
    manifest = yaml.safe_load(
        (ROOT / "tests/commands/gic720ae-final-manual-qa.yaml").read_text(
            encoding="utf-8"
        )
    )
    assert manifest["commands"]
    prompts = (
        "gic720ae-f1-plan-compliance.md",
        "gic720ae-f2-code-quality.md",
        "gic720ae-f3-manual-qa.md",
        "gic720ae-f4-scope-fidelity.md",
    )
    for filename in prompts:
        prompt = (ROOT / "tests/prompts" / filename).read_text(encoding="utf-8")
        assert "descriptor-chain" in prompt
        assert "direct measurement" in prompt
        assert "APPROVE|REJECT" in prompt


def test_malformed_input_and_invalid_schema_fail_closed(tmp_path: Path) -> None:
    malformed = tmp_path / "malformed.json"
    malformed.write_text('{"fixture":', encoding="utf-8")
    receipt_output = tmp_path / "receipt.json"
    receipt = run_tool(
        "verify_gic720ae_independent_review_receipt.py",
        "--self-test-negative",
        str(malformed),
        "--receipt-schema",
        str(SCHEMAS / "gic720ae-reviewer-receipt.schema.json"),
        "--output",
        str(receipt_output),
    )
    assert receipt.returncode != 0
    assert json.loads(receipt_output.read_text())["reason"] == "malformed_input"
    bad_schema = tmp_path / "bad-schema.json"
    bad_schema.write_text('{"type": 7}\n', encoding="utf-8")
    final_output = tmp_path / "final.json"
    final = run_tool(
        "run_gic720ae_final_qualification.py",
        "--self-test",
        "--fixture",
        str(FIXTURES / "final-complete.json"),
        "--schema",
        str(bad_schema),
        "--output",
        str(final_output),
    )
    assert final.returncode != 0
    assert json.loads(final_output.read_text())["reason"] == "invalid_schema"


def test_build_command_injection_and_timeout_fail_closed(tmp_path: Path) -> None:
    local_build = tmp_path / "local_build.sh"
    local_build.write_text("#!/bin/sh\nsleep 5\n", encoding="utf-8")
    local_build.chmod(0o755)
    common = [
        "--component", "qbox", "--producer-mode", "clean_build",
        "--cwd", str(tmp_path), "--source-repos", ".",
        "--require-outputs", "missing", "--schema",
        str(SCHEMAS / "gic720ae-runtime-provenance.schema.json"),
    ]
    injected_output = tmp_path / "injected.json"
    injected = run_tool(
        "capture_gic720ae_runtime_provenance.py",
        *common, "--build-command", "./local_build.sh; curl invalid",
        "--output", str(injected_output),
    )
    assert injected.returncode != 0
    assert json.loads(injected_output.read_text())["reason"] == "forbidden_command"
    timeout_output = tmp_path / "timeout.json"
    timed = run_tool(
        "capture_gic720ae_runtime_provenance.py",
        *common, "--build-command", "./local_build.sh clean-build",
        "--timeout", "1",
        "--output", str(timeout_output),
    )
    assert timed.returncode != 0
    assert json.loads(timeout_output.read_text())["reason"] == "build_timeout"


def test_publication_self_test_is_concurrency_isolated(tmp_path: Path) -> None:
    def invoke(index: int) -> subprocess.CompletedProcess[str]:
        return run_tool(
            "run_gic720ae_github_push.py",
            "--self-test-bare-remote",
            "--schema",
            str(SCHEMAS / "gic720ae-publication.schema.json"),
            "--output",
            str(tmp_path / f"publication-{index}.json"),
        )

    with ThreadPoolExecutor(max_workers=2) as executor:
        results = list(executor.map(invoke, range(2)))
    assert [result.returncode for result in results] == [0, 0]


def test_final_qualification_rejects_fake_pass_closure(tmp_path: Path) -> None:
    closure = tmp_path / "closure.json"
    closure.write_text('{"verdict":"PASS"}\n', encoding="utf-8")
    output = tmp_path / "qualification.json"
    result = run_tool(
        "run_gic720ae_final_qualification.py",
        "--runtime-input-closure", str(closure),
        "--runtime-input-closure-schema",
        str(SCHEMAS / "gic720ae-runtime-input-closure.schema.json"),
        "--schema", str(SCHEMAS / "gic720ae-final-qualification.schema.json"),
        "--output", str(output),
    )
    assert result.returncode != 0
    assert json.loads(output.read_text())["reason"] == "invalid_runtime_closure"


def test_publication_rejects_top_first_policy_fixture(tmp_path: Path) -> None:
    fixture = tmp_path / "top-first.json"
    fixture.write_text(json.dumps({
        "repositories": [
            {
                "path": ".", "changed": True, "selected": True, "order": 0,
                "local_sha": "a" * 40, "remote_sha": "", "remote": "owned",
                "remote_url": "ssh://git@example.invalid/owner/top.git",
                "remote_host": "example.invalid", "remote_owner": "owner",
                "remote_repo": "top",
                "branch": "main",
            },
            {
                "path": "nested", "changed": True, "selected": True, "order": 1,
                "local_sha": "b" * 40, "remote_sha": "", "remote": "owned",
                "remote_url": "ssh://git@example.invalid/owner/nested.git",
                "remote_host": "example.invalid", "remote_owner": "owner",
                "remote_repo": "nested",
                "branch": "main",
            },
        ],
        "owner": "owner",
    }), encoding="utf-8")
    output = tmp_path / "publication.json"
    result = run_tool(
        "run_gic720ae_github_push.py",
        "--self-test-negative", str(fixture),
        "--schema", str(SCHEMAS / "gic720ae-publication.schema.json"),
        "--output", str(output),
    )
    assert result.returncode != 0
    assert json.loads(output.read_text())["reason"] == "top_repository_not_last"


def test_runtime_provenance_rejects_all_shell_control_operators(
    tmp_path: Path,
) -> None:
    output_file = tmp_path / "artifact"
    output_file.write_text("artifact", encoding="utf-8")
    operators = ("; touch x", "&& touch x", "| tee x", "> x", "$(touch x)", "`touch x`")
    for index, operator in enumerate(operators):
        output = tmp_path / f"result-{index}.json"
        result = run_tool(
            "capture_gic720ae_runtime_provenance.py",
            "--component", "qbox", "--producer-mode", "clean_build",
            "--cwd", str(tmp_path),
            "--build-command", f"./local_build.sh clean-build {operator}",
            "--source-repos", ".",
            "--require-outputs", "artifact",
            "--dry-run",
            "--schema", str(SCHEMAS / "gic720ae-runtime-provenance.schema.json"),
            "--output", str(output),
        )
        assert result.returncode != 0
        assert json.loads(output.read_text())["reason"] == "forbidden_command"


def test_command_replay_executes_exact_registry_argv(tmp_path: Path) -> None:
    tool = load_tool("verify_gic720ae_independent_review_receipt.py")
    registry = ROOT / "tests/commands/gic720ae-final-manual-qa.yaml"
    leaf = {
        "type": "command_replay", "value": str(ROOT),
        "command_id": "audit-plan-compliance", "exit_code": 99,
        "digest": "0" * 64,
    }
    measured = tool.recompute_leaf(leaf, registry)
    replay = subprocess.run(
        ["python3", "scripts/test/audit_gic720ae_plan_compliance.py"],
        cwd=ROOT, check=False, capture_output=True,
    )
    expected = hashlib.sha256(
        json.dumps({
            "argv": ["python3", "scripts/test/audit_gic720ae_plan_compliance.py"],
            "command_id": "audit-plan-compliance",
            "exit_code": replay.returncode,
            "stderr_sha256": hashlib.sha256(replay.stderr).hexdigest(),
            "stdout_sha256": hashlib.sha256(replay.stdout).hexdigest(),
        }, sort_keys=True, separators=(",", ":")).encode() + b"\n"
    ).hexdigest()
    assert measured == expected


def test_yocto_dry_run_cannot_synthesize_taskhash(tmp_path: Path) -> None:
    deploy = tmp_path / "deploy"
    deploy.mkdir()
    (deploy / "image").write_bytes(b"image")
    output = tmp_path / "yocto.json"
    result = run_tool(
        "capture_gic720ae_yocto_provenance.py",
        "--producer-mode", "bitbake_taskhash",
        "--build-command", "bitbake linux-yocto -c compile",
        "--require-taskhash", "linux-yocto:compile",
        "--build-conf", "build/conf/local.conf",
        "--bblayers", "build/conf/bblayers.conf",
        "--templateconf", "build/conf/templateconf.cfg",
        "--expect-machine", "apollo-qvp",
        "--expect-tmpdir", "build/tmp_baremetal",
        "--expect-variant", "cfg2", "--expect-pc-cpus", "4",
        "--linux-source", "hsoc-stack/components/primary_compute/linux",
        "--yocto-repos", "layers/poky",
        "--deploy-dir", str(deploy), "--require-outputs", "image",
        "--dry-run",
        "--schema", str(SCHEMAS / "gic720ae-yocto-provenance.schema.json"),
        "--output", str(output),
    )
    assert result.returncode != 0
    assert json.loads(output.read_text())["reason"] == "bitbake_metadata_unavailable"


def test_yocto_offline_fixture_hashes_real_metadata_bytes(tmp_path: Path) -> None:
    recipe_repo = tmp_path / "recipe-repo"
    recipe_repo.mkdir()
    subprocess.run(["git", "init", "-q", str(recipe_repo)], check=True)
    subprocess.run(
        ["git", "-C", str(recipe_repo), "config", "user.email", "qa@example.invalid"],
        check=True,
    )
    subprocess.run(
        ["git", "-C", str(recipe_repo), "config", "user.name", "QA"],
        check=True,
    )
    recipe = recipe_repo / "linux-test.bb"
    recipe.write_bytes(b'SUMMARY = "fixture recipe"\n')
    subprocess.run(["git", "-C", str(recipe_repo), "add", "."], check=True)
    subprocess.run(
        ["git", "-C", str(recipe_repo), "commit", "-q", "-m", "fixture"],
        check=True,
    )
    taskhash = "1" * 64
    siginfo = tmp_path / f"linux-test.do_compile.sigdata.{taskhash}"
    sstate = tmp_path / f"sstate-linux-test-{taskhash}.tgz"
    siginfo.write_bytes(b"real siginfo fixture bytes\n")
    sstate.write_bytes(b"real sstate fixture bytes\n")
    metadata = tmp_path / "metadata.json"
    metadata.write_text(json.dumps({"recipes": [{
        "name": "linux-test:compile", "origin": str(recipe),
        "taskhash": taskhash, "siginfo": str(siginfo), "sstate": str(sstate),
    }]}), encoding="utf-8")
    deploy = tmp_path / "deploy"
    deploy.mkdir()
    (deploy / "image").write_bytes(b"image")
    output = tmp_path / "yocto.json"
    result = run_tool(
        "capture_gic720ae_yocto_provenance.py",
        "--producer-mode", "bitbake_taskhash",
        "--build-command", "bitbake linux-test -c compile",
        "--require-taskhash", "linux-test:compile",
        "--build-conf", "build/conf/local.conf",
        "--bblayers", "build/conf/bblayers.conf",
        "--templateconf", "build/conf/templateconf.cfg",
        "--expect-machine", "apollo-qvp",
        "--expect-tmpdir", "build/tmp_baremetal",
        "--expect-variant", "cfg2", "--expect-pc-cpus", "4",
        "--linux-source", str(recipe_repo),
        "--yocto-repos", "layers/poky",
        "--deploy-dir", str(deploy), "--require-outputs", "image",
        "--dry-run", "--self-test-metadata", str(metadata),
        "--schema", str(SCHEMAS / "gic720ae-yocto-provenance.schema.json"),
        "--output", str(output),
    )
    assert result.returncode == 0, result.stderr
    record = json.loads(output.read_text())["recipes"][0]
    assert hashlib.sha256(siginfo.read_bytes()).hexdigest() in record["siginfo"]
    assert hashlib.sha256(sstate.read_bytes()).hexdigest() in record["sstate"]


def test_negative_paths_are_semantic_not_fixture_labels(tmp_path: Path) -> None:
    tag_only = tmp_path / "tag-only.json"
    tag_only.write_text('{"fixture":"fvp_hash_mismatch"}\n', encoding="utf-8")
    output = tmp_path / "tag-only-result.json"
    result = run_tool(
        "run_gic720ae_final_qualification.py",
        "--self-test-negative", str(tag_only),
        "--schema", str(SCHEMAS / "gic720ae-final-qualification.schema.json"),
        "--output", str(output),
    )
    assert result.returncode != 0
    assert json.loads(output.read_text())["reason"] == "malformed_fixture"


def test_qualifier_rejects_wrong_role_and_forged_producer_edges(
    tmp_path: Path,
) -> None:
    source = tmp_path / "runner.py"
    source.write_bytes(b"runner")
    leaf = {
        "role": "deliberately-wrong-role",
        "realpath": str(source.resolve()),
        "sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
        "producer_receipt_sha": "0" * 64,
        "producer_task": 999,
        "lineage": "invocation:forged",
    }
    contract_sha = hashlib.sha256(
        (json.dumps([leaf], sort_keys=True, separators=(",", ":")) + "\n").encode()
    ).hexdigest()
    closure = tmp_path / "closure.json"
    closure.write_text(json.dumps({
        "format_version": 1, "verdict": "PASS", "reason": "closed",
        "leaves": [leaf], "contract_sha": contract_sha,
    }), encoding="utf-8")
    output = tmp_path / "qualification.json"
    result = run_tool(
        "run_gic720ae_final_qualification.py",
        "--runtime-input-closure", str(closure), "--runner", str(source),
        "--runtime-input-closure-schema",
        str(SCHEMAS / "gic720ae-runtime-input-closure.schema.json"),
        "--schema", str(SCHEMAS / "gic720ae-final-qualification.schema.json"),
        "--output", str(output),
    )
    assert result.returncode != 0
    assert json.loads(output.read_text())["reason"] == "runtime_input_mismatch"


def test_publication_rejects_owner_substring_lookalike(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    remote = tmp_path / "not-the-owner-but-owner-substring.git"
    remote.mkdir()
    subprocess.run(["git", "init", "-q", "--bare", str(remote)], check=True)
    repo.mkdir()
    subprocess.run(["git", "init", "-q", "-b", "main", str(repo)], check=True)
    subprocess.run(["git", "-C", str(repo), "config", "user.name", "QA"], check=True)
    subprocess.run(
        ["git", "-C", str(repo), "config", "user.email", "qa@example.invalid"],
        check=True,
    )
    (repo / "f").write_text("x", encoding="utf-8")
    subprocess.run(["git", "-C", str(repo), "add", "f"], check=True)
    subprocess.run(["git", "-C", str(repo), "commit", "-q", "-m", "x"], check=True)
    subprocess.run(
        ["git", "-C", str(repo), "remote", "add", "dubious", str(remote)],
        check=True,
    )
    head = subprocess.check_output(
        ["git", "-C", str(repo), "rev-parse", "HEAD"], text=True,
    ).strip()
    manifest = tmp_path / "manifest.json"
    manifest.write_text(json.dumps({
        "format_version": 1, "verdict": "PASS", "reason": "manifest_audited",
        "mode": "audit", "repositories": [{
            "path": str(repo), "changed": True, "selected": True, "order": 0,
            "local_sha": head, "remote_sha": "", "remote": "dubious",
            "remote_url": str(remote), "remote_host": "local",
            "remote_owner": str(tmp_path),
            "remote_repo": "not-the-owner-but-owner-substring",
            "branch": "main",
        }],
    }), encoding="utf-8")
    output = tmp_path / "result.json"
    result = run_tool(
        "run_gic720ae_github_push.py", "--mode", "dry-run",
        "--owner", "owner", "--manifest", str(manifest),
        "--schema", str(SCHEMAS / "gic720ae-publication.schema.json"),
        "--output", str(output),
    )
    assert result.returncode != 0
    assert json.loads(output.read_text())["reason"] == "third_party_remote"


def test_runtime_provenance_rejects_extra_fixed_argv(tmp_path: Path) -> None:
    script = tmp_path / "local_build.sh"
    script.write_text(
        "#!/bin/sh\nprintf '%s\\n' \"$@\" > executed-argv.log\n", encoding="utf-8",
    )
    script.chmod(0o755)
    output = tmp_path / "result.json"
    result = run_tool(
        "capture_gic720ae_runtime_provenance.py",
        "--component", "qbox", "--producer-mode", "clean_build",
        "--cwd", str(tmp_path),
        "--build-command", "./local_build.sh clean-build unexpected-extra-argv",
        "--source-repos", ".", "--require-outputs", "missing",
        "--schema", str(SCHEMAS / "gic720ae-runtime-provenance.schema.json"),
        "--output", str(output),
    )
    assert result.returncode != 0
    assert json.loads(output.read_text())["reason"] == "forbidden_command"
    assert not (tmp_path / "executed-argv.log").exists()


def test_command_replay_rejects_noncanonical_shell_registry(tmp_path: Path) -> None:
    side_effect = tmp_path / "EXECUTED"
    registry = tmp_path / "registry.yaml"
    registry.write_text(
        "format_version: 1\nregistry_id: attacker\npolicy:\n"
        "  shell_text_allowed: false\n  network_allowed: false\n"
        "  timeout_seconds: 5\ncommands:\n  - id: exact-command\n"
        f"    argv: [sh, -c, \"touch {side_effect}\"]\n"
        "    measurement: command_replay\n",
        encoding="utf-8",
    )
    tool = load_tool("verify_gic720ae_independent_review_receipt.py")
    leaf = {
        "type": "command_replay", "value": str(tmp_path),
        "command_id": "exact-command", "exit_code": 0, "digest": "0" * 64,
    }
    try:
        tool.recompute_leaf(leaf, registry)
    except tool.ContractError as error:
        assert error.reason == "forbidden_command"
    else:
        raise AssertionError("attacker registry was accepted")
    assert not side_effect.exists()


def test_yocto_provenance_rejects_shell_control_with_offline_metadata(
    tmp_path: Path,
) -> None:
    recipe_repo = tmp_path / "recipe"
    recipe_repo.mkdir()
    subprocess.run(["git", "init", "-q", str(recipe_repo)], check=True)
    subprocess.run(["git", "-C", str(recipe_repo), "config", "user.name", "QA"], check=True)
    subprocess.run(
        ["git", "-C", str(recipe_repo), "config", "user.email", "qa@example.invalid"],
        check=True,
    )
    origin = recipe_repo / "linux-test.bb"
    origin.write_bytes(b"recipe")
    subprocess.run(["git", "-C", str(recipe_repo), "add", "."], check=True)
    subprocess.run(["git", "-C", str(recipe_repo), "commit", "-q", "-m", "x"], check=True)
    taskhash = "1" * 64
    siginfo = tmp_path / f"linux-test.do_compile.sigdata.{taskhash}"
    sstate = tmp_path / f"sstate-linux-test-{taskhash}.tgz"
    siginfo.write_bytes(b"siginfo")
    sstate.write_bytes(b"sstate")
    metadata = tmp_path / "metadata.json"
    metadata.write_text(json.dumps({"recipes": [{
        "name": "linux-test:compile", "origin": str(origin),
        "taskhash": taskhash, "siginfo": str(siginfo), "sstate": str(sstate),
    }]}), encoding="utf-8")
    deploy = tmp_path / "deploy"
    deploy.mkdir()
    (deploy / "image").write_bytes(b"image")
    output = tmp_path / "result.json"
    result = run_tool(
        "capture_gic720ae_yocto_provenance.py",
        "--producer-mode", "bitbake_taskhash",
        "--build-command", "bitbake linux-test -c compile; touch SHOULD_NOT_RUN",
        "--require-taskhash", "linux-test:compile",
        "--build-conf", "build/conf/local.conf",
        "--bblayers", "build/conf/bblayers.conf",
        "--templateconf", "build/conf/templateconf.cfg",
        "--expect-machine", "apollo-qvp", "--expect-tmpdir", "build/tmp_baremetal",
        "--expect-variant", "cfg2", "--expect-pc-cpus", "4",
        "--linux-source", str(recipe_repo), "--yocto-repos", "layers/poky",
        "--deploy-dir", str(deploy), "--require-outputs", "image",
        "--dry-run", "--self-test-metadata", str(metadata),
        "--schema", str(SCHEMAS / "gic720ae-yocto-provenance.schema.json"),
        "--output", str(output),
    )
    assert result.returncode != 0
    assert json.loads(output.read_text())["reason"] == "forbidden_command"


def test_yocto_provenance_accepts_only_exact_task27_canonical_command() -> None:
    tool = load_tool("capture_gic720ae_yocto_provenance.py")
    canonical = (
        "(source layers/poky/oe-init-build-env build >/dev/null &&\n"
        "  MACHINE=apollo-qvp bitbake -c cleansstate linux-yocto-rt\n"
        "  nexios-bsp-initramfs); MACHINE=apollo-qvp ./yocto_build.sh --bsp"
    )
    args = argparse.Namespace(
        build_command=canonical,
        require_taskhash="linux-yocto-rt:cleansstate,nexios-bsp-initramfs:build",
    )
    assert tool.build_argv(args) == [tool.TASK27_CANONICAL_BUILD]
    for changed in (
        canonical.replace("  ", " ", 1),
        canonical.replace("\n", " ", 1),
        canonical + " ",
        canonical.replace("--bsp", "--bsp; touch PWNED"),
    ):
        args.build_command = changed
        try:
            tool.build_argv(args)
        except tool.ContractError as error:
            assert error.reason == "forbidden_command"
        else:
            raise AssertionError("non-canonical Task 27 command was accepted")


def test_task27_canonical_command_maps_to_fixed_argv_not_user_shell_text() -> None:
    tool = load_tool("capture_gic720ae_yocto_provenance.py")
    assert tool.TASK27_BUILD_STEPS == (
        ("bitbake", "-c", "cleansstate", "linux-yocto-rt", "nexios-bsp-initramfs"),
        ("./yocto_build.sh", "--bsp"),
    )


def test_release_and_manual_negatives_do_not_require_fixture_label(
    tmp_path: Path,
) -> None:
    cases = (
        (
            "audit_gic720ae_release_commits.py",
            {"transition": "BLOCKED->PASS", "approved": False},
            "unapproved_status_transition",
            "gic720ae-release-audit.schema.json",
        ),
        (
            "run_gic720ae_manual_qa_postprocess.py",
            {"qbox": True, "fvp": False},
            "missing_fvp_evidence",
            "gic720ae-manual-qa.schema.json",
        ),
    )
    for index, (script, fixture, reason, schema) in enumerate(cases):
        source = tmp_path / f"fixture-{index}.json"
        source.write_text(json.dumps(fixture), encoding="utf-8")
        output = tmp_path / f"result-{index}.json"
        result = run_tool(
            script, "--self-test-negative", str(source),
            "--schema", str(SCHEMAS / schema), "--output", str(output),
        )
        assert result.returncode != 0
        assert json.loads(output.read_text())["reason"] == reason


def test_runtime_timeout_terminates_descendant_process_group(tmp_path: Path) -> None:
    script = tmp_path / "local_build.sh"
    script.write_text(
        "#!/bin/sh\nsleep 300 &\necho $! > child.pid\nwait\n", encoding="utf-8",
    )
    script.chmod(0o755)
    output = tmp_path / "result.json"
    result = run_tool(
        "capture_gic720ae_runtime_provenance.py",
        "--component", "qbox", "--producer-mode", "clean_build",
        "--cwd", str(tmp_path), "--build-command", "./local_build.sh clean-build",
        "--source-repos", ".", "--require-outputs", "missing", "--timeout", "1",
        "--schema", str(SCHEMAS / "gic720ae-runtime-provenance.schema.json"),
        "--output", str(output),
    )
    assert result.returncode != 0
    child_pid = int((tmp_path / "child.pid").read_text())
    child_alive = True
    try:
        os.kill(child_pid, 0)
    except ProcessLookupError:
        child_alive = False
    if child_alive:
        os.kill(child_pid, signal.SIGKILL)
        raise AssertionError(f"residual child process: {child_pid}")
