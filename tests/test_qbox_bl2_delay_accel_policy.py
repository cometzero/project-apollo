from pathlib import Path
import importlib.util
import sys


ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "scripts/run/run_qbox_apollo_fvp_full.py"


def test_default_delay_acceleration_preserves_si_startup_wait(monkeypatch):
    # Given: the Apollo full-system runner with its default performance preset.
    spec = importlib.util.spec_from_file_location("apollo_full_delay_policy", RUNNER)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    monkeypatch.setattr(sys, "argv", [RUNNER.name, "--check-only"])

    # When: command-line defaults are resolved.
    args = module.parse_args()

    # Then: only the LBIST and MBIST delays are accelerated.
    assert args.rse_bl2_delay_expected_hits == 2
