#!/usr/bin/env python3
"""Destructive, bounded demo suite for an explicitly selected disposable guest."""
import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
import time


CASES = [
    ("S01-coldboot", "bash ./check-guest.sh"),
    ("S02-bluechi", """
bluechictl stop qm.host apollo-qm-app.service
test "$(podman exec qm systemctl is-active apollo-qm-app.service)" = inactive
podman exec apollo-adas /workload health /run/heartbeat
podman exec qm podman exec apollo-qm-container /workload health /run/heartbeat
bluechictl start qm.host apollo-qm-app.service
sleep 3
bash ./check-guest.sh
"""),
    ("S03-qm-restart", """
old=$(podman exec qm podman inspect --format '{{.Id}}' apollo-qm-container)
podman exec qm podman kill --signal KILL apollo-qm-container
for ((i=0; i<60; i++)); do
    new=$(podman exec qm podman inspect --format '{{.Id}}' apollo-qm-container 2>/dev/null || true)
    if [[ -n "$new" && "$new" != "$old" ]] && podman exec qm podman exec apollo-qm-container /workload health /run/heartbeat; then
        break
    fi
    sleep 1
done
test -n "$new"
test "$new" != "$old"
echo "QM container replaced: $old -> $new"
bash ./check-guest.sh
"""),
    ("S04-adas-fault", "bash ./fault-guest.sh"),
    ("S05-latch", """
systemctl restart apollo-safety-monitor || true
sleep 5
test "$(systemctl is-active apollo-safety-monitor)" = failed
python3 -c 'import json; assert json.load(open("/run/apollo-safety/state.json"))["state"] == "FAULT_LATCHED"'
test -z "$(podman ps -q --filter 'name=^apollo-adas$')"
podman exec qm /usr/libexec/apollo/workload health /run/apollo-qm/heartbeat
podman exec qm podman exec apollo-qm-container /workload health /run/heartbeat
"""),
    ("S06-operator-recovery", """
systemctl stop apollo-safety-monitor
cp /run/apollo-safety/state.json "$DEMO_EVIDENCE/fault-before-recovery.json"
python3 -c 'from pathlib import Path; Path("/run/apollo-safety/state.json").unlink()'
systemctl reset-failed apollo-adas apollo-safety-monitor
systemctl start apollo-adas
podman exec apollo-adas /workload health /run/heartbeat
systemctl start apollo-safety-monitor
for ((i=0; i<30; i++)); do
    if python3 -c 'import json; assert json.load(open("/run/apollo-safety/state.json"))["state"] == "HEALTHY"'; then break; fi
    sleep 1
done
bash ./check-guest.sh
"""),
]


def run_case(name, command, output, timeout):
    started = time.monotonic()
    print(f"[guest:{name}] BEGIN (timeout={timeout}s)", flush=True)
    with (output / (name + ".log")).open("w") as log:
        try:
            # Tee while the child is running; capture_output/run would hide all
            # guest output until completion. Export xtrace to nested bash checks
            # so silent assertions and bounded wait loops are visible too.
            with subprocess.Popen(
                ["timeout", "--kill-after=10", str(timeout), "bash", "-euxo", "pipefail", "-c", command],
                stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                env=os.environ | {"DEMO_EVIDENCE": str(output),
                                  "SHELLOPTS": "xtrace", "PYTHONUNBUFFERED": "1",
                                  "PS4": "+ [${BASH_SOURCE:-scenario}:${LINENO}] "},
            ) as process:
                while data := process.stdout.read1(4096):
                    text = data.decode(errors="replace")
                    log.write(text)
                    log.flush()
                    sys.stdout.write(text)
                    sys.stdout.flush()
                code = process.wait()
        except OSError as error:
            log.write(str(error) + "\n")
            print(f"[guest:{name}] ERROR: {error}", flush=True)
            code = 127
    print(f"[guest:{name}] END rc={code} elapsed={time.monotonic() - started:.3f}s", flush=True)
    return {"id": name, "status": "PASS" if code == 0 else "FAIL",
            "returncode": code, "elapsed_seconds": round(time.monotonic() - started, 3)}


def selected_cases(selection):
    return [case for case in CASES if selection == "all" or case[0].split("-")[0] == selection]


def precheck(selection, output):
    """Selected cases never run prerequisites or recover state implicitly."""
    if selection in ("S02", "S03", "S04"):
        command = "bash ./check-guest.sh"
    elif selection in ("S05", "S06"):
        command = """
python3 -c 'import json; assert json.load(open("/run/apollo-safety/state.json"))["state"] == "FAULT_LATCHED"'
test -z "$(podman ps -q --filter 'name=^apollo-adas$')"
"""
    else:
        return None
    return run_case(selection + "-precheck", command, output, 90)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--allow-disruptive-demo", action="store_true", required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--case", choices=["all"] + [f"S{i:02d}" for i in range(1, 7)], default="all")
    args = parser.parse_args()
    output = args.out.resolve()
    output.mkdir(parents=True, exist_ok=False)
    results = []
    for name, command in selected_cases(args.case):
        print(json.dumps({"event": "case-start", "id": name, "status": "RUNNING"}), flush=True)
        gate = precheck(args.case, output)
        if gate and gate["status"] != "PASS":
            result = {"id": name, "status": "BLOCKED", "returncode": 1,
                      "reason": "Required guest state is absent; no scenario mutation performed",
                      "precheck": gate}
            results.append(result)
            (output / "results.json").write_text(json.dumps(results, indent=2) + "\n")
            print(json.dumps(result | {"event": "case-complete"}), flush=True)
            return 1
        result = run_case(name, command, output, 240)
        if name == "S04-adas-fault" and args.case != "all" and result["status"] == "PASS":
            result["guest_state"] = "FAULT_LATCHED"
            result["next_step"] = "S05 latch check or explicit S06 operator recovery"
        results.append(result)
        (output / "results.json").write_text(json.dumps(results, indent=2) + "\n")
        print(json.dumps(result | {"event": "case-complete"}), flush=True)
        if result["status"] != "PASS":
            print("Stopped on failure; no implicit recovery. Inspect logs and guest state.", flush=True)
            return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
