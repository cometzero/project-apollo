#!/usr/bin/env python3
"""Read-only /proc snapshot. Optional existing managed QMP monitor enrichment."""
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import socket
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'scripts'))
from autosd_dashboard.qbox_monitor import QBoxMonitorCollector, process_identity
from autosd_dashboard.qbox_diagnostics import QBoxDiagnostics

INSTANCES = {'ap': 'platform.ap_qemu_inst', 'rse': 'platform.rse_cpu_pass.qemu_inst',
             'si-cl0': 'platform.si_cl0_qemu_inst', 'si-cl1': 'platform.si_cl1_qemu_inst'}


def collect_process(logical_id, pid, proc=Path('/proc')):
    result = dict(id=logical_id, host=socket.gethostname(), executable='UNKNOWN',
                  pid=None, ppid=None, start_time=None, status='ERROR', threads=[],
                  evidence='/proc snapshot; logical role explicitly assigned by caller',
                  binary_revision='UNKNOWN', tcg_mode='UNKNOWN', errors=[])
    try:
        parent, start = process_identity(pid, proc)
        boot = (proc / 'sys/kernel/random/boot_id').read_text().strip()
        base = proc / str(pid)
        exe = str((base / 'exe').resolve(strict=True))
        cmdline = (base / 'cmdline').read_bytes().replace(b'\0', b' ').decode(errors='replace').strip()
        threads = []
        for task in sorted((base / 'task').iterdir(), key=lambda p: int(p.name)):
            try:
                _, tstart = process_identity(int(task.name), base / 'task')
                name = (task / 'comm').read_text().strip()
                if process_identity(int(task.name), base / 'task')[1] != tstart:
                    raise ValueError('thread identity changed during collection')
                threads.append(dict(tid=int(task.name), start_time=f'{boot}:{tstart}',
                                    name=name, role='UNKNOWN', cpus=[]))
            except (OSError, ValueError, IndexError) as exc:
                result['errors'].append(f'task {task.name}: {exc}')
        if process_identity(pid, proc)[1] != start:
            raise ValueError('PID identity changed during collection')
        result.update(pid=pid, ppid=parent, start_time=f'{boot}:{start}', status='OBSERVED',
                      executable=exe, cmdline=cmdline, threads=threads)
    except (OSError, ValueError, IndexError) as exc:
        result['errors'].append(str(exc))
    return result


def enrich_qmp(process, manifest):
    """Reuse bounded allowlisted QMP queries and existing monitor ownership checks."""
    if process['status'] != 'OBSERVED':
        process['errors'].append('QMP NOT_RUN: process identity unavailable')
        return
    try:
        endpoint = manifest.get('monitor', manifest)
        start_ticks = int(process['start_time'].rsplit(':', 1)[1])
        if endpoint.get('owner_pid') != process['pid'] or endpoint.get('owner_start_ticks') != start_ticks:
            raise ValueError('QMP manifest owner does not match sampled process identity')
        wrapper = manifest if 'monitor' in manifest else {
            'run_id': 'qvp-interactive-snapshot', 'monitor': endpoint, 'domains': endpoint.get('domains', [])}
        diagnostics = QBoxDiagnostics(QBoxMonitorCollector(wrapper, timeout=.5), timeout=.5)
        if not diagnostics.domains:
            raise ValueError('QMP mappings unavailable in manifest')
        threads = {t['tid']: t for t in process['threads']}
        for domain in diagnostics.domains:
            try:
                instance = INSTANCES[domain]
                cpus = diagnostics.query(domain, 'query-cpus-fast')['result']
                if not isinstance(cpus, list) or not cpus:
                    raise ValueError('empty/invalid CPU mapping')
                mappings = []
                for cpu in cpus:
                    tid, index = cpu['thread-id'], cpu['cpu-index']
                    if type(tid) is not int or type(index) is not int or index < 0 or tid not in threads:
                        raise ValueError('invalid/foreign QMP TID or CPU index')
                    task_start = process_identity(tid, Path(f"/proc/{process['pid']}/task"))[1]
                    if int(threads[tid]['start_time'].rsplit(':', 1)[1]) != task_start:
                        raise ValueError('thread identity changed since /proc sample')
                    mappings.append((tid, dict(instance=instance, index=index, evidence='QMP query-cpus-fast')))
                for tid, mapping in mappings:
                    threads[tid]['cpus'].append(mapping)
                    threads[tid]['role'] = 'QEMU vCPU execution (QMP observed)'
            except (OSError, ValueError, KeyError, RuntimeError) as exc:
                process['errors'].append(f'QMP {domain}: {exc}')
        if process_identity(process['pid'])[1] != start_ticks:
            raise ValueError('process changed during QMP collection')
    except (OSError, ValueError, KeyError, RuntimeError) as exc:
        process['errors'].append(str(exc))
        for thread in process['threads']:
            thread.update(cpus=[], role='UNKNOWN')


def revision(relative):
    try:
        return subprocess.check_output(['git', '-C', str(ROOT / relative), 'rev-parse', 'HEAD'],
                                       text=True, stderr=subprocess.DEVNULL, timeout=2).strip()
    except (OSError, subprocess.SubprocessError):
        return 'UNKNOWN'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--process', action='append', required=True, metavar='ID=PID',
                        help='explicit logical assignment, e.g. qbox=1234 or http=5678')
    parser.add_argument('--monitor-manifest', type=Path, help='existing monitor runtime manifest; queries only')
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    assignments = {}
    try:
        for item in args.process:
            name, value = item.split('=', 1)
            pid = int(value)
            if not name or len(name) > 64 or name in assignments or pid < 1 or pid in assignments.values():
                raise ValueError('duplicate/invalid process assignment')
            assignments[name] = pid
    except ValueError as exc:
        parser.error(str(exc))
    processes = [collect_process(name, pid) for name, pid in assignments.items()]
    if args.monitor_manifest:
        qbox = next((p for p in processes if p['id'] == 'qbox'), None)
        if qbox is None:
            parser.error('--monitor-manifest requires --process qbox=PID')
        try:
            enrich_qmp(qbox, json.loads(args.monitor_manifest.read_text()))
        except (OSError, ValueError) as exc:
            qbox['errors'].append(f'QMP manifest: {exc}')
    # Recheck after all optional queries; do not publish a reused/exited PID as observed.
    for p in processes:
        if p['status'] != 'OBSERVED':
            continue
        try:
            if process_identity(p['pid'])[1] != int(p['start_time'].rsplit(':', 1)[1]):
                raise ValueError('PID reused')
        except (OSError, ValueError, IndexError) as exc:
            p.update(status='EXITED', pid=None, ppid=None, start_time=None, threads=[])
            p['errors'].append(f'Final identity check: {exc}')
    result = dict(schema_version=1, collected_at=datetime.now(timezone.utc).isoformat(),
                  processes=processes, links=[], source_revisions={
                      name: revision(name) for name in ('.', 'hsoc-stack/tools/qbox', 'hsoc-stack/tools/qbox-platform')},
                  notes=['Snapshot, not live. IPC endpoints not collected.',
                         'Binary revision / effective TCG mode UNKNOWN unless independently verified.'])
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n')
    print(f"Wrote {args.output}: " + ', '.join(f"{p['id']}={p['status']}" for p in processes))


if __name__ == '__main__':
    main()
