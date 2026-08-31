from __future__ import annotations

from pathlib import Path

from nexios_bsp_workflow_support import (
    run_build_dry_run,
    run_qbox_bsp_dry_run,
    runner_argv,
)


def test_default_build_requests_only_product_target(tmp_path: Path) -> None:
    # Given: the default Apollo QVP build profile.
    # When: the public build wrapper is inspected through dry-run.
    result = run_build_dry_run(tmp_path, [])

    # Then: only the product image target is requested.
    assert result.returncode == 0, result.stderr
    assert result.stdout.split()[-1] == "nexios-image"
    assert "nexios-bsp-initramfs" not in result.stdout.split()


def test_bsp_build_requests_only_bsp_target(tmp_path: Path) -> None:
    # Given: the dedicated BSP build profile.
    # When: --bsp is selected through the public wrapper.
    result = run_build_dry_run(tmp_path, ["--bsp"])

    # Then: no product image target is requested.
    assert result.returncode == 0, result.stderr
    assert result.stdout.split()[-1] == "nexios-bsp-initramfs"
    assert "nexios-image" not in result.stdout.split()


def test_qbox_bsp_profile_selects_bsp_artifacts_and_markers(
    tmp_path: Path,
) -> None:
    # Given: an isolated QVP deploy tree containing only BSP image artifacts.
    # When: the QBox wrapper is run with --bsp.
    result = run_qbox_bsp_dry_run(tmp_path)

    # Then: the child runner receives the BSP WIC and completion contract.
    assert result.returncode == 0, result.stderr
    assert "boot profile:  bsp-initramfs" in result.stdout
    assert "nexios-bsp-initramfs-apollo-qvp.qboxconf" in result.stdout
    argv = runner_argv(result.stdout)
    assert argv[argv.index("--rootfs") + 1].endswith(
        "nexios-bsp-initramfs-apollo-qvp.wic"
    )
    assert argv[argv.index("--primary-login-prompt") + 1] == (
        "NEXIOS_BSP_INITRAMFS_READY"
    )
    assert argv[argv.index("--primary-shell-marker") + 1] == "nexios-bsp#"
