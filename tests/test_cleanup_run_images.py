"""Cleanup policy tests use temporary disks, never workspace runtime images."""
import importlib.util
import json
from pathlib import Path

import pytest


spec = importlib.util.spec_from_file_location(
    "cleanup_run_images", Path(__file__).resolve().parents[1] / "scripts/cleanup_run_images.py")
cleanup = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cleanup)


def disk(tmp_path, name="qemu-test/old", source=None):
    source = source or tmp_path / "build/input.wic"
    source.parent.mkdir(parents=True, exist_ok=True)
    if not source.exists():
        source.write_bytes(b"source")
    path = tmp_path / "build" / name / "rootfs.wic"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(b"disk")
    (path.parent / "launch.json").write_text(json.dumps({
        "source_rootfs": str(source), "command": ["qemu", f"file={path}"]}))
    return path


def selection(tmp_path, protected=(), keep=(), newest=0, days=0):
    entries, sources, _, errors = cleanup.inventory(tmp_path)
    assert errors == []
    return cleanup.select(entries, sources, set(protected), set(keep), days, newest)


def test_default_is_nonmutating_and_apply_only_unlinks_disk(tmp_path):
    path = disk(tmp_path)
    log = path.parent / "uart.log"
    log.write_text("retained")
    entries = selection(tmp_path)
    assert entries[0]["decision"] == "candidate"
    assert path.exists()
    cleanup.apply(entries)
    assert not path.exists()
    assert log.read_text() == "retained"
    assert (path.parent / "launch.json").exists()


@pytest.mark.parametrize("protection", ["live", "keep", "directory", "source", "symlink", "hardlink"])
def test_protection(tmp_path, protection):
    path = disk(tmp_path)
    live, keep = set(), set()
    if protection == "live":
        live.add(path)
    elif protection == "keep":
        keep.add(path)
    elif protection == "directory":
        keep.add(path.parent)
    elif protection == "source":
        disk(tmp_path, "qemu-test/new", source=path)
    elif protection == "symlink":
        path.unlink()
        path.symlink_to(tmp_path / "build/input.wic")
    elif protection == "hardlink":
        (path.parent / "hardlink.wic").hardlink_to(path)
    entries = selection(tmp_path, live, keep)
    assert next(item for item in entries if item["path"] == str(path))["decision"] == "keep"
    cleanup.apply(entries)
    assert path.exists()


def test_scope_and_canonical_builder_preserved(tmp_path):
    disk(tmp_path, "unrelated/old")
    disk(tmp_path, "autosd/demo-prepared")
    disk(tmp_path, "autosd/demo-builder")
    disk(tmp_path, "qbox-test/session")
    entries = selection(tmp_path)
    assert len(entries) == 3
    eligible = [item for item in entries if item["decision"] == "candidate"]
    assert len(eligible) == 1
    assert eligible[0]["family"] == "qbox-test"


def test_age_and_newest(tmp_path):
    disk(tmp_path)
    assert selection(tmp_path, days=7)[0]["decision"] == "keep"
    assert selection(tmp_path, newest=2)[0]["decision"] == "keep"


def test_changed_disk_refuses_unlink(tmp_path):
    path = disk(tmp_path)
    entries = selection(tmp_path)
    path.write_bytes(b"modified disk")
    with pytest.raises(RuntimeError, match="changed after inspection"):
        cleanup.apply(entries)
    assert path.exists()


def test_swapped_parent_refuses_unlink(tmp_path):
    path = disk(tmp_path)
    entries = selection(tmp_path)
    original_parent = path.parent
    moved = original_parent.with_name("moved")
    original_parent.rename(moved)
    original_parent.symlink_to(moved, target_is_directory=True)
    with pytest.raises(RuntimeError, match="parent became a symlink"):
        cleanup.apply(entries)
    assert path.exists()


def test_apply_blocked_by_incomplete_inspection(tmp_path, monkeypatch, capsys):
    path = disk(tmp_path)
    monkeypatch.setattr(cleanup, "__file__", str(tmp_path / "scripts/cleanup_run_images.py"))
    monkeypatch.setattr(cleanup, "runtime_protection", lambda _: (set(), ["unreadable process"]))
    monkeypatch.setattr(cleanup, "backing_protection", lambda _: (set(), []))
    result = cleanup.main(["--apply", "--older-than-days", "0", "--keep-newest", "0"])
    report = json.loads(capsys.readouterr().out)
    assert result == 2
    assert report["blocked"]
    assert path.exists()


def test_backing_chain_protects_base(tmp_path, monkeypatch):
    base = disk(tmp_path)
    overlay = tmp_path / "overlay.qcow2"
    overlay.write_bytes(b"fake")
    monkeypatch.setattr(cleanup.shutil, "which", lambda _: "/usr/bin/qemu-img")
    monkeypatch.setattr(cleanup, "run_json", lambda command: [
        {"format": "qcow2", "full-backing-filename": str(base)}, {"format": "raw"}])
    protected, errors = cleanup.backing_protection([overlay])
    assert not errors
    assert base in protected
    assert selection(tmp_path, protected)[0]["decision"] == "keep"


def test_bad_metadata_fails_closed(tmp_path):
    path = disk(tmp_path)
    (path.parent / "launch.json").write_text("broken")
    entries, _, _, errors = cleanup.inventory(tmp_path)
    assert not entries
    assert errors


def test_missing_backing_tool_fails_closed(monkeypatch):
    monkeypatch.setattr(cleanup.shutil, "which", lambda _: None)
    assert cleanup.backing_protection([])[1]


@pytest.mark.parametrize("value", ["nan", "inf", "-1"])
def test_reject_nonfinite_retention(value):
    with pytest.raises(SystemExit):
        cleanup.main(["--older-than-days", value])
