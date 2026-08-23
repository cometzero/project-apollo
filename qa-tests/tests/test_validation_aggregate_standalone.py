from __future__ import annotations

from pathlib import Path

import pytest

from apollo_validation.aggregate import (
    AggregateError,
    JsonMapping,
    SourceResult,
    _validate_references,
)


REVISION = "1" * 40


def _source(
    path: Path,
    profile_id: str,
    backend: str,
    extra: JsonMapping | None = None,
) -> SourceResult:
    summary: JsonMapping = {
        "test_profile": profile_id,
        "backend": backend,
        "run_id": f"{backend}-{profile_id}",
        "provenance": {
            "semantic_profile_digest": "semantic-digest",
            "source_revisions": {"workspace": REVISION},
        },
    }
    if extra is not None:
        summary.update(extra)
    return SourceResult(path, "a" * 64, "2026-08-23T00:00:00Z", summary)


def _pair(
    tmp_path: Path,
    profile_id: str,
    qbox_extra: JsonMapping,
) -> dict[tuple[str, str], SourceResult]:
    return {
        (profile_id, "fvp"): _source(
            tmp_path / f"fvp-{profile_id}/summary.json",
            profile_id,
            "fvp",
        ),
        (profile_id, "qbox"): _source(
            tmp_path / f"qbox-{profile_id}/summary.json",
            profile_id,
            "qbox",
            qbox_extra,
        ),
    }


def test_platform_devices_standalone_needs_no_fvp_receipt(
    tmp_path: Path,
) -> None:
    results = _pair(
        tmp_path,
        "platform-devices",
        {"comparison_mode": "standalone"},
    )

    _validate_references(results)


@pytest.mark.parametrize("profile_id", ("pfdi", "platform-devices-extra"))
def test_other_profile_cannot_claim_standalone(
    tmp_path: Path,
    profile_id: str,
) -> None:
    results = _pair(
        tmp_path,
        profile_id,
        {"comparison_mode": "standalone"},
    )

    with pytest.raises(
        AggregateError,
        match="blocked_aggregate_fvp_reference_mismatch",
    ):
        _validate_references(results)


def test_platform_devices_missing_comparison_mode_is_rejected(
    tmp_path: Path,
) -> None:
    results = _pair(tmp_path, "platform-devices", {})

    with pytest.raises(
        AggregateError,
        match="blocked_aggregate_fvp_reference_mismatch",
    ):
        _validate_references(results)


def test_optional_platform_devices_reference_is_still_validated(
    tmp_path: Path,
) -> None:
    fvp_path = tmp_path / "fvp-platform-devices/summary.json"
    results = _pair(
        tmp_path,
        "platform-devices",
        {
            "comparison_mode": "fvp-reference",
            "accepted_fvp_reference": {
                "run_id": "fvp-platform-devices",
                "path": str(fvp_path),
                "summary_sha256": "a" * 64,
                "semantic_profile_digest": "semantic-digest",
            },
        },
    )

    _validate_references(results)
