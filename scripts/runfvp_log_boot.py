#!/usr/bin/env python3
"""Run Apollo/RD-Aspen FVP headlessly and capture per-console boot logs."""

from __future__ import annotations

import argparse
import datetime as _dt
import json
import os
from pathlib import Path
import re
import shutil
import signal
import subprocess
import sys
import threading
import time


PORT_RE = re.compile(
    r"(?P<term>terminal_[A-Za-z0-9_]+): "
    r"Listening for serial connection on port (?P<port>\d+)"
)
ERROR_RE = re.compile(r"(\[ERR\]|\[ERROR\]|ERROR:)")

CHECKS = {
    "terminal_uart": {
        "name": "RSE / TF-M",
        "all": [
            "Starting TF-M BL1_1",
            "Jumping to BL2",
            "Jumping to the first image slot",
            "RSE to SCP SCMI power on AP succeeded",
        ],
    },
    "terminal_uart_si_cluster0": {
        "name": "Safety Island CL0 / SCP-firmware",
        "all": [
            "SSU initialized",
            "Module initialization complete",
        ],
    },
    "terminal_ns_uart0": {
        "name": "Primary Compute U-Boot/Linux",
        "all": [
            "U-Boot ",
            "Booting Linux on physical CPU",
            "Linux version",
        ],
        "any": [
            " login:",
            "root@",
        ],
    },
    "terminal_sec_uart": {
        "name": "TF-A / Secure-world AP",
        "all": [
            "NOTICE:  BL2:",
            "NOTICE:  BL2: Booting BL31",
            "NOTICE:  BL31:",
            "INFO:    BL31: Preparing for EL3 exit to normal world",
        ],
    },
    "terminal_uart_si_cluster1": {
        "name": "Safety Island CL1",
        "all": [
            "*** Booting Zephyr OS build",
            "Secondary CPU core 1",
        ],
        "any": [
            "Hello World",
            "Cluster control registers initialized",
            "Secondary CPU core 3",
        ],
    },
}

BOOT_DOMAINS = {
    "rse": ("RSE / TF-M", "terminal_uart"),
    "safety_island_cl0": (
        "Safety Island CL0 / SCP-firmware",
        "terminal_uart_si_cluster0",
    ),
    "safety_island_cl1": (
        "Safety Island CL1 / Zephyr",
        "terminal_uart_si_cluster1",
    ),
    "tf_a": ("TF-A / BL31", "terminal_sec_uart"),
    "u_boot_linux": ("U-Boot / Linux", "terminal_ns_uart0"),
}

CRITICAL_TERMS = {
    "terminal_uart",
    "terminal_uart_si_cluster0",
    "terminal_ns_uart0",
}

LOGIN_READY_PATTERNS = [
    re.compile(r"[\w.-]+ login:"),
    re.compile(r"Started .*Serial Getty on ttyAMA0"),
    re.compile(r"Reached target .*Login Prompts"),
]

LOGIN_RETRY_READY_PATTERNS = [
    re.compile(r"Linux version "),
    re.compile(r"systemd\[1\]:"),
]
LOGIN_MAX_ATTEMPTS = 80
ROOT_PROMPT_RE = re.compile(r"root@[\w.-]+")


class ConsoleCapture:
    def __init__(self, term: str, port: int, log_path: Path) -> None:
        self.term = term
        self.port = port
        self.log_path = log_path
        self.proc: subprocess.Popen[str] | None = None
        self._file = None

    def start(self) -> None:
        telnet = shutil.which("telnet")
        if not telnet:
            raise RuntimeError("telnet is required to capture FVP consoles")

        cmd = [telnet, "localhost", str(self.port)]
        stdbuf = shutil.which("stdbuf")
        if stdbuf:
            cmd = [stdbuf, "-o0", "-e0", *cmd]

        self.log_path.parent.mkdir(parents=True, exist_ok=True)
        self._file = self.log_path.open(
            "w", encoding="utf-8", errors="replace", buffering=1
        )
        self.proc = subprocess.Popen(
            cmd,
            stdin=subprocess.PIPE,
            stdout=self._file,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
        )

    def sendline(self, line: str) -> None:
        if not self.proc or not self.proc.stdin:
            return
        try:
            self.proc.stdin.write(f"{line}\n")
            self.proc.stdin.flush()
        except BrokenPipeError:
            return

    def stop(self) -> None:
        if self.proc and self.proc.poll() is None:
            self.proc.terminate()
            try:
                self.proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.proc.kill()
                self.proc.wait(timeout=5)
        if self._file:
            self._file.close()


def workspace_root() -> Path:
    return Path(__file__).resolve().parents[1]


def timestamp() -> str:
    return _dt.datetime.now().strftime("%Y%m%d-%H%M%S")


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except FileNotFoundError:
        return ""


def load_fvpconf(path: Path) -> dict:
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def short_terminal_name(full_name: str) -> str:
    return full_name.rsplit(".", 1)[-1]


def terminal_metadata(config: dict) -> tuple[set[str], dict[str, str], dict[str, list[str]]]:
    expected = {short_terminal_name(k) for k in config.get("terminals", {})}
    labels = {
        short_terminal_name(k): v
        for k, v in config.get("terminals", {}).items()
        if v
    }
    roles: dict[str, list[str]] = {}
    for role, term in config.get("consoles", {}).items():
        roles.setdefault(term, []).append(role)
        expected.add(term)
    return expected, labels, roles


def copy_writable_flash(config: dict, out_dir: Path) -> list[str]:
    extra_args: list[str] = []
    image_dir = out_dir / "writable-images"
    for key, value in config.get("parameters", {}).items():
        if not key.endswith(".fnameWrite") or not value:
            continue
        src = Path(value)
        if not src.exists():
            continue
        image_dir.mkdir(parents=True, exist_ok=True)
        dst = image_dir / src.name
        shutil.copy2(src, dst)
        extra_args.extend(["--parameter", f"{key}={dst}"])
    return extra_args


def build_runfvp_command(args: argparse.Namespace, extra_args: list[str]) -> list[str]:
    cmd = [
        str(args.runfvp_bin),
        "-t",
        "none",
    ]
    if args.runfvp_verbose:
        cmd.append("--verbose")
    cmd.append(str(args.fvpconf))
    all_extra = [*extra_args, *args.extra_fvp_args]
    if all_extra:
        cmd.extend(["--", *all_extra])
    return cmd


def enable_terminal_telnet_args(config: dict) -> list[str]:
    args: list[str] = []
    for terminal_path in sorted(config.get("terminals", {})):
        args.extend(["--parameter", f"{terminal_path}.start_telnet=1"])
    return args


def start_fvp(cmd: list[str], boot_log: Path) -> subprocess.Popen[str]:
    boot_log.parent.mkdir(parents=True, exist_ok=True)
    env = os.environ.copy()
    return subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
        start_new_session=True,
        env=env,
    )


def stop_process_group(proc: subprocess.Popen[str]) -> None:
    if proc.poll() is not None:
        return

    # Let runfvp handle KeyboardInterrupt so its finally block stops the FVP
    # child cleanly. SIGTERM on the whole process group can orphan the model.
    proc.send_signal(signal.SIGINT)
    try:
        proc.wait(timeout=20)
        return
    except subprocess.TimeoutExpired:
        pass

    try:
        os.killpg(proc.pid, signal.SIGTERM)
    except ProcessLookupError:
        return
    try:
        proc.wait(timeout=10)
    except subprocess.TimeoutExpired:
        os.killpg(proc.pid, signal.SIGKILL)
        proc.wait(timeout=5)


def check_console(term: str, text: str) -> dict:
    plan = CHECKS.get(term, {})
    all_patterns = plan.get("all", [])
    any_patterns = plan.get("any", [])
    all_results = {pattern: pattern in text for pattern in all_patterns}
    any_results = {pattern: pattern in text for pattern in any_patterns}
    passed = all(all_results.values())
    if any_patterns:
        passed = passed and any(any_results.values())
    return {
        "name": plan.get("name", term),
        "all": all_results,
        "any": any_results,
        "passed": passed if plan else bool(text),
        "error_pattern_found": bool(ERROR_RE.search(text)),
    }


def login_ready(text: str) -> bool:
    return any(pattern.search(text) for pattern in LOGIN_READY_PATTERNS)


def login_retry_ready(text: str) -> bool:
    return login_ready(text) or any(
        pattern.search(text) for pattern in LOGIN_RETRY_READY_PATTERNS
    )


def build_status(
    expected_terms: set[str],
    captures: dict[str, ConsoleCapture],
    roles: dict[str, list[str]],
    require: str,
) -> dict:
    missing_terms = sorted(expected_terms - captures.keys())
    console_status = {}
    for term, capture in sorted(captures.items()):
        text = read_text(capture.log_path)
        status = check_console(term, text)
        status["path"] = str(capture.log_path)
        status["bytes"] = capture.log_path.stat().st_size if capture.log_path.exists() else 0
        status["roles"] = roles.get(term, [])
        console_status[term] = status

    if require == "none":
        required_terms = set()
    elif require == "critical":
        required_terms = CRITICAL_TERMS
    else:
        required_terms = expected_terms

    missing_required_patterns = []
    for term in sorted(required_terms):
        if term not in console_status:
            missing_required_patterns.append(f"{term}: no log")
            continue
        if not console_status[term]["passed"]:
            missing_required_patterns.append(term)

    error_terms = [
        term
        for term, status in console_status.items()
        if status["error_pattern_found"]
    ]
    passed = not missing_terms and not missing_required_patterns and not error_terms
    if require == "none":
        passed = not missing_terms and not error_terms

    return {
        "passed": passed,
        "missing_terms": missing_terms,
        "missing_required_patterns": missing_required_patterns,
        "error_terms": error_terms,
        "consoles": console_status,
    }


def build_domain_status(status: dict) -> dict:
    domains = {}
    consoles = status["consoles"]
    for domain, (name, term) in BOOT_DOMAINS.items():
        console = consoles.get(term)
        domains[domain] = {
            "name": name,
            "term": term,
            "passed": bool(console and console["passed"]),
            "path": console.get("path") if console else None,
            "missing": console is None,
        }
    return domains


def write_summary(
    out_dir: Path,
    command: list[str],
    fvpconf: Path,
    boot_log: Path,
    expected_terms: set[str],
    ports: dict[str, int],
    labels: dict[str, str],
    status: dict,
    duration_s: float,
    post_login: dict,
) -> None:
    passed = status["passed"] and (
        not post_login.get("requested") or post_login.get("done")
    )
    domains = build_domain_status(status)
    result = {
        "passed": passed,
        "duration_s": round(duration_s, 3),
        "command": command,
        "fvpconf": str(fvpconf),
        "boot_log": str(boot_log),
        "expected_terms": sorted(expected_terms),
        "ports": ports,
        "labels": labels,
        "status": status,
        "domains": domains,
        "post_login": post_login,
    }
    (out_dir / "result.json").write_text(
        json.dumps(result, indent=2, sort_keys=True),
        encoding="utf-8",
    )

    lines = [
        f"passed: {passed}",
        f"boot_status_passed: {status['passed']}",
        f"duration_s: {duration_s:.3f}",
        f"fvpconf: {fvpconf}",
        f"boot_log: {boot_log}",
        "boot_domains:",
    ]
    for domain, domain_status in domains.items():
        lines.append(
            f"  - {domain}: passed={domain_status['passed']}"
            f" term={domain_status['term']}"
            f" path={domain_status['path']}"
        )
    lines.extend([
        "console_logs:",
    ])
    for term, console in status["consoles"].items():
        label = labels.get(term, "")
        roles = ",".join(console.get("roles", []))
        detail = f"  - {term}"
        if label:
            detail += f" ({label})"
        if roles:
            detail += f" roles={roles}"
        detail += (
            f" port={ports.get(term, 'unknown')}"
            f" passed={console['passed']}"
            f" bytes={console['bytes']}"
            f" path={console['path']}"
        )
        lines.append(detail)
    if status["missing_terms"]:
        lines.append(f"missing_terms: {', '.join(status['missing_terms'])}")
    if status["missing_required_patterns"]:
        lines.append(
            "missing_required_patterns: "
            + ", ".join(status["missing_required_patterns"])
        )
    if status["error_terms"]:
        lines.append(f"error_terms: {', '.join(status['error_terms'])}")
    if post_login.get("requested"):
        lines.append(f"post_login_requested: {post_login['requested']}")
        lines.append(f"post_login_started: {post_login['started']}")
        lines.append(f"post_login_done: {post_login['done']}")
        lines.append(f"login_sent: {post_login['login_sent']}")
        lines.append(f"login_attempts: {post_login['login_attempts']}")
        if post_login.get("timeout_s") is not None:
            lines.append(f"post_login_timeout_s: {post_login['timeout_s']}")
        if post_login.get("commands"):
            lines.append("post_login_commands:")
            for command_line in post_login["commands"]:
                lines.append(f"  - {command_line}")
    (out_dir / "summary.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")


def parse_args() -> argparse.Namespace:
    root = workspace_root()
    parser = argparse.ArgumentParser(
        description="Run Apollo/RD-Aspen FVP without a UI and save boot logs per console."
    )
    parser.add_argument(
        "--machine",
        default="apollo-fvp",
        help="Machine name used to derive the default deploy .fvpconf path.",
    )
    parser.add_argument(
        "--fvpconf",
        type=Path,
        default=None,
        help=(
            "Explicit runfvp .fvpconf path. Defaults to the selected "
            "machine deploy symlink."
        ),
    )
    parser.add_argument(
        "--runfvp-bin",
        type=Path,
        default=root / "layers/meta-arm/scripts/runfvp",
    )
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=None,
        help="Output directory. Defaults to build/fvp-boot-logs/<machine>-<timestamp>.",
    )
    parser.add_argument("--timeout", type=int, default=900)
    parser.add_argument(
        "--require",
        choices=("critical", "all", "none"),
        default="all",
        help="Pattern strictness before the run is marked passing.",
    )
    parser.add_argument(
        "--no-login",
        action="store_true",
        help="Do not send root to the primary Linux login prompt.",
    )
    parser.add_argument(
        "--no-copy-writable-flash",
        action="store_true",
        help="Let FVP write back to the image paths from the .fvpconf.",
    )
    parser.add_argument(
        "--runfvp-verbose",
        action="store_true",
        help="Pass --verbose to runfvp while still using file-backed logs.",
    )
    parser.add_argument(
        "--post-login-command",
        action="append",
        default=[],
        help="Shell command to send after the root prompt appears. May be repeated.",
    )
    parser.add_argument(
        "--post-login-timeout",
        type=int,
        default=60,
        help="Seconds to wait for post-login command completion marker.",
    )
    parser.add_argument(
        "extra_fvp_args",
        nargs=argparse.REMAINDER,
        help="Extra FVP arguments. Prefix with -- before the first FVP argument.",
    )
    args = parser.parse_args()
    if args.extra_fvp_args and args.extra_fvp_args[0] == "--":
        args.extra_fvp_args = args.extra_fvp_args[1:]
    return args


def main() -> int:
    args = parse_args()
    root = workspace_root()
    if args.fvpconf is None:
        args.fvpconf = (
            root
            / "build/tmp_baremetal/deploy/images"
            / args.machine
            / f"baremetal-image-{args.machine}.fvpconf"
        )
    if args.out_dir is None:
        args.out_dir = root / "build/fvp-boot-logs" / f"{args.machine}-{timestamp()}"
    args.fvpconf = args.fvpconf.resolve()
    args.runfvp_bin = args.runfvp_bin.resolve()
    args.out_dir = args.out_dir.resolve()

    if not args.fvpconf.exists():
        print(f"error: fvpconf not found: {args.fvpconf}", file=sys.stderr)
        return 2
    if not args.runfvp_bin.exists():
        print(f"error: runfvp not found: {args.runfvp_bin}", file=sys.stderr)
        return 2
    if not shutil.which("telnet"):
        print("error: telnet not found", file=sys.stderr)
        return 2
    if args.no_login and args.post_login_command:
        print("error: --post-login-command requires login", file=sys.stderr)
        return 2

    config = load_fvpconf(args.fvpconf)
    expected_terms, labels, roles = terminal_metadata(config)
    args.out_dir.mkdir(parents=True, exist_ok=True)
    boot_log = args.out_dir / "fvp_stdout.log"
    extra_args = enable_terminal_telnet_args(config)
    if not args.no_copy_writable_flash:
        extra_args.extend(copy_writable_flash(config, args.out_dir))
    command = build_runfvp_command(args, extra_args)

    captures: dict[str, ConsoleCapture] = {}
    ports: dict[str, int] = {}
    lock = threading.Lock()

    proc = start_fvp(command, boot_log)
    start_time = time.monotonic()
    login_sent = False
    login_attempts = 0
    last_login_time = 0.0
    post_login_started = False
    post_login_done = not args.post_login_command
    post_login_start_time: float | None = None
    post_login_marker = "__FVP_POST_LOGIN_DONE__"

    def stdout_reader() -> None:
        assert proc.stdout is not None
        with boot_log.open("w", encoding="utf-8", errors="replace", buffering=1) as f:
            for line in proc.stdout:
                f.write(line)
                match = PORT_RE.search(line)
                if not match:
                    continue
                term = match.group("term")
                port = int(match.group("port"))
                with lock:
                    if term in captures:
                        continue
                    ports[term] = port
                    capture = ConsoleCapture(
                        term=term,
                        port=port,
                        log_path=args.out_dir / f"{term}_{port}.log",
                    )
                    capture.start()
                    captures[term] = capture

    reader = threading.Thread(target=stdout_reader, daemon=True)
    reader.start()

    try:
        while time.monotonic() - start_time < args.timeout:
            with lock:
                default_capture = captures.get("terminal_ns_uart0")
            if default_capture and not args.no_login and login_attempts < LOGIN_MAX_ATTEMPTS:
                text = read_text(default_capture.log_path)
                should_retry_login = (
                    login_sent
                    and not ROOT_PROMPT_RE.search(text)
                    and time.monotonic() - last_login_time >= 5.0
                )
                if (not login_sent and login_retry_ready(text)) or should_retry_login:
                    default_capture.sendline("root")
                    login_sent = True
                    login_attempts += 1
                    last_login_time = time.monotonic()

            if (
                default_capture
                and login_sent
                and args.post_login_command
                and not post_login_started
            ):
                text = read_text(default_capture.log_path)
                if ROOT_PROMPT_RE.search(text):
                    for command_line in args.post_login_command:
                        default_capture.sendline(command_line)
                    default_capture.sendline(f"echo {post_login_marker}")
                    post_login_started = True
                    post_login_start_time = time.monotonic()

            if (
                default_capture
                and post_login_started
                and args.post_login_command
                and not post_login_done
            ):
                text = read_text(default_capture.log_path)
                if post_login_marker in text:
                    post_login_done = True
                elif (
                    post_login_start_time is not None
                    and time.monotonic() - post_login_start_time
                    >= args.post_login_timeout
                ):
                    post_login_done = False
                    break

            with lock:
                status = build_status(expected_terms, captures, roles, args.require)
            if status["passed"] and post_login_done:
                break
            if proc.poll() is not None:
                break
            time.sleep(1)
    finally:
        stop_process_group(proc)
        reader.join(timeout=5)
        with lock:
            for capture in captures.values():
                capture.stop()

    duration_s = time.monotonic() - start_time
    with lock:
        status = build_status(expected_terms, captures, roles, args.require)
    if time.monotonic() - start_time >= args.timeout and not status["passed"]:
        status["timeout_s"] = args.timeout
    post_login = {
        "requested": bool(args.post_login_command),
        "commands": args.post_login_command,
        "started": post_login_started,
        "done": post_login_done,
        "marker": post_login_marker if args.post_login_command else None,
        "timeout_s": args.post_login_timeout if args.post_login_command else None,
        "login_sent": login_sent,
        "login_attempts": login_attempts,
    }
    write_summary(
        out_dir=args.out_dir,
        command=command,
        fvpconf=args.fvpconf,
        boot_log=boot_log,
        expected_terms=expected_terms,
        ports=ports,
        labels=labels,
        status=status,
        duration_s=duration_s,
        post_login=post_login,
    )

    passed = status["passed"] and (
        not post_login.get("requested") or post_login.get("done")
    )

    print(args.out_dir)
    print(args.out_dir / "summary.txt")
    print(args.out_dir / "result.json")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
