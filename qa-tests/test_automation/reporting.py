"""Pytest runtime reports grouped by the repository's domain/category paths."""

from __future__ import annotations

from collections import Counter
from datetime import datetime, timezone
from html import escape
import json
import os
from pathlib import Path
import sys
import time
from urllib.parse import quote

import pytest


DOMAINS = ("ap", "rse", "si_cl0", "si_cl1")
TESTS_ROOT = Path(__file__).resolve().parents[1] / "tests"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _counts(cases: list[dict]) -> dict[str, int]:
    statuses = Counter(case["status"] for case in cases)
    return {
        "selected": len(cases),
        "executed": len(cases) - statuses["NOT_RUN"],
        "not_run": statuses["NOT_RUN"],
        "passed": statuses["PASS"],
        "failed": statuses["FAIL"],
        "skipped": statuses["SKIP"],
        "errors": statuses["ERROR"],
        "xfailed": sum(case["expected_outcome"] == "xfail" for case in cases),
        "xpassed": sum(case["expected_outcome"] == "xpass" for case in cases),
    }


def _case_outcome(case: dict) -> None:
    phases = case["phases"]
    case["duration_s"] = sum(phase["duration_s"] for phase in phases.values())
    case["expected_outcome"] = next(
        (phase["expected_outcome"] for phase in phases.values() if phase["expected_outcome"]), None
    )
    outcomes = {phase["status"] for phase in phases.values()}
    if "ERROR" in outcomes:
        case["status"] = "ERROR"
    elif "FAIL" in outcomes:
        case["status"] = "FAIL"
    elif "SKIP" in outcomes:
        case["status"] = "SKIP"
    elif phases.get("call", {}).get("status") == "PASS":
        case["status"] = "PASS"
    else:
        case["status"] = "NOT_RUN"


def _profile_evidence(case: dict) -> None:
    properties = dict(case["user_properties"])
    case["validation_profile"] = properties.get("validation_profile")
    case["assertions"] = []
    case["assertion_error"] = None
    if "assertions" not in properties:
        return
    try:
        value = properties["assertions"]
        assertions = json.loads(value) if isinstance(value, str) else value
        if not isinstance(assertions, list) or any(
            not isinstance(item, dict) or not isinstance(item.get("id"), str)
            or not isinstance(item.get("status"), str) for item in assertions
        ):
            raise ValueError("assertions must be a list of objects with string id/status")
        case["assertions"] = assertions
    except (ValueError, TypeError) as exc:
        case["assertion_error"] = str(exc)


def _assertion_counts(cases: list[dict]) -> dict[str, int]:
    counts = Counter(item["status"] for case in cases for item in case["assertions"])
    return {"total": sum(counts.values()), **dict(sorted(counts.items()))}


def _profile_label(case: dict) -> str:
    profile = case["validation_profile"]
    if case["assertion_error"]:
        return f"{profile or 'unknown profile'}: invalid assertion metadata: {case['assertion_error']}"
    if case["assertions"]:
        counts = ", ".join(f"{key}={value}" for key, value in _assertion_counts([case]).items())
        return f"{profile or 'unassigned profile'}: {counts}"
    return f"{profile}: no assertions recorded" if profile else "—"


def _details(case: dict) -> str:
    chunks = []
    for name, phase in case["phases"].items():
        if phase["longrepr"]:
            chunks.append(f"[{name}]\n{phase['longrepr']}")
        for title, content in phase["captured"]:
            chunks.append(f"[{title}]\n{content}")
    return "\n\n".join(chunks)


def _label(case: dict) -> str:
    expected = case["expected_outcome"]
    return case["status"] + (f" ({expected.upper()})" if expected else "")


def _md(value: object) -> str:
    return escape(str(value)).replace("|", "\\|").replace("\n", " ").replace("`", "\\`")


def _render(result: dict) -> tuple[str, str]:
    counts = result["counts"]
    summary = ", ".join(f"{key}={value}" for key, value in counts.items())
    metadata = [
        f"Run: {result['run_id']}", f"Status: {result['status']}",
        f"Exit status: {result['exit_status']}",
        f"Python: {result['python_version']}; pytest: {result['pytest_version']}",
        f"Invocation directory: {result['invocation_dir']}",
        f"Pytest arguments: {json.dumps(result['pytest_args'])}",
        f"Started (UTC): {result['started_at']}", f"Finished (UTC): {result['finished_at']}",
        f"Wall duration: {result['duration_s']:.6f}s", summary,
        "Recorded profile assertion observations: " + ", ".join(
            f"{key}={value}" for key, value in result["assertion_counts"].items()
        ),
        f"Assertion metadata errors: {result['assertion_metadata_errors']}",
        "Test image scopes: " + ", ".join(
            f"{scope}={count}" for scope, count in result["image_scopes"].items()
        ),
    ]
    md = ["# Apollo runtime pytest report", "", *(_md(line) + "  " for line in metadata), ""]
    html = [
        '<!doctype html><html lang="en"><meta charset="utf-8">',
        "<title>Apollo runtime pytest report</title>",
        "<style>body{font-family:system-ui,sans-serif;max-width:1200px;margin:2rem auto;padding:0 1rem}"
        "table{border-collapse:collapse;width:100%;margin:1rem 0}th,td{border:1px solid #bbb;padding:.4rem;text-align:left}"
        "pre{white-space:pre-wrap;overflow-wrap:anywhere;background:#f3f3f3;padding:1rem}"
        "td:first-child{overflow-wrap:anywhere}summary{cursor:pointer}</style>",
        "<h1>Apollo runtime pytest report</h1><ul>",
        *(f"<li>{escape(line)}</li>" for line in metadata), "</ul>",
    ]
    for domain in DOMAINS:
        cases = [case for case in result["tests"] if case["domain"] == domain]
        domain_summary = ", ".join(f"{key}={value}" for key, value in _counts(cases).items())
        md.extend([f"## {domain}", "", domain_summary, ""])
        html.append(f'<h2 id="{domain}">{domain}</h2><p>{escape(domain_summary)}</p>')
        if not cases:
            md.extend(["No selected tests.", ""])
            html.append("<p>No selected tests.</p>")
        for category in sorted({case["category"] for case in cases}):
            selected = [case for case in cases if case["category"] == category]
            category_summary = ", ".join(f"{key}={value}" for key, value in _counts(selected).items())
            md.extend([
                f"### {_md(category)}", "", category_summary, "",
                "| Test | Image scope | Result | Profile assertions | Setup status / s | Call status / s | Teardown status / s | Total (s) |",
                "| --- | --- | --- | --- | --- | --- | --- | ---: |",
            ])
            html.extend([
                f"<h3>{escape(category)}</h3><p>{escape(category_summary)}</p>",
                "<table><thead><tr><th>Test</th><th>Image scope</th><th>Result</th><th>Profile assertions</th><th>Setup status / s</th>"
                "<th>Call status / s</th><th>Teardown status / s</th><th>Total (s)</th></tr></thead><tbody>",
            ])
            for case in selected:
                values = [case["nodeid"], case["image_scope"], _label(case), _profile_label(case)]
                values.extend(f"{case['phases'][phase]['status']} / {case['phases'][phase]['duration_s']:.6f}"
                              if phase in case["phases"] else "—"
                              for phase in ("setup", "call", "teardown"))
                values.append(f"{case['duration_s']:.6f}")
                md.append("| " + " | ".join(_md(value) for value in values) + " |")
                html.append("<tr>" + "".join(f"<td>{escape(value)}</td>" for value in values) + "</tr>")
            md.append("")
            html.append("</tbody></table>")
            for case in selected:
                details = _details(case)
                if details and (case["status"] != "PASS" or case["expected_outcome"]):
                    md.extend([f"#### {_md(case['nodeid'])}: {_md(_label(case))}", ""])
                    md.extend("    " + line for line in details.splitlines())
                    md.append("")
                    html.append(f"<details><summary>{escape(case['nodeid'])}: {escape(_label(case))}</summary>"
                                f"<pre>{escape(details)}</pre></details>")
    for key, title in (("collection_errors", "Collection / runner errors"), ("collection_skips", "Collection skips")):
        if result[key]:
            md.extend([f"## {title}", ""])
            html.append(f"<h2>{title}</h2>")
            for error in result[key]:
                text = f"{error['nodeid']}\n{error['longrepr']}"
                for title, content in error.get("captured", []):
                    text += f"\n\n[{title}]\n{content}"
                md.extend("    " + line for line in text.splitlines())
                md.append("")
                html.append(f"<pre>{escape(text)}</pre>")
    note = ("Durations are host wall time, including fixture setup/teardown; shared boot cost appears in the first "
            "dependent test. NOT_RUN means no completed test call or setup failure was recorded. "
            "XFAIL is included in SKIP; non-strict XPASS is included in PASS and explicitly flagged. "
            "Simulation results do not establish physical timing or hardware qualification.")
    md.extend(["## Artifacts and interpretation", "", note, ""])
    html.extend(["<h2>Artifacts and interpretation</h2>", f"<p>{escape(note)}</p><ul>"])
    for relative in result["artifacts"]:
        href = quote(relative, safe="/")
        md.append(f"- [{_md(relative)}]({href})")
        html.append(f'<li><a href="{escape(href, quote=True)}">{escape(relative)}</a></li>')
    html.append("</ul></html>")
    return "\n".join(md) + "\n", "\n".join(html) + "\n"


class RuntimeReporter:
    def __init__(self, config: pytest.Config) -> None:
        self.config = config
        self.run_dir = Path(config._apollo_run_dir)
        self.run_dir.mkdir(parents=True, exist_ok=True)
        self.started_at = _now()
        self.started = time.monotonic()
        self.cases: dict[str, dict] = {}
        self.deselected: set[str] = set()
        self.collection_errors: list[dict] = []
        self.collection_skips: list[dict] = []
        self.interrupted = False

    def pytest_deselected(self, items) -> None:
        self.deselected.update(item.nodeid for item in items)

    def pytest_collection_finish(self, session) -> None:
        for item in session.items:
            try:
                parts = item.path.resolve().relative_to(TESTS_ROOT).parts
                if len(parts) < 3 or parts[0] not in DOMAINS:
                    raise ValueError("expected tests/<ap|rse|si_cl0|si_cl1>/<category>/test_*.py")
            except ValueError as exc:
                self.collection_errors.append({"nodeid": item.nodeid, "longrepr": str(exc)})
                raise pytest.UsageError(f"invalid runtime test path: {item.path}: {exc}") from exc
            self.cases[item.nodeid] = {
                "nodeid": item.nodeid, "domain": parts[0], "category": parts[1],
                "image_scope": dict(item.user_properties).get("image_scope", "any"),
                "status": "NOT_RUN", "expected_outcome": None, "duration_s": 0.0, "phases": {},
                "user_properties": list(item.user_properties), "validation_profile": None,
                "assertions": [], "assertion_error": None,
            }
            _profile_evidence(self.cases[item.nodeid])

    def pytest_collectreport(self, report) -> None:
        entry = {"nodeid": report.nodeid, "longrepr": report.longreprtext, "captured": report.sections}
        if report.failed:
            self.collection_errors.append(entry)
        elif report.skipped:
            self.collection_skips.append(entry)

    def pytest_runtest_logreport(self, report) -> None:
        case = self.cases[report.nodeid]
        case["user_properties"] = list(report.user_properties)
        _profile_evidence(case)
        status = "ERROR" if report.failed and report.when != "call" else {
            "passed": "PASS", "failed": "FAIL", "skipped": "SKIP",
        }[report.outcome]
        expected = None
        if hasattr(report, "wasxfail"):
            expected = "xfail" if report.skipped else "xpass"
        elif report.failed and report.longreprtext.startswith("[XPASS(strict)]"):
            expected = "xpass"
        case["phases"][report.when] = {
            "status": status, "duration_s": report.duration, "expected_outcome": expected,
            "longrepr": report.longreprtext,
            "captured": [(title, content) for title, content in report.sections
                         if title.endswith(" " + report.when)],
        }
        _case_outcome(case)

    def pytest_keyboard_interrupt(self, excinfo) -> None:
        # Pytest also calls this hook for its collection-error Interrupted subclass.
        self.interrupted = excinfo.type is KeyboardInterrupt

    def pytest_internalerror(self, excrepr, excinfo) -> None:
        self.collection_errors.append({"nodeid": "<pytest internal error>", "longrepr": str(excrepr)})

    @pytest.hookimpl(tryfirst=True)
    def pytest_sessionfinish(self, session, exitstatus) -> None:
        cases = list(self.cases.values())
        counts = _counts(cases)
        assertion_metadata_errors = sum(case["assertion_error"] is not None for case in cases)
        counts.update(deselected=len(self.deselected), collection_errors=len(self.collection_errors),
                      collection_skipped=len(self.collection_skips))
        if self.interrupted:
            status = "INTERRUPTED"
        elif self.collection_errors or counts["errors"] or assertion_metadata_errors:
            status = "ERROR"
        elif counts["failed"] or int(exitstatus) not in (0, 5):
            status = "FAIL"
        elif not counts["executed"]:
            status = "NO_EXECUTION"
        elif counts["xpassed"]:
            status = "XPASS"
        elif not counts["passed"]:
            status = "NO_PASSING_TESTS"
        else:
            status = "PASS"
        artifacts = ["results.json", "report.md", "report.html"]
        if self.config.option.xmlpath:
            junit_path = Path(os.path.expandvars(self.config.option.xmlpath)).expanduser()
            if not junit_path.is_absolute():
                junit_path = self.config.invocation_params.dir / junit_path
            artifacts.append(os.path.relpath(junit_path, self.run_dir))
        artifacts.extend(name for name in ("platform.json", "invocation.json") if (self.run_dir / name).is_file())
        artifacts.extend(str(path.relative_to(self.run_dir)) for path in sorted((self.run_dir / "target").rglob("*"))
                         if path.is_file())
        result = {
            "schema_version": 1, "run_id": self.run_dir.name, "status": status,
            "python_version": sys.version.split()[0], "pytest_version": pytest.__version__,
            "invocation_dir": str(self.config.invocation_params.dir),
            "pytest_args": list(self.config.invocation_params.args),
            "exit_status": int(exitstatus), "started_at": self.started_at, "finished_at": _now(),
            "duration_s": time.monotonic() - self.started, "collect_only": self.config.option.collectonly,
            "counts": counts, "tests": cases, "deselected": sorted(self.deselected),
            "image_scopes": {scope: sum(case["image_scope"] == scope for case in cases)
                             for scope in ("bsp-only", "product-only", "any")},
            "assertion_counts": _assertion_counts(cases),
            "assertion_metadata_errors": assertion_metadata_errors,
            "collection_errors": self.collection_errors, "collection_skips": self.collection_skips,
            "artifacts": artifacts,
        }
        (self.run_dir / "results.json").write_text(json.dumps(result, indent=2, default=str) + "\n", encoding="utf-8")
        markdown, html = _render(result)
        (self.run_dir / "report.md").write_text(markdown, encoding="utf-8")
        (self.run_dir / "report.html").write_text(html, encoding="utf-8")

    def pytest_terminal_summary(self, terminalreporter, exitstatus, config) -> None:
        terminalreporter.write_sep("=", f"Runtime report: {self.run_dir / 'report.html'}")


def configure(config: pytest.Config) -> RuntimeReporter:
    """Register after the runtime conftest sets ``config._apollo_run_dir``."""
    reporter = RuntimeReporter(config)
    config.pluginmanager.register(reporter, "apollo-runtime-report")
    return reporter
