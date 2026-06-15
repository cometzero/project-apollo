# Script Layout

The executable implementations under `scripts/` are grouped by workflow. New
automation and documentation should call the categorized paths directly.

## Directories

- `analyze/`: log, trace, and boot timing analysis helpers.
- `build/`: QBox and platform build entrypoints.
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
scripts/test/validate_qbox_fvp_rd_aspen_map.py
```

The workspace still keeps user-facing root entrypoints such as `./build.sh`,
`./local-build.sh`, and `./run_qbox.sh`.

## Cleanup Policy

Generated files such as `__pycache__/` and `*.pyc` are not source and should be
removed when found. Tracked scripts should only be deleted after a repository
search proves that they are obsolete and no longer user-facing entrypoints.
