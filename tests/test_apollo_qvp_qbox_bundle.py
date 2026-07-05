from __future__ import annotations

import json
import os
from pathlib import Path
import stat
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/test/validate_apollo_qvp_qbox_bundle.py"


def write_file(path: Path, text: str = "") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def write_executable(path: Path) -> None:
    write_file(path, "#!/bin/sh\n")
    path.chmod(path.stat().st_mode | stat.S_IXUSR)


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def run_validator(bundle: Path, output: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT), "--bundle", str(bundle), "--output", str(output)],
        cwd=ROOT,
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )


def write_manifest(bundle: Path, targets: list[str]) -> None:
    required = [
        "platforms-vp",
        "lib/libqbox.so",
        "lib/libqemu-system-aarch64.so",
        "qbox-apollo-qvp-env.sh",
        "platforms/apollo/apollo-qvp.lua",
    ]
    required.extend(f"lib/{target}.so" for target in targets if target != "platforms-vp")
    manifest = {
        "bundle": "qbox-apollo-qvp",
        "machine": "apollo-qvp",
        "required_targets": targets,
        "required_artifacts": [
            {
                "category": "fixture",
                "bundle_path": str(bundle / relpath),
                "relative_path": relpath,
            }
            for relpath in required
        ],
    }
    write_file(bundle / "qbox-apollo-qvp-manifest.json", json.dumps(manifest, indent=2))


def write_bundle(bundle: Path, targets: list[str] | None = None) -> Path:
    selected_targets = targets or ["platforms-vp", "keep_alive"]
    write_executable(bundle / "platforms-vp")
    write_file(bundle / "platforms/apollo/apollo-qvp.lua", "return {}\n")
    write_file(bundle / "lib/libqbox.so")
    write_file(bundle / "lib/libqemu-system-aarch64.so")
    for target in selected_targets:
        if target != "platforms-vp":
            write_file(bundle / "lib" / f"{target}.so")
    write_file(
        bundle / "qbox-apollo-qvp-env.sh",
        'export LD_LIBRARY_PATH="${QBOX_APOLLO_QVP_BUNDLE_DIR}/lib${LD_LIBRARY_PATH:+:${LD_LIBRARY_PATH}}"\n',
    )
    write_manifest(bundle, selected_targets)
    return bundle


def missing_ids(report: dict) -> set[str]:
    return {entry["id"] for entry in report["missing_required"]}


def test_validator_passes_for_complete_fixture_bundle(tmp_path: Path) -> None:
    # Given: a fixture bundle containing the executable, Lua, modules, manifest, and env file.
    bundle = write_bundle(tmp_path / "qbox-apollo-qvp")
    output = tmp_path / "result.json"

    # When: the validator checks the bundle through the public CLI.
    result = run_validator(bundle, output)

    # Then: the JSON report is a machine-readable pass with no missing entries.
    assert result.returncode == 0, result.stderr
    report = load_json(output)
    assert report["status"] == "pass"
    assert report["bundle"] == str(bundle.resolve())
    assert report["missing_required"] == []
    assert {check["name"] for check in report["checks"]} == {
        "environment",
        "executable",
        "lua-config",
        "manifest",
        "shared-libraries",
    }


def test_validator_fails_when_libqemu_is_missing(tmp_path: Path) -> None:
    # Given: an otherwise complete bundle without the required libqemu shared library.
    bundle = write_bundle(tmp_path / "qbox-apollo-qvp")
    os.remove(bundle / "lib/libqemu-system-aarch64.so")
    output = tmp_path / "result.json"

    # When: the validator checks the incomplete bundle.
    result = run_validator(bundle, output)

    # Then: it exits nonzero and reports the missing shared library by stable id.
    assert result.returncode == 1
    report = load_json(output)
    assert report["status"] == "fail"
    assert "shared:libqemu-system-aarch64.so" in missing_ids(report)
    assert "manifest:required_artifacts:lib/libqemu-system-aarch64.so" in missing_ids(report)


def test_validator_fails_when_env_does_not_cover_required_library_dir(tmp_path: Path) -> None:
    # Given: a bundle whose environment file sets LD_LIBRARY_PATH to the wrong directory.
    bundle = write_bundle(tmp_path / "qbox-apollo-qvp")
    write_file(
        bundle / "qbox-apollo-qvp-env.sh",
        'export LD_LIBRARY_PATH="${QBOX_APOLLO_QVP_BUNDLE_DIR}/other"\n',
    )
    output = tmp_path / "result.json"

    # When: the validator checks runtime library path coverage.
    result = run_validator(bundle, output)

    # Then: it fails with a machine-readable missing entry for the lib directory.
    assert result.returncode == 1
    report = load_json(output)
    assert report["status"] == "fail"
    assert "env:ld_library_path:lib" in missing_ids(report)


def test_validator_fails_when_manifest_required_artifact_is_stale(tmp_path: Path) -> None:
    # Given: a bundle manifest that names an artifact no longer present in the bundle.
    bundle = write_bundle(tmp_path / "qbox-apollo-qvp")
    os.remove(bundle / "lib/keep_alive.so")
    output = tmp_path / "result.json"

    # When: the validator cross-checks manifest-required artifacts.
    result = run_validator(bundle, output)

    # Then: both the module check and manifest consistency check report the stale path.
    assert result.returncode == 1
    report = load_json(output)
    assert "module:keep_alive" in missing_ids(report)
    assert "manifest:required_artifacts:lib/keep_alive.so" in missing_ids(report)


def test_validator_accepts_manifest_documented_lua_compatibility_path(tmp_path: Path) -> None:
    # Given: a bundle with a manifest-declared Lua compatibility path instead of apollo-qvp.lua.
    bundle = write_bundle(tmp_path / "qbox-apollo-qvp")
    os.remove(bundle / "platforms/apollo/apollo-qvp.lua")
    write_file(bundle / "platforms/apollo/apollo-fvp.lua", "return {}\n")
    manifest = load_json(bundle / "qbox-apollo-qvp-manifest.json")
    manifest["compatibility_paths"] = {"apollo_qvp_lua": "platforms/apollo/apollo-fvp.lua"}
    manifest["required_artifacts"] = [
        entry
        for entry in manifest["required_artifacts"]
        if entry["relative_path"] != "platforms/apollo/apollo-qvp.lua"
    ]
    write_file(bundle / "qbox-apollo-qvp-manifest.json", json.dumps(manifest, indent=2))
    output = tmp_path / "result.json"

    # When: the validator checks Lua config presence.
    result = run_validator(bundle, output)

    # Then: the documented compatibility path satisfies the Lua config contract.
    assert result.returncode == 0, result.stderr
    report = load_json(output)
    lua_check = next(check for check in report["checks"] if check["name"] == "lua-config")
    assert lua_check["details"]["compatibility_path"] == "platforms/apollo/apollo-fvp.lua"
