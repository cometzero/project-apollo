from __future__ import annotations

import os
from pathlib import Path
import shutil
import subprocess


ROOT = Path(__file__).resolve().parents[1]


def test_yocto_build_sh_uses_system_python_when_virtualenv_is_active(
    tmp_path: Path,
) -> None:
    # Given: a virtualenv precedes system tools in the caller's PATH.
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    script = shutil.copy2(ROOT / "yocto_build.sh", workspace / "yocto_build.sh")
    build_dir = workspace / "build"
    (build_dir / "conf").mkdir(parents=True)
    (workspace / "hsoc-stack/yocto/meta-hsoc-auto-solutions/conf/templates/apollo-qvp").mkdir(
        parents=True
    )
    poky_dir = workspace / "layers/poky"
    poky_dir.mkdir(parents=True)
    (poky_dir / "oe-init-build-env").write_text(
        'cd "$1"\nexport PATH="${FAKE_BITBAKE_DIR}:$PATH"\n', encoding="utf-8"
    )
    tools_dir = tmp_path / "tools"
    tools_dir.mkdir()
    bitbake = tools_dir / "bitbake"
    bitbake.write_text("#!/usr/bin/env bash\ncommand -v python3\n", encoding="utf-8")
    bitbake.chmod(0o755)
    venv_bin = tmp_path / "venv/bin"
    venv_bin.mkdir(parents=True)
    venv_python = venv_bin / "python3"
    venv_python.write_text("#!/usr/bin/env bash\nexit 0\n", encoding="utf-8")
    venv_python.chmod(0o755)
    env = os.environ.copy()
    env.update(
        {
            "APOLLO_AUTO_RESOURCE_LIMITS": "0",
            "BUILD_DIR": str(build_dir),
            "FAKE_BITBAKE_DIR": str(tools_dir),
            "PATH": f"{venv_bin}:/usr/bin:/bin",
            "VIRTUAL_ENV": str(venv_bin.parent),
        }
    )

    # When: the normal build entrypoint initializes and invokes BitBake.
    result = subprocess.run(
        [str(script), "--keep-conf"],
        cwd=workspace,
        env=env,
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    # Then: BitBake resolves the stable host Python, not the virtualenv Python.
    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == "/usr/bin/python3"
