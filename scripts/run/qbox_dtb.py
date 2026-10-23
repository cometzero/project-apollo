"""Read the image DT selection without requiring an installed QBox provider."""
from __future__ import annotations

import json
from pathlib import Path
import subprocess


LEGACY_DTB = "apollo-qvp-saturn-v.dtb"


def read_dtb_config(conf: Path) -> tuple[Path | None, int | None]:
    if not conf.exists():
        return None, None
    conf = conf.resolve()
    value = json.loads(conf.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"qboxconf root must be an object: {conf}")
    images, environment = value.get("images", {}), value.get("env", {})
    if not isinstance(images, dict) or not isinstance(environment, dict):
        raise ValueError(f"qboxconf images/env must be objects: {conf}")
    selected = images.get("ap_dtb") or images.get("dtb")
    dtb = None
    if selected is not None:
        if (not isinstance(selected, str) or not selected
                or Path(selected).is_absolute() or ".." in Path(selected).parts
                or any(ord(char) < 32 for char in selected)):
            raise ValueError(f"qboxconf DTB must be a safe relative path: {conf}")
        dtb = conf.parent / selected
    raw_count = environment.get("QBOX_APOLLO_NUM_CPUS")
    count = None
    if raw_count is not None:
        if (not isinstance(raw_count, str) or not raw_count.isdecimal()
                or not 1 <= int(raw_count) <= 16):
            raise ValueError(f"qboxconf CPU count must be a decimal string in 1..16: {conf}")
        count = int(raw_count)
    return dtb, count


def deployment_dtb(deploy: Path, image: str) -> Path:
    selected, _ = read_dtb_config(deploy / f"{image}-apollo-qvp.qboxconf")
    return selected if selected is not None else deploy / LEGACY_DTB


def resolve_cpu_count(requested: int | None, configured: int | None,
                      dtb: Path, *, explicit_dtb: bool = False) -> int:
    count = requested if requested is not None else configured or 4
    # Older manifests did not declare a CPU population; retain their direct
    # boot convention (a full SoC DT plus an explicit nr_cpus limit).
    if configured is None:
        return count
    if not explicit_dtb and count != configured:
        raise ValueError(
            f"requested {count} CPUs but the image manifest selects {configured}; "
            "provide --dtb for the requested CPU population"
        )
    result = subprocess.run(["fdtget", "-l", str(dtb), "/cpus"],
                            capture_output=True, text=True)
    if result.returncode:
        raise ValueError(f"cannot read CPU topology from {dtb}: {result.stderr.strip()}")
    actual = sum(name.startswith("cpu@") for name in result.stdout.splitlines())
    if actual != count:
        raise ValueError(f"DTB {dtb} describes {actual} CPUs; requested {count}")
    return count
