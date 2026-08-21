from __future__ import annotations

from run_test_fvp_tap_contract import JsonValue, selected_tap_network, tap_network_bitbake_assignments
Manifest = dict[str, JsonValue]


def device_assignments(
    manifest: Manifest,
    scoped_assignments,
) -> list[str]:
    devices = manifest.get("test_fvp_devices")
    if not isinstance(devices, list):
        return []
    values = [device for device in devices if isinstance(device, str)]
    return scoped_assignments("TEST_FVP_DEVICES", " ".join(values), manifest) if values else []


def tap_network_values(machine: str) -> tuple[list[str], str, str] | None:
    network = selected_tap_network()
    if network is None:
        return None
    return (tap_network_bitbake_assignments(machine), network.target_ip, network.host_ip)
