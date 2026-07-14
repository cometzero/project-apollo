from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from local_debug_components import ComponentRecord
from local_debug_support import gdb_quote


@dataclass(frozen=True)
class DomainSpec:
    name: str
    label: str
    members: tuple[str, ...]
    remote: str


DOMAIN_SPECS = (
    DomainSpec(
        "rse",
        "RSE staged firmware",
        ("tfm-bl1_1", "tfm-bl1_2", "tfm-bl2", "tfm-s"),
        "127.0.0.1:12340",
    ),
    DomainSpec(
        "si0",
        "Safety Island cluster 0",
        ("scp-si0",),
        "127.0.0.1:12341",
    ),
    DomainSpec(
        "si1",
        "Safety Island cluster 1",
        ("si-cl1-zephyr",),
        "127.0.0.1:12342",
    ),
    DomainSpec(
        "ap",
        "Application processor staged firmware and Linux",
        ("tfa-bl2", "tfa-bl31", "optee-core", "u-boot", "linux"),
        "127.0.0.1:12343",
    ),
)


def domain_gdb_lines(
    spec: DomainSpec, records: list[tuple[str, ComponentRecord]]
) -> list[str]:
    primary = records[0][1]
    source_roots = sorted(
        {root for _, record in records for root in record["source_roots"]}
    )
    lines = [
        "set pagination off",
        "set confirm off",
        "set breakpoint pending on",
        "set debuginfod enabled off",
        f"# {spec.label}",
    ]
    lines.extend(f"directory {gdb_quote(Path(root))}" for root in source_roots)
    lines.append(f"file {gdb_quote(Path(primary['elf']))}")
    for _, record in records[1:]:
        lines.append(
            f"add-symbol-file {gdb_quote(Path(record['elf']))} "
            f"{record['text_address']}"
        )
    lines.append("info files")
    for member, record in records:
        symbol = record["default_symbol"]
        if symbol is None:
            continue
        address = record["symbols"][symbol]
        location = record["source_locations"].get(symbol, "source unavailable")
        symbol_file = f"symbol-file {gdb_quote(Path(record['elf']))}"
        if "load_offset" in record:
            symbol_file = (
                f"symbol-file -o {record['load_offset']} "
                f"{gdb_quote(Path(record['elf']))}"
            )
        lines.extend(
            (
                f"echo \\n[{member}] {symbol} at {address} ({location})\\n",
                f"info symbol {address}",
                f"info line *{address}",
                f"break *{address}",
                "commands $bpnum",
                "  silent",
                f"  {symbol_file}",
                f"  echo \\nStopped at [{member}] {symbol}\\n",
                "  info symbol $pc",
                "  info line *$pc",
                "  list *$pc",
                "end",
            )
        )
    lines.extend(("", f"# QEMU GDB endpoint: {spec.remote}"))
    return lines


def make_domain_record(
    spec: DomainSpec,
    script: Path,
    records: list[tuple[str, ComponentRecord]],
) -> ComponentRecord:
    primary = records[0][1]
    symbols: dict[str, str] = {}
    locations: dict[str, str] = {}
    for member, record in records:
        for name, address in record["symbols"].items():
            key = f"{member}:{name}"
            symbols[key] = address
            if name in record["source_locations"]:
                locations[key] = record["source_locations"][name]
    return {
        "label": spec.label,
        "domain": spec.name,
        "target": primary["target"],
        "elf": primary["elf"],
        "gdb_script": str(script),
        "debugger": "gdb-multiarch",
        "arch": primary["arch"],
        "has_symtab": all(record["has_symtab"] for _, record in records),
        "has_debug_info": all(record["has_debug_info"] for _, record in records),
        "has_debug_line": all(record["has_debug_line"] for _, record in records),
        "default_symbol": None,
        "symbols": symbols,
        "text_address": primary["text_address"],
        "source_locations": locations,
        "source_roots": sorted(
            {root for _, record in records for root in record["source_roots"]}
        ),
        "members": [member for member, _ in records],
        "remote": spec.remote,
    }


def add_domain_records(
    out_dir: Path, components: dict[str, ComponentRecord]
) -> None:
    for spec in DOMAIN_SPECS:
        records = [
            (name, components[name]) for name in spec.members if name in components
        ]
        if not records:
            continue
        script = out_dir / "gdb" / f"domain-{spec.name}.gdb"
        script.parent.mkdir(parents=True, exist_ok=True)
        script.write_text(
            "\n".join(domain_gdb_lines(spec, records)) + "\n", encoding="utf-8"
        )
        components[f"domain-{spec.name}"] = make_domain_record(
            spec, script, records
        )
