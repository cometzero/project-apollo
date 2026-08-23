from __future__ import annotations

from dataclasses import dataclass
import re
from typing import Final

FIELD_RE: Final = re.compile(r"^[A-Za-z0-9_./,:+-]+$")
EXPECTED_STATES: Final = tuple(
    (cpu, state, name, residency, latency)
    for cpu in range(4)
    for state, name, residency, latency in (
        ("state0", "WFI", 1, 1),
        ("state1", "cpu-sleep", 4200, 4000),
        ("state2", "cluster-sleep", 4500, 4200),
    )
)


@dataclass(frozen=True, slots=True)
class Record:
    fields: tuple[tuple[str, str], ...]

    def value(self, name: str) -> str | None:
        return next((value for key, value in self.fields if key == name), None)


def _records(output: str, marker: str) -> tuple[Record, ...]:
    parsed: list[Record] = []
    for line in output.splitlines():
        if not line.startswith(marker + " "):
            continue
        fields: list[tuple[str, str]] = []
        for token in line.removeprefix(marker + " ").split():
            if "=" not in token:
                return ()
            name, value = token.split("=", maxsplit=1)
            if not name or not value or FIELD_RE.fullmatch(value) is None:
                return ()
            if any(existing == name for existing, _value in fields):
                return ()
            fields.append((name, value))
        parsed.append(Record(tuple(fields)))
    return tuple(parsed)


def _integer(record: Record, name: str) -> int | None:
    value = record.value(name)
    if value is None or not value.isdecimal():
        return None
    return int(value)


def _has_fields(record: Record, names: frozenset[str]) -> bool:
    return frozenset(name for name, _value in record.fields) == names


def _increases(record: Record, before_name: str, after_name: str) -> bool:
    before = _integer(record, before_name)
    after = _integer(record, after_name)
    return before is not None and after is not None and after > before


def _state_map(
    records: tuple[Record, ...],
    fields: frozenset[str],
) -> dict[tuple[int, str], Record] | None:
    mapped: dict[tuple[int, str], Record] = {}
    for record in records:
        if not _has_fields(record, fields):
            return None
        cpu = _integer(record, "cpu")
        state = record.value("state")
        if cpu is None or state is None or (cpu, state) in mapped:
            return None
        mapped[(cpu, state)] = record
    expected = {(cpu, state) for cpu, state, _name, _res, _lat in EXPECTED_STATES}
    return mapped if set(mapped) == expected else None


def evaluate_cpuidle_probe(outputs: tuple[str, ...]) -> tuple[bool, ...]:
    combined = "\n".join(outputs)
    ensure = _records(combined, "CPUIDLE_ENSURE")
    cstates = _state_map(
        _records(combined, "CPUIDLE_CSTATE"),
        frozenset({"cpu", "state", "name"}),
    )
    defaults = _state_map(
        _records(combined, "CPUIDLE_DEFAULT"),
        frozenset({"cpu", "state", "value"}),
    )
    disabled = _state_map(
        _records(combined, "CPUIDLE_DISABLE"),
        frozenset(
            {
                "cpu",
                "state",
                "before",
                "after_write",
                "baseline_usage",
                "baseline_time",
                "sample0_usage",
                "sample0_time",
                "sample1_usage",
                "sample1_time",
                "peer_disable_before",
                "peer_disable_after",
                "restored",
            }
        ),
    )
    residency = _state_map(
        _records(combined, "CPUIDLE_RESIDENCY"),
        frozenset(
            {
                "cpu",
                "state",
                "residency",
                "latency",
                "usage_before",
                "usage_after",
                "time_before",
                "time_after",
                "wake",
                "restored",
            }
        ),
    )
    governors = _records(combined, "CPUIDLE_GOVERNORS")
    switches = _records(combined, "CPUIDLE_SWITCH")
    restored = _records(combined, "CPUIDLE_SWITCH_RESTORE")
    invalid = _records(combined, "CPUIDLE_INVALID")
    state_names = cstates is not None and all(
        cstates[(cpu, state)].value("name") == name
        for cpu, state, name, _res, _lat in EXPECTED_STATES
    )
    default_ok = defaults is not None and all(
        record.value("value") == "enabled" for record in defaults.values()
    )
    disable_ok = disabled is not None and all(
        record.value("before") == "0"
        and record.value("after_write") == "1"
        and record.value("restored") == "0"
        and record.value("peer_disable_before") == "0"
        and record.value("peer_disable_after") == "0"
        and all(
            _integer(record, field) is not None
            for field in (
                "baseline_usage",
                "baseline_time",
                "sample0_usage",
                "sample0_time",
                "sample1_usage",
                "sample1_time",
            )
        )
        and _integer(record, "baseline_usage")
        == _integer(record, "sample0_usage")
        == _integer(record, "sample1_usage")
        and _integer(record, "baseline_time")
        == _integer(record, "sample0_time")
        == _integer(record, "sample1_time")
        for record in disabled.values()
    )
    residency_ok = residency is not None and all(
        _integer(residency[(cpu, state)], "residency") == expected_res
        and _integer(residency[(cpu, state)], "latency") == expected_lat
        and residency[(cpu, state)].value("restored") == "1"
        and residency[(cpu, state)].value("wake") == "natural-timer"
        and _increases(residency[(cpu, state)], "usage_before", "usage_after")
        and _increases(residency[(cpu, state)], "time_before", "time_after")
        for cpu, state, _name, expected_res, expected_lat in EXPECTED_STATES
    )
    governor = governors[0] if len(governors) == 1 else Record(())
    available_raw = governor.value("available") or ""
    available = tuple(item for item in available_raw.split(",") if item)
    original = governor.value("current")
    governors_ok = (
        _has_fields(
            governor,
            frozenset({"available", "current", "current_ro"}),
        )
        and available == ("menu", "teo")
        and original in available
        and governor.value("current_ro") == original
    )
    switching_ok = (
        governors_ok
        and len(switches) == len(available)
        and len(restored) == 1
        and all(
            _has_fields(
                item,
                frozenset({"requested", "current", "current_ro"}),
            )
            for item in switches
        )
        and _has_fields(
            restored[0],
            frozenset({"original", "current", "current_ro", "restored"}),
        )
        and {item.value("requested") for item in switches} == set(available)
        and all(
            item.value("current") == item.value("requested")
            and item.value("current_ro") == item.value("requested")
            for item in switches
        )
        and restored[0].value("original") == original
        and restored[0].value("current") == original
        and restored[0].value("current_ro") == original
        and restored[0].value("restored") == "1"
    )
    invalid_ok = (
        governors_ok
        and len(invalid) == 1
        and _has_fields(
            invalid[0],
            frozenset(
                {
                    "rejected",
                    "original",
                    "current",
                    "current_ro",
                    "disable_zero",
                    "restored",
                }
            ),
        )
        and invalid[0].value("rejected") == "1"
        and invalid[0].value("original") == original
        and invalid[0].value("current") == original
        and invalid[0].value("current_ro") == original
        and invalid[0].value("disable_zero") == "12"
        and invalid[0].value("restored") == "1"
    )
    return (
        len(ensure) == 1
        and _has_fields(ensure[0], frozenset({"cpu_count", "states"}))
        and ensure[0].value("cpu_count") == "4"
        and ensure[0].value("states") == "12",
        state_names,
        default_ok,
        disable_ok,
        residency_ok,
        governors_ok,
        switching_ok,
        invalid_ok,
    )
