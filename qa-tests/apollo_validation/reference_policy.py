from __future__ import annotations

from typing import Final, Literal


ComparisonMode = Literal["none", "standalone", "fvp-reference"]
STANDALONE_QBOX_PROFILES: Final = frozenset({"platform-devices"})


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
