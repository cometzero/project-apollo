from __future__ import annotations

from dataclasses import dataclass
import re
from typing import Final


FIELD_RE: Final = re.compile(r"^[A-Za-z0-9_./,:+-]+$")
GOVERNORS: Final = frozenset({"ondemand", "performance", "powersave", "schedutil"})
OPPS: Final = frozenset({1800000, 2000000, 2500000})


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
            if (
                not name
                or not value
                or FIELD_RE.fullmatch(value) is None
                or any(existing == name for existing, _value in fields)
            ):
                return ()
            fields.append((name, value))
        parsed.append(Record(tuple(fields)))
    return tuple(parsed)


def _fields(record: Record, expected: frozenset[str]) -> bool:
    return frozenset(name for name, _value in record.fields) == expected


def _integer(record: Record, field: str) -> int | None:
    value = record.value(field)
    return int(value) if value is not None and value.isdecimal() else None


def _csv(record: Record, field: str) -> tuple[str, ...]:
    value = record.value(field)
    return tuple(value.split(",")) if value else ()


def _integer_csv(record: Record, field: str) -> frozenset[int] | None:
    values = _csv(record, field)
    return (
        frozenset(int(value) for value in values)
        if all(value.isdecimal() for value in values)
        else None
    )


def _policy_names(cpu_count: int) -> tuple[str, ...]:
    return tuple(f"policy{first}" for first in range(0, cpu_count, 4))


def _by_policy(
    records: tuple[Record, ...],
    fields: frozenset[str],
    policies: tuple[str, ...],
) -> dict[str, Record] | None:
    mapped: dict[str, Record] = {}
    for record in records:
        policy = record.value("policy")
        if not _fields(record, fields) or policy is None or policy in mapped:
            return None
        mapped[policy] = record
    return mapped if set(mapped) == set(policies) else None


def _restored(output: str, policies: tuple[str, ...]) -> bool:
    records = _by_policy(
        _records(output, "CPUFREQ_RESTORE"),
        frozenset({"policy", "governor", "min", "max", "restored"}),
        policies,
    )
    return records is not None and all(
        record.value("governor") == "schedutil"
        and record.value("min") == "1800000"
        and record.value("max") == "2500000"
        and record.value("restored") == "1"
        for record in records.values()
    )


def _matrix(
    records: tuple[Record, ...],
    fields: frozenset[str],
    policies: tuple[str, ...],
    values: frozenset[str],
    value_field: str,
) -> bool:
    if len(records) != len(policies) * len(values):
        return False
    pairs: set[tuple[str, str]] = set()
    for record in records:
        policy = record.value("policy")
        value = record.value(value_field)
        if not _fields(record, fields) or policy is None or value is None:
            return False
        pairs.add((policy, value))
    return pairs == {(policy, value) for policy in policies for value in values}


def evaluate_cpufreq_probe(outputs: tuple[str, ...]) -> tuple[bool, ...]:
    padded = (*outputs[:10], *("" for _missing in range(max(0, 10 - len(outputs)))))
    metadata = _records(padded[0], "CPUFREQ_META")
    meta = metadata[0] if len(metadata) == 1 else Record(())
    cpu_count = _integer(meta, "cpu_count")
    policies = _policy_names(cpu_count) if cpu_count in {4, 16} else ()
    policy_records = _by_policy(
        _records(padded[0], "CPUFREQ_POLICY"),
        frozenset(
            {
                "policy",
                "governors",
                "frequencies",
                "driver",
                "affected",
                "min",
                "max",
                "current",
            }
        ),
        policies,
    )
    policy_ok = (
        len(outputs) == 10
        and _fields(
            meta, frozenset({"cpu_count", "guest_contract", "performance_coupling"})
        )
        and meta.value("guest_contract") == "identical"
        and meta.value("performance_coupling") == "unsupported"
        and policy_records is not None
        and all(
            frozenset(_csv(record, "governors")) == GOVERNORS
            and _integer_csv(record, "frequencies") == OPPS
            and record.value("driver") == "scmi"
            and _csv(record, "affected")
            == tuple(
                str(cpu)
                for cpu in range(
                    int(policy.removeprefix("policy")),
                    int(policy.removeprefix("policy")) + 4,
                )
            )
            and record.value("min") == "1800000"
            and record.value("max") == "2500000"
            and _integer(record, "current") in OPPS
            for policy, record in policy_records.items()
        )
    )
    defaults = _by_policy(
        _records(padded[1], "CPUFREQ_DEFAULT"),
        frozenset({"policy", "governor"}),
        policies,
    )
    governors = _records(padded[2], "CPUFREQ_GOVERNOR")
    drivers = _by_policy(
        _records(padded[3], "CPUFREQ_DRIVER"),
        frozenset({"policy", "driver"}),
        policies,
    )
    current = _records(padded[4], "CPUFREQ_CURRENT")
    affected = _by_policy(
        _records(padded[5], "CPUFREQ_AFFECTED"),
        frozenset({"policy", "cpus"}),
        policies,
    )
    invalid = _by_policy(
        _records(padded[6], "CPUFREQ_INVALID_GOVERNOR"),
        frozenset({"policy", "rejected", "unchanged"}),
        policies,
    )
    minimum = _records(padded[7], "CPUFREQ_MIN")
    maximum = _records(padded[8], "CPUFREQ_MAX")
    negative = _by_policy(
        _records(padded[9], "CPUFREQ_NEGATIVE"),
        frozenset({"policy", "rejected_min", "rejected_max", "unchanged"}),
        policies,
    )
    governor_values = frozenset(GOVERNORS)
    opp_values = frozenset(str(item) for item in OPPS)
    return (
        policy_ok,
        defaults is not None
        and all(item.value("governor") == "schedutil" for item in defaults.values()),
        _matrix(
            governors,
            frozenset({"policy", "requested", "actual"}),
            policies,
            governor_values,
            "requested",
        )
        and all(item.value("actual") == item.value("requested") for item in governors)
        and _restored(padded[2], policies),
        drivers is not None
        and all(item.value("driver") == "scmi" for item in drivers.values()),
        _matrix(
            current,
            frozenset({"policy", "governor", "frequency"}),
            policies,
            governor_values,
            "governor",
        )
        and all(_integer(item, "frequency") in OPPS for item in current)
        and _restored(padded[4], policies),
        affected is not None
        and all(
            _csv(item, "cpus")
            == tuple(
                str(cpu)
                for cpu in range(
                    int(policy.removeprefix("policy")),
                    int(policy.removeprefix("policy")) + 4,
                )
            )
            for policy, item in affected.items()
        ),
        invalid is not None
        and all(
            item.value("rejected") == "1" and item.value("unchanged") == "1"
            for item in invalid.values()
        )
        and _restored(padded[6], policies),
        _matrix(
            minimum,
            frozenset({"policy", "frequency", "applied"}),
            policies,
            opp_values,
            "frequency",
        )
        and all(item.value("applied") == "1" for item in minimum)
        and _restored(padded[7], policies),
        _matrix(
            maximum,
            frozenset({"policy", "frequency", "applied"}),
            policies,
            opp_values,
            "frequency",
        )
        and all(item.value("applied") == "1" for item in maximum)
        and _restored(padded[8], policies),
        negative is not None
        and all(
            item.value("rejected_min") == "1"
            and item.value("rejected_max") == "1"
            and item.value("unchanged") == "1"
            for item in negative.values()
        )
        and _restored(padded[9], policies),
    )
