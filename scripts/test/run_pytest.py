#!/usr/bin/env python3
"""Run the Apollo-owned host pytest suites and retain a per-run report."""

from __future__ import annotations

from collections import Counter
from datetime import datetime, timezone
import os
from pathlib import Path
import shlex
import signal
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET


ROOT = Path(__file__).resolve().parents[2]


def now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def write_report(
    run_dir: Path, command: list[str], started: str, finished: str, exit_code: int
) -> None:
    counts: Counter[str] = Counter()
    suites: Counter[str] = Counter()
    findings: list[str] = []
    parse_error = ""
    try:
        tree = ET.parse(run_dir / "junit.xml")
        if tree.getroot().tag not in {"testsuites", "testsuite"}:
            raise ValueError("unexpected JUnit root element")
        for case in tree.iter("testcase"):
            suite = case.get("classname", "<collection>")
            name = f"{suite}::{case.get('name', '<unnamed>')}"
            suites[suite] += 1
            outcome = "passed"
            for tag in ("error", "failure", "skipped"):
                detail = case.find(tag)
                if detail is not None:
                    outcome = {"error": "errors", "failure": "failed", "skipped": "skipped"}[tag]
                    message = detail.get("message", "")
                    detail_lines = (detail.text or "").strip().splitlines()
                    if detail_lines and detail_lines[-1] not in message:
                        message = f"{message}: {detail_lines[-1]}".lstrip(": ")
                    message = " ".join(message.split()) or "No detail in JUnit"
                    findings.append(f"- {outcome.upper()}: `{name}` — {message}")
                    break
            counts[outcome] += 1
    except (OSError, ET.ParseError, ValueError) as exc:
        parse_error = str(exc)

    if exit_code == 130:
        status = "INTERRUPTED"
    elif exit_code != 0:
        status = "FAIL"
    elif parse_error or counts["failed"] or counts["errors"]:
        status = "ERROR"
    elif counts["passed"]:
        status = "PASS"
    else:
        status = "NO PASSING TESTS"

    lines = [
        "# Apollo host pytest report", "", f"**Status: {status}**", "",
        f"- Started (UTC): {started}", f"- Finished (UTC): {finished}",
        f"- Working directory: `{ROOT}`", f"- Exit code: `{exit_code}`",
        f"- Python version: `{sys.version.split()[0]}`",
        f"- `APOLLO_RUN_BITBAKE_MATRIX_TESTS`: `{os.environ.get('APOLLO_RUN_BITBAKE_MATRIX_TESTS', '<unset>')}`",
        "- Default scope: `qa-tests/unittests`, `tests`, `scripts/gem5`.",
        "- Explicit pytest selectors/options below may narrow or override that scope.",
        "", "```sh", shlex.join(command), "```", "",
        "| JUnit case results | Count |", "| --- | ---: |",
        f"| Total | {sum(counts.values())} |",
    ]
    lines.extend(f"| {label.title()} | {counts[label]} |" for label in ("passed", "failed", "errors", "skipped"))
    if parse_error:
        lines.extend(["", f"JUnit could not be read: {parse_error}"])
    lines.extend([
        "", "Counts describe JUnit case results; collection/setup/teardown errors may appear as separate results.",
        "", "## Failures, errors and skips", "",
        *(findings or ["None recorded in JUnit. Consult the exit code and console log for collection or runner errors."]),
        "", "## Test suites recorded in JUnit", "",
        *(f"- `{suite}`: {count}" for suite, count in sorted(suites.items())),
        "", "## Artifacts and evidence limits", "",
        "- [Combined stdout/stderr](console.log)", "- [JUnit XML](junit.xml)",
        "- This run checks host-side Python tools, parsers, contracts and fixtures.",
        "- External nested-repository tests are excluded from the default scope.",
        "- A passing host suite does not establish QBox/FVP boot, guest UART/SSH behavior, hardware timing or qualification.",
        "- Run `python3 -m pytest -c qa-tests/pyproject.toml qa-tests/tests --image=bsp` (and `--image=product`) separately for runtime evidence.",
        "",
    ])
    (run_dir / "report.md").write_text("\n".join(lines), encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    output_root = ROOT / "build/qbox-apollo-qvp"
    output_root.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    run_dir = Path(tempfile.mkdtemp(prefix=f"pytest-{stamp}-", dir=output_root))
    command = [
        sys.executable, "-m", "pytest", "-c", str(ROOT / "pytest.ini"),
        *(sys.argv[1:] if argv is None else argv),
        f"--junitxml={run_dir / 'junit.xml'}",
    ]
    started = now()
    print(f"Pytest artifacts: {run_dir}", flush=True)
    previous_sigint_handler = None
    with (run_dir / "console.log").open("w", encoding="utf-8") as log:
        process = subprocess.Popen(
            command, cwd=ROOT, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
            text=True, encoding="utf-8", errors="replace", bufsize=1,
            start_new_session=True,
        )
        assert process.stdout is not None
        try:
            for line in process.stdout:
                log.write(line)
                log.flush()
                print(line, end="", flush=True)
            exit_code = process.wait()
        except KeyboardInterrupt:
            # Finish cleanup and report writing even if Ctrl+C is pressed again.
            previous_sigint_handler = signal.signal(signal.SIGINT, signal.SIG_IGN)
            exit_code = 130
            for stop_signal in (signal.SIGINT, signal.SIGKILL):
                try:
                    os.killpg(process.pid, stop_signal)
                except ProcessLookupError:
                    pass
                try:
                    tail, _ = process.communicate(timeout=5)
                    break
                except subprocess.TimeoutExpired as exc:
                    if stop_signal == signal.SIGKILL:
                        # A detached descendant can retain stdout after pytest dies.
                        process.stdout.close()
                        process.wait(timeout=5)
                        tail = (exc.output or b"").decode("utf-8", errors="replace")
            try:
                os.killpg(process.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
            log.write(tail)
            log.write("\nPytest run interrupted; process group stopped (exit 130).\n")
            print(tail, end="", flush=True)
    try:
        write_report(run_dir, command, started, now(), exit_code)
        print(f"Pytest report: {run_dir / 'report.md'}", flush=True)
    finally:
        if previous_sigint_handler is not None:
            signal.signal(signal.SIGINT, previous_sigint_handler)
    return exit_code if exit_code >= 0 else 128 - exit_code


if __name__ == "__main__":
    raise SystemExit(main())
