#!/usr/bin/env python3
"""Bounded Linux RTC suspend probe; never equate shell return with domain-off."""
import argparse
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[2]


def guest_command(state, seconds):
    # Fresh FVP with copied writable images only; no host UART wake injection.
    return (
        'echo __AP_PM_BEGIN__; cat /sys/power/state; cat /sys/power/mem_sleep; '
        'cat /proc/uptime; '
        f'if ! grep -qw {state} /sys/power/mem_sleep; then '
        'echo __AP_PM_UNSUPPORTED_STATE__; '
        'elif [ ! -w /sys/class/rtc/rtc0/wakealarm ]; then '
        'echo __AP_PM_UNSUPPORTED_RTC__; '
        'else '
        'cat /sys/class/rtc/rtc0/name; '
        'if [ -w /sys/class/rtc/rtc0/device/power/wakeup ]; then '
        'echo enabled > /sys/class/rtc/rtc0/device/power/wakeup; fi; '
        f'if echo {state} > /sys/power/mem_sleep && '
        'echo 0 > /sys/class/rtc/rtc0/wakealarm && '
        f'echo +{seconds} > /sys/class/rtc/rtc0/wakealarm; then '
        'pm_boot_id=$(cat /proc/sys/kernel/random/boot_id); pm_pid=$$; '
        'pm_context_dir=$(mktemp -d /tmp/ap-pm-context.XXXXXX); '
        'pm_context_file="$pm_context_dir/sentinel"; '
        'if [ -n "$pm_context_dir" ] && '
        'mount -t tmpfs -o size=64k tmpfs "$pm_context_dir" && '
        'dd if=/dev/urandom of="$pm_context_file" bs=4096 count=1 2>/dev/null && '
        'pm_context_sum=$(sha256sum "$pm_context_file"); then '
        'echo __AP_PM_IRQ_BEFORE__; cat /proc/interrupts; '
        'echo __AP_PM_ARMED__; cat /sys/class/rtc/rtc0/wakealarm; '
        'echo mem > /sys/power/state; pm_probe_rc=$?; '
        'echo __AP_PM_RETURN_RC__=$pm_probe_rc; cat /proc/uptime; '
        'if [ "$pm_boot_id" = "$(cat /proc/sys/kernel/random/boot_id)" ] && '
        '[ "$pm_pid" = "$$" ] && '
        '[ "$pm_context_sum" = "$(sha256sum "$pm_context_file")" ]; then '
        'echo __AP_PM_OS_CONTEXT_MATCH__; '
        'else echo __AP_PM_OS_CONTEXT_MISMATCH__; fi; '
        'sleep 1; echo __AP_PM_IRQ_AFTER__; cat /proc/interrupts; '
        'rm -f "$pm_context_file"; '
        'else echo __AP_PM_SETUP_FAILED__; fi; '
        'if [ -n "$pm_context_dir" ]; then '
        'umount "$pm_context_dir"; rmdir "$pm_context_dir"; fi; '
        'echo 0 > /sys/class/rtc/rtc0/wakealarm; '
        'else echo __AP_PM_SETUP_FAILED__; fi; fi; '
        'dmesg | tail -n 100; echo __AP_PM_END__'
    )


def classify(log, runner_ok, secure_log='', management_log='', diagnostic_shell=False):
    # Match output lines, not terminal echo of the submitted command.
    lines = {line.strip() for line in log.splitlines()}
    if any(line.startswith('ASSERT:') for line in secure_log.splitlines()):
        return 'TF_A_ASSERT'
    if 'SCMI system power domain suspend return' in secure_log:
        return 'SCMI_SUSPEND_FAILED'
    if '__AP_PM_UNSUPPORTED_STATE__' in lines:
        return 'UNSUPPORTED_SUSPEND_STATE'
    if '__AP_PM_UNSUPPORTED_RTC__' in lines:
        return 'UNSUPPORTED_RTC_WAKE'
    if '__AP_PM_SETUP_FAILED__' in lines:
        return 'SETUP_FAILED'
    if '__AP_PM_OS_CONTEXT_MISMATCH__' in lines:
        return 'OS_CONTEXT_MISMATCH'
    if ('__AP_PM_RETURN_RC__=0' in lines and '__AP_PM_END__' in lines
            and '__AP_PM_OS_CONTEXT_MATCH__' in lines
            and 'PM: suspend entry' in log and 'PM: suspend exit' in log
            and (runner_ok or diagnostic_shell)):
        return ('OS_SUSPEND_RETURN_OBSERVED' if runner_ok else
                'OS_RETURN_OBSERVED_WITH_BOOT_FAILURE')
    if '[PPU TEST] OFF timeout PWPR=' in management_log:
        return 'AP_CORE_OFF_TIMEOUT'
    if '[SYS-POW TEST] SRAM retention failed; CPU release blocked:' in management_log:
        return 'AP_SRAM_RETENTION_FAILED'
    if '[SYS-POW TEST] AP cores/clusters OFF; SYSTOP remains ON;' in management_log:
        return 'AP_COMPUTE_OFF_SYSTOP_ON_NO_OS_RESUME'
    if '[SYS-POW TEST] AP SYS0 PPU OFF observed; arming timer' in management_log:
        return 'AP_SYS0_OFF_OBSERVED_NO_OS_RESUME'
    return 'FAIL_OR_INCOMPLETE'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--state', choices=('deep', 's2idle'), required=True)
    parser.add_argument('--seconds', type=int, default=10)
    parser.add_argument('--timeout', type=int, default=900)
    parser.add_argument('--out-dir', type=Path, required=True)
    parser.add_argument('--cl1-isolated', action='store_true',
                        help='Do not require CL1 boot markers; OFF needs separate PPU evidence')
    parser.add_argument('--iris-port', type=int,
                        help='Expose Iris for a separate read-only power-state observer')
    args = parser.parse_args()
    if not 2 <= args.seconds <= 60 or not 60 <= args.timeout <= 1800:
        parser.error('seconds must be 2..60 and timeout 60..1800')
    if args.iris_port is not None and not 1024 <= args.iris_port <= 65535:
        parser.error('iris-port must be 1024..65535')
    output = args.out_dir.resolve()
    if output.exists():
        parser.error('out-dir must be new to prevent stale evidence reuse')
    command = [
        'python3', str(ROOT / 'scripts/run/runfvp_log_boot.py'),
        '--machine', 'apollo-fvp', '--fvpconf', str(ROOT /
            'build/tmp_baremetal/deploy/images/apollo-fvp/nexios-bsp-initramfs-apollo-fvp.fvpconf'),
        '--out-dir', str(output), '--timeout', str(args.timeout),
        '--require', 'critical' if args.cl1_isolated else 'all',
        '--post-login-timeout', '180',
        '--post-login-command', guest_command(args.state, args.seconds)]
    if args.cl1_isolated:
        # Keep failures in the verdict, but observe power/wake until the bounded
        # deadline instead of aborting at expected diagnostic-shell errors.
        command += ['--allow-bsp-failure-shell', '--min-runtime', str(args.timeout)]
    if args.iris_port is not None:
        command += ['--', '--iris-server', '--iris-port', str(args.iris_port)]
    completed = subprocess.run(command, cwd=ROOT, check=False)
    log_path = output / 'terminal_ns_uart0_5004.log'
    log = log_path.read_text(errors='replace') if log_path.exists() else ''
    secure_path = output / 'terminal_sec_uart_5003.log'
    secure_log = secure_path.read_text(errors='replace') if secure_path.exists() else ''
    management_path = output / 'terminal_uart_si_cluster0_5001.log'
    management_log = (management_path.read_text(errors='replace')
                      if management_path.exists() else '')
    status = classify(log, completed.returncode == 0, secure_log, management_log,
                      diagnostic_shell=args.cl1_isolated)
    output.mkdir(parents=True, exist_ok=True)
    result = {
        'status': status, 'requested_state': args.state,
        'requested_rtc_seconds': args.seconds, 'runner_exit': completed.returncode,
        'command': command, 'domain_power_off_verified': False,
        'os_context_witness_verified': status in (
            'OS_SUSPEND_RETURN_OBSERVED', 'OS_RETURN_OBSERVED_WITH_BOOT_FAILURE'),
        'si_cl1_suspend_verified': False,
        'cl1_isolation_requested': args.cl1_isolated,
        'cl1_power_off_verified': False,
        'ap_sram_mapped_2mib_fingerprint_match': (
            '[AP SRAM TEST] retained 2 MiB fingerprint match' in management_log),
        'scmi_fast_channels_resume_observed': (
            '[SCMI-PERF] Retained Fast Channels resumed' in management_log),
        'systop_on_suspend_reported': (
            '[SYS-POW TEST] AP cores/clusters OFF; SYSTOP remains ON;' in management_log),
        'limitations': ['OS suspend return alone does not prove PPU power-off or RTC wake cause.',
                        'OS witness checks boot ID, shell PID/state and a 4 KiB tmpfs hash; '
                        'it does not prove architectural CPU/device context or power loss.',
                        'No AON counter continuity evidence collected by this probe.']}
    (output / 'suspend-result.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, indent=2))
    return 0 if status == 'OS_SUSPEND_RETURN_OBSERVED' else 1


if __name__ == '__main__':
    raise SystemExit(main())
