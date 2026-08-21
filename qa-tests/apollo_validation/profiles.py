from __future__ import annotations

from dataclasses import dataclass
import ipaddress
import json
from pathlib import Path
from typing import TypeAlias


JsonScalar: TypeAlias = str | int | bool | None
JsonValue: TypeAlias = JsonScalar | list["JsonValue"] | dict[str, "JsonValue"]
FvpConfig: TypeAlias = tuple[tuple[str, str], ...]
SI_CL1_UART = "css.smb.si.cluster1_pl011_uart.uart_enable"
FVP_USER_NETWORKING = "ros.virtio_net.hostbridge.userNetworking"
FVP_INTERFACE_NAME = "ros.virtio_net.hostbridge.interfaceName"
FVP_CONFIG_PROFILES = frozenset({"bsp-core", "pfdi-si-cl1", "si-cl1"})
FVP_TAP_NETWORK_PROFILES = frozenset({"platform-devices"})
FVP_TAP_INTERFACE = "apollo-fvp-tap0"
FVP_TAP_HOST_IP = "192.0.2.1"
FVP_TAP_TARGET_IP = "192.0.2.10"
FVP_TAP_PREFIX_LENGTH = 24


class ProfileError(Exception):
    def __init__(self, reason: str) -> None:
        super().__init__(reason)
        self.reason = reason

    def __str__(self) -> str:
        return self.reason


@dataclass(frozen=True, slots=True)
class TestProfile:
    name: str
    path: Path
    selectors: tuple[str, ...]
    oeqa_kind: str
    test_target: str
    timeout_seconds: int
    backend: str
    image_profile: str
    fvp_config: FvpConfig
    fvp_tap_network: "FvpTapNetwork | None"


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

    def runtime_fvp_config(self) -> FvpConfig:
        return (
            (FVP_USER_NETWORKING, "0"),
            (FVP_INTERFACE_NAME, self.interface_name),
        )


def merge_fvp_runtime_config(
    profile_config: FvpConfig,
    tap_network: FvpTapNetwork | None,
) -> FvpConfig:
    network_config = () if tap_network is None else tap_network.runtime_fvp_config()
    merged: list[tuple[str, str]] = []
    selected_keys: set[str] = set()
    for key, value in (*profile_config, *network_config):
        if key in selected_keys:
            raise ProfileError(f"duplicate FVP config key: {key}")
        selected_keys.add(key)
        merged.append((key, value))
    return tuple(merged)


def _mapping(value: JsonValue, field: str) -> dict[str, JsonValue]:
    if not isinstance(value, dict):
        raise ProfileError(f"profile field {field} must be an object")
    return value


def _strings(value: JsonValue, field: str) -> tuple[str, ...]:
    if not isinstance(value, list) or not value or not all(
        isinstance(item, str) and item for item in value
    ):
        raise ProfileError(f"profile field {field} must be a non-empty string list")
    return tuple(_string(item, field) for item in value)


def _string(value: JsonValue, field: str) -> str:
    if not isinstance(value, str) or not value:
        raise ProfileError(f"profile field {field} must be a non-empty string")
    return value


def _positive_int(value: JsonValue, field: str) -> int:
    if type(value) is not int or value <= 0:
        raise ProfileError(f"profile field {field} must be a positive integer")
    return value


def _fvp_config(value: JsonValue, profile_name: str) -> FvpConfig:
    if value is None:
        return ()
    if profile_name not in FVP_CONFIG_PROFILES:
        raise ProfileError(f"profile {profile_name} does not permit FVP config")
    data = _mapping(value, "fvp_config")
    entries: list[tuple[str, str]] = []
    for key, raw_value in data.items():
        if key != SI_CL1_UART:
            raise ProfileError(f"unknown FVP config key: {key}")
        if not isinstance(raw_value, str):
            raise ProfileError(f"FVP config value for {key} must be a string")
        if raw_value != "1":
            raise ProfileError(f"unsafe FVP config value for {key}")
        entries.append((key, raw_value))
    if not entries:
        raise ProfileError("profile field fvp_config must not be empty")
    return tuple(entries)


def _fvp_tap_network(value: JsonValue, profile_name: str) -> FvpTapNetwork | None:
    if value is None:
        if profile_name in FVP_TAP_NETWORK_PROFILES:
            raise ProfileError(f"profile {profile_name} requires FVP TAP network")
        return None
    if profile_name not in FVP_TAP_NETWORK_PROFILES:
        raise ProfileError(f"profile {profile_name} does not permit FVP TAP network")
    data = _mapping(value, "fvp_tap_network")
    expected = {"interface_name", "host_ip", "target_ip", "prefix_length"}
    if set(data) != expected:
        raise ProfileError("FVP TAP network has unknown or missing fields")
    interface_name = _string(data.get("interface_name"), "fvp_tap_network.interface_name")
    host_ip = _string(data.get("host_ip"), "fvp_tap_network.host_ip")
    target_ip = _string(data.get("target_ip"), "fvp_tap_network.target_ip")
    prefix_length = data.get("prefix_length")
    if type(prefix_length) is not int:
        raise ProfileError("FVP TAP network prefix_length must be an integer")
    try:
        host_address = ipaddress.ip_address(host_ip)
        target_address = ipaddress.ip_address(target_ip)
    except ValueError as error:
        raise ProfileError("FVP TAP network addresses must be IPv4") from error
    if (
        not isinstance(host_address, ipaddress.IPv4Address)
        or not isinstance(target_address, ipaddress.IPv4Address)
        or host_address.is_loopback
        or target_address.is_loopback
    ):
        raise ProfileError("FVP TAP network addresses must be non-loopback IPv4")
    if (
        interface_name != FVP_TAP_INTERFACE
        or str(host_address) != FVP_TAP_HOST_IP
        or str(target_address) != FVP_TAP_TARGET_IP
        or prefix_length != FVP_TAP_PREFIX_LENGTH
    ):
        raise ProfileError("FVP TAP network does not match the project-owned contract")
    return FvpTapNetwork(interface_name, str(host_address), str(target_address), prefix_length)


def load_test_profile(
    root: Path,
    name: str,
    backend: str,
    image_profile: str,
) -> TestProfile:
    path = root / "qa-tests/profiles" / f"{name}.yaml"
    try:
        loaded: JsonValue = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as error:
        raise ProfileError(f"unknown test profile: {name}") from error
    except json.JSONDecodeError as error:
        raise ProfileError(f"invalid test profile {path}: {error}") from error
    data = _mapping(loaded, "root")
    if data.get("version") != 1:
        raise ProfileError(f"unsupported test profile version in {path}")
    profile_name = _string(data.get("name"), "name")
    if profile_name != name:
        raise ProfileError(f"profile name {profile_name} does not match {name}")
    compatibility = _mapping(data.get("compatibility"), "compatibility")
    backends = _strings(compatibility.get("backends"), "compatibility.backends")
    images = _strings(compatibility.get("images"), "compatibility.images")
    if backend not in backends:
        raise ProfileError(f"profile {name} does not support backend {backend}")
    if image_profile not in images:
        raise ProfileError(f"profile {name} does not support image {image_profile}")
    oeqa = _mapping(data.get("oeqa"), "oeqa")
    targets = _mapping(data.get("targets"), "targets")
    return TestProfile(
        name=profile_name,
        path=path,
        selectors=_strings(oeqa.get("selectors"), "oeqa.selectors"),
        oeqa_kind=_string(oeqa.get("kind"), "oeqa.kind"),
        test_target=_string(targets.get(backend), f"targets.{backend}"),
        timeout_seconds=_positive_int(
            oeqa.get("timeout_seconds"),
            "oeqa.timeout_seconds",
        ),
        backend=backend,
        image_profile=image_profile,
        fvp_config=_fvp_config(data.get("fvp_config"), profile_name),
        fvp_tap_network=_fvp_tap_network(data.get("fvp_tap_network"), profile_name),
    )
