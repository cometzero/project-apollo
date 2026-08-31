from __future__ import annotations

import json
from pathlib import Path
import subprocess


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/test/build_gic720ae_pcie_its_profile.py"


def run_builder(output_root: Path, machine: str = "apollo-fvp") -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            "python3",
            str(SCRIPT),
            "--machine",
            machine,
            "--output-root",
            str(output_root),
        ],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
        timeout=30,
    )


def assert_no_output(link: Path, target: Path) -> None:
    assert not (link / "profile.json").exists()
    assert list(target.iterdir()) == []


def test_cli_rejects_existing_symlink_without_writing(tmp_path: Path) -> None:
    target = tmp_path / "target"
    target.mkdir()
    link = tmp_path / "profile-link"
    link.symlink_to(target, target_is_directory=True)

    result = run_builder(link)

    assert result.returncode != 0
    assert "output_root_symlink_forbidden" in result.stderr
    assert_no_output(link, target)


def test_cli_rejects_symlink_ancestor_without_writing(tmp_path: Path) -> None:
    target = tmp_path / "target"
    target.mkdir()
    ancestor = tmp_path / "ancestor-link"
    ancestor.symlink_to(target, target_is_directory=True)
    output = ancestor / "child"

    result = run_builder(output, machine="invalid-machine")

    assert result.returncode != 0
    assert "output_root_symlink_forbidden" in result.stderr
    assert not output.exists()
    assert list(target.iterdir()) == []


def test_cli_rejects_case_variant_symlink_without_writing(tmp_path: Path) -> None:
    target = tmp_path / "CaseTarget"
    target.mkdir()
    ancestor = tmp_path / "CaseLink"
    ancestor.symlink_to(target, target_is_directory=True)
    output = ancestor / "Profile"

    result = run_builder(output, machine="invalid-machine")

    assert result.returncode != 0
    assert "output_root_symlink_forbidden" in result.stderr
    assert not output.exists()
    assert list(target.iterdir()) == []


def test_cli_rejects_active_default_root_without_writing() -> None:
    output = ROOT / "build/tmp_baremetal/todo5-invalid-output-root"
    assert not output.exists()

    result = run_builder(output, machine="invalid-machine")

    assert result.returncode != 0
    assert "active_default_path_forbidden" in result.stderr
    assert not output.exists()


def test_valid_root_keeps_normalized_failure_receipt(tmp_path: Path) -> None:
    output = tmp_path / "ordinary-profile"

    result = run_builder(output, machine="invalid-machine")

    receipt = json.loads((output / "profile.json").read_text(encoding="utf-8"))
    assert result.returncode != 0
    assert receipt["verdict"] == "FAIL"
    assert receipt["reason"] == "unsupported_machine"
    assert receipt["output_root"] == str(output)
    assert not (output / ".profile.json.tmp").exists()


def test_valid_root_rejects_symlink_receipt_path(tmp_path: Path) -> None:
    output = tmp_path / "ordinary-profile"
    output.mkdir()
    outside = tmp_path / "outside.json"
    outside.write_text("preserve", encoding="utf-8")
    receipt = output / "profile.json"
    receipt.symlink_to(outside)

    result = run_builder(output, machine="invalid-machine")

    error = json.loads(result.stderr)
    assert result.returncode != 0
    assert error["reason"] == "unsupported_machine"
    assert error["receipt_reason"] == "receipt_path_symlink_forbidden"
    assert outside.read_text(encoding="utf-8") == "preserve"
    assert receipt.is_symlink()
    assert not any(path.name.startswith(".profile.json.") for path in output.iterdir())
