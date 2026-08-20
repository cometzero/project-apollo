from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path

import pytest

from scripts.run.qbox_validation import registry
from scripts.run.qbox_validation.registry import (
    ProfileRegistryError,
    enabled_profile_ids,
    resolve_profile,
)
from scripts.run.qbox_validation.types import (
    AssertionObservation,
    CleanupReceipt,
    Console,
    ConsoleSnapshot,
    CoverageKind,
    ProbeStep,
    ProfileProbeSpec,
    ProfileRegistration,
)


ROOT = Path(__file__).resolve().parents[1]
MATRIX = ROOT / "qa-tests/validation/arm-zena-css-v2.2-non-xen.yaml"


@dataclass(frozen=True, slots=True)
class NoopEvaluator:
    def evaluate(
        self,
        snapshot: ConsoleSnapshot,
        outputs: tuple[str, ...],
    ) -> tuple[AssertionObservation, ...]:
        return (AssertionObservation("one", "PASS"),)


@dataclass(frozen=True, slots=True)
class NoopCleanup:
    def cleanup(self) -> CleanupReceipt:
        return CleanupReceipt(True, "clean")


def test_registry_enables_only_existing_profile_implementations() -> None:
    # Given: the canonical Task 1 validation matrix.
    # When: the repository-owned registry is loaded.
    profile_ids = enabled_profile_ids(MATRIX)

    # Then: only the four pre-existing runtime probes are enabled.
    assert profile_ids == (
        "pfdi",
        "pfdi-si-cl1",
        "ras_cpu",
        "safety-diagnostics-tests",
    )


@pytest.mark.parametrize(
    ("profile_id", "flag", "consoles"),
    (
        ("pfdi", "--pfdi-probe", frozenset({Console.PRIMARY})),
        ("pfdi-si-cl1", "--pfdi-si-cl1-probe", frozenset({Console.SI1})),
        ("ras_cpu", "--ras-cpu-probe", frozenset({Console.PRIMARY})),
        (
            "safety-diagnostics-tests",
            "--safety-diagnostics-probe",
            frozenset({Console.SI0}),
        ),
    ),
)
def test_compatibility_adapters_are_registry_metadata(
    profile_id: str,
    flag: str,
    consoles: frozenset[Console],
) -> None:
    # Given: an implemented legacy QBox profile.
    # When: its canonical spec is resolved.
    spec = resolve_profile(profile_id, MATRIX)

    # Then: routing no longer needs per-profile launcher branches.
    assert spec.legacy_flag == flag
    assert spec.required_consoles == consoles
    assert spec.expected_assertion_ids


@pytest.mark.parametrize(
    ("profile_id", "reason"),
    (
        ("unknown", "unknown_validation_profile:unknown"),
        ("bsp-core", "validation_profile_unavailable:bsp-core"),
    ),
)
def test_unknown_or_unimplemented_profile_rejects_preflight(
    profile_id: str,
    reason: str,
) -> None:
    # Given: an unknown matrix ID or a future profile without an evaluator.
    # When: registry resolution occurs before process launch.
    with pytest.raises(ProfileRegistryError, match=f"^{reason}$"):
        resolve_profile(profile_id, MATRIX)


def test_unbound_console_and_malformed_spec_reject_preflight() -> None:
    # Given: a spec whose ordered step is not in its required console set.
    malformed = ProfileProbeSpec(
        profile_id="pfdi",
        required_consoles=frozenset({Console.PRIMARY}),
        steps=(ProbeStep(Console.SI1, "run", r"READY> $", 1.0),),
        expected_assertion_ids=("one",),
        coverage_kind="identical",
        evaluator=NoopEvaluator(),
        cleanup=NoopCleanup(),
        legacy_flag="--pfdi-probe",
    )

    # When/Then: the registry's structural validator rejects the bad binding.
    with pytest.raises(
        ProfileRegistryError,
        match="^profile_step_console_unbound:pfdi:si1$",
    ):
        malformed.validate()


@pytest.mark.parametrize(
    ("command", "prompt", "timeout", "reason"),
    (
        ("", r"READY> $", 1.0, "profile_step_command_empty"),
        ("run\x00next", r"READY> $", 1.0, "profile_step_command_nul"),
        ("run", "", 1.0, "profile_step_prompt_empty"),
        ("run", r"READY> $", 0.0, "profile_step_timeout_invalid"),
    ),
)
def test_malformed_step_input_is_rejected(
    command: str,
    prompt: str,
    timeout: float,
    reason: str,
) -> None:
    # Given: malformed repository-owned step metadata.
    spec = ProfileProbeSpec(
        profile_id="pfdi",
        required_consoles=frozenset({Console.PRIMARY}),
        steps=(ProbeStep(Console.PRIMARY, command, prompt, timeout),),
        expected_assertion_ids=("one",),
        coverage_kind="identical",
        evaluator=NoopEvaluator(),
        cleanup=NoopCleanup(),
        legacy_flag="--pfdi-probe",
    )

    # When/Then: invalid commands cannot reach a shell writer.
    with pytest.raises(ProfileRegistryError, match=f"^{reason}:pfdi:0$"):
        spec.validate()


def test_one_registration_enables_a_new_repository_profile(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    # Given: one additional repository factory and its Task 1-style contract.
    new_profile_id = "registered-test-profile"

    def factory(
        profile_id: str,
        expected: tuple[str, ...],
        coverage_kind: CoverageKind,
    ) -> ProfileProbeSpec:
        return ProfileProbeSpec(
            profile_id,
            frozenset({Console.PRIMARY}),
            (ProbeStep(Console.PRIMARY, "run", r"READY> $", 1.0),),
            expected,
            "identical",
            NoopEvaluator(),
            NoopCleanup(),
            None,
        )

    registration = ProfileRegistration(new_profile_id, factory)
    monkeypatch.setattr(
        registry,
        "PROFILE_REGISTRATIONS",
        (*registry.PROFILE_REGISTRATIONS, registration),
    )
    matrix = tmp_path / "matrix.json"
    matrix.write_text(
        json.dumps(
            {
                "profiles": [
                    {
                        "id": new_profile_id,
                        "coverage_kind": "identical",
                        "qbox_assertions": ["one"],
                    }
                ]
            }
        ),
        encoding="utf-8",
    )

    # When: the normal registry resolver consumes the added registration.
    spec = resolve_profile(new_profile_id, matrix)

    # Then: no allowlist or per-profile resolver branch is needed.
    assert spec.profile_id == new_profile_id
    assert spec.expected_assertion_ids == ("one",)
