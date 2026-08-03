#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# ///

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import time
from typing import Any


CANONICAL_ENDPOINT = "127.0.0.1:12341"
LEGACY_ENDPOINT = "127.0.0.1:12342"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def listening_ports() -> set[int]:
    ports: set[int] = set()
    for table in (Path("/proc/net/tcp"), Path("/proc/net/tcp6")):
        try:
            lines = table.read_text(encoding="ascii").splitlines()[1:]
        except OSError:
            continue
        for line in lines:
            fields = line.split()
            if len(fields) > 3 and fields[3] == "0A":
                ports.add(int(fields[1].rsplit(":", 1)[1], 16))
    return ports


def wait_for_listener(port: int, timeout: float) -> bool:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if port in listening_ports():
            return True
        time.sleep(0.2)
    return port in listening_ports()


def child_terminal_evidence(platform_out: Path) -> dict[str, Any]:
    evidence: dict[str, Any] = {}
    status_path = platform_out / "qbox-run.status"
    if status_path.is_file():
        value = status_path.read_text(encoding="utf-8").strip()
        if value.lstrip("-").isdigit():
            evidence["qbox_run_status"] = int(value)
    for name in ("result.json", "rd-aspen-result.json"):
        path = platform_out / name
        if not path.is_file():
            continue
        try:
            decoded = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        if isinstance(decoded, dict):
            evidence[name] = {
                key: decoded.get(key)
                for key in (
                    "blocker", "child_returncode", "platform_returncode", "verdict"
                )
                if key in decoded
            }
    codes = [
        value
        for value in (
            evidence.get("qbox_run_status"),
            *(record.get("platform_returncode") for record in evidence.values() if isinstance(record, dict)),
        )
        if isinstance(value, int)
    ]
    signals = {6: "SIGABRT", 7: "SIGBUS", 4: "SIGILL", 11: "SIGSEGV"}
    observed = []
    for code in codes:
        signal_number = -code if code < 0 else code - 128 if code >= 128 else 0
        if signal_number in signals:
            observed.append(signals[signal_number])
    if observed:
        evidence["signals"] = sorted(set(observed))
    return evidence


def terminal_reason(evidence: dict[str, Any]) -> str | None:
    for record in evidence.values():
        if not isinstance(record, dict):
            continue
        blocker = record.get("blocker")
        if isinstance(blocker, str) and blocker:
            return blocker
        returncode = record.get("platform_returncode")
        if isinstance(returncode, int) and returncode != 0:
            return f"platform_returncode:{returncode}"
    status = evidence.get("qbox_run_status")
    if isinstance(status, int) and status != 0:
        return f"qbox_run_status:{status}"
    return None


def require_live_child(platform_out: Path, *, listener_ready: bool) -> dict[str, Any]:
    evidence = child_terminal_evidence(platform_out)
    reason = terminal_reason(evidence)
    if reason is not None:
        raise RuntimeError(f"QBox child terminated before SI attach: {reason}")
    if not listener_ready:
        raise RuntimeError("SI listener is not ready")
    pid_path = platform_out / "qbox-run.pid"
    try:
        pid = int(pid_path.read_text(encoding="utf-8").strip())
    except (OSError, ValueError) as error:
        raise RuntimeError(f"QBox child PID is unavailable: {error}") from error
    if not Path(f"/proc/{pid}").is_dir():
        raise RuntimeError(f"QBox child PID {pid} is not live")
    evidence["qbox_run_pid"] = pid
    return evidence


def wait_for_live_listener(port: int, platform_out: Path, timeout: float) -> dict[str, Any]:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        ready = port in listening_ports()
        evidence = child_terminal_evidence(platform_out)
        reason = terminal_reason(evidence)
        if reason is not None:
            raise RuntimeError(f"QBox child terminated before SI attach: {reason}")
        if ready:
            return require_live_child(platform_out, listener_ready=True)
        time.sleep(0.2)
    return require_live_child(platform_out, listener_ready=port in listening_ports())


def validate_host_release(output: str, returncode: int) -> None:
    if returncode != 0:
        raise RuntimeError(f"host GDB release failed with rc={returncode}")
    if "TASK16_HOST_SC_MAIN_REACHED=1" not in output:
        raise RuntimeError("host GDB release did not observe a sc_main stop")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Prove CL0 and CL1 selectors on one five-thread SI GDB stub."
    )
    parser.add_argument("--launcher", type=Path, required=True)
    parser.add_argument("--symbols-json", type=Path, required=True)
    parser.add_argument("--require-manifest-hash", action="store_true")
    parser.add_argument("--endpoint", required=True)
    parser.add_argument("--cl0-symbol", required=True)
    parser.add_argument("--cl1-symbol", required=True)
    parser.add_argument("--expect-threads", type=int, required=True)
    parser.add_argument("--timeout", type=float, required=True)
    parser.add_argument("--out-dir", type=Path, required=True)
    return parser.parse_args()


def reject_endpoint(endpoint: str) -> None:
    if endpoint == LEGACY_ENDPOINT:
        raise ValueError(
            f"{LEGACY_ENDPOINT} is retired; use {CANONICAL_ENDPOINT} and "
            "select domain-si0 thread 1 or domain-si1 thread 2"
        )
    if endpoint != CANONICAL_ENDPOINT:
        raise ValueError(
            f"unsupported SI GDB endpoint {endpoint!r}; use {CANONICAL_ENDPOINT}"
        )


def load_selector(
    manifest: dict[str, Any], component_name: str, symbol: str
) -> dict[str, Any]:
    components = manifest.get("components")
    if not isinstance(components, dict):
        raise ValueError("manifest has no components object")
    record = components.get(component_name)
    if not isinstance(record, dict):
        raise ValueError(f"manifest has no {component_name} component")
    for field in ("elf", "gdb_script", "remote", "gdb_thread", "mpidr"):
        if field not in record:
            raise ValueError(f"{component_name} is missing {field}")
    elf = Path(str(record["elf"])).resolve()
    gdb_script = Path(str(record["gdb_script"])).resolve()
    symbols = record.get("symbols")
    locations = record.get("source_locations")
    if not elf.is_file() or not gdb_script.is_file():
        raise ValueError(f"{component_name} ELF or GDB script does not exist")
    if record.get("has_debug_info") is not True or record.get("has_debug_line") is not True:
        raise ValueError(f"{component_name} lacks required DWARF/source data")
    if not isinstance(symbols, dict) or symbol not in symbols:
        raise ValueError(f"{component_name} has no {symbol} symbol")
    if not isinstance(locations, dict) or symbol not in locations:
        raise ValueError(f"{component_name} has no source location for {symbol}")
    remote = str(record["remote"])
    if remote != CANONICAL_ENDPOINT:
        raise ValueError(f"{component_name} manifest remote is {remote}, not {CANONICAL_ENDPOINT}")
    thread = record["gdb_thread"]
    if not isinstance(thread, int) or thread < 1:
        raise ValueError(f"{component_name} has invalid gdb_thread")
    return {
        "component": component_name,
        "elf": elf,
        "elf_sha256": sha256(elf),
        "gdb_script": gdb_script,
        "thread": thread,
        "mpidr": int(str(record["mpidr"]), 0),
        "symbol": symbol,
        "symbol_address": int(str(symbols[symbol]), 0) & ~1,
        "source": str(locations[symbol]),
    }


def gdb_command(
    gdb: str, endpoint: str, cl0: dict[str, Any], cl1: dict[str, Any]
) -> list[str]:
    command = [gdb, "-q", "-batch", "-ex", "set pagination off", "-ex", "set confirm off"]
    command += ["-ex", f"file {cl0['elf']}", "-ex", f"target remote {endpoint}"]
    command += [
        "-ex",
        "python print('TASK16_THREADS=' + ','.join(str(t.num) for t in gdb.inferiors()[0].threads()))",
    ]
    for label, selector in (("CL0", cl0), ("CL1", cl1)):
        command += ["-ex", f"symbol-file {selector['elf']}"]
        command += ["-ex", f"thread {selector['thread']}"]
        command += ["-ex", f'printf "TASK16_{label}_THREAD=%d\\n", $_thread']
        command += ["-ex", f'printf "TASK16_{label}_PC=0x%lx\\n", (unsigned long)$pc']
        command += [
            "-ex",
            f'printf "TASK16_{label}_MPIDR=0x%lx\\n", (unsigned long)$mpidr_el1',
        ]
        command += ["-ex", "info symbol $pc", "-ex", "info line *$pc", "-ex", "list *$pc"]
    command += ["-ex", "detach"]
    return command


def marker(output: str, name: str) -> str:
    match = re.search(rf"^{re.escape(name)}=(.+)$", output, flags=re.MULTILINE)
    if match is None:
        raise ValueError(f"GDB output has no {name} marker")
    return match.group(1).strip()


def stop_runtime(root: Path, session: str, platform_out: Path) -> dict[str, Any]:
    helper = root / "scripts/run/run_qbox_apollo_fvp_full_tmux.sh"
    env = os.environ.copy()
    env["OUT_DIR"] = str(platform_out)
    stopped = subprocess.run(
        [str(helper), "--stop-session", session],
        cwd=root,
        env=env,
        capture_output=True,
        text=True,
        timeout=30,
        check=False,
    )
    active = subprocess.run(
        ["tmux", "has-session", "-t", session],
        capture_output=True,
        check=False,
    ).returncode == 0
    return {"returncode": stopped.returncode, "session_active": active}


def main() -> int:
    args = parse_args()
    root = Path(__file__).resolve().parents[2]
    out_dir = args.out_dir.resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    result_path = out_dir / "result.json"
    result: dict[str, Any] = {"status": "FAIL", "endpoint": args.endpoint}
    exit_code = 2
    session = f"gic720-t16-platform-{os.getpid()}"
    platform_out = out_dir / "platform"
    deadline = time.monotonic() + args.timeout
    launched = False
    try:
        reject_endpoint(args.endpoint)
        if args.expect_threads != 5:
            raise ValueError("--expect-threads must be 5 for the canonical SI topology")
        launcher = args.launcher.resolve()
        manifest_path = args.symbols_json.resolve()
        if not launcher.is_file() or not manifest_path.is_file():
            raise ValueError("launcher or symbols manifest does not exist")
        manifest_hash = sha256(manifest_path)
        decoded = json.loads(manifest_path.read_text(encoding="utf-8"))
        if not isinstance(decoded, dict):
            raise ValueError("manifest root is not an object")
        cl0 = load_selector(decoded, "scp-si0", args.cl0_symbol)
        cl1 = load_selector(decoded, "si-cl1-zephyr", args.cl1_symbol)
        if cl0["thread"] == cl1["thread"]:
            raise ValueError("CL0 and CL1 selectors alias one GDB thread")
        components = decoded.get("components")
        host = components.get("qbox-host") if isinstance(components, dict) else None
        if not isinstance(host, dict):
            raise ValueError("manifest has no qbox-host component")
        host_script = Path(str(host.get("gdb_script", ""))).resolve()
        host_elf = Path(str(host.get("elf", ""))).resolve()
        host_gdb = shutil.which(str(host.get("debugger", "gdb")))
        if host_gdb is None or not host_script.is_file() or not host_elf.is_file():
            raise ValueError("qbox-host debugger, script, or ELF is unavailable")
        launcher_command = [
            str(launcher), "--vscode", "--no-attach", "--multi-session",
            "--firmware-early-attach", "--session", session,
            "--out-dir", str(platform_out), "--",
            "--platform-param", f"platform.si_cl0_cpu_0.gdb_breakpoint={cl0['symbol_address']:#x}",
            "--platform-param", f"platform.si_cl1_cpu_0.gdb_breakpoint={cl1['symbol_address']:#x}",
        ]
        env = os.environ.copy()
        env.update({"LOCAL_DEBUG_SKIP_MANIFEST": "1", "LOCAL_DEBUG_MANIFEST": str(manifest_path)})
        launched = True
        launched_result = subprocess.run(
            launcher_command, cwd=root, env=env, capture_output=True, text=True,
            timeout=max(0.1, deadline - time.monotonic()), check=False,
        )
        (out_dir / "launcher.log").write_text(
            launched_result.stdout + launched_result.stderr, encoding="utf-8"
        )
        if launched_result.returncode != 0:
            raise RuntimeError(f"launcher failed with rc={launched_result.returncode}")
        if args.require_manifest_hash and sha256(manifest_path) != manifest_hash:
            raise RuntimeError("symbols manifest changed during launch")
        host_command = [
            host_gdb, "-q", "-batch", "-x", str(host_script),
            "-ex", "target remote 127.0.0.1:12339", "-ex", "continue",
            "-ex", 'printf "TASK16_HOST_SC_MAIN_REACHED=1\\n"',
            "-ex", "delete breakpoints", "-ex", "detach",
        ]
        host_started = datetime.now(timezone.utc).isoformat()
        host_result = subprocess.run(
            host_command, cwd=root, capture_output=True, text=True,
            timeout=max(0.1, deadline - time.monotonic()), check=False,
        )
        host_finished = datetime.now(timezone.utc).isoformat()
        host_output = host_result.stdout + host_result.stderr
        (out_dir / "host-gdb.log").write_text(host_output, encoding="utf-8")
        result["host_release"] = {
            "command": host_command, "returncode": host_result.returncode,
            "started_at": host_started, "finished_at": host_finished,
            "gdb_sha256": sha256(Path(host_gdb)), "elf": str(host_elf),
            "elf_sha256": sha256(host_elf), "script": str(host_script),
            "script_sha256": sha256(host_script),
        }
        validate_host_release(host_output, host_result.returncode)
        result["child_before_si_attach"] = wait_for_live_listener(
            12341, platform_out, max(0.1, deadline - time.monotonic())
        )
        if 12342 in listening_ports():
            raise RuntimeError("retired SI endpoint 127.0.0.1:12342 unexpectedly listens")
        gdb = shutil.which("gdb-multiarch")
        if gdb is None:
            raise RuntimeError("gdb-multiarch is required")
        command = gdb_command(gdb, args.endpoint, cl0, cl1)
        gdb_result = subprocess.run(
            command, cwd=root, capture_output=True, text=True,
            timeout=max(0.1, deadline - time.monotonic()), check=False,
        )
        gdb_output = gdb_result.stdout + gdb_result.stderr
        (out_dir / "gdb.log").write_text(gdb_output, encoding="utf-8")
        if gdb_result.returncode != 0:
            raise RuntimeError(f"gdb-multiarch -batch failed with rc={gdb_result.returncode}")
        threads = sorted({int(value) for value in marker(gdb_output, "TASK16_THREADS").split(",")})
        observed: dict[str, Any] = {}
        for label, selector in (("CL0", cl0), ("CL1", cl1)):
            observed[label.lower()] = {
                **selector,
                "elf": str(selector["elf"]),
                "gdb_script": str(selector["gdb_script"]),
                "observed_thread": int(marker(gdb_output, f"TASK16_{label}_THREAD")),
                "observed_pc": int(marker(gdb_output, f"TASK16_{label}_PC"), 0) & ~1,
                "observed_mpidr": int(marker(gdb_output, f"TASK16_{label}_MPIDR"), 0),
            }
        failures = []
        if len(threads) != args.expect_threads:
            failures.append(f"expected {args.expect_threads} threads, observed {threads}")
        for label, selector in observed.items():
            for expected_key, observed_key in (
                ("thread", "observed_thread"), ("symbol_address", "observed_pc"),
                ("mpidr", "observed_mpidr"),
            ):
                if selector[expected_key] != selector[observed_key]:
                    failures.append(f"{label} {observed_key} mismatch")
            source_name = Path(str(selector["source"]).split(":", 1)[0]).name
            if selector["symbol"] not in gdb_output or source_name not in gdb_output:
                failures.append(f"{label} symbol/source was not resolved by live GDB")
        if failures:
            raise RuntimeError("; ".join(failures))
        result.update({
            "status": "PASS", "manifest": str(manifest_path),
            "manifest_sha256": manifest_hash, "thread_count": len(threads),
            "threads": threads, "selectors": observed, "gdb": {
                "path": gdb, "sha256": sha256(Path(gdb)),
                "command": command, "returncode": gdb_result.returncode,
            }, "launcher": {"path": str(launcher), "sha256": sha256(launcher),
                "command": launcher_command, "returncode": launched_result.returncode},
            "legacy_endpoint": {"endpoint": LEGACY_ENDPOINT, "listening": False},
        })
        local_build_dir = manifest_path.parent.parent
        runtime_paths = {
            "platforms_vp": local_build_dir / "work/qbox-platform/platforms-vp",
            "libqemu_aarch64": local_build_dir / (
                "work/qbox-platform/_deps/libqemu-build/qemu-prefix/lib/"
                "libqemu-system-aarch64.so"
            ),
        }
        result["runtime_artifacts"] = {
            name: {"path": str(path), "sha256": sha256(path)}
            for name, path in runtime_paths.items()
            if path.is_file()
        }
        version = subprocess.run(
            [gdb, "--version"], capture_output=True, text=True, check=False
        )
        result["gdb"]["version"] = version.stdout.splitlines()[0]
        exit_code = 0
    except (OSError, ValueError, RuntimeError, json.JSONDecodeError, subprocess.TimeoutExpired) as error:
        result["error"] = str(error)
        result["child_failure"] = child_terminal_evidence(platform_out)
        print(f"error: {error}", file=sys.stderr)
    finally:
        try:
            cleanup = stop_runtime(root, session, platform_out) if launched else {
                "returncode": 0, "session_active": False
            }
        except (OSError, subprocess.TimeoutExpired) as error:
            cleanup = {"returncode": 2, "session_active": True, "error": str(error)}
        result["cleanup"] = cleanup
        if cleanup["returncode"] != 0 or cleanup["session_active"]:
            result["status"] = "FAIL"
        result_path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return exit_code if result["status"] == "PASS" else 2


if __name__ == "__main__":
    raise SystemExit(main())
