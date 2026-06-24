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
        ROOT / "local-build.sh",
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
        ROOT / "local-build.sh",
        ROOT / "scripts" / "package.sh",
        *sorted(BUILD.glob("*.sh")),
        *sorted(MODULES.glob("*.sh")),
    ]
    for script in scripts:
        result = run("bash", "-n", str(script))
        assert result.returncode == 0, f"{script}: {result.stderr}"
