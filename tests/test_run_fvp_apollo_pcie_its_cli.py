from __future__ import annotations

import importlib.util
from pathlib import Path
import subprocess
import sys

import pytest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/run/run_fvp_apollo_pcie_its.py"


def load_runner():
    spec = importlib.util.spec_from_file_location("fvp_pcie_its_cli", SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


@pytest.mark.parametrize("kind", ["outside", "symlink"])
def test_cli_rejects_uncontained_output_before_creating_a_receipt(
    tmp_path: Path, kind: str
) -> None:
    # Given: an output route that is outside the repository or traverses a symlink.
    target = tmp_path / "external-output"
    output = target
    if kind == "symlink":
        output = tmp_path / "output-link"
        output.symlink_to(target, target_is_directory=True)

    # When: the actual offline CLI receives the unsafe route.
    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "--profile-dir",
            str(tmp_path / "missing-profile"),
            "--out-dir",
            str(output),
            "--timeout",
            "0",
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )

    # Then: it fails before a result can be materialized through that route.
    assert result.returncode == 2
    assert "output_path" in result.stderr
    assert not (target / "result.json").exists()


def test_output_parser_rejects_workspace_symlink_before_writing(tmp_path: Path) -> None:
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    target = tmp_path / "target"
    link = workspace / "link"
    link.symlink_to(target, target_is_directory=True)

    runner = load_runner()

    with pytest.raises(runner.RunError, match="output_path_symlink"):
        runner.parse_output_dir(link, workspace)


def test_output_writer_rejects_a_parent_swap_before_creating_a_receipt(
    tmp_path: Path,
) -> None:
    workspace = tmp_path / "workspace"
    checked = workspace / "checked"
    output = checked / "out"
    output.mkdir(parents=True)
    external = tmp_path / "external"
    external.mkdir()
    runner = load_runner()
    handle = runner.parse_output_dir(output, workspace)
    checked.rename(workspace / "checked-moved")
    checked.symlink_to(external, target_is_directory=True)

    with pytest.raises(runner.RunError, match="output_path_changed"):
        runner.atomic_write(handle, {"status": "fail"})

    assert not (external / "out" / "result.json").exists()
    assert not list((workspace / "checked-moved" / "out").glob(".*.tmp"))
    handle.close()


def test_output_writer_removes_a_staged_receipt_after_a_parent_swap(
    tmp_path: Path,
) -> None:
    workspace = tmp_path / "workspace"
    checked = workspace / "checked"
    output = checked / "out"
    output.mkdir(parents=True)
    external = tmp_path / "external"
    external.mkdir()
    runner = load_runner()
    handle = runner.parse_output_dir(output, workspace)
    staged = handle.stage_json({"status": "fail"})
    checked.rename(workspace / "checked-moved")
    checked.symlink_to(external, target_is_directory=True)

    with pytest.raises(runner.RunError, match="output_path_changed"):
        staged.commit()

    assert not (external / "out" / "result.json").exists()
    assert not list((workspace / "checked-moved" / "out").glob(".*.tmp"))
    handle.close()


def test_output_writer_rejects_a_directory_move_before_creating_a_receipt(
    tmp_path: Path,
) -> None:
    workspace = tmp_path / "workspace"
    output = workspace / "out"
    output.mkdir(parents=True)
    runner = load_runner()
    handle = runner.parse_output_dir(output, workspace)
    output.rename(workspace / "out-moved")

    with pytest.raises(runner.RunError, match="output_path_changed"):
        runner.atomic_write(handle, {"status": "fail"})

    assert not (workspace / "out-moved" / "result.json").exists()
    assert not list((workspace / "out-moved").glob(".*.tmp"))
    handle.close()


def test_output_parser_rejects_lexical_traversal_without_creating_a_directory(
    tmp_path: Path,
) -> None:
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    runner = load_runner()

    with pytest.raises(runner.RunError, match="output_path_traversal"):
        runner.parse_output_dir(Path("out/../escape"), workspace)

    assert not (workspace / "escape").exists()
