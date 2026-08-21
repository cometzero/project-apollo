from __future__ import annotations

from dataclasses import dataclass
import ipaddress
import json
import os
from pathlib import Path
from typing import Final, TypeAlias


JsonValue: TypeAlias = None | bool | int | float | str | list["JsonValue"] | dict[str, "JsonValue"]
FVP_TAP_NETWORK_ENV: Final = "APOLLO_VALIDATION_FVP_TAP_NETWORK"
FVP_TAP_INTERFACE: Final = "apollo-fvp-tap0"
FVP_TAP_HOST_IP: Final = "192.0.2.1"
FVP_TAP_TARGET_IP: Final = "192.0.2.10"
FVP_TAP_PREFIX_LENGTH: Final = 24
FVP_TAP_NETWORK: Final = "192.0.2.0/24"
FVP_USER_NETWORKING_KEY: Final = "ros.virtio_net.hostbridge.userNetworking"
FVP_INTERFACE_NAME_KEY: Final = "ros.virtio_net.hostbridge.interfaceName"
SETUP_HINT: Final = (
    "sudo scripts/setup/fvp_tap_network.sh setup && "
    "sudo scripts/setup/fvp_tap_network.sh status"
)
STATE_PATH: Final = Path("/run/apollo-fvp-tap-network.state")
DNSMASQ_PID_PATH: Final = Path("/run/apollo-fvp-tap-network-dnsmasq.pid")
DNSMASQ_LEASE_PATH: Final = Path("/run/apollo-fvp-tap-network.leases")
ATTESTATION_PATH: Final = Path("/run/apollo-fvp-tap-network.attestation.json")


class FvpTapNetworkError(ValueError):
    pass


@dataclass(frozen=True, slots=True)
class FvpTapNetwork:
    interface_name: str
    host_ip: str
    target_ip: str
    prefix_length: int

    def as_json(self) -> dict[str, JsonValue]:
        return {
            "interface_name": self.interface_name,
            "host_ip": self.host_ip,
            "target_ip": self.target_ip,
            "prefix_length": self.prefix_length,
        }


def _error(message: str) -> FvpTapNetworkError:
    return FvpTapNetworkError(f"FVP TAP network {message}")


def _mapping(value: JsonValue) -> dict[str, JsonValue]:
    if not isinstance(value, dict):
        raise _error("must be a JSON object")
    return value


def _string(data: dict[str, JsonValue], field: str) -> str:
    value = data.get(field)
    if not isinstance(value, str) or not value:
        raise _error(f"field {field} must be a non-empty string")
    return value


def _ipv4(value: str, field: str) -> str:
    try:
        address = ipaddress.ip_address(value)
    except ValueError as error:
        raise _error(f"field {field} must be an IPv4 address") from error
    if not isinstance(address, ipaddress.IPv4Address) or address.is_loopback:
        raise _error(f"field {field} must be a non-loopback IPv4 address")
    return str(address)


def parse_tap_network(raw: str | None) -> FvpTapNetwork | None:
    if raw is None:
        return None
    try:
        loaded: JsonValue = json.loads(raw)
    except json.JSONDecodeError as error:
        raise _error("must be valid JSON") from error
    data = _mapping(loaded)
    expected = {"interface_name", "host_ip", "target_ip", "prefix_length"}
    if set(data) != expected:
        raise _error("has unknown or missing fields")
    interface_name = _string(data, "interface_name")
    host_ip = _ipv4(_string(data, "host_ip"), "host_ip")
    target_ip = _ipv4(_string(data, "target_ip"), "target_ip")
    prefix_length = data.get("prefix_length")
    if type(prefix_length) is not int:
        raise _error("field prefix_length must be an integer")
    if (
        interface_name != FVP_TAP_INTERFACE
        or host_ip != FVP_TAP_HOST_IP
        or target_ip != FVP_TAP_TARGET_IP
        or prefix_length != FVP_TAP_PREFIX_LENGTH
    ):
        raise _error("does not match the project-owned contract")
    return FvpTapNetwork(interface_name, host_ip, target_ip, prefix_length)


def selected_tap_network() -> FvpTapNetwork | None:
    return parse_tap_network(os.environ.get(FVP_TAP_NETWORK_ENV))


def tap_network_bitbake_assignments(machine: str) -> list[str]:
    network = selected_tap_network()
    if network is None:
        return []
    if machine != "apollo-fvp":
        raise _error("is valid only for apollo-fvp")
    return [
        f'BB_ENV_PASSTHROUGH_ADDITIONS:append = " {FVP_TAP_NETWORK_ENV}"',
        f"export {FVP_TAP_NETWORK_ENV}",
        f'FVP_CONFIG[{FVP_USER_NETWORKING_KEY}] = "0"',
        f'FVP_CONFIG[{FVP_INTERFACE_NAME_KEY}] = "{network.interface_name}"',
    ]
