from __future__ import annotations
from dataclasses import dataclass
from typing import Literal

ViewKind = Literal["register", "memory"]

@dataclass(frozen=True, slots=True)
class ViewSpec:
    view_id: str
    target: str
    kind: ViewKind
    value: str
    address: int | None = None
    width: int | None = None
    memory_space: str | None = None

@dataclass(frozen=True, slots=True)
class SampleSpec:
    name: str
    component: str
    symbol: str

def parse_view(spec: str) -> ViewSpec:
    view_id, separator, body = spec.partition("=")
    if not separator or not view_id or not body:
        raise ValueError("view must be ID=TARGET:register:NAME or ID=TARGET:memory:ADDRESS:WIDTH")
    target, separator, remainder = body.partition(":register:")
    if separator:
        if not target or not remainder:
            raise ValueError("register view requires target and register name")
        return ViewSpec(view_id, target, "register", remainder)
    target, separator, remainder = body.partition(":memory:")
    if not separator:
        raise ValueError("view kind must be register or memory")
    parts = remainder.split(":")
    if len(parts) == 2:
        space, address_text, width_text = "SP", parts[0], parts[1]
    elif len(parts) == 3:
        space, address_text, width_text = parts
    else:
        raise ValueError("memory view requires target, optional SP/NP space, address, and width")
    address, width = int(address_text, 0), int(width_text, 0)
    if not target or width not in {1, 2, 4, 8}:
        raise ValueError("memory view requires target and width 1, 2, 4, or 8")
    return ViewSpec(view_id, target, "memory", address_text, address, width, space)

def parse_sample(spec: str) -> SampleSpec:
    name, separator, location = spec.partition("=")
    component, symbol_separator, symbol = location.partition(":")
    if not separator or not name or not symbol_separator or not component or not symbol:
        raise ValueError("sample must be NAME=COMPONENT:SYMBOL")
    return SampleSpec(name, component, symbol)
