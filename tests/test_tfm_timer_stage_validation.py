import importlib.util
from pathlib import Path

spec = importlib.util.spec_from_file_location(
    "timer_stages", Path(__file__).resolve().parents[1] / "scripts/test/validate_tfm_timer_stages.py")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def complete_log():
    return "\n".join(
        f"APOLLO_TIMER_TEST stage={stage} timer={timer} result=PASS start=10 end=20 spins=4 freq=125000000 pending=1 core_hz=100000000"
        for stage in module.STAGES for timer in module.TIMERS)


def test_complete_matrix_and_missing_stage():
    text = complete_log()
    assert module.validate(text)["passed"]
    assert not module.validate(text.rsplit("\n", 1)[0])["passed"]
    assert not module.validate("")["passed"]


def test_failure_duplicate_and_invalid_counter():
    text = complete_log()
    assert not module.validate(text.replace("result=PASS", "result=FAIL", 1))["passed"]
    assert not module.validate(text + "\n" + text.splitlines()[0])["passed"]
    assert not module.validate(text.replace("end=20", "end=10"))["passed"]
    assert not module.validate(text.replace("freq=125000000", "freq=32000000"))["passed"]
    assert not module.validate(text.replace("pending=1", "pending=0"))["passed"]
