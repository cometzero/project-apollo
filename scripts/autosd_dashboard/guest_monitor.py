"""Read-only guest telemetry payload, executed over the managed local SSH link."""
import json
from pathlib import Path
import subprocess
import time


def read(path):
    try:
        return Path(path).read_text().strip()
    except OSError:
        return None


def snapshot():
    cpus = {}
    for line in (read('/proc/stat') or '').splitlines():
        name, *values = line.split()
        if name.startswith('cpu') and name[3:].isdigit():
            cpus[name] = list(map(int, values[:8]))
    services = ['apollo-safety-monitor.service', 'apollo-adas.service', 'qm.service',
                'bluechi-controller.service', 'bluechi-agent.service']
    try:
        result = subprocess.run(['systemctl', 'show', *services, '--property=Id,ActiveState,SubState,ControlGroup'],
                                capture_output=True, text=True, timeout=8)
        units = [dict(line.split('=', 1) for line in block.splitlines() if '=' in line)
                 for block in result.stdout.strip().split('\n\n')]
    except (OSError, subprocess.TimeoutExpired):
        units = []
    subsystems = []
    for unit in units:
        cg = Path('/sys/fs/cgroup') / unit.get('ControlGroup', '').lstrip('/')
        values = {}
        if unit.get('ControlGroup'):
            for name in ['cpu.stat', 'memory.current', 'memory.max', 'cpuset.cpus.effective', 'cpu.pressure', 'memory.events']:
                values[name] = read(cg / name)
        subsystems.append({'id': unit.get('Id'), 'status': unit.get('ActiveState', 'UNKNOWN'),
                           'substate': unit.get('SubState'), 'metrics': values})
    # Container workloads may live in scopes outside their launcher service cgroup.
    # Read the actual init PID's cgroup, never label podman/conmon CPU as ADAS CPU.
    try:
        containers = subprocess.run(['podman', 'inspect', 'apollo-adas', 'qm'],
                                    capture_output=True, text=True, timeout=5)
        observed = set()
        for container in json.loads(containers.stdout or '[]'):
            observed.add(container.get('Name'))
            state = container.get('State', {})
            pid = int(state.get('Pid', 0))
            paths = (read(f'/proc/{pid}/cgroup') or '').splitlines() if pid > 0 else []
            path = next((line[3:] for line in paths if line.startswith('0::')), None)
            cg = Path('/sys/fs/cgroup') / path.lstrip('/') if path else None
            metrics = {name: read(cg / name) for name in ['cpu.stat', 'memory.current', 'memory.max',
                       'cpuset.cpus.effective', 'cpu.pressure', 'memory.events']} if cg else {}
            subsystems.append({'id': 'container:' + container.get('Name', 'unknown'),
                               'status': state.get('Status', 'UNKNOWN'), 'metrics': metrics,
                               'pid': pid, 'cgroup': path})
        for name in {'apollo-adas', 'qm'} - observed:
            subsystems.append({'id': 'container:' + name, 'status': 'NOT_OBSERVED', 'metrics': {}})
    except (OSError, ValueError, TypeError, subprocess.TimeoutExpired):
        subsystems.append({'id': 'containers', 'status': 'UNAVAILABLE', 'metrics': {}})
    safety = read('/run/apollo-safety/state.json')
    try:
        safety = json.loads(safety) if safety else None
    except ValueError:
        safety = None
    mem = dict(line.split(':', 1) for line in (read('/proc/meminfo') or '').splitlines() if ':' in line)
    return {'guest_monotonic': time.monotonic(), 'boot_id': read('/proc/sys/kernel/random/boot_id'),
            'cpu_ticks': cpus, 'subsystems': subsystems, 'safety': safety,
            'memory': {k: int(mem[k].split()[0]) * 1024 for k in ['MemTotal', 'MemAvailable'] if k in mem},
            'pressure': read('/proc/pressure/cpu'), 'realtime': read('/sys/kernel/realtime'),
            'unsupported': ['RSE firmware CPU', 'Safety Island CL0/CL1', 'physical power/temperature'],
            'scope': 'Guest Linux CPUs and service cgroups; not host CPU or firmware telemetry'}


if __name__ == '__main__':
    print(json.dumps(snapshot()))
