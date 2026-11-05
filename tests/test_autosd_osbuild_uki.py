import importlib.util
import hashlib
from pathlib import Path
import struct

import pytest

SPEC = importlib.util.spec_from_file_location('apollo_uki_stage', Path(__file__).resolve().parents[1] / 'scripts/autosd_demo/osbuild_apollo_uki.py')
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def stub(tree, machine):
    path = tree / 'usr/lib/systemd/boot/efi/linuxaa64.efi.stub'
    path.parent.mkdir(parents=True)
    data = bytearray(128)
    data[:2] = b'MZ'
    struct.pack_into('<I', data, 60, 64)
    data[64:68] = b'PE\0\0'
    struct.pack_into('<H', data, 68, machine)
    path.write_bytes(data)
    return path


def test_uki_uses_target_architecture_and_files(tmp_path, monkeypatch):
    target_stub = stub(tmp_path, 0xaa64)
    calls = []
    monkeypatch.setattr(MODULE.subprocess, 'run', lambda command, **kwargs: calls.append(command))
    MODULE.build_uki(tmp_path, {'kernel': '6.18.5-test+', 'implementation_sha256': hashlib.sha256(Path(MODULE.__file__).read_bytes()).hexdigest()})
    command = calls[0]
    assert command[command.index('--efi-arch') + 1] == 'aa64'
    assert command[command.index('--stub') + 1] == str(target_stub)
    assert command[command.index('--linux') + 1] == str(tmp_path / 'usr/lib/modules/6.18.5-test+/vmlinuz')
    assert command[command.index('--cmdline') + 1] == '@' + str(tmp_path / 'etc/kernel/cmdline')


def test_wrong_stub_rejected_before_ukify(tmp_path):
    stub(tmp_path, 0x8664)
    with pytest.raises(ValueError, match='must be AArch64'):
        MODULE.build_uki(tmp_path, {'kernel': '6.18.5', 'implementation_sha256': hashlib.sha256(Path(MODULE.__file__).read_bytes()).hexdigest()})


def test_stale_stage_implementation_rejected(tmp_path):
    with pytest.raises(ValueError, match='implementation hash mismatch'):
        MODULE.build_uki(tmp_path, {'kernel': '6.18.5', 'implementation_sha256': '0' * 64})
