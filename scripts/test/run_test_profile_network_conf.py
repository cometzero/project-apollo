from __future__ import annotations

type JsonValue = None | bool | int | float | str | list[JsonValue] | dict[str, JsonValue]
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
