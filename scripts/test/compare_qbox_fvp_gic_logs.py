#!/usr/bin/env python3
from __future__ import annotations

import argparse
from dataclasses import dataclass
import json
from pathlib import Path
import re
import sys
from typing import Final, TypedDict


SCHEMA_VERSION: Final = 1
GICV3_FEATURES: Final = re.compile(r"GICv3: GICv3 features:\s*(?P<ppis>[0-9]+) PPIs(?P<features>.*)")
GICV4_FEATURES: Final = re.compile(r"GICv3: GICv4 features:\s*(?P<features>.*)")
SPIS_IMPLEMENTED: Final = re.compile(r"GICv3:\s*(?P<count>[0-9]+) SPIs implemented")
INTERRUPT_COLLECTIONS: Final = re.compile(r"allocated (?P<count>[0-9]+) Interrupt Collections")


class GicEvidence(TypedDict):
    spis: int | None
    ppis: int | None
    direct_lpi_gicv3: bool
    direct_lpi_rvpeid_gicv4: bool
    gicv4_1_mode: bool
    interrupt_collections: int | None
    direct_lpi_vpe_invalidation: bool


class Check(TypedDict):
    id: str
    status: str
    fvp: bool | int | None
    qbox: bool | int | None
    message: str


class Report(TypedDict):
    schema_version: int
    status: str
    inputs: dict[str, str]
    fvp: GicEvidence
    qbox: GicEvidence
    checks: list[Check]
    missing_from_qbox: list[str]


@dataclass(frozen=True, slots=True)
class CliArgs:
    fvp_log: Path
    qbox_log: Path
    expect_fvp_parity: bool
    output: Path


def parse_gic_evidence(text: str) -> GicEvidence:
    spis: int | None = None
    ppis: int | None = None
    interrupt_collections: int | None = None
    direct_lpi_gicv3 = False
    direct_lpi_rvpeid_gicv4 = False
    gicv4_1_mode = False
    direct_lpi_vpe_invalidation = False

    for line in text.splitlines():
        spis_match = SPIS_IMPLEMENTED.search(line)
        if spis_match is not None:
            spis = int(spis_match.group("count"))

        gicv3_match = GICV3_FEATURES.search(line)
        if gicv3_match is not None:
            ppis = int(gicv3_match.group("ppis"))
            direct_lpi_gicv3 = "DirectLPI" in gicv3_match.group("features")

        gicv4_match = GICV4_FEATURES.search(line)
        if gicv4_match is not None:
            features = gicv4_match.group("features")
            direct_lpi_rvpeid_gicv4 = (
                "DirectLPI" in features and "RVPEID" in features and "Valid+Dirty" in features
            )

        collections_match = INTERRUPT_COLLECTIONS.search(line)
        if collections_match is not None:
            interrupt_collections = int(collections_match.group("count"))

        if "Using GICv4.1 mode" in line:
            gicv4_1_mode = True

        if "Using DirectLPI for VPE invalidation" in line:
            direct_lpi_vpe_invalidation = True

    return {
        "spis": spis,
        "ppis": ppis,
        "direct_lpi_gicv3": direct_lpi_gicv3,
        "direct_lpi_rvpeid_gicv4": direct_lpi_rvpeid_gicv4,
        "gicv4_1_mode": gicv4_1_mode,
        "interrupt_collections": interrupt_collections,
        "direct_lpi_vpe_invalidation": direct_lpi_vpe_invalidation,
    }


def feature_check(check_id: str, fvp: bool, qbox: bool) -> Check:
    status = "pass" if (not fvp or qbox) else "fail"
    message = f"{check_id} parity satisfied"
    if status == "fail":
        message = f"FVP exposes {check_id}, but QBox log does not"
    return {"id": check_id, "status": status, "fvp": fvp, "qbox": qbox, "message": message}


def collection_check(fvp: int | None, qbox: int | None) -> Check:
    status = "pass" if fvp != 32768 or qbox == 32768 else "fail"
    message = "interrupt_collections_32768 parity satisfied"
    if status == "fail":
        message = f"FVP allocates 32768 interrupt collections, but QBox allocates {qbox!r}"
    return {
        "id": "interrupt_collections_32768",
        "status": status,
        "fvp": fvp,
        "qbox": qbox,
        "message": message,
    }


def numeric_check(check_id: str, fvp: int | None, qbox: int | None, expected: int) -> Check:
    fvp_has_expected = fvp == expected
    qbox_has_expected = qbox == expected
    status = "pass" if (not fvp_has_expected or qbox_has_expected) else "fail"
    message = f"{check_id} parity satisfied"
    if status == "fail":
        message = f"FVP reports {expected} for {check_id}, but QBox reports {qbox!r}"
    return {"id": check_id, "status": status, "fvp": fvp, "qbox": qbox, "message": message}


def build_report(args: CliArgs) -> Report:
    fvp = parse_gic_evidence(args.fvp_log.read_text(encoding="utf-8", errors="replace"))
    qbox = parse_gic_evidence(args.qbox_log.read_text(encoding="utf-8", errors="replace"))
    checks = [
        numeric_check("spis_960", fvp["spis"], qbox["spis"], 960),
        feature_check("direct_lpi_gicv3", fvp["direct_lpi_gicv3"], qbox["direct_lpi_gicv3"]),
        feature_check("direct_lpi_rvpeid_gicv4", fvp["direct_lpi_rvpeid_gicv4"], qbox["direct_lpi_rvpeid_gicv4"]),
        feature_check("gicv4_1_mode", fvp["gicv4_1_mode"], qbox["gicv4_1_mode"]),
        collection_check(fvp["interrupt_collections"], qbox["interrupt_collections"]),
        feature_check(
            "direct_lpi_vpe_invalidation",
            fvp["direct_lpi_vpe_invalidation"],
            qbox["direct_lpi_vpe_invalidation"],
        ),
    ]
    missing = [check["id"] for check in checks if check["status"] == "fail"]
    status = "fail" if args.expect_fvp_parity and missing else "pass"
    return {
        "schema_version": SCHEMA_VERSION,
        "status": status,
        "inputs": {
            "fvp_log": str(args.fvp_log),
            "qbox_log": str(args.qbox_log),
        },
        "fvp": fvp,
        "qbox": qbox,
        "checks": checks,
        "missing_from_qbox": missing,
    }


def parse_args() -> CliArgs:
    parser = argparse.ArgumentParser(description="Compare Apollo FVP and QBox Linux GIC probe evidence.")
    parser.add_argument("--fvp-log", type=Path, required=True)
    parser.add_argument("--qbox-log", type=Path, required=True)
    parser.add_argument("--expect-fvp-parity", action="store_true")
    parser.add_argument("--output", type=Path, required=True)
    namespace = parser.parse_args()
    return CliArgs(
        fvp_log=namespace.fvp_log,
        qbox_log=namespace.qbox_log,
        expect_fvp_parity=namespace.expect_fvp_parity,
        output=namespace.output,
    )


def main() -> int:
    args = parse_args()
    report = build_report(args)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(args.output)
    if args.expect_fvp_parity and report["missing_from_qbox"]:
        for check_id in report["missing_from_qbox"]:
            print(f"FAIL {check_id}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
