from __future__ import annotations

import json
import socket
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts/test"))

from run_test_preflight import PreflightInputs, run_preflight


def write_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def make_preflight_tree(
    root: Path,
    *,
    executable: bool = True,
    plugin: bool = True,
    target_ip: str = "127.0.0.1:2299",
) -> Path:
    deploy_dir = root / "build/tmp_baremetal/deploy/images/apollo-fvp"
    fvp_bin = root / "build/tmp_baremetal/sysroots-components/x86_64/fvp-rd-aspen-native/usr/bin"
    runfvp = root / "layers/meta-arm/scripts/runfvp"
    image_rootfs = root / "build/tmp_baremetal/work/apollo_fvp-poky-linux/nexios-image/1.0/rootfs"
    for path in (deploy_dir, fvp_bin, runfvp.parent, image_rootfs):
        path.mkdir(parents=True, exist_ok=True)
    runfvp.write_text("#!/bin/sh\n", encoding="utf-8")
    if executable:
        (fvp_bin / "FVP_Zena_CSS_Cfg2").write_text("model\n", encoding="utf-8")
    if plugin:
        (fvp_bin / "Crypto.so").write_text("plugin\n", encoding="utf-8")
    for name in (
        "nexios-image-apollo-fvp.wic",
        "nexios-image-apollo-fvp.ext4.verity",
        "rse-rom-image.img",
        "rse-flash-image.img",
        "rse-otp-image.img",
        "ap-flash-image.img",
        "combined_provisioning_message.bin",
        "efi-capsule-update-disk-image-fvp-rd-aspen.img",
    ):
        (deploy_dir / name).write_text(name + "\n", encoding="utf-8")
    write_json(
        deploy_dir / "nexios-image-apollo-fvp.testdata.json",
        {
            "IMAGE_FSTYPES": "wic ext4.verity",
            "IMAGE_LINK_NAME": "nexios-image-apollo-fvp",
            "IMAGE_ROOTFS": "tmp_baremetal/work/apollo_fvp-poky-linux/nexios-image/1.0/rootfs",
            "TEST_TARGET_IP": target_ip,
        },
    )
    fvpconf = deploy_dir / "nexios-image-apollo-fvp.fvpconf"
    write_json(
        fvpconf,
        {
            "fvp-bindir": str(fvp_bin),
            "exe": "FVP_Zena_CSS_Cfg2",
            "parameters": {
                "css.smb.rseil.rse.rom.raw_image": str(deploy_dir / "rse-rom-image.img"),
                "css.smb.rseil.rse_flashloader.fname": str(deploy_dir / "rse-flash-image.img"),
                "css.smb.rseil.rse_flashloader.fnameWrite": str(
                    root / "build/tmp_baremetal/fvp-writable/rse-flash-image.img"
                ),
                "css.smb.rseil.rse.lcm_nvm.raw_image": str(deploy_dir / "rse-otp-image.img"),
                "ros.flash_loader.fname": str(deploy_dir / "ap-flash-image.img"),
                "ros.flash_loader.fnameWrite": str(
                    root / "build/tmp_baremetal/fvp-writable/ap-flash-image.img"
                ),
                "ros.virtio_block0.image_path": str(deploy_dir / "nexios-image-apollo-fvp.wic"),
                "ros.virtio_block1.image_path": str(
                    deploy_dir / "efi-capsule-update-disk-image-fvp-rd-aspen.img"
                ),
            },
            "data": [
                "css.smb.rseil.rse.sram1="
                + str(deploy_dir / "combined_provisioning_message.bin")
                + "@0x20000"
            ],
            "args": ["--plugin", "Crypto.so"],
        },
    )
    return fvpconf


def test_fvpconf_preflight_resolves_bindir(tmp_path: Path) -> None:
    # Given: a fake Apollo deploy with fvp-bindir, executable, and image artifacts.
    root = tmp_path / "repo"
    fvpconf = make_preflight_tree(root)

    # When: preflight checks the selected deployment.
    result = run_preflight(PreflightInputs(root, Path("build"), "apollo-fvp", fvpconf))

    # Then: the executable is resolved from fvp-bindir and no blocker is reported.
    assert result["status"] == "ok"
    executable = next(check for check in result["checks"] if check["name"] == "fvp_executable")
    assert executable["path"].endswith("usr/bin/FVP_Zena_CSS_Cfg2")
    assert result["blockers"] == []


def test_preflight_does_not_require_fvp_writeback_outputs(tmp_path: Path) -> None:
    root = tmp_path / "repo"
    fvpconf = make_preflight_tree(root)

    result = run_preflight(PreflightInputs(root, Path("build"), "apollo-fvp", fvpconf))

    assert result["status"] == "ok"
    checked_paths = {check["path"] for check in result["checks"]}
    assert str(root / "build/tmp_baremetal/fvp-writable/rse-flash-image.img") not in checked_paths
    assert str(root / "build/tmp_baremetal/fvp-writable/ap-flash-image.img") not in checked_paths


def test_crypto_plugin_check_resolves_plugin_from_fvpconf_args(tmp_path: Path) -> None:
    # Given: a fake FVP config whose Crypto plugin arg is relative to fvp-bindir.
    root = tmp_path / "repo"
    fvpconf = make_preflight_tree(root)

    # When: preflight parses plugin args from the fvpconf.
    result = run_preflight(PreflightInputs(root, Path("build"), "apollo-fvp", fvpconf))

    # Then: the Crypto plugin path is resolved and accepted.
    crypto = next(check for check in result["checks"] if check["name"] == "plugin:Crypto.so")
    assert crypto["status"] == "ok"
    assert crypto["path"].endswith("usr/bin/Crypto.so")


def test_preflight_reports_missing_executable_blocker(tmp_path: Path) -> None:
    # Given: a fake FVP config whose fvp-bindir/exe path does not exist.
    root = tmp_path / "repo"
    fvpconf = make_preflight_tree(root, executable=False)

    # When: preflight checks the deployment.
    result = run_preflight(PreflightInputs(root, Path("build"), "apollo-fvp", fvpconf))

    # Then: it blocks with the precise missing executable reason.
    assert result["status"] == "blocked"
    assert {blocker["reason"] for blocker in result["blockers"]} == {
        "blocked_missing_fvp_executable"
    }


def test_preflight_reports_missing_crypto_plugin_blocker(tmp_path: Path) -> None:
    # Given: a fake FVP config whose Crypto plugin arg points at a missing file.
    root = tmp_path / "repo"
    fvpconf = make_preflight_tree(root, plugin=False)

    # When: preflight checks the deployment.
    result = run_preflight(PreflightInputs(root, Path("build"), "apollo-fvp", fvpconf))

    # Then: it blocks with the precise missing Crypto plugin reason.
    plugin_check = next(check for check in result["checks"] if check["name"] == "plugin:Crypto.so")
    assert result["status"] == "blocked"
    assert plugin_check["status"] == "blocked"
    assert plugin_check["reason"] == "blocked_missing_crypto_plugin"
    assert "blocked_missing_crypto_plugin" in {blocker["reason"] for blocker in result["blockers"]}


def test_preflight_reports_port_in_use_blocker(tmp_path: Path) -> None:
    # Given: the runtime target endpoint is already listening on loopback.
    root = tmp_path / "repo"
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as listener:
        listener.bind(("127.0.0.1", 0))
        listener.listen(1)
        host, port = listener.getsockname()
        target_ip = f"{host}:{port}"
        fvpconf = make_preflight_tree(root, target_ip=target_ip)

        # When: preflight checks the deployment.
        result = run_preflight(PreflightInputs(root, Path("build"), "apollo-fvp", fvpconf))

    # Then: it reports the target endpoint as blocked without launching FVP.
    port_check = next(check for check in result["checks"] if check["name"] == "runtime_port")
    assert result["status"] == "blocked"
    assert port_check == {
        "name": "runtime_port",
        "status": "blocked",
        "path": target_ip,
        "reason": "blocked_port_in_use",
    }
    assert {"reason": "blocked_port_in_use", "path": target_ip, "name": "runtime_port"} in result[
        "blockers"
    ]
