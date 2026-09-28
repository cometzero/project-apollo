import importlib.util
from pathlib import Path

spec = importlib.util.spec_from_file_location('telemetry', Path(__file__).resolve().parents[1] / 'scripts/autosd_dashboard/telemetry.py')
telemetry = importlib.util.module_from_spec(spec)
spec.loader.exec_module(telemetry)


def test_cpu_delta_not_cumulative_or_host_usage():
    old = {'boot_id': 'a', 'cpu_ticks': {'cpu0': [10, 0, 10, 80, 0, 0, 0, 0]}}
    new = {'boot_id': 'a', 'cpu_ticks': {'cpu0': [20, 0, 20, 100, 0, 0, 0, 0]}}
    assert telemetry.rates(new, old)[0]['utilization_pct'] == 50
    assert telemetry.rates(new, {})[0]['utilization_pct'] is None
    old['boot_id'] = 'b'
    assert telemetry.rates(new, old)[0]['utilization_pct'] is None


def test_counter_reset_unavailable_not_negative():
    old = {'boot_id': 'a', 'cpu_ticks': {'cpu0': [20] * 8}}
    new = {'boot_id': 'a', 'cpu_ticks': {'cpu0': [10] * 8}}
    assert telemetry.rates(new, old)[0]['utilization_pct'] is None


def test_cgroup_cores_and_missing_metrics():
    old = {'boot_id': 'a', 'guest_monotonic': 10, 'subsystems': [
        {'id': 'qm', 'metrics': {'cpu.stat': 'usage_usec 1000000'}}]}
    new = {'boot_id': 'a', 'guest_monotonic': 12, 'subsystems': [
        {'id': 'qm', 'metrics': {'cpu.stat': 'usage_usec 4000000'}},
        {'id': 'absent', 'metrics': {}}]}
    telemetry.rates(new, old)
    assert new['subsystems'][0]['cpu_cores'] == 1.5
    assert new['subsystems'][1]['cpu_cores'] is None
