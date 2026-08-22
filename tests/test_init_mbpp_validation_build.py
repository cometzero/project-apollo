from __future__ import annotations

import os
from pathlib import Path
import shutil
import subprocess

import pytest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/build/init_mbpp_validation_build.sh"


def _workspace(tmp_path: Path) -> Path:
    workspace = tmp_path / "workspace"
    script = workspace / "scripts/build/init_mbpp_validation_build.sh"
    script.parent.mkdir(parents=True)
    shutil.copy2(SCRIPT, script)

    poky = workspace / "layers/poky"
    poky.mkdir(parents=True)
    init = poky / "oe-init-build-env"
    init.write_text(
        "build_dir=$1\n"
        "mkdir -p \"$build_dir/conf\"\n"
        "if [ ! -f \"$build_dir/conf/local.conf\" ]; then\n"
        "  cp \"$TEMPLATECONF/local.conf.sample\" \"$build_dir/conf/local.conf\"\n"
        "  cp \"$TEMPLATECONF/bblayers.conf.sample\" \"$build_dir/conf/bblayers.conf\"\n"
        "  printf '%s\\n' \"$TEMPLATECONF\" > \"$build_dir/conf/templateconf.cfg\"\n"
        "fi\n"
        "cd \"$build_dir\"\n",
        encoding="utf-8",
    )

    for machine in ("apollo-fvp", "apollo-qvp"):
        template = (
            workspace
            / "hsoc-stack/yocto/meta-hsoc-auto-solutions/conf/templates"
            / machine
        )
        template.mkdir(parents=True)
        (template / "local.conf.sample").write_text(
            f'MACHINE ??= "{machine}"\n'
            'RD_ASPEN_VARIANT = "cfg2"\n'
            'PC_CPUS_COUNT_DEFAULT = "4"\n'
            'TMPDIR = "${TOPDIR}/tmp_baremetal"\n',
            encoding="utf-8",
        )
        (template / "bblayers.conf.sample").write_text(
            'BBLAYERS = "sample"\n', encoding="utf-8"
        )
    return workspace


def _run(workspace: Path, build_dir: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [str(workspace / "scripts/build/init_mbpp_validation_build.sh"), build_dir],
        cwd=workspace,
        env={**os.environ, "PATH": "/usr/bin:/bin"},
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )


@pytest.mark.parametrize(
    ("build_dir", "machine"),
    [
        ("build/validation/apollo-fvp-16", "apollo-fvp"),
        ("build/validation/apollo-qvp-16", "apollo-qvp"),
    ],
)
def test_helper_initializes_exact_isolated_mbpp_build(
    tmp_path: Path,
    build_dir: str,
    machine: str,
) -> None:
    workspace = _workspace(tmp_path)

    result = _run(workspace, build_dir)

    assert result.returncode == 0, result.stderr
    local_conf = (workspace / build_dir / "conf/local.conf").read_text(
        encoding="utf-8"
    )
    assert f'MACHINE = "{machine}"' in local_conf
    assert 'RD_ASPEN_VARIANT = "cfg2"' in local_conf
    assert 'PC_CPUS_COUNT_DEFAULT = "16"' in local_conf
    assert 'TMPDIR = "${TOPDIR}/tmp_mbpp16"' in local_conf
    assert f'DL_DIR = "{workspace}/build/downloads"' in local_conf
    assert f'SSTATE_DIR = "{workspace}/build/sstate-cache"' in local_conf


def test_helper_is_idempotent_and_preserves_user_configuration(
    tmp_path: Path,
) -> None:
    workspace = _workspace(tmp_path)
    build_dir = "build/validation/apollo-fvp-16"
    first = _run(workspace, build_dir)
    assert first.returncode == 0, first.stderr
    local_conf = workspace / build_dir / "conf/local.conf"
    local_conf.write_text(
        local_conf.read_text(encoding="utf-8") + 'USER_SETTING = "kept"\n',
        encoding="utf-8",
    )

    second = _run(workspace, build_dir)

    assert second.returncode == 0, second.stderr
    content = local_conf.read_text(encoding="utf-8")
    assert content.count("# BEGIN APOLLO MBPP 16-CPU") == 1
    assert content.count("# END APOLLO MBPP 16-CPU") == 1
    assert content.count('USER_SETTING = "kept"') == 1


@pytest.mark.parametrize(
    "build_dir",
    [
        "build",
        "build/validation",
        "build/validation/apollo-fvp-4",
        "build/validation/../apollo-fvp-16",
        "/tmp/apollo-fvp-16",
        ".",
    ],
)
def test_helper_rejects_noncanonical_build_path(
    tmp_path: Path,
    build_dir: str,
) -> None:
    workspace = _workspace(tmp_path)

    result = _run(workspace, build_dir)

    assert result.returncode == 64
    assert "exactly build/validation/apollo-fvp-16" in result.stderr


def test_helper_rejects_symlinked_validation_target(tmp_path: Path) -> None:
    workspace = _workspace(tmp_path)
    validation = workspace / "build/validation"
    validation.mkdir(parents=True)
    external = tmp_path / "external"
    external.mkdir()
    (validation / "apollo-fvp-16").symlink_to(external, target_is_directory=True)

    result = _run(workspace, "build/validation/apollo-fvp-16")

    assert result.returncode == 64
    assert "symlink" in result.stderr
