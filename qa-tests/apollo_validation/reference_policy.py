from __future__ import annotations

from typing import Final, Literal


ComparisonMode = Literal["none", "standalone", "fvp-reference"]
STANDALONE_QBOX_PROFILES: Final = frozenset(
    {
        "bsp-core",
        "cpuidle",
        "cpufreq",
        "pfdi",
        "pfdi-si-cl1",
        "platform-devices",
        "ras_cpu",
        "safety-diagnostics-tests",
        "si-cl1",
        "smcf",
    }
)


def profile_requires_fvp_reference(profile_id: str | None) -> bool:
    return profile_id is not None and profile_id not in STANDALONE_QBOX_PROFILES


def comparison_mode(
    profile_id: str | None,
    reference_supplied: bool,
) -> ComparisonMode:
    if profile_id is None:
        return "none"
    if reference_supplied:
        return "fvp-reference"
    return "standalone"
