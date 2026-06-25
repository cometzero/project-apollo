from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess


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
    assert f"session: apollo-fvp-yocto-pytest" in result.stdout
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
