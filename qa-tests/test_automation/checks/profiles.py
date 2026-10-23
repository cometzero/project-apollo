"""Execute existing probe contracts through the upstream manager API."""
from __future__ import annotations

import json
import re
from collections.abc import Callable

import pytest

from scripts.run.qbox_validation.registry import canonical_matrix_path, resolve_profile
from scripts.run.qbox_validation.result import normalize_profile_result
from scripts.run.qbox_validation.types import Console, ConsoleSnapshot, EvaluationError


PORT_NAMES = {Console.PRIMARY: "ap", Console.SI0: "si_cl0", Console.SI1: "si_cl1"}


def console_snapshot(manager) -> ConsoleSnapshot:
    return ConsoleSnapshot(**{
        field: manager.read_log(manager.get_port(port))
        for field, port in (("primary", "ap"), ("secure", "secure"),
                            ("rse", "rse"), ("si0", "si_cl0"), ("si1", "si_cl1"))
    })


def execute_profile(platform, profile_id: str, record_property: Callable | None = None):
    """One ordered profile is one timed pytest case, including its cleanup."""
    if record_property is not None:
        record_property("validation_profile", profile_id)
    spec = resolve_profile(profile_id, canonical_matrix_path())
    manager = platform.mgr
    outputs = []
    initial = console_snapshot(manager)
    try:
        for index, step in enumerate(spec.steps):
            port = manager.get_port(PORT_NAMES[step.console])
            # The manager owns framing and its fresh log cursor. SI0 sampling
            # may finish after CLI exit, so retain the profile's completion rule.
            completion_key = (port, step.command)
            previous_completion = None
            if step.console == Console.SI0:
                previous_completion = manager.command_completion_patterns.get(completion_key)
                manager.command_completion_patterns[completion_key] = step.prompt_pattern
            try:
                rc, output = manager.execute_command_with_prompt_capture(
                    port, step.command, timeout=step.timeout_s,
                )
            finally:
                if step.console == Console.SI0:
                    if previous_completion is None:
                        manager.command_completion_patterns.pop(completion_key, None)
                    else:
                        manager.command_completion_patterns[completion_key] = previous_completion
            # Zephyr negative PFDI cases deliberately produce firmware errors.
            allowed = (0, 1) if step.console == Console.SI1 else (0,)
            assert rc in allowed, f"{profile_id} step {index}: command rc={rc}: {output}"
            if step.console == Console.SI0:
                assert re.search(step.prompt_pattern, output), (
                    f"{profile_id} step {index}: fresh firmware completion missing"
                )
            if step.completion_pattern is not None:
                assert re.search(step.completion_pattern, output), (
                    f"{profile_id} step {index}: command completion record missing"
                )
            outputs.append(output)
        snapshot = console_snapshot(manager)
        if profile_id == "safety-diagnostics-tests":
            # These evaluators otherwise accept the first integration result.
            snapshot = ConsoleSnapshot(si0=snapshot.si0[len(initial.si0):])
        observed = spec.evaluator.evaluate(snapshot, tuple(outputs))
        result = normalize_profile_result(spec, observed)
        if record_property is not None:
            record_property("assertions", json.dumps(result["assertions"], sort_keys=True))
        failed = [item["id"] for item in result["assertions"] if item["status"] != "PASS"]
        assert result["verdict"] == "PASS", f"{profile_id}: failed assertions: {failed}"
        return result
    except EvaluationError as error:
        if error.reason.startswith("unsupported:"):
            pytest.skip(error.reason)
        raise
    finally:
        receipt = spec.cleanup.cleanup()
        assert receipt.passed, f"{profile_id}: cleanup failed: {receipt.detail}"


def require_log_markers(platform, domain: str, markers: tuple[str, ...], timeout=60):
    manager = platform.mgr
    port = manager.get_port(domain)
    for marker in markers:
        assert manager.wait_for_prompt_in_log(port, marker, timeout=timeout), (
            f"{domain}: boot marker missing: {marker}"
        )
    text = manager.read_log(port)
    assert all(marker in text for marker in markers), f"{domain}: boot log incomplete"
    return text


def run_ap_command(platform, command: str, timeout=120):
    rc, output = platform.mgr.execute_command_with_prompt_capture(
        platform.mgr.get_port("ap"), command, timeout=timeout,
    )
    assert rc == 0, f"AP command failed (rc={rc}): {output}"
    return output
