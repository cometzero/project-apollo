#!/usr/bin/env python3
"""AutoSD dashboard: loopback by default, explicitly opted-in LAN listeners."""
import argparse
import base64
import ipaddress
import os
from contextlib import nullcontext
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import mimetypes
from pathlib import Path
import secrets
import shlex
import socket
import stat
import subprocess
import sys
import threading
import time
from urllib.parse import parse_qs, urlsplit
import uuid

ROOT = Path(__file__).resolve().parents[2]
WEB = Path(__file__).resolve().parent / "web"
sys.path.insert(0, str(WEB.parent))
from service_logs import SOURCES as SERVICE_LOG_SOURCES, collect as collect_service_logs
CATALOG = [
    ("boot", "AutoSD 시뮬레이션 부팅", "전용 복사본으로 Apollo QEMU TCG 실행", False),
    ("health", "Automotive 상태 검사", "Safety monitor · ADAS · QM · BlueChi 검사", False),
    ("automotive", "Automotive S01–S06", "QM 재시작, ADAS fault/latch 및 명시적 복구 포함", True),
    ("rt", "PREEMPT_RT R01–R06", "TCG 관찰 기준 5000 µs · 일반 스케줄러 비교/지연 주입은 성능 판정 제외", False),
    ("timerlat", "Timerlat IRQ/thread latency", "CPU 1 FIFO 50, 5초, TCG trace 중지 기준 5000 µs", False),
    ("osnoise", "OS noise", "CPU 1 histogram · TCG sample 중지 기준 5000 µs", False),
    ("mixed-criticality", "Mixed criticality MC01–MC03", "자원 분리 · QM 부하 · 장애 격리 기능 데모 (안전 인증 아님)", True),
    ("watchdog", "Watchdog WD01–WD03", "장치 검사 · keepalive · 서비스 watchdog; 하드웨어 reset 제외", True),
    ("monitor-mhu", "MHU doorbell 장애 및 전체 reset 복구", "QBox full opt-in 전용; HIPC 손실 주입 후 RSE/SI/AP 전체 reset · 앱/통신 복구 검사", True),
    ("monitor-qualify", "QBox Pause/Resume 실증 검증", "QBox full 전용; 10회 정지/재개 · HIPC/health · watchdog AP reset 복구 검증 후 현재 VM 제어 활성화", True),
    ("shutdown", "시뮬레이션 종료", "이 서버가 시작한 guest만 정상 종료", False),
]
SCENARIOS = {
    "mixed-criticality": [
        ("MC01", "Partition 자원 분리", "root / ASIL-B / QM 서비스 및 cgroup 검사", False),
        ("MC02", "QM 부하 격리", "제한된 QM 부하 중 ADAS heartbeat 관찰", True),
        ("MC03", "QM 장애 격리", "QM 장애 주입 및 ADAS/safety 상태와 복구 확인", True),
    ],
    "watchdog": [
        ("WD01", "SBSA 구성 검사", "장치를 열지 않는 sysfs / systemd 정책 검사", False),
        ("WD02", "SBSA keepalive", "timeout 20초, 30초 급식 및 정상 disarm", True),
        ("WD03", "서비스 watchdog", "전용 transient 서비스 notify 중단 · watchdog 검출 · 정리", True),
        ("WD04", "SBSA WS1 reset 및 복구", "QBox full 전용; AP reset · 새 boot ID · 앱 및 HIPC 검증", True),
    ],
    "automotive": [
        ("S01", "현재 부팅 상태 검사", "Safety monitor · ADAS · QM · BlueChi 상태 확인", False),
        ("S02", "BlueChi 제어", "정상 상태에서 BlueChi 서비스 제어 검증", True),
        ("S03", "QM 컨테이너 재시작", "정상 상태에서 QM 컨테이너 강제 종료·재생성 확인", True),
        ("S04", "ADAS 장애 주입", "정상 상태에서 ADAS 장애 및 safety latch 검증", True),
        ("S05", "Safety latch 확인", "기존 장애 latch가 유지되는지 확인; S04 이후 실행", True),
        ("S06", "운영자 복구", "기존 장애 latch를 명시적으로 복구; S04 이후 실행", True),
    ],
    "rt": [
        ("R01", "SCHED_OTHER 기준 측정", "CPU 1 일반 스케줄러 latency 측정", False),
        ("R02", "FIFO 기준 측정", "CPU 1 FIFO 50 · mlock latency 측정", False),
        ("R03", "QM 부하 측정", "QM CPU 부하 중 FIFO latency 측정", False),
        ("R04", "동일 CPU 경합", "CPU 1 경합 부하 중 FIFO latency 측정", False),
        ("R05", "지연 주입 검출", "합성 지연 주입과 임계값 검출; 성능 판정 제외", False),
        ("R06", "Cyclictest", "외부 cyclictest 벤치마크 및 실제 sample 검증", False),
    ],
}
CHILD_ACTIONS = {parent + "-" + code.lower(): (parent, code, title, desc, disruptive)
                 for parent, rows in SCENARIOS.items()
                 for code, title, desc, disruptive in rows}
ACTION_METADATA = {action: (title, desc, disruptive) for action, title, desc, disruptive in CATALOG}
ACTION_METADATA.update({action: row[2:] for action, row in CHILD_ACTIONS.items()})
SYSTEM_CONTROLS = [
    ("boot", "Power on", "AutoSD VM 부팅", False),
    ("shutdown", "Power off", "guest 정상 종료 (강제 종료 아님)", True),
    ("reboot", "Reboot", "현재 디스크를 유지하고 guest OS 재부팅", True),
    ("pause", "Pause", "가상 시스템 실행 일시정지; 먼저 진행 중 작업을 완료하세요", True),
    ("resume", "Resume", "일시정지한 가상 시스템 실행 재개", False),
]
ACTION_METADATA.update({a: (t, d, c) for a, t, d, c in SYSTEM_CONTROLS if a != "shutdown"})
CONTROL_BARRIERS = {"pause", "resume", "reboot", "shutdown", "monitor-mhu", "monitor-qualify"}
MEASUREMENT_ACTIONS = {"rt", "timerlat", "osnoise"} | {
    action for action, row in CHILD_ACTIONS.items() if row[0] in ("rt", "watchdog", "mixed-criticality")} | {"watchdog", "mixed-criticality"}
BACKENDS = {"qemu": "QEMU TCG", "qbox": "QBox AP only", "qbox-full": "QBox full system"}
DOMAIN_LOGS = {"rse": "rse-uart.log", "si-cl0": "si-cl0-uart.log", "si-cl1": "si-cl1-uart.log"}
FULL_DOMAINS = ("rse", "si-cl0", "si-cl1", "ap")


def action_family(action):
    return CHILD_ACTIONS[action][0] if action in CHILD_ACTIONS else action


def guest_timeout(action):
    return 1500 if action == "automotive" else 360 if action_family(action) == "automotive" else 240


ARTIFACTS = {"evidence.tar.gz", "results.json", "scenarios.json", "trace-result.json", "qualification.json",
             "rtla.log", "job.json", "console.log"}


def now():
    return datetime.now(timezone.utc).isoformat()


def read_json(path):
    try:
        if path.stat().st_size > 4 * 1024 * 1024:
            return {"status": "UNAVAILABLE", "error": "Evidence exceeds size limit"}
        return json.loads(path.read_text())
    except (OSError, ValueError):
        return None


def evidence(base):
    """Only known structured evidence, never arbitrary user-selected paths."""
    found = []
    patterns = ("rt-*-verified/results.json", "rt-*-verified/trace-result.json",
                "automotive-demo-suite*/scenarios.json", "automotive-demo-suite*/results.json")
    for pattern in patterns:
        for path in sorted(base.glob(pattern)):
            if path.is_symlink() or base.resolve() not in path.resolve().parents:
                continue
            result = read_json(path)
            if result is not None:
                found.append({"id": path.parent.name + "/" + path.name, "path": str(path.relative_to(ROOT))
                              if ROOT in path.parents else str(path),
                              "modified_at": datetime.fromtimestamp(path.stat().st_mtime,
                                  timezone.utc).isoformat(), "result": result})
    return found


def telemetry_history(base):
    """Restore bounded historical samples, never adopt a former VM or live status."""
    for path in sorted((base / "dashboard").glob("*/telemetry.jsonl"), reverse=True):
        try:
            if path.is_symlink() or base.resolve() not in path.resolve().parents:
                continue
            size = path.stat().st_size
            if size > 256 * 1024 * 1024:
                continue
            with path.open("rb") as stream:
                offset = max(0, size - 4 * 1024 * 1024)
                stream.seek(offset)
                if offset:
                    stream.readline()  # Discard a possibly incomplete leading record.
                lines = stream.read(4 * 1024 * 1024).splitlines()
            history = []
            for line in reversed(lines):
                try:
                    sample = json.loads(line)
                except (ValueError, UnicodeError):
                    continue
                if (isinstance(sample, dict) and isinstance(sample.get("cpus"), list)
                        and isinstance(sample.get("subsystems"), list)
                        and sample.get("collected_at")):
                    history.append(sample)
                if len(history) == 120:
                    break
            if history:
                return list(reversed(history))
        except OSError:
            continue
    return []


class Dashboard:
    def __init__(self, base, manifest=None, rootfs=None, ssh_port=2244, allow=False, backend="qemu",
                 runtime_injection=False, qbox_diagnostics=False):
        if backend not in BACKENDS:
            raise ValueError("Unsupported backend: choose qemu, qbox or qbox-full")
        self.backend = backend
        self.runtime_injection = runtime_injection
        self.qbox_diagnostics = qbox_diagnostics
        self.qbox_pause_run = None
        self.qbox_pause_unknown_run = None
        self.boot_timeout = {"qemu": 240, "qbox": 600, "qbox-full": 900}[backend]
        self.base = Path(base)
        self.manifest, self.rootfs = manifest, rootfs
        self.ssh_port, self.allow = ssh_port, allow
        self.token = secrets.token_urlsafe(32)
        self.lock = threading.RLock()
        self.jobs = []
        self.vm_process = None
        self.vm_job = None
        self.vm_paused = False
        self.log_session = None
        self.feature_session = None
        self.feature_boot = None
        self.feature_health = None
        self.boot_deadline = None
        self.auto_health_pending = False
        self.guest_log_offset = 0
        self.service_log_cache = {}
        self.service_log_inflight = False
        self.active = None
        self.monitoring = {"status": "OFFLINE", "sampled_at": None,
                           "cpus": [], "subsystems": []}
        self.monitor_stop = threading.Event()
        self.telemetry_lock = threading.Lock()
        self.history = telemetry_history(self.base)
        real = next((sample for sample in reversed(self.history) if sample.get("cpus")), None)
        if real:
            self.monitoring = dict(real, status="OFFLINE", historical=True)
        self.sample_count = 0
        self.session = None
        from simulator import Simulator
        self.simulator_barriers = MEASUREMENT_ACTIONS | CONTROL_BARRIERS
        self.simulator = Simulator(self)
        self.monitor_port = None
        for path in sorted((self.base / "dashboard").glob("*/*/job.json"))[-200:]:
            if path.is_symlink() or (self.base / "dashboard").resolve() not in path.resolve().parents:
                continue
            job = read_json(path)
            if not isinstance(job, dict) or job.get("id") != path.parent.name:
                continue
            if len(job["id"]) != 32 or any(c not in "0123456789abcdef" for c in job["id"]):
                continue
            job["evidence_path"] = str(path.parent.resolve())
            if job.get("status") == "RUNNING":
                job["status"] = "ORPHANED_NOT_MANAGED"
                job["error"] = "Previous server stopped; process ownership not adopted"
            self.jobs.append(job)

    def running(self):
        return self.vm_process is not None and self.vm_process.poll() is None

    def unsupported_control(self, action):
        if (self.backend == "qbox-full" and action == "resume" and self.vm_job is not None
                and self.qbox_pause_unknown_run == self.vm_job):
            return None
        if (self.backend == "qbox-full" and action in ("pause", "resume") and self.vm_job is not None
                and self.qbox_pause_run == self.vm_job):
            return None
        if ((self.backend != "qemu" and action in ("pause", "resume"))
                or (self.backend == "qbox" and action == "reboot")):
            return (BACKENDS[self.backend] + ": " + action + " control is not qualified; "
                    "use Power off then Power on for a preserved-disk restart")
        return None

    def select_backend(self, backend):
        with self.lock:
            if not isinstance(backend, str) or backend not in BACKENDS:
                raise ValueError("Unsupported backend: choose qemu, qbox or qbox-full")
            if self.running() or self.active or self.auto_health_pending:
                raise ValueError("Power off and finish all operations before selecting a backend")
            if backend != self.backend:
                self.backend = backend
                self.boot_timeout = {"qemu": 240, "qbox": 600, "qbox-full": 900}[backend]
                self.vm_process = None
                self.vm_job = None
                self.vm_paused = False
                self.log_session = None
                self.feature_session = None
                self.feature_boot = None
                self.feature_health = None
                self.boot_deadline = None
                self.guest_log_offset = 0
                self.service_log_cache.clear()
                self.monitoring = {"status": "OFFLINE", "sampled_at": None, "cpus": [], "subsystems": []}
                self.history = []
                self.session = None
                self.sample_count = 0
            return {"backend": self.backend, "backends": self.backend_catalog(), "feature_session": self.feature_session}

    def backend_catalog(self):
        enabled = not self.running() and not self.active and not self.auto_health_pending
        return [{"id": backend, "title": title, "selected": backend == self.backend, "enabled": enabled}
                for backend, title in BACKENDS.items()]

    def domain_boot(self):
        if self.backend != "qbox-full":
            return None
        boot = next((job for job in self.jobs if job["id"] == self.vm_job), None)
        result = read_json(Path(boot["evidence_path"]) / "vm/domains.json") if boot else None
        if not isinstance(result, dict) or not isinstance(result.get("domains"), list):
            result = {"status": "WAITING", "domains": []}
        rows = {row.get("id"): row for row in result["domains"] if isinstance(row, dict)}
        domains = [rows.get(name, {"id": name, "status": "WAITING"}) for name in FULL_DOMAINS]
        status = ("PASS" if result.get("status") == "PASS" and all(row.get("status") == "PASS" for row in domains)
                  else "FAIL" if result.get("status") == "FAIL" or any(row.get("status") == "FAIL" for row in domains)
                  else "WAITING")
        return dict(result, status=status, domains=domains)

    def reboot_verified(self, before, after, previous_domains=None):
        if (after.get("status") != "ONLINE" or not after.get("boot_id")
                or after["boot_id"] == before.get("boot_id")):
            return False
        if self.backend != "qbox-full":
            return True
        domains = self.domain_boot()
        old_ap = next((row for row in (previous_domains or {}).get("domains", []) if row.get("id") == "ap"), {})
        ap = next(row for row in domains["domains"] if row["id"] == "ap")
        epoch = ap.get("boot_epoch", 0)
        provision = domains.get("provision", {})
        return (domains["status"] == "PASS" and epoch > old_ap.get("boot_epoch", 0)
                and provision.get("status") == "PASS" and provision.get("boot_epoch") == epoch)

    def shutdown_wait_timeout(self):
        return 180 if self.backend == "qbox-full" else 60

    def boot_command(self, directory):
        launcher = {"qemu": "run_qemu_linux.sh", "qbox": "run_qbox_linux.sh", "qbox-full": "run_qbox_autosd.sh"}[self.backend]
        argv = [str(ROOT / launcher),
                "--autosd", str(self.manifest), "--rootfs", str(self.rootfs),
                "--headless", "--timeout", "7200", "--out-dir", str(directory / "vm")]
        if self.backend != "qemu":
            with socket.socket() as probe:
                probe.bind(('127.0.0.1', 0))
                self.monitor_port = probe.getsockname()[1]
            argv += ["--monitor-port", str(self.monitor_port)]
            if self.qbox_diagnostics:
                argv += ["--qmp"]
            if self.backend == "qbox-full":
                argv += ["--reset-trace"]
                if self.runtime_injection:
                    argv += ["--runtime-injection"]
            return argv + ["--ssh-port", str(self.ssh_port)]
        return argv + ["--netdev", "user,id=net0,hostfwd=tcp:127.0.0.1:" + str(self.ssh_port) + "-:22"]

    def operation_timeout(self, action):
        """Host wall-time allowance; QBox guest time need not track host time."""
        if action_family(action) in ("watchdog", "mixed-criticality"):
            return 600
        if self.backend != "qemu":
            family = action_family(action)
            if family == "automotive":
                return 1500 if action == "automotive" else 600
            if family == "rt":
                return 600
            if action in ("health", "timerlat", "osnoise"):
                return 360
        return guest_timeout(action)

    def mark_offline(self):
        snapshot = self.monitoring
        if not snapshot.get("cpus"):
            snapshot = next((sample for sample in reversed(self.history) if sample.get("cpus")), snapshot)
        self.monitoring = dict(snapshot, status="OFFLINE", historical=True)

    def state(self):
        with self.lock:
            running = self.running()
            enabled = self.allow and bool(self.manifest and self.rootfs)
            domain_boot = self.domain_boot()
            domains_ready = domain_boot is None or domain_boot["status"] == "PASS"
            catalog = [{"action": action, "title": title, "description": desc,
                        "disruptive": disruptive,
                        "enabled": enabled and not self.active and
                        (not running if action == "boot" else running and not self.vm_paused
                         and not self.auto_health_pending and (domains_ready or action == "shutdown"))}
                       for action, title, desc, disruptive in CATALOG]
            for item in catalog:
                if item["action"] == "monitor-qualify" and self.backend != "qbox-full":
                    item["enabled"] = False
                    item["unsupported_reason"] = "QBox full system only"
                if item["action"] == "monitor-mhu":
                    reason = ("QBox full system only" if self.backend != "qbox-full" else
                              "Requires server --runtime-injection and a fresh opted-in boot"
                              if not self.runtime_injection else None)
                    item["enabled"] = item["enabled"] and reason is None
                    item["unsupported_reason"] = reason
                if self.backend != "qemu":
                    item["description"] = ("전용 복사본으로 Apollo " + ("QBox AP direct" if self.backend == "qbox" else BACKENDS[self.backend]) + " 실행" if item["action"] == "boot"
                                           else item["description"].replace("TCG", "QBox 기능 관찰용 잠정"))
                item["children"] = [
                    {"action": item["action"] + "-" + code.lower(), "code": code,
                     "title": title, "description": desc, "disruptive": disruptive,
                     "enabled": item["enabled"] and (code != "WD04" or self.backend == "qbox-full"),
                     "unsupported_reason": "QBox full system only" if code == "WD04" and self.backend != "qbox-full" else None}
                    for code, title, desc, disruptive in SCENARIOS.get(item["action"], [])]
            controls = [{"action": a, "title": t, "description": d, "disruptive": c,
                         "unsupported_reason": self.unsupported_control(a),
                         "enabled": enabled and not self.unsupported_control(a) and not self.active and
                         (not running if a == "boot" else running and
                          (self.vm_paused if a == "resume" else not self.vm_paused))}
                        for a, t, d, c in SYSTEM_CONTROLS]
            return {"csrf_token": self.token, "catalog": catalog, "system_controls": controls, "jobs": list(self.jobs),
                    "backends": self.backend_catalog(),
                    "backend_selection_enabled": not running and not self.active and not self.auto_health_pending,
                    "feature_session": self.feature_session,
                    "feature_boot": self.feature_boot, "feature_health": self.feature_health,
                    "guest_log_sources": [{"id": "uart", "title": "Boot UART", "description": "현재 AP 부팅 콘솔"},
                                          *([{"id": name, "title": name.upper() + " UART", "description": "Full-system firmware UART"}
                                             for name in DOMAIN_LOGS] if self.backend == "qbox-full" else []), *SERVICE_LOG_SOURCES],
                    "domain_boot": domain_boot,
                    "monitoring": self.monitoring, "monitoring_history": list(self.history),
                    "simulator": self.simulator.snapshot(),
                    "simulator_capabilities": self.simulator.capabilities(),
                    "evidence": evidence(self.base),
                    "vm": {"running": running, "owned": self.vm_process is not None,
                           "backend": self.backend,
                           "paused": running and self.vm_paused,
                           "pause_state_unknown": running and self.vm_job is not None and self.qbox_pause_unknown_run == self.vm_job,
                           "log_session": self.log_session,
                           "guest_log_url": "/api/guest/log",
                           "ssh_port": self.ssh_port, "boot_job": self.vm_job},
                    "capabilities": {"execution_enabled": enabled, "platform": "QBox AP direct" if self.backend == "qbox" else BACKENDS[self.backend],
                        "qualification": "FUNCTIONAL_ONLY_NOT_HARDWARE_TIMING",
                        "unsupported": (["QBox Pause/Resume/Reboot"] if self.backend == "qbox" else
                                        ["QBox Pause/Resume"] if self.backend == "qbox-full" and (not self.vm_job or self.qbox_pause_run != self.vm_job) else []) + ["RSE/Safety Island physical counters",
                                        "key-only SSH" if self.backend == "qbox-full" else "native UKI/key-only SSH", "remote hosts"],
                        "manual_features": [
                            {"id": "ota", "title": "OTA / UKIBoot A/B", "status": "MANUAL_ONLY", "reason": "Native UKI/OSTree guest and signed update payload required"},
                            {"id": "ipc", "title": "IPC / iceoryx2", "status": "MANUAL_ONLY", "reason": "Separate prepared IPC payload and policy required"},
                            {"id": "selinux", "title": "SELinux policy demos", "status": "MANUAL_ONLY", "reason": "Policy build/install is not exposed through HTTP"}]}}

    def start(self, action, confirmed=False, *, automatic=False):
        with self.lock:
            if action not in ACTION_METADATA:
                raise ValueError("Unknown action")
            if action == "watchdog-wd04" and self.backend != "qbox-full":
                raise ValueError("WD04 is supported only on QBox full system")
            if action == "monitor-mhu" and (self.backend != "qbox-full" or not self.runtime_injection):
                raise ValueError("MHU reset scenario requires QBox full and server --runtime-injection")
            if action == "monitor-qualify" and self.backend != "qbox-full":
                raise ValueError("Pause/Resume qualification requires QBox full")
            if self.unsupported_control(action):
                raise ValueError(self.unsupported_control(action))
            if not self.allow or not self.manifest or not self.rootfs:
                raise ValueError("Execution disabled; explicitly configure a disposable private guest")
            if ACTION_METADATA[action][2] and confirmed is not True:
                raise ValueError("Fault injection/recovery requires confirm_disruptive=true")
            if self.active:
                raise ValueError("Another demo operation is running")
            if self.auto_health_pending and not automatic and action not in CONTROL_BARRIERS:
                raise ValueError("Automatic boot health verification is pending")
            if self.backend == "qbox-full" and action not in ("boot", "shutdown", "resume") and self.domain_boot()["status"] != "PASS":
                raise ValueError("Full-system domain boot verification is not complete")
            if (action == "boot") == self.running():
                raise ValueError("VM already running" if action == "boot" else "No owned running VM")
            if action == "resume" and not self.vm_paused:
                raise ValueError("VM is not paused")
            if self.running() and self.vm_paused and action != "resume":
                raise ValueError("VM paused; resume before guest operations")
            if action == "boot":
                with socket.socket() as probe:
                    probe.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                    probe.bind(("127.0.0.1", self.ssh_port))
            if self.session is None:
                self.session = self.base / "dashboard" / (datetime.now().strftime("%Y%m%d-%H%M%S-") + uuid.uuid4().hex[:8])
                self.session.mkdir(parents=True, exist_ok=False)
            job = {"id": uuid.uuid4().hex, "action": action, "status": "RUNNING",
                   "backend": self.backend,
                   "started_at": now(), "finished_at": None, "returncode": None, "result": None}
            if action == "boot":
                self.qbox_pause_run = None
                self.qbox_pause_unknown_run = None
                self.log_session = job["id"]
                self.guest_log_offset = 0
            job["log_session"] = self.log_session
            job["vm_run_id"] = job["id"] if action == "boot" else self.vm_job
            job["log_url"] = "/api/jobs/" + job["id"] + "/log"
            job["artifacts_url"] = "/api/jobs/" + job["id"] + "/artifacts/"
            if action in ("boot", "reboot", "shutdown", "watchdog-wd04", "monitor-mhu", "monitor-qualify"):
                self.feature_session = job["id"]
                self.auto_health_pending = action != "shutdown"
                self.boot_deadline = time.monotonic() + self.boot_timeout if action == "boot" else None
                self.feature_boot = (dict(job, action="boot", feature_session=self.feature_session,
                                          phase="Guest boot ID / SSH 확인 중")
                                     if action != "shutdown" else None)
                self.feature_health = (dict(job, action="health", status="QUEUED", feature_session=self.feature_session,
                                           phase="부팅 확인 후 Automotive 상태 자동 검사")
                                       if action != "shutdown" else None)
            job["feature_session"] = self.feature_session
            if automatic:
                job["automatic"] = True
            directory = self.session / job["id"]
            directory.mkdir()
            job["evidence_path"] = str(directory)
            self.jobs.append(job)
            if action == "boot":
                # Publish the new UART owner atomically with its log epoch;
                # never tag the previous boot's UART as the new session.
                self.vm_job = job["id"]
            # Reserve boot too until Popen has established ownership.
            self.active = job["id"]
            self.persist(job)
            threading.Thread(target=self.execute, args=(job,), daemon=True).start()
            return dict(job)

    def persist(self, job):
        (Path(job["evidence_path"]) / "job.json").write_text(json.dumps(job, indent=2) + "\n")

    def guest_command(self, job):
        action = job["action"]
        if action not in ACTION_METADATA:
            raise ValueError("Unknown action")
        family = action_family(action)
        case = CHILD_ACTIONS[action][1] if action in CHILD_ACTIONS else None
        remote = "/var/tmp/apollo-dashboard-" + job["id"]
        platform = "qbox" if self.backend != "qemu" else "tcg"
        argv = [sys.executable, str(ROOT / "scripts/autosd_demo/guest_exec.py"),
                "--port", str(self.ssh_port), "--out", job["evidence_path"] + "/guest",
                "--timeout", str(self.operation_timeout(action))]
        uploads = []
        downloads = []
        if action == "health":
            uploads = [(ROOT / "autosd/customization/check-guest.sh", remote + "-check.sh")]
            command = "bash " + remote + "-check.sh"
            if job.get("automatic"):
                command = ("deadline=$((SECONDS+180)); until " + command + "; do "
                           "if (( SECONDS >= deadline )); then echo '[boot-health] readiness deadline exceeded'; exit 1; fi; "
                           "echo '[boot-health] services initializing; retry in 5 seconds'; sleep 5; done")
                command = "bash -c " + shlex.quote(command)
        elif family == "mixed-criticality":
            uploads = [(ROOT / "autosd/customization/mixed-criticality-guest.py", remote + "-mixed.py")]
            command = "python3 " + remote + "-mixed.py --allow-disruptive-demo --out " + remote
            if case:
                command += " --case " + case
            downloads = [(remote + "/results.json", "scenarios.json")]
        elif family == "automotive":
            # Upload unique filenames, then move into an exclusively created suite directory.
            files = ("demo-guest.py", "check-guest.sh", "fault-guest.sh")
            uploads = [(ROOT / "autosd/customization" / name, remote + "-" + name) for name in files]
            command = "set -e; mkdir " + remote + "; " + "; ".join(
                "mv " + remote + "-" + name + " " + remote + "/" + name for name in files)
            command += "; cd " + remote + "; python3 demo-guest.py --allow-disruptive-demo --out evidence"
            if case:
                command += " --case " + case
            downloads = [(remote + "/evidence/results.json", "scenarios.json")]
        elif family == "rt":
            uploads = [(ROOT / "autosd/customization/rt/experiment.py", remote + "-experiment.py")]
            command = "python3 " + remote + "-experiment.py --allow-private-guest --platform " + platform + " --duration 5 --threshold-us 5000 --external-tools --out " + remote
            if case:
                command += " --case " + case
            downloads = [(remote + "/results.json", "results.json")]
        elif action in ("timerlat", "osnoise"):
            uploads = [(ROOT / "autosd/customization/rt/trace-guest.py", remote + "-trace.py")]
            command = "set -e; mountpoint -q /sys/kernel/tracing || mount -t tracefs tracefs /sys/kernel/tracing; python3 " + remote + "-trace.py --allow-private-guest --platform " + platform + " --duration 5 --threshold-us 5000 --mode " + action + " --out " + remote
            downloads = [(remote + "/result.json", "trace-result.json"), (remote + "/rtla.log", "rtla.log")]
        elif action == "shutdown":
            command = "systemctl poweroff --no-block"
        elif action == "reboot":
            command = "systemctl reboot --no-block"
        else:
            raise ValueError("Not a guest operation")
        if family in ("automotive", "rt", "timerlat", "osnoise", "mixed-criticality"):
            # Retain every per-case log/trace, including failed cases, without rewriting exit status.
            command = "( " + command + " ); rc=$?; if test -d " + remote + "; then python3 -m tarfile -c " + remote + ".tar.gz " + remote + "; fi; exit $rc"
            downloads.insert(0, (remote + ".tar.gz", "evidence.tar.gz"))
        argv += ["--command", command]
        for source, dest in uploads:
            argv += ["--upload", str(source) + ":" + dest]
        for source, dest in downloads:
            argv += ["--download", source + ":" + dest]
        return argv

    def control_monitor(self, action, log):
        """Use only the owned launcher's existing HMP channel, never arbitrary commands."""
        if self.unsupported_control(action):
            raise ValueError(self.unsupported_control(action))
        if action not in ("pause", "resume") or not self.running():
            raise ValueError("No owned VM or invalid monitor control")
        if self.backend == "qbox-full":
            collector = self.simulator.collector
            if collector is None or collector.run_id != self.vm_job:
                raise ValueError("Current owned QBox collector unavailable")
            from qbox_control import control
            result = control(collector, action)
            if result.get("status") == "PASS":
                self.vm_paused = action == "pause"
                self.qbox_pause_unknown_run = None
            else:
                # An uncertain pause OR resume may have left simulation stopped.
                # Block guest jobs and expose only explicit current-run Resume.
                self.vm_paused = True
                self.qbox_pause_unknown_run = self.vm_job
                self.qbox_pause_run = None
            log.write(("[qbox] " + action + " " + result.get("status", "UNKNOWN") + "\n").encode())
            return result
        boot = next(j for j in self.jobs if j["id"] == self.vm_job)
        directory = Path(boot["evidence_path"]) / "vm"
        output = directory / "qemu-monitor.log"
        source = directory / "qemu-monitor.in"
        if not output.is_file() or not source.is_file() or source.is_symlink() or output.is_symlink():
            raise ValueError("Owned QEMU monitor is not ready")
        offset = output.stat().st_size
        command = "stop" if action == "pause" else "cont"
        with source.open("ab", buffering=0) as stream:
            stream.write((command + "\ninfo status\n").encode())
        log.write(f"[qemu] {command}; awaiting info status\n".encode())
        expected = b"VM status: paused" if action == "pause" else b"VM status: running"
        deadline = time.monotonic() + 10
        while time.monotonic() < deadline and self.running():
            with output.open("rb") as stream:
                stream.seek(offset)
                data = stream.read(65536)
            if expected in data:
                log.write(data)
                self.vm_paused = action == "pause"
                return {"status": "PASS", "qemu_status": "paused" if self.vm_paused else "running"}
            time.sleep(.1)
        raise RuntimeError("QEMU state not confirmed; inspect qemu-monitor.log")

    def execute(self, job):
        directory = Path(job["evidence_path"])
        action = job["action"]
        code = 1
        try:
            with (self.simulator.io_lock if action in MEASUREMENT_ACTIONS | CONTROL_BARRIERS else nullcontext()), (self.telemetry_lock if action in MEASUREMENT_ACTIONS | CONTROL_BARRIERS else nullcontext()), (directory / "console.log").open("wb", buffering=0) as log:
                if action == "boot":
                    argv = self.boot_command(directory)
                    process = subprocess.Popen(argv, cwd=ROOT, stdout=log, stderr=subprocess.STDOUT,
                                               start_new_session=True)
                    with self.lock:
                        self.vm_process, self.vm_job = process, job["id"]
                        self.vm_paused = False
                        self.active = None
                    code = process.wait()
                elif action in ("pause", "resume"):
                    job["result"] = self.control_monitor(action, log)
                    code = 0 if job["result"].get("status") != "UNKNOWN" else 1
                    self.monitoring = dict(self.monitoring, status="PAUSED" if self.vm_paused else "STALE")
                elif action_family(action) == "watchdog":
                    from watchdog_scenarios import run
                    job["result"] = run(self, job, log)
                    code = 0 if job["result"]["status"] == "PASS" else 1
                elif action == "monitor-mhu":
                    from monitor_scenarios import run
                    job["result"] = run(self, job, log)
                    code = 0 if job["result"]["status"] == "PASS" else 1
                elif action == "monitor-qualify":
                    from qbox_control import run
                    job["result"] = run(self, job, log)
                    code = 0 if job["result"]["status"] == "PASS" else 1
                    if job["result"].get("pause_state_unknown"):
                        self.qbox_pause_unknown_run = self.vm_job
                        self.qbox_pause_run = None
                        self.vm_paused = True
                else:
                    if action == "reboot":
                        from telemetry import collect
                        before = collect(self.ssh_port)
                        previous_domains = self.domain_boot()
                        if before.get("status") != "ONLINE" or not before.get("boot_id"):
                            raise RuntimeError("Cannot verify current guest boot ID; reboot not issued")
                        self.monitoring = dict(self.monitoring, status="REBOOTING")
                        log.write(f"[reboot] previous boot_id={before['boot_id']}\n".encode())
                        with self.lock:
                            boot = next(j for j in self.jobs if j["id"] == self.vm_job)
                            uart = Path(boot["evidence_path"]) / "vm/linux-uart.log"
                            self.guest_log_offset = uart.stat().st_size if uart.is_file() else 0
                            self.log_session = job["id"]
                            job["log_session"] = self.log_session
                            self.persist(job)
                    process = subprocess.Popen(self.guest_command(job), cwd=ROOT, stdout=log,
                                               stderr=subprocess.STDOUT, start_new_session=True)
                    try:
                        code = process.wait(timeout=self.operation_timeout(action) + 50)
                    except subprocess.TimeoutExpired:
                        process.terminate()
                        try:
                            process.wait(timeout=5)
                        except subprocess.TimeoutExpired:
                            process.kill()
                            process.wait()
                        code = 124
                    for name in ("results.json", "scenarios.json", "trace-result.json", "result.json"):
                        result = read_json(directory / "guest" / name)
                        if result is not None:
                            job["result"] = result
                            break
                    if action == "shutdown":
                        try:
                            vm_code = self.vm_process.wait(timeout=self.shutdown_wait_timeout())
                            boot = next(j for j in self.jobs if j["id"] == self.vm_job)
                            uart = Path(boot["evidence_path"]) / "vm/linux-uart.log"
                            powered_down = uart.is_file() and "reboot: Power down" in uart.read_text(errors="replace")
                            job["shutdown_evidence"] = {"vm_returncode": vm_code, "uart_power_down": powered_down}
                            code = 0 if vm_code == 0 and powered_down else 1
                            if code == 0:
                                # A later Power on must retain the user's disk changes.
                                self.rootfs = Path(boot["evidence_path"]) / "vm/rootfs.wic"
                        except subprocess.TimeoutExpired:
                            code = 124
                            job["error"] = "Guest did not power off; VM left running, no forced kill"
                    elif action == "reboot":
                        deadline = time.monotonic() + self.boot_timeout
                        code = 124
                        while time.monotonic() < deadline and self.running():
                            after = collect(self.ssh_port)
                            if self.reboot_verified(before, after, previous_domains):
                                self.monitoring = after
                                job["result"] = {"status": "PASS", "before_boot_id": before["boot_id"],
                                                 "after_boot_id": after["boot_id"],
                                                 "note": "OS reboot observed; automatic Automotive health follows"}
                                if self.backend == "qbox-full":
                                    job["result"]["domains"] = self.domain_boot()
                                log.write((json.dumps(job["result"]) + "\n").encode())
                                code = 0
                                break
                            log.write(b"[reboot] Waiting for a new guest boot ID, SSH and current firmware/provision readiness\n")
                            time.sleep(3)
        except Exception as error:
            job["error"] = str(error)
            with (directory / "console.log").open("a") as log:
                log.write(str(error) + "\n")
        finally:
            with self.lock:
                job.update(returncode=code, finished_at=now(), status=
                           "BOOT_PROCESS_COMPLETED" if action == "boot" and code == 0 else
                           "BLOCKED" if code == 1 and action_family(action) == "automotive"
                           and isinstance(job.get("result"), list) and job["result"]
                           and isinstance(job["result"][-1], dict)
                           and job["result"][-1].get("status") == "BLOCKED" else
                           "UNSUPPORTED" if code == 77 or (isinstance(job.get("result"), dict)
                                                           and job["result"].get("status") == "UNSUPPORTED") else
                           job["result"]["status"] if action in ("monitor-mhu", "monitor-qualify", "pause", "resume") and
                           isinstance(job.get("result"), dict) and
                           job["result"].get("status") in ("UNKNOWN", "UNCONFIRMED") else
                           "EXCEEDED" if action_family(action) == "rt" and code == 2 else
                           "PASS" if code == 0 else "TIMEOUT" if code == 124 else "FAIL")
                if self.active == job["id"]:
                    self.active = None
                if job.get("feature_session") and job["feature_session"] == self.feature_session:
                    if action in ("reboot", "watchdog-wd04", "monitor-mhu", "monitor-qualify"):
                        if code == 0 or (action == "monitor-mhu" and isinstance(job.get("result"), dict)
                                        and job["result"].get("after_boot_id")
                                        and not job["result"].get("recovery_required", True)):
                            self.boot_ready(job["feature_session"], job["result"]["after_boot_id"])
                        else:
                            self.boot_failed(job["status"], job.get("error", "Reboot verification failed"))
                    elif action == "boot" and self.feature_boot and self.feature_boot["status"] == "RUNNING":
                        self.boot_failed("FAIL", "VM exited before guest boot readiness")
                    elif action == "boot" and self.auto_health_pending:
                        self.feature_health.update(status="BLOCKED", phase="VM 종료: 자동 검사 미실행")
                        self.auto_health_pending = False
                self.persist(job)

            if action != 'boot':
                try:
                    evidence = self.simulator.finish_evidence(job)
                    (directory / 'simulator-result.json').write_text(json.dumps(evidence) + '\n')
                except OSError:
                    pass

    def boot_failed(self, status, reason):
        """Caller holds lock; historical jobs remain unchanged."""
        if self.feature_boot:
            self.feature_boot.update(status=status, phase=reason, finished_at=now())
        if self.feature_health:
            self.feature_health.update(status="BLOCKED", phase="부팅 확인 실패: 자동 검사 미실행")
        self.auto_health_pending = False
        self.boot_deadline = None

    def boot_ready(self, session, boot_id):
        """Only call for a fresh owned-VM sample or verified reboot-ID transition."""
        if session != self.feature_session or not self.feature_boot or self.feature_boot["status"] != "RUNNING":
            return
        if self.backend == "qbox-full":
            domains = self.domain_boot()
            if not self.running() or domains["status"] != "PASS":
                self.feature_boot["phase"] = "RSE / SI CL0 / SI CL1 / AP firmware 부팅 확인 중"
                return
        self.feature_boot.update(status="PASS", phase="Guest boot ID / SSH 확인 완료",
                                 finished_at=now(), result={"boot_id": boot_id})
        self.boot_deadline = None

    def advance_features(self, session, sample=None):
        """Advance one epoch atomically; stale telemetry never completes a new boot."""
        with self.lock:
            if session != self.feature_session or not self.auto_health_pending:
                return
            if any(j.get("id") == self.active and j.get("action") in ("reboot", "watchdog-wd04", "monitor-mhu", "monitor-qualify") for j in self.jobs):
                # Only the reboot worker can validate the pre/post boot ID
                # and firmware epoch; background telemetry cannot bypass it.
                return
            if self.boot_deadline and time.monotonic() >= self.boot_deadline:
                self.boot_failed("TIMEOUT", f"Guest boot readiness deadline exceeded ({self.boot_timeout}s)")
                return
            if self.backend == "qbox-full" and self.domain_boot()["status"] == "FAIL":
                self.boot_failed("FAIL", "Full-system firmware domain boot failed")
                return
            if sample and sample.get("status") == "ONLINE" and sample.get("boot_id") and self.running():
                self.boot_ready(session, sample["boot_id"])
            if self.feature_boot["status"] == "PASS" and not self.active and not self.vm_paused and self.running():
                # start reserves active before starting its worker; only this epoch
                # may schedule the one automatic check, even with concurrent polls.
                self.start("health", automatic=True)
                self.auto_health_pending = False

    def monitor(self):
        from telemetry import collect
        while not self.monitor_stop.is_set():
            sample = None
            with self.lock:
                busy = next((j for j in self.jobs if j["id"] == self.active), {})
                paused = busy.get("action") in MEASUREMENT_ACTIONS | CONTROL_BARRIERS or self.vm_paused
                running = self.running()
                feature_session = self.feature_session
            if paused:
                self.monitoring = dict(self.monitoring, status="PAUSED" if self.vm_paused else
                                       "REBOOTING" if busy.get("action") == "reboot" else
                                       "CONTROL_IN_PROGRESS" if busy.get("action") in CONTROL_BARRIERS else
                                       "PAUSED_DURING_MEASUREMENT")
            elif running:
                try:
                    with self.telemetry_lock:
                        # A benchmark may have begun while this sampler waited.
                        with self.lock:
                            busy = next((j for j in self.jobs if j["id"] == self.active), {})
                        if busy.get("action") not in MEASUREMENT_ACTIONS | CONTROL_BARRIERS and not self.vm_paused:
                            sample = collect(self.ssh_port)
                            with self.lock:
                                if feature_session == self.feature_session and self.running():
                                    self.monitoring = sample
                                else:
                                    sample = None
                except Exception as error:
                    self.monitoring = {"status": "ERROR", "error": str(error), "sampled_at": now(),
                                       "cpus": [], "subsystems": []}
            else:
                with self.lock:
                    self.mark_offline()
            self.advance_features(feature_session, sample)
            if self.session and running:
                snapshot = dict(self.monitoring, dashboard_recorded_at=now())
                with self.lock:
                    self.history.append(snapshot)
                    self.history = self.history[-120:]
                    if self.sample_count < 10000:
                        with (self.session / "telemetry.jsonl").open("a") as output:
                            output.write(json.dumps(snapshot) + "\n")
                        self.sample_count += 1
            self.monitor_stop.wait(5)

    def service_log(self, source):
        if source not in {item["id"] for item in SERVICE_LOG_SOURCES}:
            raise ValueError("Unknown guest log source")
        with self.lock:
            key = (self.log_session, source)
            cached = self.service_log_cache.get(key)
            busy = next((j for j in self.jobs if j["id"] == self.active), {})
            blocked = not self.running() or self.vm_paused or busy.get("action") in MEASUREMENT_ACTIONS | CONTROL_BARRIERS
            if not blocked and not self.service_log_inflight and (cached is None or time.monotonic() - cached[0] > 15):
                self.service_log_inflight = True
                threading.Thread(target=self.fetch_service_log, args=(key,), daemon=True).start()
            result = dict(cached[1]) if cached else {"text": "서비스 로그 수집 대기 중", "status": "WAITING"}
            result.update(log_session=self.log_session, source=source)
            if blocked:
                result["status"] = "PAUSED" if self.vm_paused else "DEFERRED" if self.running() else "OFFLINE"
            return result

    def fetch_service_log(self, key):
        try:
            with self.telemetry_lock:
                with self.lock:
                    busy = next((j for j in self.jobs if j["id"] == self.active), {})
                    if key[0] != self.log_session or not self.running() or self.vm_paused or busy.get("action") in MEASUREMENT_ACTIONS | CONTROL_BARRIERS:
                        return
                try:
                    result = collect_service_logs(self.ssh_port, key[1])
                except Exception as error:
                    result = {"text": str(error), "status": "ERROR", "collected_at": now()}
                with self.lock:
                    if key[0] == self.log_session:
                        self.service_log_cache = {k: v for k, v in self.service_log_cache.items() if k[0] == key[0]}
                        self.service_log_cache[key] = (time.monotonic(), result)
        finally:
            with self.lock:
                self.service_log_inflight = False

    def guest_log(self, source="uart"):
        """UART output for the current owned boot epoch, independent of host job selection."""
        with self.lock:
            if source != "uart" and (self.backend != "qbox-full" or source not in DOMAIN_LOGS):
                raise ValueError("Unknown guest log source")
            boot = next((j for j in self.jobs if j["id"] == self.vm_job), None)
            session, offset = self.log_session, self.guest_log_offset if source == "uart" else 0
        if boot is None:
            return {"text": "아직 이 서버에서 부팅한 guest가 없습니다.", "truncated": False,
                    "log_session": session}
        path = Path(boot["evidence_path"]) / "vm" / ("linux-uart.log" if source == "uart" else DOMAIN_LOGS[source])
        try:
            with path.open("rb") as stream:
                size = path.stat().st_size
                start = max(min(offset, size), size - 256 * 1024)
                stream.seek(start)
                return {"text": stream.read(256 * 1024).decode(errors="replace"),
                        "truncated": start > offset, "log_session": session}
        except FileNotFoundError:
            return {"text": "Guest UART 출력 대기 중", "truncated": False, "log_session": session}

    def log(self, identifier):
        job = next((job for job in self.jobs if job["id"] == identifier), None)
        if job is None:
            raise KeyError(identifier)
        path = Path(job["evidence_path"]) / "console.log"
        try:
            with path.open("rb") as stream:
                size = path.stat().st_size
                stream.seek(max(0, size - 256 * 1024))
                return {"text": stream.read().decode(errors="replace"), "truncated": size > 256 * 1024}
        except FileNotFoundError:
            return {"text": "", "truncated": False}

    def artifact(self, identifier, name):
        job = next((j for j in self.jobs if j["id"] == identifier), None)
        if job is None or name not in ARTIFACTS:
            raise KeyError(name)
        directory = Path(job["evidence_path"]).resolve()
        path = directory / name if name in ("job.json", "console.log", "qualification.json") or (
            action_family(job.get("action", "")) in ("watchdog", "monitor-mhu", "monitor-qualify") and name == "scenarios.json") else directory / "guest" / name
        if path.is_symlink() or directory not in path.resolve().parents or not path.is_file():
            raise KeyError(name)
        if path.stat().st_size > 256 * 1024 * 1024:
            raise ValueError("Artifact exceeds 256 MiB web download limit; use evidence_path locally")
        return path


class Handler(BaseHTTPRequestHandler):
    server_version = "AutoSDDashboard/1"

    def send(self, status, payload, content_type="application/json", headers=None):
        data = json.dumps(payload, ensure_ascii=False).encode() if content_type == "application/json" else payload
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        for name, value in (headers or {}).items():
            self.send_header(name, value)
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Content-Security-Policy", "default-src 'self'; script-src 'self'; style-src 'self'; connect-src 'self'; frame-ancestors 'none'")
        self.end_headers()
        self.wfile.write(data)

    def safe_request(self, mutation=False):
        port = self.server.server_port
        hosts = getattr(self.server, "allowed_hosts", {"127.0.0.1:" + str(port), "localhost:" + str(port)})
        host = self.headers.get("Host", "")
        origin = self.headers.get("Origin")
        if host not in hosts or (origin is not None and origin != "http://" + host):
            self.send(403, {"error": "Only configured same-origin addresses allowed"})
            return False
        if self.headers.get("Sec-Fetch-Site") == "cross-site":
            self.send(403, {"error": "Cross-site request rejected"})
            return False
        expected = getattr(self.server, "authorization", None)
        if expected is not None and not secrets.compare_digest(
                self.headers.get("Authorization", "").encode(), expected.encode()):
            self.send(401, {"error": "Authentication required"}, headers={
                "WWW-Authenticate": 'Basic realm="AutoSD Dashboard", charset="UTF-8"'})
            return False
        if mutation and not secrets.compare_digest(self.headers.get("X-CSRF-Token", ""), self.server.app.token):
            self.send(403, {"error": "Invalid CSRF token"})
            return False
        return True

    def do_GET(self):
        if not self.safe_request():
            return
        path = urlsplit(self.path).path
        if path == "/api/state":
            self.send(200, self.server.app.state())
        elif path == "/api/simulator/snapshot":
            self.send(200, self.server.app.simulator.snapshot())
        elif path == "/api/simulator/capabilities":
            self.send(200, self.server.app.simulator.capabilities())
        elif path == "/api/simulator/objects":
            try:
                parent = parse_qs(urlsplit(self.path).query).get('parent', [''])[0]
                self.send(200, self.server.app.simulator.objects(parent))
            except (ValueError, RuntimeError) as error:
                self.send(503, {'error': str(error)})
        elif path == "/api/simulator/qmp":
            try:
                if not self.server.app.qbox_diagnostics:
                    raise RuntimeError("QMP diagnostics require server --qbox-diagnostics and a new opted-in boot")
                query = parse_qs(urlsplit(self.path).query)
                domain = query.get('domain', ['ap'])[0]
                command = query.get('command', ['query-status'])[0]
                self.send(200, self.server.app.simulator.diagnostics(domain, command))
            except (ValueError, RuntimeError) as error:
                self.send(503, {'error': str(error)})
        elif path == "/api/simulator/events":
            try:
                after = int(parse_qs(urlsplit(self.path).query).get('after', ['0'])[0])
                if after < 0:
                    raise ValueError('after must be nonnegative')
                snapshot = self.server.app.simulator.snapshot()
                events = snapshot.get('events', [])
                self.send(200, {'run_id': snapshot.get('run_id'),
                                'gap': bool(events and after and after < events[0]['seq'] - 1),
                                'events': [event for event in events if event['seq'] > after][:100]})
            except ValueError as error:
                self.send(400, {'error': str(error)})
        elif len(path.split("/")) == 6 and path.startswith("/api/jobs/") and path.split("/")[4] == "artifacts":
            try:
                file = self.server.app.artifact(path.split("/")[3], path.split("/")[5])
                with file.open("rb") as stream:
                    self.send_response(200)
                    self.send_header("Content-Type", "application/octet-stream")
                    self.send_header("Content-Disposition", 'attachment; filename="' + file.name + '"')
                    self.send_header("Content-Length", str(file.stat().st_size))
                    self.send_header("X-Content-Type-Options", "nosniff")
                    self.end_headers()
                    while data := stream.read(65536):
                        self.wfile.write(data)
            except (KeyError, OSError):
                self.send(404, {"error": "Artifact unavailable"})
            except ValueError as error:
                self.send(413, {"error": str(error)})
        elif path == "/api/guest/log":
            source = parse_qs(urlsplit(self.path).query).get("source", ["uart"])[0]
            try:
                self.send(200, self.server.app.guest_log(source) if source == "uart" or source in DOMAIN_LOGS else self.server.app.service_log(source))
            except ValueError as error:
                self.send(400, {"error": str(error)})
        elif path.startswith("/api/jobs/") and path.endswith("/log"):
            try:
                self.send(200, self.server.app.log(path.split("/")[3]))
            except KeyError:
                self.send(404, {"error": "Unknown job"})
        elif path in ("/", "/index.html", "/style.css", "/app.js"):
            file = WEB / ("index.html" if path == "/" else path[1:])
            try:
                self.send(200, file.read_bytes(), mimetypes.guess_type(str(file))[0] or "application/octet-stream")
            except FileNotFoundError:
                self.send(404, {"error": "Static file missing"})
        else:
            self.send(404, {"error": "Not found"})

    def do_POST(self):
        if not self.safe_request(mutation=True):
            return
        if self.path not in ("/api/jobs", "/api/backend"):
            self.send(404, {"error": "Not found"})
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
            if not 0 < length <= 1024 or self.headers.get("Content-Type", "").split(";")[0] != "application/json":
                raise ValueError("Expected JSON body of at most 1024 bytes")
            payload = json.loads(self.rfile.read(length))
            if self.path == "/api/backend":
                if not isinstance(payload, dict) or set(payload) != {"backend"}:
                    raise ValueError("Only backend field accepted")
                self.send(200, self.server.app.select_backend(payload["backend"]))
                return
            if not isinstance(payload, dict) or set(payload) - {"action", "confirm_disruptive"}:
                raise ValueError("Only action and confirm_disruptive fields accepted")
            if not isinstance(payload.get("action"), str):
                raise ValueError("action must be a string")
            job = self.server.app.start(payload["action"], payload.get("confirm_disruptive", False))
            self.send(202, {"job": job})
        except (ValueError, OSError) as error:
            self.send(400, {"error": str(error)})


def access_password(path):
    """Create a private random credential once; never print it or accept public files."""
    path = Path(path)
    try:
        fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
    except FileExistsError:
        pass
    else:
        with os.fdopen(fd, "w") as stream:
            stream.write(secrets.token_urlsafe(24) + "\n")
    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
    with os.fdopen(fd) as stream:
        info = os.fstat(stream.fileno())
        if not stat.S_ISREG(info.st_mode):
            raise ValueError("Password file must be a regular file")
        if info.st_uid != os.getuid() or info.st_mode & 0o077:
            raise ValueError("Password file must be owned by current user with mode 0600")
        password = stream.read(4096).strip()
    if not 20 <= len(password) <= 256 or any(c.isspace() for c in password):
        raise ValueError("Password must contain 20..256 non-whitespace characters")
    return password


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--listen", action="append", metavar="IPV4",
                        help="Exact local IPv4 address; repeat for LAN and loopback (default 127.0.0.1)")
    parser.add_argument("--password-file", type=Path,
                        help="Optional private password file for user autosd; generated if absent")
    parser.add_argument("--allow-unauthenticated-lan", action="store_true",
                        help="Explicitly permit LAN users to control demos without login (trusted LAN only)")
    parser.add_argument("--ssh-port", type=int, default=2244)
    parser.add_argument("--backend", choices=tuple(BACKENDS), default="qemu",
                        help="Initial managed backend (default qemu); selectable while powered off")
    parser.add_argument("--manifest", type=Path)
    parser.add_argument("--base-dir", type=Path, default=ROOT / "build/autosd",
                        help="Dashboard evidence and private run disks directory")
    parser.add_argument("--rootfs", type=Path)
    parser.add_argument("--allow-private-guest", action="store_true")
    parser.add_argument("--runtime-injection", action="store_true",
                        help="opt in to QBox full MHU fault and whole-system reset scenario")
    parser.add_argument("--qbox-diagnostics", action="store_true",
                        help="enable per-domain QMP on new QBox boots")
    args = parser.parse_args()
    try:
        addresses = list(dict.fromkeys(str(ipaddress.IPv4Address(value)) for value in (args.listen or ["127.0.0.1"])))
        if "0.0.0.0" in addresses:
            raise ValueError("Specify exact interface addresses instead of 0.0.0.0")
        if (any(not ipaddress.ip_address(ip).is_loopback for ip in addresses)
                and not args.password_file and not args.allow_unauthenticated_lan):
            raise ValueError("LAN listeners require --password-file or explicit --allow-unauthenticated-lan")
        password = access_password(args.password_file) if args.password_file else None
    except (ValueError, OSError) as error:
        parser.error(str(error))
    if not 1024 <= args.port <= 65535 or not 1024 <= args.ssh_port <= 65535 or args.port == args.ssh_port:
        parser.error("Use distinct non-privileged HTTP and SSH ports")
    if bool(args.manifest) != bool(args.rootfs):
        parser.error("--manifest and --rootfs must be specified together")
    if args.manifest:
        args.manifest, args.rootfs = args.manifest.resolve(), args.rootfs.resolve()
        if not args.manifest.is_file() or not args.rootfs.is_file():
            parser.error("Manifest and rootfs must exist")
        manifest = read_json(args.manifest)
        if not isinstance(manifest, dict) or manifest.get("mode") != "regular":
            parser.error("Managed demos require a prepared regular AutoSD manifest")
    app = Dashboard(args.base_dir, args.manifest, args.rootfs, args.ssh_port, args.allow_private_guest, args.backend,
                    args.runtime_injection, args.qbox_diagnostics)
    servers = []
    hosts = {ip + ":" + str(args.port) for ip in addresses}
    if "127.0.0.1" in addresses:
        hosts.add("localhost:" + str(args.port))
    try:
        for address in addresses:
            server = ThreadingHTTPServer((address, args.port), Handler)
            server.app = app
            server.allowed_hosts = hosts
            server.authorization = ("Basic " + base64.b64encode(("autosd:" + password).encode()).decode()) if password else None
            servers.append(server)
    except OSError:
        for server in servers:
            server.server_close()
        raise
    threading.Thread(target=app.monitor, daemon=True).start()
    threading.Thread(target=app.simulator.run, daemon=True).start()
    for server in servers:
        threading.Thread(target=server.serve_forever, daemon=True).start()
        print("AutoSD dashboard: http://" + server.server_address[0] + ":" + str(args.port), flush=True)
    if password:
        print("Login user: autosd; password file: " + str(args.password_file), flush=True)
        print("HTTP does not encrypt credentials; use only a trusted LAN or TLS/SSH tunnel.", flush=True)
    elif args.allow_unauthenticated_lan:
        print("WARNING: No login required. Reachable LAN users can control the VM and demos.", flush=True)
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Server stopped. Owned guest is NOT force-killed; use dashboard shutdown before exit.", flush=True)
    finally:
        app.monitor_stop.set()
        for server in servers:
            server.shutdown()
            server.server_close()


if __name__ == "__main__":
    main()
