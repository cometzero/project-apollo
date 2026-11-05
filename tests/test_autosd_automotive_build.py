"""Source policy and binary payload binding without guest installation."""
import importlib.util
import json
from pathlib import Path
from types import SimpleNamespace
import sys

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def builder(monkeypatch):
    monkeypatch.syspath_prepend(str(ROOT / 'scripts/autosd_demo'))
    spec = importlib.util.spec_from_file_location('automotive_build_test', ROOT / 'scripts/autosd_demo/automotive_build.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def inputs(tmp_path, automotive=True):
    rpm = tmp_path / 'rpm'
    (rpm / 'payload').mkdir(parents=True)
    arm64 = b'\x7fELF' + bytes(14) + b'\xb7\x00'
    for name in ('workload', 'latency-probe'):
        (rpm / 'payload' / name).write_bytes(arm64)
    (rpm / 'result.json').write_text(json.dumps({'kernel_release': '6.18.5-apollo-test'}))
    manifest = ROOT / ('autosd/customization/automotive.aib.yml' if automotive else 'autosd/sig-docs/demos/minimal_qm/minimal_qm.aib.yml')
    return SimpleNamespace(aib_manifest=manifest, customize=automotive, crun_binary=None), rpm


@pytest.mark.parametrize('automotive', [True, False])
def test_resolved_manifest_preserves_selected_policy(builder, tmp_path, automotive):
    args, rpm = inputs(tmp_path, automotive)
    output, receipt = builder.resolve_manifest(args, rpm, tmp_path / 'bundle')
    result = yaml.safe_load(output.read_text())
    assert result['kernel']['uname_r'] == receipt['kernel_release']
    assert 'kmod-apollo' not in result['content']['rpms']
    assert 'kernel-apollo' in result['content']['rpms']
    assert ('realtime-tests' in result['content']['rpms']) == automotive
    assert ('apollo-safety-monitor.service' in result['content']['systemd']['enabled_services']) == automotive
    assert bool(result['qm']['content'].get('container_images')) == automotive
    assert any(f['path'] == '/etc/modules-load.d/apollo-fullsystem.conf' for f in result['content']['add_files'])
    files = {f['path']: f.get('text', '') for f in result['content']['add_files']}
    nm = files['/etc/NetworkManager/conf.d/90-apollo-rpmsg-no-auto-default.conf']
    assert 'no-auto-default+=interface-name:ethsi1' in nm
    assert 'unmanaged-devices' not in nm
    assert 'Options=umask=0077' in files['/etc/systemd/system/boot-efi.mount.d/90-apollo-private.conf']
    if automotive:
        assert {'path': '/usr/libexec/apollo/check-automotive.sh', 'mode': '0755'} in result['content']['chmod_files']


def test_conflicting_platform_cmdline_is_not_overwritten(builder, tmp_path):
    args, rpm = inputs(tmp_path, False)
    source = yaml.safe_load(args.aib_manifest.read_text())
    source['kernel'] = {'cmdline': ['console=ttyS0']}
    args.aib_manifest = tmp_path / 'custom.yml'
    args.aib_manifest.write_text(yaml.safe_dump(source))
    with pytest.raises(ValueError, match='Conflicting Apollo kernel argument'):
        builder.resolve_manifest(args, rpm, tmp_path / 'bundle')


@pytest.mark.parametrize('scope', ['root', 'qm'])
def test_source_only_payload_policy_preserved(builder, tmp_path, scope):
    args, rpm = inputs(tmp_path)
    source = yaml.safe_load(args.aib_manifest.read_text())
    content = source['content'] if scope == 'root' else source['qm']['content']
    extra = {
        'add_files': [{'path': '/opt/custom/data', 'text': 'caller data'}],
        'chmod_files': [{'path': '/opt/custom/data', 'mode': '0640'}],
        'make_dirs': [{'path': '/opt/custom', 'mode': 0o755, 'parents': True, 'exist_ok': True}],
        'container_images': [{'source': 'localhost/caller', 'tag': '1', 'name': 'localhost/caller:1', 'containers-transport': 'containers-storage'}],
    }
    content.update(extra)
    args.aib_manifest = tmp_path / 'caller.yml'
    args.aib_manifest.write_text(yaml.safe_dump(source))
    output, _ = builder.resolve_manifest(args, rpm, tmp_path / 'bundle')
    result = yaml.safe_load(output.read_text())
    actual = result['content'] if scope == 'root' else result['qm']['content']
    for kind, entries in extra.items():
        assert entries[0] in actual[kind]


@pytest.mark.parametrize('kind,key', [('add_files', 'path'), ('chmod_files', 'path'),
                                     ('make_dirs', 'path'), ('container_images', 'name')])
def test_payload_collision_is_explicit(builder, kind, key):
    first = {key: '/same', 'value': 1}
    assert builder.merge_entries([first], [first.copy()], kind) == [first]
    with pytest.raises(ValueError, match='Conflicting ' + kind):
        builder.merge_entries([first], [{key: '/same', 'value': 2}], kind)


def test_minimal_enables_password_ssh_without_replacing_hash(builder, tmp_path):
    args, rpm = inputs(tmp_path, False)
    expected = yaml.safe_load(args.aib_manifest.read_text())['auth']['root_password']
    output, _ = builder.resolve_manifest(args, rpm, tmp_path / 'bundle')
    auth = yaml.safe_load(output.read_text())['auth']
    assert auth['root_password'] == expected
    assert auth['sshd_config'] == {'PasswordAuthentication': True, 'PermitRootLogin': True}


def test_minimal_rejects_conflicting_ssh_policy(builder, tmp_path):
    args, rpm = inputs(tmp_path, False)
    source = yaml.safe_load(args.aib_manifest.read_text())
    source['auth']['sshd_config'] = {'PermitRootLogin': False}
    args.aib_manifest = tmp_path / 'caller.yml'
    args.aib_manifest.write_text(yaml.safe_dump(source))
    with pytest.raises(ValueError, match='Minimal readiness requires PermitRootLogin'):
        builder.resolve_manifest(args, rpm, tmp_path / 'bundle')


def test_prepare_inputs_uses_yocto_packaging_without_kernel_compile(builder, tmp_path, monkeypatch):
    calls = []
    monkeypatch.setattr(builder.subprocess, 'run', lambda command, **kwargs: calls.append(command))
    args = SimpleNamespace(rpm_build_dir=tmp_path / 'rpms', deploy_dir=tmp_path / 'deploy',
                           kernel_artifacts=tmp_path / 'artifacts', prepare_inputs_only=True,
                           builder_image='already-prepared')
    assert builder._run(args, tmp_path) == 0
    assert calls == [[str(ROOT / 'scripts/autosd_demo/kernel_rpm_build.sh'),
                      str(args.deploy_dir), str(args.kernel_artifacts), str(args.rpm_build_dir), '--prepare-only']]
    assert not args.rpm_build_dir.exists()
