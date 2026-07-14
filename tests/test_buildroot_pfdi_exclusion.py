from pathlib import Path
import os
import subprocess
from typing import Final


ROOT: Final = Path(__file__).resolve().parents[1]
BUILDROOT_SCRIPT: Final = ROOT / "scripts/build/modules/build_buildroot.sh"
COMMON_SCRIPT: Final = ROOT / "scripts/build/local_build_common.sh"


def test_buildroot_has_no_pfdi_local_agent_build_path() -> None:
    buildroot_script = BUILDROOT_SCRIPT.read_text(encoding="utf-8")
    common_script = COMMON_SCRIPT.read_text(encoding="utf-8")

    assert "build_pfdi_local_agent" not in buildroot_script
    assert "pfdi-local-agent-build" not in buildroot_script
    assert "starting pfdi-local-agent" not in buildroot_script
    assert "PFDI_LOCAL_AGENT_SRC" not in common_script


def test_buildroot_overlay_removes_stale_pfdi_local_agent(
    tmp_path: Path,
) -> None:
    overlay = tmp_path / "overlay"
    build_dir = tmp_path / "buildroot"
    work_dir = tmp_path / "work"
    overlay_agent = overlay / "usr/bin/pfdi-local-agent"
    target_agent = build_dir / "target/usr/bin/pfdi-local-agent"
    legacy_build_agent = work_dir / "pfdi-local-agent/pfdi-local-agent"
    for agent in (overlay_agent, target_agent, legacy_build_agent):
        agent.parent.mkdir(parents=True, exist_ok=True)
        agent.write_text("stale\n", encoding="utf-8")

    env = os.environ.copy()
    env.update(
        {
            "APOLLO_LOCAL_BUILD_USE_YOCTO_VARS": "0",
            "TEST_BUILDROOT_BUILD_DIR": str(build_dir),
            "TEST_BUILDROOT_OVERLAY": str(overlay),
            "TEST_WORK_DIR": str(work_dir),
        }
    )
    command = (
        "set -euo pipefail\n"
        "source scripts/build/local_build_common.sh\n"
        "source scripts/build/modules/build_buildroot.sh\n"
        'BUILDROOT_BUILD_DIR="${TEST_BUILDROOT_BUILD_DIR}"\n'
        'BUILDROOT_OVERLAY="${TEST_BUILDROOT_OVERLAY}"\n'
        'WORK_DIR="${TEST_WORK_DIR}"\n'
        "prepare_buildroot_overlay\n"
    )

    result = subprocess.run(
        ("bash", "-lc", command),
        cwd=ROOT,
        env=env,
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr
    assert not overlay_agent.exists()
    assert not target_agent.exists()
    assert not legacy_build_agent.exists()
