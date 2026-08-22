from __future__ import annotations

import json
from dataclasses import replace
import hashlib
from pathlib import Path
import sys

import pytest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts/test"))

from run_test_fvp_tap_contract import (  # noqa: E402
    FVP_TAP_NETWORK_ENV,
    FvpTapNetwork,
    JsonValue,
)
from run_test_fvp_tap_state import (  # noqa: E402
    TapNetworkState,
    _expected_dnsmasq_options,
    _process_identity_matches,
    authenticated_tap_state,
)
from run_test_fvp_tap_network import (  # noqa: E402
    _interface_is_owned,
    _nft_contract_matches,
    tap_network_preflight,
    verify_unprivileged_contract,
    verify_tap_contract,
)


NETWORK = {
    "interface_name": "apollo-fvp-tap0",
    "host_ip": "192.0.2.1",
    "target_ip": "192.0.2.10",
    "prefix_length": 24,
}


@pytest.mark.parametrize(
    ("output", "expected"),
    [
        ("apollo-fvp-tap0: tap persist user 1000\n", True),
        ("apollo-fvp-tap0: tap vnet_hdr persist user 1000\n", True),
        ("apollo-fvp-tap0: tap vnet_hdr persist user 999\n", False),
        ("apollo-fvp-tap0: tap multi_queue persist user 1000\n", False),
        ("apollo-fvp-tap0: tap vnet_hdr persist user 1000 extra\n", False),
    ],
)
def test_tap_owner_accepts_only_kernel_vnet_header_flag(
    monkeypatch: pytest.MonkeyPatch,
    output: str,
    expected: bool,
) -> None:
    # Given: the kernel's persistent TAP description before or after FVP use.
    network = FvpTapNetwork(
        "apollo-fvp-tap0",
        "192.0.2.1",
        "192.0.2.10",
        24,
    )
    monkeypatch.setattr(
        "run_test_fvp_tap_network._command_output",
        lambda _argv: (0, output, ""),
    )

    # When/Then: only the owned base form and FVP-added vnet_hdr form pass.
    assert _interface_is_owned(network, 1000) is expected


def test_tap_preflight_blocks_absent_interface_before_fvp(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # Given: a selected platform profile with no project-owned TAP device.
    monkeypatch.setenv(FVP_TAP_NETWORK_ENV, json.dumps(NETWORK))
    monkeypatch.setattr(
        "run_test_fvp_tap_network._command_output",
        lambda _argv: (1, "", 'Device "apollo-fvp-tap0" does not exist.'),
    )

    # When: runtime prerequisites are inspected before an FVP launch.
    result = tap_network_preflight()

    # Then: the stable blocker states the exact setup command and target.
    assert result.reason == "blocked_fvp_tap_network_unavailable"
    assert result.interface_name == "apollo-fvp-tap0"
    assert result.target_ip == "192.0.2.10"
    assert "sudo scripts/setup/fvp_tap_network.sh setup" in result.hint
    assert "sudo scripts/setup/fvp_tap_network.sh status" in result.hint


def test_tap_preflight_accepts_owned_up_interface_with_host_address(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # Given: the status commands report the exact TAP object created for this UID.
    monkeypatch.setenv(FVP_TAP_NETWORK_ENV, json.dumps(NETWORK))
    monkeypatch.setattr("run_test_fvp_tap_network.os.getuid", lambda: 1000)
    monkeypatch.setattr("run_test_fvp_tap_network.verify_unprivileged_contract", lambda _owner: True)

    # When: the same preflight checks the live host network shape.
    result = tap_network_preflight()

    # Then: it permits the runner to continue to BitBake/FVP.
    assert result.reason is None


def test_unprivileged_verifier_uses_attestation_without_nft_or_exe(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # Given: a fresh root attestation and a readable state/process identity.
    state = TapNetworkState(1000, "a" * 32, 42, "123", "/usr/sbin/dnsmasq", "d" * 64, uplink="eth0")
    monkeypatch.setattr("run_test_fvp_tap_network._load_tap_state", lambda _path, _owner: state)
    monkeypatch.setattr("run_test_fvp_tap_network._attestation_state", lambda _state: object())
    monkeypatch.setattr("run_test_fvp_tap_network.attestation_is_fresh", lambda *_args: True)
    monkeypatch.setattr("run_test_fvp_tap_network.unprivileged_identity_matches", lambda _state: True)
    monkeypatch.setattr("run_test_fvp_tap_network._interface_is_up", lambda _network: True)
    monkeypatch.setattr("run_test_fvp_tap_network._interface_is_owned", lambda _network, owner: owner == 1000)
    monkeypatch.setattr("run_test_fvp_tap_network._interface_has_host_address", lambda _network: True)
    monkeypatch.setattr("run_test_fvp_tap_network._ip_forward_is_enabled", lambda: True)
    monkeypatch.setattr("run_test_fvp_tap_network._nft_contract_matches", lambda _state: pytest.fail("nft queried"))
    monkeypatch.setattr("run_test_fvp_tap_network.authenticated_tap_state", lambda *_args: pytest.fail("exe queried"))

    # When: the normal runner verifies the profile-owned TAP contract.
    result = verify_unprivileged_contract(1000)

    # Then: root-only nft and executable capabilities are not required.
    assert result


@pytest.mark.parametrize(
    "link,owner,addresses",
    [
        ({"ifname": "apollo-fvp-tap0", "flags": []}, "apollo-fvp-tap0: tap persist user 1000\n", [{"local": "192.0.2.1", "prefixlen": 24}]),
        ({"ifname": "apollo-fvp-tap0", "flags": ["UP"]}, "apollo-fvp-tap0: tap persist user 999\n", [{"local": "192.0.2.1", "prefixlen": 24}]),
        ({"ifname": "apollo-fvp-tap0", "flags": ["UP"]}, "apollo-fvp-tap0: tap persist user 1000\n", [{"local": "192.0.2.1", "prefixlen": 24}, {"local": "192.0.2.2", "prefixlen": 24}]),
    ],
)
def test_tap_preflight_rejects_down_wrong_owner_or_extra_address(
    monkeypatch: pytest.MonkeyPatch,
    link: dict[str, JsonValue],
    owner: str,
    addresses: list[dict[str, JsonValue]],
) -> None:
    # Given: one live interface fact no longer matches the project contract.
    monkeypatch.setenv(FVP_TAP_NETWORK_ENV, json.dumps(NETWORK))
    outputs = iter(
        [
            (0, json.dumps([link]), ""),
            (0, owner, ""),
            (0, json.dumps([{"addr_info": addresses}]), ""),
        ]
    )
    monkeypatch.setattr("run_test_fvp_tap_network._command_output", lambda _argv: next(outputs))
    monkeypatch.setattr("run_test_fvp_tap_network.os.getuid", lambda: 1000)
    monkeypatch.setattr(
        "run_test_fvp_tap_network.authenticated_tap_state",
        lambda _path, _owner: object(),
    )
    monkeypatch.setattr("run_test_fvp_tap_network._ip_forward_is_enabled", lambda: True)
    monkeypatch.setattr("run_test_fvp_tap_network._nft_contract_matches", lambda _state: True)

    # When: the unprivileged preflight evaluates the exact public interface.
    result = tap_network_preflight()

    # Then: no partial, foreign, or expanded address state can launch FVP.
    assert result.reason == "blocked_fvp_tap_network_unavailable"


@pytest.mark.parametrize(("forwarding", "nft"), [(False, True), (True, False)])
def test_verify_contract_requires_forwarding_and_exact_nft(
    monkeypatch: pytest.MonkeyPatch,
    forwarding: bool,
    nft: bool,
) -> None:
    # Given: every authenticated TAP fact except one host forwarding or NAT fact.
    state = TapNetworkState(1000, "a" * 32, 42, "123", "/usr/sbin/dnsmasq", "d" * 64, uplink="eth0")
    observed: list[str] = []
    monkeypatch.setattr("run_test_fvp_tap_network.authenticated_tap_state", lambda _path, owner: state if owner == 1000 else None)
    monkeypatch.setattr("run_test_fvp_tap_network._interface_is_up", lambda _network: True)
    monkeypatch.setattr("run_test_fvp_tap_network._interface_is_owned", lambda _network, owner: owner == 1000)
    monkeypatch.setattr("run_test_fvp_tap_network._interface_has_host_address", lambda _network: True)
    monkeypatch.setattr("run_test_fvp_tap_network._ip_forward_is_enabled", lambda: observed.append("forward") or forwarding)
    monkeypatch.setattr("run_test_fvp_tap_network._nft_contract_matches", lambda _state: observed.append("nft") or nft)

    # When: root status validates the runner UID rather than its effective UID.
    result = verify_tap_contract(1000)

    # Then: both required host controls are called and either missing control blocks.
    assert observed == ["forward", "nft"]
    assert not result


def test_verify_contract_accepts_exact_sudo_owner_not_root(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # Given: sudo runs status as root for a TAP explicitly owned by UID 1000.
    state = TapNetworkState(1000, "a" * 32, 42, "123", "/usr/sbin/dnsmasq", "d" * 64, uplink="eth0")
    owners: list[int] = []
    monkeypatch.setattr("run_test_fvp_tap_network.authenticated_tap_state", lambda _path, owner: state if owner == 1000 else None)
    monkeypatch.setattr("run_test_fvp_tap_network._interface_is_up", lambda _network: True)
    monkeypatch.setattr("run_test_fvp_tap_network._interface_is_owned", lambda _network, owner: owners.append(owner) or owner == 1000)
    monkeypatch.setattr("run_test_fvp_tap_network._interface_has_host_address", lambda _network: True)
    monkeypatch.setattr("run_test_fvp_tap_network._ip_forward_is_enabled", lambda: True)
    monkeypatch.setattr("run_test_fvp_tap_network._nft_contract_matches", lambda _state: True)

    # When: the root helper validates the saved sudo caller identity.
    result = verify_tap_contract(1000)

    # Then: `tap persist user 1000` is accepted without treating root as owner.
    assert result
    assert owners == [1000]


@pytest.mark.parametrize(
    "network",
    [
        {**NETWORK, "target_ip": "127.0.0.1"},
        {**NETWORK, "interface_name": "not-project-owned"},
    ],
)
def test_tap_preflight_rejects_malformed_environment(
    monkeypatch: pytest.MonkeyPatch,
    network: dict[str, str | int],
) -> None:
    # Given: a caller tries to alter the selected TAP contract after selection.
    monkeypatch.setenv(FVP_TAP_NETWORK_ENV, json.dumps(network))

    # When: preflight parses the environment boundary.
    result = tap_network_preflight()

    # Then: malformed data never reaches host command execution.
    assert result.reason == "blocked_fvp_tap_network_unavailable"


def test_authenticated_state_rejects_reused_pid_or_foreign_cmdline(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # Given: a root-owned state file pointing at a reused process ID.
    state_path = tmp_path / "state"
    state_path.write_text("state\n", encoding="utf-8")
    state = TapNetworkState(
        owner_uid=1000,
        nonce="nonce",
        pid=42,
        start_time="123",
        executable="/usr/sbin/dnsmasq",
        argv_sha256="expected",
    )
    monkeypatch.setattr(
        "run_test_fvp_tap_state._load_tap_state",
        lambda _path, _owner: state,
    )
    monkeypatch.setattr(
        "run_test_fvp_tap_state._process_identity_matches",
        lambda _state: False,
    )

    # When: preflight authenticates state and process identity together.
    result = authenticated_tap_state(state_path, 1000)

    # Then: a same-PID foreign command line cannot satisfy the DHCP gate.
    assert result is None


@pytest.mark.parametrize(
    "mutator",
    [
        lambda state: state | {"OWNER_UID": "999"},
        lambda state: state | {"HOST_CIDR": "192.0.2.2/24"},
        lambda state: state | {"EXTRA": "stale"},
        lambda state: {key: value for key, value in state.items() if key != "NONCE"},
    ],
)
def test_authenticated_state_rejects_wrong_or_stale_contract(
    monkeypatch: pytest.MonkeyPatch,
    mutator,
) -> None:
    # Given: a complete authenticated state whose live process is trusted at this seam.
    state = TapNetworkState(
        owner_uid=1000,
        nonce="a" * 32,
        pid=42,
        start_time="123",
        executable="/usr/sbin/dnsmasq",
        argv_sha256="",
        uplink="eth0",
    )
    digest = hashlib.sha256(
        b"\0".join(
            item.encode("utf-8")
            for item in (state.argv0, *_expected_dnsmasq_options(state))
        )
    ).hexdigest()
    valid = {
        "VERSION": "1",
        "INTERFACE_NAME": "apollo-fvp-tap0",
        "OWNER_UID": "1000",
        "HOST_CIDR": "192.0.2.1/24",
        "TARGET_IP": "192.0.2.10",
        "NETWORK_CIDR": "192.0.2.0/24",
        "NAT_TABLE": "apollo_fvp_tap",
        "UPLINK": "eth0",
        "IP_FORWARD_PREVIOUS": "0",
        "NONCE": state.nonce,
        "DNSMASQ_PID": "42",
        "DNSMASQ_STARTTIME": "123",
        "DNSMASQ_EXE": "/usr/sbin/dnsmasq",
        "DNSMASQ_ARGV0": "dnsmasq",
        "DNSMASQ_ARGS_SHA256": digest,
    }
    current = {"value": valid}
    monkeypatch.setattr(
        "run_test_fvp_tap_state._read_root_owned_state",
        lambda _path: current["value"],
    )
    monkeypatch.setattr(
        "run_test_fvp_tap_state._process_identity_matches", lambda _state: True
    )

    # When: one valid contract field is replaced after the passing baseline.
    assert authenticated_tap_state(Path("/run/irrelevant"), 1000) is not None
    current["value"] = mutator(valid)
    result = authenticated_tap_state(Path("/run/irrelevant"), 1000)

    # Then: incomplete or mismatched state fails closed before FVP.
    assert result is None


@pytest.mark.parametrize(
    "mutation",
    [
        lambda state: replace(state, start_time="stale"),
        lambda state: replace(state, executable="/bin/false"),
        lambda state: replace(state, nonce="f" * 32),
    ],
)
def test_process_identity_rejects_stale_start_executable_or_nonce(
    monkeypatch: pytest.MonkeyPatch,
    mutation,
) -> None:
    # Given: the exact process identity written by a successful helper setup.
    executable = Path("/usr/sbin/dnsmasq").resolve()
    state = TapNetworkState(
        owner_uid=1000,
        nonce="a" * 32,
        pid=42,
        start_time="123",
        executable=str(executable),
        argv_sha256="",
    )
    argv = (state.argv0, *_expected_dnsmasq_options(state))
    digest = hashlib.sha256(
        b"\0".join(item.encode("utf-8") for item in argv)
    ).hexdigest()
    state = replace(state, argv_sha256=digest)
    monkeypatch.setattr("run_test_fvp_tap_state.shutil.which", lambda _name: str(executable))
    monkeypatch.setattr("run_test_fvp_tap_state._process_start_time", lambda _pid: "123")
    monkeypatch.setattr("run_test_fvp_tap_state._process_executable", lambda _pid: executable)
    monkeypatch.setattr("run_test_fvp_tap_state._process_argv", lambda _pid: argv)
    assert _process_identity_matches(state)

    # When: the process identity is compared after one stale-field mutation.
    result = _process_identity_matches(mutation(state))

    # Then: stale PID reuse, a foreign executable, and another nonce all fail.
    assert not result


@pytest.mark.parametrize(("rule_count", "expected"), [(0, False), (1, True), (2, False)])
def test_nft_contract_rejects_missing_or_extra_rules(
    monkeypatch: pytest.MonkeyPatch,
    rule_count: int,
    expected: bool,
) -> None:
    # Given: the project-owned table has zero, one, or two NAT rules.
    state = TapNetworkState(1000, "a" * 32, 42, "123", "/usr/sbin/dnsmasq", "digest", uplink="eth0")
    table = {"table": {"family": "ip", "name": "apollo_fvp_tap"}}
    chain = {
        "chain": {
            "family": "ip",
            "table": "apollo_fvp_tap",
            "name": "postrouting",
            "type": "nat",
            "hook": "postrouting",
            "prio": "srcnat",
            "policy": "accept",
        }
    }
    rule = {
        "rule": {
            "family": "ip",
            "table": "apollo_fvp_tap",
            "chain": "postrouting",
            "expr": _canonical_expr(),
        }
    }
    entries = [table, chain, *([rule] * rule_count)]
    monkeypatch.setattr(
        "run_test_fvp_tap_network._command_output",
        lambda _argv: (0, json.dumps({"nftables": entries}), ""),
    )

    # When: root status verifies table, chain, and rule cardinality.
    result = _nft_contract_matches(state)

    # Then: only the single exact NAT rule is accepted.
    assert result is expected


def _canonical_expr() -> list[dict[str, JsonValue]]:
    return [
        {
            "match": {
                "op": "==",
                "left": {"payload": {"protocol": "ip", "field": "saddr"}},
                "right": {"prefix": {"addr": "192.0.2.0", "len": 24}},
            }
        },
        {
            "match": {
                "op": "==",
                "left": {"meta": {"key": "oifname"}},
                "right": "eth0",
            }
        },
        {"masquerade": None},
    ]


def test_nft_contract_accepts_live_prefix_expression(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # Given: nft 1.0.9 serializes the configured CIDR as a prefix object.
    state = TapNetworkState(
        1000,
        "a" * 32,
        42,
        "123",
        "/usr/sbin/dnsmasq",
        "digest",
        uplink="enp3s0",
    )
    entries = [
        {"metainfo": {"version": "1.0.9", "json_schema_version": 1}},
        {"table": {"family": "ip", "name": "apollo_fvp_tap", "handle": 8}},
        {
            "chain": {
                "family": "ip",
                "table": "apollo_fvp_tap",
                "name": "postrouting",
                "handle": 1,
                "type": "nat",
                "hook": "postrouting",
                "prio": 100,
                "policy": "accept",
            }
        },
        {
            "rule": {
                "family": "ip",
                "table": "apollo_fvp_tap",
                "chain": "postrouting",
                "handle": 2,
                "expr": [
                    {
                        "match": {
                            "op": "==",
                            "left": {
                                "payload": {
                                    "protocol": "ip",
                                    "field": "saddr",
                                }
                            },
                            "right": {
                                "prefix": {"addr": "192.0.2.0", "len": 24}
                            },
                        }
                    },
                    {
                        "match": {
                            "op": "==",
                            "left": {"meta": {"key": "oifname"}},
                            "right": "enp3s0",
                        }
                    },
                    {"masquerade": None},
                ],
            }
        },
    ]
    monkeypatch.setattr(
        "run_test_fvp_tap_network._command_output",
        lambda _argv: (0, json.dumps({"nftables": entries}), ""),
    )

    # When/Then: status accepts the exact live rule without relaxing its shape.
    assert _nft_contract_matches(state)


def test_nft_contract_accepts_only_handle_metadata(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # Given: realistic nft JSON with non-semantic handles on each live object.
    state = TapNetworkState(1000, "a" * 32, 42, "123", "/usr/sbin/dnsmasq", "digest", uplink="eth0")
    entries = [
        {"metainfo": {"version": "1.0"}},
        {"table": {"family": "ip", "name": "apollo_fvp_tap", "handle": 1}},
        {"chain": {"family": "ip", "table": "apollo_fvp_tap", "name": "postrouting", "type": "nat", "hook": "postrouting", "prio": "srcnat", "policy": "accept", "handle": 2}},
        {"rule": {"family": "ip", "table": "apollo_fvp_tap", "chain": "postrouting", "expr": _canonical_expr(), "handle": 3}},
    ]
    monkeypatch.setattr("run_test_fvp_tap_network._command_output", lambda _argv: (0, json.dumps({"nftables": entries}), ""))

    # When: the root verifier normalizes known nft metadata.
    result = _nft_contract_matches(state)

    # Then: handles pass without relaxing the ordered expression contract.
    assert result


@pytest.mark.parametrize(
    "mutate_expr",
    [
        lambda expr: [*expr, {"drop": None}],
        lambda expr: [expr[1], expr[0], expr[2]],
        lambda _expr: [{"drop": None}],
    ],
)
def test_nft_contract_rejects_extra_reordered_or_unrelated_expressions(
    monkeypatch: pytest.MonkeyPatch,
    mutate_expr,
) -> None:
    # Given: one rule whose canonical expression is changed without changing table count.
    state = TapNetworkState(1000, "a" * 32, 42, "123", "/usr/sbin/dnsmasq", "digest", uplink="eth0")
    rule = {
        "rule": {
            "family": "ip",
            "table": "apollo_fvp_tap",
            "chain": "postrouting",
            "expr": mutate_expr(_canonical_expr()),
            "comment": "192.0.2.0/24 eth0 masquerade",
        }
    }
    entries = [
        {"table": {"family": "ip", "name": "apollo_fvp_tap"}},
        {"chain": {"family": "ip", "table": "apollo_fvp_tap", "name": "postrouting", "type": "nat", "hook": "postrouting", "prio": "srcnat", "policy": "accept"}},
        rule,
    ]
    monkeypatch.setattr("run_test_fvp_tap_network._command_output", lambda _argv: (0, json.dumps({"nftables": entries}), ""))

    # When: root status examines the real nft JSON expression tree.
    result = _nft_contract_matches(state)

    # Then: text in comments cannot compensate for an unsafe expression tree.
    assert not result
