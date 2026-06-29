from __future__ import annotations

import os
from pathlib import Path
import subprocess

import pytest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "run_qbox_yocto.sh"


def touch_file(path: Path, content: str = "x\n") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def create_yocto_tree(tmp_path: Path) -> tuple[Path, Path, Path, Path, Path]:
    yocto_build = tmp_path / "yocto-build"
    deploy = yocto_build / "tmp_baremetal/deploy/images/apollo-fvp"
    work = yocto_build / "tmp_baremetal/work/apollo_fvp-poky-linux"
    local_build = tmp_path / "local-build"
    qbox_build = local_build / "work/qbox-platform"

    for path in (
        deploy / "nexios-image-apollo-fvp.wic",
        deploy / "efi-capsule-update-disk-image-fvp-rd-aspen.img",
        deploy / "rse-rom-image.img",
        deploy / "rse-flash-image.img",
        deploy / "rse-otp-image.img",
        deploy / "ap-flash-image.img",
        deploy / "bl2.elf",
        deploy / "combined_provisioning_message.bin",
        deploy / "apollo-fvp.dtb",
        deploy / "si0_ramfw.bin",
        deploy / "zephyr-demos-cl1.bin",
        deploy / "zephyr-demos-cl1.elf",
        work / "trusted-firmware-m/2.2.2+git/build/bin/bl1_2.elf",
        work / "trusted-firmware-m/2.2.2+git/build/bin/bl2.elf",
        local_build / "debug/symbols.json",
    ):
        touch_file(path)
    (deploy / "rse-otp-image.img").write_bytes(b"")
    qbox_build.mkdir(parents=True)

    conf = tmp_path / "qbox-platform/platforms/apollo/apollo-qvp.lua"
    touch_file(conf, "return {}\n")
    return yocto_build, deploy, work, local_build, conf


def run_dry_run(
    tmp_path: Path,
    extra_args: list[str] | None = None,
    extra_env: dict[str, str] | None = None,
) -> subprocess.CompletedProcess[str]:
    yocto_build, _deploy, _work, local_build, conf = create_yocto_tree(tmp_path)
    out_dir = tmp_path / "out"

    env = os.environ.copy()
    env.update(
        {
            "YOCTO_BUILD_DIR": str(yocto_build),
            "LOCAL_BUILD_DIR": str(local_build),
            "QBOX_BUILD_DIR": str(local_build / "work/qbox-platform"),
            "QBOX_CONF": str(conf),
            "OUT_DIR": str(out_dir),
            "TMUX_SESSION": "pytest-run-qbox-yocto",
            "SSH_PORT_START": "24600",
            "SSH_PORT_END": "24699",
        }
    )
    if extra_env:
        env.update(extra_env)

    command = [str(SCRIPT), "--dry-run", "--no-attach", *(extra_args or [])]
    return subprocess.run(
        command,
        cwd=ROOT,
        env=env,
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )


def test_run_qbox_yocto_dry_run_maps_yocto_artifacts(tmp_path: Path) -> None:
    result = run_dry_run(tmp_path)

    assert result.returncode == 0, result.stderr
    assert "Apollo QBox Yocto launch" in result.stdout
    assert "tmux_layout: fvp-like" in result.stdout
    assert "ap cpus:       4" in result.stdout
    assert "--rootfs" in result.stdout
    assert "nexios-image-apollo-fvp.wic" in result.stdout
    assert "--efi-capsule-disk" in result.stdout
    assert "efi-capsule-update-disk-image-fvp-rd-aspen.img" in result.stdout
    assert "--rse-rom" in result.stdout
    assert "rse-rom-image.img" in result.stdout
    assert "input-images/rse-otp-image.img" in result.stdout
    assert "--ap-flash" in result.stdout
    assert "ap-flash-image.img" in result.stdout
    assert "--rse-symbols" in result.stdout
    assert "debug/symbols.json" in result.stdout
    assert "--qbox-performance-preset" in result.stdout
    assert "--cc3xx-qemu-native-backend" in result.stdout
    assert "type=user,hostfwd=tcp::" in result.stdout


def test_run_qbox_yocto_passes_child_args_after_separator(tmp_path: Path) -> None:
    result = run_dry_run(tmp_path, extra_args=["--", "--check-only"])

    assert result.returncode == 0, result.stderr
    assert "--check-only" in result.stdout


def test_run_qbox_yocto_uses_fvp_like_tmux_splits(tmp_path: Path) -> None:
    yocto_build, deploy, _work, local_build, conf = create_yocto_tree(tmp_path)
    out_dir = tmp_path / "out"
    fake_bin_dir = tmp_path / "bin"
    tmux_log = tmp_path / "tmux.log"
    fake_bin_dir.mkdir()
    (deploy / "rse-otp-image.img").write_bytes(b"otp")

    fake_tmux = fake_bin_dir / "tmux"
    fake_tmux.write_text(
        "#!/usr/bin/env bash\n"
        "printf '%s\\n' \"$*\" >> \"$TMUX_LOG\"\n"
        "case \"$1\" in\n"
        "  has-session) exit 1 ;;\n"
        "  new-session) printf '%%0\\n' ;;\n"
        "  split-window)\n"
        "    counter_file=\"${TMUX_LOG}.counter\"\n"
        "    counter=0\n"
        "    [[ -f \"$counter_file\" ]] && counter=\"$(<\"$counter_file\")\"\n"
        "    counter=$((counter + 1))\n"
        "    printf '%s\\n' \"$counter\" > \"$counter_file\"\n"
        "    printf '%%%s\\n' \"$counter\"\n"
        "    ;;\n"
        "esac\n",
        encoding="utf-8",
    )
    fake_tmux.chmod(0o755)

    env = os.environ.copy()
    env.update(
        {
            "YOCTO_BUILD_DIR": str(yocto_build),
            "LOCAL_BUILD_DIR": str(local_build),
            "QBOX_BUILD_DIR": str(local_build / "work/qbox-platform"),
            "QBOX_CONF": str(conf),
            "OUT_DIR": str(out_dir),
            "TMUX_SESSION": "pytest-run-qbox-yocto-layout",
            "TMUX_BIN": str(fake_tmux),
            "TMUX_LOG": str(tmux_log),
            "SSH_PORT_START": "24800",
            "SSH_PORT_END": "24899",
        }
    )

    result = subprocess.run(
        [str(SCRIPT), "--no-attach"],
        cwd=ROOT,
        env=env,
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    assert result.returncode == 0, result.stderr
    tmux_lines = tmux_log.read_text(encoding="utf-8").splitlines()
    split_lines = [line for line in tmux_lines if line.startswith("split-window ")]
    assert len(split_lines) == 6
    assert any(" -v -b -l 70% -t %0 " in f" {line} " for line in split_lines)
    assert any(" -h -l 40% -t %1 " in f" {line} " for line in split_lines)
    assert any(" -v -l 75% -t %2 " in f" {line} " for line in split_lines)
    assert any(" -v -l 67% -t %3 " in f" {line} " for line in split_lines)
    assert any(" -v -l 50% -t %4 " in f" {line} " for line in split_lines)
    assert any(" -h -l 50% -t %0 " in f" {line} " for line in split_lines)
    assert any(line == "select-pane -t %1 -T primary_console" for line in tmux_lines)
    assert any(line == "select-pane -t %2 -T rse" for line in tmux_lines)
    assert any(line == "select-pane -t %3 -T safety_island_cl0" for line in tmux_lines)
    assert any(line == "select-pane -t %4 -T safety_island_cl1" for line in tmux_lines)
    assert any(line == "select-pane -t %5 -T secure_console" for line in tmux_lines)
    assert any(line == "select-pane -t %6 -T platform" for line in tmux_lines)
    assert not any(line.startswith("select-layout ") for line in tmux_lines)
    assert any("QBOX_APOLLO_NUM_CPUS=4" in line for line in tmux_lines)


def test_tmux_primary_console_filters_terminal_status_response() -> None:
    tmux_script = ROOT / "scripts/run/run_qbox_apollo_fvp_full_tmux.sh"
    script_text = tmux_script.read_text(encoding="utf-8")

    assert "is_terminal_status_response_line" in script_text
    assert r"^\[[0-9]{1,5}\;[0-9]{1,5}R$" in script_text
    assert "write_fifo_line \"${fifo_path}\" \"${line}\"" in script_text


@pytest.mark.parametrize(
    ("args", "message"),
    [
        (
            ["--enable-test-device"],
            "is no longer supported",
        ),
        (
            ["--mock-cc3xx"],
            "is no longer supported",
        ),
    ],
)
def test_run_qbox_yocto_rejects_removed_options(
    tmp_path: Path,
    args: list[str],
    message: str,
) -> None:
    result = run_dry_run(tmp_path, extra_args=args)

    assert result.returncode != 0
    assert message in result.stderr


def test_run_qbox_yocto_rejects_missing_rootfs(tmp_path: Path) -> None:
    yocto_build, deploy, _work, local_build, conf = create_yocto_tree(tmp_path)
    (deploy / "nexios-image-apollo-fvp.wic").unlink()

    env = os.environ.copy()
    env.update(
        {
            "YOCTO_BUILD_DIR": str(yocto_build),
            "LOCAL_BUILD_DIR": str(local_build),
            "QBOX_BUILD_DIR": str(local_build / "work/qbox-platform"),
            "QBOX_CONF": str(conf),
            "OUT_DIR": str(tmp_path / "out"),
            "TMUX_SESSION": "pytest-run-qbox-yocto-missing-rootfs",
            "SSH_PORT_START": "24700",
            "SSH_PORT_END": "24799",
        }
    )

    result = subprocess.run(
        [str(SCRIPT), "--dry-run", "--no-attach"],
        cwd=ROOT,
        env=env,
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    assert result.returncode != 0
    assert "missing required Yocto rootfs WIC image" in result.stderr
