from pathlib import Path
import importlib.util
import sys


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/run/run_qbox_apollo_fvp_full.py"


def load_runner():
    spec = importlib.util.spec_from_file_location("apollo_full_runner", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def make_args(tmp_path, *, post_login_probe=True):
    return type(
        "Args",
        (),
        {
            "out_dir": tmp_path,
            "post_login_probe": post_login_probe,
            "si_mode": "live-cl0-cl1",
            "remotepass_dmi_cache": True,
        },
    )()


def write_passing_logs(tmp_path):
    (tmp_path / "qbox-rse.log").write_text(
        "\n".join(
            [
                "Starting TF-M BL1_1",
                "Init SCMI comm to SCP succeeded",
                "RSE to SCP SCMI power on AP succeeded",
                "SCMI Comms subscribed to power state notifications",
                "Measured boot: BL1_2 BL2 SI_CL0 AP_BL2 RT_0 "
                "SECURE_RT_EL3 SECURE_RT_EL1_SPMD BL_33",
                "Jumping to the first image slot",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    (tmp_path / "qbox-secure-console.log").write_text(
        "NOTICE:  BL2:\nNOTICE:  BL31:\nOP-TEE version:\n",
        encoding="utf-8",
    )
    (tmp_path / "qbox-primary-console.log").write_text(
        "\n".join(
            [
                "apollo-fvp login:",
                "~ # echo __QBOX_PROBE_START__",
                "__QBOX_PROBE_START__",
                "arm_si_rproc_modprobe_rc:0",
                "virtio_rpmsg_bus_modprobe_rc:0",
                "rpmsg_net_modprobe_rc:0",
                "rpmsg_device:virtio6.ethsi1.-1.1024:ethsi1",
                "ethsi1_iplink_rc:0",
                "~ # echo __QBOX_PROBE_DONE__",
                "__QBOX_PROBE_DONE__",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    (tmp_path / "qbox-safety-island-cl0.log").write_text(
        "[SI0_PLATFORM] SCP started\n",
        encoding="utf-8",
    )


def test_keep_running_child_status_passes_after_probe_marker(tmp_path):
    runner = load_runner()
    write_passing_logs(tmp_path)

    status = runner.synthesize_keep_running_child_status(
        make_args(tmp_path),
        ["child-runner"],
        child_returncode=None,
    )

    assert status["passed"] is True
    assert status["marker_hits"]["linux_boot"]["apollo-fvp login:"] is True
    assert status["post_login_probe"]["complete"] is True
    assert status["post_login_probe"]["driver_patterns"] == {
        "arm_si_rproc": True,
        "rpmsg": True,
        "hipc_ethsi1": True,
    }
    assert status["scp_service_model"]["strategy"] == "real-si-scp"


def test_keep_running_child_status_waits_for_probe_done_marker(tmp_path):
    runner = load_runner()
    write_passing_logs(tmp_path)
    primary = tmp_path / "qbox-primary-console.log"
    primary.write_text(
        primary.read_text(encoding="utf-8").replace("__QBOX_PROBE_DONE__", ""),
        encoding="utf-8",
    )

    status = runner.synthesize_keep_running_child_status(
        make_args(tmp_path),
        ["child-runner"],
        child_returncode=None,
    )

    assert status["passed"] is False
    assert status["post_login_probe"]["complete"] is False
