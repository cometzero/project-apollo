#!/usr/bin/env python3
"""Inspect RD-Aspen RSE flash Protected Storage and ITS partitions."""

from __future__ import annotations

import argparse
import datetime as _dt
import gzip
import hashlib
import json
from pathlib import Path
from typing import Iterable


RSE_FLASH_RAW_SIZE = 0x04000000
RSE_FLASH_IMG_OFFSET = 0x00007000
RSE_FLASH_IMG_SIZE = 0x03000000
RSE_FLASH_PS_OFFSET = RSE_FLASH_IMG_OFFSET + RSE_FLASH_IMG_SIZE
RSE_FLASH_PS_SIZE = 0x00100000
RSE_FLASH_ITS_OFFSET = RSE_FLASH_PS_OFFSET + RSE_FLASH_PS_SIZE
RSE_FLASH_ITS_SIZE = 0x00040000
RSE_FLASH_SECTOR_SIZE = 0x1000

PARTITIONS = [
    {
        "name": "ps",
        "description": "TF-M Protected Storage",
        "offset": RSE_FLASH_PS_OFFSET,
        "size": RSE_FLASH_PS_SIZE,
        "sectors_per_block": 4,
    },
    {
        "name": "its",
        "description": "TF-M Internal Trusted Storage",
        "offset": RSE_FLASH_ITS_OFFSET,
        "size": RSE_FLASH_ITS_SIZE,
        "sectors_per_block": 1,
    },
]

LAYOUT_SOURCES = [
    "tfm/platform/ext/target/arm/rse/automotive_rd/css-aspen/flash_layout.h",
    "tfm/platform/ext/target/arm/rse/automotive_rd/css-aspen/rse_memory_sizes.h",
]


def workspace_root() -> Path:
    return Path(__file__).resolve().parents[1]


def timestamp() -> str:
    return _dt.datetime.now(tz=_dt.timezone.utc).isoformat(timespec="seconds")


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def relpath(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(workspace_root()))
    except ValueError:
        return str(path)


def read_maybe_gzip(path: Path) -> tuple[bytes, dict[str, object]]:
    raw = path.read_bytes()
    info: dict[str, object] = {
        "path": relpath(path),
        "stored_size": len(raw),
        "stored_sha256": sha256(raw),
        "gzip": raw.startswith(b"\x1f\x8b"),
    }
    if info["gzip"]:
        data = gzip.decompress(raw)
        info["state"] = "gzip_decompressed"
    else:
        data = raw
        info["state"] = "raw"
    info["raw_size_before_padding"] = len(data)
    info["raw_sha256_before_padding"] = sha256(data)
    return data, info


def normalize_flash_image(data: bytes, info: dict[str, object]) -> bytes:
    if len(data) < RSE_FLASH_RAW_SIZE:
        info["normalization"] = "padded_with_erased_ff"
        info["pad_bytes"] = RSE_FLASH_RAW_SIZE - len(data)
        data = data + bytes([0xFF]) * (RSE_FLASH_RAW_SIZE - len(data))
    elif len(data) > RSE_FLASH_RAW_SIZE:
        info["normalization"] = "truncated_to_rse_flash_size"
        info["truncated_tail_bytes"] = len(data) - RSE_FLASH_RAW_SIZE
        data = data[:RSE_FLASH_RAW_SIZE]
    else:
        info["normalization"] = "none"
    info["raw_size"] = len(data)
    info["raw_sha256"] = sha256(data)
    return data


def count_non_erased(data: bytes) -> int:
    return sum(1 for value in data if value != 0xFF)


def contiguous_ranges(values: Iterable[int]) -> list[dict[str, object]]:
    sorted_values = sorted(values)
    if not sorted_values:
        return []

    ranges: list[dict[str, object]] = []
    start = previous = sorted_values[0]
    for value in sorted_values[1:]:
        if value == previous + 1:
            previous = value
            continue
        ranges.append({"start": start, "end": previous, "count": previous - start + 1})
        start = previous = value
    ranges.append({"start": start, "end": previous, "count": previous - start + 1})
    return ranges


def format_sector_ranges(
    sector_ranges: list[dict[str, object]],
    partition_offset: int,
    limit: int,
) -> list[dict[str, object]]:
    formatted = []
    for item in sector_ranges[:limit]:
        start_sector = int(item["start"])
        end_sector = int(item["end"])
        formatted.append(
            {
                "start_sector": start_sector,
                "end_sector": end_sector,
                "count": int(item["count"]),
                "start_offset": hex(partition_offset + start_sector * RSE_FLASH_SECTOR_SIZE),
                "end_offset_exclusive": hex(
                    partition_offset + (end_sector + 1) * RSE_FLASH_SECTOR_SIZE
                ),
            }
        )
    return formatted


def sample_non_erased(data: bytes, base_offset: int, from_tail: bool) -> dict[str, object] | None:
    indexes = range(len(data) - 1, -1, -1) if from_tail else range(len(data))
    found = next((idx for idx in indexes if data[idx] != 0xFF), None)
    if found is None:
        return None
    if from_tail:
        start = max(0, found - 15)
        end = found + 1
    else:
        start = found
        end = min(len(data), found + 16)
    return {
        "offset": hex(base_offset + start),
        "length": end - start,
        "hex": data[start:end].hex(),
    }


def partition_summary(
    image: bytes,
    partition: dict[str, object],
    baseline: bytes | None,
    range_limit: int,
) -> dict[str, object]:
    name = str(partition["name"])
    offset = int(partition["offset"])
    size = int(partition["size"])
    sectors_per_block = int(partition["sectors_per_block"])
    data = image[offset : offset + size]

    dirty_sectors = [
        index
        for index in range(size // RSE_FLASH_SECTOR_SIZE)
        if count_non_erased(
            data[index * RSE_FLASH_SECTOR_SIZE : (index + 1) * RSE_FLASH_SECTOR_SIZE]
        )
    ]
    dirty_blocks = sorted({sector // sectors_per_block for sector in dirty_sectors})
    sector_ranges = contiguous_ranges(dirty_sectors)
    block_ranges = contiguous_ranges(dirty_blocks)

    result: dict[str, object] = {
        "name": name,
        "description": partition["description"],
        "offset": hex(offset),
        "size": size,
        "sector_size": RSE_FLASH_SECTOR_SIZE,
        "sector_count": size // RSE_FLASH_SECTOR_SIZE,
        "sectors_per_logical_block": sectors_per_block,
        "logical_block_size": sectors_per_block * RSE_FLASH_SECTOR_SIZE,
        "logical_block_count": size // (sectors_per_block * RSE_FLASH_SECTOR_SIZE),
        "sha256": sha256(data),
        "non_erased_bytes": count_non_erased(data),
        "erased_bytes": sum(1 for value in data if value == 0xFF),
        "dirty_sector_count": len(dirty_sectors),
        "dirty_sector_ranges": format_sector_ranges(sector_ranges, offset, range_limit),
        "dirty_sector_ranges_truncated": len(sector_ranges) > range_limit,
        "dirty_logical_block_count": len(dirty_blocks),
        "dirty_logical_block_ranges": block_ranges[:range_limit],
        "dirty_logical_block_ranges_truncated": len(block_ranges) > range_limit,
        "first_non_erased_sample": sample_non_erased(data, offset, from_tail=False),
        "last_non_erased_sample": sample_non_erased(data, offset, from_tail=True),
    }

    if baseline is not None:
        base_data = baseline[offset : offset + size]
        changed_offsets = [idx for idx, value in enumerate(data) if value != base_data[idx]]
        changed_sectors = sorted({idx // RSE_FLASH_SECTOR_SIZE for idx in changed_offsets})
        result["baseline_compare"] = {
            "changed_bytes": len(changed_offsets),
            "changed_sector_count": len(changed_sectors),
            "changed_sector_ranges": format_sector_ranges(
                contiguous_ranges(changed_sectors), offset, range_limit
            ),
            "changed_to_erased_ff_bytes": sum(
                1 for idx in changed_offsets if data[idx] == 0xFF
            ),
            "changed_from_erased_ff_bytes": sum(
                1 for idx in changed_offsets if base_data[idx] == 0xFF
            ),
        }

    return result


def inspect_image(path: Path, baseline: bytes | None, range_limit: int) -> dict[str, object]:
    data, info = read_maybe_gzip(path)
    data = normalize_flash_image(data, info)
    return {
        "image": info,
        "partitions": [
            partition_summary(data, partition, baseline, range_limit)
            for partition in PARTITIONS
        ],
    }


def write_json(path: Path, data: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def markdown_table(report: dict[str, object]) -> str:
    lines = [
        "# RD-Aspen RSE Flash Storage Inspection",
        "",
        f"Generated: `{report['generated_at_utc']}`",
        "",
        "Layout:",
        "",
        f"- RSE flash raw size: `{hex(RSE_FLASH_RAW_SIZE)}`",
        f"- PS offset/size: `{hex(RSE_FLASH_PS_OFFSET)}` / `{hex(RSE_FLASH_PS_SIZE)}`",
        f"- ITS offset/size: `{hex(RSE_FLASH_ITS_OFFSET)}` / `{hex(RSE_FLASH_ITS_SIZE)}`",
        f"- Sector size: `{hex(RSE_FLASH_SECTOR_SIZE)}`",
        "",
        "| Image | Partition | Non-erased bytes | Dirty sectors | Dirty logical blocks | Changed bytes vs baseline | Last non-erased sample |",
        "| --- | --- | ---: | ---: | ---: | ---: | --- |",
    ]
    for item in report["images"]:
        image_path = item["image"]["path"]
        for partition in item["partitions"]:
            compare = partition.get("baseline_compare", {})
            sample = partition.get("last_non_erased_sample")
            sample_text = ""
            if sample:
                sample_text = f"{sample['offset']} `{sample['hex']}`"
            lines.append(
                "| "
                + " | ".join(
                    [
                        f"`{image_path}`",
                        f"`{partition['name']}`",
                        str(partition["non_erased_bytes"]),
                        str(partition["dirty_sector_count"]),
                        str(partition["dirty_logical_block_count"]),
                        str(compare.get("changed_bytes", "")),
                        sample_text,
                    ]
                )
                + " |"
            )
    lines.append("")
    return "\n".join(lines)


def write_markdown(path: Path, report: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(markdown_table(report), encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Inspect RD-Aspen RSE flash PS/ITS partition state."
    )
    parser.add_argument("images", nargs="+", type=Path, help="RSE flash images to inspect")
    parser.add_argument(
        "--baseline",
        type=Path,
        help="Optional baseline RSE flash image for byte/sector comparison",
    )
    parser.add_argument("--output", type=Path, help="Write JSON report to this path")
    parser.add_argument("--markdown", type=Path, help="Write Markdown summary to this path")
    parser.add_argument(
        "--range-limit",
        type=int,
        default=16,
        help="Maximum dirty range entries per partition in JSON output",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    baseline_data = None
    baseline_info = None
    if args.baseline:
        baseline_data, baseline_info = read_maybe_gzip(args.baseline)
        baseline_data = normalize_flash_image(baseline_data, baseline_info)

    report: dict[str, object] = {
        "generated_at_utc": timestamp(),
        "layout": {
            "rse_flash_raw_size": RSE_FLASH_RAW_SIZE,
            "rse_flash_img_offset": RSE_FLASH_IMG_OFFSET,
            "rse_flash_img_size": RSE_FLASH_IMG_SIZE,
            "rse_flash_ps_offset": RSE_FLASH_PS_OFFSET,
            "rse_flash_ps_size": RSE_FLASH_PS_SIZE,
            "rse_flash_its_offset": RSE_FLASH_ITS_OFFSET,
            "rse_flash_its_size": RSE_FLASH_ITS_SIZE,
            "sector_size": RSE_FLASH_SECTOR_SIZE,
            "sources": LAYOUT_SOURCES,
        },
        "baseline": baseline_info,
        "images": [
            inspect_image(path, baseline_data, args.range_limit) for path in args.images
        ],
    }

    if args.output:
        write_json(args.output, report)
    if args.markdown:
        write_markdown(args.markdown, report)
    if not args.output and not args.markdown:
        print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
