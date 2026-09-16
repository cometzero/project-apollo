import importlib.util
from pathlib import Path


path = Path(__file__).resolve().parents[1] / 'scripts/test/analyze_qbox_i2s_period.py'
spec = importlib.util.spec_from_file_location('i2s_period', path)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def test_pairs_are_per_task_and_missing_events_are_visible():
    result = module.summarize('''
 irq/40-dma-118 [000] D...1 1.000000: irq_enter: probe
 irq/40-dma-122 [000] D...1 1.001000: irq_enter: probe
 irq/40-dma-118 [001] D...1 1.003000: irq_exit: probe
 irq/40-dma-122 [000] D...1 1.005000: irq_exit: probe
 irq/40-dma-122 [000] D...1 1.006000: program_exit: probe
 irq/40-dma-122 [000] D...1 1.007000: program_enter: probe
''')
    assert result['durations']['irq']['count'] == 2
    assert round(result['durations']['irq']['min_ms'], 6) == 3
    assert round(result['durations']['irq']['max_ms'], 6) == 4
    assert result['unmatched_entries'] == 1
    assert result['unmatched_exits'] == 1


def test_empty_trace_does_not_invent_measurements():
    result = module.summarize('# tracer: nop\n')
    assert result['events'] == {}
    assert result['durations']['irq'] == {'count': 0}


def test_pio_receive_is_separate_from_transmit():
    result = module.summarize('''
 arecord-100 [000] D...1 1.000000: receive_enter: probe
 aplay-101 [001] D...1 1.001000: program_enter: probe
 arecord-100 [000] D...1 1.004000: receive_exit: probe
 aplay-101 [001] D...1 1.007000: program_exit: probe
''')
    assert round(result['durations']['receive']['max_ms'], 6) == 4
    assert round(result['durations']['program']['max_ms'], 6) == 6
    assert result['unmatched_entries'] == result['unmatched_exits'] == 0
