from __future__ import annotations

from collections.abc import Callable
from copy import deepcopy
from datetime import UTC, datetime, timedelta
import hashlib
import json
from pathlib import Path
import subprocess
from typing import TypeAlias

import pytest

from apollo_validation.validation_matrix import load_validation_matrix


JsonScalar: TypeAlias = str | int | bool | None
JsonValue: TypeAlias = JsonScalar | list["JsonValue"] | dict[str, "JsonValue"]
ROOT = Path(__file__).resolve().parents[2]
MATRIX = ROOT / "qa-tests/validation/arm-zena-css-v2.2-non-xen.yaml"
NOW = datetime(2026, 8, 22, 1, 0, tzinfo=UTC)
REVISION = "1" * 40


def _digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _write_json(path: Path, value: JsonValue) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _summary(
    run_dir: Path,
    profile_id: str,
    backend: str,
    image_profile: str,
    cpu_count: int,
    coverage_kind: str,
    selectors: tuple[str, ...],
    assertions: tuple[str, ...],
) -> dict[str, JsonValue]:
    image = "nexios-bsp-initramfs" if image_profile == "bsp" else "nexios-image"
    machine = "apollo-fvp" if backend == "fvp" else "apollo-qvp"
    revisions = {
        "workspace": REVISION,
        "qa_runner": REVISION,
        "bsp_layer": REVISION,
        "platform_layer": REVISION,
    }
    if backend == "qbox":
        revisions.update(
            qbox_core="2" * 40,
            qbox_platform="2" * 40,
            qemu="2" * 40,
        )
    return {
        "schema_version": 1,
        "run_id": run_dir.name,
        "run_dir": str(run_dir),
        "status": "PASS",
        "exit_code": 0,
        "backend": backend,
        "machine": machine,
        "image": image,
        "image_profile": image_profile,
        "test_profile": profile_id,
        "counts": {
            "passed": len(assertions),
            "failed": 0,
            "blocked": 0,
            "skipped": 0,
            "total": len(assertions),
        },
        "profile_result": {
            "version": 1,
            "profile_id": profile_id,
            "backend": backend,
            "verdict": "PASS",
            "expected": list(assertions),
            "assertions": [
                {"id": item, "status": "PASS", "coverage_kind": coverage_kind}
                for item in assertions
            ],
        },
        "input_revisions": revisions,
        "provenance": {
            "version": 1,
            "profile_id": profile_id,
            "semantic_profile_digest": hashlib.sha256(
                f"{profile_id}:{backend}".encode()
            ).hexdigest(),
            "selectors": list(selectors),
            "expected_assertion_ids": list(assertions),
            "coverage_kind": coverage_kind,
            "machine": machine,
            "image": image,
            "image_profile": image_profile,
            "cpu_count": cpu_count,
            "source_revisions": revisions,
        },
    }


def make_complete_run_set(base: Path) -> tuple[Path, dict[str, JsonValue]]:
    matrix = load_validation_matrix(MATRIX)
    entries: list[JsonValue] = []
    fvp_sources: dict[str, tuple[Path, dict[str, JsonValue]]] = {}
    for profile in matrix.profiles:
        run_dir = base / f"fvp-{profile.profile_id}"
        summary = _summary(
            run_dir,
            profile.profile_id,
            "fvp",
            profile.image,
            profile.cpu_count,
            profile.coverage_kind,
            profile.fvp_selectors,
            profile.qbox_assertions,
        )
        path = run_dir / "summary.json"
        _write_json(path, summary)
        fvp_sources[profile.profile_id] = (path, summary)
        entries.append(
            {
                "path": str(path),
                "sha256": _digest(path),
                "captured_at": NOW.isoformat().replace("+00:00", "Z"),
            }
        )
    for profile in matrix.profiles:
        run_dir = base / f"qbox-{profile.profile_id}"
        summary = _summary(
            run_dir,
            profile.profile_id,
            "qbox",
            profile.image,
            profile.cpu_count,
            profile.coverage_kind,
            profile.fvp_selectors,
            profile.qbox_assertions,
        )
        fvp_path, fvp_summary = fvp_sources[profile.profile_id]
        summary["accepted_fvp_reference"] = {
            "run_id": fvp_summary["run_id"],
            "path": str(fvp_path),
            "summary_sha256": _digest(fvp_path),
            "semantic_profile_digest": fvp_summary["provenance"][
                "semantic_profile_digest"
            ],
        }
        path = run_dir / "summary.json"
        _write_json(path, summary)
        entries.append(
            {
                "path": str(path),
                "sha256": _digest(path),
                "captured_at": NOW.isoformat().replace("+00:00", "Z"),
            }
        )
    run_set: dict[str, JsonValue] = {
        "version": 1,
        "matrix_sha256": _digest(MATRIX),
        "not_before": (NOW - timedelta(minutes=1)).isoformat().replace("+00:00", "Z"),
        "results": entries,
    }
    path = base / "run-set.json"
    _write_json(path, run_set)
    return path, run_set


def _run(run_set: Path, out_dir: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            str(ROOT / "run_test.sh"),
            "aggregate",
            "--matrix",
            str(MATRIX),
            "--run-set",
            str(run_set),
            "--out-dir",
            str(out_dir),
        ],
        cwd=ROOT,
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )


def test_complete_non_xen_fixture_aggregates_public_cli(tmp_path: Path) -> None:
    # Given: an explicit fresh 14-FVP plus 14-QBox run set.
    run_set, _ = make_complete_run_set(tmp_path / "fixture")

    # When: the root public aggregate command consumes it.
    result = _run(run_set, tmp_path / "out")

    # Then: all fixed coverage counts and reports are observable.
    assert result.returncode == 0, result.stderr
    summary = json.loads((tmp_path / "out/summary.json").read_text())
    assert summary["status"] == "PASS"
    assert summary["counts"] == {
        "areas": 15,
        "runs": 28,
        "actions": 100,
        "required_actions": 99,
        "excluded_actions": 1,
    }
    coverage = json.loads((tmp_path / "out/coverage.json").read_text())
    assert coverage["excluded_actions"] == [
        {
            "id": "primary-ping",
            "profile_id": "platform-devices",
            "reason": (
                "Host ICMP is unavailable with FVP user networking; SSH through "
                "127.0.0.1:2222 is required instead."
            ),
            "status": "EXCLUDED",
        }
    ]
    assert (tmp_path / "out/coverage.json").is_file()
    assert (tmp_path / "out/summary.txt").is_file()
    assert (tmp_path / "out/junit.xml").is_file()


Mutation = Callable[[dict[str, JsonValue], Path], None]


def _mutate_result(
    run_set: dict[str, JsonValue],
    base: Path,
    predicate: Callable[[dict[str, JsonValue]], bool],
    mutate: Callable[[dict[str, JsonValue]], None],
) -> None:
    for raw_entry in run_set["results"]:
        entry = raw_entry
        path = Path(entry["path"])
        summary = json.loads(path.read_text())
        if predicate(summary):
            mutate(summary)
            _write_json(path, summary)
            entry["sha256"] = _digest(path)
            return
    raise AssertionError(f"fixture result not found: {base}")


def _missing(run_set: dict[str, JsonValue], _: Path) -> None:
    run_set["results"].pop()


def _duplicate(run_set: dict[str, JsonValue], _: Path) -> None:
    run_set["results"].append(deepcopy(run_set["results"][0]))


def _stale(run_set: dict[str, JsonValue], _: Path) -> None:
    run_set["results"][0]["captured_at"] = "2020-01-01T00:00:00Z"


def _profile(run_set: dict[str, JsonValue], base: Path) -> None:
    _mutate_result(run_set, base, lambda item: item["backend"] == "fvp", lambda item: item.update(test_profile="wrong"))


def _image(run_set: dict[str, JsonValue], base: Path) -> None:
    _mutate_result(run_set, base, lambda item: item["backend"] == "fvp", lambda item: item.update(image="wrong"))


def _cpu(run_set: dict[str, JsonValue], base: Path) -> None:
    _mutate_result(run_set, base, lambda item: item["test_profile"] != "mbpp", lambda item: item["provenance"].update(cpu_count=16))


def _selector(run_set: dict[str, JsonValue], base: Path) -> None:
    _mutate_result(run_set, base, lambda item: item["backend"] == "fvp", lambda item: item["provenance"].update(selectors=["wrong-selector"]))


def _assertion(run_set: dict[str, JsonValue], base: Path) -> None:
    _mutate_result(run_set, base, lambda item: item["backend"] == "fvp", lambda item: item["profile_result"].update(expected=["wrong-assertion"]))


def _revision(run_set: dict[str, JsonValue], base: Path) -> None:
    _mutate_result(run_set, base, lambda item: item["backend"] == "fvp", lambda item: item["input_revisions"].update(workspace="3" * 40))


def _reference(run_set: dict[str, JsonValue], base: Path) -> None:
    _mutate_result(run_set, base, lambda item: item["backend"] == "qbox", lambda item: item["accepted_fvp_reference"].update(summary_sha256="0" * 64))


def _semantic(run_set: dict[str, JsonValue], base: Path) -> None:
    _mutate_result(run_set, base, lambda item: item["test_profile"] == "crypto-extension", lambda item: item["profile_result"]["assertions"][0].update(coverage_kind="identical"))


def _mbpp(run_set: dict[str, JsonValue], base: Path) -> None:
    _mutate_result(run_set, base, lambda item: item["test_profile"] == "mbpp", lambda item: item["provenance"].update(cpu_count=4))


def _skip(run_set: dict[str, JsonValue], base: Path) -> None:
    _mutate_result(run_set, base, lambda item: item["backend"] == "fvp", lambda item: item["profile_result"]["assertions"][0].update(status="SKIPPED"))


def _zero(run_set: dict[str, JsonValue], base: Path) -> None:
    _mutate_result(run_set, base, lambda item: item["backend"] == "fvp", lambda item: item["counts"].update(total=0))


def _xen(run_set: dict[str, JsonValue], base: Path) -> None:
    _mutate_result(run_set, base, lambda item: item["backend"] == "fvp", lambda item: item["provenance"].update(selectors=["test_40_virtualization"]))


@pytest.mark.parametrize(
    ("mutation", "reason"),
    (
        (_missing, "blocked_aggregate_missing_result"),
        (_duplicate, "blocked_aggregate_duplicate_result"),
        (_stale, "blocked_aggregate_stale_result"),
        (_profile, "blocked_aggregate_profile_mismatch"),
        (_image, "blocked_aggregate_image_mismatch"),
        (_cpu, "blocked_aggregate_cpu_mismatch"),
        (_selector, "blocked_aggregate_selector_mismatch"),
        (_assertion, "blocked_aggregate_assertion_mismatch"),
        (_revision, "blocked_aggregate_revision_mismatch"),
        (_reference, "blocked_aggregate_fvp_reference_mismatch"),
        (_semantic, "blocked_aggregate_semantic_label_mismatch"),
        (_mbpp, "blocked_aggregate_mbpp_topology"),
        (_skip, "blocked_aggregate_skipped_result"),
        (_zero, "blocked_aggregate_zero_assertions"),
        (_xen, "blocked_aggregate_xen_leakage"),
    ),
)
def test_invalid_aggregate_fixture_has_stable_reason(
    tmp_path: Path,
    mutation: Mutation,
    reason: str,
) -> None:
    # Given: one exact mutation to an otherwise complete run set.
    run_set_path, run_set = make_complete_run_set(tmp_path / "fixture")
    mutation(run_set, tmp_path)
    _write_json(run_set_path, run_set)

    # When: the public aggregate command validates the run set.
    result = _run(run_set_path, tmp_path / "out")

    # Then: it fails closed with the mutation's stable reason.
    assert result.returncode != 0
    assert result.stderr.strip() == f"error: {reason}"
