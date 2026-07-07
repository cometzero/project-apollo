from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/test/validate_qboxconf.py"


def write_file(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def run_validator(qboxconf: Path, output: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT), "--qboxconf", str(qboxconf), "--output", str(output)],
        cwd=ROOT,
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )


def complete_qboxconf() -> dict:
    return {
        "provider": {
            "name": "qbox-apollo-qvp-native",
            "bindir": "/build/tmp/sysroots-components/x86_64/qbox-apollo-qvp-native/usr/bin",
            "libdir": "/build/tmp/sysroots-components/x86_64/qbox-apollo-qvp-native/usr/lib",
            "module_dir": "/build/tmp/sysroots-components/x86_64/qbox-apollo-qvp-native/usr/lib/qbox",
            "data_dir": "/build/tmp/sysroots-components/x86_64/qbox-apollo-qvp-native/usr/share/qbox",
        },
        "sysroot": {
            "components_dir": "/build/tmp/sysroots-components/x86_64",
            "recipe_sysroot_native": "/build/tmp/work/x86_64/qbox-apollo-qvp-native/1.0/recipe-sysroot-native",
        },
        "exe": "platforms-vp",
        "config": "platforms/apollo/apollo-qvp.lua",
        "data": ["firmware-apollo-qvp.bin@0x0"],
        "images": {
            "wic": "nexios-image-apollo-qvp.wic",
            "rse_flash": "firmware-apollo-qvp.rse.bin",
        },
        "env": {
            "LD_LIBRARY_PATH": "${provider.libdir}:${provider.module_dir}",
        },
    }


def missing_ids(report: dict) -> set[str]:
    return {entry["id"] for entry in report["missing_required"]}


def test_validator_passes_for_complete_qboxconf(tmp_path: Path) -> None:
    # Given: a complete qboxconf with provider, sysroot, executable, config, image, and env metadata.
    qboxconf = tmp_path / "nexios-image-apollo-qvp.qboxconf"
    write_file(qboxconf, json.dumps(complete_qboxconf(), indent=2))
    output = tmp_path / "result.json"

    # When: the validator checks the qboxconf through the public CLI.
    result = run_validator(qboxconf, output)

    # Then: the JSON report is a machine-readable pass with no missing entries.
    assert result.returncode == 0, result.stderr
    report = load_json(output)
    assert report["status"] == "pass"
    assert report["qboxconf"] == str(qboxconf.resolve())
    assert report["missing_required"] == []
    assert {check["name"] for check in report["checks"]} == {
        "json",
        "paths",
        "provider",
        "shape",
        "sysroot",
    }


def test_validator_fails_for_malformed_json(tmp_path: Path) -> None:
    # Given: a qboxconf path containing malformed JSON.
    qboxconf = tmp_path / "bad.qboxconf"
    write_file(qboxconf, '{"provider": ')
    output = tmp_path / "result.json"

    # When: the validator parses the qboxconf.
    result = run_validator(qboxconf, output)

    # Then: it exits nonzero and records a stable malformed JSON id.
    assert result.returncode == 1
    report = load_json(output)
    assert report["status"] == "fail"
    assert "json:malformed" in missing_ids(report)


def test_validator_fails_when_provider_or_sysroot_fields_are_missing(tmp_path: Path) -> None:
    # Given: a qboxconf with required provider and sysroot fields removed.
    payload = complete_qboxconf()
    del payload["provider"]["bindir"]
    del payload["provider"]["module_dir"]
    del payload["sysroot"]["recipe_sysroot_native"]
    qboxconf = tmp_path / "missing.qboxconf"
    write_file(qboxconf, json.dumps(payload, indent=2))
    output = tmp_path / "result.json"

    # When: the validator checks the incomplete qboxconf.
    result = run_validator(qboxconf, output)

    # Then: each missing field is reported by a stable id for recipe/runner callers.
    assert result.returncode == 1
    report = load_json(output)
    assert report["status"] == "fail"
    ids = missing_ids(report)
    assert "provider:bindir" in ids
    assert "provider:module_dir" in ids
    assert "sysroot:recipe_sysroot_native" in ids


def test_validator_fails_for_unsafe_relative_paths(tmp_path: Path) -> None:
    # Given: a qboxconf with paths that would escape the deploy/config directory.
    payload = complete_qboxconf()
    payload["exe"] = "../platforms-vp"
    payload["config"] = "/tmp/apollo-qvp.lua"
    payload["images"]["wic"] = "../nexios-image-apollo-qvp.wic"
    qboxconf = tmp_path / "unsafe.qboxconf"
    write_file(qboxconf, json.dumps(payload, indent=2))
    output = tmp_path / "result.json"

    # When: the validator checks path safety.
    result = run_validator(qboxconf, output)

    # Then: it rejects each unsafe path with stable ids instead of accepting stale or escaped artifacts.
    assert result.returncode == 1
    report = load_json(output)
    ids = missing_ids(report)
    assert "path:exe" in ids
    assert "path:config" in ids
    assert "path:images:wic" in ids
