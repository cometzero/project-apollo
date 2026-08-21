from __future__ import annotations

import json
import os
from typing import Final


type JsonValue = None | bool | int | float | str | list[JsonValue] | dict[str, JsonValue]
SELECTED_FVP_CONFIG_ENV: Final = "APOLLO_VALIDATION_FVP_CONFIG"
SI_CL1_UART: Final = "css.smb.si.cluster1_pl011_uart.uart_enable"
FVP_USER_NETWORKING: Final = "ros.virtio_net.hostbridge.userNetworking"
FVP_INTERFACE_NAME: Final = "ros.virtio_net.hostbridge.interfaceName"
APPROVED_FVP_CONFIG: Final = {
    SI_CL1_UART: "1",
    FVP_USER_NETWORKING: "0",
    FVP_INTERFACE_NAME: "apollo-fvp-tap0",
}


class FvpConfigError(ValueError):
    pass


def fvp_config_assignments(machine: str) -> list[str]:
    raw = os.environ.get(SELECTED_FVP_CONFIG_ENV)
    if raw is None:
        return []
    if machine != "apollo-fvp":
        raise FvpConfigError("FVP config is valid only for apollo-fvp")
    try:
        loaded: JsonValue = json.loads(raw)
    except json.JSONDecodeError as error:
        raise FvpConfigError("FVP config must be a JSON object") from error
    if not isinstance(loaded, dict):
        raise FvpConfigError("FVP config must be a JSON object")
    if not loaded:
        raise FvpConfigError("FVP config must not be empty")
    assignments = [
        'BB_ENV_PASSTHROUGH_ADDITIONS:append = " APOLLO_VALIDATION_FVP_CONFIG"',
        "export APOLLO_VALIDATION_FVP_CONFIG",
    ]
    for key, value in loaded.items():
        expected_value = APPROVED_FVP_CONFIG.get(key)
        if expected_value is None:
            raise FvpConfigError(f"unknown FVP config key: {key}")
        if not isinstance(value, str):
            raise FvpConfigError(f"FVP config value for {key} must be a string")
        if value != expected_value:
            raise FvpConfigError(f"unsafe FVP config value for {key}")
        assignments.append(f'FVP_CONFIG[{key}] = "{value}"')
    return assignments
