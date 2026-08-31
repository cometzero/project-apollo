from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import subprocess
import sys

import pytest
import jsonschema


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/test/validate_apollo_pcie_its_runtime.py"
FIXTURES = ROOT / "tests/fixtures/gic720ae/pcie-its"
JsonValue = str | int | bool | None | list["JsonValue"] | dict[str, "JsonValue"]


def materialize_fixture(source: Path) -> str:
    if source.suffix != ".json":
        return source.read_text(encoding="utf-8")
    mutation = json.loads(source.read_text(encoding="utf-8"))
    text = materialize_fixture(FIXTURES / mutation["base"])
    replacements = mutation.get("replacements", [[mutation.get("old"), mutation.get("new")]])
    for replacement in replacements:
        old, new = replacement[0], replacement[1]
        assert old in text
        text = text.replace(old, new, replacement[2] if len(replacement) == 3 else 1)
    return text


def invoke(tmp_path: Path, fixture: str, platform: str, mode: str, digest: str) -> tuple[subprocess.CompletedProcess[str], dict[str, JsonValue]]:
    source = FIXTURES / fixture
    if source.suffix == ".json":
        text = materialize_fixture(source)
        source = tmp_path / source.with_suffix(".log").name
        source.write_text(text, encoding="utf-8")
    output = tmp_path / f"{fixture}.json"
    result = subprocess.run(
        [sys.executable, str(SCRIPT), "--log", str(source), "--platform", platform,
         "--mode", mode, "--input-sha256", digest, "--output", str(output)],
        cwd=ROOT, text=True, capture_output=True, check=False,
    )
    return result, json.loads(output.read_text(encoding="utf-8")) if output.exists() else {}


@pytest.mark.parametrize(
    ("fixture", "platform", "digest"),
    [("fvp-msix.log", "fvp", "a" * 64), ("qbox-msix.log", "qbox", "b" * 64)],
)
def test_cli_passes_complete_endpoint_bound_msix_evidence(tmp_path: Path, fixture: str, platform: str, digest: str) -> None:
    result, payload = invoke(tmp_path, fixture, platform, "msix", digest)
    assert result.returncode == 0
    assert payload["status"] == "pass"
    assert payload["reason"] == "ok"


@pytest.mark.parametrize(
    ("fixture", "reason"),
    [
        ("missing-chain.json", "chain_missing"),
        ("duplicate-chain.json", "chain_duplicate"),
        ("unordered-chain.json", "chain_order"),
        ("parent-hwirq-low.json", "lpi_hwirq_range"),
        ("wrong-endpoint.json", "endpoint_identity"),
        ("wrong-action.json", "action_contract"),
        ("zero-delta.json", "cpu0_delta"),
        ("wrong-cpu-delta.json", "cpu1_delta"),
        ("workload-failed.json", "workload_rc"),
        ("affinity-mismatch.json", "affinity_effective"),
        ("offline-stall.json", "offline_delta"),
        ("replay-failed.json", "replay_delta"),
        ("missing-cleanup.json", "cleanup_missing"),
        ("missing-final.json", "final_missing"),
        ("stale-hash.json", "input_hash"),
        ("stale-version.json", "contract_version"),
        ("virtio-mmio-as-pci.json", "endpoint_kind"),
        ("intx-wrong-hwirq.json", "intx_hwirq"),
        ("malformed-input.json", "malformed_input"),
        ("out-of-order-phase.json", "event_order"),
        ("fake-domain-identities.json", "chain_domain_identity"),
        ("spi-untrusted-device.json", "spi_endpoint_path"),
        ("spi-wrong-driver.json", "spi_endpoint_identity"),
        ("spi-hwirq-32.json", "spi_hwirq"),
    ],
)
def test_cli_rejects_each_negative_with_unique_reason(tmp_path: Path, fixture: str, reason: str) -> None:
    mode = "intx" if fixture == "intx-wrong-hwirq.json" else ("spi" if fixture.startswith("spi-") or fixture == "virtio-mmio-as-pci.json" else "msix")
    result, payload = invoke(tmp_path, f"negative/{fixture}", "qbox", mode, "b" * 64)
    assert result.returncode != 0
    assert payload["status"] == "fail"
    assert payload["reason"] == reason


def test_dynamic_cpu_count_is_preserved(tmp_path: Path) -> None:
    _, payload = invoke(tmp_path, "qbox-msix.log", "qbox", "msix", "b" * 64)
    assert payload["cpu_count"] == 4
    phases = payload["phases"]
    assert isinstance(phases, dict)
    cpu1 = phases["cpu1"]
    assert isinstance(cpu1, dict)
    assert cpu1["delta"] == [0, 5, 0, 0]


@pytest.mark.parametrize(("fixture", "mode"), [("qbox-intx.json", "intx"), ("qbox-spi.json", "spi")])
def test_cli_passes_qbox_control_modes(tmp_path: Path, fixture: str, mode: str) -> None:
    result, payload = invoke(tmp_path, fixture, "qbox", mode, "b" * 64)
    assert result.returncode == 0
    assert payload["status"] == "pass"


def test_outputs_validate_against_normalized_schema(tmp_path: Path) -> None:
    _, payload = invoke(tmp_path, "fvp-msix.log", "fvp", "msix", "a" * 64)
    schema = json.loads((ROOT / "tests/schemas/apollo-pcie-its-runtime.schema.json").read_text(encoding="utf-8"))
    jsonschema.Draft202012Validator(schema).validate(payload)


def test_invalid_cli_hash_emits_normalized_schema_valid_failure(tmp_path: Path) -> None:
    result, payload = invoke(tmp_path, "qbox-msix.log", "qbox", "msix", "not-a-sha256")
    schema = json.loads((ROOT / "tests/schemas/apollo-pcie-its-runtime.schema.json").read_text(encoding="utf-8"))
    assert result.returncode != 0
    jsonschema.Draft202012Validator(schema).validate(payload)
    assert payload["reason"] == "input_hash"
    assert payload["input_sha256"] != "not-a-sha256"
    assert payload["input_sha256_valid"] is False


@pytest.mark.parametrize(("platform", "mode"), [("untrusted", "msix"), ("qbox", "untrusted")])
def test_invalid_cli_variants_emit_normalized_schema_valid_failure(tmp_path: Path, platform: str, mode: str) -> None:
    result, payload = invoke(tmp_path, "qbox-msix.log", platform, mode, "b" * 64)
    schema = json.loads((ROOT / "tests/schemas/apollo-pcie-its-runtime.schema.json").read_text(encoding="utf-8"))
    assert result.returncode != 0
    jsonschema.Draft202012Validator(schema).validate(payload)
    assert payload["reason"] == "platform_contract"


def test_cli_atomically_replaces_stale_output_with_failure(tmp_path: Path) -> None:
    output = tmp_path / "negative" / "malformed-input.json.json"
    output.parent.mkdir()
    output.write_text('{"status":"pass","partial":true}', encoding="utf-8")
    result, payload = invoke(tmp_path, "negative/malformed-input.json", "qbox", "msix", "b" * 64)
    assert result.returncode != 0
    assert payload == json.loads(output.read_text(encoding="utf-8"))
    assert payload["status"] == "fail"


def test_untrusted_success_labels_and_instructions_are_ignored(tmp_path: Path) -> None:
    result, payload = invoke(tmp_path, "qbox-untrusted-text.json", "qbox", "msix", "b" * 64)
    assert result.returncode == 0
    assert payload["status"] == "pass"
    assert "injected" not in payload


def test_module_has_importable_validation_surface() -> None:
    spec = importlib.util.spec_from_file_location("validator", SCRIPT)
    assert spec is not None and spec.loader is not None
