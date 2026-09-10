from pathlib import Path

from scripts.test.audit_qbox_apollo_ap_memory_map import (
    current_ap_view_bindings,
    current_coverage,
)


ROOT = Path(__file__).resolve().parents[1]


def test_dma_instances_have_separate_ap_ranges() -> None:
    sockets = {s.object_name: s for s in current_coverage(ROOT)}
    bindings = {b.object_name for b in current_ap_view_bindings(ROOT)}
    for name, address in (("dma350_0", 0x31000000),
                          ("dma350_1", 0x31010000)):
        assert sockets[name].address == address
        assert sockets[name].size == 0x10000
        assert name in bindings


def test_dwc_ap_ranges_are_complete_and_non_overlapping() -> None:
    sockets = {
        socket.object_name: socket
        for socket in current_coverage(ROOT)
        if socket.object_name.startswith("ap_dw_")
    }
    expected = {
        **{f"ap_dw_i2c_{index}": (0x30100000 + index * 0x10000, "dw_apb_i2c") for index in range(6)},
        **{f"ap_dw_ssi_{index}": (0x30160000 + index * 0x10000, "dw_apb_ssi") for index in range(4)},
        **{f"ap_dw_uart_{index}": (0x301A0000 + index * 0x10000, "dw_apb_uart") for index in range(4)},
        **{f"ap_dw_i2s_{index}": (0x30200000 + index * 0x10000, "dw_apb_i2s") for index in range(2)},
    }

    assert set(sockets) == set(expected)
    ranges = []
    for name, (address, module) in expected.items():
        socket = sockets[name]
        assert socket.address == address
        assert socket.size == 0x10000
        assert socket.module_type == module
        ranges.append((socket.address, socket.address + socket.size, name))

    for previous, current in zip(sorted(ranges), sorted(ranges)[1:]):
        assert previous[1] <= current[0], (previous, current)


def test_dwc_ap_ranges_are_rebound_to_the_ap_router() -> None:
    bindings = {
        (binding.object_name, binding.socket_name)
        for binding in current_ap_view_bindings(ROOT)
        if binding.object_name.startswith("ap_dw_")
    }
    expected = {
        *((f"ap_dw_i2c_{index}", "target_socket") for index in range(6)),
        *((f"ap_dw_ssi_{index}", "target_socket") for index in range(4)),
        *((f"ap_dw_uart_{index}", "target_socket") for index in range(4)),
        *((f"ap_dw_i2s_{index}", "target_socket") for index in range(2)),
    }
    assert bindings == expected
