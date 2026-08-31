from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

import jsonschema
import pytest


ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = ROOT / "scripts/test/validate_qbox_apollo_pcie_irq_spi.py"
SCHEMA = ROOT / "tests/schemas/apollo-qbox-pcie-irq-spi.schema.json"
DIGEST = "9" * 64
JsonValue = str | int | bool | None | list["JsonValue"] | dict[str, "JsonValue"]


def complete_log() -> str:
    return (
        "\n".join(
            (
                f"APOLLO_SPI|v=1|event=contract|input_sha256={DIGEST}|platform=qbox|mode=spi",
                "APOLLO_SPI|v=1|event=endpoint|bdf=-|driver=virtio-mmio|compatible=virtio,mmio|devpath=/sys/bus/platform/devices/30060000.virtio|target=eth0",
                "APOLLO_SPI|v=1|event=pci_vector|virq=33|owner=/sys/bus/pci/devices/0000:00:01.0/msi_irqs/33",
                "APOLLO_SPI|v=1|event=line_irq|virq=40|owner=/sys/bus/platform/devices/30060000.virtio",
                "APOLLO_SPI|v=1|event=chain|virq=40|index=0|domain=GICv3|hwirq=0x125|chip=GICv3",
                "APOLLO_SPI|v=1|event=count|phase=spi-before|values=10,8,0,0",
                "APOLLO_SPI|v=1|event=count|phase=pci-before|values=4,2,0,0",
                "APOLLO_SPI|v=1|event=workload|phase=isolated|target=eth0|rc=0",
                "APOLLO_SPI|v=1|event=count|phase=spi-after|values=12,8,0,0",
                "APOLLO_SPI|v=1|event=count|phase=pci-after|values=4,2,0,0",
                "APOLLO_SPI|v=1|event=cleanup|affinity_restored=1|rc=0",
                f"APOLLO_SPI|v=1|event=final|input_sha256={DIGEST}|status=complete",
            )
        )
        + "\n"
    )


def invoke(tmp_path: Path, text: str) -> tuple[int, dict[str, JsonValue]]:
    source = tmp_path / "primary.log"
    output = tmp_path / "normalized.json"
    source.write_text(text, encoding="utf-8")
    result = subprocess.run(
        [
            sys.executable,
            str(VALIDATOR),
            "--log",
            str(source),
            "--input-sha256",
            DIGEST,
            "--output",
            str(output),
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    payload = json.loads(output.read_text(encoding="utf-8")) if output.exists() else {}
    return result.returncode, payload


def test_spi_validator_accepts_positive_isolated_spi_and_zero_pci_delta(
    tmp_path: Path,
) -> None:
    returncode, payload = invoke(tmp_path, complete_log())
    assert returncode == 0
    assert payload["status"] == "pass"
    assert payload["spi_delta"] == [2, 0, 0, 0]
    assert payload["pci_vector_delta"] == [0, 0, 0, 0]
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    jsonschema.Draft202012Validator(schema).validate(payload)


@pytest.mark.parametrize(
    ("old", "new", "reason"),
    [
        (
            "values=4,2,0,0\nAPOLLO_SPI|v=1|event=cleanup",
            "values=4,3,0,0\nAPOLLO_SPI|v=1|event=cleanup",
            "pci_vector_delta",
        ),
        ("hwirq=0x125", "hwirq=0x124", "spi_hwirq"),
        ("values=12,8,0,0", "values=10,8,0,0", "spi_delta"),
    ],
)
def test_spi_validator_rejects_cross_interface_or_misdirected_evidence(
    tmp_path: Path,
    old: str,
    new: str,
    reason: str,
) -> None:
    returncode, payload = invoke(tmp_path, complete_log().replace(old, new, 1))
    assert returncode == 1
    assert payload["status"] == "fail"
    assert payload["reason"] == reason
