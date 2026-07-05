from __future__ import annotations

from pathlib import Path
import subprocess
from typing import Final


ROOT: Final = Path(__file__).resolve().parents[1]
BUILD: Final = ROOT / "scripts" / "build"
MODULES: Final = BUILD / "modules"

EXPECTED_MODULES: Final[tuple[str, ...]] = (
    "build_qbox.sh",
    "build_sdk.sh",
    "build_tfm.sh",
    "build_scp.sh",
    "build_zephyr.sh",
    "build_uboot.sh",
    "build_optee.sh",
    "build_tfa.sh",
    "build_linux.sh",
    "build_buildroot.sh",
    "build_flash_images.sh",
    "build_boot_disk.sh",
    "build_fvpconf.sh",
    "build_debug_manifest.sh",
    "build_orchestrator.sh",
)


def run(*argv: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        argv,
        cwd=ROOT,
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )


def test_component_modules_exist_and_are_source_only() -> None:
    for name in EXPECTED_MODULES:
        path = MODULES / name
        assert path.is_file(), f"missing module: {path}"
        text = path.read_text(encoding="utf-8")
        assert "APOLLO_LOCAL_BUILD_COMMON_SOURCED" in text
        direct = run("bash", str(path))
        assert direct.returncode != 0
        assert "source scripts/build/local_build_common.sh" in direct.stderr


def test_stage_wrappers_keep_help_contract() -> None:
    scripts = [
        ROOT / "local_build.sh",
        BUILD / "build_all.sh",
        BUILD / "build_images.sh",
        BUILD / "build_qbox.sh",
        BUILD / "build_sdk.sh",
        BUILD / "build_zephyr.sh",
        BUILD / "build_clean.sh",
        ROOT / "scripts" / "package.sh",
    ]
    for script in scripts:
        result = run(str(script), "--help")
        assert result.returncode == 0, f"{script}: {result.stderr}"
        assert "Usage:" in result.stdout


def test_shell_syntax_for_local_build_scripts() -> None:
    scripts = [
        ROOT / "local_build.sh",
        ROOT / "scripts" / "package.sh",
        *sorted(BUILD.glob("*.sh")),
        *sorted(MODULES.glob("*.sh")),
    ]
    for script in scripts:
        result = run("bash", "-n", str(script))
        assert result.returncode == 0, f"{script}: {result.stderr}"


def test_tfa_rebuild_observes_stale_platform_reset_and_dts_arg(
    tmp_path: Path,
) -> None:
    fake_bin = tmp_path / "bin"
    fake_bin.mkdir()
    make_args_log = tmp_path / "make-args.txt"
    fake_make = fake_bin / "make"
    fake_make.write_text(
        "\n".join(
            (
                "#!/usr/bin/env bash",
                "set -euo pipefail",
                "printf '%s\\n' \"$@\" > \"${MAKE_ARGS_LOG}\"",
                'build_base=""',
                'linux_dts=""',
                'for arg in "$@"; do',
                '    case "${arg}" in',
                '        BUILD_BASE=*) build_base="${arg#BUILD_BASE=}" ;;',
                '        LINUX_DTS=*) linux_dts="${arg#LINUX_DTS=}" ;;',
                "    esac",
                "done",
                '[[ -n "${build_base}" ]] || { printf '
                "'missing BUILD_BASE\\n' >&2; exit 41; }",
                '[[ "${linux_dts}" == "7" ]] || { printf '
                "'bad LINUX_DTS=%s\\n' \"${linux_dts}\" >&2; exit 42; }",
                '[[ ! -e "${build_base}/apollo_fvp/stale-output" ]] ||',
                "    { printf 'stale platform output survived\\n' >&2; exit 43; }",
                'mkdir -p "${build_base}/apollo_fvp/debug"',
                "printf 'new-bl2\\n' > "
                '"${build_base}/apollo_fvp/debug/bl2.bin"',
                "printf 'new-fip\\n' > "
                '"${build_base}/apollo_fvp/debug/fip.bin"',
                "",
            )
        ),
        encoding="utf-8",
    )
    fake_make.chmod(0o755)

    local_build_dir = tmp_path / "local-build"
    yocto_tmp = tmp_path / "yocto-tmp"
    tfa_src = tmp_path / "trusted-firmware-a"
    env = {
        "APOLLO_LOCAL_BUILD_USE_YOCTO_VARS": "0",
        "ROOT_DIR": str(ROOT),
        "LOCAL_BUILD_DIR": str(local_build_dir),
        "YOCTO_TMP": str(yocto_tmp),
        "TFA_SRC": str(tfa_src),
        "TFA_LINUX_DTS": "7",
        "PATH": f"{fake_bin}:/usr/bin:/bin",
        "MAKE_ARGS_LOG": str(make_args_log),
    }
    result = subprocess.run(
        (
            "bash",
            "-c",
            "\n".join(
                (
                    "set -euo pipefail",
                    'source "${ROOT_DIR}/scripts/build/local_build_common.sh"',
                    'source "${ROOT_DIR}/scripts/build/modules/build_tfa.sh"',
                    "",
                    "mkdir -p \\",
                    '    "${TFA_SRC}" \\',
                    '    "${DEPLOY_DIR}/u-boot" \\',
                    '    "${DEPLOY_DIR}/optee" \\',
                    '    "${TFA_BUILD_DIR}/apollo_fvp/debug" \\',
                    '    "${YOCTO_TMP}/work/apollo_fvp-poky-linux/trusted-firmware-a/1.0/recipe-sysroot-native/usr/bin" \\',
                    '    "${YOCTO_TMP}/work/apollo_fvp-poky-linux/trusted-firmware-a/1.0/recipe-sysroot-native/usr/lib/python3.13/site-packages"',
                    "printf 'u-boot\\n' > "
                    '"${DEPLOY_DIR}/u-boot/u-boot.bin"',
                    "printf 'optee\\n' > "
                    '"${DEPLOY_DIR}/optee/tee-pager_v2.bin"',
                    "printf 'old-bl2\\n' > "
                    '"${TFA_BUILD_DIR}/apollo_fvp/debug/bl2.bin"',
                    "printf 'old-fip\\n' > "
                    '"${TFA_BUILD_DIR}/apollo_fvp/debug/fip.bin"',
                    "printf 'stale\\n' > "
                    '"${TFA_BUILD_DIR}/apollo_fvp/stale-output"',
                    "printf 'stale-digest\\n' > "
                    '"${TFA_BUILD_DIR}/.apollo-tfa-build.sha256"',
                    "",
                    "build_tfa",
                    "",
                    '[[ ! -e "${TFA_BUILD_DIR}/apollo_fvp/stale-output" ]]',
                    'cmp -s "${TFA_BUILD_DIR}/apollo_fvp/debug/bl2.bin" '
                    '"${FW_DIR}/bl2.bin"',
                    'cmp -s "${TFA_BUILD_DIR}/apollo_fvp/debug/fip.bin" '
                    '"${FW_DIR}/fip.bin"',
                    '[[ "$(cat "${FW_DIR}/bl2.bin")" == "new-bl2" ]]',
                    '[[ "$(cat "${FW_DIR}/fip.bin")" == "new-fip" ]]',
                    "grep -Eq '^[0-9a-f]{64}$' "
                    '"${TFA_BUILD_DIR}/.apollo-tfa-build.sha256"',
                    "printf 'observable build_tfa behavior passed\\n'",
                    "",
                )
            ),
        ),
        cwd=ROOT,
        check=False,
        env=env,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    assert result.returncode == 0, f"{result.stdout}\n{result.stderr}"
    assert "observable build_tfa behavior passed" in result.stdout
    assert "LINUX_DTS=7" in make_args_log.read_text(encoding="utf-8")
