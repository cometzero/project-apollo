from __future__ import annotations

import os
from pathlib import Path

import pytest

from scripts.run import qbox_apollo_runtime as runtime


class FakePlatformProcess:
    def __init__(self, stdout_fd: int) -> None:
        self.stdout = os.fdopen(stdout_fd, "rb", buffering=0)
        self.returncode: int | None = None
        self.pid = os.getpid()

    def poll(self) -> int | None:
        return self.returncode


def pfdi_primary_evidence() -> str:
    lines = [
        "PFDI prerequisites OK",
        "Loading config V1.0: running 4 tasks every 60 ms",
        "libPFDI version: 1.0",
        "Stub firmware detected",
        "pfdi_prerequisites_rc:0",
        "pfdi_service_rc:0",
        "pfdi_cli_rc:0",
        "pfdi_online_rc:0",
        "__QBOX_PFDI_PROBE_DONE__",
    ]
    for cpu in range(4):
        lines.extend(
            (
                f"CPU{cpu}: Firmware reports 41 available diagnostic tests",
                f"CPU{cpu}: Out of Reset (OoR) test OK",
                f"CPU{cpu}: PFDI Online (OnL) test (0 - 40) OK",
                f"CPU{cpu}: injected force error",
                f"CPU{cpu}: PFDI Online (OnL) test failed: "
                "Input/output error (errno=5)",
                f"pfdi_force_error_cpu{cpu}_rc:0",
            )
        )
    return "\n".join(lines)


def pfdi_scp_evidence() -> str:
    lines: list[str] = []
    for cpu in range(4):
        lines.extend(
            (
                f"Started PFDI monitoring for AP cluster 0 core {cpu}",
                f"[SBISTC] SBISTC_EQ_FAIL_CORE{cpu} detected",
                f"[PFDI_MONITOR] Onl PFDI for AP cluster 0 core {cpu} "
                "failed, stopping PFDI monitoring",
                "[FMU] Non-critical fault received:",
            )
        )
    return "\n".join(lines)


def test_run_platform_executes_registry_driver_and_cleans_fifo(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    # Given: real profile/FIFO code with only process and live-log seams faked.
    args = runtime.parse_args(
        ["--validation-profile", "pfdi", "--out-dir", str(tmp_path)]
    )
    reader_fd, writer_fd = os.pipe()
    process = FakePlatformProcess(reader_fd)
    call_count = 0
    launched_fifo_paths: list[str] = []

    def fake_popen(command, **keywords) -> FakePlatformProcess:
        environment = keywords.get("env")
        assert isinstance(environment, dict)
        fifo_path = environment.get("QBOX_RDASPEN_PRIMARY_UART_READ_FILE")
        assert isinstance(fifo_path, str)
        launched_fifo_paths.append(fifo_path)
        return process

    def fake_logs(out_dir: Path) -> dict[str, str]:
        nonlocal call_count
        call_count += 1
        prompts = "\nnexios-bsp# " * call_count
        return {
            "primary_console": pfdi_primary_evidence() + prompts,
            "secure_console": "",
            "scp": pfdi_scp_evidence(),
            "rse": "",
        }

    def fake_stop(active: FakePlatformProcess) -> None:
        active.returncode = 0

    monkeypatch.setattr(runtime, "qbox_env", lambda root, config, artifacts: {})
    monkeypatch.setattr(runtime.subprocess, "Popen", fake_popen)
    monkeypatch.setattr(runtime, "read_console_logs", fake_logs)
    monkeypatch.setattr(runtime, "stop_process", fake_stop)
    monkeypatch.setattr(
        runtime,
        "evaluate",
        lambda logs, **options: {"passed": True, "fail_patterns": {}},
    )
    monkeypatch.setattr(runtime, "missing_required_pass_markers", lambda items: [])
    monkeypatch.setattr(
        runtime,
        "update_progress_marker_first_hits",
        lambda logs, hits, elapsed: None,
    )

    # When: the real production launch loop executes the selected profile.
    result = runtime.run_platform(Path.cwd(), args, {})
    os.close(writer_fd)
    process.stdout.close()

    # Then: the registry result passes and its managed FIFO is cleaned.
    post_login = result[5]
    profile_result = post_login["validation_profile_result"]
    assert isinstance(profile_result, dict)
    assert profile_result.get("verdict") == "PASS"
    assert post_login["cleanup"] == {
        "passed": True,
        "detail": "no_resources",
    }
    fifo_path = tmp_path / "primary-uart-input.fifo"
    assert launched_fifo_paths == [str(fifo_path)]
    assert not fifo_path.exists()


def test_run_platform_launch_failure_cleans_managed_fifo(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    # Given: a selected profile whose platform process cannot launch.
    args = runtime.parse_args(
        ["--validation-profile", "pfdi", "--out-dir", str(tmp_path)]
    )
    monkeypatch.setattr(runtime, "qbox_env", lambda root, config, artifacts: {})

    def fail_launch(command, **keywords) -> FakePlatformProcess:
        raise OSError("task-owned launch failure")

    monkeypatch.setattr(runtime.subprocess, "Popen", fail_launch)

    # When: the production process seam raises during launch.
    with pytest.raises(OSError, match="task-owned launch failure"):
        runtime.run_platform(Path.cwd(), args, {})

    # Then: managed profile ownership removes the FIFO on that exit too.
    assert not (tmp_path / "primary-uart-input.fifo").exists()
