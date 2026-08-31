from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

import jsonschema

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/test/publish_apollo_fvp_pcie_limit.py"
SCHEMA = ROOT / "tests/schemas/apollo-fvp-pcie-limit-producer.schema.json"


def invoke(tmp_path: Path) -> tuple[int, dict[str, str | bool | dict[str, str | bool | int]]]:
    output = tmp_path / "producer.json"
    result = subprocess.run([sys.executable, str(SCRIPT), "--output", str(output)], cwd=ROOT, text=True, capture_output=True, check=False)
    payload = json.loads(output.read_text(encoding="utf-8"))
    assert isinstance(payload, dict)
    return result.returncode, payload


def test_offline_producer_emits_only_an_unsupported_reference_gate(tmp_path: Path) -> None:
    # Given: the repository-owned Task7 input fixture.
    # When: the producer regenerates a gate without starting FVP.
    returncode, payload = invoke(tmp_path)

    # Then: its successful reference gate remains explicitly non-qualifying.
    assert returncode == 0
    assert payload["reference_gate"] == "PASS"
    assert payload["fvp_qualification"] == "UNSUPPORTED"
    assert payload["qbox_started"] is False
    assert payload["claims"] == {"physical_its_delivery": False, "endpoint_enumeration": False, "qbox_equivalence": False}
    jsonschema.Draft202012Validator(json.loads(SCHEMA.read_text(encoding="utf-8"))).validate(payload)
