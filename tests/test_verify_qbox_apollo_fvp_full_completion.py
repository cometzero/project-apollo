from pathlib import Path
import importlib.util
import json
import sys


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/test/verify_qbox_apollo_fvp_full_completion.py"
LINUX_16_CPU_CONSOLE = (
    "U-Boot \n"
    "Kernel command line: root=PARTLABEL=rootfs\n"
    "smp: Brought up 1 node, 16 CPUs\n"
    "possible=0-15\n"
    "present=0-15\n"
    "online=0-15\n"
    "cpuinfo_processors=16\n"
    "cpu_directories=16\n"
)
LINUX_STALE_4_CPU_CONSOLE = (
    "U-Boot \n"
    "Kernel command line: root=PARTLABEL=rootfs maxcpus=4\n"
    "smp: Brought up 1 node, 4 CPUs\n"
    "possible=0-15\n"
    "present=0-15\n"
    "online=0-3\n"
    "cpuinfo_processors=4\n"
    "cpu_directories=16\n"
)


def load_verifier():
    spec = importlib.util.spec_from_file_location("full_completion_verifier", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def write_json(path: Path, data) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def write_log(path: Path, text: str = "log\n") -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


def marker_groups() -> dict[str, dict[str, bool]]:
    return {
        "rse": {"boot": True},
        "si_cl0": {"scp": True},
        "si_cl1": {"zephyr": True},
        "ap_firmware": {"bl2": True, "bl31": True, "optee": True, "uboot": True},
        "linux": {"login": True},
        "post_login": {"probe": True},
        "maps_and_interrupts": {"reviewed": True},
    }


def console_logs(run_dir: Path, primary_text: str) -> dict[str, str]:
    return {
        "rse": str(write_log(run_dir / "qbox-rse.log")),
        "si_cl0": str(write_log(run_dir / "qbox-safety-island-cl0.log")),
        "si_cl1": str(write_log(run_dir / "qbox-safety-island-cl1.log")),
        "secure_console": str(
            write_log(
                run_dir / "qbox-secure-console.log",
                "NOTICE:  BL2:\nNOTICE:  BL31:\nOP-TEE version:\n",
            )
        ),
        "primary_console": str(
            write_log(run_dir / "qbox-primary-console.log", primary_text)
        ),
        "platform": str(write_log(run_dir / "qbox-platform.log")),
    }


def live_result(
    run_dir: Path,
    *,
    mode: str,
    gate: str,
    ap_cpus: int,
    primary_text: str = LINUX_16_CPU_CONSOLE,
    post_login_probe_passed: bool = True,
) -> dict:
    return {
        "passed": True,
        "verdict": "pass",
        "safety_island_mode": mode,
        "completion_gates": {"G0": "pass", "G1": "pass", gate: "pass"},
        "marker_groups": marker_groups(),
        "console_logs": console_logs(run_dir, primary_text),
        "post_login_probe": {
            "requested": True,
            "passed": post_login_probe_passed,
        },
        "platform_observations": {
            "ap_cpus": ap_cpus,
            "expected_ap_cpus": 16,
            "ap_cpus_enabled_for_full_system": ap_cpus == 16,
        },
        "secure_console_observations": {
            "ap_bl2_console": True,
            "bl31_console": True,
            "optee_console": True,
        },
        "primary_console_observations": {"u_boot_console": True},
    }


def make_evidence_root(
    tmp_path: Path,
    *,
    final_ap_cpus: int,
    final_primary_text: str = LINUX_16_CPU_CONSOLE,
    service_post_login_probe_passed: bool = True,
) -> Path:
    evidence_root = tmp_path / "qbox-apollo-fvp"
    check_dir = evidence_root / "full-check-only"
    service_dir = evidence_root / "full-service-model"
    live_cl1_dir = evidence_root / "full-live-cl1"
    final_dir = evidence_root / "full-live-cl0-cl1"

    write_json(
        check_dir / "result.json",
        {
            "passed": True,
            "completion_gates": {
                "G0": "pass",
                "G1": "not_run",
                "G2": "not_run",
                "G3": "not_run",
                "G4": "not_run",
                "G5": "not_run",
            },
        },
    )
    write_json(check_dir / "map-validation.json", {"passed": True})
    write_json(check_dir / "coverage-audit.json", {"passed": True})

    write_json(
        service_dir / "result.json",
        live_result(
            service_dir,
            mode="service-model",
            gate="G2",
            ap_cpus=16,
            post_login_probe_passed=service_post_login_probe_passed,
        ),
    )
    write_json(service_dir / "comparison.json", {"passed": True})
    write_json(
        live_cl1_dir / "result.json",
        live_result(live_cl1_dir, mode="live-cl1", gate="G3", ap_cpus=16),
    )
    write_json(
        final_dir / "result.json",
        live_result(
            final_dir,
            mode="live-cl0-cl1",
            gate="G4",
            ap_cpus=final_ap_cpus,
            primary_text=final_primary_text,
        ),
    )
    write_json(final_dir / "comparison.json", {"passed": True})
    write_json(final_dir / "map-comparison.json", {"passed": True})
    write_json(final_dir / "coverage-audit.json", {"passed": True})
    return evidence_root


def run_strict_verifier(
    tmp_path: Path,
    monkeypatch,
    *,
    final_ap_cpus: int,
    final_primary_text: str = LINUX_16_CPU_CONSOLE,
    service_post_login_probe_passed: bool = True,
) -> tuple[int, dict]:
    verifier = load_verifier()
    evidence_root = make_evidence_root(
        tmp_path,
        final_ap_cpus=final_ap_cpus,
        final_primary_text=final_primary_text,
        service_post_login_probe_passed=service_post_login_probe_passed,
    )
    output = evidence_root / "full-live-cl0-cl1/final-verification.json"
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "verify_qbox_apollo_fvp_full_completion.py",
            "--strict-final",
            "--evidence-root",
            str(evidence_root),
            "--output",
            str(output),
        ],
    )

    exit_code = verifier.main()

    return exit_code, json.loads(output.read_text(encoding="utf-8"))


def find_check(result: dict, name: str) -> dict:
    return next(check for check in result["checks"] if check["name"] == name)


def test_parse_args_rejects_removed_isolated_evidence_option(monkeypatch):
    verifier = load_verifier()
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "verify_qbox_apollo_fvp_full_completion.py",
            "--si-cl1-isolated-dir",
            "retired-evidence",
        ],
    )

    try:
        verifier.parse_args()
    except SystemExit as exc:
        assert exc.code == 2
    else:
        raise AssertionError("removed isolated evidence option was accepted")


def test_strict_final_accepts_16_ap_cpu_full_system_evidence(tmp_path, monkeypatch):
    # Given: synthetic final evidence for the active 16-CPU Apollo full-system contract.
    # When: the strict final verifier evaluates the canonical live CL0/CL1 bundle.
    exit_code, result = run_strict_verifier(tmp_path, monkeypatch, final_ap_cpus=16)

    # Then: completion is authorized and the G4 AP CPU acceptance check passes.
    assert exit_code == 0
    assert result["completion_claim_allowed"] is True
    assert result["overall_gates"]["G1"] == "pass"
    assert result["overall_gates"]["G4"] == "pass"
    assert "milestone_evidence" not in result
    assert find_check(result, "live-cl0-cl1 AP CPUs enabled")["passed"] is True
    assert find_check(result, "live-cl0-cl1 Linux enumerated 16 CPUs")["passed"] is True


def test_strict_final_rejects_failed_full_system_ap_probe(tmp_path, monkeypatch):
    exit_code, result = run_strict_verifier(
        tmp_path,
        monkeypatch,
        final_ap_cpus=16,
        service_post_login_probe_passed=False,
    )

    assert exit_code == 1
    assert result["completion_claim_allowed"] is False
    assert result["overall_gates"]["G1"] == "fail"
    assert find_check(result, "full-system AP post-login probe passed")["passed"] is False


def test_strict_final_rejects_4_ap_cpu_full_system_evidence(tmp_path, monkeypatch):
    # Given: otherwise passing final evidence that only reports the stale 4-CPU topology.
    # When: the strict final verifier evaluates the canonical live CL0/CL1 bundle.
    exit_code, result = run_strict_verifier(tmp_path, monkeypatch, final_ap_cpus=4)

    # Then: final completion is rejected by the AP CPU acceptance check.
    assert exit_code == 1
    assert result["completion_claim_allowed"] is False
    assert result["overall_gates"]["G4"] == "fail"
    ap_cpu_check = find_check(result, "live-cl0-cl1 AP CPUs enabled")
    assert ap_cpu_check["passed"] is False
    assert ap_cpu_check["status"] == "ap_cpus=4"


def test_strict_final_rejects_stale_linux_4_cpu_full_system_evidence(
    tmp_path, monkeypatch
):
    # Given: modeled platform evidence reports 16 AP CPUs but Linux is masked to 4 CPUs.
    # When: the strict final verifier evaluates the canonical live CL0/CL1 bundle.
    exit_code, result = run_strict_verifier(
        tmp_path,
        monkeypatch,
        final_ap_cpus=16,
        final_primary_text=LINUX_STALE_4_CPU_CONSOLE,
    )

    # Then: final completion is rejected by the Linux-side CPU enumeration check.
    assert exit_code == 1
    assert result["completion_claim_allowed"] is False
    assert result["overall_gates"]["G4"] == "fail"
    linux_cpu_check = find_check(result, "live-cl0-cl1 Linux enumerated 16 CPUs")
    assert linux_cpu_check["passed"] is False
