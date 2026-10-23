from __future__ import annotations

from pathlib import Path

import pytest

from apollo_validation.aggregate import (
    AggregateError,
    JsonMapping,
    JsonValue,
    SourceResult,
    _validate_references,
)
from apollo_validation.reference_policy import STANDALONE_QBOX_PROFILES


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


@pytest.mark.parametrize("profile_id", sorted(STANDALONE_QBOX_PROFILES))
def test_supported_profile_standalone_needs_no_fvp_receipt(
    tmp_path: Path,
    profile_id: str,
) -> None:
    results = _pair(
        tmp_path,
        profile_id,
        {"comparison_mode": "standalone"},
    )

    _validate_references(results)


@pytest.mark.parametrize(
    "profile_id",
    ("crypto-extension", "hipc", "mbpp", "platform-devices-extra"),
)
def test_unsupported_profile_cannot_claim_standalone(
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


@pytest.mark.parametrize("profile_id", ("platform-devices", "trusted-services"))
def test_optional_reference_is_accepted_when_it_matches(
    tmp_path: Path,
    profile_id: str,
) -> None:
    fvp_path = tmp_path / f"fvp-{profile_id}/summary.json"
    results = _pair(
        tmp_path,
        profile_id,
        {
            "comparison_mode": "fvp-reference",
            "accepted_fvp_reference": {
                "run_id": f"fvp-{profile_id}",
                "path": str(fvp_path),
                "summary_sha256": "a" * 64,
                "semantic_profile_digest": "semantic-digest",
            },
        },
    )

    _validate_references(results)


@pytest.mark.parametrize("comparison_mode", ("standalone", "fvp-reference"))
def test_standalone_policy_does_not_bypass_a_supplied_reference(
    tmp_path: Path,
    comparison_mode: str,
) -> None:
    results = _pair(
        tmp_path,
        "trusted-services",
        {
            "comparison_mode": comparison_mode,
            "accepted_fvp_reference": {
                "run_id": "fvp-trusted-services",
                "path": str(tmp_path / "fvp-trusted-services/summary.json"),
                "summary_sha256": "0" * 64,
                "semantic_profile_digest": "semantic-digest",
            },
        },
    )

    with pytest.raises(
        AggregateError,
        match="blocked_aggregate_fvp_reference_mismatch",
    ):
        _validate_references(results)


@pytest.mark.parametrize(
    "receipt",
    (None, "invalid", [], 1, {}),
    ids=("null", "string", "list", "number", "empty-object"),
)
def test_standalone_rejects_malformed_receipt_instead_of_ignoring_it(
    tmp_path: Path,
    receipt: JsonValue,
) -> None:
    results = _pair(
        tmp_path,
        "trusted-services",
        {"comparison_mode": "standalone", "accepted_fvp_reference": receipt},
    )

    with pytest.raises(
        AggregateError,
        match="blocked_aggregate_fvp_reference_mismatch",
    ):
        _validate_references(results)
