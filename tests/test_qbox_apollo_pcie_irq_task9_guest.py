from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
GUEST = ROOT / "scripts/test/apollo_qbox_pcie_irq_task9_guest.sh"
LOCAL_LINUX_BUILDER = ROOT / "scripts/build/modules/build_linux.sh"
PROCESS = ROOT / "scripts/test/qbox_apollo_pcie_irq_task9_process.py"


def test_guest_script_uses_bounded_network_flags_not_timeout() -> None:
    guest = GUEST.read_text(encoding="utf-8")
    assert "busybox timeout" not in guest
    assert " timeout " not in guest
    assert 'ping -I "$target" -c 2 -W 2 10.0.2.2' in guest
    assert 'udhcpc -n -q -t 3 -T 1 -i "$target"' in guest


def test_guest_script_mounts_debugfs_before_irq_debugfs_reads() -> None:
    guest = GUEST.read_text(encoding="utf-8")
    assert "ensure_debugfs()" in guest
    assert "mount -t debugfs debugfs /sys/kernel/debug" in guest
    assert "ensure_debugfs && debugfs_ready=1" in guest
    assert "ensure_debugfs || return 45" in guest


def test_guest_script_selects_msix_vector_from_proc_interrupts() -> None:
    guest = GUEST.read_text(encoding="utf-8")
    assert 'done < /proc/interrupts' in guest
    assert '*"ITS-PCI-MSIX-0000:00:01.0"*"$virtio_name-input.0"*)' in guest
    assert '[ -e "$dev/msi_irqs/$candidate" ] || continue' in guest
    assert 'grep -Eq "^device:[[:space:]]+$virtio_name-input' not in guest


def test_guest_script_preserves_raw_chain_names_while_normalizing_protocol() -> None:
    guest = GUEST.read_text(encoding="utf-8")
    assert 'chip="PCI-MSIX"; domain="PCI-MSIX-0000:00:01.0"' in guest
    assert 'chip="ITS-MSI"; domain="ITS-MSI"' in guest
    assert 'raw_domain=%s|raw_chip=%s' in guest


def test_local_linux_debug_config_enables_irq_debugfs() -> None:
    builder = LOCAL_LINUX_BUILDER.read_text(encoding="utf-8")
    debug_block = builder[
        builder.index('if [[ "${KERNEL_DEBUG_INFO}" == "1" ]]')
        : builder.index('if [[ "${LOCAL_LINUX_DM_VERITY:-0}" == "1" ]]')
    ]
    assert "--enable DEBUG_KERNEL" in debug_block
    assert "--enable DEBUG_INFO_DWARF_TOOLCHAIN_DEFAULT" in debug_block
    assert "--enable GENERIC_IRQ_DEBUGFS" in debug_block


def test_host_injection_triggers_on_first_shell_prompt() -> None:
    process = PROCESS.read_text(encoding="utf-8")
    assert 'if "nexios-bsp#" in text:' in process
