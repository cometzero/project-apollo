"""Owned Yocto board lifecycle and typed jobs, shared by HTTP and validation."""
from copy import deepcopy
from datetime import datetime, timezone
import json
import math
from pathlib import Path
import secrets
import signal
import subprocess
import sys
import threading
import time
import uuid

ROOT = Path(__file__).resolve().parents[2]
EVIDENCE_LIMIT = 1024 * 1024 * 1024
JOB_LIMIT = 1000
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts/run"))
from board_io import LOGS, clean, fields, load, log_page, records, save, tail
from vmcu import Vmcu, UnknownOutcome
from qbox_monitor import QBoxMonitorCollector, process_identity
from qbox_diagnostics import QBoxDiagnostics
from qbox_validation.registry import canonical_matrix_path, enabled_profile_ids, resolve_profile
from run_qbox_apollo_fvp_full import CHILD_REQUIRED_MARKERS, SI_CL0_REQUIRED_MARKERS, SI_CL1_REQUIRED_MARKERS


class BoardError(ValueError):
    def __init__(self, message, status=400):
        super().__init__(message)
        self.status = status


def utc():
    return datetime.now(timezone.utc).isoformat()


def descriptor(identifier, title, description, available, reason="", disruptive=False, mode="live", args=None):
    return {"id": identifier, "title": title, "description": description,
            "available": available, "reason": "" if available else reason,
            "disruptive": disruptive, "mode": mode, "args_schema": args or {},
            "qualified": False, "evidence_tier": "functional QVP"}


class Board:
    def __init__(self, spec_path, boot_timeout=900):
        self.spec_path = Path(spec_path).resolve()
        self.spec = load(self.spec_path)
        if not isinstance(self.spec.get("command"), list) or not self.spec["command"]:
            raise ValueError("launch spec requires resolved command")
        self.base = Path(self.spec["out_dir"]).resolve()
        self.base.mkdir(parents=True, exist_ok=True, mode=0o700)
        self.boot_timeout = boot_timeout
        self.token = secrets.token_urlsafe(32)
        self.lock = threading.RLock()
        self.operation = threading.Lock()
        self.close_event = threading.Event()
        self.run_abort = threading.Event()
        self.last_quota_check = 0
        self.proc = None
        self.proc_log = None
        self.run_id = None
        self.directory = None
        self.lifecycle = "STOPPED"
        self.error = None
        self.started = None
        self.jobs = []
        self.active_job = None
        self.request_cache = {}
        self.vmcu_status = {}
        self.domains = []
        self.boot_evidence = {}
        self.collector = None
        self.diagnostics = None
        self.monitor_error = None
        self.last_vmcu_poll = 0
        self.worker = threading.Thread(target=self.monitor, daemon=True, name="board-observer")
        self.worker.start()

    def alive(self):
        return self.proc is not None and self.proc.poll() is None

    def _generation(self):
        """Caller holds self.lock while capturing or comparing a run identity."""
        return self.run_id, self.directory, self.proc

    def command_option(self, flag, default=None):
        command = self.spec["command"]
        try:
            return command[command.index(flag) + 1]
        except (ValueError, IndexError):
            return default

    def _launch(self, profile=None):
        if self.close_event.is_set():
            raise InterruptedError("server closing; new board launch rejected")
        if self.alive():
            raise BoardError("board already running", 409)
        if self.proc_log:
            self.proc_log.close()
        self.run_abort.clear()
        identifier = datetime.now().strftime("%Y%m%d-%H%M%S-") + uuid.uuid4().hex[:8]
        directory = self.base / "runs" / identifier
        directory.mkdir(parents=True, mode=0o700)
        spec = deepcopy(self.spec)
        if profile:
            command = []
            argv = iter(spec["command"])
            for arg in argv:
                if arg in ("--keep-running-after-pass", "--foreground-runtime"):
                    continue
                if arg == "--timeout":
                    next(argv)
                    continue
                command.append(arg)
            command.extend(["--validation-profile", profile, "--timeout", "900"])
            spec["command"] = command
        spec_path = directory / "launch-spec.json"
        save(spec_path, spec)
        with self.lock:
            self.run_id, self.directory = identifier, directory
            self.lifecycle, self.error = "PREPARING", None
            self.proc = None
            self.vmcu_status, self.domains, self.boot_evidence = {}, [], {}
            self.collector, self.diagnostics = None, None
            self.started, self.last_vmcu_poll = time.monotonic(), 0
            self.profile = profile
        command = [sys.executable, str(ROOT / "scripts/run/qbox_board_session.py"),
                   "--launch-spec", str(spec_path), "--out-dir", str(directory), "--run-id", identifier]
        self.proc_log = (directory / "board-session.log").open("wb")
        try:
            proc = subprocess.Popen(command, cwd=ROOT, stdin=subprocess.DEVNULL,
                                    stdout=self.proc_log, stderr=subprocess.STDOUT, start_new_session=True)
        except BaseException as error:
            self.proc_log.close()
            with self.lock:
                self.lifecycle, self.error = "FAILED", str(error)
            raise
        with self.lock:
            self.proc, self.lifecycle = proc, "BOOTING"
        save(directory / "dashboard-run.json", {"run_id": identifier, "created_at": utc(),
             "supervisor_pid": self.proc.pid, "supervisor_start_ticks": process_identity(self.proc.pid)[1],
             "bsp": self.spec.get("bsp", False), "vmcu": self.spec.get("vmcu", False),
             "scope": "Yocto full-system", "profile": profile})
        return identifier

    def _stop(self, expected_generation=None):
        with self.lock:
            generation = self._generation()
            if expected_generation is not None and expected_generation != generation:
                return {"status": "STALE_RUN"}
            _, directory, proc = generation
            proc_log = self.proc_log
            self.lifecycle = "STOPPING"
        if proc and proc.poll() is None:
            proc.send_signal(signal.SIGTERM)
            try:
                proc.wait(timeout=45)
            except subprocess.TimeoutExpired:
                with self.lock:
                    if generation == self._generation():
                        self.lifecycle = "FAILED"
                raise RuntimeError("owned supervisor cleanup timeout; process not silently abandoned")
        if proc_log:
            proc_log.close()
            with self.lock:
                if self.proc_log is proc_log:
                    self.proc_log = None
        receipt = load(directory / "board-session.json") if directory else {}
        cleanup = receipt.get("cleanup")
        if proc and (not isinstance(cleanup, dict) or cleanup.get("status") != "PASS"):
            with self.lock:
                if generation == self._generation():
                    self.lifecycle = "FAILED"
            raise RuntimeError("board cleanup did not report PASS: " + str(receipt))
        with self.lock:
            if generation == self._generation():
                self.lifecycle = "STOPPED"
        return {"supervisor_returncode": proc.returncode if proc else None, "cleanup": receipt}

    def _wait_boot(self):
        while not self.close_event.is_set():
            if self.run_abort.is_set():
                raise RuntimeError(self.error or "run aborted")
            with self.lock:
                state, error = self.lifecycle, self.error
            if state == "RUNNING":
                return deepcopy(self.boot_evidence)
            if state in ("FAILED", "STOPPED"):
                raise RuntimeError(error or "board exited before boot readiness")
            time.sleep(.2)
        raise InterruptedError("server closing")

    def _observe_boot(self, generation=None):
        with self.lock:
            generation = generation or self._generation()
            if generation != self._generation() or self.lifecycle not in ("BOOTING", "RUNNING"):
                return False
            _, directory, _ = generation
        if directory is None:
            return False
        texts = {key: clean(tail(directory / filename)) for key, (_, filename) in LOGS.items()
                 if key in ("ap-primary", "ap-secure", "rse", "si-cl0", "si-cl1", "tc397")}
        combined = "\n".join(texts.values())
        groups = {name: {marker: marker in combined for marker in markers}
                  for name, markers in CHILD_REQUIRED_MARKERS.items()}
        groups["si-cl0"] = {marker: marker in texts["si-cl0"] for marker in SI_CL0_REQUIRED_MARKERS.values()}
        groups["si-cl1"] = {marker: marker in texts["si-cl1"] for marker in SI_CL1_REQUIRED_MARKERS.values()}
        prompt = self.command_option("--primary-login-prompt", "apollo-qvp login:")
        primary = texts["ap-primary"]
        ap_ready = ("NEXIOS_BSP_INITRAMFS_READY" in primary if self.spec.get("bsp")
                    else prompt in primary or "root@apollo-qvp" in primary)
        groups["linux"] = {"ready": ap_ready}
        if self.spec.get("vmcu"):
            groups["tc397"] = {"app": "VMCU_INIT result=PASS" in texts["tc397"]}
        failures = [name for name in ("Kernel panic - not syncing", "No working init found") if name in primary]
        ready = all(all(rows.values()) for rows in groups.values()) and not failures
        domains = [{"id": "ap", "label": "AP Linux", "status": "READY" if ap_ready else "BOOTING"},
                   {"id": "rse", "label": "RSE", "status": "READY" if all(groups["rse_boot"].values()) else "BOOTING"}]
        domains += [{"id": key, "label": key.upper(), "status": "READY" if all(groups[key].values()) else "BOOTING"}
                    for key in ("si-cl0", "si-cl1")]
        if self.spec.get("vmcu"):
            domains.append({"id": "tc397", "label": "TC397", "status": "READY" if groups["tc397"]["app"] else "BOOTING"})
        with self.lock:
            if generation != self._generation() or self.lifecycle not in ("BOOTING", "RUNNING"):
                return False
            self.domains = domains
            self.boot_evidence = {"ready": ready, "markers": groups, "failures": failures,
                                  "scope": "boot/login; post-login qualification is a separate job"}
            if self.lifecycle == "BOOTING" and ready:
                self.lifecycle = "RUNNING"
                save(directory / "dashboard-boot.json", self.boot_evidence)
        return ready

    def _observe_monitor(self, generation=None):
        with self.lock:
            generation = generation or self._generation()
            # Optional SystemC diagnostics wait for boot. Host --stats has its
            # own producer and remains available while firmware starts.
            if generation != self._generation() or self.lifecycle != "RUNNING":
                return
            run_id, directory, proc = generation
            collector = self.collector
        if directory is None or proc is None:
            return
        launch = load(directory / "board-launch.json")
        runtime = load(directory / "monitor-runtime.json")
        if collector is None:
            pid = launch.get("pid") or launch.get("qbox_pid") or runtime.get("pid")
            if not pid:
                return
            from qbox_monitor_manifest import monitor_plan
            plan = launch.get("monitor") or monitor_plan(True, int(self.spec.get("monitor_port", 18080)), directory, full=True)
            plan = deepcopy(plan)
            observed_start = process_identity(pid)[1]
            expected_start = launch.get("start_ticks", runtime.get("start_ticks", observed_start))
            if int(expected_start) != observed_start:
                raise RuntimeError("monitor owner process identity changed")
            plan.update(owner_pid=pid, owner_start_ticks=observed_start)
            for row in plan.get("domains", []):
                name = row["domain_id"].replace("-", "_")
                prefix = "platform.rse_cpu_pass" if name == "rse" else "platform"
                row["qmp_biflow"] = f"{prefix}.{name}_qmp.qmp_socket.qmp_socket_router"
            collector = QBoxMonitorCollector({"run_id": run_id, "backend": "qbox-full",
                "monitor": plan, "domains": plan["domains"], "launcher_pid": proc.pid,
                "launcher_start_ticks": process_identity(proc.pid)[1]}, evidence_dir=directory,
                interval=2, timeout=.4)
            diagnostics = QBoxDiagnostics(collector, timeout=.4)
            with self.lock:
                if generation != self._generation() or self.lifecycle not in ("BOOTING", "RUNNING"):
                    return
                self.collector, self.diagnostics = collector, diagnostics
        with self.lock:
            if generation != self._generation() or self.lifecycle not in ("BOOTING", "RUNNING"):
                return
        collector.sample()

    def operation_stopped(self):
        return self.close_event.is_set() or self.run_abort.is_set()

    def _check_quota(self, generation):
        """Stop writers at the evidence budget; never truncate another writer."""
        if time.monotonic() - self.last_quota_check < 10 or self.run_abort.is_set():
            return
        self.last_quota_check = time.monotonic()
        _, directory, proc = generation
        # Writable disk images are separately selected inputs, not log evidence.
        size = sum(path.stat().st_size for path in directory.iterdir()
                   if path.suffix in (".log", ".json", ".jsonl") and path.is_file() and not path.is_symlink())
        if size >= EVIDENCE_LIMIT:
            with self.lock:
                if generation != self._generation():
                    return
                self.error = "active run evidence limit reached (1 GiB); writers stopped, evidence preserved"
                self.lifecycle = "FAILED"
                self.run_abort.set()
                if proc and proc.poll() is None:
                    proc.send_signal(signal.SIGTERM)

    def monitor(self):
        while not self.close_event.wait(.5):
            with self.lock:
                generation = self._generation()
                _, directory, proc = generation
                lifecycle = self.lifecycle
            try:
                if directory is None or proc is None or lifecycle not in ("BOOTING", "RUNNING"):
                    continue
                if proc.poll() is None:
                    self._check_quota(generation)
                    if self.run_abort.is_set():
                        continue
                    self._observe_boot(generation)
                    with self.lock:
                        if generation != self._generation():
                            continue
                        expired = self.lifecycle == "BOOTING" and time.monotonic() - self.started > self.boot_timeout
                    if expired:
                        self._stop(expected_generation=generation)
                        with self.lock:
                            if generation == self._generation():
                                self.lifecycle, self.error = "FAILED", "boot readiness deadline exceeded"
                        continue
                    try:
                        self._observe_monitor(generation)
                    except (OSError, ValueError, RuntimeError, KeyError) as error:
                        with self.lock:
                            if generation == self._generation():
                                self.monitor_error = str(error)
                    if (self.spec.get("vmcu") and self.lifecycle == "RUNNING" and not self.active_job
                            and time.monotonic() - self.last_vmcu_poll >= 5 and self.operation.acquire(False)):
                        try:
                            with self.lock:
                                if generation != self._generation() or self.lifecycle != "RUNNING" or self.active_job:
                                    continue
                            self.last_vmcu_poll = time.monotonic()
                            value = Vmcu(directory, self.operation_stopped).status()
                            value["can"] = Vmcu(directory).telemetry() if self.spec.get("silkit") else {}
                            with self.lock:
                                if generation == self._generation():
                                    self.vmcu_status = value
                        except (OSError, ValueError, RuntimeError, TimeoutError) as error:
                            with self.lock:
                                if generation == self._generation():
                                    self.vmcu_status = {"status": "UNAVAILABLE", "error": str(error)}
                        finally:
                            self.operation.release()
                else:
                    with self.lock:
                        if generation == self._generation() and self.lifecycle in ("BOOTING", "RUNNING"):
                            self.lifecycle = "FAILED" if not getattr(self, "profile", None) else "STOPPED"
                            self.error = None if proc.returncode == 0 else f"board supervisor exited: {proc.returncode}"
            except Exception as error:
                with self.lock:
                    if generation == self._generation():
                        self.error = "observer: " + str(error)

    def stats(self):
        interval = self.spec.get("stats_interval")
        if interval is None:
            return {"enabled": False, "status": "DISABLED", "samples": [], "latest": None}
        samples = records(self.directory / "stats.jsonl")[-120:] if self.directory else []
        samples = [row for row in samples if row.get("run_id") == self.run_id]
        latest = samples[-1] if samples else None
        age = max(0, time.monotonic() - latest["sample_monotonic"]) if latest else None
        status = "WARMING_UP" if not latest else "STALE" if age > 3 * float(interval) else latest.get("status", "ONLINE")
        return {"enabled": True, "status": status, "age_s": age, "interval_s": interval,
                "samples": samples, "latest": latest, "scope": "QBox host process; 100% = one host logical CPU"}

    def catalog(self):
        running = self.lifecycle == "RUNNING" and self.alive()
        idle = not self.alive()
        mcu = running and bool(self.spec.get("vmcu"))
        can = mcu and bool(self.spec.get("silkit"))
        reason = "BSP vMCU 실행이 필요합니다" if not self.spec.get("vmcu") else "보드 부팅 완료가 필요합니다"
        rows = [descriptor("board.start", "보드 실행 시작", "선택한 Yocto 이미지로 새 run을 시작합니다", idle, "이미 실행 중입니다"),
                descriptor("board.stop", "보드 실행 정지", "소유 QBox/MCU/participant를 정리합니다", self.alive(), "실행 중인 보드가 없습니다", True),
                descriptor("board.restart", "보드 재실행", "현재 run을 정리하고 새 run으로 부팅합니다", True, disruptive=True)]
        actions = [
            ("status", "vMCU 상태 조회", "SI CL0 PFDI · Safety age · GPIO", False),
            ("ap.ping", "AP 관리 ping", "AP UART 응답; health 판정과 별개", False),
            ("safety.ping", "SI CL0 ping", "독립 Safety UART 응답", False),
            ("pmic.snapshot", "PMIC snapshot", "SI 소유 TPS6594 rail 9개 · live STAT 11개 조회", False),
            ("power.off", "AP graceful 종료", "AP core OFF; SI/RSE/MCU는 유지", True),
            ("power.on", "AP wake", "AP_OFF → RSE reload → Linux/PFDI 복귀", True),
            ("recover", "AP 복구", "SI 조정 복구 후 Linux/PFDI 정상 여부 확인", True),
            ("reset", "TC397 재시작", "MCU만 reset; SI/AP 유지 및 session 재협상", True),
            ("pfdi.fault-recover", "PFDI fault → 복구", "실제 AP agent 정지와 SI fault 관측 후 명시적 AP 복구", True),
            ("safety.loss-recover", "Safety 보고 단절 → 복구", "15초 freshness timeout 관측 후 보고 재개", True),
        ]
        for name, title, description, disruptive in actions:
            available = mcu
            why = reason
            if name == "power.on" and self.vmcu_status.get("state") != "OFF":
                available, why = False, "AP_OFF 상태에서만 wake 가능합니다"
            if name == "power.off" and self.vmcu_status.get("state") != "RUN":
                available, why = False, "PFDI RUN 상태가 필요합니다"
            rows.append(descriptor("vmcu." + name, title, description, available, why, disruptive))
        rows.extend([
            descriptor("vmcu.can.status", "CAN 상태", "M_CAN TX/RX/error/drop", can, "--sil-kit 실행이 필요합니다"),
            descriptor("vmcu.can.restart", "CAN controller 재시작", "transport 복구 후 bus-off 해제", can, "--sil-kit 실행이 필요합니다", True),
            descriptor("vmcu.can.roundtrip", "CAN classic / FD64 왕복", "실제 driver IRQ와 SIL Kit echo fixture", can and bool(self.spec.get("silkit_echo_fixture")), "--sil-kit-echo-fixture 필요", True),
            descriptor("vehicle.command", "차량 CAN 명령", "0x600/0x601 epoch·cookie·sequence 검증", can, "--sil-kit 필요", True,
                       args={"op": {"title": "차량 명령", "type": "integer", "min": 1, "max": 7, "default": 1,
                                    "enum": [1, 2, 3, 4, 5, 6, 7],
                                    "enumNames": ["상태 조회", "AP ping", "PMIC rail 조회", "PMIC STAT 조회",
                                                  "AP 복구", "AP 종료", "AP wake"]},
                             "arg": {"title": "Rail/STAT 번호 (그 외 명령은 0)",
                                     "type": "integer", "min": 0, "max": 10, "default": 0}})])
        for profile in enabled_profile_ids(canonical_matrix_path()):
            spec = resolve_profile(profile, canonical_matrix_path())
            row = descriptor("qvp." + profile, profile, f"새 run · {len(spec.expected_assertion_ids)} assertions · {spec.coverage_kind}",
                             bool(self.spec.get("bsp")), "초기 adapter는 BSP profile만 지원합니다", True, "fresh-run")
            row["coverage_kind"] = spec.coverage_kind
            rows.append(row)
        for action, title in [("autosd.automotive", "AutoSD S01–S06"), ("autosd.rt", "RT R01–R06"),
                              ("autosd.mixed-criticality", "MC01–MC03"), ("autosd.watchdog", "WD01–WD04"),
                              ("autosd.monitor-mhu", "MHU01")]:
            rows.append(descriptor(action, title, "기존 AutoSD backend에서 제공", False,
                                   "AutoSD customization/SSH adapter 필요; Yocto BSP에서 실행하지 않음"))
        rows.append(descriptor("board.pause", "Apollo QBox 일시정지", "독립 MCU/SIL Kit clock 조정 필요", False,
                               "현재 board profile에서 coherent pause 미검증"))
        for row in rows:
            evidence = next((job for job in reversed(self.jobs)
                             if job["action"] == row["id"] and job["status"] == "PASS"
                             and self.run_id is not None and job["run_id"] == self.run_id), None)
            if evidence:
                row["qualified"] = True
                row["qualification"] = {"run_id": self.run_id, "job_id": evidence["id"],
                                        "scope": "successful action in this run; functional QVP only"}
        return rows

    def state(self):
        with self.lock:
            vmcu_status = deepcopy(self.vmcu_status)
            observed = vmcu_status.get("observed_monotonic")
            vmcu_status["observation_age_s"] = (
                max(0, time.monotonic() - observed)
                if type(observed) in (int, float) and math.isfinite(observed) else None)
            return {"schema_version": 1, "run_id": self.run_id, "lifecycle": self.lifecycle,
                    "error": self.error, "bsp": bool(self.spec.get("bsp")), "vmcu": bool(self.spec.get("vmcu")),
                    "silkit": bool(self.spec.get("silkit")), "image": self.spec.get("image_basename"),
                    "csrf_token": self.token, "domains": deepcopy(self.domains),
                    "vmcu_status": vmcu_status, "stats_enabled": self.spec.get("stats_interval") is not None,
                    "stats_interval": self.spec.get("stats_interval"), "capabilities": self.catalog(),
                    "active_job": deepcopy(next((j for j in self.jobs if j["id"] == self.active_job), None)),
                    "jobs": deepcopy(self.jobs[-100:]), "elapsed_s": time.monotonic() - self.started if self.started else 0,
                    "boot_evidence": deepcopy(self.boot_evidence), "monitor_error": self.monitor_error}

    def start_job(self, payload):
        if not isinstance(payload, dict) or set(payload) - {"action", "args", "run_id", "request_id", "confirm_disruptive"}:
            raise BoardError("unknown job field")
        action = payload.get("action")
        arguments = payload.get("args", {})
        request = payload.get("request_id")
        if (not isinstance(action, str) or not isinstance(arguments, dict) or
                not isinstance(request, str) or not 1 <= len(request) <= 128):
            raise BoardError("action, args and request_id required")
        signature = json.dumps(payload, sort_keys=True)
        with self.lock:
            if request in self.request_cache:
                previous, identifier = self.request_cache[request]
                if previous != signature:
                    raise BoardError("request_id reused with different payload", 409)
                return deepcopy(next(j for j in self.jobs if j["id"] == identifier))
            if payload.get("run_id") != self.run_id:
                raise BoardError("stale run_id", 409)
            if self.active_job:
                raise BoardError("another board job is running", 409)
            if len(self.jobs) >= JOB_LIMIT and action != "board.stop":
                raise BoardError("session job limit reached; restart dashboard to begin a new session", 429)
            entry = next((x for x in self.catalog() if x["id"] == action), None)
            if entry is None or not entry["available"]:
                raise BoardError(entry["reason"] if entry else "unknown action", 422)
            if entry["disruptive"] and payload.get("confirm_disruptive") is not True:
                raise BoardError("confirm_disruptive is required")
            if set(arguments) != set(entry["args_schema"]):
                raise BoardError("unexpected or missing action arguments")
            for key, rule in entry["args_schema"].items():
                if type(arguments[key]) is not int or not rule["min"] <= arguments[key] <= rule["max"]:
                    raise BoardError("invalid argument: " + key)
            if action == "vehicle.command":
                op, arg = arguments["op"], arguments["arg"]
                if op >= 5 and not self.spec.get("silkit_allow_actuation"):
                    raise BoardError("--sil-kit-allow-actuation required", 422)
                if arg > (8 if op == 3 else 10 if op == 4 else 0):
                    raise BoardError("invalid vehicle arg for op")
            identifier = uuid.uuid4().hex
            job = {"id": identifier, "action": action, "args": arguments, "run_id": self.run_id,
                   "status": "QUEUED", "phase": "접수", "created_at": utc(), "mode": entry["mode"]}
            self.jobs.append(job)
            self.request_cache[request] = (signature, identifier)
            self.active_job = identifier
            self._persist_job(job)
            threading.Thread(target=self._run_job, args=(job,), daemon=True, name="board-job").start()
            return deepcopy(job)

    def _persist_job(self, job):
        save(self.base / "jobs" / job["id"] / "result.json", job)

    def _run_job(self, job):
        with self.operation:
            with self.lock:
                job.update(status="RUNNING", phase="실행 및 후조건 확인", started_at=utc())
            try:
                result = self._execute(job)
                job.update(status="PASS", phase="완료", result=result)
            except UnknownOutcome as error:
                job.update(status="UNKNOWN", error=str(error), recovery_required=True)
            except Exception as error:
                result = job.get("result", {})
                profile = result.get("profile") or {}
                cleanup = (result.get("session") or {}).get("cleanup") or {}
                status = profile.get("verdict") if (job["action"].startswith("qvp.")
                    and cleanup.get("status") == "PASS" and cleanup.get("residual_pids") == []) else "FAIL"
                if status not in ("BLOCKED", "UNSUPPORTED", "SKIP"):
                    status = "FAIL"
                job.update(status=status, error=str(error), recovery_required=job["action"] not in ("board.start", "vmcu.status"))
            finally:
                with self.lock:
                    job["finished_at"] = utc()
                    self._persist_job(job)
                    self.active_job = None

    def _execute(self, job):
        action = job["action"]
        if action in ("board.start", "board.restart"):
            if action == "board.restart":
                self._stop()
            self._launch()
            job["run_id"] = self.run_id
            return self._wait_boot()
        if action == "board.stop":
            return self._stop()
        if action.startswith("qvp."):
            self._stop()
            self._launch(action[4:])
            job["run_id"] = self.run_id
            deadline = time.monotonic() + 960
            while self.alive() and time.monotonic() < deadline and not self.operation_stopped():
                time.sleep(.5)
            if self.alive():
                self._stop()
                raise TimeoutError("profile deadline exceeded")
            result = load(self.directory / "result.json")
            profile = result.get("validation_profile") or result.get("validation_profile_result")
            if not profile:
                child = load(self.directory / "rd-aspen-result.json")
                profile = child.get("validation_profile_result") or child.get("post_login_probe", {}).get("validation_profile_result")
            session = load(self.directory / "board-session.json")
            cleanup = session.get("cleanup")
            job["result"] = {"runner": result, "profile": profile, "session": session}
            if (not isinstance(profile, dict) or profile.get("verdict") != "PASS"
                    or result.get("passed") is not True or result.get("verdict") != "pass"
                    or self.proc.returncode != 0 or session.get("returncode") != 0
                    or not isinstance(cleanup, dict) or cleanup.get("status") != "PASS"
                    or cleanup.get("residual_pids") != []):
                raise RuntimeError("profile, canonical runner or owned process cleanup did not pass; see raw evidence")
            return job["result"]
        vmcu = Vmcu(self.directory, self.operation_stopped)
        if action == "vmcu.status":
            self.vmcu_status = vmcu.status()
            return self.vmcu_status
        if action == "vmcu.ap.ping": return vmcu.rpc("apollo ping", "AP", 1)
        if action == "vmcu.safety.ping": return vmcu.rpc("safety ping", "SI0", 1)
        if action == "vmcu.pmic.snapshot": return vmcu.pmic()
        if action == "vmcu.power.off": result = vmcu.power_off()
        elif action == "vmcu.power.on": result = vmcu.boot_ap()
        elif action == "vmcu.recover": result = vmcu.boot_ap(recover=True)
        elif action == "vmcu.reset": result = vmcu.reset(self.proc.pid)
        elif action == "vmcu.can.status": return fields(vmcu.cli("can status", "VMCU_CAN_STATUS"))
        elif action == "vmcu.can.restart":
            receipt = vmcu.cli("can restart", r"VMCU_CAN_RESTART\b")
            if fields(receipt).get("errno") != "0":
                raise RuntimeError("CAN restart failed: " + receipt)
            status = fields(vmcu.cli("can status", r"VMCU_CAN_STATUS\b"))
            if status.get("state") != "0":
                raise RuntimeError("CAN restart did not reach ERROR_ACTIVE: " + str(status))
            return {"receipt": receipt, "status": status}
        elif action == "vmcu.can.roundtrip": return vmcu.can_roundtrip()
        elif action == "vmcu.safety.loss-recover": result = vmcu.safety_loss()
        elif action == "vmcu.pfdi.fault-recover": result = vmcu.pfdi_fault()
        elif action == "vehicle.command": result = vmcu.vehicle_command(**job["args"])
        else: raise BoardError("unimplemented action", 422)
        self.vmcu_status = vmcu.status()
        return result

    def logs(self):
        return {"sources": [{"id": key, "label": label,
                 "available": bool(self.directory and (self.directory / filename).exists())}
                for key, (label, filename) in LOGS.items()]}

    def log(self, identifier, cursor="", limit=65536):
        if not self.directory:
            raise BoardError("no run", 409)
        return log_page(self.directory, self.run_id, identifier, cursor, limit)

    def topology(self):
        from scripts.autosd_dashboard.board_topology import get_board_topology
        if not self.directory:
            raise BoardError("no launch snapshot yet", 409)
        return get_board_topology(ROOT, self.directory)

    def evidence(self):
        mapping = {"launch": "board-launch.json", "topology": "board-topology.json",
                   "boot": "dashboard-boot.json", "session": "board-session.json",
                   "stats": "stats.jsonl", "runner": "result.json"}
        rows = [{"id": key, "label": filename, "available": bool(self.directory and (self.directory / filename).is_file()),
                 "url": "/api/board/evidence/" + key} for key, filename in mapping.items()]
        return mapping, {"files": rows}

    def close(self):
        self.close_event.set()
        self.worker.join(timeout=3)
        with self.operation:
            self._stop()
