# Script Layout

The executable implementations under `scripts/` are grouped by workflow. New
automation and documentation should call the categorized paths directly.

## Directories

- `analyze/`: log, trace, and boot timing analysis helpers.
- `build/`: local Apollo FVP build stage entrypoints.
- `debug/`: GDB, Iris, and debug-session helpers.
- `inspect/`: source, image, firmware, and environment inspection helpers.
- `run/`: FVP and QBox runtime launchers, including tmux wrappers.
- `setup/`: bootstrap, provisioning, and debug-manifest setup helpers.
- `test/`: audit, validation, and completion-check helpers.

## Entrypoints

Top-level compatibility wrappers were removed after all in-repository callers
and guides were migrated. Use the categorized paths directly, for example:

```bash
scripts/run/run_qbox_apollo_fvp_full.py --help
scripts/test/validate_qbox_apollo_fvp_full_map.py
```

The workspace still keeps user-facing root entrypoints such as `./build.sh`,
`./local-build.sh`, and `./run_qbox.sh`.

Use `./local-build.sh qbox` for QBox target builds. The former dedicated build
shortcut wrappers were replaced by stage entrypoints under `scripts/build/`.
`local-build.sh` is the user-facing gate and calls those scripts.

Build stages can also be run directly:

```bash
scripts/build/build_qbox.sh
scripts/build/build_images.sh
scripts/build/build_zephyr.sh
```

Use `./local-build.sh package` or `scripts/package.sh` to package existing
local build outputs into a QBox-runnable local-build tree under
`build/local-apollo-fvp/package/qbox/local-build`.

## Run Scripts

`scripts/run/` intentionally keeps only runtime entrypoints that are either
user-facing, called by another live runner, or part of the active verification
contract.

| Script | Status | Reason |
| --- | --- | --- |
| `run_qbox_apollo_fvp_full_tmux.sh` | keep | User-facing tmux launcher used by `./run_qbox.sh`. |
| `run_qbox_apollo_fvp_full.py` | keep | Canonical Apollo full-system QBox runner. |
| `run_qbox_fvp_rd_aspen_rse.py` | keep | RSE-first child runner used by the full-system runner, build packaging checks, and debug helpers. |
| `run_qbox_apollo_fvp_si_cl1.py` | keep | Isolated CL1 child runner used by `run_qbox_apollo_fvp_full.py --isolated --si-mode live-cl1`. |
| `run_qbox_apollo_fvp_linux.py` | keep | Direct AP Linux guardrail still required by `scripts/test/verify_qbox_apollo_fvp_full_completion.py` and its pytest coverage. |
| `run_local_fvp_tmux.sh` | keep | Interactive local FVP launcher used by `scripts/debug/run_local_fvp_debug.sh`. |
| `runfvp_log_boot.py` | keep | Headless FVP log-capture runner used for FVP baseline and QBox comparison. |

Removed compatibility wrappers:

- `run_qbox_apollo_fvp_linux.sh`
- `run_qbox_fvp_rd_aspen_linux.py`
- `run_qbox_fvp_rd_aspen_linux.sh`
- `runfvp_tmux.sh`

Removed standalone RD-Aspen platform validators:

- `scripts/test/validate_qbox_fvp_rd_aspen_map.py`
- `scripts/test/audit_qbox_fvp_rd_aspen_coverage.py`

## Cleanup Policy

Generated files such as `__pycache__/` and `*.pyc` are not source and should be
removed when found. Tracked scripts should only be deleted after a repository
search proves that they are obsolete and no longer user-facing entrypoints.
