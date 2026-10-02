"""CPU cost must be normalized against both host and simulation time."""

import pytest

from scripts.test.measure_qbox_pfdi_load import proc_stat, summarize


def snapshot(time, ticks, start=7):
    thread = {"cpu_ticks": ticks, "start_ticks": start,
              "voluntary_ctxt_switches": ticks * 2,
              "nonvoluntary_ctxt_switches": ticks}
    return {"monotonic": time, "process": thread, "threads": {"23": thread}}


def test_cpu_cost_uses_simulated_time_and_one_host_cpu():
    result = summarize(snapshot(10, 100), snapshot(30, 400), 5, {"ap": [23]}, 100)
    assert result["process"]["host_cpu_percent"] == 15
    assert result["domains"]["ap"]["cpu_seconds_per_sim_second"] == .6
    assert result["sim_seconds_per_host_second"] == .25
    assert result["domains"]["ap"]["voluntary_context_switches"] == 600


def test_reused_pid_and_stopped_simulation_rejected():
    with pytest.raises(RuntimeError, match="identity changed"):
        summarize(snapshot(10, 100), snapshot(30, 400, start=8), 5, {"ap": [23]}, 100)
    with pytest.raises(RuntimeError, match="clocks must advance"):
        summarize(snapshot(10, 100), snapshot(30, 400), 0, {"ap": [23]}, 100)


def test_proc_stat_handles_spaces_and_parentheses(tmp_path):
    fields = ["0"] * 20
    fields[11], fields[12], fields[19] = "4", "7", "19"
    path = tmp_path / "stat"
    path.write_text("23 (CPU 0 (TCG)) " + " ".join(fields))
    assert proc_stat(path) == {"comm": "CPU 0 (TCG)", "cpu_ticks": 11,
                               "user_ticks": 4, "system_ticks": 7,
                               "start_ticks": 19}
