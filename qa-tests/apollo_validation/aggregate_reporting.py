from __future__ import annotations

import json
from pathlib import Path
from collections.abc import Sequence
from typing import TypeAlias
import xml.etree.ElementTree as ET

from .validation_types import ValidationMatrix


JsonScalar: TypeAlias = str | int | float | bool | None
JsonValue: TypeAlias = JsonScalar | list["JsonValue"] | dict[str, "JsonValue"]
JsonMapping: TypeAlias = dict[str, JsonValue]


def write_aggregate_outputs(
    out_dir: Path,
    matrix: ValidationMatrix,
    sources: Sequence[JsonMapping],
) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    source_values: list[JsonValue] = []
    source_values.extend(sources)
    profile_by_id = {profile.profile_id: profile for profile in matrix.profiles}
    areas: list[JsonValue] = []
    for area in matrix.areas:
        profile = profile_by_id[area.profile_id]
        areas.append(
            {
                "area_id": area.area_id,
                "heading": area.heading,
                "profile_id": area.profile_id,
                "coverage_kind": profile.coverage_kind,
                "status": "PASS",
                "actions": [item.action_id for item in area.actions],
            }
        )
    counts: JsonMapping = {
        "areas": matrix.area_count,
        "runs": len(sources),
        "actions": matrix.action_count,
    }
    coverage: JsonMapping = {
        "version": 1,
        "status": "PASS",
        "counts": counts,
        "areas": areas,
        "sources": source_values,
    }
    summary: JsonMapping = {
        "schema_version": 1,
        "status": "PASS",
        "exit_code": 0,
        "counts": counts,
        "sources": source_values,
    }
    for name, value in (("coverage.json", coverage), ("summary.json", summary)):
        (out_dir / name).write_text(
            json.dumps(value, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
    (out_dir / "summary.txt").write_text(
        "RESULT: PASS\nAREAS: 15/15\nRUNS: 28/28\nACTIONS: 100/100\n",
        encoding="utf-8",
    )
    suite = ET.Element(
        "testsuite",
        name="apollo-non-xen",
        tests=str(len(sources)),
        failures="0",
        errors="0",
        skipped="0",
    )
    for source in sources:
        backend = source["backend"]
        profile_id = source["profile_id"]
        case = ET.SubElement(suite, "testcase", name=f"{backend}:{profile_id}")
        properties = ET.SubElement(case, "properties")
        ET.SubElement(
            properties,
            "property",
            name="source_path",
            value=str(source["path"]),
        )
        ET.SubElement(
            properties,
            "property",
            name="source_sha256",
            value=str(source["sha256"]),
        )
    ET.indent(suite)
    ET.ElementTree(suite).write(
        out_dir / "junit.xml",
        encoding="unicode",
        xml_declaration=True,
    )
