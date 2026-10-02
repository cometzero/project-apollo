"""Bounded, deterministic evaluation of Apollo Lua descriptors, without QBox.

Only supplied source text is executable. Host environment, filesystem, native
modules and processes are unavailable to Lua. Typed snapshots preserve numeric
versus string keys, booleans, empty tables and ordered reset/binding strings.
Object provenance is diagnostic and is excluded from semantic comparisons.
"""
from __future__ import annotations

import json
from functools import lru_cache
import posixpath
from pathlib import Path
import shutil
import subprocess
from typing import Any


class DescriptorError(RuntimeError):
    pass


def lua_literal(value: str) -> str:
    eq = "="
    while f"]{eq}]" in value:
        eq += "="
    return f"[{eq}[{value}]{eq}]"


_EVALUATOR = r'''
local pack = table.pack or function(...) return {n=select('#', ...), ...} end
local unpack_values = unpack or table.unpack
local budget = 0
debug.sethook(function()
    budget = budget + 1
    assert(budget <= 200000, 'Lua instruction budget exceeded')
end, '', 1000)
local origins, wrapped, executed, loading = {}, {}, {}, {}
local env = {
    assert=assert, error=error, ipairs=ipairs, pairs=pairs, next=next,
    tonumber=tonumber, tostring=tostring, type=type, select=select,
    math=math, string=string, table=table, unpack=unpack_values,
    print=function() end, os={getenv=function(name) return injected_env[name] end},
    debug={getinfo=debug.getinfo},
}
env._G = env
local function normalize(path)
    assert(type(path) == 'string' and path:sub(1,1) ~= '/', 'module_outside_root')
    local parts = {}
    for part in path:gmatch('[^/]+') do
        if part == '..' then
            assert(#parts > 0, 'module_outside_root: '..path)
            parts[#parts] = nil
        elseif part ~= '.' then parts[#parts+1] = part end
    end
    return './'..table.concat(parts, '/')
end
local function mark(value, path, line, seen, accuracy)
    if type(value) ~= 'table' or seen[value] then return end
    seen[value] = true
    if value.moduletype and not origins[value] then
        origins[value] = {path=path,line=line,accuracy=accuracy or 'function-scope'}
    end
    for _, child in pairs(value) do mark(child,path,line,seen,accuracy) end
end
local wrap_values
local function wrap(fn, path)
    if wrapped[fn] then return wrapped[fn] end
    local info = debug.getinfo(fn, 'S')
    local own_path = info.source:sub(2)
    if sources[own_path] then path = own_path end
    local result = function(...)
        local arguments = pack(...)
        local caller = debug.getinfo(2, 'Sl')
        local caller_path = caller and caller.source:sub(2)
        if caller_path and sources[caller_path] then
            local seen = {}
            for _, value in pairs(arguments) do
                mark(value,caller_path,caller.currentline,seen,'call-site-scope')
            end
            mark(env.platform,caller_path,caller.currentline,seen,'call-site-scope')
        end
        local results = pack(fn(...))
        local seen = {}
        for i=1,results.n do mark(results[i],path,info.linedefined,seen) end
        for _, value in pairs(arguments) do mark(value,path,info.linedefined,seen) end
        mark(env.platform,path,info.linedefined,seen)
        -- Factories return module APIs; wrap those methods as well so ownership
        -- follows the component function, rather than the factory/aggregator.
        for i=1,results.n do results[i] = wrap_values(results[i],path,{}) end
        return unpack_values(results,1,results.n)
    end
    wrapped[fn], wrapped[result] = result, result
    return result
end
wrap_values = function(value,path,seen)
    if type(value) == 'function' then return wrap(value,path) end
    if type(value) ~= 'table' or seen[value] then return value end
    seen[value] = true
    for key, child in pairs(value) do value[key] = wrap_values(child,path,seen) end
    return value
end
env.dofile = function(path)
    path = normalize(path)
    assert(sources[path], 'source outside allowlist: '..path)
    assert(not loading[path], 'module_cycle: '..path)
    loading[path], executed[path] = true, true
    local fn, err
    if setfenv then
        fn, err = loadstring(sources[path], '@'..path)
        if fn then setfenv(fn, env) end
    else fn, err = load(sources[path], '@'..path, 't', env) end
    assert(fn, err)
    local result = fn()
    loading[path] = nil
    mark(result,path,1,{})
    return wrap_values(result,path,{})
end
env.dofile(entrypoint)
assert(type(env.platform) == 'table', 'entrypoint has no platform table')
local function quoted(s)
    return '"'..s:gsub('[%z\1-\31\\"]', function(c)
        return string.format('\\u%04x',string.byte(c))
    end)..'"'
end
local function number(v)
    assert(v == v and v ~= math.huge and v ~= -math.huge, 'nonfinite number')
    if math.type and math.type(v) == 'integer' then return tostring(v) end
    return string.format('%.17g',v)
end
local function sorted_keys(v)
    local keys = {}
    for key in pairs(v) do
        assert(type(key) == 'string' or type(key) == 'number' or
               type(key) == 'boolean', 'unsupported table key')
        keys[#keys+1] = key
    end
    table.sort(keys,function(a,b)
        if type(a) ~= type(b) then return type(a) < type(b) end
        if type(a) == 'boolean' then return not a and b end
        return a < b
    end)
    return keys
end
local total = 0
local function typed(v,seen)
    total = total + 1
    assert(total < 500000, 'descriptor size budget exceeded')
    local t = type(v)
    if t == 'string' then return '{"type":"string","value":'..quoted(v)..'}' end
    if t == 'boolean' then return '{"type":"boolean","value":'..tostring(v)..'}' end
    if t == 'number' then return '{"type":"number","value":'..quoted(number(v))..'}' end
    assert(t == 'table', 'unsupported descriptor value: '..t)
    assert(not seen[v], 'cyclic platform table')
    seen[v] = true
    local parts = {}
    for _, key in ipairs(sorted_keys(v)) do
        parts[#parts+1] = '{"key":'..typed(key,seen)..',"value":'..typed(v[key],seen)..'}'
    end
    seen[v] = nil
    return '{"type":"table","entries":['..table.concat(parts,',')..']}'
end
local function json(v)
    local t = type(v)
    if t == 'string' then return quoted(v) end
    if t == 'boolean' then return tostring(v) end
    if t == 'number' then return number(v) end
    local parts = {}
    for _, key in ipairs(sorted_keys(v)) do
        parts[#parts+1] = quoted(tostring(key))..':'..json(v[key])
    end
    return '{'..table.concat(parts,',')..'}'
end
local locations = {}
local function collect(v,path)
    if type(v) ~= 'table' then return end
    if v.moduletype then
        locations[path] = origins[v] or {path=entrypoint,line=1,accuracy='file-scope'}
    end
    for key, child in pairs(v) do collect(child,path..'.'..tostring(key)) end
end
local descriptor = typed(env.platform,{})
collect(env.platform,'platform')
io.write('{"descriptor":'..descriptor..',"locations":'..json(locations)..
         ',"executed":'..json(executed)..'}')
'''


def evaluate_modules(
    modules: dict[str, str], *, entrypoint: str = "apollo-qvp.lua",
    environment: dict[str, str] | None = None, timeout: float = 12,
) -> dict[str, Any]:
    lua = next((path for name in ("lua5.4", "lua5.3", "lua", "luajit")
                if (path := shutil.which(name))), None)
    if not lua:
        raise DescriptorError("Lua interpreter missing (install lua5.4 or lua)")
    if sum(len(text) for text in modules.values()) > 8 * 1024 * 1024:
        raise DescriptorError("Lua source budget exceeded")
    env = {"QBOX_RDASPEN_ENABLE_AP_CPUS": "true", **(environment or {})}
    if any(not isinstance(key, str) or not isinstance(value, str)
           for key, value in env.items()):
        raise DescriptorError("environment values must be strings")
    script = "local sources = {\n" + "\n".join(
        f"[ {lua_literal('./' + path.removeprefix('./'))} ]={lua_literal(text)},"
        for path, text in sorted(modules.items())) + "\n}\n"
    script += "local injected_env = {" + ",".join(
        f"[ {lua_literal(key)} ]={lua_literal(value)}" for key, value in sorted(env.items())) + "}\n"
    script += f"local entrypoint = {lua_literal('./' + entrypoint.removeprefix('./'))}\n"
    script += _EVALUATOR
    try:
        result = subprocess.run([lua, "-"], input=script, text=True,
                                capture_output=True, timeout=timeout,
                                env={"PATH": "/usr/bin:/bin", "LANG": "C"})
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise DescriptorError(f"Lua evaluation failed: {type(exc).__name__}") from exc
    if result.returncode:
        raise DescriptorError(f"Lua evaluation failed: {result.stderr[-2000:].strip()}")
    try:
        return json.loads(result.stdout)
    except ValueError as exc:
        raise DescriptorError("Lua evaluation returned invalid JSON") from exc


def read_sources(source_root: Path) -> dict[str, str]:
    """Read an allowlist; execution records distinguish included from unused Lua."""
    root = source_root.resolve()
    sources = {}
    for path in sorted(root.rglob("*.lua")):
        if not path.resolve().is_relative_to(root):
            raise DescriptorError(f"module_outside_root: {path}")
        sources[path.relative_to(root).as_posix()] = path.read_text(encoding="utf-8")
    return sources


def evaluate_source(source_root: Path, **kwargs: Any) -> dict[str, Any]:
    return evaluate_modules(read_sources(source_root), **kwargs)


@lru_cache(maxsize=4)
def _cached_evaluation(sources: tuple[tuple[str, str], ...], entrypoint: str) -> dict:
    return evaluate_modules(dict(sources), entrypoint=entrypoint)


def evaluated_platform(source_root: Path) -> tuple[dict, dict]:
    """Current full-profile defaults, invalidated by source contents on each call."""
    sources = read_sources(source_root)
    entrypoint = ("apollo-qvp-saturn-v.lua" if "apollo-qvp-saturn-v.lua" in sources
                  else "apollo-qvp.lua")
    evaluated = _cached_evaluation(tuple(sources.items()), entrypoint)
    return plain_descriptor(evaluated["descriptor"]), evaluated["locations"]


def plain_descriptor(value: dict[str, Any], *, string_keys: bool = False) -> Any:
    """Decode the typed form for existing map/graph consumers; snapshots stay typed."""
    kind = value["type"]
    if kind == "table":
        result = {}
        for entry in value["entries"]:
            key = plain_descriptor(entry["key"])
            if string_keys:
                key = str(key)
            if key in result:
                raise DescriptorError("key collision in plain descriptor")
            result[key] = plain_descriptor(entry["value"], string_keys=string_keys)
        return result
    if kind == "number":
        number = value["value"]
        return float(number) if any(char in number for char in ".eE") else int(number)
    return value["value"]


def descriptor_differences(before: dict, after: dict, path: str = "platform") -> list[dict]:
    if before == after:
        return []
    if before["type"] != "table" or after["type"] != "table":
        return [{"path": path, "before": before, "after": after}]
    def index(value):
        return {json.dumps(entry["key"], sort_keys=True): entry for entry in value["entries"]}
    left, right = index(before), index(after)
    differences = []
    for key in sorted(left.keys() | right.keys()):
        entry = left.get(key) or right[key]
        typed_key = entry["key"]
        suffix = ("." + typed_key["value"] if typed_key["type"] == "string" else
                  "[" + typed_key["type"] + ":" + str(typed_key["value"]) + "]")
        if key not in left or key not in right:
            differences.append({"path": path + suffix,
                                "before": left[key]["value"] if key in left else None,
                                "after": right[key]["value"] if key in right else None})
        else:
            differences.extend(descriptor_differences(left[key]["value"], right[key]["value"], path + suffix))
    return differences


def normalize_file_paths(value: dict, field: str = "") -> dict:
    """Normalize lexical path components only in declared file-valued fields.

    A file moving from hw-block to vp may derive the same workspace path with
    different ../ spelling. Never normalize CCI names, binding order, QEMU args,
    addresses, device strings or arbitrary scalar values.
    """
    if value["type"] == "table":
        return {"type": "table", "entries": [
            {"key": entry["key"], "value": normalize_file_paths(
                entry["value"], str(entry["key"].get("value", "")))}
            for entry in value["entries"]]}
    if value["type"] != "string":
        return value
    text = value["value"]
    if field == "blkdev_str" and text.startswith("file="):
        file, separator, rest = text[5:].partition(",")
        return {**value, "value": "file=" + posixpath.normpath(file) + separator + rest}
    if (field.endswith(("_file", "_path")) or field in {"otp_image"}) and text:
        return {**value, "value": posixpath.normpath(text)}
    return value
