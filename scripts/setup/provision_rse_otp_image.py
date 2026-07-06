#!/usr/bin/env python3
"""Create a QBox-friendly provisioned RSE OTP image from TF-M build outputs."""

from __future__ import annotations

import argparse
import hashlib
import importlib
import logging
import os
import struct
import sys
from pathlib import Path


RSE_OTP_SIZE = 0x10000
SYNTHETIC_KP = bytes([1, 2, 3, 4]) * 8
DEFAULT_GPPC_FLAGS = 0x0008


def parse_int(value: str | None, default: int = 0) -> int:
    if value is None or value == "":
        return default
    return int(value, 0)


def parse_bool(value: str | None) -> bool:
    return str(value or "").upper() in {"1", "ON", "TRUE", "YES", "Y"}


def read_cmake_cache(cache: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    for line in cache.read_text().splitlines():
        if not line or line.startswith(("#", "//")) or "=" not in line:
            continue
        key_type, value = line.split("=", 1)
        key = key_type.split(":", 1)[0]
        values[key] = value
    return values


def require(path: Path, description: str) -> Path:
    if not path.exists():
        raise FileNotFoundError(f"missing {description}: {path}")
    return path


def find_site_packages(root: Path, tfm_build: Path) -> list[Path]:
    candidates = []
    work = root / "build/tmp_baremetal/work"
    for native in work.glob("*-poky-linux/trusted-firmware-m"):
        candidates.extend(
            native.glob("*/recipe-sysroot-native/usr/lib/python*/site-packages")
        )

    components = root / "build/tmp_baremetal/sysroots-components/x86_64"
    candidates.extend(
        components.glob("trusted-firmware-m-scripts-native/usr/lib/python*/site-packages")
    )
    candidates.extend(
        components.glob("python3-pyhsslms-native/usr/lib/python*/site-packages")
    )

    native_from_build = tfm_build / "recipe-sysroot-native/usr/lib"
    candidates.extend(native_from_build.glob("python*/site-packages"))

    return [path for path in candidates if path.exists()]


def setup_tfm_python(root: Path, tfm_build: Path) -> None:
    common_scripts = (
        root
        / "hsoc-stack/components/system_mgmt/trusted-firmware-m/"
        "platform/ext/target/arm/rse/common/scripts"
    )
    paths = [common_scripts] + find_site_packages(root, tfm_build)
    for path in reversed(paths):
        if str(path) not in sys.path:
            sys.path.insert(0, str(path))
    os.environ.setdefault("CRYPTOGRAPHY_OPENSSL_NO_LEGACY", "1")


def cmake_bool(cache: dict[str, str], key: str) -> bool:
    return parse_bool(cache.get(key))


def cache_path(cache: dict[str, str], key: str) -> Path:
    return Path(cache[key])


def mcuboot_rotpk_type(cache: dict[str, str]) -> str:
    value = cache.get("MCUBOOT_SIGNATURE_TYPE", "EC-P256").split("-", 1)[0]
    return value.replace("EC", "ECDSA")


def build_provisioning_args(root: Path, tfm_build: Path, cache: dict[str, str]) -> list[str]:
    otp_config = tfm_build / "platform/target/common/config/otp_config.pickle"
    prov_config = (
        tfm_build
        / "platform/target/common/provisioning/bundle/config/provisioning_config.pickle"
    )
    msg_config = (
        tfm_build
        / "platform/target/common/provisioning/bundle/config/message_config.pickle"
    )
    provisioning_elf = (
        tfm_build
        / "platform/target/common/provisioning/bundle/bin/combined_provisioning_code.axf"
    )

    for path, desc in [
        (otp_config, "OTP config"),
        (prov_config, "provisioning config"),
        (msg_config, "provisioning message config"),
        (provisioning_elf, "combined provisioning code ELF"),
    ]:
        require(path, desc)

    cm_policies = parse_int(cache.get("RSE_OTP_CM_POLICIES_FEATURE_CONTROL_BITS"), 0) << 8
    if cmake_bool(cache, "RSE_NON_ENDORSED_DM_PROVISIONING"):
        cm_policies |= 1 << 4

    rotpk_type = mcuboot_rotpk_type(cache)
    rotpk_hash = cache.get("MCUBOOT_ROTPK_HASH_ALG", "SHA256")
    bl1_rotpk_hash = cache.get("TFM_BL1_2_ROTPK_HASH_ALG", "SHA256")
    sign_alg = cache.get("RSE_PROVISIONING_SIGN_ALG", "ECDSA")
    sign_hash_alg = cache.get("RSE_PROVISIONING_HASH_ALG", "SHA256")
    encrypt_alg = cache.get("RSE_PROVISIONING_ENCRYPTION_ALG", "AES_CTR")
    tp_mode = cache.get("RSE_TP_MODE", "TCI")

    args = [
        "--otp_config",
        str(otp_config),
        "--provisioning_config",
        str(prov_config),
        "--provisioning_message_config",
        str(msg_config),
        "--provisioning_code_elf",
        str(provisioning_elf),
        f"--tp_mode=RSE_PROVISIONING_AUTH_MSG_REQUIRES_TP_MODE_{tp_mode}",
        f"--version={cache.get('RSE_CM_BLOB_VERSION', '0')}",
        f"--signature_config=RSE_PROVISIONING_AUTH_MSG_SIGNATURE_{cache.get('RSE_PROVISIONING_DM_SIGNATURE_CONFIG', 'ROTPK_IN_ROM')}",
        "--valid_lcs=RSE_PROVISIONING_AUTH_MSG_VALID_IN_CM_LCS",
        "--valid_lcs=RSE_PROVISIONING_AUTH_MSG_VALID_IN_DM_LCS",
        "--sign_key",
        str(cache_path(cache, "TFM_BL1_2_CM_SIGNING_KEY_PATH")),
        f"--sign_alg={sign_alg}",
        f"--sign_hash_alg={sign_hash_alg}",
        "--encrypt_key",
        str(tfm_build / "bin/keys/kprov_cm.bin"),
        f"--encrypt_alg={encrypt_alg}",
        "--encrypt_code_and_data=RSE_PROVISIONING_AUTH_MSG_CODE_DATA_DECRYPTION_NONE",
        "--encrypt_secret_values=RSE_PROVISIONING_AUTH_MSG_SECRET_VALUES_DECRYPTION_AES",
        "--sp_mode=RSE_PROVISIONING_AUTH_MSG_REQUIRES_SP_MODE_ENABLED",
        "--non_secret_cm:bl1_2.bl1_2",
        str(tfm_build / "bin/bl1_2_padded.bin"),
        "--non_secret_cm:bl1_2.bl1_2_hash",
        str(tfm_build / "bin/bl1_2_padded_hash.bin"),
        "--secret_cm:guk",
        str(cache_path(cache, "TFM_GUK_PATH")),
        "--non_secret_cm:otp_dma_ics",
        str(tfm_build / "bin/otp_dma_ics.bin"),
        "--secret_cm:kce_cm",
        str(cache_path(cache, "TFM_GUK_PATH")),
        f"--non_secret_cm:cm.cm_policies={cm_policies}",
        "--non_secret_cm:cm.rotpk_areas_0.rotpk_0",
        str(cache_path(cache, "TFM_BL1_2_CM_SIGNING_KEY_PATH")),
        "--non_secret_cm:cm.rotpk_areas_0.rotpk_policy_0=RSE_ROTPK_POLICY_SIG_REQUIRED",
        f"--non_secret_cm:cm.rotpk_areas_0.rotpk_type_0=RSE_ROTPK_TYPE_{cache.get('TFM_BL1_2_CM_SIGNING_ALG', 'LMS')}",
        f"--non_secret_cm:cm.rotpk_areas_0.rotpk_hash_alg_0=RSE_ROTPK_HASH_ALG_{bl1_rotpk_hash}",
        "--non_secret_cm:cm.rotpk_areas_0.rotpk_1",
        str(cache_path(cache, "MCUBOOT_KEY_S")),
        "--non_secret_cm:cm.rotpk_areas_0.rotpk_policy_1=RSE_ROTPK_POLICY_SIG_REQUIRED",
        f"--non_secret_cm:cm.rotpk_areas_0.rotpk_type_1=RSE_ROTPK_TYPE_{rotpk_type}",
        f"--non_secret_cm:cm.rotpk_areas_0.rotpk_hash_alg_1=RSE_ROTPK_HASH_ALG_{rotpk_hash}",
        "--non_secret_dm:dm.rotpk_areas_0.rotpk_1",
        str(cache_path(cache, "MCUBOOT_KEY_NS")),
        "--non_secret_dm:dm.rotpk_areas_0.rotpk_policy_1=RSE_ROTPK_POLICY_SIG_REQUIRED",
        f"--non_secret_dm:dm.rotpk_areas_0.rotpk_type_1=RSE_ROTPK_TYPE_{rotpk_type}",
        f"--non_secret_dm:dm.rotpk_areas_0.rotpk_hash_alg_1=RSE_ROTPK_HASH_ALG_{rotpk_hash}",
        "--secret_dm:kce_dm",
        str(cache_path(cache, "TFM_GUK_PATH")),
    ]

    if parse_int(cache.get("TFM_BL1_2_SIGNER_AMOUNT"), 1) == 2:
        args.extend(
            [
                "--non_secret_dm:dm.rotpk_areas_0.rotpk_0",
                str(cache_path(cache, "TFM_BL1_2_DM_SIGNING_KEY_PATH")),
                "--non_secret_dm:dm.rotpk_areas_0.rotpk_policy_0=RSE_ROTPK_POLICY_SIG_OPTIONAL",
                f"--non_secret_dm:dm.rotpk_areas_0.rotpk_type_0=RSE_ROTPK_TYPE_{cache.get('TFM_BL1_2_DM_SIGNING_ALG', 'LMS')}",
                f"--non_secret_dm:dm.rotpk_areas_0.rotpk_hash_alg_0=RSE_ROTPK_HASH_ALG_{bl1_rotpk_hash}",
            ]
        )

    dm_sig = cache.get("RSE_PROVISIONING_DM_SIGNATURE_CONFIG", "ROTPK_IN_ROM")
    if dm_sig == "ROTPK_NOT_IN_ROM" or cmake_bool(cache, "RSE_NON_ENDORSED_DM_PROVISIONING"):
        idx = parse_int(cache.get("RSE_PROVISIONING_DM_SIGN_KEY_CM_ROTPK_IDX"), 2)
        dm_hash = cache.get("RSE_PROVISIONING_DM_SIGN_KEY_CM_ROTPK_HASH_ALG", sign_hash_alg)
        args.extend(
            [
                f"--non_secret_cm:cm.rotpk_areas_0.rotpk_{idx}",
                str(cache_path(cache, "RSE_CM_PROVISIONING_SIGNING_KEY")),
                f"--non_secret_cm:cm.rotpk_areas_0.rotpk_policy_{idx}=RSE_ROTPK_POLICY_SIG_REQUIRED",
                f"--non_secret_cm:cm.rotpk_areas_0.rotpk_type_{idx}=RSE_ROTPK_TYPE_{sign_alg}",
                f"--non_secret_cm:cm.rotpk_areas_0.rotpk_hash_alg_{idx}=RSE_ROTPK_HASH_ALG_{dm_hash}",
            ]
        )

    return args


def zero_count(data: bytes | bytearray) -> int:
    return sum(8 - byte.bit_count() for byte in data)


def put32(buf: bytearray, offset: int, value: int) -> None:
    buf[offset : offset + 4] = struct.pack("<I", value)


def field_map(csv_path: Path) -> dict[str, tuple[int, int]]:
    fields: dict[str, tuple[int, int]] = {}
    for line in csv_path.read_text().splitlines():
        parts = [part.strip() for part in line.split(",")]
        if len(parts) < 3 or not parts[0]:
            continue
        fields[parts[0]] = (int(parts[1], 16), int(parts[2], 16))
    return fields


def field_offset(fields: dict[str, tuple[int, int]], name: str) -> int:
    return fields[name][0]


def set_header_config_words(otp, image: bytearray, tp_mode: str) -> None:
    hardware = otp.header.lcm_hardware_area
    if tp_mode == "TCI":
        tp_mode_config = 0x0000FFFF
    elif tp_mode == "PCI":
        tp_mode_config = 0xFFFF0000
    else:
        tp_mode_config = 0

    huk = bytes(hardware.huk.to_bytes())
    guk = bytes(hardware.guk.to_bytes())
    kp_cm = bytes(hardware.kp_cm.to_bytes())
    kce_cm = bytes(hardware.kce_cm.to_bytes())
    kp_dm = bytes(hardware.kp_dm.to_bytes())
    kce_dm = bytes(hardware.kce_dm.to_bytes())
    rotpk = bytes(hardware.rotpk.to_bytes())

    cm_config_1 = (
        (zero_count(huk) & 0xFF)
        | ((zero_count(guk) & 0xFF) << 8)
        | ((zero_count(kp_cm) & 0xFF) << 16)
        | ((zero_count(kce_cm) & 0xFF) << 24)
    )
    cm_config_2 = (zero_count(rotpk) & 0xFF) | (DEFAULT_GPPC_FLAGS << 8)
    dm_config = (zero_count(kp_dm) & 0xFF) | ((zero_count(kce_dm) & 0xFF) << 8)

    put32(image, 0xE0, tp_mode_config)
    put32(image, 0xE4, cm_config_1)
    put32(image, 0xE8, cm_config_2)
    put32(image, 0xEC, dm_config)


def set_zero_counts(image: bytearray, fields: dict[str, tuple[int, int]]) -> None:
    for area in ["cm", "bl1_2", "dm", "dynamic", "soc"]:
        start = field_offset(fields, f"header.{area}_area_info.offset")
        zc_off = field_offset(fields, f"header.{area}_area_info_zero_count")
        put32(image, zc_off, zero_count(image[start : start + 4]))

    cm_off = int.from_bytes(image[field_offset(fields, "header.cm_area_info.offset") :][:2], "little")
    cm_size = int.from_bytes(image[field_offset(fields, "header.cm_area_info.size") :][:2], "little")
    bl_off = int.from_bytes(image[field_offset(fields, "header.bl1_2_area_info.offset") :][:2], "little")
    bl_size = int.from_bytes(image[field_offset(fields, "header.bl1_2_area_info.size") :][:2], "little")
    dm_off = int.from_bytes(image[field_offset(fields, "header.dm_area_info.offset") :][:2], "little")
    dm_size = int.from_bytes(image[field_offset(fields, "header.dm_area_info.size") :][:2], "little")

    cm_zc = field_offset(fields, "cm.zero_count")
    cm_rotpk_zc = field_offset(fields, "cm.rotpk_areas_0.zero_count")
    cm_rotpk_next = field_offset(fields, "cm.rotpk_areas_1.zero_count")
    bl_zc = field_offset(fields, "bl1_2.zero_count")
    dm_zc = field_offset(fields, "dm.zero_count")
    dm_rotpk_zc = field_offset(fields, "dm.rotpk_areas_0.zero_count")
    dm_rotpk_next = field_offset(fields, "dm.rotpk_areas_1.zero_count")

    put32(image, cm_zc, zero_count(image[cm_zc + 4 : cm_rotpk_zc]))
    put32(image, cm_rotpk_zc, zero_count(image[cm_rotpk_zc + 4 : cm_rotpk_next]))
    put32(image, bl_zc, zero_count(image[bl_zc + 4 : bl_off + bl_size]))
    put32(image, dm_zc, zero_count(image[dm_zc + 4 : dm_rotpk_zc]))
    put32(image, dm_rotpk_zc, zero_count(image[dm_rotpk_zc + 4 : dm_rotpk_next]))

    if cm_off + cm_size <= cm_rotpk_zc or dm_off + dm_size <= dm_rotpk_zc:
        raise ValueError("invalid OTP area offsets generated from TF-M config")


def create_otp(root: Path, tfm_build: Path, output: Path, size: int) -> str:
    setup_tfm_python(root, tfm_build)
    logging.getLogger("TF-M").setLevel(logging.ERROR)

    import __main__

    otp_module = importlib.import_module("rse.otp_config")
    prov_module = importlib.import_module("rse.provisioning_config")
    msg_module = importlib.import_module("rse.provisioning_message_config")
    cpb = importlib.import_module("rse_scripts.create_combined_provisioning_bundle")

    OTP_config = otp_module.OTP_config
    Provisioning_config = prov_module.Provisioning_config
    Provisioning_message_config = msg_module.Provisioning_message_config

    setattr(__main__, "OTP_config", OTP_config)
    setattr(__main__, "Provisioning_config", Provisioning_config)
    setattr(__main__, "Provisioning_message_config", Provisioning_message_config)

    cache = read_cmake_cache(require(tfm_build / "CMakeCache.txt", "TF-M CMake cache"))
    argv = ["provision_rse_otp_image.py"] + build_provisioning_args(root, tfm_build, cache)
    sys.argv = argv
    parser = argparse.ArgumentParser(allow_abbrev=False)
    cpb.add_arguments(parser, required=False)
    args = parser.parse_args(argv[1:])
    kwargs = cpb.parse_args(args)

    otp = kwargs["otp_config"]
    otp.set_cm_offsets_automatically()
    otp.set_dm_offsets_automatically()

    prov = kwargs["provisioning_config"]
    prov.set_area_infos_from_otp_config(**kwargs)

    for dst, src in [
        (otp.header.dma_ics, prov.non_secret_cm_layout.otp_dma_ics),
        (otp.header.lcm_hardware_area.guk, prov.secret_cm_layout.guk),
        (otp.header.lcm_hardware_area.kce_cm, prov.secret_cm_layout.kce_cm),
        (otp.header.lcm_hardware_area.kce_dm, prov.secret_dm_layout.kce_dm),
        (otp.bl1_2, prov.non_secret_cm_layout.bl1_2),
        (otp.cm, prov.non_secret_cm_layout.cm),
        (otp.dm, prov.non_secret_dm_layout.dm),
    ]:
        dst.set_value_from_bytes(src.to_bytes())

    otp.header.lcm_hardware_area.kp_cm.set_value_from_bytes(SYNTHETIC_KP)
    otp.header.lcm_hardware_area.kp_dm.set_value_from_bytes(SYNTHETIC_KP)

    seed = prov.non_secret_cm_layout.to_bytes() + prov.non_secret_dm_layout.to_bytes()
    otp.header.lcm_hardware_area.huk.set_value_from_bytes(hashlib.sha256(seed).digest())

    image = bytearray(otp.to_bytes())
    if len(image) > size:
        raise ValueError(f"generated OTP image is {len(image)} bytes, size limit is {size}")
    image.extend(bytes(size - len(image)))

    set_header_config_words(otp, image, cache.get("RSE_TP_MODE", "TCI"))
    set_zero_counts(
        image,
        field_map(tfm_build / "platform/target/common/config/otp_layout.csv"),
    )

    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_bytes(image)
    return hashlib.sha256(image).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument(
        "--tfm-build-dir",
        type=Path,
        default=Path("build/local-apollo-fvp/work/trusted-firmware-m"),
    )
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--size", type=lambda value: int(value, 0), default=RSE_OTP_SIZE)
    args = parser.parse_args()

    root = args.root.resolve()
    tfm_build = args.tfm_build_dir
    if not tfm_build.is_absolute():
        tfm_build = root / tfm_build

    digest = create_otp(root, tfm_build.resolve(), args.output.resolve(), args.size)
    print(f"Generated provisioned RSE OTP image: {args.output} sha256={digest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
