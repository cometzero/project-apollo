from __future__ import annotations

import argparse
from dataclasses import dataclass
import hashlib
import json
import os
import subprocess
import sys

from run_test_fvp_tap_contract import (
    ATTESTATION_PATH,
    FVP_TAP_HOST_IP,
    FVP_TAP_INTERFACE,
    FVP_TAP_NETWORK,
    FVP_TAP_PREFIX_LENGTH,
    FVP_TAP_TARGET_IP,
    FvpTapNetwork,
    FvpTapNetworkError,
    JsonValue,
    SETUP_HINT,
    STATE_PATH,
    selected_tap_network,
)
from run_test_fvp_tap_state import (
    TapNetworkState,
    _load_tap_state,
    authenticated_tap_state,
    unprivileged_identity_matches,
)
from run_test_fvp_tap_attestation import AttestationState, attestation_is_fresh, write_attestation


@dataclass(frozen=True, slots=True)
class TapNetworkPreflight:
    interface_name: str
    host_ip: str
    target_ip: str
    reason: str | None
    hint: str


def _command_output(argv: list[str]) -> tuple[int, str, str]:
    try:
        completed = subprocess.run(
            argv, check=False, capture_output=True, text=True, timeout=5
        )
    except FileNotFoundError:
        return 127, "", "command unavailable"
    except subprocess.TimeoutExpired:
        return 124, "", "command timed out"
    return completed.returncode, completed.stdout, completed.stderr


def _json_list(raw: str) -> list[dict[str, JsonValue]]:
    try:
        loaded: JsonValue = json.loads(raw)
    except json.JSONDecodeError:
        return []
    return [item for item in loaded if isinstance(item, dict)] if isinstance(loaded, list) else []


def _strings(value: JsonValue) -> list[str]:
    return [item for item in value if isinstance(item, str)] if isinstance(value, list) else []


def _is_ipv4_entry(address: dict[str, JsonValue]) -> bool:
    local = address.get("local")
    return address.get("family") == "inet" or isinstance(local, str) and "." in local


def _objects(value: JsonValue) -> list[dict[str, JsonValue]]:
    return [item for item in value if isinstance(item, dict)] if isinstance(value, list) else []


def _interface_is_up(network: FvpTapNetwork) -> bool:
    rc, stdout, _stderr = _command_output(
        ["ip", "-j", "link", "show", "dev", network.interface_name]
    )
    links = _json_list(stdout) if rc == 0 else []
    return (
        len(links) == 1
        and links[0].get("ifname") == network.interface_name
        and "UP" in _strings(links[0].get("flags"))
    )


def _interface_is_owned(network: FvpTapNetwork, expected_owner: int) -> bool:
    rc, stdout, _stderr = _command_output(
        ["ip", "tuntap", "show", "dev", network.interface_name]
    )
    descriptions = (
        f"{network.interface_name}: tap persist user {expected_owner}",
        f"{network.interface_name}: tap vnet_hdr persist user {expected_owner}",
    )
    return rc == 0 and stdout.splitlines() in ([value] for value in descriptions)


def _interface_has_host_address(network: FvpTapNetwork) -> bool:
    rc, stdout, _stderr = _command_output(
        ["ip", "-j", "addr", "show", "dev", network.interface_name]
    )
    entries = _json_list(stdout) if rc == 0 else []
    if len(entries) != 1:
        return False
    addresses = entries[0].get("addr_info")
    if not isinstance(addresses, list):
        return False
    ipv4 = [
        (address.get("local"), address.get("prefixlen"))
        for address in addresses
        if isinstance(address, dict)
        and _is_ipv4_entry(address)
    ]
    return ipv4 == [(network.host_ip, network.prefix_length)]


def _ip_forward_is_enabled() -> bool:
    rc, stdout, _stderr = _command_output(["sysctl", "-n", "net.ipv4.ip_forward"])
    return rc == 0 and stdout.strip() == "1"


def _expected_nat_expr(uplink: str) -> list[dict[str, JsonValue]]:
    return [
        {
            "match": {
                "op": "==",
                "left": {"payload": {"protocol": "ip", "field": "saddr"}},
                "right": {
                    "prefix": {
                        "addr": FVP_TAP_NETWORK.rsplit("/", maxsplit=1)[0],
                        "len": FVP_TAP_PREFIX_LENGTH,
                    }
                },
            }
        },
        {
            "match": {
                "op": "==",
                "left": {"meta": {"key": "oifname"}},
                "right": uplink,
            }
        },
        {"masquerade": None},
    ]


def _nft_semantic_digest(uplink: str) -> str:
    semantic = {
        "table": {"family": "ip", "name": "apollo_fvp_tap"},
        "chain": {"family": "ip", "table": "apollo_fvp_tap", "name": "postrouting", "type": "nat", "hook": "postrouting", "prio": "srcnat", "policy": "accept"},
        "expr": _expected_nat_expr(uplink),
    }
    payload = json.dumps(semantic, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(payload).hexdigest()


def _attestation_state(state: TapNetworkState) -> AttestationState:
    return AttestationState(
        state_sha256=hashlib.sha256(STATE_PATH.read_bytes()).hexdigest(),
        pid=state.pid,
        start_time=state.start_time,
        nonce=state.nonce,
        argv_sha256=state.argv_sha256,
        nft_semantic_digest=_nft_semantic_digest(state.uplink),
    )


def _metadata_only(value: dict[str, JsonValue], required: set[str]) -> bool:
    return set(value) <= (required | {"handle"}) and required <= set(value)


def _nft_contract_matches(state: TapNetworkState) -> bool:
    rc, stdout, _stderr = _command_output(
        ["nft", "-j", "list", "table", "ip", "apollo_fvp_tap"]
    )
    try:
        loaded: JsonValue = json.loads(stdout) if rc == 0 else None
    except json.JSONDecodeError:
        return False
    if not isinstance(loaded, dict) or not isinstance(loaded.get("nftables"), list):
        return False
    entries = _objects(loaded["nftables"])
    tables = [item["table"] for item in entries if isinstance(item, dict) and isinstance(item.get("table"), dict)]
    chains = [item["chain"] for item in entries if isinstance(item, dict) and isinstance(item.get("chain"), dict)]
    rules = [item["rule"] for item in entries if isinstance(item, dict) and isinstance(item.get("rule"), dict)]
    if len(tables) != 1 or len(chains) != 1 or len(rules) != 1:
        return False
    table, chain, rule = tables[0], chains[0], rules[0]
    if not isinstance(table, dict) or not isinstance(chain, dict) or not isinstance(rule, dict):
        return False
    valid_chain = (
        _metadata_only(chain, {"family", "table", "name", "type", "hook", "prio", "policy"})
        and chain.get("family") == "ip" and chain.get("table") == "apollo_fvp_tap"
        and chain.get("name") == "postrouting" and chain.get("type") == "nat"
        and chain.get("hook") == "postrouting" and chain.get("prio") in {"srcnat", 100}
        and chain.get("policy") == "accept"
    )
    expression = rule.get("expr")
    return (
        _metadata_only(table, {"family", "name"})
        and table.get("family") == "ip" and table.get("name") == "apollo_fvp_tap"
        and valid_chain and rule.get("family") == "ip"
        and _metadata_only(rule, {"family", "table", "chain", "expr"})
        and rule.get("table") == "apollo_fvp_tap" and rule.get("chain") == "postrouting"
        and expression == _expected_nat_expr(state.uplink)
    )


def verify_tap_contract(expected_owner: int) -> bool:
    network = FvpTapNetwork(
        FVP_TAP_INTERFACE, FVP_TAP_HOST_IP, FVP_TAP_TARGET_IP, FVP_TAP_PREFIX_LENGTH
    )
    state = authenticated_tap_state(STATE_PATH, expected_owner)
    if state is None:
        return False
    checks = (
        _interface_is_up(network),
        _interface_is_owned(network, expected_owner),
        _interface_has_host_address(network),
        _ip_forward_is_enabled(),
        _nft_contract_matches(state),
    )
    return all(checks)


def verify_unprivileged_contract(expected_owner: int) -> bool:
    state = _load_tap_state(STATE_PATH, expected_owner)
    if state is None:
        return False
    try:
        attestation = _attestation_state(state)
    except OSError:
        return False
    network = FvpTapNetwork(
        FVP_TAP_INTERFACE, FVP_TAP_HOST_IP, FVP_TAP_TARGET_IP, FVP_TAP_PREFIX_LENGTH
    )
    checks = (
        attestation_is_fresh(ATTESTATION_PATH, STATE_PATH, attestation),
        unprivileged_identity_matches(state),
        _interface_is_up(network),
        _interface_is_owned(network, expected_owner),
        _interface_has_host_address(network),
        _ip_forward_is_enabled(),
    )
    return all(checks)


def tap_network_preflight() -> TapNetworkPreflight:
    try:
        network = selected_tap_network()
    except FvpTapNetworkError:
        return TapNetworkPreflight(FVP_TAP_INTERFACE, FVP_TAP_HOST_IP, FVP_TAP_TARGET_IP, "blocked_fvp_tap_network_unavailable", SETUP_HINT)
    if network is None:
        return TapNetworkPreflight("", "", "", None, "")
    valid = verify_unprivileged_contract(os.getuid())
    return TapNetworkPreflight(
        network.interface_name, network.host_ip, network.target_ip,
        None if valid else "blocked_fvp_tap_network_unavailable", SETUP_HINT,
    )


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Verify the Apollo FVP TAP contract")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--verify", action="store_true")
    group.add_argument("--verify-process", action="store_true")
    group.add_argument("--attest", action="store_true")
    parser.add_argument("--owner-uid", type=int, required=True)
    return parser.parse_args()


def main() -> int:
    args = _parse_args()
    if args.verify_process:
        passed = authenticated_tap_state(STATE_PATH, args.owner_uid) is not None
    else:
        passed = verify_tap_contract(args.owner_uid)
    if passed and args.attest:
        state = _load_tap_state(STATE_PATH, args.owner_uid)
        if state is None:
            passed = False
        else:
            write_attestation(ATTESTATION_PATH, _attestation_state(state))
    if passed:
        print("FVP TAP contract verified")
        return 0
    print("blocked_fvp_tap_network_unavailable", file=sys.stderr)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
