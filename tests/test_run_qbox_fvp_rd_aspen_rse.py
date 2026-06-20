from pathlib import Path
import importlib.util
from types import SimpleNamespace
import sys


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/run/run_qbox_fvp_rd_aspen_rse.py"


def load_runner():
    spec = importlib.util.spec_from_file_location("rd_aspen_runner", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_strip_runner_control_env_keeps_paths_out_of_qbox_env():
    runner = load_runner()
    env = {
        "QBOX_RDASPEN_RESULT_PATH": "result.json",
        "QBOX_RDASPEN_SUMMARY_PATH": "summary.txt",
        "QBOX_RDASPEN_RSE_ROM": "rse-rom-image.img",
    }

    stripped = runner.strip_runner_control_env(env)

    assert stripped is env
    assert "QBOX_RDASPEN_RESULT_PATH" not in stripped
    assert "QBOX_RDASPEN_SUMMARY_PATH" not in stripped
    assert stripped["QBOX_RDASPEN_RSE_ROM"] == "rse-rom-image.img"


def test_apply_rse_cpu_backend_env_defaults_to_remote(tmp_path):
    runner = load_runner()
    args = SimpleNamespace(rse_cpu_mode="remote", remotepass_dmi_cache=True)
    env = {}

    runner.apply_rse_cpu_backend_env(env, args, tmp_path)

    assert env["QBOX_RSE_CPU_MODE"] == "remote"
    assert env["QBOX_REMOTE_CPU_EXEC"] == str((tmp_path / "apollo_rse_remote_cpu").resolve())
    assert runner.remotepass_dmi_cache_result(args) == {
        "enabled": True,
        "requested": True,
        "rse_cpu_mode": "remote",
    }


def test_apply_rse_cpu_backend_env_inprocess_removes_remote_exec(tmp_path):
    runner = load_runner()
    args = SimpleNamespace(rse_cpu_mode="inprocess", remotepass_dmi_cache=True)
    env = {"QBOX_REMOTE_CPU_EXEC": "ambient-remote-cpu"}

    runner.apply_rse_cpu_backend_env(env, args, tmp_path)

    assert env == {"QBOX_RSE_CPU_MODE": "inprocess"}
    assert runner.remotepass_dmi_cache_result(args) == {
        "enabled": False,
        "requested": True,
        "rse_cpu_mode": "inprocess",
    }


def test_apply_rse_cpu_backend_env_rejects_invalid_mode(tmp_path):
    runner = load_runner()
    args = SimpleNamespace(rse_cpu_mode="bad", remotepass_dmi_cache=False)

    try:
        runner.apply_rse_cpu_backend_env({}, args, tmp_path)
    except ValueError as exc:
        assert str(exc) == "QBOX_RSE_CPU_MODE must be remote or inprocess"
    else:
        raise AssertionError("invalid RSE CPU mode was accepted")


def test_apply_rse_cpu_backend_env_rejects_internal_local_alias(tmp_path):
    runner = load_runner()
    args = SimpleNamespace(rse_cpu_mode="local", remotepass_dmi_cache=False)

    try:
        runner.apply_rse_cpu_backend_env({}, args, tmp_path)
    except ValueError as exc:
        assert str(exc) == "QBOX_RSE_CPU_MODE must be remote or inprocess"
    else:
        raise AssertionError("internal RSE CPU mode alias was accepted")
