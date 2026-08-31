from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "tests/fixtures/gic720ae/pcie-model"
CAPTURE = ROOT / "scripts/test/capture_apollo_fvp_pcie_model.py"
SCHEMA = ROOT / "tests/schemas/apollo-fvp-pcie-model-contract.schema.json"
FVP = ROOT / "build/tmp_baremetal/sysroots-components/x86_64/fvp-rd-aspen-native/usr/bin/FVP_Zena_CSS_Cfg2"


def test_current_good_fixture_characterizes_static_configuration_declaration() -> None:
    # Given: a generated FVP configuration with the required PCIe declarations.
    fvpconf = json.loads((FIXTURES / "current-good.fvpconf.json").read_text(encoding="utf-8"))

    # When: its declaration values are read without model introspection or runtime execution.
    parameters = fvpconf["parameters"]

    # Then: the static contract proves declarations, not application.
    assert parameters["pcie_group_0.pcie4.hierarchy_file_name"] == "<default>"
    assert parameters["pcie_group_0.pcie4.pcie_rc.ahci0.endpoint.ats_supported"] == "true"
    assert parameters["pcie_group_0.pcie4.pcie_rc.ahci0.ahci.image_path"] == ""
    assert parameters["css.gic_distributor.ITS-count"] == "1"


def test_schema_has_no_runtime_configuration_applied_claim() -> None:
    # Given: the Todo 1 result schema.
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))

    # When: the static capture contract is inspected for runtime application language.
    schema_text = json.dumps(schema, sort_keys=True)

    # Then: it accepts only separately named static declaration evidence.
    assert "configuration_applied" not in schema_text
    assert "configuration_declared" in schema_text


def test_cli_has_no_final_argv_receipt_option() -> None:
    # Given: the Todo 1 capture CLI.
    result = subprocess.run([sys.executable, str(CAPTURE), "--help"], cwd=ROOT, check=False, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    # When: its supported input surface is displayed.
    help_text = result.stdout + result.stderr

    # Then: it accepts no final argv receipt because Todo 7 owns runtime application.
    assert result.returncode == 0
    assert "--final-argv-file" not in help_text


def test_default_only_configuration_fails_as_not_declared_without_a_runtime_receipt(tmp_path: Path) -> None:
    # Given: a real cfg2 metadata surface and a default-only active configuration.
    output = tmp_path / "model-contract.json"

    # When: Todo 1 captures declarations without a final argv receipt.
    result = subprocess.run(
        [sys.executable, str(CAPTURE), "--fvp", str(FVP), "--fvpconf", str(FIXTURES / "default-only.fvpconf.json"), "--schema", str(SCHEMA), "--output", str(output)],
        cwd=ROOT,
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    # Then: the missing active declaration fails with the declaration-specific reason.
    assert result.returncode != 0
    assert '"reason": "configuration_not_declared"' in result.stderr
    assert not output.exists()


def test_malformed_fvpconf_fails_without_a_partial_result(tmp_path: Path) -> None:
    # Given: a malformed FVP configuration object with no parameters field.
    fvpconf = tmp_path / "malformed.fvpconf.json"
    output = tmp_path / "model-contract.json"
    fvpconf.write_text("{}", encoding="utf-8")

    # When: the CLI parses the malformed declaration input.
    result = subprocess.run(
        [sys.executable, str(CAPTURE), "--fvp", str(FVP), "--fvpconf", str(fvpconf), "--schema", str(SCHEMA), "--output", str(output)],
        cwd=ROOT,
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    # Then: it fails closed before writing a success JSON artifact.
    assert result.returncode != 0
    assert '"reason": "malformed_input"' in result.stderr
    assert not output.exists()
