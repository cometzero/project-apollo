"""Typed schema and immutable contracts for Apollo timer snapshots."""

from __future__ import annotations

from typing import Final, NotRequired, TypedDict


SCHEMA_VERSION: Final = 1
COUNTER_MASK: Final = (1 << 64) - 1
CSS_VIEW_IDS: Final = (
    "smd",
    "ap_cpu0",
    "ap_refclk_ns",
    "ap_refclk_s",
    "si0_cpu0",
    "si0_cntbase",
    "si1_cpu0",
)
REPORTED_FREQUENCIES_HZ: Final = {
    "ap_cpu0": 125_000_000,
    "ap_refclk_ns": 125_000_000,
    "ap_refclk_s": 125_000_000,
    "si1_cpu0": 100_000_000,
}
RSE_IRQS: Final = {
    "rse_timer0": 3,
    "rse_timer1": 4,
    "rse_timer2": 5,
    "rse_timer3": 27,
}


class TimerView(TypedDict):
    domain: str
    counter: NotRequired[int]
    reported_frequency_hz: NotRequired[int]
    input_frequency_hz: NotRequired[int]
    increment: NotRequired[int]
    cval: NotRequired[int]
    enabled: NotRequired[bool]
    masked: NotRequired[bool]
    istatus: NotRequired[bool]
    irq: NotRequired[int]
    access_control_state: NotRequired[str]
    counter_basis: NotRequired[str]
    reset_domain: NotRequired[str]
    observed_counter: NotRequired[int]
    observation_time_ns: NotRequired[int]
    observed: bool


class TimerSample(TypedDict):
    name: str
    marker: str
    sim_time_ns: int
    raw_simulation_ticks: NotRequired[int]
    iris_timebase_hz: NotRequired[int]
    views: dict[str, TimerView]


class TimerSource(TypedDict):
    machine: str
    revision: str
    run_id: NotRequired[str]
    rse_smd_counter_mirror: NotRequired[bool]


class TimerSnapshot(TypedDict):
    schema_version: int
    producer: str
    status: str
    captured_at: str
    source: TimerSource
    samples: list[TimerSample]


class Check(TypedDict):
    id: str
    status: str
    message: str
