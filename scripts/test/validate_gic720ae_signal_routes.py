#!/usr/bin/env python3

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
from typing import TypeAlias

Json: TypeAlias = None | bool | int | float | str | list["Json"] | dict[str, "Json"]
REQUIRED = frozenset(("name", "source", "controller", "kind", "architectural_intid", "socket_class", "socket_index", "trigger", "polarity", "owner_view", "target_semantics", "target_pes"))
KINDS = frozenset(("SGI", "PPI", "SPI", "ESPI", "EPPI", "IRQ", "MSI_LPI"))
TRIGGERS = frozenset(("edge", "level"))
POLARITIES = frozenset(("high", "low", "positive", "negative", "none"))
TARGET_SEMANTICS = frozenset(("shared", "per_cpu", "directed", "broadcast"))
VIEWS = frozenset(("View1", "View2"))
LUA_EXPORT = r'''local value = dofile(os.getenv("GIC720AE_ROUTES"))
local function quote(s) return string.format("%q", s):gsub("\\\n", "\\n") end
local function encode(v)
  local t = type(v)
  if t == "nil" then return "null" end
  if t == "boolean" then return v and "true" or "false" end
  if t == "number" then return tostring(v) end
  if t == "string" then return quote(v) end
  if t ~= "table" then error("unsupported Lua value: " .. t) end
  local n = #v
  local count = 0
  for k,_ in pairs(v) do
    count = count + 1
    if type(k) ~= "number" and type(k) ~= "string" then error("unsupported Lua key") end
  end
  if n > 0 then
    if count ~= n then error("mixed Lua table is unsupported") end
    local out = {}
    for i=1,n do out[i] = encode(v[i]) end
    return "[" .. table.concat(out, ",") .. "]"
  end
  local keys = {}
  for k,_ in pairs(v) do table.insert(keys, k) end
  table.sort(keys, function(a,b) return tostring(a) < tostring(b) end)
  local out = {}
  for _,k in ipairs(keys) do table.insert(out, quote(tostring(k)) .. ":" .. encode(v[k])) end
  return "{" .. table.concat(out, ",") .. "}"
end
io.write(encode(value))'''


class RouteError(Exception):
    def __init__(self, diagnostic: str) -> None:
        self.diagnostic = diagnostic
        super().__init__(diagnostic)


def route_json(path: Path) -> dict[str, Json]:
    try:
        raw = path.read_bytes()
    except OSError as error:
        raise RouteError(f"read-error: {error}") from error
    if path.suffix == ".lua":
        process = subprocess.run(("lua", "-e", LUA_EXPORT), capture_output=True, text=True, check=False, env={**os.environ, "GIC720AE_ROUTES": str(path)})
        if process.returncode != 0:
            raise RouteError(f"malformed-lua: {process.stderr.strip()}")
        raw = process.stdout.encode()
    try:
        parsed: Json = json.loads(raw)
    except json.JSONDecodeError as error:
        raise RouteError(f"malformed-json: {error.msg}") from error
    if not isinstance(parsed, dict):
        raise RouteError("schema-error: root must be an object")
    return parsed


def field(route: dict[str, Json], key: str, route_name: str) -> Json:
    if key not in route:
        raise RouteError(f"missing-required-field: route={route_name} field={key}")
    return route[key]


def text_field(route: dict[str, Json], key: str, route_name: str) -> str:
    value = field(route, key, route_name)
    if not isinstance(value, str) or not value:
        raise RouteError(f"invalid-field: route={route_name} field={key}")
    return value


def int_field(route: dict[str, Json], key: str, route_name: str) -> int:
    value = field(route, key, route_name)
    if not isinstance(value, int) or isinstance(value, bool):
        raise RouteError(f"invalid-field: route={route_name} field={key}")
    return value


def canonical_route(route_value: Json) -> dict[str, Json]:
    if not isinstance(route_value, dict):
        raise RouteError("schema-error: route must be an object")
    route = dict(route_value)
    aliases = (("intid", "architectural_intid"), ("view", "owner_view"), ("targets", "target_pes"))
    for old, new in aliases:
        if new not in route and old in route:
            route[new] = route[old]
    if "owner_view" in route and isinstance(route["owner_view"], int):
        route["owner_view"] = f"View{route['owner_view']}"
    if "target_semantics" not in route and "target_pes" in route:
        route["target_semantics"] = "per_cpu" if route.get("kind") == "PPI" else "shared"
    return route


def validate_route(route_value: Json, source_seen: set[tuple[str, str, int]], owner_seen: set[tuple[str, str, int]], spi_rows: list[dict[str, Json]], ppi_ids: set[int], sgi_ids: set[int]) -> None:
    route = canonical_route(route_value)
    name = text_field(route, "name", "<unnamed>")
    missing = REQUIRED.difference(route)
    if missing:
        raise RouteError(f"missing-required-field: route={name} fields={','.join(sorted(missing))}")
    source = text_field(route, "source", name)
    controller = text_field(route, "controller", name)
    kind = text_field(route, "kind", name)
    socket_class = text_field(route, "socket_class", name)
    trigger = text_field(route, "trigger", name)
    polarity = text_field(route, "polarity", name)
    intid = int_field(route, "architectural_intid", name)
    socket_index = int_field(route, "socket_index", name)
    owner_view = text_field(route, "owner_view", name)
    target_semantics = text_field(route, "target_semantics", name).lower().replace("-", "_")
    targets = field(route, "target_pes", name)
    if kind not in KINDS:
        raise RouteError(f"unknown-kind: route={name} kind={kind}")
    if trigger not in TRIGGERS:
        raise RouteError(f"unknown-trigger: route={name} trigger={trigger}")
    if polarity not in POLARITIES:
        raise RouteError(f"unknown-polarity: route={name} polarity={polarity}")
    if owner_view not in VIEWS:
        raise RouteError(f"unknown-view: route={name} owner_view={owner_view}")
    if target_semantics not in TARGET_SEMANTICS:
        raise RouteError(f"invalid-target-semantics: route={name} target_semantics={target_semantics}")
    if not isinstance(targets, list) or not targets or any(not isinstance(target, int) or isinstance(target, bool) or target < 0 for target in targets):
        raise RouteError(f"invalid-targets: route={name}")
    binding = (source, controller, socket_index)
    owner_route = (controller, owner_view, intid)
    if binding in source_seen:
        raise RouteError(f"duplicate-binding: route={name} source={source} controller={controller} socket_index={socket_index}")
    if owner_route in owner_seen:
        raise RouteError(f"duplicate-owner-route: route={name} controller={controller} owner_view={owner_view} intid={intid}")
    source_seen.add(binding)
    owner_seen.add(owner_route)
    if kind == "SGI":
        if not 0 <= intid <= 15 or socket_class != "sgi" or socket_index != intid:
            raise RouteError(f"invalid-sgi: route={name}")
        if target_semantics not in ("directed", "broadcast"):
            raise RouteError(f"invalid-sgi-target-semantics: route={name}")
        sgi_ids.add(intid)
    elif kind == "PPI":
        if not 16 <= intid <= 31 or socket_class != "ppi" or socket_index != intid:
            raise RouteError(f"invalid-ppi: route={name}")
        if target_semantics != "per_cpu":
            raise RouteError(f"per-cpu-ppi-target-required: route={name}")
        ppi_ids.add(intid)
    elif kind == "SPI":
        if not 32 <= intid <= 991:
            raise RouteError(f"invalid-spi-range: route={name} intid={intid}")
        if socket_class != "normal_spi":
            raise RouteError(f"invalid-socket-class: route={name} expected=normal_spi")
        if socket_index != intid - 32:
            raise RouteError(f"off-by-32: route={name} intid={intid} socket_index={socket_index} expected={intid - 32}")
        spi_rows.append(route)
    elif kind == "ESPI":
        if not 4096 <= intid <= 5119 or socket_class != "espi":
            raise RouteError(f"invalid-espi: route={name}")
        if socket_index >= 960:
            raise RouteError(f"ESPI-as-consecutive-normal-socket: route={name} socket_index={socket_index}")
    elif kind == "EPPI":
        if not 1056 <= intid <= 1119 or socket_class != "eppi":
            raise RouteError(f"invalid-eppi: route={name}")
    elif socket_class not in ("nvic", "lpi"):
        raise RouteError(f"invalid-socket-class: route={name} class={socket_class}")


def validate(document: dict[str, Json], source_sha256: str) -> dict[str, Json]:
    active = document.get("si_active_routes", document)
    if not isinstance(active, dict):
        raise RouteError("schema-error: si_active_routes must be an object")
    schema = active.get("schema_version")
    routes = active.get("routes", active.get("irq_routes"))
    if not isinstance(schema, int) or schema < 2:
        raise RouteError("schema-error: schema_version must be >= 2")
    if not isinstance(routes, list) or not routes:
        raise RouteError("schema-error: routes must be a non-empty array")
    source_seen: set[tuple[str, str, int]] = set()
    owner_seen: set[tuple[str, str, int]] = set()
    spi_rows: list[dict[str, Json]] = []
    ppi_ids: set[int] = set()
    sgi_ids: set[int] = set()
    for route in routes:
        validate_route(route, source_seen, owner_seen, spi_rows, ppi_ids, sgi_ids)
    if not spi_rows:
        raise RouteError("coverage-error: no active normal SPI routes")
    canonical_spis = [canonical_route(row) for row in spi_rows]
    ordered_spis = sorted(canonical_spis, key=lambda row: int_field(row, "architectural_intid", text_field(row, "name", "<unnamed>")))
    pfdi_view2 = any("pfdi" in text_field(row, "source", text_field(row, "name", "<unnamed>")).lower() and text_field(row, "controller", text_field(row, "name", "<unnamed>")) == "si_cl1_gic" and text_field(row, "owner_view", text_field(row, "name", "<unnamed>")) == "View2" for row in canonical_spis)
    if not pfdi_view2:
        raise RouteError("coverage-error: CL1 PFDI route must be owned by si_cl1 in View2")
    def summary(row: dict[str, Json]) -> dict[str, Json]:
        name = text_field(row, "name", "<unnamed>")
        return {"name": name, "intid": int_field(row, "architectural_intid", name), "socket_index": int_field(row, "socket_index", name)}
    return {"passed": True, "schema": schema, "source_sha256": source_sha256, "routes_sha256": hashlib.sha256(json.dumps(routes, sort_keys=True, separators=(",", ":")).encode()).hexdigest(), "route_count": len(routes), "first_active_standard_spi": summary(ordered_spis[0]), "last_active_standard_spi": summary(ordered_spis[-1]), "ppi_coverage": sorted(ppi_ids), "sgi_coverage": sorted(sgi_ids), "cl1_pfdi_view2_ownership": pfdi_view2}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--routes", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--expect-source-sha256")
    args = parser.parse_args()
    try:
        source_bytes = args.routes.read_bytes()
        source_sha256 = hashlib.sha256(source_bytes).hexdigest()
        if args.expect_source_sha256 and args.expect_source_sha256 != source_sha256:
            raise RouteError(f"source-hash-mismatch: expected={args.expect_source_sha256} actual={source_sha256}")
        result = validate(route_json(args.routes), source_sha256)
    except (OSError, RouteError) as error:
        result = {"passed": False, "diagnostic": str(error)}
    try:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    except OSError as error:
        print(f"output-error: {error}", file=sys.stderr)
        return 2
    print(json.dumps(result, sort_keys=True))
    return 0 if result.get("passed") is True else 1


if __name__ == "__main__":
    raise SystemExit(main())
