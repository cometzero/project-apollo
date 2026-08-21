from __future__ import annotations

import argparse
import os
from pathlib import Path
import secrets
import signal
import subprocess
import sys
import time

from fvp_tap_lifecycle import ChildIdentity, ManagedChild


ROOT = Path(__file__).resolve().parents[2]
VALIDATOR = ROOT / "scripts/test/run_test_fvp_tap_network.py"
INTERFACE = "apollo-fvp-tap0"
HOST_CIDR = "192.0.2.1/24"
HOST_IP = "192.0.2.1"
TARGET_IP = "192.0.2.10"
NETWORK_CIDR = "192.0.2.0/24"
NFT_TABLE = "apollo_fvp_tap"
STATE = Path("/run/apollo-fvp-tap-network.state")
PID = Path("/run/apollo-fvp-tap-network-dnsmasq.pid")
LEASE = Path("/run/apollo-fvp-tap-network.leases")
ATTESTATION = Path("/run/apollo-fvp-tap-network.attestation.json")


def _run(argv: list[str], capture: bool = False) -> subprocess.CompletedProcess[str]:
    return subprocess.run(argv, check=True, text=True, capture_output=capture)


def _owner() -> int:
    raw = os.environ.get("SUDO_UID", "")
    if not raw.isdigit():
        raise RuntimeError("setup must be invoked through sudo by the FVP runner user")
    return int(raw)


def _validator(owner: int, mode: str) -> bool:
    return subprocess.run(
        [sys.executable, str(VALIDATOR), mode, "--owner-uid", str(owner)],
        check=False,
    ).returncode == 0


def _uplink() -> str:
    routes = _run(["ip", "-j", "route", "show", "default"], capture=True).stdout
    import json

    data = json.loads(routes)
    for route in data:
        device = route.get("dev")
        if isinstance(device, str) and device:
            return device
    raise RuntimeError("no default uplink route")


def _state_text(owner: int, uplink: str, previous: str, identity: ChildIdentity) -> str:
    nonce = next(
        value.removeprefix("--dhcp-option-force=224,")
        for value in identity.argv
        if value.startswith("--dhcp-option-force=224,")
    )
    values = {
        "VERSION": "1", "INTERFACE_NAME": INTERFACE, "OWNER_UID": str(owner),
        "HOST_CIDR": HOST_CIDR, "TARGET_IP": TARGET_IP, "NETWORK_CIDR": NETWORK_CIDR,
        "NAT_TABLE": NFT_TABLE, "UPLINK": uplink, "IP_FORWARD_PREVIOUS": previous,
        "NONCE": nonce, "DNSMASQ_PID": str(identity.pid),
        "DNSMASQ_STARTTIME": identity.start_time, "DNSMASQ_EXE": str(identity.executable),
        "DNSMASQ_ARGV0": identity.argv[0], "DNSMASQ_ARGS_SHA256": identity.argv_sha256,
    }
    return "".join(f"{key}={value}\n" for key, value in values.items())


def _dnsmasq_argv(nonce: str) -> list[str]:
    return [
        "dnsmasq", "--keep-in-foreground", f"--interface={INTERFACE}",
        "--bind-interfaces", "--except-interface=lo",
        f"--dhcp-range={TARGET_IP},{TARGET_IP},255.255.255.0,1h",
        f"--dhcp-option=option:router,{HOST_IP}",
        f"--dhcp-option=option:dns-server,{HOST_IP}", f"--pid-file={PID}",
        f"--dhcp-leasefile={LEASE}", f"--dhcp-option-force=224,{nonce}",
    ]


def _cleanup_host(previous: str) -> None:
    for argv in (["nft", "delete", "table", "ip", NFT_TABLE], ["ip", "link", "delete", "dev", INTERFACE]):
        subprocess.run(argv, check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    _run(["sysctl", "-w", f"net.ipv4.ip_forward={previous}"])
    try:
        ATTESTATION.unlink()
    except FileNotFoundError:
        pass


def setup() -> int:
    owner = _owner()
    interface_exists = Path(f"/sys/class/net/{INTERFACE}").exists()
    if interface_exists or STATE.exists():
        if interface_exists and STATE.is_file() and _validator(owner, "--attest"):
            print(f"already configured {INTERFACE} for UID {owner}")
            return 0
        raise RuntimeError("blocked_fvp_tap_network_unavailable: partial or foreign state")
    uplink = _uplink()
    previous = _run(["sysctl", "-n", "net.ipv4.ip_forward"], capture=True).stdout.strip()
    child: ManagedChild | None = None
    try:
        _run(["ip", "tuntap", "add", "dev", INTERFACE, "mode", "tap", "user", str(owner)])
        _run(["ip", "addr", "add", HOST_CIDR, "dev", INTERFACE])
        _run(["ip", "link", "set", "dev", INTERFACE, "up"])
        _run(["sysctl", "-w", "net.ipv4.ip_forward=1"])
        _run(["nft", "add", "table", "ip", NFT_TABLE])
        _run(["nft", "add", "chain", "ip", NFT_TABLE, "postrouting", "{", "type", "nat", "hook", "postrouting", "priority", "srcnat", ";", "policy", "accept", ";", "}"])
        _run(["nft", "add", "rule", "ip", NFT_TABLE, "postrouting", "ip", "saddr", NETWORK_CIDR, "oifname", uplink, "masquerade"])
        child = ManagedChild(_dnsmasq_argv(secrets.token_hex(16)), PID, LEASE, STATE)
        child.run(lambda identity: _state_text(owner, uplink, previous, identity), lambda _stage: None)
        if not _validator(owner, "--attest"):
            raise RuntimeError("dnsmasq identity could not be authenticated")
    except (OSError, RuntimeError, subprocess.CalledProcessError):
        if child is not None:
            child.cleanup()
        _cleanup_host(previous)
        raise
    print(f"configured {INTERFACE}: host={HOST_CIDR} target={TARGET_IP} uplink={uplink}")
    return 0


def teardown() -> int:
    owner = _owner()
    if not STATE.is_file():
        print("no project-owned TAP state exists")
        return 0
    if not _validator(owner, "--verify-process"):
        raise RuntimeError("blocked_fvp_tap_network_unavailable: refusing unauthenticated cleanup")
    values = dict(line.split("=", maxsplit=1) for line in STATE.read_text(encoding="utf-8").splitlines())
    if PID.read_text(encoding="utf-8").strip() != values["DNSMASQ_PID"]:
        raise RuntimeError("blocked_fvp_tap_network_unavailable: dnsmasq pidfile mismatch")
    os.kill(int(values["DNSMASQ_PID"]), signal.SIGTERM)
    for _ in range(50):
        try:
            os.kill(int(values["DNSMASQ_PID"]), 0)
        except ProcessLookupError:
            break
        time.sleep(0.1)
    _cleanup_host(values["IP_FORWARD_PREVIOUS"])
    for path in (PID, LEASE, STATE, ATTESTATION):
        try:
            path.unlink()
        except FileNotFoundError:
            continue
    print(f"removed project-owned {INTERFACE} network state")
    return 0


def status() -> int:
    owner = _owner()
    if not _validator(owner, "--attest"):
        raise RuntimeError("blocked_fvp_tap_network_unavailable")
    print("FVP TAP contract verified")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Configure the Apollo FVP TAP network")
    parser.add_argument("action", choices=("setup", "teardown", "status"))
    args = parser.parse_args()
    if os.geteuid() != 0:
        raise RuntimeError("setup, teardown, and status require root; use sudo")
    return {"setup": setup, "teardown": teardown, "status": status}[args.action]()


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (RuntimeError, subprocess.CalledProcessError) as error:
        print(f"error: {error}", file=sys.stderr)
        raise SystemExit(65)
