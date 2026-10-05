"""Read-only topology of the evaluated, default Apollo full-system Lua profile.

This describes configured bindings, not instantiated SystemC objects or traffic.
Only the fixed local entrypoint and its source-graph allowlist are evaluated. Lua
has no filesystem/process APIs and no host environment; evaluation is bounded.
"""
from __future__ import annotations

import copy
import hashlib
import json
import sys
import threading
from pathlib import Path
from xml.etree import ElementTree as ET

try:
    from scripts.test.apollo_ap_map_lua import LuaModuleError, load_module_graph
    from scripts.test.apollo_lua_descriptor import DescriptorError, evaluate_modules, plain_descriptor
except ModuleNotFoundError:
    # The dashboard is also invoked directly as a script, outside a package.
    sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "test"))
    from apollo_ap_map_lua import LuaModuleError, load_module_graph
    from apollo_lua_descriptor import DescriptorError, evaluate_modules, plain_descriptor

ENTRYPOINT = "hsoc-stack/tools/qbox-platform/platforms/apollo/apollo-qvp-saturn-v.lua"
GROUP_LABELS = {
    "fabric": "System Fabric", "ap_compute": "AP Compute",
    "rse": "RSE", "si_cl0": "Safety Island CL0",
    "si_cl1": "Safety Island CL1", "system_mgmt": "System Management",
    "ros": "Rest of SoC", "pinctrl": "Pin Control", "board": "Board",
    "platform": "Platform Services", "vp": "Virtual Platform",
}
_CACHE: dict[str, tuple[str, dict]] = {}
_LOCK = threading.Lock()


class TopologyError(RuntimeError):
    """Topology cannot be safely extracted; never return an invented graph."""


def _evaluate(modules: dict[str, str], *, entrypoint: str | None = None,
              environment: dict[str, str] | None = None) -> dict:
    try:
        entry = entrypoint or Path(ENTRYPOINT).name
        evaluated = evaluate_modules(
            modules, entrypoint=entry if entry in modules else "apollo-qvp.lua",
            environment=environment)
    except DescriptorError as exc:
        raise TopologyError(str(exc)) from exc
    return {"platform": plain_descriptor(evaluated["descriptor"], string_keys=True),
            "locations": evaluated["locations"]}


def _kind(module: str) -> str:
    if module in {"QemuInstance", "QemuInstanceManager"}:
        return "instance"
    if "router" in module.lower():
        return "router"
    if ("cortex" in module.lower() or module.lower().startswith("cpu_")
            or module.lower().endswith("cpu")):
        return "cpu"
    return "component"


def _graph(evaluated: dict, sources: list[dict], *,
           entrypoint: str = ENTRYPOINT) -> dict:
    objects: dict[str, dict] = {}
    def visit(value, path):
        if not isinstance(value, dict):
            return
        if "moduletype" in value and path != "platform":
            objects[path] = value
        for key, child in value.items():
            visit(child, f"{path}.{key}")
    visit(evaluated["platform"], "platform")
    nodes, edges, warnings = [], [], []
    base = str(Path(entrypoint).parent)
    for name, obj in sorted(objects.items()):
        location = evaluated["locations"].get(name, {})
        module_path = location.get("path", "./apollo-qvp.lua").removeprefix("./")
        if module_path.startswith("soc/hw-block/"):
            group = module_path.split("/")[2]
        elif module_path.startswith("hw-block/"):
            group = Path(module_path).stem
        elif module_path.startswith("board/"):
            group = "board"
        elif module_path.startswith("vp/"):
            group = "vp"
        elif module_path.startswith("soc/"):
            group = "fabric"
        else:
            group = "platform"
        if group not in GROUP_LABELS:
            group = "platform"
        # Shared builders can create another domain's objects (e.g. CL1 CPUs
        # through CL0 helpers), so function provenance is not ownership. Keep
        # source locations untouched but use explicit domain identities for
        # CPU/instance/router objects and Safety Island component prefixes.
        label = name.rsplit(".", 1)[-1]
        kind = _kind(obj["moduletype"])
        if name == "platform.rse_cpu_pass" or name.startswith("platform.rse_cpu_pass."):
            group = "rse"
        elif label.startswith("si_cl0_"):
            group = "si_cl0"
        elif label.startswith("si_cl1_"):
            group = "si_cl1"
        elif label.startswith("ap_") and kind in {"cpu", "instance", "router"}:
            group = "ap_compute"
        parameters = {key: value for key, value in obj.items()
                      if key != "moduletype" and not (
                          isinstance(value, dict) and "moduletype" in value)}
        nodes.append({"id": name, "label": label,
                      "group": group, "kind": kind,
                      "moduletype": obj["moduletype"], "parameters": parameters,
                      "source": {**location, "path": f"{base}/{module_path}"}})

    def resolve(reference, owner):
        raw = reference.lstrip("&")
        # CCI unqualified references are scoped to the containing Container.
        scope = owner.rsplit(".", 1)[0]
        candidates = [raw] if raw.startswith("platform.") else [f"{scope}.{raw}", f"platform.{raw}"]
        for candidate in candidates:
            for boundary in range(len(candidate.split(".")), 0, -1):
                prefix = ".".join(candidate.split(".")[:boundary])
                if prefix in objects:
                    return prefix, candidate[len(prefix):].lstrip(".")
        return None

    def add_edge(node, port, reference, kind, details):
        resolved = resolve(reference, node["id"])
        if not resolved:
            warnings.append(f"Unresolved {kind}: {node['id']}.{port} -> {reference}")
            return
        target, target_port = resolved
        source, source_port = node["id"], port
        raw = {"owner": source, "port": port, "reference": reference}
        direction = "declared-reference" if kind == "reference" else "binding-order"
        # Many Lua targets bind back to a router's initiator. Reverse those
        # bindings for transaction-flow display, preserving the declaration.
        if kind == "tlm" and "initiator" in target_port.lower():
            source, target = target, source
            source_port, target_port = target_port, source_port
            direction = "initiator-to-target"
        elif kind == "tlm" and "target" in target_port.lower():
            direction = "initiator-to-target"
        elif kind == "signal" and ("_out" in target_port or target_port.endswith("out")):
            source, target = target, source
            source_port, target_port = target_port, source_port
            direction = "output-to-input"
        edge = {"source": source, "target": target, "source_port": source_port,
                "target_port": target_port, "kind": kind, "binding": raw,
                "direction": direction, **details}
        signature = json.dumps(edge, sort_keys=True)
        edge["id"] = "edge-" + hashlib.sha256(signature.encode()).hexdigest()[:16]
        edges.append(edge)
        if kind == "reference" and objects[resolved[0]]["moduletype"] == "QemuInstance":
            node["qemu_instance"] = resolved[0]

    for node in nodes:
        def scan(value, port=""):
            if not isinstance(value, dict):
                return
            if "moduletype" in value:
                return
            binding = value.get("bind")
            if isinstance(binding, str):
                for reference in binding.split(";"):
                    if not reference.strip():
                        continue
                    # Socket/address descriptors and standard memory socket
                    # names identify TLM; do not classify IRQ/reset as traffic.
                    names = port.lower() + " " + reference.lower()
                    is_tlm = "backend_socket" not in names and any(
                        x in names for x in ("socket", "initiator", "bus_master", ".mem", "_iface", ".dma"))
                    details = {key: value[key] for key in (
                        "address", "size", "relative_addresses", "priority") if key in value}
                    add_edge(node, port, reference.strip(), "tlm" if is_tlm else "signal", details)
            for key, child in value.items():
                if key == "args" and isinstance(child, dict):
                    for index, reference in child.items():
                        if isinstance(reference, str) and reference.startswith("&"):
                            add_edge(node, f"args.{index}", reference, "reference", {})
                elif key != "bind":
                    scan(child, f"{port}.{key}".strip("."))
        scan(node["parameters"])
    groups = [{"id": group, "label": label,
               "description": "Logical domain identity for CPUs/instances/routers and SI prefixes; otherwise defining Lua module."}
              for group, label in GROUP_LABELS.items()
              if any(node["group"] == group for node in nodes)]
    return {"schema_version": 1, "profile": "apollo-qvp-full-static-defaults",
            "environment": {"QBOX_RDASPEN_ENABLE_AP_CPUS": "true"},
            "entrypoint": entrypoint, "sources": sources, "groups": groups,
            "nodes": nodes, "edges": edges, "warnings": sorted(set(warnings)),
            "limitations": ["Evaluated Lua defaults with AP CPUs enabled; not the active VM configuration or runtime traffic.",
                            "Source locations identify first-observed function/call-site scopes, not exact assignment lines.",
                            "Binding directions inferred from socket/port names; raw declarations retained."]}


def get_topology(repo_root: Path | str) -> dict:
    """Extract/cache fixed local full profile; invalidate on any included source."""
    root = Path(repo_root).resolve()
    entry = root / ENTRYPOINT
    with _LOCK:
        try:
            modules = load_module_graph(entry)
        except (LuaModuleError, OSError) as exc:
            raise TopologyError(f"Lua source graph unavailable: {exc}") from exc
        sources = [{"path": f"{entry.parent.relative_to(root)}/{path}",
                    "sha256": hashlib.sha256(text.encode()).hexdigest()}
                   for path, text in sorted(modules.items())]
        fingerprint = hashlib.sha256(json.dumps(sources, sort_keys=True).encode()).hexdigest()
        key = str(root)
        if key not in _CACHE or _CACHE[key][0] != fingerprint:
            graph = _graph(_evaluate(modules), sources)
            # Bound even when tests or embedded servers request many roots.
            if len(_CACHE) >= 4:
                _CACHE.pop(next(iter(_CACHE)))
            _CACHE[key] = fingerprint, graph
        return copy.deepcopy(_CACHE[key][1])


def topology_drawio(graph: dict) -> str:
    """Native editable draw.io XML, preserving every node and binding."""
    model = ET.Element("mxGraphModel", adaptiveColors="auto",
                       profile=graph["profile"], entrypoint=graph["entrypoint"],
                       sourceHashes=json.dumps(graph["sources"], sort_keys=True))
    root = ET.SubElement(model, "root")
    ET.SubElement(root, "mxCell", id="0")
    ET.SubElement(root, "mxCell", id="1", parent="0")
    notice = ("Apollo QVP · 시작 구성 snapshot (실제 object/traffic 관측과 별개)"
              if graph.get("frozen") else
              "Apollo QVP · 정적 Lua 연결도 (AP CPU 활성화 기본값; 실행 중 VM/트래픽 아님)")
    title = ET.SubElement(root, "mxCell", id="topology-notice", parent="1", vertex="1",
                          value=notice,
                          style="text;html=0;align=left;whiteSpace=wrap;")
    ET.SubElement(title, "mxGeometry", x="40", y="0", width="1060", height="30", **{"as": "geometry"})
    node_groups = {node["id"]: node["group"] for node in graph["nodes"]}
    y = 40
    colors = {"cpu": "#dae8fc", "router": "#fff2cc", "component": "#d5e8d4", "instance": "#e1d5e7"}
    for group in graph["groups"]:
        members = [node for node in graph["nodes"] if node["group"] == group["id"]]
        columns = {"cpu": 0, "instance": 0, "router": 1, "component": 2}
        rows = [0, 0, 0]
        height = max(sum(columns[n["kind"]] == col for n in members) for col in range(3)) * 100 + 80
        cell = ET.SubElement(root, "mxCell", id="group-" + group["id"], value=group["label"],
                             style="swimlane;startSize=30;html=0;container=1;", vertex="1", parent="1")
        ET.SubElement(cell, "mxGeometry", x="40", y=str(y), width="1060", height=str(height), **{"as": "geometry"})
        y += height + 40
        for node in members:
            col = columns[node["kind"]]
            metadata = ET.SubElement(root, "object", id=node["id"], label=node["label"] + "\n" + node["moduletype"],
                                     moduletype=node["moduletype"], source=json.dumps(node["source"]),
                                     parameters=json.dumps(node["parameters"], sort_keys=True),
                                     tags=node["kind"] + " " + group["id"])
            cell = ET.SubElement(metadata, "mxCell", vertex="1", parent="group-" + group["id"],
                                 style=f"rounded=1;whiteSpace=wrap;html=0;fillColor={colors[node['kind']]};")
            ET.SubElement(cell, "mxGeometry", x=str(40 + col * 340), y=str(50 + rows[col] * 100),
                          width="290", height="70", **{"as": "geometry"})
            rows[col] += 1
    for edge in graph["edges"]:
        same = node_groups[edge["source"]] == node_groups[edge["target"]]
        parent = "group-" + node_groups[edge["source"]] if same else "1"
        cell = ET.SubElement(root, "mxCell", id=edge["id"], source=edge["source"], target=edge["target"],
                             value=f"{edge['source_port']} → {edge['target_port']}", edge="1", parent=parent,
                             style="edgeStyle=orthogonalEdgeStyle;rounded=1;html=0;" +
                             ("dashed=1;" if edge["kind"] == "reference" else ""))
        ET.SubElement(cell, "mxGeometry", relative="1", **{"as": "geometry"})
    return ET.tostring(model, encoding="unicode")
