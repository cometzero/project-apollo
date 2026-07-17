from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/test/validate_qbox_apollo_fidelity_contract.py"


def write_json(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value), encoding="utf-8")


def topology_bundle(tmp_path: Path) -> Path:
    bundle = tmp_path / "topology"
    digest = "a" * 64
    write_json(
        bundle / "topology.json",
        {"machine": "apollo-qvp", "variant": "cfg2"},
    )
    write_json(
        bundle / "boot-routes.json",
        {
            "reset_defaults": {
                "ap_primary": "reset_asserted",
                "ap_secondary": "reset_asserted_powered_off",
                "atu_apu": "default_deny_unlocked",
                "cross_domain_access": "rse_only",
            },
            "sequence": [
                {
                    "id": step_id,
                    "order": index * 10,
                    **({"after": previous} if previous else {}),
                }
                for index, (step_id, previous) in enumerate(
                    (
                        ("rse_bl1_start", None),
                        ("rse_auth_images", "rse_bl1_start"),
                        ("rse_program_atu_apu", "rse_auth_images"),
                        ("rse_release_si_cl0", "rse_program_atu_apu"),
                        ("si_cl0_verify_rse_config", "rse_release_si_cl0"),
                        ("si_cl0_init_system", "si_cl0_verify_rse_config"),
                        ("rse_scp_boot_confirm", "si_cl0_init_system"),
                        ("rse_release_ap_primary", "rse_scp_boot_confirm"),
                        ("tfa_release_ap_secondary", "rse_release_ap_primary"),
                    ),
                    start=1,
                )
            ],
        },
    )
    required_artifacts = (
        "local_conf",
        "bblayers_conf",
        "templateconf",
        "contract_topology",
        "contract_address_map",
        "contract_transaction_routes",
        "contract_signal_routes",
        "contract_boot_control",
        "contract_software_contract",
    )
    write_json(
        bundle / "artifacts.json",
        {
            "configuration": {
                "machine": "apollo-qvp",
                "rd_aspen_variant": "cfg2",
                "pc_cpus_count_default": 4,
            },
            "source_revisions": {
                "workspace": "1" * 40,
                "qbox": "2" * 40,
                "qbox_platform": "3" * 40,
                "qemu": "4" * 40,
            },
            "artifacts": [
                {"name": name, "exists": True, "sha256": digest}
                for name in required_artifacts
            ],
        },
    )
    write_json(bundle / "validation.json", {"status": "pass"})
    return bundle


def run_validator(
    bundle: Path,
    output: Path,
    runtime: Path | None = None,
) -> subprocess.CompletedProcess[str]:
    command = [
        sys.executable,
        str(SCRIPT),
        "--no-refresh",
        "--topology-dir",
        str(bundle),
        "--cpus",
        "4",
        "--fail-on-enabled-cpu-above",
        "3",
        "--output",
        str(output),
    ]
    if runtime:
        command.extend(("--runtime-result", str(runtime)))
    return subprocess.run(
        command,
        cwd=ROOT,
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )


def test_static_four_cpu_contract_passes_and_runtime_is_skipped(tmp_path: Path) -> None:
    bundle = topology_bundle(tmp_path)
    output = tmp_path / "contract.json"

    completed = run_validator(bundle, output)

    assert completed.returncode == 0, completed.stderr
    report = json.loads(output.read_text(encoding="utf-8"))
    assert report["status"] == "pass"
    runtime_check = next(
        check for check in report["checks"] if check["id"] == "runtime-four-cpu-boundary"
    )
    assert runtime_check["status"] == "skip"
    assert report["contract"]["enabled_cpu_ids"] == [0, 1, 2, 3]
    assert report["ledger"][0]["status"] == "complete"
    assert report["ledger"][1]["status"] == "complete"
    assert report["ledger"][1]["evidence"].endswith(
        "i1-request-context-completion-2026-07-16-ko.md"
    )
    assert report["ledger"][2]["status"] == "complete"
    assert report["ledger"][2]["evidence"].endswith(
        "i2-ni710ae-apu-completion-2026-07-16-ko.md"
    )
    assert report["ledger"][3]["status"] == "complete"
    assert report["ledger"][3]["evidence"].endswith(
        "i3-mmu720ae-smmuv3-completion-2026-07-16-ko.md"
    )
    assert report["ledger"][4]["status"] == "complete"
    assert report["ledger"][4]["evidence"].endswith(
        "i4-gpex-msi-lpi-completion-2026-07-16-ko.md"
    )
    assert report["ledger"][5]["status"] == "complete"
    assert report["ledger"][5]["evidence"].endswith(
        "i5-fault-safety-completion-2026-07-16-ko.md"
    )
    assert report["ledger"][6]["status"] == "complete"
    assert report["ledger"][6]["evidence"].endswith(
        "i6-software-abi-recovery-completion-2026-07-16-ko.md"
    )
    assert report["ledger"][7]["status"] == "complete"
    assert report["ledger"][7]["evidence"].endswith(
        "i7-integration-validation-completion-2026-07-17-ko.md"
    )
    assert report["ledger"][8]["status"] == "complete"
    assert report["ledger"][8]["evidence"].endswith(
        "i8-closeout-completion-2026-07-17-ko.md"
    )


def test_runtime_cpu_above_three_fails(tmp_path: Path) -> None:
    bundle = topology_bundle(tmp_path)
    runtime = tmp_path / "runtime.json"
    output = tmp_path / "contract.json"
    write_json(
        runtime,
        {
            "platform_observations": {"ap_cpus": 4, "expected_ap_cpus": 4},
            "linux_online_cpu_ids": [0, 1, 2, 3, 4],
        },
    )

    completed = run_validator(bundle, output, runtime)

    assert completed.returncode == 1
    report = json.loads(output.read_text(encoding="utf-8"))
    assert report["status"] == "fail"
    assert report["errors"] == ["runtime-four-cpu-boundary"]


def test_runtime_exact_four_cpu_boundary_passes(tmp_path: Path) -> None:
    bundle = topology_bundle(tmp_path)
    runtime = tmp_path / "runtime.json"
    output = tmp_path / "contract.json"
    write_json(
        runtime,
        {
            "platform_observations": {"ap_cpus": 4, "expected_ap_cpus": 4},
            "linux_online_cpu_ids": [0, 1, 2, 3],
            "interrupt_cpu_ids": [0, 1, 2, 3],
        },
    )

    completed = run_validator(bundle, output, runtime)

    assert completed.returncode == 0, completed.stderr
    report = json.loads(output.read_text(encoding="utf-8"))
    runtime_check = next(
        check for check in report["checks"] if check["id"] == "runtime-four-cpu-boundary"
    )
    assert runtime_check["status"] == "pass"
