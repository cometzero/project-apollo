"""Private guest policy does not change user connections or unrelated mounts."""
import importlib.util
from pathlib import Path
import subprocess

import pytest

SOURCE = Path(__file__).resolve().parents[1] / "scripts/run/autosd_fullsystem_boot_policy.py"
spec = importlib.util.spec_from_file_location("boot_policy", SOURCE)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def test_fstab_preserves_unrelated_text_and_is_idempotent():
    before = "# boot\nUUID=root / ext4 defaults 0 1\nUUID=esp\t/boot/efi vfat defaults,umask=0022 0 2 # esp\n"
    after, count = module.restrict_efi_mount(before)
    assert after == before.replace("umask=0022", "umask=0077")
    assert count == 1
    assert module.restrict_efi_mount(after) == (after, 1)


def test_stricter_masks_and_owner_permissions_preserved():
    after, _ = module.restrict_efi_mount("LABEL=ESP /boot/efi vfat ro,fmask=0177,dmask=0077 0 2\n")
    assert "ro,fmask=0177,dmask=0077,umask=0077" in after


@pytest.mark.parametrize("text", [
    "x /boot/efi ext4 defaults 0 2\n",
    "x /boot/efi vfat umask=xyz 0 2\n",
    "x /boot/efi vfat defaults 0 2\nx /boot/efi vfat defaults 0 2\n",
])
def test_ambiguous_policy_rejected(text):
    with pytest.raises(ValueError):
        module.restrict_efi_mount(text)


def test_private_files_idempotent_and_user_connections_preserved(tmp_path):
    etc = tmp_path / "etc"
    etc.mkdir()
    fstab = etc / "fstab"
    fstab.write_text("x /boot/efi vfat defaults 0 2\n")
    fstab.chmod(0o640)
    profiles = etc / "NetworkManager/system-connections"
    profiles.mkdir(parents=True)
    profile = profiles / "custom.nmconnection"
    profile.write_text("user profile contents")
    assert len(module.apply_policy(tmp_path)["changed"]) == 2
    assert module.apply_policy(tmp_path)["changed"] == []
    assert fstab.stat().st_mode & 0o777 == 0o640
    assert profile.read_text() == "user profile contents"
    assert "no-auto-default+=" in (tmp_path / module.NM_PATH).read_text()


def test_conflicting_named_config_is_preserved_before_any_changes(tmp_path):
    nm = tmp_path / module.NM_PATH
    nm.parent.mkdir(parents=True)
    nm.write_text("user supplied policy")
    fstab = tmp_path / "etc/fstab"
    original = "x /boot/efi vfat defaults 0 2\n"
    fstab.write_text(original)
    with pytest.raises(ValueError):
        module.apply_policy(tmp_path)
    assert fstab.read_text() == original
    assert nm.read_text() == "user supplied policy"


def test_command_only_installs_no_disconnect_delete_or_remount():
    command = "; ".join(module.install_commands("/var/tmp/private dir"))
    subprocess.run(["sh", "-n"], input=command, text=True, check=True)
    for forbidden in ("nmcli", "reboot", "mount -o", "rm "):
        assert forbidden not in command
    assert "restorecon /etc/fstab" in command
    assert module.service_files()["apollo-boot-policy.py"] == SOURCE.read_text()


def test_generated_mount_gets_dropin_without_creating_fstab(tmp_path):
    mount = {"Where": "/boot/efi", "Type": "vfat", "Options": "rw,relatime,fmask=0022,dmask=0022"}
    result = module.apply_policy(tmp_path, mount)
    assert result["efi_mount"] == "restricted-next-boot"
    assert not (tmp_path / "etc/fstab").exists()
    assert "Options=rw,relatime,fmask=0077,dmask=0077,umask=0077" in (tmp_path / module.EFI_PATH).read_text()
    assert module.apply_policy(tmp_path, mount)["changed"] == []


def test_unexpected_generated_mount_rejected(tmp_path):
    with pytest.raises(ValueError):
        module.apply_policy(tmp_path, {"Where": "/", "Type": "ext4"})


def trace_vendor(tmp_path):
    rule = tmp_path / "usr/lib/udev/rules.d" / module.TRACE_RULE
    rule.parent.mkdir(parents=True)
    rule.write_text("# Vendor comment retained\n" + module.TRACE_VENDOR_RULE + "\n")
    service = tmp_path / "usr/lib/systemd/system/trace-cmd.service"
    service.parent.mkdir(parents=True)
    service.write_text("[Service]\nType=oneshot\nRemainAfterExit=yes\nExecStart=/usr/bin/trace-cmd start $OPTS\n")
    return rule, service


def test_trace_guard_short_circuits_inactive_but_keeps_all_active_conditions(tmp_path):
    vendor, _ = trace_vendor(tmp_path)
    files, status = module.trace_policy_files(tmp_path)
    assert status.startswith("guarded-next-boot")
    rule = files["etc/udev/rules.d/98-trace-cmd.rules"]
    guard = 'TEST=="/run/apollo-trace-cmd-flightrecorder", '
    assert rule.replace(guard, "") == vendor.read_text()
    assert rule.index(guard) < rule.index("PROGRAM=")
    unit = files[module.TRACE_UNIT_PATH]
    assert "RuntimeDirectory=apollo-trace-cmd-flightrecorder\n" in unit
    assert "RuntimeDirectoryPreserve=" not in unit
    assert "ExecStart=" not in unit and "ExecStop=" not in unit
    assert "RuntimeDirectoryMode=0755" in unit


def test_trace_policy_install_idempotent_and_does_not_modify_vendor(tmp_path):
    vendor, _ = trace_vendor(tmp_path)
    original = vendor.read_text()
    first = module.apply_policy(tmp_path)
    assert first["trace_coldplug"].startswith("guarded")
    assert len(first["changed"]) == 3
    assert module.apply_policy(tmp_path)["changed"] == []
    assert vendor.read_text() == original


@pytest.mark.parametrize("target", ["etc/udev/rules.d/98-trace-cmd.rules", module.TRACE_UNIT_PATH,
                                    "etc/systemd/system/trace-cmd.service.d/custom.conf",
                                    "etc/systemd/system/trace-cmd.service"])
def test_trace_preserves_conflicting_user_configuration(tmp_path, target):
    trace_vendor(tmp_path)
    path = tmp_path / target
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("user contents\n")
    files, status = module.trace_policy_files(tmp_path)
    assert files == {} and status.startswith("SKIP-user")
    assert path.read_text() == "user contents\n"


def test_trace_mask_symlink_preserved(tmp_path):
    trace_vendor(tmp_path)
    path = tmp_path / "etc/udev/rules.d/98-trace-cmd.rules"
    path.parent.mkdir(parents=True)
    path.symlink_to("/dev/null")
    assert module.trace_policy_files(tmp_path)[0] == {}
    assert path.is_symlink()


def test_trace_missing_or_changed_vendor_is_nonfatal_skip(tmp_path):
    assert module.apply_policy(tmp_path)["trace_coldplug"].startswith("SKIP-vendor")
    vendor, service = trace_vendor(tmp_path)
    vendor.write_text(module.TRACE_VENDOR_RULE + "\nRUN+=\"custom\"\n")
    assert module.trace_policy_files(tmp_path)[1] == "SKIP-unrecognized-vendor-rule"
    vendor.write_text(module.TRACE_VENDOR_RULE + "\n")
    service.write_text("[Service]\nType=simple\n")
    assert module.trace_policy_files(tmp_path)[1] == "SKIP-unrecognized-service-lifecycle"
