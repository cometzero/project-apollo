from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
INIT = (
    ROOT
    / "hsoc-stack/yocto/meta-hsoc-auto-solutions/recipes-core/initrdscripts/"
    "nexios-bsp-init/init"
)


def test_bsp_console_shell_acquires_controlling_tty() -> None:
    # Given: the BSP initramfs enters a shell on both pass and failure paths.
    init = INIT.read_text(encoding="utf-8")

    # When: the console shell launch contract is inspected.
    shell_launch = "exec setsid -c sh </dev/console >/dev/console 2>&1"

    # Then: every shell launch creates a session and acquires the console.
    assert init.count(shell_launch) == 2
    assert "exec sh </dev/console >/dev/console 2>&1" not in init


def test_bsp_init_does_not_create_configfs_path_in_sysfs() -> None:
    # Given: sysfs owns its directory tree after it is mounted.
    init = INIT.read_text(encoding="utf-8")

    # When: the virtual filesystem initialization contract is inspected.
    invalid_mkdir = "mkdir -p /sys/kernel/debug /sys/kernel/config"

    # Then: init leaves the configfs mountpoint to the kernel filesystem.
    assert invalid_mkdir not in init
    assert "mkdir -p /sys/kernel/debug" in init
