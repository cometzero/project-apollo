"""Named MHU lost-doorbell experiment with explicit full-system reset recovery."""
import http.client
import json
from pathlib import Path
import time

from qbox_monitor import MonitorError, verify_listener
from watchdog_scenarios import ROOT, boot_snapshot, run_command

MHU = "platform.host_ap_si_cl1_mhu_pbx"
RESET = "apollo.control.system-reset"


class UnknownOutcome(RuntimeError):
    pass


def request(collector, method, path, payload=None):
    """Fixed scenario transport; never retry an uncertain mutation."""
    allowed = {"/api/v1/injection/capabilities", "/api/v1/injections",
               "/api/v1/injection/targets/" + MHU,
               "/api/v1/injection/targets/" + RESET}
    if path not in allowed:
        raise ValueError("non-scenario monitor path")
    if method == "POST" and (path != "/api/v1/injections" or
            (payload.get("target"), payload.get("action")) not in
            {(MHU, "drop-next-doorbell"), (RESET, "pulse")}):
        raise ValueError("non-scenario mutation")
    # Includes managed-launcher ancestry and PID start-time verification.
    collector._get("/sc_time")
    endpoint = collector.endpoint
    verify_listener(endpoint["host"], endpoint["port"], endpoint["owner_pid"], endpoint["owner_start_ticks"])
    conn = http.client.HTTPConnection(endpoint["host"], endpoint["port"], timeout=collector.timeout)
    issued = False
    try:
        issued = True
        conn.request(method, path, body=json.dumps(payload) if payload is not None else None,
                     headers={"Content-Type": "application/json", "Connection": "close"})
        response = conn.getresponse()
        deadline = time.monotonic() + collector.timeout
        chunks, length = [], 0
        while length <= collector.max_body:
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                raise TimeoutError("scenario response deadline")
            if conn.sock:
                conn.sock.settimeout(remaining)
            chunk = response.read1(min(65536, collector.max_body + 1 - length))
            if not chunk:
                break
            chunks.append(chunk)
            length += len(chunk)
        if length > collector.max_body:
            raise ValueError("scenario response too large")
        data = json.loads(b"".join(chunks))
        if response.status not in (200, 202):
            raise MonitorError("scenario HTTP %s: %s" % (response.status, data))
        return data
    except (OSError, ValueError, http.client.HTTPException) as exc:
        if issued and method == "POST":
            raise UnknownOutcome("mutation outcome unknown; not retried: " + str(exc)) from exc
        raise MonitorError(str(exc)) from exc
    finally:
        conn.close()


def supports(capabilities, target, action):
    return any(item.get("target") == target and
               any(a.get("name") == action for a in item.get("actions", []))
               for item in capabilities.get("targets", []))


def ping_report(directory):
    try:
        with (directory / "console.log").open() as stream:
            text = stream.read(1024 * 1024)
        for line in range(len(text)):
            if text[line] == "{":
                try:
                    value, _ = json.JSONDecoder().raw_decode(text[line:])
                    if isinstance(value, dict) and isinstance(value.get("packets"), list):
                        return value
                except ValueError:
                    pass
    except OSError:
        pass
    return {}


def observed_fault(before, after, report):
    return (after.get("generation") == before.get("generation") and
            after.get("match_count", 0) > before.get("match_count", 0) and
            after.get("armed") is False and report.get("status") == "FAIL" and
            any(packet.get("status") == "TIMEOUT" for packet in report.get("packets", [])))


def all_domain_epochs_advanced(before, after):
    """Full reset evidence must not reuse retained firmware PASS markers."""
    old = {row.get("id"): row for row in before.get("domains", [])}
    new = {row.get("id"): row for row in after.get("domains", [])}
    for domain in ("rse", "si-cl0", "si-cl1", "ap"):
        left, right = old.get(domain, {}).get("boot_epoch"), new.get(domain, {}).get("boot_epoch")
        if type(left) is not int or type(right) is not int or left < 1 or right <= left:
            return False
    return True


def run(app, job, log):
    directory = Path(job["evidence_path"])
    result = {"kind": "monitor", "id": "MHU01", "status": "UNSUPPORTED",
              "recovery_required": False, "observations": {}, "scenarios": []}
    collector = getattr(app.simulator, "collector", None)
    def phase(text):
        job["phase"] = text
        app.persist(job)
        log.write(("[MHU01] " + text + "\n").encode())
        log.flush()
    try:
        if app.backend != "qbox-full" or not getattr(app, "runtime_injection", False) or collector is None:
            result["reason"] = "Requires QBox full with explicit runtime injection opt-in"
            return result
        phase("Capability · HIPC baseline 확인")
        caps = request(collector, "GET", "/api/v1/injection/capabilities")
        if not supports(caps, MHU, "drop-next-doorbell") or not supports(caps, RESET, "pulse"):
            result["reason"] = "Exact MHU/reset capabilities unavailable"
            return result
        before_boot = boot_snapshot(app, directory / "before-boot", log)
        before_domains = app.domain_boot()
        if before_boot.get("status") != "ONLINE" or before_domains.get("status") != "PASS":
            raise RuntimeError("Healthy full-system baseline unavailable")
        remote = "/var/tmp/apollo-monitor-" + str(job["id"])
        uploads = [(ROOT / "scripts/autosd_demo/check_hipc_link.sh", remote + "-hipc.sh"),
                   (ROOT / "scripts/autosd_demo/hipc_ping.py", remote + "-ping.py"),
                   (ROOT / "autosd/customization/check-guest.sh", remote + "-health.sh")]
        probe = "bash " + remote + "-hipc.sh " + remote + "-ping.py"
        health = "set -e; bash " + remote + "-health.sh; " + probe
        baseline = run_command(app, directory / "baseline", log, health, uploads, timeout=300)
        if baseline != 0 or ping_report(directory / "baseline").get("status") != "PASS":
            raise RuntimeError("Automotive/HIPC baseline failed; injection not issued")
        before = request(collector, "GET", "/api/v1/injection/targets/" + MHU)["values"]
        if before.get("armed"):
            raise RuntimeError("MHU target already has an armed fault")
        phase("AP→SI1 channel 0 doorbell 1회 drop · Guest timeout 관측")
        result["recovery_required"] = True
        result["accepted"] = request(collector, "POST", "/api/v1/injections",
            {"schema_version": 1, "target": MHU, "action": "drop-next-doorbell", "reset_domain": "ap",
             "parameters": {"channel": 0}, "expected_generation": before["generation"], "clear_on_reset": True})
        code = run_command(app, directory / "fault", log, probe, timeout=180)
        after = request(collector, "GET", "/api/v1/injection/targets/" + MHU)["values"]
        fault = code != 0 and observed_fault(before, after, ping_report(directory / "fault"))
        result["observations"].update(before=before, after_fault=after, guest_fault_returncode=code,
                                      consumed_and_guest_timeout=fault)
        phase("PBX pending 복구를 위한 RSE/SI/AP 전체 reset")
        with app.lock:
            boot = next(j for j in app.jobs if j["id"] == app.vm_job)
            uart = Path(boot["evidence_path"]) / "vm/linux-uart.log"
            app.guest_log_offset = uart.stat().st_size if uart.is_file() else 0
            app.log_session = job["id"]
            job["log_session"] = job["id"]
            app.persist(job)
        # DELETE is not recovery: the consumed PBX pending bit requires reset.
        result["reset_accepted"] = request(collector, "POST", "/api/v1/injections",
            {"schema_version": 1, "target": RESET, "action": "pulse", "reset_domain": "system",
             "parameters": {"duration_ns": 1000}, "expected_generation": after["generation"], "clear_on_reset": True})
        deadline, attempt, after_boot = time.monotonic() + app.boot_timeout, 0, {}
        while time.monotonic() < deadline and app.running():
            attempt += 1
            phase("전체 reset 이후 새 boot ID · firmware 복구 대기")
            after_boot = boot_snapshot(app, directory / ("recovery-boot-%03d" % attempt), log)
            if (app.reboot_verified(before_boot, after_boot, before_domains)
                    and all_domain_epochs_advanced(before_domains, app.domain_boot())):
                break
            time.sleep(3)
        after_domains = app.domain_boot()
        all_advanced = all_domain_epochs_advanced(before_domains, after_domains)
        recovered = app.reboot_verified(before_boot, after_boot, before_domains) and all_advanced
        if recovered:
            phase("새 Guest Automotive health · HIPC 3회 왕복 검사")
            recovered = run_command(app, directory / "recovery", log, health, uploads, timeout=300) == 0
            recovered = recovered and ping_report(directory / "recovery").get("status") == "PASS"
        final = request(collector, "GET", "/api/v1/injection/targets/" + MHU)["values"]
        recovered = recovered and final.get("armed") is False and final.get("generation", -1) > before["generation"]
        result["observations"].update(recovered=recovered, final=final, before_boot=before_boot, after_boot=after_boot,
                                      before_domains=before_domains, after_domains=after_domains,
                                      all_domain_epochs_advanced=all_advanced)
        result["recovery_required"] = not recovered
        result["after_boot_id"] = after_boot.get("boot_id") if recovered else None
        result["status"] = "PASS" if fault and recovered else ("UNCONFIRMED" if recovered else "FAIL")
    except UnknownOutcome as exc:
        result.update(status="UNKNOWN", reason=str(exc), recovery_required=True)
    except Exception as exc:
        result.update(status="FAIL", reason=str(exc))
    finally:
        result["scenarios"] = [{key: value for key, value in result.items() if key not in ("scenarios", "kind")}]
        (directory / "scenarios.json").write_text(json.dumps(result, indent=2) + "\n")
        phase("완료 · " + result["status"])
    return result
