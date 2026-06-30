from __future__ import annotations

import json
import os
from pathlib import Path
import shutil
import subprocess

import pytest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "run_fvp.sh"


def make_executable(path: Path) -> Path:
    path.write_text("#!/usr/bin/env bash\nexit 0\n", encoding="utf-8")
    path.chmod(0o755)
    return path


def write_fvpconf(path: Path, flash_image: Path) -> None:
    path.write_text(
        json.dumps(
            {
                "parameters": {
                    "css.rse.flash_loader.fnameWrite": str(flash_image),
                },
                "terminals": {
                    "css.rse.terminal_uart": "RSE",
                },
            }
        ),
        encoding="utf-8",
    )


def run_dry_run(
    tmp_path: Path,
    extra_args: list[str] | None = None,
) -> subprocess.CompletedProcess[str]:
    build_dir = tmp_path / "build"
    deploy_dir = build_dir / "tmp_baremetal/deploy/images/apollo-fvp"
    fake_bin_dir = tmp_path / "bin"
    deploy_dir.mkdir(parents=True, exist_ok=True)
    fake_bin_dir.mkdir(exist_ok=True)

    env = os.environ.copy()
    env.update(
        {
            "RUN_STAMP": "pytest",
            "TMUX_BIN": str(make_executable(fake_bin_dir / "tmux")),
        }
    )

    command = [
        str(SCRIPT),
        "--dry-run",
        "--no-attach",
        "--build-dir",
        str(build_dir),
        "--runfvp-bin",
        str(make_executable(fake_bin_dir / "runfvp")),
        *(extra_args or []),
    ]
    return subprocess.run(
        command,
        cwd=ROOT,
        env=env,
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )


def run_help() -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        (str(SCRIPT), "--help"),
        cwd=ROOT,
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )


def test_help_documents_local_mode_and_recovery_command() -> None:
    # Given: the FVP runner entrypoint.
    # When: the user asks for CLI help.
    result = run_help()

    # Then: help shows how to run and recover the local FVP package workflow.
    assert result.returncode == 0, result.stderr
    output = f"{result.stdout}\n{result.stderr}"
    assert "--local" in output
    assert "./run_fvp.sh --local" in output
    assert "./local_build.sh --package first" in output

    example_lines = [
        line.strip()
        for line in output.splitlines()
        if line.strip().startswith("./")
    ]
    assert example_lines
    for line in example_lines:
        script = line.split()[0]
        assert (ROOT / script.removeprefix("./")).exists(), line


def test_run_fvp_uses_stable_yocto_fvpconf(tmp_path: Path) -> None:
    deploy_dir = tmp_path / "build/tmp_baremetal/deploy/images/apollo-fvp"
    flash_image = deploy_dir / "ap-flash.img"
    fvpconf = deploy_dir / "nexios-image-apollo-fvp.fvpconf"
    deploy_dir.mkdir(parents=True)
    flash_image.write_bytes(b"flash")
    write_fvpconf(fvpconf, flash_image)

    result = run_dry_run(tmp_path)

    assert result.returncode == 0, result.stderr
    assert "Apollo FVP tmux run" in result.stdout
    assert "session: apollo-fvp-yocto-pytest" in result.stdout
    assert f"fvpconf: {fvpconf}" in result.stdout
    assert f"out_dir: {tmp_path}/build/fvp-tmux/apollo-fvp-pytest" in result.stdout


def test_run_fvp_falls_back_to_latest_timestamped_fvpconf(tmp_path: Path) -> None:
    deploy_dir = tmp_path / "build/tmp_baremetal/deploy/images/apollo-fvp"
    flash_image = deploy_dir / "ap-flash.img"
    older = deploy_dir / "nexios-image-apollo-fvp-20260101000000.fvpconf"
    newer = deploy_dir / "nexios-image-apollo-fvp-20260202000000.fvpconf"
    deploy_dir.mkdir(parents=True)
    flash_image.write_bytes(b"flash")
    write_fvpconf(older, flash_image)
    write_fvpconf(newer, flash_image)
    os.utime(older, (1, 1))
    os.utime(newer, (2, 2))

    result = run_dry_run(tmp_path)

    assert result.returncode == 0, result.stderr
    assert f"fvpconf: {newer}" in result.stdout


def test_run_fvp_forwards_extra_fvp_args(tmp_path: Path) -> None:
    deploy_dir = tmp_path / "build/tmp_baremetal/deploy/images/apollo-fvp"
    flash_image = deploy_dir / "ap-flash.img"
    fvpconf = deploy_dir / "nexios-image-apollo-fvp.fvpconf"
    deploy_dir.mkdir(parents=True)
    flash_image.write_bytes(b"flash")
    write_fvpconf(fvpconf, flash_image)

    result = run_dry_run(
        tmp_path,
        extra_args=["--", "--parameter", "css.test_parameter=1"],
    )

    assert result.returncode == 0, result.stderr
    assert "--parameter css.test_parameter=1" in result.stdout


def test_run_fvp_copies_writable_flash_from_read_image_when_write_path_is_missing(
    tmp_path: Path,
) -> None:
    # Given: Yocto fvpconf points fnameWrite at a test-only path that does not
    # exist until do_testimage prepares it.
    deploy_dir = tmp_path / "build/tmp_baremetal/deploy/images/apollo-fvp"
    read_image = deploy_dir / "rse-flash-image.img"
    missing_write_image = tmp_path / "build/tmp_baremetal/fvp-writable/rse-flash-image.img"
    fvpconf = deploy_dir / "nexios-image-apollo-fvp.fvpconf"
    deploy_dir.mkdir(parents=True)
    read_image.write_bytes(b"clean-read-flash")
    fvpconf.write_text(
        json.dumps(
            {
                "parameters": {
                    "css.rse.flash_loader.fname": str(read_image),
                    "css.rse.flash_loader.fnameWrite": str(missing_write_image),
                },
                "terminals": {
                    "css.rse.terminal_uart": "RSE",
                },
            }
        ),
        encoding="utf-8",
    )

    # When: run_fvp.sh prepares a dry run.
    result = run_dry_run(tmp_path)

    # Then: the generated command uses a per-run writable copy sourced from
    # fname, not the missing fnameWrite path.
    writable = tmp_path / "build/fvp-tmux/apollo-fvp-pytest/writable-images/rse-flash-image.img"
    assert result.returncode == 0, result.stderr
    assert writable.read_bytes() == b"clean-read-flash"
    assert f"css.rse.flash_loader.fnameWrite={writable}" in result.stdout
    assert str(missing_write_image) not in result.stdout


def test_run_fvp_copies_rse_otp_nvm_to_writable_image(tmp_path: Path) -> None:
    deploy_dir = tmp_path / "build/tmp_baremetal/deploy/images/apollo-fvp"
    flash_image = deploy_dir / "rse-flash-image.img"
    otp_image = deploy_dir / "rse-otp-image.img"
    fvpconf = deploy_dir / "nexios-image-apollo-fvp.fvpconf"
    deploy_dir.mkdir(parents=True)
    flash_image.write_bytes(b"flash")
    otp_image.write_bytes(b"clean-otp")
    fvpconf.write_text(
        json.dumps(
            {
                "parameters": {
                    "css.rse.flash_loader.fnameWrite": str(flash_image),
                    "css.smb.rseil.rse.lcm_nvm.raw_image": str(otp_image),
                },
                "terminals": {
                    "css.rse.terminal_uart": "RSE",
                },
            }
        ),
        encoding="utf-8",
    )

    result = run_dry_run(tmp_path)

    writable = tmp_path / "build/fvp-tmux/apollo-fvp-pytest/writable-images/rse-otp-image.img"
    assert result.returncode == 0, result.stderr
    assert writable.read_bytes() == b"clean-otp"
    assert f"css.smb.rseil.rse.lcm_nvm.raw_image={writable}" in result.stdout


def test_run_fvp_local_mode_uses_local_package_defaults(tmp_path: Path) -> None:
    build_dir = tmp_path / "build"
    deploy_dir = build_dir / "local-apollo-fvp/deploy"
    flash_image = deploy_dir / "ap-flash.img"
    fvpconf = deploy_dir / "apollo-fvp-local.fvpconf"
    deploy_dir.mkdir(parents=True)
    flash_image.write_bytes(b"flash")
    write_fvpconf(fvpconf, flash_image)

    result = run_dry_run(tmp_path, extra_args=["--local"])

    assert result.returncode == 0, result.stderr
    assert "session: apollo-fvp-local-pytest" in result.stdout
    assert f"fvpconf: {fvpconf}" in result.stdout
    assert f"out_dir: {build_dir}/local-apollo-fvp/tmux-run/pytest" in result.stdout


def test_run_fvp_local_mode_preserves_fvpconf_and_deploy_dir_overrides(
    tmp_path: Path,
) -> None:
    deploy_dir = tmp_path / "custom-deploy"
    flash_image = deploy_dir / "ap-flash.img"
    fvpconf = deploy_dir / "custom.fvpconf"
    deploy_dir.mkdir()
    flash_image.write_bytes(b"flash")
    write_fvpconf(fvpconf, flash_image)

    result = run_dry_run(
        tmp_path,
        extra_args=[
            "--local",
            "--deploy-dir",
            str(deploy_dir),
            "--fvpconf",
            str(fvpconf),
        ],
    )

    assert result.returncode == 0, result.stderr
    assert "session: apollo-fvp-local-pytest" in result.stdout
    assert f"fvpconf: {fvpconf}" in result.stdout


def test_run_fvp_local_mode_missing_fvpconf_reports_local_package_command(
    tmp_path: Path,
) -> None:
    deploy_dir = tmp_path / "build/local-apollo-fvp/deploy"
    deploy_dir.mkdir(parents=True)

    result = run_dry_run(tmp_path, extra_args=["--local"])

    assert result.returncode != 0
    assert "Run ./local_build.sh --package first" in result.stderr


def test_run_fvp_missing_yocto_fvpconf_reports_yocto_build_command(
    tmp_path: Path,
) -> None:
    deploy_dir = tmp_path / "build/tmp_baremetal/deploy/images/apollo-fvp"
    deploy_dir.mkdir(parents=True)

    result = run_dry_run(tmp_path)

    assert result.returncode != 0
    assert "Run ./yocto_build.sh first" in result.stderr


def test_run_fvp_is_not_dependent_on_tmux_runner_env(tmp_path: Path) -> None:
    deploy_dir = tmp_path / "build/tmp_baremetal/deploy/images/apollo-fvp"
    flash_image = deploy_dir / "ap-flash.img"
    fvpconf = deploy_dir / "nexios-image-apollo-fvp.fvpconf"
    deploy_dir.mkdir(parents=True)
    flash_image.write_bytes(b"flash")
    write_fvpconf(fvpconf, flash_image)

    broken_runner = tmp_path / "broken-runner.sh"
    broken_runner.write_text(
        "#!/usr/bin/env bash\necho should-not-run >&2\nexit 99\n",
        encoding="utf-8",
    )
    broken_runner.chmod(0o755)

    env = os.environ.copy()
    env["TMUX_RUNNER"] = str(broken_runner)
    result = subprocess.run(
        [
            str(SCRIPT),
            "--dry-run",
            "--no-attach",
            "--build-dir",
            str(tmp_path / "build"),
            "--runfvp-bin",
            str(make_executable(tmp_path / "runfvp")),
        ],
        cwd=ROOT,
        env=env,
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    assert result.returncode == 0, result.stderr
    assert "should-not-run" not in result.stderr


def test_run_fvp_supervisor_ignores_extra_fvp_terminals(tmp_path: Path) -> None:
    out_dir = tmp_path / "out"
    fake_bin_dir = tmp_path / "bin"
    tmux_log = tmp_path / "tmux.log"
    args_file = tmp_path / "extra-args.txt"
    fvpconf = tmp_path / "apollo.fvpconf"
    fake_bin_dir.mkdir()
    out_dir.mkdir()
    args_file.write_text("", encoding="utf-8")
    write_fvpconf(fvpconf, tmp_path / "flash.img")

    fake_runfvp = fake_bin_dir / "runfvp"
    fake_runfvp.write_text(
        "#!/usr/bin/env bash\n"
        "printf '%s\\n' 'Info: RD_ASD: terminal_sec_uart: Listening for serial connection on port 5003'\n"
        "printf '%s\\n' 'Info: RD_ASD: terminal_ns_uart0: Listening for serial connection on port 5004'\n"
        "printf '%s\\n' 'Info: RD_ASD: terminal_0: Listening for serial connection on port 5005'\n"
        "printf '%s\\n' 'Info: RD_ASD: terminal_1: Listening for serial connection on port 5006'\n",
        encoding="utf-8",
    )
    fake_runfvp.chmod(0o755)
    make_executable(fake_bin_dir / "telnet")

    fake_tmux = fake_bin_dir / "tmux"
    fake_tmux.write_text(
        "#!/usr/bin/env bash\n"
        "printf '%s\\n' \"$*\" >> \"$TMUX_LOG\"\n"
        "if [[ \"$1\" == \"split-window\" ]]; then printf '%%1\\n'; fi\n",
        encoding="utf-8",
    )
    fake_tmux.chmod(0o755)

    env = os.environ.copy()
    env.update(
        {
            "PATH": f"{fake_bin_dir}:{env['PATH']}",
            "TMUX_BIN": str(fake_tmux),
            "TMUX_LOG": str(tmux_log),
            "MACHINE": "apollo-fvp",
            "DEPLOY_DIR": str(tmp_path),
            "RUNFVP_BIN": str(fake_runfvp),
            "FVP_CONF": str(fvpconf),
            "OUT_DIR": str(out_dir),
            "EXTRA_ARGS_FILE": str(args_file),
            "TMUX_SESSION": "apollo-test",
        }
    )

    result = subprocess.run(
        [str(SCRIPT), "--supervise"],
        cwd=ROOT,
        env=env,
        check=False,
        text=True,
        input="\n",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    assert result.returncode == 0, result.stderr
    tmux_text = tmux_log.read_text(encoding="utf-8")
    assert "terminal_sec_uart" in tmux_text
    assert "5003" in tmux_text
    assert "terminal_ns_uart0" in tmux_text
    assert "5004" in tmux_text
    assert "terminal_0" not in tmux_text
    assert "terminal_1" not in tmux_text
    assert "synchronize-panes off" in tmux_text
    assert "python3 -c" in tmux_text
    assert "tee -a" not in tmux_text


def test_run_fvp_supervisor_splits_from_root_pane(tmp_path: Path) -> None:
    out_dir = tmp_path / "out"
    fake_bin_dir = tmp_path / "bin"
    tmux_log = tmp_path / "tmux.log"
    args_file = tmp_path / "extra-args.txt"
    fvpconf = tmp_path / "apollo.fvpconf"
    fake_bin_dir.mkdir()
    out_dir.mkdir()
    args_file.write_text("", encoding="utf-8")
    write_fvpconf(fvpconf, tmp_path / "flash.img")

    fake_runfvp = fake_bin_dir / "runfvp"
    fake_runfvp.write_text(
        "#!/usr/bin/env bash\n"
        "printf '%s\\n' 'Info: RD_ASD: terminal_uart: Listening for serial connection on port 5000'\n"
        "printf '%s\\n' 'Info: RD_ASD: terminal_uart_si_cluster0: Listening for serial connection on port 5001'\n",
        encoding="utf-8",
    )
    fake_runfvp.chmod(0o755)
    make_executable(fake_bin_dir / "telnet")

    fake_tmux = fake_bin_dir / "tmux"
    fake_tmux.write_text(
        "#!/usr/bin/env bash\n"
        "printf '%s\\n' \"$*\" >> \"$TMUX_LOG\"\n"
        "if [[ \"$1\" == \"split-window\" ]]; then printf '%%new\\n'; fi\n",
        encoding="utf-8",
    )
    fake_tmux.chmod(0o755)

    env = os.environ.copy()
    env.update(
        {
            "PATH": f"{fake_bin_dir}:{env['PATH']}",
            "TMUX_BIN": str(fake_tmux),
            "TMUX_LOG": str(tmux_log),
            "MACHINE": "apollo-fvp",
            "DEPLOY_DIR": str(tmp_path),
            "RUNFVP_BIN": str(fake_runfvp),
            "FVP_CONF": str(fvpconf),
            "OUT_DIR": str(out_dir),
            "EXTRA_ARGS_FILE": str(args_file),
            "TMUX_SESSION": "apollo-test",
            "TMUX_PANE": "%0",
        }
    )

    result = subprocess.run(
        [str(SCRIPT), "--supervise"],
        cwd=ROOT,
        env=env,
        check=False,
        text=True,
        input="\n",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    assert result.returncode == 0, result.stderr
    tmux_lines = tmux_log.read_text(encoding="utf-8").splitlines()
    split_lines = [line for line in tmux_lines if line.startswith("split-window ")]
    assert split_lines
    assert all(" -t %0 " in f" {line} " for line in split_lines)
    assert any(line == "select-pane -t %0" for line in tmux_lines)


def test_run_fvp_precreates_uart_panes_before_fvp_start(tmp_path: Path) -> None:
    build_dir = tmp_path / "build"
    deploy_dir = build_dir / "tmp_baremetal/deploy/images/apollo-fvp"
    fake_bin_dir = tmp_path / "bin"
    tmux_log = tmp_path / "tmux.log"
    deploy_dir.mkdir(parents=True)
    fake_bin_dir.mkdir()

    flash_image = deploy_dir / "ap-flash.img"
    fvpconf = deploy_dir / "nexios-image-apollo-fvp.fvpconf"
    flash_image.write_bytes(b"flash")
    write_fvpconf(fvpconf, flash_image)
    make_executable(fake_bin_dir / "runfvp")

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
            "RUN_STAMP": "pytest",
            "TMUX_BIN": str(fake_tmux),
            "TMUX_LOG": str(tmux_log),
        }
    )

    result = subprocess.run(
        [
            str(SCRIPT),
            "--no-attach",
            "--build-dir",
            str(build_dir),
            "--runfvp-bin",
            str(fake_bin_dir / "runfvp"),
        ],
        cwd=ROOT,
        env=env,
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    assert result.returncode == 0, result.stderr
    tmux_text = tmux_log.read_text(encoding="utf-8")
    tmux_lines = tmux_text.splitlines()
    split_lines = [line for line in tmux_lines if line.startswith("split-window ")]
    assert len(split_lines) == 6
    assert any(" -v -b -l 70% -t %0 " in f" {line} " for line in split_lines)
    assert any(" -h -l 40% -t %1 " in f" {line} " for line in split_lines)
    assert any(" -v -l 75% -t %2 " in f" {line} " for line in split_lines)
    assert any(" -v -l 67% -t %3 " in f" {line} " for line in split_lines)
    assert any(" -v -l 50% -t %4 " in f" {line} " for line in split_lines)
    assert any(" -h -l 50% -t %0 " in f" {line} " for line in split_lines)
    assert any(
        line.startswith("set-hook ")
        and "client-attached" in line
        and "--rebalance-fvp-uart-panes" in line
        for line in tmux_lines
    )
    assert any(
        line.startswith("set-hook ")
        and "client-resized" in line
        and "--rebalance-fvp-uart-panes" in line
        for line in tmux_lines
    )
    assert tmux_text.count("python3 -c") >= 5
    assert tmux_text.count("display.append(13)") >= 5
    assert "tee -a" not in tmux_text
    assert not any(line.startswith("select-layout ") for line in tmux_lines)

    control_dir = build_dir / "fvp-tmux/apollo-fvp-pytest/control"
    assert (control_dir / "start").exists()


def test_run_fvp_rebalance_keeps_uart_stack_even_after_resize() -> None:
    tmux_bin = shutil.which("tmux")
    if tmux_bin is None:
        pytest.skip("tmux is not installed")

    session = f"pytest-fvp-layout-{os.getpid()}"

    def tmux(*args: str) -> str:
        result = subprocess.run(
            [tmux_bin, *args],
            check=True,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        return result.stdout.strip()

    try:
        subprocess.run(
            [
                tmux_bin,
                "new-session",
                "-d",
                "-x",
                "80",
                "-y",
                "24",
                "-s",
                session,
                "-n",
                "fvp",
                "sleep",
                "600",
            ],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        root_pane = tmux("display-message", "-p", "-t", f"{session}:fvp", "#{pane_id}")
        u_boot = tmux(
            "split-window",
            "-d",
            "-P",
            "-F",
            "#{pane_id}",
            "-v",
            "-b",
            "-l",
            "70%",
            "-t",
            root_pane,
            "sleep",
            "600",
        )
        rse = tmux(
            "split-window",
            "-d",
            "-P",
            "-F",
            "#{pane_id}",
            "-h",
            "-l",
            "40%",
            "-t",
            u_boot,
            "sleep",
            "600",
        )
        si0 = tmux(
            "split-window",
            "-d",
            "-P",
            "-F",
            "#{pane_id}",
            "-v",
            "-l",
            "75%",
            "-t",
            rse,
            "sleep",
            "600",
        )
        si1 = tmux(
            "split-window",
            "-d",
            "-P",
            "-F",
            "#{pane_id}",
            "-v",
            "-l",
            "67%",
            "-t",
            si0,
            "sleep",
            "600",
        )
        tf_a = tmux(
            "split-window",
            "-d",
            "-P",
            "-F",
            "#{pane_id}",
            "-v",
            "-l",
            "50%",
            "-t",
            si1,
            "sleep",
            "600",
        )
        tmux(
            "split-window",
            "-d",
            "-P",
            "-F",
            "#{pane_id}",
            "-h",
            "-l",
            "50%",
            "-t",
            root_pane,
            "sleep",
            "600",
        )
        tmux("resize-window", "-t", f"{session}:fvp", "-x", "240", "-y", "80")

        subprocess.run(
            [str(SCRIPT), "--rebalance-fvp-uart-panes", rse, si0, si1, tf_a],
            check=True,
            env={**os.environ, "TMUX_BIN": tmux_bin},
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

        heights = [
            int(tmux("display-message", "-p", "-t", pane, "#{pane_height}"))
            for pane in (rse, si0, si1, tf_a)
        ]
        assert max(heights) - min(heights) <= 1
    finally:
        subprocess.run(
            [tmux_bin, "kill-session", "-t", session],
            check=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
