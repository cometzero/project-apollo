"""Host-only qualification/readonly-map tests; no FVP behavior claim."""
import importlib.util
from pathlib import Path

PATH = Path(__file__).resolve().parents[1] / 'scripts/debug/probe_fvp_cl1_initial_off.py'
SPEC = importlib.util.spec_from_file_location('ppu_observer', PATH)
observer = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(observer)


def sample(core=0, cluster=0, sys0=8, qualified=True):
    ppu = {f'ap_core{i}_{j}': {'pwsr': 0} for i in range(4) for j in range(4)}
    ppu.update({f'ap_cluster{i}': {'pwsr': 0} for i in range(4)})
    ppu['ap_core0_0']['pwsr'] = core
    ppu['ap_cluster0']['pwsr'] = cluster
    ppu['ap_sys0'] = {'pwsr': sys0}
    return {'qualified': qualified, 'ppu': ppu}


def test_no_initial_reset_off_false_positive():
    cycle = observer.ComputeCycle()
    assert cycle.observe(sample()) is None
    assert cycle.observe(sample(8, 8, qualified=False)) is None
    assert not cycle.boot_seen and not cycle.off_seen


def test_full_compute_cycle_with_sys0_on():
    cycle = observer.ComputeCycle()
    assert cycle.observe(sample(8, 8)) == 'before'
    assert cycle.observe(sample()) == 'compute_off'
    assert cycle.observe(sample(8, 8)) == 'after'
    assert cycle.off_seen and cycle.resumed


def test_missing_or_live_physical_ppu_prevents_off():
    for name in ['ap_core3_3', 'ap_cluster3']:
        for bad in [{'pwsr': 8}, {'error': 'unmapped'}]:
            cycle = observer.ComputeCycle()
            cycle.observe(sample(8, 8))
            value = sample()
            value['ppu'][name] = bad
            assert cycle.observe(value) is None
            assert not cycle.off_seen


def test_sys0_off_is_not_systop_on_qualification():
    cycle = observer.ComputeCycle()
    cycle.observe(sample(8, 8))
    assert cycle.observe(sample(sys0=0)) is None
    assert not cycle.off_seen


class Reader:
    def __init__(self, fail=None):
        self.addresses = []
        self.fail = fail

    def read_memory(self, address, *, memory_space, size, count):
        assert memory_space == 'Physical Memory (Secure)' and count == 1
        self.addresses.append(address)
        if address == self.fail:
            raise RuntimeError('inaccessible')
        return (address & 3).to_bytes(size, 'little')


def test_actual_controller_map_full_assignment_and_read_only():
    reader = Reader()
    data = observer.multiview_snapshot(reader)
    for name, base, count in [('ap', 0xd0770000, 16), ('si', 0x30000000, 5)]:
        registers = data[name]['registers']
        assert data[name]['ownership_complete']
        assert len([k for k in registers if k.startswith('iviewr')]) == 60
        assert len([k for k in registers if k.endswith('_viewr')]) == count
        assert base+0xf608 in reader.addresses
        assert base+0xf6f4 in reader.addresses
        assert data[name]['ownership_sha256']
    assert 0x20800000 not in reader.addresses
    assert 0xd0f70000 in reader.addresses  # AP view1 through the CL0 ATU alias.
    assert 0x30100000 in reader.addresses  # SI CL0 view1, separate controller.
    assert 0x30200000 in reader.addresses  # SI CL1 view2.


def test_failed_assignment_read_has_no_fingerprint_pass():
    data = observer.multiview_snapshot(Reader(fail=0xd077f608))
    assert not data['ap']['ownership_complete']
    assert data['ap']['ownership_sha256'] is None
    assert data['si']['ownership_complete']
