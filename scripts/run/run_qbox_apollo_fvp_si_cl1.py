#!/usr/bin/env python3
"""Run Apollo FVP Safety Island CL1 Zephyr in an isolated QBox target."""

from __future__ import annotations

import argparse
import datetime as _dt
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import time
from typing import Any


REQUIRED_TARGETS = [
    "platforms-vp",
    "router",
    "keep_alive",
    "gs_memory",
    "loader",
    "char_backend_file",
    "uart-pl011",
    "arm_gicv3",
    "cpu_arm_cortexR82",
    "mhu320ae",
]

REQUIRED_MARKERS = {
    "cpu0_oor": "Out of Reset (OoR) completed on CPU: 0",
    "zephyr_boot": "Booting Zephyr OS",
    "shell": "uart:~$",
    "pfdi_agent": "pfdi_agent: PFDI Agent setup complete",
    "pfdi_service": "pfdi_mgmt: PFDI service ready",
}
OPTIONAL_MARKERS = {
    "cpu1_up": "Secondary CPU core 1",
    "cpu2_up": "Secondary CPU core 2",
    "cpu3_up": "Secondary CPU core 3",
    "si_network": "si_net_init: Network interface configured",
    "rpmsg_attached": "veth_rpmsg: RPMSG Endpoint: ATTACHED",
}
FAIL_PATTERNS = [
    "ASSERTION FAIL",
    "ZEPHYR FATAL ERROR",
    "Synchronous Abort",
    "Unsupported MHU",
    "Invalid Frame type",
    "Failed to initialize platform",
    "Failed to init mbox",
]


def workspace_root() -> Path:
    return Path(__file__).resolve().parents[2]


def qbox_build_dir(root: Path) -> Path:
    default_dir = root / "build/local-apollo-fvp/work/qbox-platform"
    return Path(
        os.environ.get(
            "QBOX_PLATFORM_BUILD_DIR",
            os.environ.get("QBOX_BUILD_DIR", str(default_dir)),
        )
    ).resolve()


def timestamp() -> str:
    return _dt.datetime.now().strftime("%Y%m%d-%H%M%S")


def read_text(path: Path) -> str:
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8", errors="replace")


def artifact_record(path: Path) -> dict[str, Any]:
    exists = path.exists()
    return {
        "path": str(path.resolve()),
        "exists": exists,
        "size": path.stat().st_size if exists and path.is_file() else None,
    }


def run(cmd: list[str], *, cwd: Path, env: dict[str, str] | None = None) -> None:
    print("+ " + " ".join(cmd), flush=True)
    subprocess.run(cmd, cwd=cwd, env=env, check=True)


def ensure_qbox_targets(root: Path, jobs: int) -> None:
    cmd = [
        "cmake",
        "--build",
        str(qbox_build_dir(root)),
        "--target",
        *REQUIRED_TARGETS,
        "--parallel",
        str(jobs),
    ]
    run(cmd, cwd=root)


def marker_hits(text: str) -> dict[str, dict[str, bool]]:
    return {
        "required": {
            name: marker in text for name, marker in REQUIRED_MARKERS.items()
        },
        "optional": {
            name: marker in text for name, marker in OPTIONAL_MARKERS.items()
        },
        "fail": {
            marker: marker in text for marker in FAIL_PATTERNS
        },
    }


def required_passed(hits: dict[str, dict[str, bool]]) -> bool:
    required = hits.get("required", {})
    return bool(required) and all(required.values())


def first_fail_pattern(hits: dict[str, dict[str, bool]]) -> str | None:
    for marker, hit in hits.get("fail", {}).items():
        if hit:
            return marker
    return None


def stop_process(proc: subprocess.Popen[bytes]) -> None:
    if proc.poll() is not None:
        return
    try:
        os.killpg(proc.pid, signal.SIGTERM)
    except ProcessLookupError:
        return
    try:
        proc.wait(timeout=10)
    except subprocess.TimeoutExpired:
        try:
            os.killpg(proc.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
        proc.wait(timeout=5)


def default_image(root: Path) -> Path:
    return root / "build/local-apollo-fvp/deploy/firmware/zephyr-demos-cl1.bin"


def default_symbols(root: Path) -> Path:
    return root / "build/local-apollo-fvp/deploy/firmware/zephyr-demos-cl1.elf"


def qbox_env(root: Path, args: argparse.Namespace) -> dict[str, str]:
    env = os.environ.copy()
    env.update(
        {
            "QBOX_APOLLO_SI_CL1_IMAGE": str(args.image.resolve()),
            "QBOX_APOLLO_SI_CL1_LOG": str((args.out_dir / "qbox-safety-island-cl1.log").resolve()),
            "QBOX_APOLLO_SI_CL1_UART_READ_FILE": str(args.uart_read_file.resolve())
            if args.uart_read_file
            else "/dev/null",
            "QBOX_APOLLO_SI_CL1_MHU_TRACE_FILE": str((args.out_dir / "mhuv3-trace.log").resolve()),
        }
    )
    if args.mhu_trace:
        env["QBOX_APOLLO_SI_CL1_MHU_TRACE"] = "true"
    if args.qemu_args:
        env["QBOX_APOLLO_SI_CL1_QEMU_ARGS"] = args.qemu_args
    return env


def write_result(
    args: argparse.Namespace,
    *,
    passed: bool,
    command: list[str],
    hits: dict[str, dict[str, bool]],
    blocker: str | None,
    timed_out: bool,
    duration_s: float,
    returncode: int | None,
) -> int:
    args.out_dir.mkdir(parents=True, exist_ok=True)
    result = {
        "passed": passed,
        "verdict": "pass" if passed else ("blocked" if blocker else "fail"),
        "task": "QAP-FULL-020",
        "boot_mode": "apollo-si-cl1-isolated",
        "safety_island_mode": "live-cl1",
        "completion_gate_effect": "isolated_milestone_only",
        "input_artifacts": {
            "si_cl1_image": artifact_record(args.image),
            "si_cl1_symbols": artifact_record(args.symbols),
            "conf": artifact_record(args.conf),
        },
        "console_logs": {
            "platform": str((args.out_dir / "qbox-platform.log").resolve()),
            "si_cl1": str((args.out_dir / "qbox-safety-island-cl1.log").resolve()),
            "mhu_trace": str((args.out_dir / "mhuv3-trace.log").resolve()),
        },
        "marker_groups": hits,
        "required_markers": REQUIRED_MARKERS,
        "optional_markers": OPTIONAL_MARKERS,
        "fail_patterns": FAIL_PATTERNS,
        "isolated_debt": [
            "AP/CL1 HIPC RPMsg attach is not required in isolated mode.",
            "CL0/PFDI monitor peer behavior is not required in isolated mode.",
            "This result does not satisfy integrated G3 or final G4/G5 gates.",
        ],
        "blocker": blocker,
        "timed_out": timed_out,
        "duration_s": round(duration_s, 3),
        "returncode": returncode,
        "command": command,
        "runner_argv": sys.argv,
    }
    summary = [
        f"passed: {result['passed']}",
        f"verdict: {result['verdict']}",
        f"task: {result['task']}",
        f"blocker: {blocker or 'none'}",
        f"timed_out: {timed_out}",
        f"duration_s: {result['duration_s']}",
        "required_markers:",
        *[
            f"  - {name}: {hit}"
            for name, hit in hits.get("required", {}).items()
        ],
        "optional_markers:",
        *[
            f"  - {name}: {hit}"
            for name, hit in hits.get("optional", {}).items()
        ],
    ]
    (args.out_dir / "result.json").write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    (args.out_dir / "summary.txt").write_text("\n".join(summary) + "\n", encoding="utf-8")
    print(args.out_dir)
    print(args.out_dir / "summary.txt")
    print(args.out_dir / "result.json")
    return 0 if passed else 1


def missing_inputs(args: argparse.Namespace) -> list[str]:
    missing = []
    if not args.image.exists():
        missing.append(f"missing_artifact:si_cl1_image:{args.image}")
    if args.symbols and not args.symbols.exists():
        missing.append(f"missing_artifact:si_cl1_symbols:{args.symbols}")
    if not args.conf.exists():
        missing.append(f"missing_artifact:conf:{args.conf}")
    return missing


def run_platform(args: argparse.Namespace) -> int:
    root = workspace_root()
    args.out_dir.mkdir(parents=True, exist_ok=True)
    platform_log = args.out_dir / "qbox-platform.log"
    si_log = args.out_dir / "qbox-safety-island-cl1.log"
    for log in [platform_log, si_log]:
        log.write_text("", encoding="utf-8")
    command = [
        str((qbox_build_dir(root) / "platforms-vp").resolve()),
        "-l",
        str(args.conf.resolve()),
    ]
    env = qbox_env(root, args)
    print("+ " + " ".join(command), flush=True)
    start = time.monotonic()
    proc = subprocess.Popen(
        command,
        cwd=root,
        env=env,
        stdout=platform_log.open("wb"),
        stderr=subprocess.STDOUT,
        start_new_session=True,
    )
    passed = False
    blocker: str | None = None
    timed_out = False
    hits: dict[str, dict[str, bool]] = marker_hits("")
    try:
        while args.timeout <= 0 or time.monotonic() - start < args.timeout:
            text = read_text(si_log) + "\n" + read_text(platform_log)
            hits = marker_hits(text)
            fail = first_fail_pattern(hits)
            if fail:
                blocker = f"si_cl1_fail_pattern:{fail}"
                break
            if required_passed(hits):
                passed = True
                break
            if proc.poll() is not None:
                blocker = f"qbox_exited_before_markers:{proc.returncode}"
                break
            time.sleep(0.5)
        else:
            timed_out = True
            blocker = "si_cl1_required_markers_timeout"
    finally:
        stop_process(proc)

    duration_s = time.monotonic() - start
    if proc.returncode not in (None, 0) and not passed and blocker is None:
        blocker = f"qbox_returncode:{proc.returncode}"
    return write_result(
        args,
        passed=passed,
        command=command,
        hits=hits,
        blocker=blocker,
        timed_out=timed_out,
        duration_s=duration_s,
        returncode=proc.returncode,
    )


def parse_args() -> argparse.Namespace:
    root = workspace_root()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--conf",
        type=Path,
        default=root / "tools/qbox-platform/platforms/apollo/apollo-si-cl1.lua",
    )
    parser.add_argument("--image", type=Path, default=default_image(root))
    parser.add_argument("--symbols", type=Path, default=default_symbols(root))
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=root / "build/qbox-apollo-fvp" / f"si-cl1-isolated-{timestamp()}",
    )
    parser.add_argument("--timeout", type=int, default=120)
    parser.add_argument("--jobs", type=int, default=max(1, (os.cpu_count() or 2) // 2))
    parser.add_argument(
        "--qbox-build-dir",
        type=Path,
        help=(
            "QBox CMake build directory. Defaults to "
            "build/local-apollo-fvp/work/qbox-platform."
        ),
    )
    parser.add_argument("--check-only", action="store_true")
    parser.add_argument("--skip-build", action="store_true")
    parser.add_argument("--mhu-trace", action="store_true")
    parser.add_argument("--qemu-args", default="")
    parser.add_argument("--uart-read-file", type=Path)
    args = parser.parse_args()
    args.conf = args.conf.resolve()
    args.image = args.image.resolve()
    args.symbols = args.symbols.resolve()
    args.out_dir = args.out_dir.resolve()
    if args.qbox_build_dir is not None:
        resolved_qbox_build_dir = str(args.qbox_build_dir.resolve())
        os.environ["QBOX_PLATFORM_BUILD_DIR"] = resolved_qbox_build_dir
        os.environ["QBOX_BUILD_DIR"] = resolved_qbox_build_dir
    if args.uart_read_file:
        args.uart_read_file = args.uart_read_file.resolve()
    return args


def main() -> int:
    args = parse_args()
    missing = missing_inputs(args)
    if missing or args.check_only:
        blocker = "; ".join(missing) if missing else None
        hits = marker_hits("")
        return write_result(
            args,
            passed=not missing,
            command=[],
            hits=hits,
            blocker=blocker,
            timed_out=False,
            duration_s=0.0,
            returncode=None,
        )
    if not args.skip_build:
        ensure_qbox_targets(workspace_root(), args.jobs)
    return run_platform(args)


if __name__ == "__main__":
    raise SystemExit(main())
