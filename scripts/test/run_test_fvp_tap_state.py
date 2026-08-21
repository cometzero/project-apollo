from __future__ import annotations

from dataclasses import dataclass
import hashlib
import re
from pathlib import Path
import shutil
import stat
from typing import Final

from run_test_fvp_tap_contract import (
    DNSMASQ_LEASE_PATH,
    DNSMASQ_PID_PATH,
    FVP_TAP_HOST_IP,
    FVP_TAP_INTERFACE,
    FVP_TAP_NETWORK,
    FVP_TAP_PREFIX_LENGTH,
    FVP_TAP_TARGET_IP,
)


STATE_FIELDS: Final = frozenset(
    {
        "VERSION", "INTERFACE_NAME", "OWNER_UID", "HOST_CIDR", "TARGET_IP",
        "NETWORK_CIDR", "NAT_TABLE", "UPLINK", "IP_FORWARD_PREVIOUS", "NONCE",
        "DNSMASQ_PID", "DNSMASQ_STARTTIME", "DNSMASQ_EXE", "DNSMASQ_ARGV0",
        "DNSMASQ_ARGS_SHA256",
    }
)


@dataclass(frozen=True, slots=True)
class TapNetworkState:
    owner_uid: int
    nonce: str
    pid: int
    start_time: str
    executable: str
    argv_sha256: str
    argv0: str = "dnsmasq"
    uplink: str = ""


def _read_root_owned_state(path: Path) -> dict[str, str] | None:
    try:
        metadata = path.stat()
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError:
        return None
    if metadata.st_uid != 0 or stat.S_IMODE(metadata.st_mode) != 0o644:
        return None
    values: dict[str, str] = {}
    for line in lines:
        if line.count("=") != 1:
            return None
        key, value = line.split("=", maxsplit=1)
        if not key or not value or key in values:
            return None
        values[key] = value
    return values if set(values) == STATE_FIELDS else None


def _load_tap_state(path: Path, expected_owner: int) -> TapNetworkState | None:
    values = _read_root_owned_state(path)
    if values is None or set(values) != STATE_FIELDS:
        return None
    try:
        owner_uid = int(values["OWNER_UID"])
        pid = int(values["DNSMASQ_PID"])
    except ValueError:
        return None
    expected = {
        "VERSION": "1", "INTERFACE_NAME": FVP_TAP_INTERFACE,
        "HOST_CIDR": f"{FVP_TAP_HOST_IP}/{FVP_TAP_PREFIX_LENGTH}",
        "TARGET_IP": FVP_TAP_TARGET_IP, "NETWORK_CIDR": FVP_TAP_NETWORK,
        "NAT_TABLE": "apollo_fvp_tap",
    }
    if (
        any(values[key] != value for key, value in expected.items())
        or owner_uid != expected_owner or pid <= 0
        or not values["DNSMASQ_STARTTIME"].isdigit()
        or re.fullmatch(r"[0-9a-f]{32}", values["NONCE"]) is None
        or not Path(values["DNSMASQ_EXE"]).is_absolute()
        or not values["DNSMASQ_ARGV0"]
        or re.fullmatch(r"[0-9a-f]{64}", values["DNSMASQ_ARGS_SHA256"]) is None
        or re.fullmatch(r"[A-Za-z0-9_.:-]+", values["UPLINK"]) is None
        or values["IP_FORWARD_PREVIOUS"] not in {"0", "1"}
    ):
        return None
    return TapNetworkState(
        owner_uid, values["NONCE"], pid, values["DNSMASQ_STARTTIME"],
        values["DNSMASQ_EXE"], values["DNSMASQ_ARGS_SHA256"],
        values["DNSMASQ_ARGV0"], values["UPLINK"],
    )


def _process_start_time(pid: int) -> str | None:
    try:
        raw = Path(f"/proc/{pid}/stat").read_text(encoding="utf-8")
    except OSError:
        return None
    marker = raw.rfind(")")
    fields = raw[marker + 2 :].split() if marker >= 0 else []
    return fields[19] if len(fields) > 19 and fields[19].isdigit() else None


def _process_argv(pid: int) -> tuple[str, ...] | None:
    try:
        entries = Path(f"/proc/{pid}/cmdline").read_bytes().split(b"\0")
    except OSError:
        return None
    if not entries or entries[-1] != b"":
        return None
    try:
        return tuple(entry.decode("utf-8") for entry in entries[:-1])
    except UnicodeDecodeError:
        return None


def _process_executable(pid: int) -> Path | None:
    try:
        return Path(f"/proc/{pid}/exe").resolve(strict=True)
    except OSError:
        return None


def _expected_dnsmasq_options(state: TapNetworkState) -> tuple[str, ...]:
    return (
        "--keep-in-foreground", f"--interface={FVP_TAP_INTERFACE}", "--bind-interfaces",
        "--except-interface=lo",
        f"--dhcp-range={FVP_TAP_TARGET_IP},{FVP_TAP_TARGET_IP},255.255.255.0,1h",
        f"--dhcp-option=option:router,{FVP_TAP_HOST_IP}",
        f"--dhcp-option=option:dns-server,{FVP_TAP_HOST_IP}",
        f"--pid-file={DNSMASQ_PID_PATH}", f"--dhcp-leasefile={DNSMASQ_LEASE_PATH}",
        f"--dhcp-option-force=224,{state.nonce}",
    )


def _process_identity_matches(state: TapNetworkState) -> bool:
    executable = shutil.which("dnsmasq")
    if executable is None or _process_start_time(state.pid) != state.start_time:
        return False
    process_executable = _process_executable(state.pid)
    if process_executable is None:
        return False
    try:
        expected = Path(executable).resolve(strict=True)
        persisted = Path(state.executable).resolve(strict=True)
    except OSError:
        return False
    argv = _process_argv(state.pid)
    if argv is None:
        return False
    digest = hashlib.sha256(b"\0".join(item.encode("utf-8") for item in argv)).hexdigest()
    return (
        process_executable == expected == persisted
        and argv == (state.argv0, *_expected_dnsmasq_options(state))
        and digest == state.argv_sha256
    )


def unprivileged_identity_matches(state: TapNetworkState) -> bool:
    if _process_start_time(state.pid) != state.start_time:
        return False
    argv = _process_argv(state.pid)
    if argv is None:
        return False
    digest = hashlib.sha256(b"\0".join(item.encode("utf-8") for item in argv)).hexdigest()
    return argv == (state.argv0, *_expected_dnsmasq_options(state)) and digest == state.argv_sha256


def authenticated_tap_state(path: Path, expected_owner: int) -> TapNetworkState | None:
    state = _load_tap_state(path, expected_owner)
    return state if state is not None and _process_identity_matches(state) else None
