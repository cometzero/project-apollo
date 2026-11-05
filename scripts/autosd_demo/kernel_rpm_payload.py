#!/usr/bin/env python3
"""Container-side implementation for kernel_rpm_build.sh (not a kernel build)."""

import gzip
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import shutil
import subprocess
import tarfile


RELEASE = None
OUT = Path("/output")


def digest(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def run(args, **kwargs):
    return subprocess.run(args, check=True, text=True, **kwargs)


def audit_payload(rpm, payload):
    """Verify RPM file digests against the unmodified staging payload."""
    file_hashes = run(["rpm", "-qp", "--qf", "[%{FILENAMES} %{FILEDIGESTS}\\n]", str(rpm)],
                      stdout=subprocess.PIPE).stdout
    (OUT / "rpm-file-digests.txt").write_text(file_hashes)
    for line in file_hashes.splitlines():
        fields = line.split()
        if len(fields) == 2 and fields[1] != "(none)":
            if digest(payload / fields[0].lstrip("/")) != fields[1]:
                raise ValueError(f"RPM payload digest mismatch: {fields[0]}")


def verify_module(path, release):
    header = path.read_bytes()[:20]
    if header[:5] != b'\x7fELF\x02' or header[18:20] != b'\xb7\x00':
        raise ValueError(f'Not an AArch64 module: {path}')
    for field in ('vermagic', 'signer'):
        value = subprocess.check_output(['modinfo', '-F', field, str(path)], text=True).strip()
        if not value or (field == 'vermagic' and not value.startswith(release + ' ')):
            raise ValueError(f'Module {field} mismatch: {path}')


def package_files(name, release):
    if name == 'kernel-apollo':
        return '/usr/lib/modules/' + release
    if name == 'apollo-pfdi':
        return '\n'.join(('/usr/bin/pfdi-cli', '/usr/bin/pfdi-sample-app', '/usr/bin/pfdi-tool',
                          '/usr/lib64/libpfdi.so*', '/usr/lib/python3.12/site-packages/pfdi_tool',
                          '/etc/pfdi', '/usr/share/licenses/apollo-pfdi'))
    raise ValueError(f'Unknown package: {name}')


def main():
    global RELEASE
    image = Path('/inputs/deploy/Image').read_bytes()
    releases = set(re.findall(rb'Linux version ([^ ]+) ', image))
    if len(releases) != 1:
        raise ValueError('Cannot uniquely determine deployed kernel release')
    RELEASE = next(iter(releases)).decode('ascii')
    if not re.fullmatch(r'[A-Za-z0-9_.+-]+', RELEASE):
        raise ValueError('Invalid kernel release')
    inputs = {"Image": Path("/inputs/deploy/Image"),
              "modules": Path("/inputs/deploy/modules-apollo-qvp.tgz"),
              "config": Path("/inputs/artifacts/.config"),
              "System.map": Path("/inputs/artifacts") / f"System.map-{RELEASE}"}
    hashes = {name: digest(path) for name, path in inputs.items()}
    image = inputs["Image"].read_bytes()
    releases = set(re.findall(rb"Linux version ([^ ]+) ", image))
    if releases != {RELEASE.encode()} or image[56:60] != b"ARM\x64":
        raise ValueError(f"Unexpected Image architecture/release: {releases}")
    marker = image.find(b"IKCFG_ST")
    end = image.find(b"IKCFG_ED", marker + 8)
    if marker < 0 or end < 0:
        raise ValueError("Image has no embedded config to authenticate build configuration")
    embedded_config = gzip.decompress(image[marker + 8:end])
    exported_config = inputs["config"].read_bytes()
    # Yocto's exported build-artifact config can drop this compiler probe.
    if embedded_config != exported_config and embedded_config.replace(b"CONFIG_CC_CAN_LINK=y\n", b"") != exported_config:
        raise ValueError("Build config does not match deployed Image IKCONFIG")
    payload = OUT / "kernel-stage"
    payload.mkdir()
    modules = payload / "usr/lib/modules" / RELEASE
    modules.mkdir(parents=True)
    prefix = PurePosixPath("lib/modules") / RELEASE
    with tarfile.open(inputs["modules"], "r:gz") as archive:
        members = archive.getmembers()
        epoch = int(max(member.mtime for member in members))
        for member in members:
            path = PurePosixPath(member.name)
            if path.is_absolute() or ".." in path.parts or not (member.isfile() or member.isdir()):
                raise ValueError(f"Unsafe module archive member: {member.name}")
            if member.isdir() and path in (PurePosixPath("lib"), PurePosixPath("lib/modules")):
                continue
            if not path.is_relative_to(prefix):
                raise ValueError(f"Unexpected module release/path: {member.name}")
            destination = modules / path.relative_to(prefix)
            if member.isdir():
                destination.mkdir(parents=True, exist_ok=True)
            else:
                destination.parent.mkdir(parents=True, exist_ok=True)
                with archive.extractfile(member) as source, destination.open("xb") as target:
                    shutil.copyfileobj(source, target)
                destination.chmod(0o644)
    external = sorted((OUT/'external').glob('*.ko'))
    if {p.name for p in external} != {'arm_si_rproc.ko', 'rpmsg_net.ko', 'pfdi_misc.ko'}:
        raise ValueError('Missing mandatory HIPC/PFDI external modules')
    (modules/'updates').mkdir(exist_ok=True)
    for path in external:
        shutil.copyfile(path, modules/'updates'/path.name)
    module_files = sorted(modules.rglob("*.ko"))
    if not module_files:
        raise ValueError("Empty module archive")
    for path in module_files:
        verify_module(path, RELEASE)
    for name in ("modules.builtin", "modules.builtin.modinfo", "modules.order"):
        if not (modules / name).is_file():
            raise ValueError(f"Missing module metadata: {name}")
    for source, target in (("Image", "vmlinuz"), ("System.map", "System.map")):
        shutil.copyfile(inputs[source], modules / target)
    (modules / "config").write_bytes(embedded_config)
    # kmod expects /lib/modules; this symlink is staging-only, not RPM payload.
    (payload / "lib").symlink_to("usr/lib")
    depmod = run(["depmod", "-b", str(payload), "-e", "-F", str(modules / "System.map"), RELEASE],
                 stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    (OUT / "depmod.log").write_text(depmod.stdout + depmod.stderr)
    if "unknown symbol" in depmod.stderr:
        raise ValueError("Module symbols do not match supplied System.map; see depmod.log")
    (payload / "lib").unlink()
    manifest = json.loads((OUT/'inputs.json').read_text())
    identity = digest(OUT/'inputs.json')
    rpm_release = '1.' + identity[:12]
    version = RELEASE.split('-')[0]
    env = {**os.environ, 'SOURCE_DATE_EPOCH': str(epoch)}
    repo = OUT/'repo'
    repo.mkdir(exist_ok=True)
    rpms = {}
    for name, ver, stage, license_id, extra in (
        ('kernel-apollo', version, payload, 'GPL-2.0-only',
         f'AutoReqProv: no\nProvides: kernel-uname-r({RELEASE})\nProvides: kernel-modules-uname-r({RELEASE})'),
        ('apollo-pfdi', '1.0', OUT/'pfdi-stage', 'MIT', 'Requires: python3, python3-pyyaml')):
        spec = OUT/(name+'.spec')
        template = Path('/workspace/autosd/rpm/apollo.spec.in').read_text()
        values = {'NAME':name, 'VERSION':ver, 'RELEASE':rpm_release, 'LICENSE':license_id,
                  'PROVIDES':extra, 'STAGE':str(stage), 'FILES':package_files(name, RELEASE)}
        for key, value in values.items():
            template = template.replace('@'+key+'@',value)
        spec.write_text(template)
        command = ['rpmbuild','-bb','--target','aarch64','--define','_topdir /output/rpmbuild',str(spec)]
        run(command,env=env)
        rpm = OUT/'rpmbuild/RPMS/aarch64'/f'{name}-{ver}-{rpm_release}.aarch64.rpm'
        original = digest(rpm)
        run(command,env=env)
        if original != digest(rpm):
            raise ValueError(f'Non-reproducible RPM: {name}')
        audit_payload(rpm,stage)
        shutil.copyfile(rpm,repo/rpm.name)
        rpms[rpm.name] = original
    run(['createrepo_c','--revision',str(epoch),'--set-timestamp-to-revision',str(repo)])
    shutil.copyfile('/inputs/deploy/apollo-qvp-saturn-v-4cpus.dtb',OUT/'apollo-qvp-saturn-v.dtb')
    if {name:digest(path) for name,path in inputs.items()} != hashes:
        raise ValueError('Yocto inputs changed during packaging')
    receipt = {'status':'PACKAGED_NOT_BOOT_TESTED','kernel_release':RELEASE,
               'kernel_rpm_version':version+'-'+rpm_release,'repo':'repo','payload':'payload',
               'dtb':'apollo-qvp-saturn-v.dtb','rpm_sha256':rpms,'inputs_sha256':identity,
               'artifact_sha256':{name:digest(OUT/name) for name in ('apollo-qvp-saturn-v.dtb','payload/workload','payload/latency-probe')},
               'kernel_origin':'unmodified Yocto deploy Image and signed matching modules',
               'input_sha256':hashes,'module_count':len(module_files),'repeat_build_sha256_match':True,
               'embedded_config_sha256':hashlib.sha256(embedded_config).hexdigest(),
               'source_date_epoch':epoch,'signing_policy':'existing Yocto development module signatures preserved; RPM unsigned'}
    (OUT/'result.json').write_text(json.dumps(receipt,indent=2)+'\n')


if __name__ == '__main__':
    main()
