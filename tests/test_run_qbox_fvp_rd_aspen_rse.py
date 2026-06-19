from pathlib import Path
import importlib.util
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
