"""Optional read-only monitor enrichment, isolated from the runtime log loop."""
from copy import deepcopy
import math
from pathlib import Path
import sys
import threading
import time

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from autosd_dashboard.qbox_monitor import QBoxMonitorCollector, process_identity
from autosd_dashboard.qbox_diagnostics import QBoxDiagnostics


class StatsMonitor:
    """Poll an already enabled monitor; snapshot() never performs I/O.

    domain_threads describes vCPU threads only, not all instance device costs.
    The monotonic timestamp belongs to the simulation-time observation, allowing
    callers to reject stale data without mistaking a cached read for a new sample.
    """

    def __init__(self, pid, monitor, interval):
        self.pid = int(pid)
        self.interval = max(.1, float(interval))
        self._stop = threading.Event()
        self._lock = threading.Lock()
        self._thread = None
        self._snapshot = {"domain_threads": {}, "sim_time": None,
                          "monotonic": None, "error": "starting"}
        endpoint = deepcopy(monitor)
        endpoint.update(owner_pid=self.pid)
        try:
            endpoint["owner_start_ticks"] = process_identity(self.pid)[1]
        except (OSError, ValueError, IndexError):
            endpoint["owner_start_ticks"] = -1
        manifest = {"run_id": f"stats-{self.pid}", "monitor": endpoint,
                    "domains": endpoint.get("domains", [])}
        self._collector = QBoxMonitorCollector(manifest, timeout=.2)
        self._diagnostics = QBoxDiagnostics(self._collector, timeout=.2)
        self._domain_threads = {}
        self._thread_identities = {}
        self._refresh_at = 0.

    def start(self):
        if self._thread is None and not self._stop.is_set():
            self._thread = threading.Thread(target=self._run,
                                            name="qbox-stats-monitor", daemon=True)
            self._thread.start()

    def snapshot(self):
        with self._lock:
            return deepcopy(self._snapshot)

    def close(self):
        self._stop.set()
        if self._thread is not None:
            # Each transport is bounded, but /proc ownership discovery can be
            # slow on a busy host. Never hold the launcher shutdown indefinitely.
            self._thread.join(timeout=1.)

    def _identity(self, tid):
        return process_identity(tid, proc_root=Path(f"/proc/{self.pid}/task"))[1]

    def _cache_valid(self):
        try:
            return all(self._identity(tid) == start
                       for tid, start in self._thread_identities.items())
        except (OSError, ValueError, IndexError):
            return False

    def _read_domains(self):
        if time.monotonic() < self._refresh_at and self._cache_valid():
            return
        # Clear before querying so failed refreshes cannot publish vanished TIDs.
        self._domain_threads = {}
        self._thread_identities = {}
        mappings, identities = {}, {}
        for domain in self._diagnostics.domains:
            if self._stop.is_set():
                return
            cpus = self._diagnostics.query(domain, "query-cpus-fast")["result"]
            if not isinstance(cpus, list) or not cpus:
                raise ValueError("QMP CPU mapping is unavailable")
            tids = set()
            for cpu in cpus:
                tid = cpu["thread-id"]
                if isinstance(tid, bool) or not isinstance(tid, int) or tid <= 0:
                    raise ValueError("invalid QMP CPU thread id")
                # Membership and start ticks protect against foreign/stale TIDs.
                identities[tid] = self._identity(tid)
                tids.add(tid)
            if any(tids.intersection(previous) for previous in mappings.values()):
                raise ValueError("QMP domains share a thread id")
            mappings[domain] = sorted(tids)
        self._domain_threads, self._thread_identities = mappings, identities
        self._refresh_at = time.monotonic() + 30.

    def _sample(self):
        result = {"domain_threads": {}, "sim_time": None,
                  "monotonic": None, "error": None}
        errors = []
        try:
            begin = time.monotonic()
            raw = self._collector._get("/sc_time")["sc_time_stamp"]
            observed = (begin + time.monotonic()) / 2
            if (isinstance(raw, bool) or not isinstance(raw, (int, float))
                    or not math.isfinite(raw) or raw < 0):
                raise ValueError("invalid simulation timestamp")
            result.update(sim_time=raw, monotonic=observed)
        except Exception as exc:
            errors.append(str(exc))
        if not self._stop.is_set():
            try:
                self._read_domains()
                result["domain_threads"] = deepcopy(self._domain_threads)
            except Exception as exc:
                errors.append(str(exc))
        result["error"] = "; ".join(errors) or None
        with self._lock:
            self._snapshot = result

    def _run(self):
        while not self._stop.is_set():
            started = time.monotonic()
            self._sample()
            self._stop.wait(max(0., self.interval - (time.monotonic() - started)))
