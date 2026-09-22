#!/usr/bin/env python3
"""Apply official good/bad OTA patches, then add only the Apollo kernel profile."""
import copy
import hashlib
import json
from pathlib import Path
import subprocess
import yaml

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "autosd/sig-docs/demos/system_upgrade_rollback"
OUT = ROOT / "build/autosd/demo-ota-followup/manifests"


def main():
    OUT.mkdir(exist_ok=False)
    original = SOURCE / "system_upgrade_rollback.aib.yml"
    good = OUT / "upstream-good.aib.yml"
    bad = OUT / "upstream-bad.aib.yml"
    subprocess.run(["patch", "--output", str(good), str(original), str(SOURCE / "upgrade-1.patch")], check=True)
    subprocess.run(["patch", "--output", str(bad), str(good), str(SOURCE / "upgrade-2.patch")], check=True)
    apollo = yaml.safe_load((ROOT / "scripts/autosd_demo/apollo_kernel_image.aib.yml").read_text())
    for variant, path in (("base", original), ("good", good), ("bad", bad)):
        manifest = yaml.safe_load(path.read_text())
        manifest["name"] = "apollo-ota-" + variant
        manifest["target"] = "apollo-qvp"
        manifest["kernel"] = copy.deepcopy(apollo["kernel"])
        manifest["content"]["repos"] = copy.deepcopy(apollo["content"]["repos"])
        (OUT / f"{variant}.aib.yml").write_text(yaml.safe_dump(manifest, sort_keys=False))
    (OUT / "source-sha256.json").write_text(json.dumps({str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in (original, SOURCE / "upgrade-1.patch", SOURCE / "upgrade-2.patch")}, indent=2) + "\n")


if __name__ == "__main__":
    main()
