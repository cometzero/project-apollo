"""Bounded read-only service logs from the dashboard-owned loopback guest.

The caller schedules collection outside HTTP handlers and serializes it with
telemetry/RT experiments. These are journal/container snapshots, not UART logs.
"""
from datetime import datetime, timezone
import shlex
import time

import paramiko

MAX_OUTPUT = 128 * 1024
COMMAND_TIMEOUT = 15
SOURCES = [
    {"id": "root", "title": "Root services", "description": "Root OS 서비스 및 QM 시작 journal"},
    {"id": "safety", "title": "Safety monitor", "description": "Root safety monitor journal"},
    {"id": "bluechi", "title": "BlueChi", "description": "Root controller/agent journal"},
    {"id": "adas", "title": "ADAS app", "description": "journal + stdout + heartbeat 파일 snapshot (로그 아님)"},
    {"id": "qm", "title": "QM system", "description": "QM 내부 현재 부팅 journal"},
    {"id": "qm-app", "title": "QM app", "description": "QM app journal 및 heartbeat 파일 읽기"},
    {"id": "qm-container", "title": "QM container", "description": "journal + stdout + heartbeat 파일 snapshot (로그 아님)"},
]

JOURNAL = "journalctl -b --no-pager -n 80 -o short-iso"


def heartbeat_command(container, nested=False):
    # Workload images are FROM scratch: they have no shell, cat, or tail.
    # Read their actual init PID's root from the owning Podman namespace.
    script = ("printf '%s\\n' '[heartbeat file snapshot; not application stdout]'; "
              "pid=$(podman inspect --format '{{.State.Pid}}' " + container + ") || exit; "
              'case "$pid" in ""|0|*[!0-9]*) printf \'%s\\n\' \'No running container PID\' >&2; exit 1;; esac; '
              'tail -c 4096 "/proc/$pid/root/run/heartbeat"')
    return ("podman exec qm " if nested else "") + "sh -c " + shlex.quote(script)


COMMANDS = {
    "root": (JOURNAL + " -u apollo-safety-monitor -u apollo-adas -u qm"
             " -u bluechi-controller -u bluechi-agent",),
    "safety": (JOURNAL + " -u apollo-safety-monitor",),
    "bluechi": (JOURNAL + " -u bluechi-controller -u bluechi-agent",),
    "adas": (JOURNAL + " -u apollo-adas", "podman logs --tail 80 apollo-adas",
             heartbeat_command("apollo-adas")),
    "qm": ("podman exec qm " + JOURNAL,),
    "qm-app": ("podman exec qm " + JOURNAL + " -u apollo-qm-app",
               "podman exec qm tail -c 4096 /run/apollo-qm/heartbeat"),
    "qm-container": ("podman exec qm podman logs --tail 80 apollo-qm-container",
                     "podman exec qm " + JOURNAL + " -u apollo-qm-container",
                     heartbeat_command("apollo-qm-container", nested=True)),
}


def command_for(source):
    """Only fixed read-only commands; never interpolate request parameters."""
    if not isinstance(source, str) or source not in COMMANDS:
        raise ValueError("Unknown guest log source")
    parts = ["result=0"]
    for command in COMMANDS[source]:
        parts.extend([
            "printf '%s\\n' " + shlex.quote("$ " + command),
            "output=$({ " + command + "; } 2>&1)",
            "code=$?",
            'if [ -n "$output" ]; then printf \'%s\\n\' "$output"; '
            "else printf '%s\\n' '[no output]'; fi",
            'printf \'[exit %s]\\n\' "$code"',
            'if [ "$code" -ne 0 ]; then result=1; fi',
        ])
    parts.append('exit "$result"')
    # Server-side deadline also kills a stuck podman exec after SSH disconnect.
    return "timeout -k 1s 15s sh -c " + shlex.quote("; ".join(parts))


def collect(port, source):
    """Collect one snapshot; caller must own a running, unpaused private VM."""
    command = command_for(source)  # Reject unknown sources before connecting.
    stamp = datetime.now(timezone.utc).isoformat()
    client = paramiko.SSHClient()
    # Same disposable loopback-only guest trust boundary as telemetry.py.
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    channel = None
    data = bytearray()
    status = "UNAVAILABLE"
    notice = ""
    try:
        client.connect("127.0.0.1", port=port, username="root", password="password",
                       look_for_keys=False, allow_agent=False, timeout=3,
                       banner_timeout=5, auth_timeout=5)
        channel = client.get_transport().open_session(timeout=3)
        channel.settimeout(3)
        channel.set_combine_stderr(True)
        deadline = time.monotonic() + COMMAND_TIMEOUT
        channel.exec_command(command)
        while True:
            # Check even when output never stops arriving.
            if time.monotonic() >= deadline:
                status, notice = "TIMEOUT", "[collector: 15 second command deadline exceeded]"
                break
            if channel.recv_ready():
                chunk = channel.recv(min(16384, MAX_OUTPUT - len(data) + 1))
                available = MAX_OUTPUT - len(data)
                data.extend(chunk[:available])
                if len(chunk) > available:
                    status, notice = "TRUNCATED", "[collector: output truncated at 128 KiB]"
                    break
            elif channel.exit_status_ready():
                code = channel.recv_exit_status()
                status = "OK" if code == 0 else "TIMEOUT" if code == 124 else "ERROR"
                if code:
                    notice = f"[collector: remote command exit {code}]"
                break
            else:
                time.sleep(.05)
    except Exception as error:
        status, notice = "UNAVAILABLE", f"[collector: {type(error).__name__}: {error}]"
    finally:
        if channel is not None:
            channel.close()
        client.close()
    text = data.decode("utf-8", errors="replace")
    if not text and not notice:
        text, status = "[no guest output]\n", "EMPTY"
    if notice:
        text += ("\n" if text and not text.endswith("\n") else "") + notice + "\n"
    return {"text": text, "status": status, "collected_at": stamp}
