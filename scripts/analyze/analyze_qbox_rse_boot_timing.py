#!/usr/bin/env python3
"""Analyze QBox RSE boot timing markers from saved result.json files."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any


MARKERS = [
    ("rse_bl1_1", "TF-M BL1_1 start"),
    ("rse_jump_bl1_2", "BL1_1 to BL1_2 handoff"),
    ("rse_bl1_2", "TF-M BL1_2 start"),
    ("rse_attempt_image_0", "BL1_2 image selection"),
    ("rse_bl2_decrypted", "BL2 decrypt complete"),
    ("rse_bl2_validated", "BL2 validation complete"),
    ("rse_jump_bl2", "BL1_2 to BL2 handoff"),
    ("rse_image_4_loaded", "SI CL0 image loaded"),
    ("rse_image_3_loaded", "SI CL1 image loaded"),
    ("rse_image_2_loaded", "AP BL2 image loaded"),
    ("rse_image_0_loaded", "RSE runtime image loaded"),
    ("rse_scp_power_on_ap", "AP power-on SCMI complete"),
    ("rse_first_image_slot", "RSE runtime handoff"),
    ("measured_boot_bl33", "U-Boot measured boot marker"),
    ("primary_linux_cpu", "Linux CPU boot marker"),
    ("primary_login_prompt", "Linux login prompt"),
]

MARKER_LABEL = dict(MARKERS)

CC3XX_REGISTER_NAMES = {
    "0x80": "PKA_OPCODE",
    "0x88": "PKA_STATUS",
    "0x8c": "PKA_SW_RESET",
    "0x90": "PKA_L_BASE",
    "0xb0": "PKA_PIPE_RDY",
    "0xb4": "PKA_DONE",
    "0xd4": "PKA_SRAM_ADDR",
    "0xd8": "PKA_SRAM_WDATA",
    "0xdc": "PKA_SRAM_RDATA",
    "0xe4": "PKA_SRAM_RADDR",
    "0x400": "AES_KEY_0",
    "0x440": "AES_IV_0",
    "0x460": "AES_CTR_0",
    "0x470": "AES_BUSY",
    "0x47c": "AES_CMAC_INIT",
    "0x4bc": "AES_REMAINING_BYTES",
    "0x4c0": "AES_CONTROL",
    "0x4c8": "AES_HW_FLAGS",
    "0x4fc": "AES_RBG_SEEDING_RDY",
    "0x640": "HASH_H0",
    "0x644": "HASH_H1",
    "0x648": "HASH_H2",
    "0x64c": "HASH_H3",
    "0x650": "HASH_H4",
    "0x654": "HASH_H5",
    "0x658": "HASH_H6",
    "0x65c": "HASH_H7",
    "0x684": "AUTO_HW_PADDING",
    "0x688": "ENV_APBSC_PPROT_OVERRIDE",
    "0x7c0": "HASH_CONTROL",
    "0x7c8": "HASH_PAD_CFG",
    "0x7cc": "HASH_CUR_LEN0",
    "0x7d0": "HASH_CUR_LEN1",
    "0x818": "HASH_CLK_ENABLE",
    "0x824": "CLK_STATUS",
    "0x900": "CRYPTO_CTL",
    "0x910": "CRYPTO_BUSY",
    "0x91c": "HASH_BUSY",
    "0xa00": "HOST_RGF_IRR",
    "0xa04": "HOST_RGF_IMR",
    "0xa08": "HOST_RGF_ICR",
    "0xa28": "HOST_BOOT",
    "0xa38": "HOST_CRYPTOKEY_SEL",
    "0xa7c": "HOST_CC_IS_IDLE",
    "0xa90": "HOST_SF_READY",
    "0xc20": "DIN_MEM_DMA_BUSY",
    "0xc28": "DIN_SRC_LLI_WORD0",
    "0xc2c": "DIN_SRC_LLI_WORD1",
    "0xc30": "DIN_SRAM_SRC_ADDR",
    "0xc34": "DIN_SRAM_BYTES_LEN",
    "0xc38": "DIN_SRAM_DMA_BUSY",
    "0xc50": "FIFO_IN_EMPTY",
    "0xd20": "DOUT_MEM_DMA_BUSY",
    "0xd28": "DOUT_DST_LLI_WORD0",
    "0xd2c": "DOUT_DST_LLI_WORD1",
    "0xd34": "DOUT_SRAM_BYTES_LEN",
    "0xd38": "DOUT_SRAM_DMA_BUSY",
    "0xd50": "DOUT_FIFO_EMPTY",
}


def cc3xx_register_name(offset: str) -> str:
    return CC3XX_REGISTER_NAMES.get(offset.lower(), "")

PHASE_NOTES = {
    "rse_bl2_validated": {
        "phase": "BL1_2 BL2 signature validation",
        "source": (
            "TF-M BL1_2 validates the decrypted BL2 image; previous GDB "
            "evidence places the hot loop in LMS/LMOTS verification through "
            "CC3XX hash/PKA operations."
        ),
        "stub": (
            "Candidate for an opt-in validation accelerator or narrowly "
            "matched debug stub. Do not bypass the whole RSE boot chain."
        ),
        "risk": (
            "Security semantics change if validation is skipped. Keep disabled "
            "for secure boot, FWU, provisioning, and negative-auth tests."
        ),
    },
    "rse_image_4_loaded": {
        "phase": "RSE BL2 loads Safety Island CL0 image",
        "source": "Boot flash reads plus image authentication/copy.",
        "stub": "Prefer flash read/DMI/cache optimization; not a stub candidate.",
        "risk": "Disable fast storage paths for CFI/FWU/storage fidelity tests.",
    },
    "rse_image_3_loaded": {
        "phase": "RSE BL2 loads Safety Island CL1 image",
        "source": "Boot flash reads plus image authentication/copy.",
        "stub": "Prefer flash read/DMI/cache optimization; not a stub candidate.",
        "risk": "Disable fast storage paths for CFI/FWU/storage fidelity tests.",
    },
    "rse_image_2_loaded": {
        "phase": "RSE BL2 loads AP BL2 image",
        "source": "Boot flash reads plus image authentication/copy.",
        "stub": "Prefer flash read/DMI/cache optimization; not a stub candidate.",
        "risk": "Disable fast storage paths for CFI/FWU/storage fidelity tests.",
    },
    "rse_image_0_loaded": {
        "phase": "RSE BL2 loads RSE runtime image",
        "source": "Boot flash reads plus image authentication/copy.",
        "stub": "Prefer flash read/DMI/cache optimization; not a stub candidate.",
        "risk": "Disable fast storage paths for CFI/FWU/storage fidelity tests.",
    },
    "measured_boot_bl33": {
        "phase": "AP firmware measured boot to U-Boot",
        "source": "Post-RSE AP firmware path.",
        "stub": "Not an RSE boot stub candidate.",
        "risk": "Analyze separately in TF-A/U-Boot if this dominates.",
    },
    "primary_linux_cpu": {
        "phase": "Linux kernel entry",
        "source": "Post-RSE AP Linux path.",
        "stub": "Not an RSE boot stub candidate.",
        "risk": "Analyze separately in AP Linux/QEMU if this dominates.",
    },
    "primary_login_prompt": {
        "phase": "Linux userspace login prompt",
        "source": "Post-RSE AP userspace path.",
        "stub": "Not an RSE boot stub candidate.",
        "risk": "Analyze separately in rootfs/userspace if this dominates.",
    },
}


def read_json(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return data if isinstance(data, dict) else {}


def result_path(path: Path) -> Path:
    if path.is_dir():
        return path / "result.json"
    return path


def resolve_child_status(path: Path, status: dict[str, Any]) -> dict[str, Any]:
    child = status.get("child_result")
    candidates = []
    if isinstance(child, str) and child:
        candidates.append(Path(child))
    candidates.append(path.parent / "rd-aspen-result.json")
    for candidate in candidates:
        if candidate.exists():
            child_status = read_json(candidate)
            if child_status:
                return child_status
    return status


def marker_times(status: dict[str, Any]) -> dict[str, float]:
    times: dict[str, float] = {}
    profile = status.get("rse_boot_timing_profile")
    if isinstance(profile, dict):
        markers = profile.get("markers")
        if isinstance(markers, list):
            for marker in markers:
                if not isinstance(marker, dict) or not marker.get("seen"):
                    continue
                name = marker.get("name")
                elapsed = marker.get("elapsed_s")
                if not isinstance(name, str):
                    continue
                try:
                    times[name] = float(elapsed)
                except (TypeError, ValueError):
                    pass

    first_hits = status.get("progress_marker_first_hits")
    if isinstance(first_hits, dict):
        for name, hit in first_hits.items():
            if not isinstance(name, str) or not isinstance(hit, dict):
                continue
            try:
                times[name] = float(hit["elapsed_s"])
            except (KeyError, TypeError, ValueError):
                pass
    return times


def build_deltas(times: dict[str, float]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    previous_name: str | None = None
    previous_elapsed: float | None = None
    for name, label in MARKERS:
        elapsed = times.get(name)
        if elapsed is None:
            continue
        delta = None
        if previous_elapsed is not None:
            delta = elapsed - previous_elapsed
        note = PHASE_NOTES.get(name, {})
        rows.append(
            {
                "to": name,
                "to_label": label,
                "from": previous_name,
                "from_label": MARKER_LABEL.get(previous_name or ""),
                "elapsed_s": round(elapsed, 3),
                "delta_s": round(delta, 3) if delta is not None else None,
                "phase": note.get("phase", label),
                "stub_feasibility": note.get(
                    "stub", "No specific stub recommendation."
                ),
                "risk": note.get("risk", ""),
            }
        )
        previous_name = name
        previous_elapsed = elapsed
    return rows


def load_cc3xx_stats(path: Path, status: dict[str, Any]) -> dict[str, Any]:
    candidates: list[dict[str, Any]] = []
    for source in (status,):
        cc3xx = source.get("cc3xx_stats")
        if isinstance(cc3xx, dict):
            candidates.append(cc3xx)

    runtime = status.get("runtime_artifacts")
    if isinstance(runtime, dict):
        stats_path = runtime.get("rse_cc3xx_stats")
        if isinstance(stats_path, str):
            parsed = read_json(Path(stats_path))
            if parsed:
                return {
                    "enabled": True,
                    "path": stats_path,
                    "present": True,
                    "stats": parsed,
                }

    for candidate in candidates:
        stats = candidate.get("stats")
        if isinstance(stats, dict):
            return candidate
        stats_path = candidate.get("path")
        if isinstance(stats_path, str):
            parsed = read_json(Path(stats_path))
            if parsed:
                result = dict(candidate)
                result["present"] = True
                result["stats"] = parsed
                return result

    fallback = path.parent / "rse-cc3xx-stats.json"
    parsed = read_json(fallback)
    if parsed:
        return {
            "enabled": True,
            "path": str(fallback),
            "present": True,
            "stats": parsed,
        }
    return {"enabled": False, "present": False}


def count_top(counts: Any, limit: int = 8) -> list[tuple[str, int]]:
    if not isinstance(counts, dict):
        return []
    return sorted(
        ((str(key), int(count)) for key, count in counts.items()),
        key=lambda item: item[1],
        reverse=True,
    )[:limit]


def register_top(counts: Any, limit: int = 12) -> list[dict[str, Any]]:
    rows = []
    for offset, count in count_top(counts, limit):
        normalized = offset.lower()
        rows.append(
            {
                "offset": normalized,
                "name": cc3xx_register_name(normalized),
                "count": count,
            }
        )
    return rows


def as_int(value: Any) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return 0


def cc3xx_stats_interpretation(stats: dict[str, Any]) -> str:
    sha_finishes = as_int(stats.get("sha256_finishes"))
    sha_resets = as_int(stats.get("sha256_resets"))
    pka_writes = as_int(stats.get("pka_opcode_writes"))
    aes_ops = as_int(stats.get("aes_ctr_ops")) + as_int(stats.get("aes_ecb_ops"))

    if sha_finishes > 1000 and pka_writes < 100:
        return (
            "HASH/SHA activity dominates; PKA is not the current slow-path "
            "candidate. This matches LMS/LMOTS verification."
        )
    if pka_writes > sha_resets:
        return "PKA activity dominates; inspect modular arithmetic acceleration."
    if aes_ops > sha_finishes:
        return "AES activity dominates; inspect decrypt/load path before LMS."
    return "No single CC3XX operation class dominates from aggregate counters."


def cc3xx_stats_summary(cc3xx_stats: dict[str, Any]) -> dict[str, Any]:
    stats = cc3xx_stats.get("stats")
    if not isinstance(stats, dict):
        return {}

    return {
        "path": cc3xx_stats.get("path"),
        "total_accesses": stats.get("total_accesses"),
        "read_accesses": stats.get("read_accesses"),
        "write_accesses": stats.get("write_accesses"),
        "hash_dma_triggers": stats.get("hash_dma_triggers"),
        "hash_dma_bytes": stats.get("hash_dma_bytes"),
        "hash_dma_chunks": stats.get("hash_dma_chunks"),
        "sha256_resets": stats.get("sha256_resets"),
        "sha256_update_calls": stats.get("sha256_update_calls"),
        "sha256_update_bytes": stats.get("sha256_update_bytes"),
        "sha256_transforms": stats.get("sha256_transforms"),
        "sha256_finishes": stats.get("sha256_finishes"),
        "pka_opcode_writes": stats.get("pka_opcode_writes"),
        "pka_top": count_top(stats.get("pka_opcode_count")),
        "aes_ctr_ops": stats.get("aes_ctr_ops"),
        "aes_ctr_bytes": stats.get("aes_ctr_bytes"),
        "aes_ecb_ops": stats.get("aes_ecb_ops"),
        "aes_ecb_bytes": stats.get("aes_ecb_bytes"),
        "cmac_dma_triggers": stats.get("cmac_dma_triggers"),
        "cmac_dma_bytes": stats.get("cmac_dma_bytes"),
        "crypto_engine_writes": stats.get("crypto_engine_writes"),
        "crypto_engine_top": count_top(stats.get("crypto_engine_count")),
        "register_read_top": register_top(stats.get("register_read_count")),
        "register_write_top": register_top(stats.get("register_write_count")),
        "mem_read_ops": stats.get("mem_read_ops"),
        "mem_read_bytes": stats.get("mem_read_bytes"),
        "mem_write_ops": stats.get("mem_write_ops"),
        "mem_write_bytes": stats.get("mem_write_bytes"),
        "interpretation": cc3xx_stats_interpretation(stats),
    }


def analyze_one(path: Path) -> dict[str, Any]:
    path = result_path(path)
    status = read_json(path)
    child_status = resolve_child_status(path, status) if status else {}
    cc3xx_stats = load_cc3xx_stats(path, child_status or status)
    times = marker_times(child_status or status)
    deltas = build_deltas(times)
    slowest = sorted(
        [row for row in deltas if row["delta_s"] is not None],
        key=lambda row: float(row["delta_s"]),
        reverse=True,
    )
    return {
        "path": str(path),
        "passed": status.get("passed"),
        "blocker": status.get("blocker"),
        "child_blocker": child_status.get("blocker") if child_status else None,
        "deltas": deltas,
        "slowest": slowest[:5],
        "cc3xx_stats": cc3xx_stats_summary(cc3xx_stats),
    }


def markdown_report(results: list[dict[str, Any]]) -> str:
    lines = [
        "# QBox RSE Boot Timing Analysis",
        "",
        "This report is generated from saved QBox result JSON files. It does "
        "not rerun QBox.",
        "",
    ]
    for result in results:
        lines.extend(
            [
                f"## {result['path']}",
                "",
                f"- passed: `{result.get('passed')}`",
                f"- blocker: `{result.get('blocker')}`",
                f"- child_blocker: `{result.get('child_blocker')}`",
                "",
                "| Rank | From | To | Delta s | Elapsed s | Stub feasibility | Risk |",
                "| --- | --- | --- | ---: | ---: | --- | --- |",
            ]
        )
        for index, row in enumerate(result["slowest"], start=1):
            lines.append(
                "| {rank} | `{from_name}` | `{to_name}` | {delta} | {elapsed} | "
                "{stub} | {risk} |".format(
                    rank=index,
                    from_name=row["from"],
                    to_name=row["to"],
                    delta=row["delta_s"],
                    elapsed=row["elapsed_s"],
                    stub=row["stub_feasibility"],
                    risk=row["risk"],
                )
            )
        lines.append("")
        cc3xx = result.get("cc3xx_stats")
        if isinstance(cc3xx, dict) and cc3xx:
            lines.extend(
                [
                    "### CC3XX Stats",
                    "",
                    f"- path: `{cc3xx.get('path')}`",
                    f"- total_accesses: `{cc3xx.get('total_accesses')}`",
                    f"- read/write accesses: `{cc3xx.get('read_accesses')}` / "
                    f"`{cc3xx.get('write_accesses')}`",
                    f"- hash_dma: `{cc3xx.get('hash_dma_triggers')}` "
                    f"triggers, `{cc3xx.get('hash_dma_bytes')}` bytes, "
                    f"`{cc3xx.get('hash_dma_chunks')}` chunks",
                    f"- sha256: `{cc3xx.get('sha256_resets')}` resets, "
                    f"`{cc3xx.get('sha256_update_calls')}` updates, "
                    f"`{cc3xx.get('sha256_update_bytes')}` bytes, "
                    f"`{cc3xx.get('sha256_transforms')}` transforms, "
                    f"`{cc3xx.get('sha256_finishes')}` finishes",
                    f"- pka_opcode_writes: `{cc3xx.get('pka_opcode_writes')}`",
                    f"- aes_ctr: `{cc3xx.get('aes_ctr_ops')}` ops, "
                    f"`{cc3xx.get('aes_ctr_bytes')}` bytes",
                    f"- aes_ecb: `{cc3xx.get('aes_ecb_ops')}` ops, "
                    f"`{cc3xx.get('aes_ecb_bytes')}` bytes",
                    f"- cmac_dma: `{cc3xx.get('cmac_dma_triggers')}` triggers, "
                    f"`{cc3xx.get('cmac_dma_bytes')}` bytes",
                    f"- mem read/write: `{cc3xx.get('mem_read_ops')}` ops / "
                    f"`{cc3xx.get('mem_write_ops')}` ops",
                    f"- crypto_engine_writes: "
                    f"`{cc3xx.get('crypto_engine_writes')}`",
                    f"- interpretation: {cc3xx.get('interpretation')}",
                    "",
                    "| PKA opcode | Count |",
                    "| --- | ---: |",
                ]
            )
            for opcode, count in cc3xx.get("pka_top", []):
                lines.append(f"| `{opcode}` | {count} |")
            lines.extend(["", "| Crypto engine | Count |", "| --- | ---: |"])
            for engine, count in cc3xx.get("crypto_engine_top", []):
                lines.append(f"| `{engine}` | {count} |")
            lines.extend(["", "| Register read offset | Name | Count |", "| --- | --- | ---: |"])
            for row in cc3xx.get("register_read_top", []):
                lines.append(
                    f"| `{row.get('offset')}` | {row.get('name') or ''} | "
                    f"{row.get('count')} |"
                )
            lines.extend(["", "| Register write offset | Name | Count |", "| --- | --- | ---: |"])
            for row in cc3xx.get("register_write_top", []):
                lines.append(
                    f"| `{row.get('offset')}` | {row.get('name') or ''} | "
                    f"{row.get('count')} |"
                )
            lines.append("")
    return "\n".join(lines) + "\n"


def text_report(results: list[dict[str, Any]]) -> str:
    lines: list[str] = []
    for result in results:
        lines.append(result["path"])
        lines.append(f"  passed: {result.get('passed')}")
        lines.append(f"  blocker: {result.get('blocker')}")
        for row in result["slowest"]:
            lines.append(
                "  {delta:8.3f}s {from_name} -> {to_name}: {stub}".format(
                    delta=float(row["delta_s"]),
                    from_name=row["from"],
                    to_name=row["to"],
                    stub=row["stub_feasibility"],
                )
            )
        cc3xx = result.get("cc3xx_stats")
        if isinstance(cc3xx, dict) and cc3xx:
            lines.append(
                "  cc3xx hash_dma={triggers} bytes={bytes} "
                "sha256_finishes={finishes} sha256_transforms={xforms} "
                "pka_opcode_writes={pka} note={note}".format(
                    triggers=cc3xx.get("hash_dma_triggers"),
                    bytes=cc3xx.get("hash_dma_bytes"),
                    finishes=cc3xx.get("sha256_finishes"),
                    xforms=cc3xx.get("sha256_transforms"),
                    pka=cc3xx.get("pka_opcode_writes"),
                    note=cc3xx.get("interpretation"),
                )
            )
            read_top = cc3xx.get("register_read_top") or []
            write_top = cc3xx.get("register_write_top") or []
            if read_top:
                lines.append(
                    "  cc3xx top reads: "
                    + ", ".join(
                        f"{row.get('offset')}({row.get('name') or 'unnamed'})="
                        f"{row.get('count')}"
                        for row in read_top[:5]
                    )
                )
            if write_top:
                lines.append(
                    "  cc3xx top writes: "
                    + ", ".join(
                        f"{row.get('offset')}({row.get('name') or 'unnamed'})="
                        f"{row.get('count')}"
                        for row in write_top[:5]
                    )
                )
        lines.append("")
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "results",
        type=Path,
        nargs="+",
        help="result.json paths or directories containing result.json",
    )
    parser.add_argument("--markdown", action="store_true")
    parser.add_argument("--json", action="store_true", dest="as_json")
    parser.add_argument("--output", type=Path)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    results = [analyze_one(path) for path in args.results]
    if args.as_json:
        output = json.dumps(results, indent=2, sort_keys=True) + "\n"
    elif args.markdown:
        output = markdown_report(results)
    else:
        output = text_report(results)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(output, encoding="utf-8")
    else:
        sys.stdout.write(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
