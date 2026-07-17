#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
from typing import Any


DESCRIPTION = "Validate Apollo QBox PCIe MSI-X/LPI and legacy INTx evidence."
GIC_SPI_INTID_BASE = 32
LEGACY_INTX_SPI = 301
LEGACY_INTX_INTID = GIC_SPI_INTID_BASE + LEGACY_INTX_SPI
ANSI_RE = re.compile(r"\x1b\[[0-?]*[ -/]*[@-~]")
IRQ_RE = re.compile(
    r"^\s*(?P<irq>\d+):\s+"
    r"(?P<cpu0>\d+)\s+(?P<cpu1>\d+)\s+"
    r"(?P<cpu2>\d+)\s+(?P<cpu3>\d+)\s+"
    r"(?P<tail>.*)$"
)
BDF_RE = re.compile(
    r"^__QBOX_PCIE_BDF__:(?P<domain>[0-9a-f]{4}):"
    r"(?P<bus>[0-9a-f]{2}):(?P<device>[0-9a-f]{2})\."
    r"(?P<function>[0-7])$",
    re.MULTILINE | re.IGNORECASE,
)


def clean_text(value: str) -> str:
    return ANSI_RE.sub("", value).replace("\r", "")


def read_log(path: Path) -> str:
    return clean_text(path.read_text(encoding="utf-8", errors="replace"))


def marker_value(text: str, marker: str) -> str:
    match = re.search(rf"^{re.escape(marker)}:(.*)$", text, re.MULTILINE)
    return match.group(1).strip() if match else ""


def section(text: str, start: str, end: str) -> str:
    start_index = text.find(start)
    if start_index < 0:
        return ""
    start_index = text.find("\n", start_index)
    if start_index < 0:
        return ""
    end_index = text.find(end, start_index + 1)
    if end_index < 0:
        return ""
    return text[start_index + 1 : end_index]


def parse_interrupts(value: str) -> dict[int, dict[str, Any]]:
    result: dict[int, dict[str, Any]] = {}
    for line in value.splitlines():
        match = IRQ_RE.match(line)
        if match is None:
            continue
        irq = int(match.group("irq"))
        result[irq] = {
            "counts": [
                int(match.group(f"cpu{cpu}"))
                for cpu in range(4)
            ],
            "tail": match.group("tail").strip(),
            "line": line.strip(),
        }
    return result


def bdf_identity(text: str) -> dict[str, Any]:
    match = BDF_RE.search(text)
    if match is None:
        return {}
    bus = int(match.group("bus"), 16)
    device = int(match.group("device"), 16)
    function = int(match.group("function"), 16)
    return {
        "bdf": (
            f"{match.group('domain').lower()}:{bus:02x}:"
            f"{device:02x}.{function}"
        ),
        "device_id": (bus << 8) | (device << 3) | function,
    }


def interrupt_delta(
    text: str,
    *,
    mode: str,
) -> dict[str, Any]:
    before = parse_interrupts(
        section(
            text,
            "__QBOX_PCIE_IRQ_BEFORE__",
            "__QBOX_PCIE_IRQ_BEFORE_END__",
        )
    )
    after = parse_interrupts(
        section(
            text,
            "__QBOX_PCIE_IRQ_AFTER__",
            "__QBOX_PCIE_IRQ_AFTER_END__",
        )
    )
    candidates: list[dict[str, Any]] = []
    for irq in sorted(before.keys() & after.keys()):
        before_item = before[irq]
        after_item = after[irq]
        tail = str(after_item["tail"])
        if "virtio" not in tail.lower():
            continue
        if mode == "msix" and re.search(
            r"\bITS(?:-PCI)?-MSI(?:X)?\b", tail
        ) is None:
            continue
        if mode == "intx" and (
            "gic" not in tail.lower()
            or re.search(rf"\b{LEGACY_INTX_INTID}\b", tail) is None
        ):
            continue
        deltas = [
            after_item["counts"][cpu] - before_item["counts"][cpu]
            for cpu in range(4)
        ]
        candidates.append(
            {
                "irq": irq,
                "before": before_item["counts"],
                "after": after_item["counts"],
                "delta": deltas,
                "total_delta": sum(deltas),
                "tail": tail,
            }
        )
    if not candidates:
        return {
            "irq": None,
            "cpu0_delta": 0,
            "total_delta": 0,
            "candidates": [],
        }
    selected = max(candidates, key=lambda item: item["total_delta"])
    return {
        **selected,
        "cpu0_delta": selected["delta"][0],
        "candidates": candidates,
    }


def validate_mode(path: Path, mode: str) -> dict[str, Any]:
    text = read_log(path)
    identity = bdf_identity(text)
    delta = interrupt_delta(text, mode=mode)
    begin = f"__QBOX_PCIE_IRQ_TEST_BEGIN__:{mode}" in text
    done = f"__QBOX_PCIE_IRQ_TEST_DONE__:{mode}" in text
    iface = marker_value(text, "__QBOX_PCIE_IFACE__")
    checks = {
        "begin_marker": begin,
        "done_marker": done,
        "endpoint_bdf": identity.get("bdf") == "0000:00:01.0",
        "endpoint_iface": bool(iface),
        "interrupt_increment": delta["total_delta"] > 0,
        "cpu0_increment": delta["cpu0_delta"] > 0,
    }
    if mode == "msix":
        checks["msix_enabled"] = bool(
            "MSI-X: Enable+" in text
            or (
                delta.get("tail")
                and re.search(
                    r"\bITS(?:-PCI)?-MSI(?:X)?\b",
                    str(delta["tail"]),
                )
            )
        )
        checks["its_lpi"] = bool(
            delta.get("tail")
            and re.search(
                r"\bITS(?:-PCI)?-MSI(?:X)?\b",
                str(delta["tail"]),
            )
        )
    else:
        checks["pci_nomsi"] = "pci=nomsi" in marker_value(
            text, "__QBOX_PCIE_CMDLINE__"
        ).split()
        checks["legacy_spi_301"] = bool(
            delta.get("tail")
            and re.search(
                rf"\b{LEGACY_INTX_INTID}\b",
                str(delta["tail"]),
            )
        )
    return {
        "status": "pass" if all(checks.values()) else "fail",
        "path": str(path.resolve()),
        "mode": mode,
        "identity": identity,
        "iface": iface,
        "irq": delta.get("irq"),
        "cpu0_delta": delta["cpu0_delta"],
        "total_delta": delta["total_delta"],
        "irq_evidence": delta,
        "checks": checks,
    }


def validate_pair(msix_log: Path, intx_log: Path) -> dict[str, Any]:
    msix = validate_mode(msix_log, "msix")
    intx = validate_mode(intx_log, "intx")
    same_endpoint = (
        msix["identity"].get("bdf")
        and msix["identity"] == intx["identity"]
    )
    identity = {
        **msix["identity"],
        "stream_id": 0x0040,
        "event_id_base": 0,
        "its_translator": "0x20850040",
        "legacy_intx_spi": LEGACY_INTX_SPI,
        "legacy_intx_intid": LEGACY_INTX_INTID,
    }
    checks = {
        "msix_lpi": msix["status"] == "pass",
        "legacy_intx": intx["status"] == "pass",
        "same_endpoint": bool(same_endpoint),
        "device_id": identity.get("device_id") == 0x0008,
    }
    return {
        "schema_version": 1,
        "status": "pass" if all(checks.values()) else "fail",
        "identity": identity,
        "msix": msix,
        "intx": intx,
        "checks": checks,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=DESCRIPTION)
    parser.add_argument("--msix-log", type=Path, required=True)
    parser.add_argument("--intx-log", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    result = validate_pair(args.msix_log.resolve(), args.intx_log.resolve())
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(args.output)
    return 0 if result["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
