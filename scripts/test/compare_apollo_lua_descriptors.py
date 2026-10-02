#!/usr/bin/env python3
"""Capture/compare complete typed Apollo descriptors across supported profiles."""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path

from apollo_lua_descriptor import (
    DescriptorError, descriptor_differences, evaluate_modules, read_sources,
    normalize_file_paths,
)


def profile_matrix() -> list[dict]:
    cases = []
    for cpus in (1, 4, 16):
        cases.append({"name": f"full-ap{cpus}", "entrypoint": "apollo-qvp.lua",
                      "environment": {"QBOX_APOLLO_NUM_CPUS": str(cpus)}})
        for disk in (False, True):
            cases.append({"name": f"linux-ap{cpus}-{'disk' if disk else 'no-disk'}",
                          "entrypoint": "apollo-qvp-linux.lua",
                          "environment": {
                              "QBOX_APOLLO_NUM_CPUS": str(cpus),
                              "QBOX_RDASPEN_ROOTFS": "/descriptor/rootfs.wic" if disk else "",
                              "QBOX_LINUX_BOOT_STUB": "/descriptor/boot.bin",
                              "QBOX_LINUX_KERNEL": "/descriptor/Image",
                              "QBOX_LINUX_DTB": "/descriptor/linux.dtb",
                          }})
    alternates = {
        "rse-systemc-local": {"QBOX_RDASPEN_RSE_FLASH_BACKEND": "systemc-strata"},
        "rse-systemc-remote": {"QBOX_RDASPEN_RSE_FLASH_BACKEND": "systemc-strata",
                               "QBOX_RDASPEN_RSE_LOCAL_BOOT_FLASH": "false",
                               "QBOX_RDASPEN_RSE_LOCAL_CRYPTO": "false"},
        "rse-local-counter": {"QBOX_APOLLO_RSE_SMD_COUNTER_MIRROR": "false"},
        "rse-split-tcm": {"QBOX_RDASPEN_RSE_SPLIT_CPU0_ITCM_ALIAS": "true",
                          "QBOX_RDASPEN_RSE_SPLIT_CPU0_DTCM_ALIAS": "true"},
        "monitor": {"QBOX_APOLLO_MONITOR": "true"},
        "qmp": {"QBOX_APOLLO_QMP_DIR": "/descriptor/qmp"},
        "injection": {"QBOX_APOLLO_MONITOR": "true", "QBOX_APOLLO_RUNTIME_INJECTION": "true"},
        "pcie-irq": {"QBOX_APOLLO_PCIE_IRQ_TEST": "true"},
        "pcie-endpoints": {"QBOX_APOLLO_PCIE_TEST_ENDPOINTS": "true",
                           "QBOX_APOLLO_PCIE_BIFURCATION": "port2"},
        "pcie-ep": {"QBOX_APOLLO_PCIE_EP_LOOPBACK": "true"},
        "nvme": {"QBOX_APOLLO_NVME_IMAGE": "/descriptor/nvme.raw"},
        "fault-observer": {"QBOX_APOLLO_FAULT_EVENT_TEST": "true"},
    }
    cases.extend({"name": "full-" + name, "entrypoint": "apollo-qvp.lua",
                  "environment": env} for name, env in alternates.items())
    cases.append({"name": "linux-monitor-qmp", "entrypoint": "apollo-qvp-linux.lua",
                  "environment": {"QBOX_APOLLO_MONITOR": "true",
                                  "QBOX_APOLLO_QMP_DIR": "/descriptor/qmp",
                                  "QBOX_LINUX_BOOT_STUB": "/descriptor/boot.bin",
                                  "QBOX_LINUX_KERNEL": "/descriptor/Image",
                                  "QBOX_LINUX_DTB": "/descriptor/linux.dtb"}})
    return cases


def capture(source_root: Path, cases: list[dict]) -> dict:
    sources = read_sources(source_root)
    values = []
    for case in cases:
        evaluated = evaluate_modules(sources, entrypoint=case["entrypoint"],
                                     environment=case["environment"])
        values.append({**case, **evaluated})
        print(f"CAPTURE {case['name']} objects={len(evaluated['locations'])}", flush=True)
    return {"schema_version": 1, "virtual_root": "./", "source_root": str(source_root.resolve()),
            "sources": {name: hashlib.sha256(text.encode()).hexdigest() for name, text in sources.items()},
            "cases": values,
            "limitations": ["Lua descriptor equality only; does not instantiate QBox or prove runtime behavior.",
                            "Table key/scalar types and reset/binding order are compared; source provenance is diagnostic.",
                            "Environment is injected explicitly; host environment and filesystem APIs are unavailable."]}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("capture", "compare"))
    parser.add_argument("--source-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--baseline", type=Path)
    parser.add_argument("--case", action="append", default=[], help="Select matrix case(s)")
    parser.add_argument("--full-entrypoint", default="apollo-qvp.lua")
    args = parser.parse_args()
    cases = profile_matrix()
    if args.case:
        names = {case["name"] for case in cases}
        if set(args.case) - names:
            parser.error("unknown cases: " + ", ".join(sorted(set(args.case) - names)))
        cases = [case for case in cases if case["name"] in args.case]
    if args.action == "compare":
        if args.baseline is None:
            parser.error("compare requires --baseline")
        baseline = json.loads(args.baseline.read_text())
        selected = {case["name"] for case in cases}
        counts = Counter(case["name"] for case in baseline["cases"])
        duplicates = {name for name, count in counts.items() if count > 1}
        if duplicates:
            parser.error("duplicate baseline cases: " + ", ".join(sorted(duplicates)))
        missing = selected - counts.keys()
        if missing:
            parser.error("missing baseline cases: " + ", ".join(sorted(missing)))
        cases = [{key: case[key] for key in ("name", "entrypoint", "environment")}
                 for case in baseline["cases"] if case["name"] in selected]
    for case in cases:
        if case["entrypoint"] == "apollo-qvp.lua":
            case["entrypoint"] = args.full_entrypoint
    try:
        current = capture(args.source_root, cases)
        if args.action == "capture":
            result = current
        else:
            old = {case["name"]: case for case in baseline["cases"]}
            reports = []
            for case in current["cases"]:
                changes = descriptor_differences(
                    normalize_file_paths(old[case["name"]]["descriptor"]),
                    normalize_file_paths(case["descriptor"]))
                reports.append({"name": case["name"], "passed": not changes,
                                "difference_count": len(changes), "differences": changes})
                print(f"{'PASS' if not changes else 'FAIL'} {case['name']} differences={len(changes)}")
            result = {"schema_version": 1, "passed": all(case["passed"] for case in reports),
                      "baseline": str(args.baseline), "cases": reports,
                      "sources": current["sources"], "limitations": current["limitations"],
                      "normalization": "Lexical file path components only; all other values compared exactly."}
    except DescriptorError as exc:
        result = {"schema_version": 1, "passed": False, "error": str(exc)}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(args.output)
    return 0 if result.get("passed", True) else 1


if __name__ == "__main__":
    raise SystemExit(main())
