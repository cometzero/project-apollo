#!/usr/bin/env bash

# shellcheck disable=SC2154

if [[ -z "${APOLLO_LOCAL_BUILD_COMMON_SOURCED:-}" ]]; then
    printf 'error: source scripts/build/local_build_common.sh before %s\n' \
        "${BASH_SOURCE[0]}" >&2
    exit 1
fi

create_fvpconf()
{
    local base="${YOCTO_DEPLOY_DIR}/nexios-image-${MACHINE}.fvpconf"
    require_file "${base}"
    local out="${DEPLOY_DIR}/${MACHINE}-local.fvpconf"
    mkdir -p "${DEPLOY_DIR}"

    python3 - "$base" "$out" "$FW_DIR" "$BOOT_DIR" "$(basename "${LOCAL_BUILD_BOOT_DISK}")" <<'PY'
import json
import pathlib
import sys

base, out, fw, boot = [pathlib.Path(p) for p in sys.argv[1:5]]
boot_disk = sys.argv[5]
cfg = json.loads(base.read_text(encoding="utf-8"))
p = cfg.setdefault("parameters", {})
p["css.smb.rseil.rse.rom.raw_image"] = str(fw / "rse-rom-image.img")
p["css.smb.rseil.rse_flashloader.fname"] = str(fw / "rse-flash-image.img")
p["css.smb.rseil.rse_flashloader.fnameWrite"] = str(fw / "rse-flash-image.img")
p["css.smb.rseil.rse.lcm_nvm.raw_image"] = str(fw / "rse-otp-image.img")
p["ros.flash_loader.fname"] = str(fw / "ap-flash-image.img")
p["ros.flash_loader.fnameWrite"] = str(fw / "ap-flash-image.img")
p["ros.virtio_block0.image_path"] = str(boot / boot_disk)
cfg["data"] = [f"css.smb.rseil.rse.sram1={fw / 'combined_provisioning_message.bin'}@0x20000"]
out.write_text(json.dumps(cfg, indent=2, sort_keys=True) + "\n", encoding="utf-8")
PY
}
