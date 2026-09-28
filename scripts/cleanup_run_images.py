#!/usr/bin/env python3
"""Conservative cleanup of generated runtime disk copies; never remove logs.

Default is dry-run. Run with --apply only while launchers are quiescent; process
inspection cannot prevent another terminal from starting a VM after inspection.
Use --keep for disks referenced by external tools/configuration outside build/.
"""
import argparse
import json
import math
import os
from pathlib import Path
import re
import shutil
import stat
import subprocess
import time


EXCLUDED = re.compile(r"builder|prepared|bundle|custom|compose|container-storage|overlay|demo-aib", re.I)
IMAGE_SUFFIXES = {".qcow", ".qcow2", ".vmdk", ".vhd", ".vhdx"}


def run_json(command):
    result = subprocess.run(command, check=True, capture_output=True, text=True, timeout=20)
    return json.loads(result.stdout)


def descendants(root):
    """Inspect metadata/backing files even in retained builder directories."""
    errors = []
    found = []
    for directory, dirs, files in os.walk(root, followlinks=False, onerror=errors.append):
        dirs[:] = [name for name in dirs if not (Path(directory) / name).is_symlink()]
        found.extend(Path(directory) / name for name in files)
    return found, [str(error) for error in errors]


def inventory(workspace):
    build = workspace / "build"
    roots = [build / "autosd"] + sorted(build.glob("qbox-*")) + sorted(build.glob("qemu-*"))
    candidates, sources, overlays, errors = [], set(), [], []
    for root in roots:
        if root.is_symlink() or not root.is_dir():
            continue
        files, failures = descendants(root)
        errors.extend(failures)
        overlays.extend(path for path in files if path.suffix in IMAGE_SUFFIXES)
        for metadata in files:
            if metadata.name != "launch.json":
                continue
            try:
                plan = json.loads(metadata.read_text())
                source = plan.get("source_rootfs")
                if source:
                    source = Path(source)
                    if not source.is_absolute():
                        raise ValueError("relative source_rootfs")
                    sources.add(source.resolve())
                disk = metadata.parent / "rootfs.wic"
                if not disk.exists() and not disk.is_symlink():
                    continue
                reason = None
                if metadata.is_symlink() or not source or not source.exists():
                    reason = "missing independent source/provenance"
                elif source.resolve() == disk.resolve():
                    reason = "canonical/reused source disk"
                elif EXCLUDED.search(str(disk.relative_to(build))):
                    reason = "reserved customization/builder directory"
                elif str(disk) not in json.dumps([plan.get("command"), plan.get("environment")]):
                    reason = "launch metadata does not reference disk"
                elif plan.get("reused_disk") or (plan.get("disk_path") and Path(plan["disk_path"]) != disk):
                    reason = "reused disk"
                info = disk.lstat()
                candidates.append({"path": str(disk), "family": root.name,
                                   "mtime": info.st_mtime, "allocated_bytes": info.st_blocks * 512,
                                   "identity": [info.st_dev, info.st_ino, info.st_size, info.st_mtime_ns],
                                   "reason": reason})
            except (OSError, ValueError, TypeError, AttributeError) as error:
                errors.append(f"{metadata}: {error}")
    return candidates, sources, overlays, errors


def runtime_protection(paths):
    """Any incomplete process/storage inspection makes apply fail closed."""
    protected, errors = set(), []
    needles = {str(path).encode(): path for path in paths}
    for process in Path("/proc").iterdir():
        if not process.name.isdigit() or int(process.name) == os.getpid():
            continue
        try:
            command = (process / "cmdline").read_bytes()
            if not command:
                continue
            # Inspect all our processes, plus identifiable VM/dashboard processes
            # owned by other users. Unrelated system daemons need no FD access.
            relevant = any(marker in command.lower() for marker in
                           (b"qemu", b"qbox", b"autosd_dashboard", b"run_images"))
            if os.geteuid() != 0 and process.stat().st_uid != os.getuid() and not relevant:
                continue
            environment = (process / "environ").read_bytes()
            for needle, path in needles.items():
                if needle in command or needle in environment:
                    protected.add(path)
            for descriptor in (process / "fd").iterdir():
                try:
                    target = descriptor.resolve(strict=True)
                except FileNotFoundError:
                    continue
                if target in paths:
                    protected.add(target)
        except (FileNotFoundError, ProcessLookupError):
            continue
        except OSError as error:
            errors.append(f"process {process.name}: {error}")
    try:
        for loop in Path("/sys/block").glob("loop*/loop/backing_file"):
            value = loop.read_text().strip()
            if value:
                protected.add(Path("/" + value.lstrip("/")).resolve())
        mounts = subprocess.run(["findmnt", "--json", "--output", "SOURCE"], check=True,
                                capture_output=True, text=True, timeout=20).stdout
        for path in paths:
            if str(path) in mounts:
                protected.add(path)
    except (OSError, subprocess.SubprocessError) as error:
        errors.append(f"mount inspection: {error}")
    return protected, errors


def backing_protection(images):
    protected, errors = set(), []
    executable = shutil.which("qemu-img")
    if not executable:
        return protected, ["qemu-img is required for backing dependency inspection"]
    for image in images:
        if image.is_symlink():
            protected.add(image.resolve())
            continue
        try:
            chain = run_json([executable, "info", "--force-share", "--backing-chain", "--output=json", str(image)])
            for entry in chain:
                backing = entry.get("full-backing-filename") or entry.get("backing-filename")
                if backing:
                    path = Path(backing)
                    protected.add((image.parent / path).resolve() if not path.is_absolute() else path.resolve())
            # Runtime launchers explicitly request raw. Non-raw copies are retained.
            if chain and chain[0].get("format") != "raw" and image.name == "rootfs.wic":
                protected.add(image.resolve())
        except (OSError, ValueError, subprocess.SubprocessError) as error:
            errors.append(f"backing inspection {image}: {error}")
    return protected, errors


def select(candidates, sources, protected, keep, days=7, newest=2, now=None):
    now = time.time() if now is None else now
    retained = set()
    for family in {item["family"] for item in candidates}:
        entries = sorted((item for item in candidates if item["family"] == family),
                         key=lambda item: item["mtime"], reverse=True)
        retained.update(item["path"] for item in entries[:newest])
    for item in candidates:
        path = Path(item["path"])
        info = path.lstat()
        reason = item["reason"]
        if path.is_symlink() or not stat.S_ISREG(info.st_mode) or info.st_nlink != 1:
            reason = "symlink, non-regular file or hardlink"
        elif path.resolve() in sources:
            reason = "source for another launch"
        elif path.resolve() in protected:
            reason = "active/mounted/backing disk"
        elif any(path.resolve() == entry or entry in path.resolve().parents for entry in keep):
            reason = "explicit --keep"
        elif item["path"] in retained:
            reason = "newest retained per family"
        elif now - item["mtime"] < days * 86400:
            reason = "younger than retention age"
        item["reason"] = reason or "old independent runtime copy"
        item["decision"] = "keep" if reason else "candidate"
    return candidates


def apply(items):
    """Check inode and timestamp again; unlink individual files only."""
    for item in items:
        if item["decision"] != "candidate":
            continue
        path = Path(item["path"])
        if any(parent.is_symlink() for parent in path.parents):
            raise RuntimeError(f"disk parent became a symlink: {path}")
        info = path.lstat()
        identity = [info.st_dev, info.st_ino, info.st_size, info.st_mtime_ns]
        if path.is_symlink() or info.st_nlink != 1 or identity != item["identity"]:
            raise RuntimeError(f"disk changed after inspection: {path}")
        path.unlink()
        item["decision"] = "deleted"


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true", help="irreversibly unlink eligible runtime disks")
    parser.add_argument("--older-than-days", type=float, default=7)
    parser.add_argument("--keep-newest", type=int, default=2, help="copies retained per autosd/qbox-*/qemu-* family")
    parser.add_argument("--keep", action="append", default=[], type=Path, help="protect image or directory (repeatable)")
    args = parser.parse_args(argv)
    if not math.isfinite(args.older_than_days) or args.older_than_days < 0 or args.keep_newest < 0:
        parser.error("retention values must be finite and nonnegative")
    workspace = Path(__file__).resolve().parents[1]
    candidates, sources, overlays, errors = inventory(workspace)
    paths = {Path(item["path"]).resolve() for item in candidates}
    live, failures = runtime_protection(paths)
    errors.extend(failures)
    backing, failures = backing_protection(overlays + [Path(item["path"]) for item in candidates])
    errors.extend(failures)
    items = select(candidates, sources, live | backing, {path.resolve() for path in args.keep},
                   args.older_than_days, args.keep_newest)
    if args.apply and not errors:
        # Repeat active checks immediately before mutation.
        active, failures = runtime_protection(paths)
        errors.extend(failures)
        if not failures:
            for item in items:
                if Path(item["path"]).resolve() in active:
                    item.update(decision="keep", reason="active at final inspection")
            apply(items)
    print(json.dumps({"mode": "apply" if args.apply else "dry-run", "blocked": bool(errors),
                      "errors": errors, "items": items,
                      "eligible_allocated_bytes": sum(item["allocated_bytes"] for item in items
                                                      if item["decision"] in {"candidate", "deleted"}),
                      "note": "Logs and directories preserved. Deleted disks are not recoverable. Stop concurrent launchers; use --keep for external references. Complete /proc visibility may require sudo."}, indent=2))
    return 2 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
