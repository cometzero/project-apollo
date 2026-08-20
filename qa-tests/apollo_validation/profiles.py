from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
from typing import TypeAlias


JsonScalar: TypeAlias = str | int | bool | None
JsonValue: TypeAlias = JsonScalar | list["JsonValue"] | dict[str, "JsonValue"]
FvpConfig: TypeAlias = tuple[tuple[str, str], ...]
SI_CL1_UART = "css.smb.si.cluster1_pl011_uart.uart_enable"
FVP_CONFIG_PROFILES = frozenset({"bsp-core", "si-cl1"})


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
    )
