from __future__ import annotations

import argparse
from pathlib import Path

import pytest

from apollo_validation import cli
from apollo_validation.backend import ImageProfile
from apollo_validation.qbox_runner import QBoxRunRequest, qbox_launcher_command


def qbox_request(
    tmp_path: Path,
    image_profile: ImageProfile,
    test_profile: str | None = None,
) -> QBoxRunRequest:
    image = "nexios-bsp-initramfs" if image_profile == "bsp" else "nexios-image"
    return QBoxRunRequest(
        root=tmp_path,
        build_dir=Path("build"),
        machine="apollo-qvp",
        image=image,
        image_profile=image_profile,
        timeout=600,
        out_dir=tmp_path / "out",
        dry_run=False,
        preflight_only=False,
        test_profile=test_profile,
    )


def test_root_entry_dispatches_qbox_backend(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    # Given: a QBox request and isolated backend implementations.
    request = argparse.Namespace(root=tmp_path, args=["--", "--qbox"])
    qbox_calls: list[tuple[Path, list[str]]] = []

    def run_qbox(root: Path, argv: list[str]) -> int:
        qbox_calls.append((root, argv))
        return 0

    monkeypatch.setattr(cli, "run_qbox_root", run_qbox)

    # When: the generic category runner dispatches the request.
    result = cli.cmd_root_run(request)

    # Then: only the QBox backend receives the request.
    assert result == 0
    assert qbox_calls == [(tmp_path, ["--qbox"])]


def test_qbox_product_command_uses_canonical_yocto_launcher(
    tmp_path: Path,
) -> None:
    # Given: an Apollo QVP product-image request.
    request = qbox_request(tmp_path, "product")

    # When: the QBox launcher command is constructed.
    command = qbox_launcher_command(request, dry_run=False)

    # Then: the headless full-system launcher owns the runtime.
    assert command[0] == str(tmp_path / "run_qbox_yocto.sh")
    assert command[command.index("--machine") + 1] == "apollo-qvp"
    assert command[command.index("--image-basename") + 1] == "nexios-image"
    assert "--headless" in command
    assert "--exit-after-pass" in command
    assert "--no-persistent-rse-state" in command


def test_qbox_bsp_command_selects_bsp_image(tmp_path: Path) -> None:
    # Given: an Apollo QVP BSP-image request.
    request = qbox_request(tmp_path, "bsp")

    # When: the QBox launcher command is constructed.
    command = qbox_launcher_command(request, dry_run=True)

    # Then: BSP and dry-run selection reach the launcher explicitly.
    assert "--bsp" in command
    assert "--dry-run" in command
    assert "--image-basename" not in command


def test_qbox_pfdi_command_selects_runtime_probe(tmp_path: Path) -> None:
    # Given: the Apollo QVP BSP PFDI profile.
    request = qbox_request(tmp_path, "bsp", test_profile="pfdi")

    # When: its canonical QBox launcher command is built.
    command = qbox_launcher_command(request, dry_run=False)

    # Then: the runner enables the fixed PFDI post-login probe.
    assert "--pfdi-probe" in command


def test_qbox_si_cl1_pfdi_command_selects_runtime_probe(
    tmp_path: Path,
) -> None:
    # Given: the Apollo QVP BSP SI CL1 PFDI profile.
    request = qbox_request(tmp_path, "bsp", test_profile="pfdi-si-cl1")

    # When: its canonical QBox launcher command is built.
    command = qbox_launcher_command(request, dry_run=False)

    # Then: the runner enables the fixed SI CL1 Zephyr-shell probe.
    assert "--pfdi-si-cl1-probe" in command
