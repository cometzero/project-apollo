import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCP_AARCH64 = (
    ROOT / "hsoc-stack/components/system_mgmt/scp-firmware/arch/arm/aarch64"
)


def read(relative: str) -> str:
    return (SCP_AARCH64 / relative).read_text(encoding="utf-8")


def test_disable_returns_the_preexisting_daif_state() -> None:
    header = read("include/arch_interrupt.h")
    read_daif = header.index('mrs %0, DAIF')
    mask_fiq = header.index('msr DAIFSet, %0', read_daif)
    return_state = header.index("return (unsigned int)daif;", mask_fiq)

    assert read_daif < mask_fiq < return_state


def test_nested_enable_does_not_clear_a_preexisting_fiq_mask() -> None:
    header = read("include/arch_interrupt.h")

    assert "arch_interrupts_enable(unsigned int flags)" in header
    assert "if ((flags & DAIF_FIQ_MASK) == 0U)" in header
    assert header.index("if ((flags & DAIF_FIQ_MASK) == 0U)") < header.index(
        'msr DAIFClr, %0'
    )


def test_saved_daif_fiq_mask_uses_the_aarch64_pstate_f_bit() -> None:
    registers = read("include/arch_reg.h")

    assert re.search(r"#define\s+DAIF_FIQ_MASK\s+FWK_BIT\(6\)", registers)
