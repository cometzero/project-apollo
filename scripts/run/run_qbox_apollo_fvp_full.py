#!/usr/bin/env python3
"""Run or preflight the Apollo FVP full-system QBox path."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
import datetime as _dt
import errno
import hashlib
import json
import os
from pathlib import Path
import re
import signal
import shutil
import stat
import subprocess
import sys
import time
from types import FrameType
from typing import Any
from typing import Literal, TypedDict
import uuid

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))
import qbox_apollo_fidelity as fidelity_runner  # noqa: E402
import qbox_apollo_runtime as runtime_engine  # noqa: E402


CONSOLE_LOGS = {
    "platform": "qbox-platform.log",
    "rse": "qbox-rse.log",
    "si_cl0": "qbox-safety-island-cl0.log",
    "si_cl1": "qbox-safety-island-cl1.log",
    "secure_console": "qbox-secure-console.log",
    "primary_console": "qbox-primary-console.log",
}
RD_ASPEN_CHILD_RESULT = "rd-aspen-result.json"
RSE_LCS_CM = "0xcccc3c3c"
RSE_LCS_SE = 0xEEEEA5A5

GATES = ["G0", "G1", "G2"]
DEFAULT_EXPECTED_AP_CPUS = 4
APOLLO_PRIMARY_LOGIN_PROMPT = "apollo-qvp login:"
APOLLO_PRIMARY_SHELL_MARKER = "nexios-bsp#"
CHILD_FAIL_PATTERNS = [
    "Kernel panic",
    "Unable to mount root fs",
    "No working init found",
    "[ERR]",
    "[ERROR]",
]
CHILD_REQUIRED_MARKERS = {
    "rse_boot": [
        "Starting TF-M BL1_1",
        "Jumping to the first image slot",
    ],
    "rse_scp_handoff": [
        "Init SCMI comm to SCP succeeded",
        "RSE to SCP SCMI power on AP succeeded",
        "SCMI Comms subscribed to power state notifications",
    ],
    "measured_boot": [
        "BL1_2",
        "BL2",
        "SI_CL0",
        "AP_BL2",
        "RT_0",
        "SECURE_RT_EL3",
        "SECURE_RT_EL1_SPMD",
        "BL_33",
    ],
}
CHILD_LOG_ALIASES = {
    "rse": "qbox-rse.log",
    "scp": "qbox-safety-island-cl0.log",
    "secure_console": "qbox-secure-console.log",
    "primary_console": "qbox-primary-console.log",
}
KEEP_RUNNING_PROGRESS_MARKERS = [
    ("rse_bl1_1", "TF-M BL1_1 start", "Starting TF-M BL1_1"),
    ("rse_jump_bl1_2", "BL1_1 to BL1_2 handoff", "Jumping to BL1_2"),
    ("rse_bl1_2", "TF-M BL1_2 start", "Starting TF-M BL1_2"),
    ("rse_attempt_image_0", "BL1_2 image 0 selection", "Attempting to boot image 0"),
    ("rse_bl2_decrypted", "BL2 decrypt complete", "BL2 image decrypted successfully"),
    ("rse_bl2_validated", "BL2 validation complete", "BL2 image validated successfully"),
    ("rse_jump_bl2", "BL1_2 to BL2 handoff", "Jumping to BL2"),
    ("rse_image_4_loaded", "SI CL1 image loaded", "Image 4 loaded from the primary slot"),
    ("rse_image_3_loaded", "SI CL0 image loaded", "Image 3 loaded from the primary slot"),
    ("rse_image_2_loaded", "AP BL2 image loaded", "Image 2 loaded from the primary slot"),
    ("rse_image_0_loaded", "RSE runtime image loaded", "Image 0 loaded from the primary slot"),
    (
        "rse_scp_power_on_ap",
        "AP power-on SCMI complete",
        "RSE to SCP SCMI power on AP succeeded",
    ),
    ("rse_first_image_slot", "RSE runtime handoff", "Jumping to the first image slot"),
    ("measured_boot_bl33", "U-Boot measured boot marker", "BL_33"),
    ("primary_linux_cpu", "Linux CPU boot marker", "Booting Linux on physical CPU"),
    ("primary_login_prompt", "Linux login prompt", APOLLO_PRIMARY_LOGIN_PROMPT),
]
AP_CPU_COUNT_RE = re.compile(r"^ap cpus:\s*(?P<count>\d+)\s*$", re.MULTILINE)
SI_CL1_REQUIRED_MARKERS = {
    "cpu0_oor": "Out of Reset (OoR) completed on CPU: 0",
    "zephyr_boot": "Booting Zephyr OS",
    "pfdi_agent": "PFDI Agent setup complete",
    "pfdi_service": "PFDI service ready",
    "network_configured": "si_net_init: Network interface configured",
    "rpmsg_endpoint": "RPMSG Endpoint: ATTACHED",
}
LIVE_CL1_FAIL_PATTERNS = {
    "pfdi_status_timeout": "PFDI status timed out",
    "pfdi_timeout_errno": "ret=-116",
    "pfdi_protocol_version_timeout": "PROTOCOL_VERSION timed out",
    "pfdi_agent_not_ready": "PFDI Agent device not ready",
}
SI_CL0_REQUIRED_MARKERS = {
    "scp_started": "[SI0_PLATFORM] SCP started",
    "module_init_complete": "[FWK] Module initialization complete!",
    "gic_multiview_configured": "GIC-multiview configured successfully",
}
SI_TOPOLOGY_DRY_RUN_SCRIPT = """
local function json_escape(value)
    return value:gsub("\\\\", "\\\\\\\\")
        :gsub('"', '\\\\"')
        :gsub("\\n", "\\\\n")
        :gsub("\\r", "\\\\r")
        :gsub("\\t", "\\\\t")
end
local function encode_json(value)
    local value_type=type(value)
    if value_type=="nil" then return "null" end
    if value_type=="boolean" or value_type=="number" then
        return tostring(value)
    end
    if value_type=="string" then return '"'..json_escape(value)..'"' end
    assert(value_type=="table", "unsupported topology contract value")
    local count=0
    local array=true
    for key,_ in pairs(value) do
        if type(key)~="number" or key<1 or key%1~=0 then
            array=false
            break
        end
        if key>count then count=key end
    end
    if array then
        local items={}
        for index=1,count do items[#items+1]=encode_json(value[index]) end
        return "["..table.concat(items,",").."]"
    end
    local keys={}
    for key,_ in pairs(value) do
        assert(type(key)=="string", "topology contract keys must be strings")
        keys[#keys+1]=key
    end
    table.sort(keys)
    local items={}
    for _,key in ipairs(keys) do
        items[#items+1]='"'..json_escape(key)..'":'..encode_json(value[key])
    end
    return "{"..table.concat(items,",").."}"
end
local topology=dofile(os.getenv("QBOX_APOLLO_TOPOLOGY_PATH"))
assert(topology.safety_island_contract, "missing safety_island_contract")
print(encode_json(topology.safety_island_contract))
"""
FULL_SYSTEM_AP_QEMU_DEFAULTS = (
    (
        "platform.ap_qemu_inst.tcg_mode",
        "QBOX_APOLLO_FULL_AP_TCG_MODE",
        "MULTI",
    ),
)
FULL_SYSTEM_SI_SPLIT_QEMU_DEFAULTS = (
    (
        "platform.si_cl0_qemu_inst.tcg_mode",
        "QBOX_APOLLO_FULL_SI_CL0_TCG_MODE",
        "MULTI",
    ),
    (
        "platform.si_cl1_qemu_inst.tcg_mode",
        "QBOX_APOLLO_FULL_SI_CL1_TCG_MODE",
        "MULTI",
    ),
    (
        "platform.si_cl1_qemu_inst.sync_policy",
        "QBOX_APOLLO_FULL_SI_CL1_SYNC_POLICY",
        "multithread-quantum",
    ),
)
FULL_SYSTEM_SI_SINGLE_QEMU_DEFAULTS = (
    (
        "platform.si_qemu_inst.tcg_mode",
        "QBOX_APOLLO_FULL_SI_TCG_MODE",
        "MULTI",
    ),
    (
        "platform.si_qemu_inst.sync_policy",
        "QBOX_APOLLO_FULL_SI_SYNC_POLICY",
        "multithread-quantum",
    ),
)
MARKER_GROUP_PRIORITY = [
    "rse",
    "si_cl0",
    "si_cl1",
    "ap_firmware",
    "linux",
    "maps_and_interrupts",
]
type SafetyIslandTopologyMode = Literal["single", "split"]


class SafetyIslandPeJson(TypedDict):
    pe: int
    name: str
    cluster: str
    qemu_instance: str
    mp_affinity: int
    affinity: str
    image: str
    image_loader: str
    router: str
    reset: str


class SafetyIslandGicJson(TypedDict, total=False):
    name: str
    qemu_instance: str
    redistributor_regions: list[int]
    cpu_interfaces: int
    normal_spi_count: int
    state_owner: str
    canonical: bool
    scope: str


class SafetyIslandQemuInstanceJson(TypedDict, total=False):
    name: str
    domain: str
    architecture: str
    cpu: str
    acceleration: str
    tcg_mode: str
    sync_policy: str
    ram_owner: str
    scope: str


class SafetyIslandTraceTargetJson(TypedDict, total=False):
    kind: str
    name: str
    domain: str
    qemu_instance: str
    pe: int
    affinity: str
    image: str
    cpu_interfaces: int


class SafetyIslandTopologyJson(TypedDict):
    env_var: str
    mode: SafetyIslandTopologyMode
    enabled: bool
    qemu_instances: list[SafetyIslandQemuInstanceJson]
    pes: list[SafetyIslandPeJson]
    gics: list[SafetyIslandGicJson]
    reset_targets: list[str]
    trace_targets: list[SafetyIslandTraceTargetJson]
    rollback_command: str


class SafetyIslandResultFields(TypedDict):
    safety_island_gic_topology: SafetyIslandTopologyJson
    si_gic_topology_mode: SafetyIslandTopologyMode
    si_qemu_instance_count: int
    si_pe_map: list[SafetyIslandPeJson]
    si_reset_fanout: list[str]
    si_trace_targets: list[SafetyIslandTraceTargetJson]
    si_rollback_command: str
    si_topology_source: str
    si_topology_source_sha256: str
    si_topology_contract_sha256: str
    runner_source_sha256: str


class SafetyIslandChildEnvironment(TypedDict, total=False):
    QBOX_APOLLO_FULL_SI_SINGLE_GIC: str
    QBOX_APOLLO_FULL_SI_ACCEL: str
    QBOX_APOLLO_FULL_SI_TCG_MODE: str
    QBOX_APOLLO_FULL_SI_SYNC_POLICY: str
    QBOX_APOLLO_FULL_SI_CL0_ACCEL: str
    QBOX_APOLLO_FULL_SI_CL0_TCG_MODE: str
    QBOX_APOLLO_FULL_SI_CL0_SYNC_POLICY: str
    QBOX_APOLLO_FULL_SI_CL1_ACCEL: str
    QBOX_APOLLO_FULL_SI_CL1_TCG_MODE: str
    QBOX_APOLLO_FULL_SI_CL1_SYNC_POLICY: str
    QBOX_APOLLO_FULL_SI_CL0_UART_READ_FILE: str


class SiCl0CommandRecord(TypedDict):
    command: str
    sha256: str
    raw_uart_sha256: str
    started_at: str
    done_at: str | None
    exit_at: str | None
    timed_out: bool
    timeout_seconds: float
    transport_returncode: int
    bytes_sent: int


class SiCl0TransportReceipt(TypedDict):
    schema_version: int
    requested: bool
    fifo_path: str
    fifo_created_before_child: bool
    stale_fifo_removed: bool
    fifo_cleaned: bool
    child_pid: int | None
    child_returncode: int | None
    cancelled: bool
    commands: list[SiCl0CommandRecord]


@dataclass(frozen=True, slots=True)
class SafetyIslandTopologyContractError(Exception):
    detail: str

    def __str__(self) -> str:
        return self.detail


@dataclass(frozen=True, slots=True)
class SiCl0CommandValidationError(Exception):
    detail: str

    def __str__(self) -> str:
        return self.detail


@dataclass(frozen=True, slots=True)
class SiCl0TransportSignal(Exception):
    signum: int


def has_unexpected_shadowed_range(platform_log: str) -> bool:
    for line in platform_log.splitlines():
        lowered = line.lower()
        if "shadowed" not in lowered:
            continue
        return True
    return False


def expected_ap_cpus() -> int:
    value = os.environ.get("QBOX_APOLLO_NUM_CPUS", "").strip()
    if not value:
        return DEFAULT_EXPECTED_AP_CPUS
    try:
        parsed = int(value, 0)
    except ValueError:
        return DEFAULT_EXPECTED_AP_CPUS
    if parsed < 1 or parsed > 16:
        return DEFAULT_EXPECTED_AP_CPUS
    return parsed


def platform_observations(out_dir: Path) -> dict[str, Any]:
    platform_log = read_log(out_dir / CONSOLE_LOGS["platform"])
    ap_cpu_match = AP_CPU_COUNT_RE.search(platform_log)
    ap_cpus = int(ap_cpu_match.group("count")) if ap_cpu_match else None
    expected = expected_ap_cpus()
    return {
        "ap_cpus": ap_cpus,
        "expected_ap_cpus": expected,
        "ap_cpus_enabled_for_full_system": ap_cpus == expected,
        "unexpected_shadowed_range": has_unexpected_shadowed_range(platform_log),
    }


def secure_console_observations(out_dir: Path) -> dict[str, Any]:
    secure_log = read_log(out_dir / CONSOLE_LOGS["secure_console"])
    return {
        "ap_bl2_console": "NOTICE:  BL2:" in secure_log,
        "bl31_console": "NOTICE:  BL31:" in secure_log,
        "optee_console": "OP-TEE version:" in secure_log,
        "rse_comms_mhu_init_failed": (
            "[RSE-COMMS] Host to RSE MHU driver initialization failed" in secure_log
        ),
        "mhu_wrapper_assert": (
            "ASSERT: drivers/arm/mhu/mhu_wrapper_v3_x.c:" in secure_log
        ),
    }


def primary_console_observations(
    out_dir: Path,
    login_prompt: str,
    shell_marker: str,
) -> dict[str, Any]:
    primary_log = read_log(out_dir / CONSOLE_LOGS["primary_console"])
    return {
        "u_boot_console": "U-Boot " in primary_log,
        "linux_kernel_console": (
            "Booting Linux on physical CPU" in primary_log
            or "Linux version " in primary_log
        ),
        "login_prompt": login_prompt in primary_log,
        "root_shell": shell_marker in primary_log,
    }


def workspace_root() -> Path:
    return Path(__file__).resolve().parents[2]


def timestamp() -> str:
    return _dt.datetime.now().strftime("%Y%m%d-%H%M%S")


def selected_si_topology_mode(
    args: argparse.Namespace,
) -> SafetyIslandTopologyMode:
    return "single" if args.si_single_gic else "split"


def decode_si_topology_contract(payload: str) -> SafetyIslandTopologyJson:
    try:
        decoded = json.loads(payload)
        mode = decoded["mode"]
        if mode not in ("single", "split"):
            raise SafetyIslandTopologyContractError(
                f"unsupported Safety Island topology mode: {mode!r}"
            )
        return {
            "env_var": decoded["env_var"],
            "mode": mode,
            "enabled": decoded["enabled"],
            "qemu_instances": decoded["qemu_instances"],
            "pes": decoded["pes"],
            "gics": decoded["gics"],
            "reset_targets": decoded["reset_targets"],
            "trace_targets": decoded["trace_targets"],
            "rollback_command": decoded["rollback_command"],
        }
    except (json.JSONDecodeError, KeyError, TypeError) as error:
        raise SafetyIslandTopologyContractError(
            f"invalid Safety Island topology contract: {error}"
        ) from error


def load_si_topology_contract(
    args: argparse.Namespace,
) -> SafetyIslandTopologyJson:
    topology = args.conf.parent / "hw-block/topology.lua"
    env = os.environ.copy()
    env["QBOX_APOLLO_TOPOLOGY_PATH"] = str(topology)
    env["QBOX_APOLLO_FULL_SI_SINGLE_GIC"] = (
        "true" if args.si_single_gic else "false"
    )
    command = ["lua", "-e", SI_TOPOLOGY_DRY_RUN_SCRIPT]
    print("+ lua -e <si-topology-contract>", flush=True)
    completed = subprocess.run(
        command,
        cwd=workspace_root(),
        env=env,
        check=False,
        capture_output=True,
        text=True,
    )
    if completed.returncode != 0:
        detail = completed.stderr.strip() or f"lua exited {completed.returncode}"
        raise SafetyIslandTopologyContractError(detail)
    contract = decode_si_topology_contract(completed.stdout)
    selected = selected_si_topology_mode(args)
    if contract["mode"] != selected:
        raise SafetyIslandTopologyContractError(
            f"selected topology {selected} produced {contract['mode']}"
        )
    return contract


def si_topology_result_fields(
    args: argparse.Namespace,
    contract: SafetyIslandTopologyJson,
) -> SafetyIslandResultFields:
    topology_source = args.conf.parent / "hw-block/topology.lua"
    topology_source_sha256 = (
        hashlib.sha256(topology_source.read_bytes()).hexdigest()
        if topology_source.is_file()
        else ""
    )
    contract_payload = json.dumps(
        contract,
        sort_keys=True,
        separators=(",", ":"),
    ).encode()
    return {
        "safety_island_gic_topology": contract,
        "si_gic_topology_mode": contract["mode"],
        "si_qemu_instance_count": len(contract["qemu_instances"]),
        "si_pe_map": contract["pes"],
        "si_reset_fanout": contract["reset_targets"],
        "si_trace_targets": contract["trace_targets"],
        "si_rollback_command": contract["rollback_command"],
        "si_topology_source": str(topology_source.resolve()),
        "si_topology_source_sha256": topology_source_sha256,
        "si_topology_contract_sha256": hashlib.sha256(
            contract_payload
        ).hexdigest(),
        "runner_source_sha256": hashlib.sha256(
            Path(__file__).resolve().read_bytes()
        ).hexdigest(),
    }


def run_si_topology_dry_run(args: argparse.Namespace) -> int:
    artifacts = resolved_artifacts(args)
    command = child_command(args, artifacts)
    platform_params = full_system_platform_params(args)
    topology = args.si_topology_contract
    status = {
        "schema_version": 1,
        "passed": True,
        "verdict": "automated-contract-only",
        "dry_run": True,
        "automated_contract_only": True,
        "boot_mode": "apollo-full-system",
        "safety_island_topology": "full-system",
        **si_topology_result_fields(args, topology),
        "child_command": command,
        "command": command,
        "child_environment": si_topology_child_environment(args),
        "platform_params": platform_params,
        "runner_argv": sys.argv,
    }
    args.out_dir.mkdir(parents=True, exist_ok=True)
    (args.out_dir / "result.json").write_text(
        json.dumps(status, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    (args.out_dir / "summary.txt").write_text(
        "\n".join(
            [
                "passed: True",
                "verdict: automated-contract-only",
                f"si_gic_topology_mode: {topology['mode']}",
                f"si_qemu_instance_count: {len(topology['qemu_instances'])}",
                "si_pe_map: " + json.dumps(topology["pes"], sort_keys=True),
                "si_reset_fanout: "
                + json.dumps(topology["reset_targets"], sort_keys=True),
                f"si_rollback_command: {topology['rollback_command']}",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    print(args.out_dir)
    return 0


def write_si_topology_contract_failure(
    args: argparse.Namespace,
    error: SafetyIslandTopologyContractError,
) -> int:
    mode = selected_si_topology_mode(args)
    rollback = (
        "python3 scripts/run/run_qbox_apollo_fvp_full.py --si-split-gic"
    )
    unavailable: SafetyIslandTopologyJson = {
        "env_var": "QBOX_APOLLO_FULL_SI_SINGLE_GIC",
        "mode": mode,
        "enabled": mode == "single",
        "qemu_instances": [],
        "pes": [],
        "gics": [],
        "reset_targets": [],
        "trace_targets": [],
        "rollback_command": rollback,
    }
    status = {
        "schema_version": 1,
        "passed": False,
        "verdict": "blocked",
        "dry_run": bool(args.dry_run),
        "boot_mode": "apollo-full-system",
        "safety_island_topology": "full-system",
        **si_topology_result_fields(args, unavailable),
        "blocker": "si_topology_contract_invalid",
        "detail": str(error),
        "runner_argv": sys.argv,
    }
    args.out_dir.mkdir(parents=True, exist_ok=True)
    (args.out_dir / "result.json").write_text(
        json.dumps(status, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    (args.out_dir / "summary.txt").write_text(
        "\n".join(
            [
                "passed: False",
                "verdict: blocked",
                f"si_gic_topology_mode: {mode}",
                "si_qemu_instance_count: 0",
                f"si_rollback_command: {rollback}",
                "blocker: si_topology_contract_invalid",
                f"detail: {error}",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    print(args.out_dir)
    return 1


def artifact_record(path: Path) -> dict[str, Any]:
    exists = path.exists()
    return {
        "path": str(path.resolve()),
        "exists": exists,
        "size": path.stat().st_size if exists and path.is_file() else None,
    }


def read_json(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return data if isinstance(data, dict) else {}


def timer_probe_evidence(args: argparse.Namespace) -> dict[str, Any]:
    path = args.out_dir / "timer-snapshot.json"
    snapshot = read_json(path)
    source = snapshot.get("source")
    run_id_matches = isinstance(source, dict) and source.get("run_id") == args.timer_probe_run_id
    if snapshot.get("schema_version") == 1 and snapshot.get("status") == "pass" and run_id_matches:
        return {
            "requested": True,
            "strict_gate": True,
            "status": snapshot["status"],
            "path": str(path.resolve()),
            "producer": "model-side",
        }
    reason = "model_side_timer_snapshot_missing_or_nonpass"
    if snapshot.get("schema_version") == 1 and not run_id_matches:
        reason = "model_side_timer_snapshot_run_id_mismatch"
    unavailable = {
        "schema_version": 1,
        "producer": "qbox",
        "status": "unavailable",
        "captured_at": _dt.datetime.now(_dt.timezone.utc).isoformat(),
        "source": {
            "machine": "apollo-qvp",
            "artifact_path": str(path.resolve()),
            "run_id": args.timer_probe_run_id,
        },
        "samples": [],
        "reason": reason,
    }
    args.out_dir.mkdir(parents=True, exist_ok=True)
    status_path = args.out_dir / "timer-probe-status.json"
    status_path.write_text(json.dumps(unavailable, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return {
        "requested": True,
        "strict_gate": True,
        "status": "unavailable",
        "path": str(path.resolve()),
        "producer": "model-side",
        "reason": reason,
    }


def read_log(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return ""


def clean_console_text(text: str) -> str:
    return re.sub(r"\x1b\[[0-?]*[ -/]*[@-~]", "", text).replace("\r", "")


def keep_running_child_logs(out_dir: Path) -> dict[str, str]:
    return {
        role: runtime_engine.read_required_pass_marker_file(out_dir / filename)
        for role, filename in CHILD_LOG_ALIASES.items()
    }


def keep_running_probe_state(
    primary_console: str,
    login_prompt: str,
    *,
    requested: bool,
) -> dict[str, Any]:
    clean_primary = clean_console_text(primary_console)
    evaluated = runtime_engine.evaluate_post_login_probe(primary_console)
    return {
        "requested": requested,
        "secure_service_requested": False,
        "fwu_requested": False,
        "sent_login": login_prompt in clean_primary,
        "sent_probe": "__QBOX_PROBE_START__" in clean_primary,
        "complete": bool(evaluated["done_marker"]),
        **evaluated,
    }


def keep_running_progress_marker_first_hits(
    logs: dict[str, str],
    login_prompt: str,
) -> dict[str, dict[str, Any]]:
    combined = clean_console_text("\n".join(logs.values()))
    return {
        name: {
            "elapsed_s": None,
            "marker": marker,
        }
        for name, _label, marker in keep_running_progress_markers(login_prompt)
        if marker in combined
    }


def keep_running_progress_markers(login_prompt: str) -> list[tuple[str, str, str]]:
    return [
        *KEEP_RUNNING_PROGRESS_MARKERS[:-1],
        ("primary_login_prompt", "Linux login prompt", login_prompt),
    ]


def keep_running_rse_boot_timing_profile(
    logs: dict[str, str],
    login_prompt: str,
) -> dict[str, Any]:
    first_hits = keep_running_progress_marker_first_hits(logs, login_prompt)
    markers = [
        {
            "name": name,
            "label": label,
            "marker": marker,
            "seen": name in first_hits,
            "elapsed_s": None,
        }
        for name, label, marker in keep_running_progress_markers(login_prompt)
    ]
    return {
        "markers": markers,
        "deltas": [],
        "slowest_delta": None,
        "summary": {
            "bl1_1_to_bl2_s": None,
            "bl2_to_rse_runtime_handoff_s": None,
            "rse_start_to_ap_power_on_s": None,
            "rse_start_to_linux_boot_s": None,
            "rse_start_to_login_prompt_s": None,
            "rse_start_to_runtime_handoff_s": None,
        },
    }


def synthesize_keep_running_child_status(
    args: argparse.Namespace,
    command: list[str],
    *,
    child_returncode: int | None,
) -> dict[str, Any]:
    logs = keep_running_child_logs(args.out_dir)
    combined = clean_console_text("\n".join(logs.values()))
    marker_groups = {
        group: {marker: marker in combined for marker in markers}
        for group, markers in CHILD_REQUIRED_MARKERS.items()
    }
    marker_groups["linux_boot"] = {
        args.primary_login_prompt: args.primary_login_prompt in combined,
        args.primary_shell_marker: args.primary_shell_marker in combined,
    }
    cl1_log = runtime_engine.read_required_pass_marker_file(
        args.out_dir / CONSOLE_LOGS["si_cl1"]
    )
    marker_groups["si_cl1"] = {
        marker: marker in cl1_log
        for marker in SI_CL1_REQUIRED_MARKERS.values()
    }
    cl0_log = runtime_engine.read_required_pass_marker_file(
        args.out_dir / CONSOLE_LOGS["si_cl0"]
    )
    marker_groups["si_cl0"] = {
        marker: marker in cl0_log
        for marker in SI_CL0_REQUIRED_MARKERS.values()
    }
    fail_hits = {pattern: pattern in combined for pattern in CHILD_FAIL_PATTERNS}
    fail_hits.update(
        {pattern: pattern in cl1_log for pattern in LIVE_CL1_FAIL_PATTERNS.values()}
    )
    probe = keep_running_probe_state(
        logs.get("primary_console", ""),
        args.primary_login_prompt,
        requested=bool(args.post_login_probe),
    )
    linux_hit = any(marker_groups["linux_boot"].values())
    non_linux_hit = all(
        hit
        for group, markers in marker_groups.items()
        if group != "linux_boot"
        for hit in markers.values()
    )
    probe_ready = bool(
        not args.post_login_probe
        or (
            probe.get("complete")
            and all(bool(value) for value in probe["driver_patterns"].values())
        )
    )
    passed = bool(
        non_linux_hit and linux_hit and probe_ready and not any(fail_hits.values())
    )
    rse_flash_state = read_json(
        args.out_dir / runtime_engine.RSE_FLASH_STATE_STATUS_FILE
    )
    return {
        "passed": passed,
        "blocker": None,
        "marker_hits": marker_groups,
        "fail_patterns": fail_hits,
        "log_bytes": sum(
            len(text.encode("utf-8", errors="replace")) for text in logs.values()
        ),
        "post_login_probe": probe,
        "scp_service_model": {
            "strategy": "real-si-scp",
            "live_scp_cpu_gdb": True,
        },
        "runtime_artifacts": {},
        "rse_flash_state": rse_flash_state
        or {"enabled": False, "action": "ephemeral"},
        "progress_marker_first_hits": keep_running_progress_marker_first_hits(
            logs,
            args.primary_login_prompt,
        ),
        "rse_boot_timing_profile": keep_running_rse_boot_timing_profile(
            logs,
            args.primary_login_prompt,
        ),
        "cc3xx_stats": None,
        "qbox_perf_profile": None,
        "platform_returncode": child_returncode,
        "command": command,
        "child_environment": si_topology_child_environment(args),
        **si_topology_result_fields(args, args.si_topology_contract),
    }


def write_keep_running_child_result(
    args: argparse.Namespace,
    command: list[str],
    *,
    child_returncode: int | None,
    blocker: str | None = None,
) -> dict[str, Any]:
    status = synthesize_keep_running_child_status(
        args,
        command,
        child_returncode=child_returncode,
    )
    if blocker:
        status["passed"] = False
        status["blocker"] = blocker
    (args.out_dir / "result.json").write_text(
        json.dumps(status, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return status


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def default_artifacts(local_build_dir: Path) -> dict[str, Path]:
    local_name = local_build_dir.name
    machine = (
        local_name.removeprefix("local-")
        if local_name.startswith("local-")
        else "apollo-qvp"
    )
    machine_work = machine.replace("-", "_")
    deploy = local_build_dir / "deploy"
    boot = deploy / "boot"
    firmware = deploy / "firmware"
    return {
        "rse_rom": firmware / "rse-rom-image.img",
        "rse_flash": firmware / "rse-flash-image.img",
        "rse_otp": firmware / "rse-otp-image.img",
        "ap_flash": firmware / "ap-flash-image.img",
        "fip": firmware / "fip.bin",
        "signed_ap_bl2": local_build_dir / "work/signing/deploy/signed_bl2.bin",
        "init_fwu_metadata": firmware / "init_fwu_metadata.bin",
        "ap_bl2_elf": (
            local_build_dir
            / f"work/trusted-firmware-a/{machine_work}/debug/bl2/bl2.elf"
        ),
        "rse_bl1_2_elf": local_build_dir / "work/trusted-firmware-m/bin/bl1_2.elf",
        "rse_bl2_elf": local_build_dir / "work/trusted-firmware-m/bin/bl2.elf",
        "rootfs": boot / f"{machine}-local-disk.img",
        "efi_capsule_disk": boot / "boot-fat.img",
        "provisioning_bundle": firmware / "combined_provisioning_message.bin",
        "ap_dtb": boot / f"{machine}.dtb",
        "rse_symbols": local_build_dir / "debug/symbols.json",
        "si_cl0_image": firmware / "si0_ramfw.bin",
        "si_cl1_image": firmware / "zephyr-demos-cl1.bin",
        "si_cl1_symbols": firmware / "zephyr-demos-cl1.elf",
    }


def resolved_artifacts(args: argparse.Namespace) -> dict[str, Path]:
    artifacts = default_artifacts(args.local_build_dir)
    overrides = {
        "rse_rom": args.rse_rom,
        "rse_flash": args.rse_flash,
        "rse_otp": args.rse_otp,
        "ap_flash": args.ap_flash,
        "ap_bl2_elf": args.ap_bl2_elf,
        "rse_bl1_2_elf": args.rse_bl1_2_elf,
        "rse_bl2_elf": args.rse_bl2_elf,
        "rootfs": args.rootfs,
        "efi_capsule_disk": args.efi_capsule_disk,
        "provisioning_bundle": args.provisioning_bundle,
        "ap_dtb": args.ap_dtb,
        "rse_symbols": args.rse_symbols,
        "si_cl0_image": args.si_cl0_image,
        "si_cl1_image": args.si_cl1_image,
        "si_cl1_symbols": args.si_cl1_symbols,
    }
    for name, value in overrides.items():
        if value is not None:
            artifacts[name] = value
    return {name: path.resolve() for name, path in artifacts.items()}


def missing_required(args: argparse.Namespace, artifacts: dict[str, Path]) -> list[str]:
    required = [
        "rse_rom",
        "rse_flash",
        "rse_otp",
        "ap_flash",
        "ap_bl2_elf",
        "rse_bl1_2_elf",
        "rse_bl2_elf",
        "rootfs",
        "efi_capsule_disk",
        "provisioning_bundle",
        "ap_dtb",
        "rse_symbols",
        "si_cl0_image",
        "si_cl1_image",
        "si_cl1_symbols",
    ]
    missing = [
        f"missing_artifact:{name}:{artifacts[name]}"
        for name in required
        if not artifacts[name].exists()
    ]
    if not args.conf.exists():
        missing.append(f"missing_artifact:conf:{args.conf}")
    return missing


def parse_int_auto(value: str) -> int | None:
    try:
        return int(value, 0)
    except ValueError:
        return None


def is_blank_file(path: Path) -> bool:
    with path.open("rb") as handle:
        while True:
            chunk = handle.read(1024 * 1024)
            if not chunk:
                return True
            if any(chunk):
                return False


def platform_param_value(args: argparse.Namespace, key: str) -> str | None:
    prefix = key + "="
    for param in args.platform_param:
        if param.startswith(prefix):
            return param.split("=", 1)[1].strip()
    return None


def rse_lcm_uses_se_fast_path(args: argparse.Namespace) -> bool:
    lcs = platform_param_value(args, "platform.rse_lcm_regs.lcs")
    if lcs is None:
        lcs = os.environ.get("QBOX_RDASPEN_RSE_LCM_LCS", "").strip()
    if not lcs:
        return True
    value = parse_int_auto(lcs)
    return value is None or value == RSE_LCS_SE


def ensure_default_debug_manifest(
    args: argparse.Namespace,
    artifacts: dict[str, Path],
) -> str | None:
    if args.rse_symbols is not None:
        return None
    symbol_path = artifacts["rse_symbols"]
    if symbol_path.exists():
        return None
    default_symbol_path = default_artifacts(args.local_build_dir)["rse_symbols"].resolve()
    if symbol_path != default_symbol_path:
        return None

    setup_script = workspace_root() / "scripts/setup/setup_local_debug_env.py"
    if not setup_script.exists():
        return f"missing_artifact:rse_symbols:{symbol_path}"

    args.out_dir.mkdir(parents=True, exist_ok=True)
    log_path = args.out_dir / "debug-manifest-generate.log"
    cmd = [
        sys.executable,
        str(setup_script),
        "--local-build-dir",
        str(args.local_build_dir),
        "--out-dir",
        str(symbol_path.parent),
    ]
    proc = subprocess.run(
        cmd,
        cwd=workspace_root(),
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    log_path.write_text(
        "+ " + " ".join(cmd) + "\n" + proc.stdout,
        encoding="utf-8",
    )
    if proc.returncode:
        return f"debug_manifest_generation_failed:{proc.returncode}:{log_path}"
    if not symbol_path.exists():
        return f"missing_artifact:rse_symbols:{symbol_path}"
    return None


def should_auto_provision_rse_otp(
    args: argparse.Namespace,
    artifacts: dict[str, Path],
) -> tuple[bool, str]:
    if not args.auto_provision_rse_otp:
        return False, "disabled"
    if args.check_only or args.build_only:
        return False, "non_runtime_mode"
    if args.rse_otp is not None:
        return False, "explicit_rse_otp"
    if args.no_copy_writable_flash:
        return False, "no_copy_writable_flash"
    if not rse_lcm_uses_se_fast_path(args):
        return False, "non_se_lifecycle"
    otp = artifacts["rse_otp"]
    if not otp.exists():
        return False, "missing_rse_otp"
    if not is_blank_file(otp):
        return False, "already_provisioned"
    return True, "blank_default_rse_otp"


def clone_args(args: argparse.Namespace) -> argparse.Namespace:
    values = vars(args).copy()
    values["platform_param"] = list(args.platform_param)
    return argparse.Namespace(**values)


def make_rse_otp_provision_args(args: argparse.Namespace) -> argparse.Namespace:
    provision_args = clone_args(args)
    provision_args.out_dir = args.out_dir / "rse-otp-provisioning-pass"
    provision_args.post_login_probe = False
    provision_args.keep_running_after_pass = False
    provision_args.live_trace = False
    provision_args.timeout = args.rse_otp_provision_timeout
    provision_args.provision_blank_rse_otp = True
    if platform_param_value(provision_args, "platform.rse_lcm_regs.lcs") is None:
        provision_args.platform_param.append(f"platform.rse_lcm_regs.lcs={RSE_LCS_CM}")
    return provision_args


def persist_provisioned_rse_otp(
    artifacts: dict[str, Path],
    child_status: dict[str, Any] | None,
) -> tuple[bool, str | None]:
    runtime_path = (child_status or {}).get("runtime_artifacts", {}).get("rse_otp")
    if not runtime_path:
        return False, "missing_runtime_rse_otp"
    runtime_otp = Path(str(runtime_path))
    if not runtime_otp.exists():
        return False, f"missing_runtime_rse_otp:{runtime_otp}"
    if is_blank_file(runtime_otp):
        return False, f"blank_runtime_rse_otp:{runtime_otp}"

    deploy_otp = artifacts["rse_otp"]
    deploy_otp.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(runtime_otp, deploy_otp)
    return True, str(runtime_otp.resolve())


def auto_provision_rse_otp(
    args: argparse.Namespace,
    artifacts: dict[str, Path],
) -> str | None:
    requested, reason = should_auto_provision_rse_otp(args, artifacts)
    status: dict[str, Any] = {
        "enabled": args.auto_provision_rse_otp,
        "requested": requested,
        "reason": reason,
    }
    args.rse_otp_auto_provision = status
    if not requested:
        return None

    provision_args = make_rse_otp_provision_args(args)
    status.update(
        {
            "out_dir": str(provision_args.out_dir.resolve()),
            "lcs": RSE_LCS_CM,
            "timeout": provision_args.timeout,
        }
    )
    child_rc, command = run_child(provision_args, artifacts)
    child_result = provision_args.out_dir / "result.json"
    child_status = read_json(child_result)
    status.update(
        {
            "child_returncode": child_rc,
            "child_result": str(child_result.resolve()),
            "child_passed": bool(child_status.get("passed")) if child_status else False,
            "child_blocker": child_status.get("blocker") if child_status else None,
            "command": command,
        }
    )

    persisted, detail = persist_provisioned_rse_otp(artifacts, child_status)
    status["persisted"] = persisted
    if persisted:
        status["runtime_rse_otp"] = detail
        status["deploy_rse_otp"] = str(artifacts["rse_otp"].resolve())
        return None

    status["error"] = detail
    return "rse_otp_auto_provision_failed:" + str(detail)


def gate_status(
    *,
    args: argparse.Namespace,
    child_status: dict[str, Any] | None,
    blocker: str | None,
    check_only: bool,
) -> dict[str, str]:
    gates = {gate: "not_run" for gate in GATES}
    if args.uboot_only:
        gates["G0"] = "pass" if not blocker else "blocked"
        return gates
    if blocker:
        if blocker.startswith("missing_artifact"):
            gates["G0"] = "fail"
            return gates
        gates["G0"] = "pass"
        if args.post_login_probe:
            probe = post_login_probe(child_status)
            gates["G1"] = "pass" if probe.get("passed") else "blocked"
        gates["G2"] = "blocked"
        return gates

    gates["G0"] = "pass"
    if check_only or args.build_only:
        return gates

    child_passed = bool(child_status and child_status.get("passed"))
    child_blocker = None
    if child_status:
        child_blocker = child_status.get("blocker")
    if args.post_login_probe:
        probe = post_login_probe(child_status)
        gates["G1"] = "pass" if probe.get("passed") else (
            "blocked" if child_blocker else "fail"
        )

    gates["G2"] = "pass" if child_passed else ("blocked" if child_blocker else "fail")
    return gates


def all_hits(markers: Any) -> bool:
    return isinstance(markers, dict) and bool(markers) and all(
        bool(value) for value in markers.values()
    )


def child_marker_hits(child_status: dict[str, Any] | None) -> dict[str, dict[str, bool]]:
    marker_hits = (child_status or {}).get("marker_hits", {})
    if not isinstance(marker_hits, dict):
        return {}
    normalized: dict[str, dict[str, bool]] = {}
    for group, hits in marker_hits.items():
        if isinstance(group, str) and isinstance(hits, dict):
            normalized[group] = {str(name): bool(value) for name, value in hits.items()}
    return normalized


def post_login_probe(child_status: dict[str, Any] | None) -> dict[str, Any]:
    probe = (child_status or {}).get("post_login_probe")
    if not isinstance(probe, dict):
        return {}
    normalized = dict(probe)
    if not normalized.get("requested"):
        return {}
    if "passed" not in normalized:
        driver_patterns = normalized.get("driver_patterns")
        drivers_passed = bool(
            isinstance(driver_patterns, dict)
            and driver_patterns
            and all(bool(value) for value in driver_patterns.values())
        )
        normalized["passed"] = bool(
            normalized.get("requested")
            and normalized.get("sent_probe")
            and normalized.get("complete")
            and drivers_passed
        )
    return normalized


def child_rse_boot_timing_profile(
    child_status: dict[str, Any] | None,
) -> dict[str, Any]:
    profile = (child_status or {}).get("rse_boot_timing_profile")
    if isinstance(profile, dict):
        return profile

    first_hits = (child_status or {}).get("progress_marker_first_hits")
    if not isinstance(first_hits, dict):
        return {}
    markers = []
    for name, hit in sorted(
        first_hits.items(),
        key=lambda item: float(item[1].get("elapsed_s", 0.0))
        if isinstance(item[1], dict)
        else 0.0,
    ):
        if not isinstance(hit, dict):
            continue
        markers.append(
            {
                "name": str(name),
                "marker": hit.get("marker"),
                "seen": True,
                "elapsed_s": hit.get("elapsed_s"),
            }
        )
    return {"markers": markers, "deltas": [], "slowest_delta": None, "summary": {}}


def child_runtime_evidence(
    child_status: dict[str, Any] | None,
) -> dict[str, Any]:
    status = child_status or {}
    return {
        "runtime_elapsed_s": status.get("runtime_elapsed_s"),
        "progress_marker_first_hits": status.get("progress_marker_first_hits"),
    }


def marker_from_child(
    markers: dict[str, dict[str, bool]],
    group: str,
    marker: str,
) -> bool:
    return bool(markers.get(group, {}).get(marker))


def build_marker_groups(
    args: argparse.Namespace,
    child_status: dict[str, Any] | None,
) -> dict[str, dict[str, bool]]:
    groups = child_marker_hits(child_status)
    measured_boot = groups.get("measured_boot", {})
    linux_boot = groups.get("linux_boot", {})
    rse_scp = groups.get("rse_scp_handoff", {})
    probe = post_login_probe(child_status)
    platform_obs = platform_observations(args.out_dir)
    secure_obs = secure_console_observations(args.out_dir)
    primary_obs = primary_console_observations(
        args.out_dir,
        args.primary_login_prompt,
        args.primary_shell_marker,
    )
    cl1_log = runtime_engine.read_required_pass_marker_file(
        args.out_dir / CONSOLE_LOGS["si_cl1"]
    )

    groups["rse"] = {
        "tfm_bl1_1": marker_from_child(groups, "rse_boot", "Starting TF-M BL1_1"),
        "first_image_slot": marker_from_child(
            groups, "rse_boot", "Jumping to the first image slot"
        ),
        "scmi_handoff": all_hits(rse_scp),
    }
    groups["ap_firmware"] = {
        "ap_cpus_enabled": bool(platform_obs["ap_cpus_enabled_for_full_system"]),
        "ap_bl2": bool(measured_boot.get("AP_BL2") and secure_obs["ap_bl2_console"]),
        "bl31": bool(measured_boot.get("SECURE_RT_EL3") and secure_obs["bl31_console"]),
        "optee": bool(
            measured_boot.get("SECURE_RT_EL1_SPMD") and secure_obs["optee_console"]
        ),
        "u_boot": bool(measured_boot.get("BL_33") and primary_obs["u_boot_console"]),
    }
    groups["linux"] = {
        "login_prompt": bool(linux_boot.get(args.primary_login_prompt)),
        "root_shell": bool(
            linux_boot.get(args.primary_shell_marker)
            or primary_obs["root_shell"]
            or probe.get("passed")
        ),
    }
    groups["post_login"] = {
        "probe": not args.post_login_probe or bool(probe.get("passed")),
    }
    if "linux_boot" in groups:
        groups["linux_boot"][args.primary_shell_marker] = groups["linux"][
            "root_shell"
        ]
    groups["maps_and_interrupts"] = {
        "no_unexpected_shadowed_ranges": not bool(platform_obs["unexpected_shadowed_range"]),
        "rse_scp_handoff": all_hits(rse_scp),
    }

    cl0_log = runtime_engine.read_required_pass_marker_file(
        args.out_dir / CONSOLE_LOGS["si_cl0"]
    )
    child_scp = (child_status or {}).get("scp_service_model", {})
    real_scp_cpu = (
        isinstance(child_scp, dict)
        and bool(child_scp.get("live_scp_cpu_gdb"))
        and child_scp.get("strategy") == "real-si-scp"
    )
    groups["si_cl0"] = {
        "scp_log_present": bool(cl0_log.strip()),
        **{
            name: marker in cl0_log
            for name, marker in SI_CL0_REQUIRED_MARKERS.items()
        },
        "real_scp_strategy_recorded": real_scp_cpu,
    }
    groups["si_cl1"] = {
        name: marker in cl1_log
        for name, marker in SI_CL1_REQUIRED_MARKERS.items()
    }

    return groups


def missing_markers(markers: dict[str, bool]) -> list[str]:
    return [name for name, value in markers.items() if not value]


def si_error_hits(args: argparse.Namespace) -> dict[str, bool]:
    out_dir = getattr(args, "out_dir", None)
    if out_dir is None:
        return {name: False for name in LIVE_CL1_FAIL_PATTERNS}
    cl1_log = runtime_engine.read_required_pass_marker_file(
        Path(out_dir) / CONSOLE_LOGS["si_cl1"]
    )
    return {
        name: pattern in cl1_log
        for name, pattern in LIVE_CL1_FAIL_PATTERNS.items()
    }


def si_gate_blocker(
    args: argparse.Namespace,
    marker_groups: dict[str, dict[str, bool]],
    child_status: dict[str, Any] | None,
) -> str | None:
    if child_status and not child_status.get("passed"):
        child_blocker = child_status.get("blocker")
        if child_blocker:
            return str(child_blocker)
    error_hits = [
        name for name, hit in si_error_hits(args).items() if hit
    ]
    if error_hits:
        return "si_error:" + ",".join(error_hits)
    map_missing = missing_markers(marker_groups.get("maps_and_interrupts", {}))
    if map_missing:
        return "si_map_blocked:" + ",".join(map_missing)
    cl0_missing = missing_markers(marker_groups.get("si_cl0", {}))
    if cl0_missing:
        return "si_marker_blocked:" + ",".join(cl0_missing)
    cl1_missing = missing_markers(marker_groups.get("si_cl1", {}))
    if cl1_missing:
        return "si_marker_blocked:" + ",".join(cl1_missing)
    return None


def write_result(
    args: argparse.Namespace,
    artifacts: dict[str, Path],
    *,
    command: list[str],
    child_status: dict[str, Any] | None,
    child_returncode: int | None,
    blocker: str | None,
    check_only: bool,
) -> int:
    args.out_dir.mkdir(parents=True, exist_ok=True)
    timer_probe = timer_probe_evidence(args) if args.timer_probe else {"requested": False}
    if args.timer_probe and timer_probe["status"] != "pass" and not blocker:
        blocker = "timer_probe_unavailable"
    input_artifacts = {"conf": artifact_record(args.conf)}
    input_artifacts.update(
        {name: artifact_record(path) for name, path in sorted(artifacts.items())}
    )
    marker_groups = build_marker_groups(args, child_status)
    si_errors = si_error_hits(args)
    platform_obs = platform_observations(args.out_dir)
    secure_obs = secure_console_observations(args.out_dir)
    primary_obs = primary_console_observations(
        args.out_dir,
        args.primary_login_prompt,
        args.primary_shell_marker,
    )
    gate_blocker = None
    if not check_only and not args.build_only and not args.uboot_only:
        gate_blocker = si_gate_blocker(args, marker_groups, child_status)
    if not blocker and gate_blocker:
        blocker = gate_blocker
    gates = gate_status(
        args=args,
        child_status=child_status,
        blocker=blocker,
        check_only=check_only,
    )
    passed = bool(
        not blocker and (check_only or args.build_only or (child_status or {}).get("passed"))
    )
    if (check_only or args.build_only) and not blocker:
        passed = True
    if blocker:
        passed = False

    console_logs = {
        name: str((args.out_dir / filename).resolve())
        for name, filename in CONSOLE_LOGS.items()
    }
    mhu_trace_logs = {
        "ap_si": str((args.out_dir / "ap-si-mhuv3-trace.log").resolve()),
        "si_cl1": str((args.out_dir / "si-cl1-mhuv3-trace.log").resolve()),
    }
    qbox_performance_options = {
        "rse_hotpath_accel": bool(args.rse_hotpath_accel),
        "rse_bl2_libc_hotpath": bool(args.rse_bl2_libc_hotpath),
        "rse_lms_accel": bool(args.rse_lms_accel),
        "rse_bl2_load_accel": bool(args.rse_bl2_load_accel),
        "rse_bl2_boot_enc_accel": bool(args.rse_bl2_boot_enc_accel),
        "rse_bl2_img_hash_accel": bool(args.rse_bl2_img_hash_accel),
        "rse_bl2_verify_sig_accel": bool(args.rse_bl2_verify_sig_accel),
        "rse_bl2_delay_accel": bool(args.rse_bl2_delay_accel),
        "cc3xx_qemu_native_backend": bool(args.cc3xx_qemu_native_backend),
        "rse_fast_boot_aliases": bool(args.rse_fast_boot_aliases),
        "rse_fast_boot_sram_dmi": bool(args.rse_fast_boot_sram_dmi),
    }
    status: dict[str, Any] = {
        "passed": passed,
        "pass_mode": (child_status or {}).get("pass_mode"),
        "verdict": "pass" if passed else ("blocked" if blocker else "fail"),
        "boot_mode": "apollo-full-system",
        "validation_scope": "uboot-only" if args.uboot_only else "full-system",
        "safety_island_topology": "full-system",
        **si_topology_result_fields(args, args.si_topology_contract),
        "ap_tcg_mode": effective_platform_param(
            args,
            "platform.ap_qemu_inst.tcg_mode",
            "QBOX_APOLLO_FULL_AP_TCG_MODE",
            "MULTI",
        ).upper(),
        "si_cl0_tcg_mode": effective_platform_param(
            args,
            "platform.si_cl0_qemu_inst.tcg_mode",
            "QBOX_APOLLO_FULL_SI_CL0_TCG_MODE",
            "MULTI",
        ).upper(),
        "si_cl1_tcg_mode": effective_platform_param(
            args,
            "platform.si_cl1_qemu_inst.tcg_mode",
            "QBOX_APOLLO_FULL_SI_CL1_TCG_MODE",
            "MULTI",
        ).upper(),
        "si_cl1_sync_policy": effective_platform_param(
            args,
            "platform.si_cl1_qemu_inst.sync_policy",
            "QBOX_APOLLO_FULL_SI_CL1_SYNC_POLICY",
            "multithread-quantum",
        ),
        "smmu_backend": args.smmu_backend,
        "rse_flash_backend": args.rse_flash_backend,
        "mhu_backend": "systemc-mhu320ae",
        "qbox_conf": str(args.conf),
        "qbox_build_dir": str(args.qbox_build_dir),
        "qbox_executable": str((args.qbox_build_dir / "platforms-vp").resolve()),
        "qbox_performance_preset": args.qbox_performance_preset,
        "qbox_performance_options": qbox_performance_options,
        "rse_otp_auto_provision": getattr(
            args,
            "rse_otp_auto_provision",
            {"enabled": False, "requested": False},
        ),
        "range_limited_flash_dmi": args.range_limited_flash_dmi,
        "live_trace": args.live_trace,
        "timer_probe": timer_probe,
        "completion_gates": gates,
        "input_artifacts": input_artifacts,
        "runtime_artifacts": (child_status or {}).get("runtime_artifacts", {}),
        "rse_flash_state": (child_status or {}).get(
            "rse_flash_state", {"enabled": False, "action": "ephemeral"}
        ),
        "console_logs": console_logs,
        "mhu_trace_logs": mhu_trace_logs,
        "platform_stdout_log": console_logs["platform"],
        "platform_observations": platform_obs,
        "secure_console_observations": secure_obs,
        "primary_console_observations": primary_obs,
        "marker_groups": marker_groups,
        "si_error_hits": si_errors,
        "first_failing_marker": (
            None if check_only or args.build_only else first_failing_marker(marker_groups)
        ),
        "post_login_probe": post_login_probe(child_status),
        "rse_boot_timing_profile": child_rse_boot_timing_profile(child_status),
        **child_runtime_evidence(child_status),
        "cc3xx_stats": (child_status or {}).get("cc3xx_stats"),
        "qbox_perf_profile": (child_status or {}).get("qbox_perf_profile"),
        "completion_gate_blocker": gate_blocker,
        "child_scp_runtime": (child_status or {}).get("scp_service_model"),
        "blocker": blocker or (child_status or {}).get("blocker"),
        "child_result": str((args.out_dir / RD_ASPEN_CHILD_RESULT).resolve())
        if child_status
        else None,
        "child_status": child_status or {},
        "child_returncode": child_returncode,
        "command": command,
        "child_environment": si_topology_child_environment(args),
        "si_cl0_command_transport": getattr(
            args,
            "si_cl0_command_transport",
            {
                "schema_version": 1,
                "requested": bool(args.si_cl0_command),
                "fifo_path": str(si_cl0_uart_fifo_path(args)),
                "fifo_created_before_child": False,
                "stale_fifo_removed": False,
                "fifo_cleaned": True,
                "child_pid": None,
                "child_returncode": None,
                "cancelled": False,
                "commands": [],
            },
        ),
        "runner_argv": sys.argv,
    }

    result_path = args.out_dir / "result.json"
    summary_path = args.out_dir / "summary.txt"
    result_path.write_text(json.dumps(status, indent=2, sort_keys=True) + "\n")
    lines = [
        f"passed: {status['passed']}",
        f"verdict: {status['verdict']}",
        f"boot_mode: {status['boot_mode']}",
        f"validation_scope: {status['validation_scope']}",
        f"safety_island_topology: {status['safety_island_topology']}",
        f"si_gic_topology_mode: {status['si_gic_topology_mode']}",
        f"si_qemu_instance_count: {status['si_qemu_instance_count']}",
        "si_pe_map: " + json.dumps(status["si_pe_map"], sort_keys=True),
        "si_reset_fanout: "
        + json.dumps(status["si_reset_fanout"], sort_keys=True),
        f"si_rollback_command: {status['si_rollback_command']}",
        f"ap_tcg_mode: {status['ap_tcg_mode']}",
        f"si_cl0_tcg_mode: {status['si_cl0_tcg_mode']}",
        f"si_cl1_tcg_mode: {status['si_cl1_tcg_mode']}",
        f"si_cl1_sync_policy: {status['si_cl1_sync_policy']}",
        f"smmu_backend: {status['smmu_backend']}",
        f"mhu_backend: {status['mhu_backend']}",
        f"qbox_performance_preset: {status['qbox_performance_preset']}",
        "qbox_performance_options: "
        + json.dumps(status["qbox_performance_options"], sort_keys=True),
        "rse_otp_auto_provision: "
        + json.dumps(status["rse_otp_auto_provision"], sort_keys=True),
        "rse_flash_state: "
        + json.dumps(status["rse_flash_state"], sort_keys=True),
        f"range_limited_flash_dmi: {status['range_limited_flash_dmi']}",
        f"live_trace: {status['live_trace']}",
        f"blocker: {status['blocker'] or 'none'}",
        "rse_boot_timing_profile: "
        + json.dumps(status["rse_boot_timing_profile"], sort_keys=True),
        "completion_gates:",
        *[f"  - {gate}: {verdict}" for gate, verdict in gates.items()],
        f"qbox_conf: {args.conf}",
        f"qbox_build_dir: {args.qbox_build_dir}",
        f"qbox_executable: {(args.qbox_build_dir / 'platforms-vp').resolve()}",
        "input_artifacts:",
        *[
            f"  - {name}: {record['path']} exists={record['exists']} size={record['size']}"
            for name, record in input_artifacts.items()
        ],
        "console_logs:",
        *[f"  - {name}: {path}" for name, path in console_logs.items()],
    ]
    summary_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(args.out_dir)
    print(summary_path)
    print(result_path)
    return 0 if passed else 1


def first_failing_marker(marker_groups: Any) -> str | None:
    if not isinstance(marker_groups, dict):
        return None
    ordered_groups = [
        group for group in MARKER_GROUP_PRIORITY if group in marker_groups
    ]
    ordered_groups.extend(
        group for group in marker_groups if group not in set(ordered_groups)
    )
    for group in ordered_groups:
        hits = marker_groups.get(group)
        if not isinstance(hits, dict):
            continue
        for marker, hit in hits.items():
            if not hit:
                return f"{group}:{marker}"
    return None


def copy_child_logs(args: argparse.Namespace) -> None:
    aliases = {
        "qbox-platform.log": "qbox-platform.log",
        "qbox-rse.log": "qbox-rse.log",
        "qbox-secure-console.log": "qbox-secure-console.log",
        "qbox-primary-console.log": "qbox-primary-console.log",
    }
    for src_name, dst_name in aliases.items():
        src = args.out_dir / src_name
        dst = args.out_dir / dst_name
        if src.exists() and src != dst:
            shutil.copy2(src, dst)


def clear_run_outputs(out_dir: Path) -> None:
    stale_files = {
        "result.json",
        "summary.txt",
        RD_ASPEN_CHILD_RESULT,
        "rd-aspen-summary.txt",
        "comparison.json",
        "map-comparison.json",
        "coverage-audit.json",
        "final-verification.json",
        "ap-si-mhuv3-trace.log",
        "si-cl1-mhuv3-trace.log",
        "si-cl0-pc-trace.log",
        "post-login-probe-actions.log",
        runtime_engine.RSE_FLASH_STATE_STATUS_FILE,
    }
    stale_files.update(CONSOLE_LOGS.values())
    stale_files.add("qbox-scp.log")
    out_dir.mkdir(parents=True, exist_ok=True)
    for name in stale_files:
        path = out_dir / name
        try:
            path.unlink()
        except FileNotFoundError:
            pass


def write_blocker_logs(args: argparse.Namespace, blocker: str) -> None:
    for name, filename in CONSOLE_LOGS.items():
        write_text(
            args.out_dir / filename,
            "Apollo full-system QBox run did not start.\n"
            f"console: {name}\n"
            f"blocker: {blocker}\n",
        )


def wait_for_keep_running_child_pass(
    args: argparse.Namespace,
    proc: subprocess.Popen[bytes],
    command: list[str],
) -> int:
    start = time.monotonic()
    result_path = args.out_dir / "result.json"
    while True:
        child_status = read_json(result_path)
        if child_status.get("passed"):
            return 0

        synthesized = synthesize_keep_running_child_status(
            args,
            command,
            child_returncode=proc.poll(),
        )
        if synthesized.get("passed"):
            write_keep_running_child_result(
                args,
                command,
                child_returncode=proc.poll(),
            )
            return 0

        rc = proc.poll()
        if rc is not None:
            if not result_path.exists():
                write_keep_running_child_result(
                    args,
                    command,
                    child_returncode=rc,
                    blocker=f"child_failed:{rc}",
                )
            return rc

        if args.timeout > 0 and time.monotonic() - start >= args.timeout:
            proc.terminate()
            try:
                rc = proc.wait(timeout=10)
            except subprocess.TimeoutExpired:
                proc.kill()
                rc = proc.wait(timeout=10)
            write_keep_running_child_result(
                args,
                command,
                child_returncode=rc,
                blocker="child_keep_running_timeout",
            )
            return rc if rc else 1

        time.sleep(0.2)


def env_or_default(name: str, default: str) -> str:
    return os.environ.get(name) or default


def si_cl0_uart_fifo_path(args: argparse.Namespace) -> Path:
    return (args.out_dir / "si-cl0-uart-input.fifo").resolve()


def si_cl0_command_payload(command: str) -> bytes:
    if re.fullmatch(r"[\x20-\x7e]{1,512}", command) is None:
        raise SiCl0CommandValidationError(
            "SI0 commands must be 1-512 printable ASCII bytes without line breaks"
        )
    return b"\x05" + command.encode("ascii") + b"\n\x04"


def utc_timestamp() -> str:
    return _dt.datetime.now(_dt.UTC).isoformat()


def terminate_process_group(proc: subprocess.Popen[bytes]) -> int:
    returncode = proc.poll()
    if returncode is not None:
        return returncode
    try:
        os.killpg(proc.pid, signal.SIGTERM)
        return proc.wait(timeout=5)
    except subprocess.TimeoutExpired:
        os.killpg(proc.pid, signal.SIGKILL)
        return proc.wait(timeout=5)
    except ProcessLookupError:
        return proc.wait(timeout=5)


def write_si_cl0_command(
    args: argparse.Namespace,
    proc: subprocess.Popen[bytes],
    command: str,
) -> SiCl0CommandRecord:
    fifo_path = si_cl0_uart_fifo_path(args)
    timeout_seconds = args.si_cl0_command_timeout
    payload = si_cl0_command_payload(command)
    command_bytes = command.encode("ascii")
    record: SiCl0CommandRecord = {
        "command": command,
        "sha256": hashlib.sha256(command_bytes).hexdigest(),
        "raw_uart_sha256": hashlib.sha256(payload).hexdigest(),
        "started_at": utc_timestamp(),
        "done_at": None,
        "exit_at": None,
        "timed_out": False,
        "timeout_seconds": timeout_seconds,
        "transport_returncode": 1,
        "bytes_sent": 0,
    }
    deadline = time.monotonic() + timeout_seconds
    writer_fd: int | None = None
    while writer_fd is None:
        child_returncode = proc.poll()
        if child_returncode is not None:
            record["transport_returncode"] = 125
            return record
        try:
            writer_fd = os.open(fifo_path, os.O_WRONLY | os.O_NONBLOCK)
        except OSError as error:
            if error.errno != errno.ENXIO:
                raise
            if time.monotonic() >= deadline:
                record["timed_out"] = True
                record["transport_returncode"] = 124
                return record
            time.sleep(0.01)

    try:
        entered = os.write(writer_fd, b"\x05")
        command_sent = os.write(writer_fd, command_bytes + b"\n")
        record["done_at"] = utc_timestamp()
        exited = os.write(writer_fd, b"\x04")
        record["exit_at"] = utc_timestamp()
        record["bytes_sent"] = entered + command_sent + exited
        record["transport_returncode"] = 0
    except BlockingIOError:
        record["timed_out"] = time.monotonic() >= deadline
        record["transport_returncode"] = 124 if record["timed_out"] else 1
    finally:
        os.close(writer_fd)
    return record


def run_child_with_si_cl0_transport(
    args: argparse.Namespace,
    command: list[str],
    env: dict[str, str],
) -> int:
    for si_command in args.si_cl0_command:
        si_cl0_command_payload(si_command)

    fifo_path = si_cl0_uart_fifo_path(args)
    args.out_dir.mkdir(parents=True, exist_ok=True)
    stale_fifo_removed = False
    try:
        existing_mode = fifo_path.lstat().st_mode
    except FileNotFoundError:
        existing_mode = None
    if existing_mode is not None:
        if not stat.S_ISFIFO(existing_mode):
            raise SiCl0CommandValidationError(
                f"refusing to replace non-FIFO SI0 UART input: {fifo_path}"
            )
        fifo_path.unlink()
        stale_fifo_removed = True
    os.mkfifo(fifo_path, mode=0o600)
    receipt: SiCl0TransportReceipt = {
        "schema_version": 1,
        "requested": True,
        "fifo_path": str(fifo_path),
        "fifo_created_before_child": True,
        "stale_fifo_removed": stale_fifo_removed,
        "fifo_cleaned": False,
        "child_pid": None,
        "child_returncode": None,
        "cancelled": False,
        "commands": [],
    }
    args.si_cl0_command_transport = receipt
    child_env = env.copy()
    child_env["QBOX_APOLLO_FULL_SI_CL0_UART_READ_FILE"] = str(fifo_path)
    proc: subprocess.Popen[bytes] | None = None
    previous_sigterm = signal.getsignal(signal.SIGTERM)

    def handle_sigterm(signum: int, _frame: FrameType | None) -> None:
        raise SiCl0TransportSignal(signum)

    signal.signal(signal.SIGTERM, handle_sigterm)
    try:
        proc = subprocess.Popen(
            command,
            cwd=workspace_root(),
            env=child_env,
            start_new_session=True,
        )
        receipt["child_pid"] = proc.pid
        for si_command in args.si_cl0_command:
            command_record = write_si_cl0_command(
                args,
                proc,
                si_command,
            )
            receipt["commands"].append(command_record)
            if command_record["transport_returncode"] != 0:
                receipt["child_returncode"] = terminate_process_group(proc)
                return command_record["transport_returncode"]

        child_returncode = proc.wait()
        receipt["child_returncode"] = child_returncode
        return child_returncode
    except (KeyboardInterrupt, SiCl0TransportSignal):
        receipt["cancelled"] = True
        if proc is not None:
            receipt["child_returncode"] = terminate_process_group(proc)
        return 130
    finally:
        signal.signal(signal.SIGTERM, previous_sigterm)
        if proc is not None and proc.poll() is None:
            receipt["child_returncode"] = terminate_process_group(proc)
        fifo_path.unlink(missing_ok=True)
        receipt["fifo_cleaned"] = True


def si_topology_child_environment(
    args: argparse.Namespace,
) -> dict[str, str]:
    if args.si_single_gic:
        acceleration = env_or_default("QBOX_APOLLO_FULL_SI_ACCEL", "tcg")
        tcg_mode = effective_platform_param(
            args,
            "platform.si_qemu_inst.tcg_mode",
            "QBOX_APOLLO_FULL_SI_TCG_MODE",
            "MULTI",
        )
        sync_policy = effective_platform_param(
            args,
            "platform.si_qemu_inst.sync_policy",
            "QBOX_APOLLO_FULL_SI_SYNC_POLICY",
            "multithread-quantum",
        )
        environment: dict[str, str] = {
            "QBOX_APOLLO_FULL_SI_SINGLE_GIC": "true",
            "QBOX_APOLLO_FULL_SI_ACCEL": acceleration,
            "QBOX_APOLLO_FULL_SI_TCG_MODE": tcg_mode,
            "QBOX_APOLLO_FULL_SI_SYNC_POLICY": sync_policy,
            "QBOX_APOLLO_FULL_SI_CL0_ACCEL": acceleration,
            "QBOX_APOLLO_FULL_SI_CL0_TCG_MODE": tcg_mode,
            "QBOX_APOLLO_FULL_SI_CL0_SYNC_POLICY": sync_policy,
            "QBOX_APOLLO_FULL_SI_CL1_ACCEL": acceleration,
            "QBOX_APOLLO_FULL_SI_CL1_TCG_MODE": tcg_mode,
            "QBOX_APOLLO_FULL_SI_CL1_SYNC_POLICY": sync_policy,
        }
    else:
        environment = {"QBOX_APOLLO_FULL_SI_SINGLE_GIC": "false"}
    if args.si_cl0_command:
        environment["QBOX_APOLLO_FULL_SI_CL0_UART_READ_FILE"] = str(
            si_cl0_uart_fifo_path(args)
        )
    return environment


def full_system_platform_params(args: argparse.Namespace) -> list[str]:
    params = list(args.platform_param)
    explicit_keys = {param.partition("=")[0] for param in params}
    defaults = []
    si_defaults = (
        FULL_SYSTEM_SI_SINGLE_QEMU_DEFAULTS
        if args.si_single_gic
        else FULL_SYSTEM_SI_SPLIT_QEMU_DEFAULTS
    )
    for key, env_name, default in (
        *FULL_SYSTEM_AP_QEMU_DEFAULTS,
        *si_defaults,
    ):
        if args.build_only:
            continue
        if key not in explicit_keys:
            defaults.append(f"{key}={env_or_default(env_name, default)}")
    return defaults + params


def effective_platform_param(
    args: argparse.Namespace, key: str, env_name: str, default: str
) -> str:
    prefix = key + "="
    for param in reversed(args.platform_param):
        if param.startswith(prefix):
            return param[len(prefix) :]
    return env_or_default(env_name, default)


def child_command(args: argparse.Namespace, artifacts: dict[str, Path]) -> list[str]:
    root = workspace_root()
    cmd = [
        sys.executable,
        str(root / "scripts/run/run_qbox_apollo_fvp_full.py"),
        "--runtime-child",
        "--conf",
        str(args.conf),
        "--rse-rom",
        str(artifacts["rse_rom"]),
        "--rse-flash",
        str(artifacts["rse_flash"]),
        "--rse-otp",
        str(artifacts["rse_otp"]),
        "--ap-flash",
        str(artifacts["ap_flash"]),
        "--ap-bl2-elf",
        str(artifacts["ap_bl2_elf"]),
        "--rse-bl1-2-elf",
        str(artifacts["rse_bl1_2_elf"]),
        "--rse-bl2-elf",
        str(artifacts["rse_bl2_elf"]),
        "--rootfs",
        str(artifacts["rootfs"]),
        "--ap-dtb",
        str(artifacts["ap_dtb"]),
        "--efi-capsule-disk",
        str(artifacts["efi_capsule_disk"]),
        "--provisioning-bundle",
        str(artifacts["provisioning_bundle"]),
        "--out-dir",
        str(args.out_dir),
        "--timeout",
        str(args.timeout),
        "--jobs",
        str(args.jobs),
        "--qbox-build-dir",
        str(args.qbox_build_dir),
        "--scp-strategy",
        "real-si-scp",
        "--smmu-backend",
        args.smmu_backend,
        "--rootfs-bootargs-profile",
        args.rootfs_bootargs_profile,
        "--rootfs-maxcpus",
        str(expected_ap_cpus()),
        "--primary-login-prompt",
        args.primary_login_prompt,
        "--primary-shell-marker",
        args.primary_shell_marker,
        "--primary-shell-prompt-re",
        args.primary_shell_prompt_re,
    ]
    if args.skip_build:
        cmd.append("--skip-build")
    if args.rse_flash_state is not None:
        cmd.extend(["--rse-flash-state", str(args.rse_flash_state)])
    if args.reset_rse_flash_state:
        cmd.append("--reset-rse-flash-state")
    cmd.extend(["--rse-flash-backend", args.rse_flash_backend])
    if args.no_copy_writable_flash:
        cmd.append("--no-copy-writable-flash")
    if args.range_limited_flash_dmi:
        cmd.append("--range-limited-flash-dmi")
    else:
        cmd.append("--no-range-limited-flash-dmi")
    if args.cc3xx_stats:
        cmd.append("--cc3xx-stats")
        cmd.extend(["--cc3xx-stats-interval", str(args.cc3xx_stats_interval)])
    if args.qbox_perf_profile:
        cmd.append("--qbox-perf-profile")
        cmd.extend([
            "--qbox-perf-profile-interval",
            str(args.qbox_perf_profile_interval),
        ])
    if args.rse_hotpath_accel:
        cmd.append("--rse-hotpath-accel")
        cmd.extend(["--rse-hotpath-max-bytes", str(args.rse_hotpath_max_bytes)])
    if args.rse_hotpath_memcpy_addr is not None:
        cmd.extend(["--rse-hotpath-memcpy-addr", hex(args.rse_hotpath_memcpy_addr)])
    if args.rse_hotpath_memset_addr is not None:
        cmd.extend(["--rse-hotpath-memset-addr", hex(args.rse_hotpath_memset_addr)])
    if args.rse_bl2_libc_hotpath:
        cmd.append("--rse-bl2-libc-hotpath")
    if args.rse_lms_accel:
        cmd.append("--rse-lms-accel")
        cmd.extend(["--rse-lms-max-data-bytes", str(args.rse_lms_max_data_bytes)])
    if args.rse_lms_verify_addr is not None:
        cmd.extend(["--rse-lms-verify-addr", hex(args.rse_lms_verify_addr)])
    if args.rse_bl2_load_accel:
        cmd.append("--rse-bl2-load-accel")
        cmd.extend([
            "--rse-bl2-load-accel-max-bytes",
            str(args.rse_bl2_load_accel_max_bytes),
        ])
    if args.rse_bl2_boot_enc_accel:
        cmd.append("--rse-bl2-boot-enc-accel")
    if args.rse_bl2_img_hash_accel:
        cmd.append("--rse-bl2-img-hash-accel")
        cmd.extend([
            "--rse-bl2-img-hash-max-bytes",
            str(args.rse_bl2_img_hash_max_bytes),
            "--rse-bl2-img-hash-max-seed-bytes",
            str(args.rse_bl2_img_hash_max_seed_bytes),
        ])
    if args.rse_bl2_verify_sig_accel:
        cmd.append("--rse-bl2-verify-sig-accel")
        cmd.extend([
            "--rse-bl2-verify-sig-max-key-bytes",
            str(args.rse_bl2_verify_sig_max_key_bytes),
            "--rse-bl2-verify-sig-max-sig-bytes",
            str(args.rse_bl2_verify_sig_max_sig_bytes),
        ])
    if args.rse_bl2_verify_sig_skip:
        cmd.append("--rse-bl2-verify-sig-skip")
    if args.rse_bl2_delay_accel:
        cmd.append("--rse-bl2-delay-accel")
        cmd.extend([
            "--rse-bl2-delay-max-cycles",
            str(args.rse_bl2_delay_max_cycles),
            "--rse-bl2-delay-expected-hits",
            str(args.rse_bl2_delay_expected_hits),
        ])
    if args.cc3xx_status_read_fastpath:
        cmd.append("--cc3xx-status-read-fastpath")
    if args.cc3xx_qemu_native_backend:
        cmd.append("--cc3xx-qemu-native-backend")
    if args.cc3xx_local_mmio_fastpath:
        cmd.append("--cc3xx-local-mmio-fastpath")
    if args.rse_fast_boot_aliases:
        cmd.append("--rse-fast-boot-aliases")
    if args.rse_fast_boot_sram_dmi:
        cmd.append("--rse-fast-boot-sram-dmi")
    if getattr(args, "provision_blank_rse_otp", False):
        cmd.append("--allow-blank-rse-otp")
    if args.post_login_probe and not args.uboot_only:
        cmd.append("--post-login-probe")
    if args.primary_operation_manifest is not None and not args.uboot_only:
        cmd.extend([
            "--primary-operation-manifest",
            str(args.primary_operation_manifest),
            "--primary-operation-schema",
            str(args.primary_operation_schema),
            "--primary-operation-module-path",
            str(args.primary_operation_module_path),
        ])
    if not args.uboot_only:
        cl1_log = (args.out_dir / "qbox-safety-island-cl1.log").resolve()
        for marker in SI_CL1_REQUIRED_MARKERS.values():
            cmd.extend(["--required-pass-marker", str(cl1_log), marker])
    if args.keep_running_after_pass:
        cmd.append("--keep-running-after-pass")
    if args.build_only:
        cmd.append("--check-only")
    if args.host_gdb_script is not None:
        cmd.extend(["--host-gdb-script", str(args.host_gdb_script)])
    if args.ignore_fail_patterns:
        cmd.append("--ignore-fail-patterns")
    for param in full_system_platform_params(args):
        cmd.extend(["--platform-param", param])
    return cmd


def run_child(args: argparse.Namespace, artifacts: dict[str, Path]) -> tuple[int, list[str]]:
    cmd = child_command(args, artifacts)
    clear_run_outputs(args.out_dir)
    print("+ " + " ".join(cmd), flush=True)
    env = os.environ.copy()
    env["QBOX_BUILD_DIR"] = str(args.qbox_build_dir)
    env["QBOX_PLATFORM_BUILD_DIR"] = str(args.qbox_build_dir)
    env.update(si_topology_child_environment(args))
    if args.timer_probe:
        env["QBOX_APOLLO_TIMER_SNAPSHOT"] = "1"
        env["QBOX_APOLLO_TIMER_SNAPSHOT_RUN_ID"] = args.timer_probe_run_id
        env["QBOX_APOLLO_TIMER_SNAPSHOT_TIME_NS"] = str(args.timer_snapshot_time_ns)
        env["QBOX_APOLLO_TIMER_SNAPSHOT_INTERVAL_NS"] = str(args.timer_snapshot_interval_ns)
        env["QBOX_APOLLO_TIMER_SNAPSHOT_PATH"] = str(
            (args.out_dir / "timer-snapshot.json").resolve()
        )
    if not args.build_only:
        # Full-system runtime evidence must include the AP firmware/Linux path.
        # The reused RSE child runner only enables AP CPUs for probe-oriented
        # runs by default, which is useful for RSE-only diagnostics but is not
        # a valid Apollo full-system runtime shape.
        env["QBOX_RDASPEN_ENABLE_AP_CPUS"] = "true"
    env["QBOX_APOLLO_FULL_SI_CL0_IMAGE"] = str(artifacts["si_cl0_image"])
    env["QBOX_APOLLO_FULL_SI_CL0_LOG"] = str(
        (args.out_dir / "qbox-safety-island-cl0.log").resolve()
    )
    env["QBOX_APOLLO_FULL_SI_CL1_IMAGE"] = str(artifacts["si_cl1_image"])
    env["QBOX_APOLLO_FULL_SI_CL1_LOG"] = str(
        (args.out_dir / "qbox-safety-island-cl1.log").resolve()
    )
    if args.live_trace:
        env["QBOX_APOLLO_FULL_SI_GIC_MULTIVIEW_TRACE"] = "true"
        env["QBOX_APOLLO_FULL_SI_CL0_PC_TRACE"] = "true"
        env["QBOX_APOLLO_FULL_SI_CL0_EXCEPTION_TRACE"] = "true"
        env["QBOX_APOLLO_FULL_SI_CL0_PC_TRACE_LIMIT"] = "4096"
        env["QBOX_APOLLO_FULL_SI_CL0_PC_TRACE_FILE"] = str(
            (args.out_dir / "si-cl0-pc-trace.log").resolve()
        )
        env["QBOX_APOLLO_FULL_SI_CL1_MHU_TRACE"] = "true"
        env["QBOX_APOLLO_FULL_SI_CL1_MHU_TRACE_LIMIT"] = "8192"
        env["QBOX_RDASPEN_MHU_TRACE"] = "true"
        env["QBOX_RDASPEN_MHU_TRACE_LIMIT"] = "8192"
        env["QBOX_RDASPEN_MHU_TRACE_FILE"] = str(
            (args.out_dir / "ap-si-mhuv3-trace.log").resolve()
        )
        env["QBOX_APOLLO_FULL_SI_CL1_MHU_TRACE_FILE"] = str(
            (args.out_dir / "si-cl1-mhuv3-trace.log").resolve()
        )
    if args.si_cl0_command:
        return run_child_with_si_cl0_transport(args, cmd, env), cmd
    if args.keep_running_after_pass and not args.build_only:
        env["QBOX_RDASPEN_RESULT_PATH"] = str(
            (args.out_dir / RD_ASPEN_CHILD_RESULT).resolve()
        )
        env["QBOX_RDASPEN_SUMMARY_PATH"] = str(
            (args.out_dir / "rd-aspen-summary.txt").resolve()
        )
        proc = subprocess.Popen(cmd, cwd=workspace_root(), env=env)
        return wait_for_keep_running_child_pass(args, proc, cmd), cmd

    proc = subprocess.run(cmd, cwd=workspace_root(), env=env, check=False)
    return proc.returncode, cmd


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    root = workspace_root()
    qbox_platform_dir = Path(
        os.environ.get("QBOX_PLATFORM_DIR", str(root / "hsoc-stack/tools/qbox-platform"))
    )
    parser = argparse.ArgumentParser(
        description=__doc__,
        epilog=(
            "Fidelity mode: run_qbox_apollo_fvp_full.py --fidelity "
            "--artifacts {local,yocto} [options]"
        ),
    )
    parser.add_argument(
        "--conf",
        type=Path,
        default=qbox_platform_dir / "platforms/apollo/apollo-qvp.lua",
    )
    parser.add_argument(
        "--local-build-dir",
        type=Path,
        default=root / "build/local-apollo-qvp",
    )
    parser.add_argument(
        "--qbox-build-dir",
        type=Path,
        help=(
            "QBox CMake build directory. Defaults to "
            "<local-build-dir>/work/qbox-platform."
        ),
    )
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=root / "build/qbox-apollo-qvp" / f"full-{timestamp()}",
    )
    parser.add_argument("--timeout", type=int, default=900)
    parser.add_argument(
        "--timer-probe",
        action="store_true",
        help=(
            "Require a model-side structured timer snapshot. Missing or non-pass "
            "evidence is a hard failure."
        ),
    )
    parser.add_argument(
        "--timer-snapshot-time-ns",
        type=int,
        default=1_000_000,
        help="Simulation timestamp for the single model-side timer snapshot.",
    )
    parser.add_argument(
        "--timer-snapshot-interval-ns",
        type=int,
        default=1_000_000,
        help="Interval from start to end model-side timer snapshot.",
    )
    parser.add_argument("--jobs", type=int, default=max(1, (os.cpu_count() or 2) // 2))
    parser.add_argument("--check-only", action="store_true")
    parser.add_argument("--build-only", action="store_true")
    parser.add_argument("--skip-build", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--host-gdb-script", type=Path)
    parser.add_argument("--ignore-fail-patterns", action="store_true")
    parser.add_argument(
        "--si-cl0-command",
        action="append",
        default=[],
        help=(
            "Send one printable ASCII command to the real SI0 SCP CLI as raw "
            "UART bytes: Ctrl+E, command plus newline, then Ctrl+D. Repeatable."
        ),
    )
    parser.add_argument(
        "--si-cl0-command-timeout",
        type=float,
        default=30.0,
        help="Per-command timeout while waiting for the SI0 UART FIFO reader.",
    )
    si_topology_group = parser.add_mutually_exclusive_group()
    si_topology_group.add_argument(
        "--si-single-gic",
        dest="si_single_gic",
        action="store_true",
        help="Select the shared five-PE Safety Island QEMU instance.",
    )
    si_topology_group.add_argument(
        "--si-split-gic",
        dest="si_single_gic",
        action="store_false",
        help="Select the legacy split CL0/CL1 Safety Island QEMU instances.",
    )
    parser.set_defaults(si_single_gic=False)
    parser.add_argument(
        "--uboot-only",
        action="store_true",
        help=(
            "Stop the pass criteria at U-Boot FWU Regular State and skip "
            "Safety Island/Linux completion gates."
        ),
    )
    parser.add_argument(
        "--auto-provision-rse-otp",
        dest="auto_provision_rse_otp",
        action="store_true",
        help=(
            "Fallback for legacy or experimental local-build outputs: when "
            "the RSE OTP image is all zeroes, run a bounded CM-lifecycle QBox "
            "provisioning pass first and persist the resulting OTP before the "
            "requested full-system boot."
        ),
    )
    parser.add_argument(
        "--no-auto-provision-rse-otp",
        dest="auto_provision_rse_otp",
        action="store_false",
        help="Disable the blank RSE OTP fallback helper.",
    )
    parser.add_argument("--rse-otp-provision-timeout", type=int, default=600)
    parser.add_argument(
        "--keep-running-after-pass",
        action="store_true",
        help=(
            "Forward to the RSE-oriented runner so QBox remains alive after "
            "the pass condition."
        ),
    )
    post_login_group = parser.add_mutually_exclusive_group()
    post_login_group.add_argument(
        "--post-login-probe",
        dest="post_login_probe",
        action="store_true",
        help="Require the bounded root-shell driver/service qualification gate.",
    )
    post_login_group.add_argument(
        "--no-post-login-probe",
        dest="post_login_probe",
        action="store_false",
        help="Disable the root-shell gate for focused boot diagnostics.",
    )
    parser.add_argument("--primary-operation-manifest", type=Path)
    parser.add_argument("--primary-operation-schema", type=Path)
    parser.add_argument("--primary-operation-module-path", type=Path)
    parser.add_argument(
        "--smmu-backend",
        choices=["qemu-arm-smmuv3", "systemc-mmu720ae"],
        default="systemc-mmu720ae",
        help="Forwarded SMMU backend for the AP side of the QBox platform.",
    )
    parser.add_argument("--no-copy-writable-flash", action="store_true")
    parser.add_argument(
        "--rootfs-bootargs-profile",
        choices=["none", "quiet-console", "verbose-console"],
        default="none",
        help=(
            "Patch a legacy WIC boot entry before launch. Local UKI images "
            "already embed their command line and use the default 'none'."
        ),
    )
    parser.add_argument("--primary-login-prompt", default=APOLLO_PRIMARY_LOGIN_PROMPT)
    parser.add_argument("--primary-shell-marker", default=APOLLO_PRIMARY_SHELL_MARKER)
    parser.add_argument(
        "--primary-shell-prompt-re",
        default=r"(?:nexios-bsp#|root@apollo-qvp[^\n]*[#>]|\S+ #)\s*$",
    )
    perf_group = parser.add_mutually_exclusive_group()
    perf_group.add_argument(
        "--qbox-performance-preset",
        dest="qbox_performance_preset",
        action="store_true",
        help=(
            "Enable the validated QBox Apollo full-system boot acceleration "
            "preset. This is the default."
        ),
    )
    perf_group.add_argument(
        "--no-qbox-performance-preset",
        dest="qbox_performance_preset",
        action="store_false",
        help=(
            "Disable the default acceleration preset for fidelity or debug "
            "experiments."
        ),
    )
    dmi_group = parser.add_mutually_exclusive_group()
    dmi_group.add_argument(
        "--range-limited-flash-dmi",
        dest="range_limited_flash_dmi",
        action="store_true",
        help=(
            "Forward the storage-safe Strata flash DMI fast path to the "
            "RSE child runner. This is enabled by default for Apollo full-system "
            "boot performance."
        ),
    )
    dmi_group.add_argument(
        "--no-range-limited-flash-dmi",
        dest="range_limited_flash_dmi",
        action="store_false",
        help=(
            "Disable the range-limited flash DMI fast path for storage "
            "fidelity experiments."
        ),
    )
    parser.set_defaults(
        post_login_probe=True,
        qbox_performance_preset=True,
        range_limited_flash_dmi=True,
    )
    parser.set_defaults(auto_provision_rse_otp=True)
    parser.add_argument(
        "--cc3xx-stats",
        action="store_true",
        help="Forward CC3XX aggregate statistics collection to the RSE runner.",
    )
    parser.add_argument(
        "--rse-flash-backend",
        choices=("systemc-strata", "qemu-cfi-local"),
        default="qemu-cfi-local",
        help="RSE boot flash backend used by the child QBox runner.",
    )
    parser.add_argument(
        "--qbox-perf-profile",
        action="store_true",
        help=(
            "Forward QBox-side performance profile collection to the RSE "
            "runner."
        ),
    )
    parser.add_argument("--qbox-perf-profile-interval", type=int, default=1024)
    parser.add_argument(
        "--rse-hotpath-accel",
        action="store_true",
        help="Forward RSE BL1_1 memcpy/memset semantic hotpath acceleration.",
    )
    parser.add_argument("--rse-hotpath-max-bytes", type=int, default=16 * 1024 * 1024)
    parser.add_argument(
        "--rse-hotpath-memcpy-addr",
        type=lambda value: int(value, 0),
        help="Forward RSE hotpath memcpy Thumb entry address override.",
    )
    parser.add_argument(
        "--rse-hotpath-memset-addr",
        type=lambda value: int(value, 0),
        help="Forward RSE hotpath memset Thumb entry address override.",
    )
    parser.add_argument(
        "--rse-bl2-libc-hotpath",
        action="store_true",
        help="Forward RSE BL2 libc memcpy/memset hotpath selection.",
    )
    parser.add_argument(
        "--rse-lms-accel",
        action="store_true",
        help=(
            "Forward experimental RSE BL1_2 LMS verify semantic acceleration. "
            "Confirm effectiveness from the forwarded RSE perf profile "
            "lms_hits counter."
        ),
    )
    parser.add_argument("--rse-lms-max-data-bytes", type=int, default=16 * 1024 * 1024)
    parser.add_argument(
        "--rse-lms-verify-addr",
        type=lambda value: int(value, 0),
        help="Forward RSE BL1_2 pq_crypto_verify Thumb entry override.",
    )
    parser.add_argument(
        "--rse-bl2-load-accel",
        action="store_true",
        help="Forward RSE BL2 RAM-load payload semantic acceleration.",
    )
    parser.add_argument("--rse-bl2-load-accel-max-bytes", type=int, default=16 * 1024 * 1024)
    parser.add_argument(
        "--rse-bl2-boot-enc-accel",
        action="store_true",
        help="Forward RSE BL2 boot_enc_decrypt semantic acceleration.",
    )
    parser.add_argument(
        "--rse-bl2-img-hash-accel",
        action="store_true",
        help="Forward RSE BL2 bootutil_img_hash host-native SHA256 acceleration.",
    )
    parser.add_argument("--rse-bl2-img-hash-max-bytes", type=int, default=16 * 1024 * 1024)
    parser.add_argument("--rse-bl2-img-hash-max-seed-bytes", type=int, default=4096)
    parser.add_argument(
        "--rse-bl2-verify-sig-accel",
        action="store_true",
        help="Forward RSE BL2 bootutil_verify_sig host-native ECDSA acceleration.",
    )
    parser.add_argument(
        "--rse-bl2-verify-sig-skip",
        action="store_true",
        help=(
            "Forward the positive-boot-only RSE BL2 bootutil_verify_sig skip "
            "after host-native ECDSA verification succeeds."
        ),
    )
    parser.add_argument("--rse-bl2-verify-sig-max-key-bytes", type=int, default=512)
    parser.add_argument("--rse-bl2-verify-sig-max-sig-bytes", type=int, default=128)
    parser.add_argument(
        "--rse-bl2-delay-accel",
        action="store_true",
        help=(
            "Forward RSE BL2 delay_cycles acceleration for the LBIST and "
            "MBIST mimic loops while preserving the SI startup wait by default."
        ),
    )
    parser.add_argument("--rse-bl2-delay-max-cycles", type=int, default=50 * 1000 * 1000)
    parser.add_argument("--rse-bl2-delay-expected-hits", type=int, default=2)
    parser.add_argument("--cc3xx-stats-interval", type=int, default=1024)
    parser.add_argument(
        "--cc3xx-status-read-fastpath",
        action="store_true",
        help="Forward the RSE CC3XX QEMU-side status-read fast path.",
    )
    parser.add_argument(
        "--cc3xx-qemu-native-backend",
        action="store_true",
        help=(
            "Forward the RSE CC3XX QEMU-native backend selection. This also "
            "enables the CC3XX direct MMIO fast path in the RSE runner."
        ),
    )
    parser.add_argument(
        "--cc3xx-local-mmio-fastpath",
        action="store_true",
        help="Forward the RSE CC3XX QEMU-local direct MMIO fast path.",
    )
    parser.add_argument(
        "--rse-fast-boot-aliases",
        action="store_true",
        help=(
            "Forward the legacy RSE fast-boot direct file-backed alias preset "
            "to the RSE runner."
        ),
    )
    parser.add_argument(
        "--rse-fast-boot-sram-dmi",
        action="store_true",
        help=(
            "Forward the RSE fast-boot SRAM DMI/shared-memory preset to the "
            "RSE runner without direct file-backed SRAM/AP-BL2 aliases."
        ),
    )
    parser.add_argument(
        "--legacy-file-backed-sram",
        action="store_true",
        help=(
            "Rollback path for the performance preset: forward legacy "
            "--rse-fast-boot-aliases instead of --rse-fast-boot-sram-dmi."
        ),
    )
    parser.add_argument(
        "--live-trace",
        action="store_true",
        help=(
            "Enable verbose live Safety Island GIC/MHU/PC traces. The "
            "default keeps UART logs and runtime markers but avoids trace "
            "overhead during boot-performance checks."
        ),
    )
    parser.add_argument("--platform-param", action="append", default=[])
    parser.add_argument("--rse-rom", type=Path)
    parser.add_argument("--rse-flash", type=Path)
    parser.add_argument(
        "--rse-flash-state",
        type=Path,
        help="Persistent writable RSE flash state managed by the child runner.",
    )
    parser.add_argument(
        "--reset-rse-flash-state",
        action="store_true",
        help="Recreate --rse-flash-state from the selected RSE flash image.",
    )
    parser.add_argument("--rse-otp", type=Path)
    parser.add_argument("--ap-flash", type=Path)
    parser.add_argument("--ap-bl2-elf", type=Path)
    parser.add_argument("--rse-bl1-2-elf", type=Path)
    parser.add_argument("--rse-bl2-elf", type=Path)
    parser.add_argument("--rootfs", type=Path)
    parser.add_argument("--efi-capsule-disk", type=Path)
    parser.add_argument("--provisioning-bundle", type=Path)
    parser.add_argument("--ap-dtb", type=Path)
    parser.add_argument("--rse-symbols", type=Path)
    parser.add_argument("--si-cl0-image", type=Path)
    parser.add_argument("--si-cl1-image", type=Path)
    parser.add_argument("--si-cl1-symbols", type=Path)
    args = parser.parse_args(argv)
    operation_args = (
        args.primary_operation_manifest,
        args.primary_operation_schema,
        args.primary_operation_module_path,
    )
    if any(value is not None for value in operation_args) and not all(
        value is not None for value in operation_args
    ):
        parser.error(
            "--primary-operation-manifest, --primary-operation-schema, and "
            "--primary-operation-module-path must be used together"
        )
    args.conf = args.conf.resolve()
    args.local_build_dir = args.local_build_dir.resolve()
    if args.qbox_build_dir is None:
        qbox_build_dir_env = os.environ.get("QBOX_PLATFORM_BUILD_DIR") or os.environ.get(
            "QBOX_BUILD_DIR"
        )
        if qbox_build_dir_env:
            args.qbox_build_dir = Path(qbox_build_dir_env)
        else:
            args.qbox_build_dir = args.local_build_dir / "work/qbox-platform"
    args.qbox_build_dir = args.qbox_build_dir.resolve()
    os.environ["QBOX_PLATFORM_BUILD_DIR"] = str(args.qbox_build_dir)
    os.environ["QBOX_BUILD_DIR"] = str(args.qbox_build_dir)
    args.out_dir = args.out_dir.resolve()
    if args.uboot_only:
        args.post_login_probe = False
        args.primary_login_prompt = "FWU: System booting in Regular State"
        args.primary_shell_marker = "FWU: System booting in Regular State"
        args.primary_shell_prompt_re = "FWU: System booting in Regular State"
    if args.qbox_performance_preset:
        args.rse_hotpath_accel = True
        args.rse_bl2_libc_hotpath = True
        args.rse_lms_accel = True
        args.rse_bl2_load_accel = True
        args.rse_bl2_boot_enc_accel = True
        args.rse_bl2_img_hash_accel = True
        args.rse_bl2_verify_sig_accel = True
        args.rse_bl2_delay_accel = True
        args.cc3xx_qemu_native_backend = True
        if args.legacy_file_backed_sram:
            args.rse_fast_boot_aliases = True
        else:
            args.rse_fast_boot_sram_dmi = True
    if args.legacy_file_backed_sram and args.rse_fast_boot_sram_dmi:
        parser.error(
            "--legacy-file-backed-sram cannot be used with "
            "--rse-fast-boot-sram-dmi"
        )
    if args.rse_fast_boot_sram_dmi and args.rse_fast_boot_aliases:
        parser.error(
            "--rse-fast-boot-sram-dmi cannot be used with "
            "--rse-fast-boot-aliases"
        )
    if args.rse_hotpath_max_bytes <= 0:
        parser.error("--rse-hotpath-max-bytes must be positive")
    if args.timer_snapshot_time_ns < 0:
        parser.error("--timer-snapshot-time-ns must be non-negative")
    if args.timer_snapshot_interval_ns <= 0:
        parser.error("--timer-snapshot-interval-ns must be positive")
    if args.rse_hotpath_memcpy_addr is not None and args.rse_hotpath_memcpy_addr <= 0:
        parser.error("--rse-hotpath-memcpy-addr must be positive")
    if args.rse_hotpath_memset_addr is not None and args.rse_hotpath_memset_addr <= 0:
        parser.error("--rse-hotpath-memset-addr must be positive")
    if args.rse_lms_max_data_bytes <= 0:
        parser.error("--rse-lms-max-data-bytes must be positive")
    if args.rse_lms_verify_addr is not None and args.rse_lms_verify_addr <= 0:
        parser.error("--rse-lms-verify-addr must be positive")
    if args.rse_bl2_load_accel_max_bytes <= 0:
        parser.error("--rse-bl2-load-accel-max-bytes must be positive")
    if args.rse_bl2_img_hash_max_bytes <= 0:
        parser.error("--rse-bl2-img-hash-max-bytes must be positive")
    if args.rse_bl2_img_hash_max_seed_bytes < 0:
        parser.error("--rse-bl2-img-hash-max-seed-bytes must be non-negative")
    if args.rse_bl2_verify_sig_max_key_bytes <= 0:
        parser.error("--rse-bl2-verify-sig-max-key-bytes must be positive")
    if args.rse_bl2_verify_sig_max_sig_bytes <= 0:
        parser.error("--rse-bl2-verify-sig-max-sig-bytes must be positive")
    if args.rse_bl2_delay_max_cycles <= 0:
        parser.error("--rse-bl2-delay-max-cycles must be positive")
    if args.rse_bl2_delay_expected_hits < 0:
        parser.error("--rse-bl2-delay-expected-hits must be non-negative")
    if args.rse_otp_provision_timeout <= 0:
        parser.error("--rse-otp-provision-timeout must be positive")
    if args.si_cl0_command_timeout <= 0:
        parser.error("--si-cl0-command-timeout must be positive")
    if args.si_cl0_command and args.keep_running_after_pass:
        parser.error(
            "--si-cl0-command cannot be used with --keep-running-after-pass"
        )
    for si_command in args.si_cl0_command:
        try:
            si_cl0_command_payload(si_command)
        except SiCl0CommandValidationError as error:
            parser.error(str(error))
    if args.reset_rse_flash_state and args.rse_flash_state is None:
        parser.error("--reset-rse-flash-state requires --rse-flash-state")
    if args.rse_bl2_verify_sig_skip:
        args.rse_bl2_verify_sig_accel = True
    return args


def main(argv: list[str] | None = None) -> int:
    mode_args = sys.argv[1:] if argv is None else argv
    if mode_args[:1] == ["--runtime-child"]:
        return runtime_engine.main(mode_args[1:])
    if mode_args[:1] == ["--fidelity"]:
        return fidelity_runner.main(mode_args[1:])

    args = parse_args(mode_args)
    try:
        args.si_topology_contract = load_si_topology_contract(args)
    except SafetyIslandTopologyContractError as error:
        return write_si_topology_contract_failure(args, error)
    if args.dry_run:
        return run_si_topology_dry_run(args)
    args.timer_probe_run_id = uuid.uuid4().hex
    args.provision_blank_rse_otp = False
    args.rse_otp_auto_provision = {
        "enabled": args.auto_provision_rse_otp,
        "requested": False,
        "reason": "not_evaluated",
    }
    artifacts = resolved_artifacts(args)
    debug_manifest_blocker = ensure_default_debug_manifest(args, artifacts)
    missing = missing_required(args, artifacts)
    blocker = debug_manifest_blocker or ("; ".join(missing) if missing else None)
    if args.check_only or blocker:
        return write_result(
            args,
            artifacts,
            command=[],
            child_status=None,
            child_returncode=None,
            blocker=blocker,
            check_only=True,
        )

    blocker = auto_provision_rse_otp(args, artifacts)
    if blocker:
        write_blocker_logs(args, blocker)
        return write_result(
            args,
            artifacts,
            command=[],
            child_status=None,
            child_returncode=None,
            blocker=blocker,
            check_only=False,
        )

    child_rc, command = run_child(args, artifacts)
    child_result = args.out_dir / "result.json"
    child_status = read_json(child_result)
    if child_status:
        shutil.copy2(child_result, args.out_dir / RD_ASPEN_CHILD_RESULT)
    copy_child_logs(args)
    blocker = child_status.get("blocker") if child_status else f"child_failed:{child_rc}"
    if child_status and not child_status.get("passed") and not blocker and child_rc:
        blocker = f"child_failed:{child_rc}"
    if args.build_only and blocker == "check_only_no_runtime":
        child_status["passed"] = True
        child_status["blocker"] = None
        child_status["apollo_full_note"] = "build_only_no_runtime"
        blocker = None
    if child_status and child_status.get("passed"):
        blocker = None
    return write_result(
        args,
        artifacts,
        command=command,
        child_status=child_status,
        child_returncode=child_rc,
        blocker=blocker,
        check_only=False,
    )


if __name__ == "__main__":
    raise SystemExit(main())
