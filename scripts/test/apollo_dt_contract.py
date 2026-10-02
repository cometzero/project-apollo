#!/usr/bin/env python3
"""Compare compiled Apollo DT contracts and validate SoC/board composition.

Only reference cells identified by their property binding become node paths.
Unknown properties stay byte-exact; this deliberately fails closed when a new
phandle binding needs support. No dtc/libfdt Python package is needed at runtime.
"""
from __future__ import annotations

import argparse
from dataclasses import dataclass, field
import hashlib
import json
from pathlib import Path
import re
import struct
from typing import Any


class ContractError(ValueError):
    """Malformed FDT or reference encoding; equivalence cannot be established."""


@dataclass
class Node:
    path: str
    properties: dict[str, bytes] = field(default_factory=dict)
    children: list[str] = field(default_factory=list)


@dataclass
class Tree:
    nodes: dict[str, Node]
    reservations: tuple[tuple[int, int], ...] = ()
    boot_cpu: int = 0

    @classmethod
    def read(cls, path: str | Path) -> Tree:
        return cls.parse(Path(path).read_bytes())

    @classmethod
    def parse(cls, data: bytes) -> Tree:
        if len(data) < 40:
            raise ContractError("truncated FDT header")
        magic, total, off_struct, off_strings, off_reserve, version, compatible, boot, strings_size, struct_size = struct.unpack_from(
            ">10I", data
        )
        if magic != 0xD00DFEED or version < 17 or compatible > 17:
            raise ContractError("requires a version 17 compatible FDT")
        if total > len(data) or total < 40:
            raise ContractError("invalid FDT total size")
        for name, offset, size in (
            ("structure", off_struct, struct_size),
            ("strings", off_strings, strings_size),
        ):
            if offset < 40 or offset + size > total:
                raise ContractError(f"invalid FDT {name} block bounds")
        if off_struct % 4 or off_reserve < 40 or off_reserve % 8:
            raise ContractError("invalid FDT block alignment")
        ranges = [(off_struct, off_struct + struct_size), (off_strings, off_strings + strings_size)]
        reservations = []
        pos = off_reserve
        while True:
            if pos + 16 > total or any(pos < end and pos + 16 > start for start, end in ranges):
                raise ContractError("unterminated or overlapping FDT reservation map")
            address, size = struct.unpack_from(">QQ", data, pos)
            pos += 16
            if address == size == 0:
                break
            reservations.append((address, size))
        if ranges[0][0] < ranges[1][1] and ranges[0][1] > ranges[1][0]:
            raise ContractError("overlapping FDT structure and strings blocks")
        strings = data[off_strings:off_strings + strings_size]
        block = data[off_struct:off_struct + struct_size]
        nodes: dict[str, Node] = {}
        stack: list[Node] = []
        pos = 0
        ended = False
        while pos + 4 <= len(block):
            token = struct.unpack_from(">I", block, pos)[0]
            pos += 4
            if token == 1:  # FDT_BEGIN_NODE
                end = block.find(b"\0", pos)
                if end < 0:
                    raise ContractError("unterminated FDT node name")
                try:
                    name = block[pos:end].decode("ascii")
                except UnicodeDecodeError as exc:
                    raise ContractError("non-ASCII FDT node name") from exc
                if "/" in name or (not stack and (nodes or name)):
                    raise ContractError("invalid FDT root or node name")
                if stack and not name:
                    raise ContractError("empty child node name")
                path = (stack[-1].path.rstrip("/") + "/" + name) if stack else "/"
                if path in nodes:
                    raise ContractError(f"duplicate node: {path}")
                node = Node(path)
                nodes[path] = node
                if stack:
                    stack[-1].children.append(path)
                stack.append(node)
                pos = (end + 4) & ~3
            elif token == 2:  # FDT_END_NODE
                if not stack:
                    raise ContractError("unbalanced FDT_END_NODE")
                stack.pop()
            elif token == 3:  # FDT_PROP
                if not stack or pos + 8 > len(block):
                    raise ContractError("property outside a node or truncated header")
                length, name_offset = struct.unpack_from(">II", block, pos)
                pos += 8
                end = strings.find(b"\0", name_offset)
                if name_offset >= len(strings) or end < 0 or pos + length > len(block):
                    raise ContractError("invalid FDT property bounds")
                try:
                    name = strings[name_offset:end].decode("ascii")
                except UnicodeDecodeError as exc:
                    raise ContractError("non-ASCII FDT property name") from exc
                if not name or name in stack[-1].properties:
                    raise ContractError(f"empty or duplicate property: {stack[-1].path}:{name}")
                stack[-1].properties[name] = block[pos:pos + length]
                pos = (pos + length + 3) & ~3
            elif token == 4:  # FDT_NOP
                continue
            elif token == 9:  # FDT_END
                if stack or "/" not in nodes:
                    raise ContractError("incomplete FDT node structure")
                ended = True
                break
            else:
                raise ContractError(f"unknown FDT token: {token}")
        if not ended:
            raise ContractError("missing FDT_END")
        return cls(nodes, tuple(reservations), boot)

    def available(self, path: str) -> bool:
        while True:
            node = self.nodes.get(path)
            if node is None or node.properties.get("status") not in (None, b"okay\0", b"ok\0"):
                return False
            if path == "/":
                return True
            path = path.rsplit("/", 1)[0] or "/"


def cells(data: bytes, location: str) -> tuple[int, ...]:
    if len(data) % 4:
        raise ContractError(f"{location}: non-cell-aligned property")
    return struct.unpack(f">{len(data) // 4}I", data)


def strings(data: bytes, location: str) -> tuple[str, ...]:
    if not data or data[-1:] != b"\0":
        raise ContractError(f"{location}: invalid string property")
    try:
        return tuple(part.decode("utf-8") for part in data[:-1].split(b"\0"))
    except UnicodeDecodeError as exc:
        raise ContractError(f"{location}: invalid UTF-8 string") from exc


# Provider argument counts apply to each specifier independently, not to a
# guessed fixed stride across the property. GPIO ranges and PCI maps instead
# have their own fixed tuple formats (Linux of_map_id() consumes four cells).
PROVIDER_CELLS = {
    "clocks": "#clock-cells", "assigned-clocks": "#clock-cells",
    "assigned-clock-parents": "#clock-cells", "dmas": "#dma-cells",
    "mboxes": "#mbox-cells", "sound-dai": "#sound-dai-cells",
    "iommus": "#iommu-cells", "resets": "#reset-cells",
    "power-domains": "#power-domain-cells", "phys": "#phy-cells",
    "interconnects": "#interconnect-cells", "io-channels": "#io-channel-cells",
    "thermal-sensors": "#thermal-sensor-cells", "pwms": "#pwm-cells",
    "interrupts-extended": "#interrupt-cells", "msi-parent": "#msi-cells",
}
REFERENCE_LISTS = {
    "cpu", "cpus", "next-level-cache", "cpu-idle-states", "memory-region",
    "shmem", "interrupt-parent", "remote-endpoint", "operating-points-v2",
    "bitclock-master", "frame-master", "simple-audio-card,bitclock-master",
    "simple-audio-card,frame-master",
}
SINGLE_REFERENCES = {"cpu", "next-level-cache", "interrupt-parent", "remote-endpoint"}
NULL_SPECIFIERS = {"assigned-clocks", "assigned-clock-parents"}


class Resolver:
    def __init__(self, tree: Tree, disabled_pmu_reference: Tree | None = None):
        self.tree = tree
        self.disabled_pmu_reference = disabled_pmu_reference
        self.source_phandles = Resolver(disabled_pmu_reference).phandles if disabled_pmu_reference else {}
        self.removed_cpu_references: list[tuple[str, str]] = []
        self.phandles: dict[int, str] = {}
        for path, node in tree.nodes.items():
            values = []
            for name in ("phandle", "linux,phandle"):
                if name not in node.properties:
                    continue
                value = cells(node.properties[name], f"{path}:{name}")
                if len(value) != 1 or value[0] in (0, 0xFFFFFFFF):
                    raise ContractError(f"{path}:{name}: invalid phandle")
                values.append(value[0])
            if len(set(values)) > 1:
                raise ContractError(f"{path}: inconsistent phandle aliases")
            if values:
                value = values[0]
                if value in self.phandles:
                    raise ContractError(f"duplicate phandle {value:#x}")
                self.phandles[value] = path

    def target(self, value: int, location: str) -> str:
        if value not in self.phandles:
            raise ContractError(f"{location}: unresolved phandle {value:#x}")
        return self.phandles[value]

    def count(self, path: str, name: str, default: int | None = None) -> int:
        data = self.tree.nodes[path].properties.get(name)
        if data is None:
            if default is None:
                raise ContractError(f"{path}: missing provider {name}")
            return default
        value = cells(data, f"{path}:{name}")
        if len(value) != 1 or value[0] > 64:
            raise ContractError(f"{path}:{name}: invalid cell count")
        return value[0]

    def references(self, path: str, name: str, data: bytes) -> tuple[Any, ...] | None:
        location = f"{path}:{name}"
        provider = PROVIDER_CELLS.get(name)
        if name == "gpios" or name.endswith("-gpios"):
            provider = "#gpio-cells"
        plain = name in REFERENCE_LISTS or bool(re.fullmatch(r"pinctrl-\d+", name)) or name.endswith("-supply")
        if not (provider or plain or name in {"interrupt-map", "msi-map", "iommu-map", "gpio-ranges"}):
            return None
        # Some audio bindings also allow a zero-length master flag.
        if not data and name.endswith("master"):
            return None
        values = cells(data, location)
        output: list[Any] = []
        index = 0
        if name in SINGLE_REFERENCES or name.endswith("-supply"):
            if len(values) != 1:
                raise ContractError(f"{location}: expected one reference")
        while index < len(values):
            prefix = 0
            if name == "interrupt-map":
                prefix = self.count(path, "#address-cells", 2) + self.count(path, "#interrupt-cells")
            elif name in {"msi-map", "iommu-map"}:
                prefix = 1
            if index + prefix >= len(values):
                raise ContractError(f"{location}: truncated map key or phandle")
            output.extend(values[index:index + prefix])
            index += prefix
            value = values[index]
            index += 1
            if value == 0 and (name in NULL_SPECIFIERS or provider == "#gpio-cells"):
                output.append(("null",))
                continue
            if value not in self.phandles and self.disabled_pmu_reference is not None:
                source_target = self.source_phandles.get(value)
                props = self.tree.nodes[path].properties
                # prepare.py intentionally leaves CPU lists on disabled DSU PMUs.
                # A source DTB can recover these removed CPU identities only;
                # never tolerate an enabled consumer or another dangling binding.
                if (name == "cpus" and re.fullmatch(r"/dsu-pmu-[0-3]", path)
                        and not self.tree.available(path)
                        and b"arm,dsu-pmu\0" in props.get("compatible", b"")
                        and source_target is not None and source_target not in self.tree.nodes
                        and self.disabled_pmu_reference.nodes[source_target].properties.get("device_type") == b"cpu\0"):
                    output.append(("removed-cpu", source_target))
                    self.removed_cpu_references.append((location, source_target))
                    continue
            target = self.target(value, location)
            output.append(("ref", target))
            if name == "interrupt-map":
                count = self.count(target, "#address-cells", 0) + self.count(target, "#interrupt-cells")
            elif name in {"msi-map", "iommu-map"}:
                count = 2  # output ID base and range length, not provider args
            elif name == "gpio-ranges":
                count = 3  # GPIO offset, pin offset and pin count
            elif provider:
                count = self.count(target, provider, 0 if name == "msi-parent" else None)
            else:
                count = 0
            if index + count > len(values):
                raise ContractError(f"{location}: truncated specifier for {target}")
            output.extend(values[index:index + count])
            index += count
        return tuple(output)

    def normalized(self, path: str, name: str, data: bytes) -> Any:
        references = self.references(path, name, data)
        return ("cells", references) if references is not None else ("bytes", data.hex())


SOC_OPTIONAL = frozenset({
    "/soc/serial@1a400000", "/soc/gpio@40750000", "/soc/iommu@1c0000000",
    "/soc/dma-controller@31000000", "/soc/dma-controller@31010000",
    "/soc/gpio@301e0000", "/soc/gpio@301f0000", "/soc/si_remoteproc",
    "/soc/si_remoteproc/si-cl1", "/soc/mailbox@400b0000", "/soc/mailbox@400e0000",
    "/reserved-memory/rsctbl@100000", "/reserved-memory/vdev0vring0@120000",
    "/reserved-memory/vdev0vring1@140000", "/reserved-memory/vdev0buffer@160000",
    *(f"/soc/i2c@{0x30100000 + n * 0x10000:x}" for n in range(6)),
    *(f"/soc/spi@{0x30160000 + n * 0x10000:x}" for n in range(4)),
    *(f"/soc/serial@{0x301A0000 + n * 0x10000:x}" for n in range(4)),
    "/soc/i2s@30200000", "/soc/i2s@30210000",
})
VP_OPTIONAL = frozenset({"/soc/pcie@43b50000", "/soc/pcie-epc@30300000", "/i2s0-sound", "/i2s1-sound"})
APPROVED_STATUS = SOC_OPTIONAL | VP_OPTIONAL
PIN_BANKS = {"/soc/gpio@301e0000": (8,) * 6 + (1,) * 8,
             "/soc/gpio@301f0000": (8,) * 4 + (1,) * 4}


EFI_RUNTIME_VALUES = {
    "linux,uefi-mmap-start": (8, "EFI memory map allocation address varies per boot"),
    "linux,uefi-mmap-size": (4, "EFI allocation map length varies per boot"),
    "linux,uefi-system-table": (8, "EFI system table address varies per boot"),
    "smbios3-entrypoint": (8, "SMBIOS table allocation address varies per boot"),
    "kaslr-seed": (8, "firmware supplies a fresh random seed per boot"),
}


def compare_trees(
    before: Tree, after: Tree, *, allow_added_symbols: bool = False,
    ignore_efi_runtime: bool = False,
    baseline_reference: Tree | None = None, candidate_reference: Tree | None = None,
) -> list[str]:
    if (baseline_reference is None) != (candidate_reference is None):
        raise ContractError("both source DTB companions are required for disabled PMU references")
    old, new = Resolver(before, baseline_reference), Resolver(after, candidate_reference)
    differences = []
    paths_old, paths_new = set(before.nodes), set(after.nodes)
    if allow_added_symbols and "/__symbols__" not in paths_old:
        paths_new.discard("/__symbols__")
    for path in sorted(paths_old - paths_new):
        differences.append(f"missing node: {path}")
    for path in sorted(paths_new - paths_old):
        differences.append(f"added node: {path}")
    for path in sorted(paths_old & paths_new):
        a = {k: v for k, v in before.nodes[path].properties.items() if k not in {"phandle", "linux,phandle"}}
        b = {k: v for k, v in after.nodes[path].properties.items() if k not in {"phandle", "linux,phandle"}}
        if path in APPROVED_STATUS:
            # This is the only availability equivalence approved by the plan.
            if a.get("status") == b"okay\0":
                a.pop("status")
            if b.get("status") == b"okay\0":
                b.pop("status")
        for name in sorted(a.keys() | b.keys()):
            if name not in a:
                if not (path == "/__symbols__" and allow_added_symbols):
                    differences.append(f"added property: {path}:{name}")
            elif name not in b:
                differences.append(f"missing property: {path}:{name}")
            elif ignore_efi_runtime and path == "/chosen" and name in EFI_RUNTIME_VALUES:
                width, _reason = EFI_RUNTIME_VALUES[name]
                if len(a[name]) != width or len(b[name]) != width:
                    raise ContractError(f"{path}:{name}: invalid EFI runtime value width")
                if name != "kaslr-seed" and (not any(a[name]) or not any(b[name])):
                    raise ContractError(f"{path}:{name}: zero EFI runtime pointer/size")
            elif old.normalized(path, name, a[name]) != new.normalized(path, name, b[name]):
                differences.append(f"changed property: {path}:{name}")
    for tree, resolver in ((before, old), (after, new)):
        # Validate even properties on added/missing nodes and symbol targets.
        for path, node in tree.nodes.items():
            for name, value in node.properties.items():
                resolver.references(path, name, value)
                if path == "/__symbols__":
                    target = strings(value, f"{path}:{name}")
                    if len(target) != 1 or target[0] not in tree.nodes:
                        raise ContractError(f"{path}:{name}: invalid symbol target")
    def cpu_order(tree: Tree) -> list[str]:
        node = tree.nodes.get("/cpus")
        return [path for path in node.children if tree.nodes[path].properties.get("device_type") == b"cpu\0"] if node else []
    if cpu_order(before) != cpu_order(after):
        differences.append("changed CPU declaration order: /cpus")
    if before.reservations != after.reservations:
        differences.append("changed FDT memory reservation map")
    if before.boot_cpu != after.boot_cpu:
        differences.append("changed FDT boot CPU ID")
    return differences


def bank_issues(tree: Tree, resolver: Resolver) -> list[str]:
    issues = []
    for parent, widths in PIN_BANKS.items():
        if parent not in tree.nodes:
            issues.append(f"missing pin controller: {parent}")
            continue
        banks = [path for path in tree.nodes[parent].children if "gpio-controller" in tree.nodes[path].properties]
        expected = [f"{parent}/gpio@{i:x}" for i in range(len(widths))]
        if banks != expected:
            issues.append(f"changed GPIO bank topology/order: {parent}")
        offset = 0
        for i, width in enumerate(widths):
            path = expected[i]
            if path in tree.nodes:
                props = tree.nodes[path].properties
                if props.get("status") not in (None, b"okay\0", b"ok\0"):
                    issues.append(f"disabled GPIO bank: {path}")
                if cells(props.get("reg", b""), f"{path}:reg") != (i,):
                    issues.append(f"changed GPIO bank index: {path}")
                if cells(props.get("hsoc,npins", b""), f"{path}:hsoc,npins") != (width,):
                    issues.append(f"changed GPIO bank width: {path}")
                ranges = resolver.references(path, "gpio-ranges", props.get("gpio-ranges", b""))
                if ranges != (("ref", parent), 0, offset, width):
                    issues.append(f"changed GPIO pin range: {path}")
            offset += width
    return issues


def dependency_issues(tree: Tree) -> list[str]:
    resolver = Resolver(tree)
    issues = []
    for path, node in tree.nodes.items():
        for name, value in node.properties.items():
            refs = resolver.references(path, name, value)
            if refs is None or not tree.available(path):
                continue
            for ref in refs:
                if isinstance(ref, tuple) and ref[0] == "ref" and not tree.available(ref[1]):
                    issues.append(f"unavailable dependency: {path}:{name} -> {ref[1]}")
    return issues


def validate_soc(tree: Tree) -> list[str]:
    resolver = Resolver(tree)
    issues = dependency_issues(tree) + bank_issues(tree, resolver)
    for path in sorted(SOC_OPTIONAL):
        node = tree.nodes.get(path)
        if node is None or node.properties.get("status") != b"disabled\0":
            issues.append(f"SoC optional node must exist and be disabled: {path}")
    forbidden = {"atmel,24c02", "nxp,pca9539", "virtio,mmio", "qbox,pcie-epc",
                 "pci-host-ecam-generic", "linux,spi-loopback-test", "linux,spdif-dit",
                 "linux,spdif-dir", "simple-audio-card", "arm,idle-state", "domain-idle-state"}
    for path, node in tree.nodes.items():
        compatible = strings(node.properties["compatible"], f"{path}:compatible") if "compatible" in node.properties else ()
        if (forbidden.intersection(compatible) or any("tps6594" in item for item in compatible)
                or path in {"/clock-1536000", "/chosen", "/aliases"}
                or path.startswith("/memory@")):
            issues.append(f"board/VP node leaked into SoC: {path}")
    for name in ("model", "compatible"):
        if name in tree.nodes["/"].properties:
            issues.append(f"board identity leaked into SoC: /:{name}")
    for path in ("/clock-24000000", "/cpus", "/soc/interrupt-controller@20800000", "/timer", "/firmware/scmi"):
        if not tree.available(path):
            issues.append(f"unavailable SoC foundation: {path}")
    return issues


def validate_board(tree: Tree) -> list[str]:
    resolver = Resolver(tree)
    issues = dependency_issues(tree) + bank_issues(tree, resolver)
    for path in sorted(APPROVED_STATUS):
        if not tree.available(path):
            issues.append(f"Saturn-V required node unavailable: {path}")
    for path, node in tree.nodes.items():
        compatible = strings(node.properties["compatible"], f"{path}:compatible") if "compatible" in node.properties else ()
        if any("tps6594" in item for item in compatible):
            issues.append(f"SI-owned PMIC must not be populated by Linux: {path}")
    for bus in range(6):
        parent = f"/soc/i2c@{0x30100000 + bus * 0x10000:x}"
        for address in ((0x50, 0x51, 0x52) if bus == 0 else (0x50,)):
            path = f"{parent}/eeprom@{address:x}"
            if not tree.available(path):
                issues.append(f"missing/unavailable board EEPROM: {path}")
    if not tree.available("/soc/i2c@30100000/gpio@74"):
        issues.append("missing/unavailable board PCA9539: /soc/i2c@30100000/gpio@74")
    return issues


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, help="also save JSON evidence")
    commands = parser.add_subparsers(dest="command", required=True)
    compare = commands.add_parser("compare", help="compare complete effective DT contracts")
    compare.add_argument("baseline", type=Path)
    compare.add_argument("candidate", type=Path)
    compare.add_argument("--allow-added-symbols", action="store_true", help="permit new labels only; old label paths remain exact")
    compare.add_argument("--ignore-efi-runtime", action="store_true", help="live-vs-live: normalize five documented EFI pointer/size/seed values; retain property presence, widths and bootargs")
    compare.add_argument("--baseline-reference", type=Path, help="original baseline DTB before AP-only CPU pruning")
    compare.add_argument("--candidate-reference", type=Path, help="original candidate DTB; recover only removed CPU references on disabled DSU PMUs")
    for name in ("soc", "board"):
        commands.add_parser(name, help=f"validate {name} composition").add_argument("dtb", type=Path)
    args = parser.parse_args(argv)
    paths = [args.baseline, args.candidate] if args.command == "compare" else [args.dtb]
    result: dict[str, Any] = {"command": args.command, "status": "FAIL", "inputs": []}
    try:
        for path in paths:
            result["inputs"].append({"path": str(path), "sha256": hashlib.sha256(path.read_bytes()).hexdigest()})
        trees = [Tree.read(path) for path in paths]
        if args.command == "compare":
            baseline_reference = Tree.read(args.baseline_reference) if args.baseline_reference else None
            candidate_reference = Tree.read(args.candidate_reference) if args.candidate_reference else None
            issues = compare_trees(*trees, allow_added_symbols=args.allow_added_symbols, ignore_efi_runtime=args.ignore_efi_runtime, baseline_reference=baseline_reference, candidate_reference=candidate_reference)
            if baseline_reference is not None and candidate_reference is not None:
                result["disabled_pmu_reference_policy"] = "Only disabled /dsu-pmu-[0-3]:cpus may retain references to CPU nodes removed by prepare.py"
                result["source_companions"] = [{"path": str(path), "sha256": hashlib.sha256(path.read_bytes()).hexdigest()} for path in (args.baseline_reference, args.candidate_reference)]
            if args.ignore_efi_runtime:
                result["efi_runtime_policy"] = {name: reason for name, (_width, reason) in EFI_RUNTIME_VALUES.items()}
        else:
            issues = (validate_soc if args.command == "soc" else validate_board)(trees[0])
        result.update(status="FAIL" if issues else "PASS", issues=issues, node_counts=[len(tree.nodes) for tree in trees])
    except (OSError, ContractError) as exc:
        result["error"] = str(exc)
    output = json.dumps(result, indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(output)
    print(output, end="")
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
