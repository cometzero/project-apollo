"""Check preinstalled full-system services without modifying a guest image."""
import json
from pathlib import Path
import shlex
import sys
import time

import paramiko

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'autosd_demo'))
from guest_exec import bounded_request, remaining


def command(plan):
    commands = ['set -eu', 'cat /proc/sys/kernel/random/boot_id',
                'test "$(uname -r)" = ' + shlex.quote(plan['kernel_release']),
                'test "$(getenforce)" = Enforcing',
                'rpm -q kernel-apollo apollo-pfdi',
                'test -d /sys/module/arm_si_rproc', 'test -d /sys/module/rpmsg_net',
                'test -d /sys/module/pfdi_misc', 'test -e /sys/class/net/ethsi1',
                'systemctl is-active apollo-pfdi.service',
                '/usr/libexec/apollo-pfdi-check',
                'podman exec qm systemctl --failed --no-pager',
                'podman exec qm systemctl is-system-running',
                'podman exec qm systemctl is-active multi-user.target']
    if plan['profile'] == 'automotive':
        commands += ['/usr/libexec/apollo/check-automotive.sh']
    return '; '.join(commands)


def verify(plan, out):
    result = {'status': 'FAIL', 'kind': 'preinstalled-readiness', 'mutates_image': False}
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        deadline = time.monotonic() + 360
        connect_deadline = deadline - 180
        while True:
            try:
                timeout = remaining(connect_deadline, 5)
                client.connect('127.0.0.1', port=plan['ssh_port'], username='root', password='password',
                               look_for_keys=False, allow_agent=False, timeout=timeout,
                               banner_timeout=timeout, auth_timeout=timeout)
                channel = client.get_transport().open_session(timeout=remaining(connect_deadline, 5))
                channel.set_combine_stderr(True)
                break
            except (OSError, paramiko.SSHException):
                client.close()
                if time.monotonic() >= connect_deadline:
                    raise
                time.sleep(remaining(connect_deadline, 2))
        # Nested Podman health checks can exceed 30 seconds on QBox.
        probe = 'sh -c ' + shlex.quote(command(plan))
        retry = 'while ! ' + probe + '; do echo READINESS_RETRY; sleep 3; done'
        bounded_request(channel, deadline, 30,
                        lambda: channel.exec_command('timeout 180 sh -c ' + shlex.quote(retry)))
        with (out / 'modules.log').open('wb') as log:
            while time.monotonic() < deadline:
                if channel.recv_ready():
                    log.write(channel.recv(65536))
                    log.flush()
                elif channel.exit_status_ready():
                    result['returncode'] = channel.recv_exit_status()
                    result['status'] = 'PASS' if result['returncode'] == 0 else 'FAIL'
                    break
                else:
                    time.sleep(.1)
            else:
                channel.close()
                raise TimeoutError('Readiness command timed out')
    except Exception as error:
        result['error'] = str(error)
    finally:
        client.close()
        (out / 'modules.json').write_text(json.dumps(result, indent=2) + '\n')
    return result
