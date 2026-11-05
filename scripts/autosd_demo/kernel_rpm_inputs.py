"""Bind a binary RPM cache to exact Yocto artifacts and application sources."""
import gzip
import re
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys


def digest(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def validate_cache(out, data):
    hashes = {out/'repo'/key:value for key,value in data['rpm_sha256'].items()}
    hashes.update({out/key:value for key,value in data['artifact_sha256'].items()})
    if not hashes or any(not path.is_file() or digest(path)!=value for path,value in hashes.items()):
        raise ValueError('RPM outputs missing/corrupt; choose a new output directory')


def main():
    root, deploy, artifacts, out = map(Path, sys.argv[1:])
    kernel_version = (artifacts/'kernel-abiversion').read_text().strip()
    inputs = {}
    for name, path in [('Image', deploy/'Image'), ('modules', deploy/'modules-apollo-qvp.tgz'),
                       ('config', artifacts/'.config'), ('System.map', artifacts/f'System.map-{kernel_version}'),
                       ('dtb', deploy/'apollo-qvp-saturn-v-4cpus.dtb')]:
        inputs[name] = {'path':str(path.resolve()), 'sha256':digest(path)}
    canonical = root/'hsoc-stack/components/primary_compute/linux/arch/arm64/configs/apollo_qvp_defconfig'
    image = (deploy/'Image').read_bytes()
    start = image.index(b'IKCFG_ST')+8
    embedded = gzip.decompress(image[start:image.index(b'IKCFG_ED',start)]).decode()
    def config_values(text):
        values = {}
        for line in text.splitlines():
            if line.startswith('CONFIG_'):
                key,value = line.split('=',1); values[key] = value
            elif re.fullmatch(r'# CONFIG_\w+ is not set',line):
                values[line[2:-11]] = 'n'
        return values
    wanted, actual = config_values(canonical.read_text()), config_values(embedded)
    mismatches = {key:(value,actual.get(key,'n')) for key,value in wanted.items() if actual.get(key,'n')!=value}
    if mismatches:
        raise ValueError(f'Yocto Image does not match canonical defconfig: {mismatches}; rebuild virtual/kernel')
    inputs['canonical_defconfig'] = digest(canonical)
    external = {}
    work = artifacts.parents[2]/'work/apollo_qvp-poky-linux'
    for recipe, module in [('arm-si-rproc-mod','arm_si_rproc'),('rpmsg-net-mod','rpmsg_net'),('pfdi-misc-mod','pfdi_misc')]:
        candidates = list((work/recipe).glob(f'*/image/usr/lib/modules/{kernel_version}/updates/{module}.ko'))
        if len(candidates) != 1:
            raise ValueError(f'Expected one installed Yocto module: {recipe}, got {candidates}')
        external[module+'.ko'] = candidates[0]
        inputs[module] = {'path':str(candidates[0].resolve()),'sha256':digest(candidates[0])}
    for name in ('scripts/autosd_demo/kernel_rpm_payload.py','scripts/autosd_demo/arm64_payload_build.sh',
                 'autosd/rpm/apollo.spec.in','autosd/customization/apps/workload.c','autosd/customization/apps/latency-probe.c'):
        inputs[name] = digest(root/name)
    pfdi = root/'autosd/pfdi'
    inputs['pfdi_sources'] = {str(path.relative_to(pfdi)):digest(path) for path in pfdi.rglob('*')
                             if path.is_file() and '.git' not in path.parts}
    for image in ('apollo-native-rpm','apollo-arm64-rpm'):
        inputs[image] = subprocess.check_output(['podman','image','inspect','localhost/'+image,'--format','{{.Id}}'],text=True).strip()
    receipt = out/'inputs.json'
    if receipt.exists() and json.loads(receipt.read_text()) != inputs:
        raise ValueError('RPM inputs changed; choose a new output directory')
    receipt.write_text(json.dumps(inputs,indent=2)+'\n')
    result = out/'result.json'
    if result.exists():
        data = json.loads(result.read_text())
        if data.get('inputs_sha256') != digest(receipt):
            raise ValueError('Receipt inputs mismatch')
        validate_cache(out, data)
        return
    # Failed packaging is inexpensive to repeat; preserve ARM64 application objects.
    for name in ('kernel-stage','rpmbuild','repo'):
        if (out/name).exists():
            shutil.rmtree(out/name)
    (out/'external').mkdir(exist_ok=True)
    for name,path in external.items():
        shutil.copyfile(path,out/'external'/name)


if __name__ == '__main__':
    main()
