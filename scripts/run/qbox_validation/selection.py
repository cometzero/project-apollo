from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .registry import resolve_profile_selection
from .types import ProfileProbeSpec


@dataclass(frozen=True, slots=True)
class ProfileSelectionRequest:
    profile_id: str | None
    pfdi: bool
    pfdi_si_cl1: bool
    ras_cpu: bool
    safety_diagnostics: bool


@dataclass(frozen=True, slots=True)
class ProfileSelection:
    profile_id: str | None
    spec: ProfileProbeSpec | None
    pfdi: bool
    pfdi_si_cl1: bool
    ras_cpu: bool
    safety_diagnostics: bool


def select_profile(
    request: ProfileSelectionRequest,
    matrix_path: Path,
) -> ProfileSelection:
    active_flags = tuple(
        flag
        for flag, enabled in (
            ("--pfdi-probe", request.pfdi),
            ("--pfdi-si-cl1-probe", request.pfdi_si_cl1),
            ("--ras-cpu-probe", request.ras_cpu),
            ("--safety-diagnostics-probe", request.safety_diagnostics),
        )
        if enabled
    )
    spec = resolve_profile_selection(
        request.profile_id,
        active_flags,
        matrix_path,
    )
    if spec is None:
        return ProfileSelection(
            None,
            None,
            request.pfdi,
            request.pfdi_si_cl1,
            request.ras_cpu,
            request.safety_diagnostics,
        )
    return ProfileSelection(
        spec.profile_id,
        spec,
        request.pfdi or spec.legacy_flag == "--pfdi-probe",
        request.pfdi_si_cl1 or spec.legacy_flag == "--pfdi-si-cl1-probe",
        request.ras_cpu or spec.legacy_flag == "--ras-cpu-probe",
        request.safety_diagnostics
        or spec.legacy_flag == "--safety-diagnostics-probe",
    )
