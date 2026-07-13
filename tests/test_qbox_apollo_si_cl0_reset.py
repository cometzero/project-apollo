from pathlib import Path
from typing import Final


ROOT: Final = Path(__file__).resolve().parents[1]
SI_CL0_LUA: Final = (
    ROOT / "hsoc-stack/tools/qbox-platform/platforms/apollo/hw-block/si_cl0.lua"
)


def test_si_cl0_uses_managed_start_in_reset_release() -> None:
    # Given: the full-system Safety Island CL0 platform configuration.
    config = SI_CL0_LUA

    # When: its QEMU instance settings are inspected.
    text = config.read_text(encoding="utf-8")

    # Then: reset release uses the race-free QBox CPU path.
    assert "managed_start_in_reset_release = true" in text
