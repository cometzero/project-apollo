from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
QBOX_PLATFORM = ROOT / "hsoc-stack/tools/qbox-platform"


def read(relative: str) -> str:
    return (QBOX_PLATFORM / relative).read_text(encoding="utf-8")


def test_fmu_fault_input_records_ordered_json_and_recovery() -> None:
    header = read("systemc-components/zena_fmu/include/zena_fmu.h")

    assert "TargetSignalSocket<bool> fault_in" in header
    assert 'p_fault_input_enabled("fault_input_enabled", false)' in header
    assert 'append_event("source", true)' in header
    assert 'append_event("record", true)' in header
    assert 'append_event("sink_assert"' in header
    assert 'append_event("clear", false)' in header
    assert 'append_event("sink_deassert"' in header
    assert 'append_event("recovery", true)' in header


def test_full_machine_smmu_event_fans_out_to_gic_and_test_fmu() -> None:
    config = read("platforms/apollo/hw-block/config.lua")
    ap_compute = read("platforms/apollo/hw-block/ap_compute.lua")

    assert 'getenv_bool_or("QBOX_APOLLO_FAULT_EVENT_TEST", false)' in config
    assert 'event_irq_target = "&ap_smmu_event_fanout.signal_in"' in config
    assert 'moduletype = "signal_fanout"' in ap_compute
    assert (
        'bind = "&ap_gic.spi_in_65;&ap_smmu_fault_observer.fault_in"'
        in ap_compute
    )
    assert 'fault_source = "ap_smmu_0.irq_eventq"' in ap_compute
    assert 'fault_input_record = 1' in ap_compute
