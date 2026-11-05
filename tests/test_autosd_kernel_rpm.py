import importlib.util
from pathlib import Path
import pytest

spec = importlib.util.spec_from_file_location('kernel_rpm_payload', Path(__file__).resolve().parents[1] / 'scripts/autosd_demo/kernel_rpm_payload.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def test_module_architecture_and_signature(tmp_path, monkeypatch):
    path = tmp_path / 'driver.ko'
    data = bytearray(20)
    data[:5] = b'\x7fELF\x02'
    data[18:20] = b'\xb7\x00'
    path.write_bytes(data)
    monkeypatch.setattr(module.subprocess, 'check_output', lambda args, **kw: '6.18.5-test SMP' if args[2] == 'vermagic' else 'Apollo key')
    module.verify_module(path, '6.18.5-test')
    with pytest.raises(ValueError, match='vermagic'):
        module.verify_module(path, 'other')
    monkeypatch.setattr(module.subprocess, 'check_output', lambda args, **kw: '6.18.5-test SMP' if args[2] == 'vermagic' else '')
    with pytest.raises(ValueError, match='signer'):
        module.verify_module(path, '6.18.5-test')
    data[18:20] = b'\x3e\x00'
    path.write_bytes(data)
    with pytest.raises(ValueError, match='AArch64'):
        module.verify_module(path, '6.18.5-test')


def test_prepare_only_does_not_compile(tmp_path):
    import os
    import subprocess
    binary = tmp_path/'podman'
    log = tmp_path/'calls'
    binary.write_text('#!/bin/sh\nprintf "%s\\n" "$*" >> "$CALL_LOG"\n')
    binary.chmod(0o755)
    script = Path(__file__).resolve().parents[1]/'scripts/autosd_demo/kernel_rpm_build.sh'
    output = tmp_path/'output'
    subprocess.run([str(script),str(tmp_path),str(tmp_path),str(output),'--prepare-only'],check=True,
                   env={**os.environ,'PATH':str(tmp_path)+':'+os.environ['PATH'],'CALL_LOG':str(log)})
    commands = log.read_text().splitlines()
    assert len(commands) == 2
    assert commands[0].startswith('build --platform linux/amd64 ')
    assert commands[1].startswith('build --platform linux/arm64 ')
    assert not (output/'inputs.json').exists()
    assert not (output/'kernel').exists()


def test_cache_requires_unchanged_rpms_and_payload(tmp_path):
    cache_spec = importlib.util.spec_from_file_location('kernel_rpm_inputs',Path(__file__).resolve().parents[1]/'scripts/autosd_demo/kernel_rpm_inputs.py')
    cache = importlib.util.module_from_spec(cache_spec)
    cache_spec.loader.exec_module(cache)
    (tmp_path/'repo').mkdir()
    rpm = tmp_path/'repo/kernel.rpm'
    rpm.write_bytes(b'signed modules preserved')
    artifact = tmp_path/'board.dtb'
    artifact.write_bytes(b'board')
    data = {'rpm_sha256':{'kernel.rpm':cache.digest(rpm)},'artifact_sha256':{'board.dtb':cache.digest(artifact)}}
    cache.validate_cache(tmp_path,data)
    artifact.write_bytes(b'changed')
    with pytest.raises(ValueError,match='missing/corrupt'):
        cache.validate_cache(tmp_path,data)
    artifact.write_bytes(b'board')
    rpm.unlink()
    with pytest.raises(ValueError,match='missing/corrupt'):
        cache.validate_cache(tmp_path,data)
