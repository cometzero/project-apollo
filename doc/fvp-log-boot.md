# Headless FVP Boot Logs

Generated: 2026-05-28

`scripts/run_local_fvp_tmux.sh` is intended for interactive inspection of the
locally built Apollo FVP image. It starts FVP in tmux, opens one pane per known
subsystem UART, and mirrors those UARTs to log files under the selected run
directory:

```bash
scripts/run_local_fvp_tmux.sh
scripts/run_local_fvp_tmux.sh --session apollo-demo
scripts/run_local_fvp_tmux.sh --out-dir build/local-apollo-fvp/tmux-run/demo
scripts/run_local_fvp_tmux.sh --no-attach
```

Default local-build inputs:

- `build/local-apollo-fvp/deploy/apollo-fvp-local.fvpconf`
- `build/local-apollo-fvp/tmux-run/<timestamp>/`

Per-run logs for agent review:

- `fvp_stdout.log`
- `ports.tsv`
- `uarts/rse.log`
- `uarts/safety_island_cl0.log`
- `uarts/safety_island_cl1.log`
- `uarts/tf_a.log`
- `uarts/u_boot_linux.log`

The older `scripts/runfvp_tmux.sh` remains a generic runfvp tmux wrapper for
Yocto deploy configs. For agent-side validation, prefer a file-log workflow so
the result can be checked without attaching to a terminal UI.

The existing `runfvp` tool already supports headless launch with `-t none`, and
the test automation guide documents per-run boot logs under `logs/`. This
workspace also provides a thin wrapper for Codex-style runtime checks:

```bash
scripts/runfvp_log_boot.py
```

By default it uses:

- `layers/meta-arm/scripts/runfvp`
- `build/tmp_baremetal/deploy/images/apollo-fvp/baremetal-image-apollo-fvp.fvpconf`
- `build/fvp-boot-logs/apollo-fvp-<timestamp>/`

The script launches FVP without tmux or GUI terminals, captures FVP stdout, opens
telnet loggers for discovered consoles, sends `root` on the primary Linux login
prompt, and writes:

- `fvp_stdout.log`
- `<terminal>_<port>.log` for each discovered console
- `summary.txt`
- `result.json`

Default pass criteria require all Apollo boot domains:

- RSE / TF-M: BL1_1, BL2, first image slot, and AP power-on handoff
- Safety Island CL0 / SCP-firmware: SSU and framework initialization
- Safety Island CL1 / Zephyr: Zephyr banner and secondary CPU startup
- TF-A / BL31: BL2 handoff to BL31 and EL3 exit toward normal world
- Primary Compute U-Boot/Linux: U-Boot banner, kernel start, Linux version, and
  login or root shell prompt

Use `--require critical` for a faster RSE/Safety Island CL0/Linux smoke check,
or `--require none` when only port discovery and log capture are needed.

Examples:

```bash
scripts/runfvp_log_boot.py
scripts/runfvp_log_boot.py --timeout 1200
scripts/runfvp_log_boot.py --runfvp-verbose --timeout 1200
scripts/runfvp_log_boot.py --out-dir build/fvp-boot-logs/manual-check
scripts/runfvp_log_boot.py --machine fvp-rd-aspen \
  --fvpconf build/tmp_baremetal/deploy/images/fvp-rd-aspen/baremetal-image-fvp-rd-aspen.fvpconf
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

For each run, `summary.txt` includes a `boot_domains` section and `result.json`
includes a `domains` object so CI or an agent can directly report whether
`rse`, `safety_island_cl0`, `safety_island_cl1`, `tf_a`, and `u_boot_linux`
passed.
