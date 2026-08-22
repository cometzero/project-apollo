from __future__ import annotations

from dataclasses import dataclass
from typing import Final

from .types import AssertionStatus, CleanupReceipt


PRIMARY_PROMPT: Final = r"(?m)(?:nexios-bsp#|root@apollo-qvp[^\n]*[#>])\s*$"
SI1_PROMPT: Final = r"(?m)(?:^|\n)(?:(?:uart:)?~\$\s*)+$"
SCP_BOOT_ANCHOR: Final = "[SI0_PLATFORM] SCP started"


@dataclass(frozen=True, slots=True)
class NoopCleanup:
    def cleanup(self) -> CleanupReceipt:
        return CleanupReceipt(True, "no_resources")


def status(passed: bool) -> AssertionStatus:
    return "PASS" if passed else "FAIL"


def contains_all(text: str, markers: tuple[str, ...]) -> bool:
    return all(marker in text for marker in markers)


def current_scp_segment(text: str) -> str:
    anchor = text.rfind(SCP_BOOT_ANCHOR)
    return text[anchor + len(SCP_BOOT_ANCHOR) :] if anchor >= 0 else ""
