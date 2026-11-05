#!/usr/bin/python3
"""Build an ARM64 UKI using the target tree's stub in a native OSBuild root."""
import hashlib
import re
import struct
import subprocess
from pathlib import Path

SCHEMA_2 = """
"options": {
  "additionalProperties": false,
  "required": ["kernel", "implementation_sha256"],
  "properties": {"kernel": {"type": "string"},
                 "implementation_sha256": {"type": "string", "pattern": "^[0-9a-f]{64}$"}}
}
"""


def build_uki(tree, options):
    actual = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    if options.get("implementation_sha256") != actual:
        raise ValueError("Apollo UKI stage implementation hash mismatch")
    tree = Path(tree)
    release = options['kernel']
    if not re.fullmatch(r'[A-Za-z0-9_.+\-]+', release):
        raise ValueError('Invalid kernel release')
    stub = tree / 'usr/lib/systemd/boot/efi/linuxaa64.efi.stub'
    with stub.open('rb') as stream:
        header = stream.read(64)
        if len(header) != 64 or header[:2] != b'MZ':
            raise ValueError('Invalid target EFI stub')
        stream.seek(struct.unpack_from('<I', header, 60)[0])
        if stream.read(6) != b'PE\0\0\x64\xaa':
            raise ValueError('Target EFI stub must be AArch64')
    command = ['ukify', 'build', '--efi-arch', 'aa64', '--stub', str(stub),
               '--linux', str(tree / 'usr/lib/modules' / release / 'vmlinuz'),
               '--initrd', str(tree / 'boot' / f'initramfs-{release}.img'),
               '--uname', release, '--cmdline', '@' + str(tree / 'etc/kernel/cmdline'),
               '--os-release', '@' + str(tree / 'usr/lib/os-release'),
               '--output', str(tree / 'boot' / f'aboot-{release}.img')]
    subprocess.run(command, check=True)


if __name__ == '__main__':
    import osbuild.api
    args = osbuild.api.arguments()
    build_uki(args['tree'], args['options'])
