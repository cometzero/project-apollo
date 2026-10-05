"""Frozen, source-derived launch topology for the Saturn-V dashboard.

The launcher owns ``board-launch.json`` and captures it immediately before QBox
starts. This module never evaluates a browser-supplied path or host environment.
The resulting graph proves configuration, not object existence or bus traffic.
"""
from __future__ import annotations

import copy
from contextlib import nullcontext
from datetime import datetime, timezone
import fcntl
import hashlib
import json
import os
from pathlib import Path
import re
import threading

from . import topology

TopologyError = topology.TopologyError
_LOCK = threading.Lock()
_ADDRESS_FIELDS = {"address", "size", "mapped_base_addr", "base_addr"}
_LIMIT = 32 * 1024 * 1024


def _read_json_with_hash(path: Path, limit: int = _LIMIT) -> tuple[dict, str]:
    try:
        with path.open("rb") as stream:
            raw = stream.read(limit + 1)
        if len(raw) > limit:
            raise TopologyError(f"Topology input exceeds size limit: {path.name}")
        value = json.loads(raw)
    except (OSError, ValueError) as exc:
        raise TopologyError(f"Invalid topology input: {path.name}") from exc
    if not isinstance(value, dict):
        raise TopologyError(f"Expected JSON object: {path.name}")
    return value, hashlib.sha256(raw).hexdigest()


def _read_json(path: Path, limit: int = _LIMIT) -> dict:
    return _read_json_with_hash(path, limit)[0]


def _display_path(path: Path, root: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return str(path)


def _safe_numbers(value, field=""):
    """Keep address zero and all 64-bit values exact in a browser's JSON parser."""
    if isinstance(value, dict):
        return {key: _safe_numbers(child, key) for key, child in value.items()}
    if isinstance(value, list):
        return [_safe_numbers(child) for child in value]
    if isinstance(value, int) and not isinstance(value, bool):
        if field in _ADDRESS_FIELDS:
            return hex(value)
        if abs(value) > (1 << 53) - 1:
            return str(value)
    if isinstance(value, float) and field in _ADDRESS_FIELDS:
        # Lua 5.1/5.2 has only double numbers: it can already have rounded a
        # literal before the JSON boundary. Never pretend that hex formatting
        # repairs that lost precision. Lua 5.3/5.4 integer values arrive as int.
        if abs(value) > (1 << 53) - 1 or not value.is_integer():
            raise TopologyError("Lua address precision unavailable; use a Lua 5.4 interpreter or exact string/CCI integer")
        return hex(int(value))
    return value


def _apply_overrides(platform: dict, overrides: list[str]) -> tuple[list, list]:
    applied, unresolved = [], []
    for text in overrides:
        path, separator, raw = text.partition("=")
        path = path.strip()
        if not separator or not re.fullmatch(r"platform(?:\.[A-Za-z_0-9]+)+", path):
            unresolved.append({"parameter": text, "reason": "unsupported CCI path or syntax"})
            continue
        keys = path.split(".")[1:]
        parent = platform
        for key in keys[:-1]:
            parent = parent.get(key) if isinstance(parent, dict) else None
        if not isinstance(parent, dict) or keys[-1] not in parent or keys[-1] == "moduletype":
            unresolved.append({"parameter": text, "reason": "not a declared Lua scalar"})
            continue
        old = parent[keys[-1]]
        try:
            value = json.loads(raw)
        except ValueError:
            try:
                value = int(raw, 0)
            except ValueError:
                value = raw
        valid = ((isinstance(old, bool) and isinstance(value, bool)) or
                 (isinstance(old, (int, float)) and not isinstance(old, bool)
                  and isinstance(value, (int, float)) and not isinstance(value, bool)) or
                 (isinstance(old, str) and isinstance(value, str)))
        if not valid:
            unresolved.append({"parameter": text, "reason": "unsupported scalar type change"})
            continue
        parent[keys[-1]] = value
        applied.append({"path": path, "value": value})
    return applied, unresolved


def _windows(node: dict) -> list[dict]:
    windows = []

    def visit(value, path):
        if not isinstance(value, dict):
            return
        address = value.get("address")
        if isinstance(address, str) and re.fullmatch(r"0[xX][0-9a-fA-F]+", address):
            address = int(address, 16)
        if isinstance(address, int) and not isinstance(address, bool):
            window = {key: value[key] for key in (
                "address", "size", "relative_addresses", "mapped_base_addr", "priority") if key in value}
            window.update(port=path, address_space=value.get("bind"), evidence="lua-configured")
            if isinstance(value.get("size"), int) and value["size"] > 0:
                window["end"] = hex(address + value["size"] - 1)
            windows.append(window)
        for key, child in value.items():
            visit(child, f"{path}.{key}".strip("."))

    visit(node["parameters"], "")
    return windows


def _external_node(identity, label, module, parameters, source):
    return {"id": identity, "label": label, "group": "external", "kind": "component",
            "moduletype": module, "parameters": parameters, "source": source,
            "provenance": "launcher-attached", "windows": []}


def _attachment_edge(source, target, channel, source_port, target_port, evidence):
    return {"id": f"attachment-{source}-{channel}-{target}", "source": source,
            "target": target, "kind": channel, "source_port": source_port,
            "target_port": target_port, "direction": "bidirectional",
            "provenance": "launcher-attached", "connection": "CONFIGURED_ENDPOINT_MATCH",
            "evidence": evidence,
            "binding": {"owner": source, "port": source_port, "reference": "&" + target}}


def _add_attachments(graph: dict, run_dir: Path) -> list[dict]:
    path = run_dir / "tc397-status.json"
    if not path.is_file():
        return []
    manifest, digest = _read_json_with_hash(path, 2 * 1024 * 1024)
    source = {"path": str(path), "sha256": digest,
              "accuracy": "launcher-manifest"}
    # A STARTING manifest exists even if executable/startup validation failed.
    # The process command is required before claiming a configured MCU node.
    if not manifest.get("qemu_command"):
        return [{"id": "external.tc397", "connection": "UNCONFIRMED",
                 "reason": "TC397 process command not captured", "source": source}]
    graph["nodes"].append(_external_node(
        "external.tc397", "TC397 · Zephyr vMCU", "QEMU external process",
        {key: manifest[key] for key in ("qemu_command", "tc397_pid", "console_fifo") if key in manifest}, source))
    graph["groups"].append({"id": "external", "label": "External board participants",
                             "description": "Launcher configuration; independent processes, not Lua CCI objects."})
    links = []
    for key, channel, port in (("uart_endpoint", "uart", "ASCLIN0"),
                               ("safety_endpoint", "uart", "ASCLIN2"),
                               ("gpio_endpoint", "gpio", "PORT0")):
        endpoint = manifest.get(key)
        targets = [node for node in graph["nodes"]
                   if node["moduletype"] == "char_backend_socket" and endpoint
                   and node["parameters"].get("address") == endpoint
                   and node["parameters"].get("server") is False]
        match = len(targets) == 1
        link = {"id": key, "source": "external.tc397", "source_port": port,
                "endpoint": endpoint, "kind": channel, "provenance": "launcher-attached",
                "connection": "CONFIGURED_ENDPOINT_MATCH" if match else "UNCONFIRMED",
                "manifest_source": source["path"]}
        if match:
            link["target"] = targets[0]["id"]
            graph["edges"].append(_attachment_edge("external.tc397", targets[0]["id"],
                                                  channel, port, "biflow_socket", link))
        else:
            link["reason"] = "No unique matching Lua client backend endpoint"
        links.append(link)

    silkit = manifest.get("sil_kit")
    if not isinstance(silkit, dict):
        return links
    roles = {}
    for process in silkit.get("processes", []):
        role = process.get("role")
        if role not in {"bridge", "restbus", "registry"}:
            continue
        identity = "external.silkit." + role
        roles[role] = identity
        graph["nodes"].append(_external_node(
            identity, silkit.get("participant_names", {}).get(role, "SIL Kit " + role),
            "SIL Kit " + role, {**process, "network": silkit.get("network"),
                                "registry_uri": silkit.get("registry_uri")}, source))
    # Registry participates in discovery only, never draw it as the CAN data bus.
    endpoint = silkit.get("can_endpoint")
    bridge = next((p for p in silkit.get("processes", []) if p.get("role") == "bridge"), {})
    command = bridge.get("command", [])
    try:
        bridge_endpoint = command[command.index("--qemu-endpoint") + 1]
    except (ValueError, IndexError):
        bridge_endpoint = None
    can_configured = any("tc397-can.chardev=tc397can" == arg for arg in manifest["qemu_command"])
    matched = bool(endpoint and endpoint == bridge_endpoint and can_configured and "bridge" in roles)
    can = {"id": "can_endpoint", "kind": "can", "endpoint": endpoint,
           "source": "external.tc397", "target": roles.get("bridge"),
           "connection": "CONFIGURED_ENDPOINT_MATCH" if matched else "UNCONFIRMED",
           "provenance": "launcher-attached", "manifest_source": source["path"]}
    links.append(can)
    if matched:
        graph["edges"].append(_attachment_edge("external.tc397", roles["bridge"], "can",
                                              "M_CAN", "CAN1 transport", can))
    if "bridge" in roles and "restbus" in roles and silkit.get("network"):
        graph["edges"].append(_attachment_edge(roles["bridge"], roles["restbus"], "can",
                                              silkit["network"], silkit["network"],
                                              {"manifest_source": source["path"],
                                               "network": silkit["network"]}))
    return links


def _build(root: Path, run_dir: Path, launch: dict | None) -> dict:
    if launch is None:
        graph = topology.get_topology(root)
        graph.update(profile="apollo-qvp-board-source-preview", frozen=False,
                     evidence="source-preview", attachments=[], snapshot=None)
    else:
        raw_conf = launch.get("conf")
        if not isinstance(raw_conf, str) or not raw_conf:
            raise TopologyError("Launch snapshot has no selected Lua conf")
        entry = Path(raw_conf)
        if not entry.is_absolute():
            entry = root / entry
        entry = entry.resolve()
        environment = launch.get("environment", {})
        overrides = launch.get("platform_params", [])
        if (not isinstance(environment, dict) or any(not isinstance(k, str) or not isinstance(v, str)
                                                   for k, v in environment.items())):
            raise TopologyError("Launch environment must contain string values")
        if not isinstance(overrides, list) or any(not isinstance(p, str) for p in overrides):
            raise TopologyError("Launch platform_params must be string list")
        try:
            modules = topology.load_module_graph(entry)
        except (topology.LuaModuleError, OSError) as exc:
            raise TopologyError(f"Lua source graph unavailable: {exc}") from exc
        # Unlike the legacy static preview, an absent AP enable variable must
        # remain absent/false. Never silently inject the preview's AP default.
        effective = {"QBOX_RDASPEN_ENABLE_AP_CPUS": "", **environment}
        evaluated = topology._evaluate(modules, entrypoint=entry.name, environment=effective)
        applied, unresolved = _apply_overrides(evaluated["platform"], overrides)
        sources = [{"path": _display_path(entry.parent / name, root),
                    "sha256": hashlib.sha256(text.encode()).hexdigest()}
                   for name, text in sorted(modules.items())]
        graph = topology._graph(evaluated, sources, entrypoint=_display_path(entry, root))
        graph.update(profile="apollo-qvp-board-launch-snapshot", frozen=True,
                     evidence="startup-configured", environment=environment)
        graph["limitations"] = [
            "Frozen startup configuration; not runtime object existence, traffic or health.",
            "Source locations are observed function/call-site scopes, not exact assignment lines.",
            "Binding directions are inferred; original declarations are retained.",
            "Board placement is logical and does not establish physical Saturn-V schematic parity.",
            "External process/endpoint matches describe configured transport, not communication success.",
        ]
        if unresolved:
            graph["warnings"].append("Some CCI overrides could not be interpreted; topology is not run-exact.")
        graph["attachments"] = _add_attachments(graph, run_dir)
        graph["snapshot"] = {"run_id": launch.get("run_id"), "entrypoint": str(entry),
                             "captured_at": datetime.now(timezone.utc).isoformat(),
                             "manifest_source": str(run_dir / "board-launch.json"),
                             "provider": launch.get("provider", {}),
                             "exact_environment": True, "resolved_overrides": applied,
                             "unresolved_overrides": unresolved, "run_exact": not unresolved}
        fingerprint = {"sources": sources, "environment": environment, "overrides": overrides,
                       "attachments": graph["attachments"], "entrypoint": str(entry), "schema_version": 2}
        graph["snapshot"]["fingerprint"] = hashlib.sha256(
            json.dumps(fingerprint, sort_keys=True).encode()).hexdigest()
    graph["schema_version"] = 2
    source_hashes = {source["path"]: source["sha256"] for source in graph["sources"]}
    for node in graph["nodes"]:
        node.setdefault("provenance", "lua-configured")
        node.setdefault("windows", _windows(node))
        if node["source"]["path"] in source_hashes:
            node["source"]["sha256"] = source_hashes[node["source"]["path"]]
    for edge in graph["edges"]:
        edge.setdefault("provenance", "lua-configured")
    return _safe_numbers(graph)


def get_board_topology(repo_root: Path | str, run_dir: Path | str, *,
                       launch: dict | None = None) -> dict:
    """Return startup snapshot, or explicitly marked source preview before boot.

    A provided launch dict follows the same contract as board-launch.json:
    ``{run_id, conf, environment, platform_params, provider}``. The selected conf
    is the actual Lua entrypoint after provider/explicit-conf precedence. Once
    frozen, changes in the checkout or status logs never rewrite this run's graph.
    """
    root, output = Path(repo_root).resolve(), Path(run_dir).resolve()
    with _LOCK:
        manifest = output / "board-launch.json"
        if launch is None and manifest.is_file():
            launch = _read_json(manifest, 2 * 1024 * 1024)
        if launch is not None:
            output.mkdir(parents=True, exist_ok=True)
        # The runtime and HTTP server can request the first snapshot together.
        # Serialize their writes across processes as well as server threads.
        lock_context = (output / ".board-topology.lock").open("a") if launch is not None else nullcontext()
        with lock_context as lock:
            if lock is not None:
                fcntl.flock(lock, fcntl.LOCK_EX)
            snapshot = output / "board-topology.json"
            if snapshot.is_file():
                graph = _read_json(snapshot)
                if launch is not None and graph.get("snapshot", {}).get("run_id") != launch.get("run_id"):
                    raise TopologyError("Frozen topology belongs to another run; use a new run directory")
                return graph
            graph = _build(root, output, launch)
            if launch is not None:
                temporary = output / (".board-topology-" + str(os.getpid()) + ".tmp")
                try:
                    temporary.write_text(json.dumps(graph, indent=2, sort_keys=True) + "\n", encoding="utf-8")
                    temporary.replace(snapshot)
                finally:
                    temporary.unlink(missing_ok=True)
            return copy.deepcopy(graph)
