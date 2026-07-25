#!/usr/bin/env python3
"""Compare structured Apollo QBox and FVP timer snapshots."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))
from timer_snapshot_schema import (
    COUNTER_MASK,
    CSS_VIEW_IDS,
    REPORTED_FREQUENCIES_HZ,
    RSE_IRQS,
    SCHEMA_VERSION,
    Check,
    TimerSample,
    TimerSnapshot,
    TimerSource,
    TimerView,
)


def check(check_id: str, passed: bool, message: str) -> Check:
    return {"id": check_id, "status": "pass" if passed else "fail", "message": message}


def css_identity_checks(producer: str, snapshot: TimerSnapshot) -> list[Check]:
    checks: list[Check] = []
    for sample in snapshot["samples"]:
        required = [sample["views"].get(view_id) for view_id in CSS_VIEW_IDS]
        valid = all(
            view is not None and view["observed"] and "counter" in view
            for view in required
        )
        secure_frame = sample["views"].get("ap_refclk_s")
        valid = valid and secure_frame is not None and secure_frame.get("access_control_state") == "enabled"
        counters = [view["counter"] for view in required if view is not None and "counter" in view]
        valid = valid and len(set(counters)) == 1
        checks.append(
            check(
                f"{producer}:css-identity:{sample['name']}",
                valid,
                "same-timestamp CSS view counters must be exactly equal",
            )
        )
    return checks


def samples_by_name(snapshot: TimerSnapshot) -> dict[str, TimerSample]:
    return {sample["name"]: sample for sample in snapshot["samples"]}
def snapshot_names_are_unique(snapshot: TimerSnapshot) -> bool:
    return len(samples_by_name(snapshot)) == len(snapshot["samples"])
def quantized_rates_overlap(
    qbox_start: TimerSample, qbox_end: TimerSample, fvp_start: TimerSample, fvp_end: TimerSample,
    qbox_delta: int, fvp_delta: int,
) -> bool:
    raw_fields = ("raw_simulation_ticks", "iris_timebase_hz")

    def timing(start: TimerSample, end: TimerSample) -> tuple[int, int]:
        if all(field in start and field in end for field in raw_fields):
            if start["iris_timebase_hz"] != end["iris_timebase_hz"]:
                return 0, 0
            return (
                end["raw_simulation_ticks"] - start["raw_simulation_ticks"],
                start["iris_timebase_hz"],
            )
        return end["sim_time_ns"] - start["sim_time_ns"], 1_000_000_000

    qbox_ticks, qbox_hz = timing(qbox_start, qbox_end)
    fvp_ticks, fvp_hz = timing(fvp_start, fvp_end)
    if qbox_ticks <= 0 or fvp_ticks <= 0 or qbox_hz <= 0 or fvp_hz <= 0:
        return False
    return (qbox_delta - 1) * qbox_hz * fvp_ticks <= (fvp_delta + 1) * fvp_hz * qbox_ticks and (fvp_delta - 1) * fvp_hz * qbox_ticks <= (qbox_delta + 1) * qbox_hz * fvp_ticks


def rate_checks(qbox: TimerSnapshot, fvp: TimerSnapshot) -> list[Check]:
    qbox_samples = samples_by_name(qbox)
    fvp_samples = samples_by_name(fvp)
    common = sorted(
        (name for name in qbox_samples if name in fvp_samples),
        key=lambda name: (qbox_samples[name]["sim_time_ns"], fvp_samples[name]["sim_time_ns"], name),
    )
    checks: list[Check] = []
    checks.append(check("rate:common-samples", len(common) >= 2, "at least two ordered common samples are required"))
    for start_name, end_name in zip(common, common[1:]):
        qbox_start, qbox_end = qbox_samples[start_name], qbox_samples[end_name]
        fvp_start, fvp_end = fvp_samples[start_name], fvp_samples[end_name]
        qbox_elapsed = qbox_end["sim_time_ns"] - qbox_start["sim_time_ns"]
        fvp_elapsed = fvp_end["sim_time_ns"] - fvp_start["sim_time_ns"]
        for view_id in sorted(set(qbox_start["views"]) & set(fvp_start["views"])):
            if view_id not in CSS_VIEW_IDS:
                continue
            qbox_start_view = qbox_start["views"][view_id]
            qbox_end_view = qbox_end["views"].get(view_id)
            fvp_start_view = fvp_start["views"][view_id]
            fvp_end_view = fvp_end["views"].get(view_id)
            required = (qbox_end_view, fvp_end_view)
            if (
                qbox_elapsed <= 0
                or fvp_elapsed <= 0
                or any(view is None for view in required)
                or "counter" not in qbox_start_view
                or "counter" not in fvp_start_view
                or qbox_end_view is None
                or fvp_end_view is None
                or "counter" not in qbox_end_view
                or "counter" not in fvp_end_view
            ):
                continue
            qbox_delta = (qbox_end_view["counter"] - qbox_start_view["counter"]) & COUNTER_MASK
            fvp_delta = (fvp_end_view["counter"] - fvp_start_view["counter"]) & COUNTER_MASK
            equal_rate = quantized_rates_overlap(
                qbox_start, qbox_end, fvp_start, fvp_end, qbox_delta, fvp_delta
            )
            checks.append(
                check(
                    f"rate:{view_id}:{start_name}->{end_name}",
                    equal_rate,
                    "two-sample counter delta/rate must match across producers",
                )
            )
    return checks


def qbox_contract_checks(snapshot: TimerSnapshot) -> list[Check]:
    mode = snapshot["source"].get("rse_smd_counter_mirror")
    checks: list[Check] = [
        check(
            "qbox:rse-mode",
            isinstance(mode, bool),
            "QBox source must declare boolean RSE SMD counter mirror mode",
        )
    ]
    for sample in snapshot["samples"]:
        views = sample["views"]
        smd = views.get("smd")
        smd_contract = smd is not None and smd.get("input_frequency_hz") == 125_000_000 and smd.get("increment") == 1 and smd.get("reported_frequency_hz") == 125_000_000
        checks.append(check(f"qbox:normal-css-contract:{sample['name']}", smd_contract, "normal CSS count contract is 125MHz input, increment 1, reported 125MHz"))
        mirror_observation_valid = all(
            views.get(view_id) is not None
            and views[view_id].get("observed_counter")
            == views[view_id].get("counter")
            for view_id in CSS_VIEW_IDS
        )
        checks.append(
            check(
                f"qbox:mirror-observation:{sample['name']}",
                mirror_observation_valid,
                "all CSS local mirrors must match the authority at the synchronization barrier",
            )
        )
        for view_id, expected_hz in REPORTED_FREQUENCIES_HZ.items():
            view = views.get(view_id)
            checks.append(check(f"qbox:reported-frequency:{view_id}:{sample['name']}", view is not None and view.get("reported_frequency_hz") == expected_hz, f"{view_id} reported frequency must be {expected_hz}Hz"))
        for view_id, expected_irq in (("ap_refclk_ns", 49), ("ap_refclk_s", 48), *RSE_IRQS.items()):
            view = views.get(view_id)
            checks.append(check(f"qbox:irq:{view_id}:{sample['name']}", view is not None and view.get("irq") == expected_irq, f"{view_id} IRQ must be {expected_irq}"))
        for view_id in ("ap_refclk_ns", "ap_refclk_s"):
            view = views.get(view_id)
            deadline_state = view is not None and all(field in view for field in ("cval", "enabled", "masked", "istatus"))
            checks.append(check(f"qbox:deadline-state:{view_id}:{sample['name']}", deadline_state, "AP MMIO timer deadline state must be observed"))
        rse_views = [views.get(view_id) for view_id in RSE_IRQS]
        if mode is True:
            mirror_valid = (
                smd is not None
                and "counter" in smd
                and all(
                    view is not None
                    and view.get("counter") == smd["counter"]
                    and view.get("observed_counter") == smd["counter"]
                    and view.get("counter_basis") == "css_mirror"
                    for view in rse_views
                )
            )
            checks.append(
                check(
                    f"qbox:rse-mirror:{sample['name']}",
                    mirror_valid,
                    "RSE TIMER0-3 must use the SMD counter in mirror mode",
                )
            )
        elif mode is False:
            local_valid = all(
                view is not None
                and view.get("counter_basis") == "rse_local"
                and isinstance(view.get("input_frequency_hz"), int)
                and view.get("input_frequency_hz", 0) > 0
                and view.get("reset_domain") == "rse_local_aon"
                for view in rse_views
            )
            checks.append(
                check(
                    f"qbox:rse-local:{sample['name']}",
                    local_valid,
                    "RSE local mode requires explicit rate, basis, and reset evidence",
                )
            )
    if mode is False and len(snapshot["samples"]) >= 2:
        start, end = snapshot["samples"][0], snapshot["samples"][-1]
        elapsed_ns = end["sim_time_ns"] - start["sim_time_ns"]
        start_views = [start["views"].get(view_id) for view_id in RSE_IRQS]
        end_views = [end["views"].get(view_id) for view_id in RSE_IRQS]
        local_rate_valid = elapsed_ns > 0
        for start_view, end_view in zip(start_views, end_views):
            if (
                start_view is None
                or end_view is None
                or "counter" not in start_view
                or "counter" not in end_view
                or not isinstance(start_view.get("input_frequency_hz"), int)
            ):
                local_rate_valid = False
                continue
            delta = (end_view["counter"] - start_view["counter"]) & COUNTER_MASK
            expected = (
                start_view["input_frequency_hz"] * elapsed_ns
            ) // 1_000_000_000
            local_rate_valid = local_rate_valid and abs(delta - expected) <= 1
        checks.append(
            check(
                "qbox:rse-local-rate",
                local_rate_valid,
                "RSE local counter delta must match its independent input rate",
            )
        )
    return checks


def build_report(qbox: TimerSnapshot, fvp: TimerSnapshot) -> dict[str, object]:
    checks = [
        check("qbox:snapshot-status", qbox["status"] == "pass", "QBox snapshot must be pass"),
        check("fvp:snapshot-status", fvp["status"] == "pass", "FVP snapshot must be pass"),
        check("qbox:schema", qbox["schema_version"] == SCHEMA_VERSION, "QBox schema version must match"),
        check("fvp:schema", fvp["schema_version"] == SCHEMA_VERSION, "FVP schema version must match"),
        check("qbox:sample-names", snapshot_names_are_unique(qbox), "QBox sample names must be unique"),
        check("fvp:sample-names", snapshot_names_are_unique(fvp), "FVP sample names must be unique"),
        *css_identity_checks("qbox", qbox),
        *css_identity_checks("fvp", fvp),
        *qbox_contract_checks(qbox),
        *rate_checks(qbox, fvp),
    ]
    return {
        "schema_version": SCHEMA_VERSION,
        "status": "pass" if all(item["status"] == "pass" for item in checks) else "fail",
        "inputs": {"qbox_producer": qbox["producer"], "fvp_producer": fvp["producer"]},
        "checks": checks,
    }


def read_snapshot(path: Path) -> TimerSnapshot:
    raw = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise ValueError(f"snapshot is not an object: {path}")
    required = {"schema_version", "producer", "status", "captured_at", "source", "samples"}
    missing = sorted(required - set(raw))
    if missing:
        raise ValueError(f"snapshot missing fields {missing}: {path}")
    source = raw["source"]
    samples = raw["samples"]
    if not isinstance(source, dict) or not isinstance(samples, list):
        raise ValueError(f"snapshot source/samples have invalid types: {path}")
    source_machine = source.get("machine")
    source_revision = source.get("revision")
    if not isinstance(source_machine, str) or not isinstance(source_revision, str):
        raise ValueError(f"snapshot source is incomplete: {path}")
    parsed_samples: list[TimerSample] = []
    for sample in samples:
        if not isinstance(sample, dict):
            raise ValueError(f"snapshot sample is not an object: {path}")
        name, marker, sim_time_ns, views = (
            sample.get("name"),
            sample.get("marker"),
            sample.get("sim_time_ns"),
            sample.get("views"),
        )
        if not isinstance(name, str) or not isinstance(marker, str) or not isinstance(sim_time_ns, int) or not isinstance(views, dict):
            raise ValueError(f"snapshot sample is incomplete: {path}")
        parsed_views: dict[str, TimerView] = {}
        for view_id, view in views.items():
            if not isinstance(view_id, str) or not isinstance(view, dict):
                raise ValueError(f"snapshot view is invalid: {path}")
            domain, observed = view.get("domain"), view.get("observed")
            if not isinstance(domain, str) or not isinstance(observed, bool):
                raise ValueError(f"snapshot view is incomplete: {path}")
            parsed_views[view_id] = {"domain": domain, "observed": observed}
            for field in (
                "counter",
                "reported_frequency_hz",
                "input_frequency_hz",
                "increment",
                "cval",
                "irq",
                "observed_counter",
                "observation_time_ns",
            ):
                value = view.get(field)
                if isinstance(value, int):
                    parsed_views[view_id][field] = value
            for field in ("enabled", "masked", "istatus"):
                value = view.get(field)
                if isinstance(value, bool):
                    parsed_views[view_id][field] = value
            access_control_state = view.get("access_control_state")
            if isinstance(access_control_state, str):
                parsed_views[view_id]["access_control_state"] = access_control_state
            counter_basis = view.get("counter_basis")
            if isinstance(counter_basis, str):
                parsed_views[view_id]["counter_basis"] = counter_basis
            reset_domain = view.get("reset_domain")
            if isinstance(reset_domain, str):
                parsed_views[view_id]["reset_domain"] = reset_domain
        parsed = {"name": name, "marker": marker, "sim_time_ns": sim_time_ns, "views": parsed_views}
        for field in ("raw_simulation_ticks", "iris_timebase_hz"):
            value = sample.get(field)
            if isinstance(value, int):
                parsed[field] = value
        parsed_samples.append(parsed)
    schema_version, producer, status, captured_at = (
        raw["schema_version"], raw["producer"], raw["status"], raw["captured_at"]
    )
    if not isinstance(schema_version, int) or not isinstance(producer, str) or not isinstance(status, str) or not isinstance(captured_at, str):
        raise ValueError(f"snapshot header is invalid: {path}")
    parsed_source: TimerSource = {
        "machine": source_machine,
        "revision": source_revision,
    }
    run_id = source.get("run_id")
    if isinstance(run_id, str):
        parsed_source["run_id"] = run_id
    rse_mode = source.get("rse_smd_counter_mirror")
    if isinstance(rse_mode, bool):
        parsed_source["rse_smd_counter_mirror"] = rse_mode
    return {
        "schema_version": schema_version,
        "producer": producer,
        "status": status,
        "captured_at": captured_at,
        "source": parsed_source,
        "samples": parsed_samples,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--qbox", type=Path, required=True)
    parser.add_argument("--fvp", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    report = build_report(read_snapshot(args.qbox), read_snapshot(args.fvp))
    report["inputs"] = {"qbox": str(args.qbox.resolve()), "fvp": str(args.fvp.resolve())}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(args.output)
    for item in report["checks"]:
        if item["status"] == "fail":
            print(f"FAIL {item['id']}: {item['message']}", file=sys.stderr)
    return 0 if report["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
