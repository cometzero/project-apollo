"""Offline staging validates archive boundaries and enables early PFDI."""
import io
from pathlib import Path
import sys
import shlex
import stat
import tarfile

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts/run"))
import autosd_offline_modules as offline


@pytest.fixture
def inputs(tmp_path, monkeypatch):
    module = tmp_path / "test.ko"
    module.write_bytes(b"fixture")
    entry = {"path": str(module), "release": "test", "target": "/usr/lib/modules/test/updates/pfdi_misc.ko", "mode": "0644"}
    monkeypatch.setattr(offline, "module_inputs", lambda _: {"arm_si_rproc": entry})
    monkeypatch.setattr(offline, "pfdi_inputs", lambda _: {"pfdi_misc.ko": entry})
    return tmp_path / "modules.tgz"


def archive(path, extra=None):
    with tarfile.open(path, "w:gz") as target:
        entry = tarfile.TarInfo("lib/modules/test/kernel/test.ko")
        entry.size = 4
        target.addfile(entry, io.BytesIO(b"test"))
        if extra:
            target.addfile(extra)


def test_preboot_payload_and_selinux_relabel(inputs, monkeypatch):
    archive(inputs)
    calls = []
    def run(command, **kwargs):
        calls.append(command)
        if command[0] == "depmod":
            root = Path(command[2])
            assert (root / "lib/modules/test/kernel/test.ko").read_bytes() == b"test"
        elif "--rw" in command:
            lines = kwargs["input"].splitlines()
            tar_index = next(i for i, line in enumerate(lines) if line.startswith("tar-in "))
            assert all(line.startswith("mkdir-p ") for line in lines[:tar_index])
            with tarfile.open(shlex.split(lines[tar_index])[1]) as payload:
                assert "etc/systemd/system/multi-user.target.wants/apollo-pfdi.service" in payload.getnames()
                assert "usr/libexec/apollo-pfdi-check" in payload.getnames()
                assert "lib" not in payload.getnames()
                assert all(member.uid == member.gid == 0 for member in payload)
            assert all(line.startswith("lsetxattr security.selinux ") for line in lines[tar_index + 1:])
        else:
            assert "download" in command
            Path(command[-1]).write_text("/.* system_u:object_r:default_t:s0\n")
    monkeypatch.setattr(offline.subprocess, "run", run)
    def output(command, **kwargs):
        if "is-file" in command:
            assert command[-1] == "followsymlinks:true"
        if "is-file" in command and command[-2].endswith((".local", ".subs", ".subs_dist")):
            return "false\n"
        if command[-1] == "/etc/selinux/config":
            return "SELINUX=enforcing\nSELINUXTYPE=automotive\n"
        return "/dev/sda3: ext4\n" if command[-1] == "list-filesystems" else "ID=autosd\n" if "cat" in command else "true\n"
    monkeypatch.setattr(offline.subprocess, "check_output", output)
    result = offline.prepare("private.wic", inputs, "build")
    assert result["status"] == "INSTALLED"
    assert calls[-1][0] == "guestfish"


@pytest.mark.parametrize("name,link", [("lib/modules/test/../../escape", None),
    ("lib/modules/test/evil", "/etc/passwd"), ("lib/modules/test/evil", "../../../escape")])
def test_unsafe_archive_rejected_before_disk_access(inputs, monkeypatch, name, link):
    entry = tarfile.TarInfo(name)
    if link:
        entry.type, entry.linkname = tarfile.SYMTYPE, link
    archive(inputs, entry)
    monkeypatch.setattr(offline.subprocess, "run", lambda *a, **k: pytest.fail("disk or depmod accessed"))
    with pytest.raises(ValueError, match="archive"):
        offline.prepare("private.wic", inputs, "build")


def test_guest_policy_labels_files_and_symlinks(tmp_path):
    policy = tmp_path / "file_contexts"
    policy.write_text("/usr/libexec/.* -- system_u:object_r:bin_t:s0\n/etc/.* system_u:object_r:etc_t:s0\n")
    assert offline.file_contexts(policy, [("/usr/libexec/apollo-pfdi-check", stat.S_IFREG | 0o755),
        ("/etc/systemd/system/multi-user.target.wants/apollo-pfdi.service", stat.S_IFLNK | 0o777)]) == [
        ("/usr/libexec/apollo-pfdi-check", "system_u:object_r:bin_t:s0"),
        ("/etc/systemd/system/multi-user.target.wants/apollo-pfdi.service", "system_u:object_r:etc_t:s0")]
