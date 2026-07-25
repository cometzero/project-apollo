from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import subprocess
import sys
from types import ModuleType


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/test/compare_qbox_fvp_timer_snapshots.py"


def load_module() -> ModuleType:
    spec = importlib.util.spec_from_file_location("compare_timer_snapshots", SCRIPT)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def snapshot(producer: str, *, second_counter: int = 200) -> dict[str, object]:
    def sample(name: str, sim_time_ns: int, counter: int) -> dict[str, object]:
        result = {
            "name": name,
            "marker": name,
            "sim_time_ns": sim_time_ns,
            "views": {
                "smd": {"domain": "css", "counter": counter, "input_frequency_hz": 125000000, "increment": 1, "reported_frequency_hz": 125000000, "observed": True},
                "ap_cpu0": {"domain": "css", "counter": counter, "reported_frequency_hz": 125000000, "observed": True},
                "ap_refclk_ns": {"domain": "css", "counter": counter, "reported_frequency_hz": 125000000, "cval": 300, "enabled": True, "masked": False, "istatus": False, "irq": 49, "observed": True},
                "ap_refclk_s": {"domain": "css", "counter": counter, "reported_frequency_hz": 125000000, "cval": 300, "enabled": True, "masked": False, "istatus": False, "irq": 48, "access_control_state": "enabled", "observed": True},
                "si0_cpu0": {"domain": "css", "counter": counter, "reported_frequency_hz": 125000000, "observed": True},
                "si0_cntbase": {"domain": "css", "counter": counter, "reported_frequency_hz": 125000000, "observed": True},
                "si1_cpu0": {"domain": "css", "counter": counter, "reported_frequency_hz": 100000000, "observed": True},
                "rse_timer0": {"domain": "rse", "counter": counter, "counter_basis": "css_mirror", "irq": 3, "observed": True},
                "rse_timer1": {"domain": "rse", "counter": counter, "counter_basis": "css_mirror", "irq": 4, "observed": True},
                "rse_timer2": {"domain": "rse", "counter": counter, "counter_basis": "css_mirror", "irq": 5, "observed": True},
                "rse_timer3": {"domain": "rse", "counter": counter, "counter_basis": "css_mirror", "irq": 27, "observed": True},
            },
        }
        views = result["views"]
        assert isinstance(views, dict)
        for view in views.values():
            assert isinstance(view, dict)
            view["observed_counter"] = counter
        return result

    return {
        "schema_version": 1,
        "producer": producer,
        "status": "pass",
        "captured_at": "2026-07-22T00:00:00Z",
        "source": {
            "machine": "apollo-qvp",
            "revision": "test",
            "rse_smd_counter_mirror": True,
        },
        "samples": [sample("start", 1_000, 100), sample("end", 2_000, second_counter)],
    }


def test_build_report_passes_when_same_timestamp_identity_and_rates_match() -> None:
    # Given: two valid producers with equal CSS samples and deltas.
    module = load_module()

    # When: their snapshots are compared.
    report = module.build_report(snapshot("qbox"), snapshot("fvp"))

    # Then: exact identity and rate checks pass independently.
    assert report["status"] == "pass"
    assert {check["id"] for check in report["checks"]} >= {
        "qbox:css-identity:start",
        "fvp:css-identity:start",
        "rate:ap_cpu0:start->end",
    }


def test_build_report_fails_when_one_css_view_differs_at_same_timestamp() -> None:
    # Given: a QBox sample whose AP MMIO view is not the shared CSS count.
    module = load_module()
    qbox = snapshot("qbox")
    samples = qbox["samples"]
    assert isinstance(samples, list)
    first = samples[0]
    assert isinstance(first, dict)
    views = first["views"]
    assert isinstance(views, dict)
    ap_mmio = views["ap_refclk_ns"]
    assert isinstance(ap_mmio, dict)
    ap_mmio["counter"] = 101

    # When: the malformed identity sample is compared.
    report = module.build_report(qbox, snapshot("fvp"))

    # Then: the result identifies a same-timestamp identity failure.
    assert report["status"] == "fail"
    assert any(
        check["id"] == "qbox:css-identity:start" and check["status"] == "fail"
        for check in report["checks"]
    )


def test_build_report_rejects_raz_secure_frame_as_identity_evidence() -> None:
    # Given: a secure frame read while CNTACR1 leaves that frame RAZ.
    module = load_module()
    qbox = snapshot("qbox")
    samples = qbox["samples"]
    assert isinstance(samples, list)
    first = samples[0]
    assert isinstance(first, dict)
    views = first["views"]
    assert isinstance(views, dict)
    secure = views["ap_refclk_s"]
    assert isinstance(secure, dict)
    secure.update({"counter": 0, "access_control_state": "raz", "observed": False})

    # When: strict same-timestamp identity is evaluated.
    report = module.build_report(qbox, snapshot("fvp"))

    # Then: provider-internal count cannot stand in for inaccessible MMIO.
    assert report["status"] == "fail"


def test_build_report_fails_when_required_css_view_is_missing() -> None:
    # Given: a snapshot that cannot prove all required CSS views.
    module = load_module()
    qbox = snapshot("qbox")
    samples = qbox["samples"]
    assert isinstance(samples, list)
    first = samples[0]
    assert isinstance(first, dict)
    views = first["views"]
    assert isinstance(views, dict)
    del views["si1_cpu0"]

    # When: the strict comparison runs.
    report = module.build_report(qbox, snapshot("fvp"))

    # Then: partial identity evidence is rejected.
    assert report["status"] == "fail"
    assert any(
        check["id"] == "qbox:css-identity:start" and check["status"] == "fail"
        for check in report["checks"]
    )


def test_rate_comparison_handles_a_64_bit_counter_wrap() -> None:
    # Given: matching rates represented across a 64-bit counter wrap.
    module = load_module()
    qbox = snapshot("qbox", second_counter=5)
    fvp = snapshot("fvp", second_counter=115)
    for sample, counter in zip(qbox["samples"], ((1 << 64) - 10, 5)):
        assert isinstance(sample, dict)
        views = sample["views"]
        assert isinstance(views, dict)
        for view in views.values():
            assert isinstance(view, dict)
            view["counter"] = counter
            view["observed_counter"] = counter
    for sample, counter in zip(fvp["samples"], (100, 115)):
        assert isinstance(sample, dict)
        views = sample["views"]
        assert isinstance(views, dict)
        for view in views.values():
            assert isinstance(view, dict)
            view["counter"] = counter

    # When: rates are compared using adjacent samples.
    report = module.build_report(qbox, fvp)

    # Then: the wrapped delta is interpreted modulo 64 bits.
    assert report["status"] == "pass"


def test_rate_comparison_uses_each_producers_native_timebase() -> None:
    # Given: QBox nanoseconds and FVP picoseconds describe the same 125MHz rate.
    module = load_module()
    qbox = snapshot("qbox", second_counter=125_100)
    fvp = snapshot("fvp", second_counter=1_365)
    qbox_samples = qbox["samples"]
    assert isinstance(qbox_samples, list)
    for sample, time_ns in zip(qbox_samples, (1_000_000, 2_000_000)):
        assert isinstance(sample, dict)
        sample["sim_time_ns"] = time_ns
    fvp_samples = fvp["samples"]
    assert isinstance(fvp_samples, list)
    for sample, ticks in zip(fvp_samples, (2_384_796_440_900, 2_384_806_559_300)):
        assert isinstance(sample, dict)
        sample["raw_simulation_ticks"] = ticks
        sample["iris_timebase_hz"] = 1_000_000_000_000

    # When: the comparator evaluates quantized deltas from each native timebase.
    report = module.build_report(qbox, fvp)

    # Then: sub-nanosecond FVP timing does not create a false rate mismatch.
    assert report["status"] == "pass"


def test_build_report_rejects_duplicate_or_insufficient_common_samples() -> None:
    # Given: duplicate QBox labels and only one label shared with FVP.
    module = load_module()
    qbox = snapshot("qbox")
    fvp = snapshot("fvp")
    samples = qbox["samples"]
    assert isinstance(samples, list)
    duplicate = dict(samples[0])
    samples[1] = duplicate
    fvp_samples = fvp["samples"]
    assert isinstance(fvp_samples, list)
    fvp_samples[1] = {**fvp_samples[1], "name": "fvp-only"}

    # When: strict comparison evaluates the samples.
    report = module.build_report(qbox, fvp)

    # Then: no rate result can mask malformed sample topology.
    assert report["status"] == "fail"
    assert {item["id"] for item in report["checks"] if item["status"] == "fail"} >= {
        "qbox:sample-names",
        "rate:common-samples",
    }


def test_build_report_rejects_divergent_rse_timer_when_mirror_is_enabled() -> None:
    # Given: default mirror mode but one RSE normalized counter diverges.
    module = load_module()
    qbox = snapshot("qbox")
    samples = qbox["samples"]
    assert isinstance(samples, list)
    first = samples[0]
    assert isinstance(first, dict)
    views = first["views"]
    assert isinstance(views, dict)
    timer = views["rse_timer2"]
    assert isinstance(timer, dict)
    timer["counter"] = 101

    # When: the RSE mirror contract is checked.
    report = module.build_report(qbox, snapshot("fvp"))

    # Then: the mismatch is a hard failure.
    assert report["status"] == "fail"
    assert any(
        item["id"] == "qbox:rse-mirror:start"
        and item["status"] == "fail"
        for item in report["checks"]
    )


def test_build_report_accepts_explicit_rse_local_counter_mode() -> None:
    # Given: RSE local mode with explicit rate, basis, and reset evidence.
    module = load_module()
    qbox = snapshot("qbox")
    source = qbox["source"]
    assert isinstance(source, dict)
    source["rse_smd_counter_mirror"] = False
    samples = qbox["samples"]
    assert isinstance(samples, list)
    for sample_item in samples:
        assert isinstance(sample_item, dict)
        views = sample_item["views"]
        assert isinstance(views, dict)
        for index in range(4):
            timer = views[f"rse_timer{index}"]
            assert isinstance(timer, dict)
            timer.update(
                {
                    "counter": timer["counter"] + 17,
                    "counter_basis": "rse_local",
                    "input_frequency_hz": 100_000_000,
                    "reset_domain": "rse_local_aon",
                }
            )

    # When: the explicit independent-mode contract is checked.
    report = module.build_report(qbox, snapshot("fvp"))

    # Then: CSS identity remains strict while RSE may be independent.
    assert report["status"] == "pass"


def test_build_report_rejects_missing_rse_mirror_mode() -> None:
    # Given: a QBox snapshot without the platform mode that explains RSE time.
    module = load_module()
    qbox = snapshot("qbox")
    source = qbox["source"]
    assert isinstance(source, dict)
    del source["rse_smd_counter_mirror"]

    # When: the source contract is checked.
    report = module.build_report(qbox, snapshot("fvp"))

    # Then: ambiguous RSE evidence is rejected.
    assert report["status"] == "fail"
    assert any(
        item["id"] == "qbox:rse-mode" and item["status"] == "fail"
        for item in report["checks"]
    )


def test_cli_fails_for_unavailable_snapshot(tmp_path: Path) -> None:
    # Given: an unavailable QBox probe and a valid FVP baseline.
    qbox = snapshot("qbox")
    qbox["status"] = "unavailable"
    qbox_path = tmp_path / "qbox.json"
    fvp_path = tmp_path / "fvp.json"
    output = tmp_path / "report.json"
    qbox_path.write_text(json.dumps(qbox), encoding="utf-8")
    fvp_path.write_text(json.dumps(snapshot("fvp")), encoding="utf-8")

    # When: the strict comparison CLI runs.
    completed = subprocess.run(
        [sys.executable, str(SCRIPT), "--qbox", str(qbox_path), "--fvp", str(fvp_path), "--output", str(output)],
        cwd=ROOT,
        check=False,
        text=True,
        capture_output=True,
    )

    # Then: unavailable evidence is a hard non-pass.
    assert completed.returncode == 1
    assert json.loads(output.read_text(encoding="utf-8"))["status"] == "fail"
