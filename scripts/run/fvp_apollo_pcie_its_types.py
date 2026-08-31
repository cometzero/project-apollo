from __future__ import annotations

from dataclasses import dataclass
from typing import Literal, NotRequired, TypedDict


type JsonScalar = str | int | float | bool | None
type JsonValue = JsonScalar | list[JsonValue] | dict[str, JsonValue]
type JsonObject = dict[str, JsonValue]


@dataclass(frozen=True, slots=True)
class RunError(Exception):
    reason: str
    detail: str = ""

    def __str__(self) -> str:
        return f"{self.reason}: {self.detail}" if self.detail else self.reason


class DtContract(TypedDict):
    node: str
    ecam_base: str
    its_base: str
    smmu_base: str


class ProcessObservation(TypedDict):
    pid: int
    ppid: int
    argv: list[str]
    observed_at_unix: float


class CleanupReceipt(TypedDict):
    observed_fvp_pids: list[int]
    remaining_observed_fvp_pids: list[int]
    clean: bool


class FvpResult(TypedDict):
    schema_version: Literal[1]
    status: Literal["pass", "fail"]
    reason: str
    profile_sha256: str
    configuration_applied: bool
    qbox_started: Literal[False]
    detail: NotRequired[JsonObject]


def json_strings(values: list[str]) -> list[JsonValue]:
    return [value for value in values]


def json_integers(values: list[int]) -> list[JsonValue]:
    return [value for value in values]


def observations_json(observations: list[ProcessObservation]) -> list[JsonValue]:
    serialized: list[JsonValue] = []
    for item in observations:
        record: JsonObject = {
            "pid": item["pid"],
            "ppid": item["ppid"],
            "argv": json_strings(item["argv"]),
            "observed_at_unix": item["observed_at_unix"],
        }
        serialized.append(record)
    return serialized


def cleanup_json(receipt: CleanupReceipt) -> JsonObject:
    return {
        "observed_fvp_pids": json_integers(receipt["observed_fvp_pids"]),
        "remaining_observed_fvp_pids": json_integers(
            receipt["remaining_observed_fvp_pids"]
        ),
        "clean": receipt["clean"],
    }


def contract_json(contract: DtContract) -> JsonObject:
    return {
        "node": contract["node"],
        "ecam_base": contract["ecam_base"],
        "its_base": contract["its_base"],
        "smmu_base": contract["smmu_base"],
    }
