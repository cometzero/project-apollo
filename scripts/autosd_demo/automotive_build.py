"""Yocto kernel RPM -> complete AIB disk; QBox only verifies the finished artifact."""
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys
import time
import yaml

from build_minimal_qm import ROOT, sha256


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def merge_entries(original, additions, kind):
    """Preserve caller policy, rejecting incompatible definitions of one object."""
    key = 'name' if kind == 'container_images' else 'path'
    result = []
    indexed = {}
    for entry in original + additions:
        identity = entry[key]
        if identity in indexed:
            if indexed[identity] != entry:
                raise ValueError(f'Conflicting {kind} entry: {identity}')
            continue
        indexed[identity] = entry
        result.append(entry)
    return result


def resolve_manifest(args, rpm, bundle):
    source = yaml.safe_load(args.aib_manifest.read_text())
    if args.customize:
        prepare = load(ROOT / 'autosd/customization/prepare.py', 'automotive_payload')
        generated = prepare.prepare(bundle, None, rt_tools=True, watchdog_tools=True,
                                    binaries=rpm / 'payload', crun_binary=args.crun_binary)
        # Source policy owns packages/auth/services; generated payload owns source file contents.
        for scope in ('content',):
            for key in ('add_files', 'chmod_files', 'make_dirs', 'container_images'):
                source[scope][key] = merge_entries(source[scope].get(key, []), generated[scope].get(key, []), key)
        for key in ('add_files', 'chmod_files', 'make_dirs', 'container_images'):
            source['qm']['content'][key] = merge_entries(source['qm']['content'].get(key, []), generated['qm']['content'].get(key, []), key)
    else:
        bundle.mkdir(parents=True)
    if not args.customize:
        # Upstream minimal_qm supplies the demo password, but no SSH root policy.
        auth = source.setdefault('auth', {})
        if not auth.get('root_password'):
            raise ValueError('Minimal readiness requires an explicit root password hash')
        ssh = auth.setdefault('sshd_config', {})
        for key in ('PasswordAuthentication', 'PermitRootLogin'):
            if key in ssh and ssh[key] is not True:
                raise ValueError(f'Minimal readiness requires {key}=true')
            ssh[key] = True
    receipt = json.loads((rpm / 'result.json').read_text())
    if source.get('target', 'apollo-qvp') != 'apollo-qvp':
        raise ValueError('Selected manifest target conflicts with Apollo')
    kernel = source.get('kernel', {})
    if kernel.get('kernel_package', 'kernel-apollo') != 'kernel-apollo':
        raise ValueError('Selected manifest kernel conflicts with Apollo')
    if kernel.get('uname_r', receipt['kernel_release']) != receipt['kernel_release']:
        raise ValueError('Selected manifest uname_r conflicts with source RPM')
    source['target'] = 'apollo-qvp'
    source['kernel'] = dict(source.get('kernel', {}), kernel_package='kernel-apollo',
                            uname_r=receipt['kernel_release'])
    if receipt.get('kernel_rpm_version'):
        if kernel.get('kernel_version', receipt['kernel_rpm_version']) != receipt['kernel_rpm_version']:
            raise ValueError('Selected manifest kernel version conflicts with source RPM')
        source['kernel']['kernel_version'] = receipt['kernel_rpm_version']
    required = ['console=ttyAMA0', 'earlycon=pl011,0x1a400000',
        'efi=runtime', 'systemd.show_status=yes', 'apollo.fullsystem=1', 'systemd.default_device_timeout_sec=180s']
    cmdline = source['kernel'].setdefault('cmdline', [])
    if {'slub_debug=FPZ', 'rcupdate.rcu_expedited=1', 'rcupdate.rcu_normal_after_boot=0'}.intersection(cmdline):
        raise ValueError('Diagnostic kernel arguments conflict with the normal-RT build profile')
    for word in required:
        key = word.split('=', 1)[0]
        if any(item.split('=', 1)[0] == key and item != word for item in cmdline):
            raise ValueError(f'Conflicting Apollo kernel argument: {key}')
        if word not in cmdline:
            cmdline.append(word)
    content = source.setdefault('content', {})
    repository = {'id': 'apollo-kernel', 'baseurl': 'file:///apollo-kernel-repo', 'priority': 1}
    repos = content.setdefault('repos', [])
    existing = [r for r in repos if r['id'] == 'apollo-kernel']
    if existing and existing != [repository]:
        raise ValueError('Selected manifest Apollo repository conflicts with build input')
    if not existing:
        repos.append(repository)
    content['rpms'] = list(dict.fromkeys(content.get('rpms', []) +
                                        ['kernel-apollo', 'apollo-pfdi', 'openssh-server', 'iproute']))
    content.setdefault('systemd', {}).setdefault('enabled_services', []).extend(['sshd.service', 'apollo-pfdi.service'])
    sys.path.insert(0, str(ROOT / 'scripts/run'))
    from autosd_fullsystem_pfdi import service_files
    from autosd_fullsystem_boot_policy import NM_CONFIG, NM_PATH, EFI_PATH
    original_files = content.get('add_files', [])
    files = []
    for name, text in service_files().items():
        destination = '/etc/systemd/system/' + name if name.endswith('.service') else '/usr/libexec/' + name
        files.append({'path': destination, 'text': text})
    files.extend([{'path': '/' + NM_PATH, 'text': NM_CONFIG},
                  {'path': '/' + EFI_PATH, 'text': '# Apollo image build policy: preserve root-only ESP access.\n[Mount]\nOptions=umask=0077\n'}])
    files.append({'path': '/etc/modules-load.d/apollo-fullsystem.conf', 'text': 'virtio_rpmsg_bus\narm_si_rproc\nrpmsg_net\n'})

    for filename in ('check-guest.sh', 'wait-ready-guest.sh'):
        if args.customize:
            files.append({'path': '/usr/libexec/apollo/' + filename, 'text': (ROOT / 'autosd/customization' / filename).read_text()})
    files = merge_entries(original_files, files, 'add_files')
    content['add_files'] = files
    chmod = []
    for item in files:
        if item['path'].startswith('/usr/libexec/'):
            chmod.append({'path': item['path'], 'mode': '0755'})
    content['chmod_files'] = merge_entries(content.get('chmod_files', []), chmod, 'chmod_files')
    directories = {str(Path(f['path']).parent) for f in files}
    content['make_dirs'] = merge_entries(content.get('make_dirs', []),
        [{'path': d, 'mode': 0o755, 'parents': True, 'exist_ok': True} for d in sorted(directories)], 'make_dirs')
    output = bundle / 'automotive.aib.yml'
    output.write_text(yaml.safe_dump(source, sort_keys=False))
    import jsonschema
    schema = yaml.safe_load((ROOT / 'autosd/automotive-image-builder/files/manifest_schema.yml').read_text())
    jsonschema.Draft7Validator(schema).validate(source)
    return output, receipt


def _run(args, cache):
    from bootstrap import checked_builder
    from builder_podman import build
    rpm = (args.rpm_build_dir or cache / 'rpm-yocto').absolute()
    subprocess.run([str(ROOT / 'scripts/autosd_demo/kernel_rpm_build.sh'),
                    str(args.deploy_dir), str(args.kernel_artifacts), str(rpm)] +
                   (['--prepare-only'] if args.prepare_inputs_only else []), check=True)
    if not args.builder_image:
        args.builder_archive, args.builder_image = checked_builder(cache, args.builder_reference)
    if args.prepare_inputs_only:
        print(json.dumps({'rpm_build_dir': str(rpm), 'builder_image': args.builder_image}))
        return 0
    args.work_dir.mkdir(parents=True, exist_ok=False)
    manifest, receipt = resolve_manifest(args, rpm, args.work_dir / 'bundle')
    from argparse import Namespace
    build(Namespace(manifest=manifest, image=args.builder_image, archive=args.builder_archive,
                    work_dir=args.work_dir / 'fetch', timeout=args.build_timeout,
                    rootless=args.rootless, rpm_repo=rpm / 'repo', cache_dir=args.aib_cache_dir))
    subprocess.run([args.qemu_img, 'check', '-f', 'qcow2',
                    str(args.work_dir / 'fetch/minimal_qm.aarch64.qcow2')], check=True)
    args.output.mkdir(parents=True, exist_ok=False)
    disk = args.output / 'rootfs.img'
    subprocess.run([args.qemu_img, 'convert', '-f', 'qcow2', '-O', 'raw',
                    str(args.work_dir / 'fetch/minimal_qm.aarch64.qcow2'), str(disk)], check=True)
    sys.path.insert(0, str(ROOT / 'scripts/run'))
    from autosd_disk import inspect_disk
    disk_info = inspect_disk(disk)
    if disk_info['bootctl']['state'] not in ('valid', 'uninitialized'):
        raise ValueError('AIB produced invalid UKIBoot control data')
    (args.work_dir / 'disk-inspection.json').write_text(json.dumps(disk_info, indent=2) + '\n')
    from image_architecture import inspect_image_architecture
    architecture = inspect_image_architecture(disk)
    (args.work_dir / 'image-architecture.json').write_text(json.dumps(architecture, indent=2) + '\n')
    dtb = args.output / 'apollo-qvp-saturn-v.dtb'
    shutil.copy2(rpm / receipt['dtb'], dtb)
    profile = 'automotive' if args.customize else 'minimal-qm'
    osbuild = json.loads((args.work_dir / 'fetch/minimal_qm.osbuild.json').read_text())
    cmdlines = [stage['options']['kernel_opts'] for pipeline in osbuild['pipelines']
                for stage in pipeline.get('stages', []) if stage['type'] == 'org.osbuild.kernel-cmdline']
    if len(cmdlines) != 1:
        raise ValueError('Expected one effective OSBuild kernel command line')
    artifact = {'schema_version': 2, 'mode': 'regular', 'rootfs': str(disk.absolute()),
                'platform_requirements': {'machine': 'apollo-qvp', 'variant': 'cfg2', 'ap_cpus': 4, 'pfdi': True},
                'sha256': sha256(disk), 'dtb': str(dtb.absolute()), 'dtb_sha256': sha256(dtb),
                'kernel_release': receipt['kernel_release'], 'profile': profile,
                'build_id': args.work_dir.name, 'boot_profile': 'normal-rt',
                'bootargs': cmdlines[0],
                'uki_stage_sha256': sha256(args.work_dir / 'fetch/apollo-osbuild-lib/stages/org.osbuild.apollo.uki'),
                'osbuild_manifest_sha256': sha256(args.work_dir / 'fetch/minimal_qm.osbuild.json'),
                'kernel_input': 'yocto-deploy',
                'rpm_receipt_sha256': sha256(rpm / 'result.json'),
                'resolved_manifest_sha256': sha256(manifest), 'source_manifest': str(args.aib_manifest),
                'source_manifest_sha256': sha256(args.aib_manifest)}
    path = args.output / 'regular.json'
    path.write_text(json.dumps(artifact, indent=2) + '\n')
    (args.work_dir / 'result.json').write_text(json.dumps({
        'status': 'IMAGE_BUILT', 'runtime_status': 'NOT_RUN', 'manifest': str(path.absolute())}, indent=2) + '\n')
    print(f'IMAGE_BUILT: {path}', flush=True)
    if args.build_only:
        return 0
    out = args.qbox_out_dir or args.build_dir / 'qbox-apollo-qvp' / ('autosd-' + args.work_dir.name)
    out.parent.mkdir(parents=True, exist_ok=True)
    command = [str(ROOT / 'run_qbox_autosd.sh'), '--autosd', str(path), '--headless',
               '--out-dir', str(out), '--ssh-port', str(args.qbox_port), '--timeout', str(args.boot_timeout + 600)]
    with (args.work_dir / 'qbox.log').open('w') as logfile:
        proc = subprocess.Popen(command, stdout=logfile, stderr=subprocess.STDOUT)
        deadline = time.monotonic() + args.boot_timeout
        while time.monotonic() < deadline:
            if proc.poll() is not None:
                raise RuntimeError('QBox exited before readiness; see qbox.log')
            try:
                result = json.loads((out / 'domains.json').read_text())
            except (OSError, ValueError):
                result = {}
            if result.get('status') == 'FAIL':
                raise RuntimeError(f'QBox readiness failed; preserved {out}')
            if result.get('status') == 'PASS':
                break
            time.sleep(3)
        else:
            raise TimeoutError(f'QBox readiness timed out; VM preserved at {out}')
        guest = [sys.executable, str(ROOT / 'scripts/autosd_demo/guest_exec.py'), '--port', str(args.qbox_port),
                 '--timeout', '180', '--out', str(args.work_dir / 'guest-validation'), '--command']
        check = 'uname -r; getenforce; systemctl is-active qm'
        if args.customize:
            check += '; bash /usr/libexec/apollo/wait-ready-guest.sh && bash /usr/libexec/apollo/check-guest.sh'
        subprocess.run(guest + ['set -eu; ' + check], check=True)
        shutdown = guest.copy()
        shutdown[shutdown.index('--out') + 1] = str(args.work_dir / 'shutdown')
        subprocess.run(shutdown + ['systemd-run --on-active=3s /usr/bin/systemctl poweroff'], check=True)
        if proc.wait(timeout=300) != 0:
            raise RuntimeError('QBox shutdown failed')
    result = json.loads((out / 'result.json').read_text())
    if result.get('domains', {}).get('status') != 'PASS' or not result.get('poweroff_observed'):
        raise RuntimeError('QBox all-domain shutdown evidence failed')
    (args.work_dir / 'result.json').write_text(json.dumps({'status': 'PASS', 'artifact': artifact, 'runtime': result}, indent=2))
    return 0


def run(args, cache):
    try:
        return _run(args, cache)
    except (OSError, ValueError, RuntimeError, subprocess.SubprocessError) as error:
        if args.work_dir.is_dir() and not args.prepare_inputs_only:
            (args.work_dir / 'result.json').write_text(json.dumps({
                'status': 'FAIL', 'error': str(error),
                'note': 'Inspect build/runtime logs; any live VM is preserved for diagnosis.'}, indent=2) + '\n')
        raise
