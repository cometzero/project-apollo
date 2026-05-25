# Headless FVP Boot Logs

Generated: 2026-05-17

`scripts/runfvp_tmux.sh` is intended for interactive user inspection. For
agent-side validation, prefer a file-log workflow so the result can be checked
without attaching to a terminal UI.

The existing `runfvp` tool already supports headless launch with `-t none`, and
the test automation guide documents per-run boot logs under `logs/`. This
workspace also provides a thin wrapper for Codex-style runtime checks:

```bash
scripts/runfvp_log_boot.py
```

By default it uses:

- `layers/meta-arm/scripts/runfvp`
- `build/tmp_baremetal/deploy/images/fvp-rd-aspen/baremetal-image-fvp-rd-aspen.fvpconf`
- `build/fvp-boot-logs/<timestamp>/`

The script launches FVP without tmux or GUI terminals, captures FVP stdout, opens
telnet loggers for discovered consoles, sends `root` on the primary Linux login
prompt, and writes:

- `fvp_stdout.log`
- `<terminal>_<port>.log` for each discovered console
- `summary.txt`
- `result.json`

Default pass criteria are the critical boot consoles:

- RSE: first image slot and AP power-on handoff
- SCP / Safety Island CL0: SSU and framework initialization
- Primary Compute Linux: kernel boot plus login or shell prompt

Use `--require all` when secure-world and Safety Island CL1 patterns must also
be mandatory, or `--require none` when only port discovery and log capture are
needed.

Examples:

```bash
scripts/runfvp_log_boot.py
scripts/runfvp_log_boot.py --timeout 1200 --require all
scripts/runfvp_log_boot.py --runfvp-verbose --timeout 1200 --require all
scripts/runfvp_log_boot.py --out-dir build/fvp-boot-logs/manual-check
scripts/runfvp_log_boot.py --runfvp-verbose \
  --post-login-command 'timeout 8s psa-iat-api-test; echo fvp_iat_rc:$?' \
  --post-login-timeout 30
```

The wrapper copies FVP writable flash outputs into the run directory by default
and passes those copy paths back to FVP. Use `--no-copy-writable-flash` only when
the deploy image paths may be updated in place.

Use `--runfvp-verbose` when QBox investigation needs a fresh verbose FVP stdout
log while preserving the same non-interactive console capture flow.

Use repeated `--post-login-command` entries when an investigation needs a
file-backed FVP userspace probe after Linux login. The wrapper waits for the
root prompt, sends the commands, appends a completion marker, records the
commands in `result.json`, and treats an incomplete post-login marker as a
failed run even if the basic boot markers passed.
