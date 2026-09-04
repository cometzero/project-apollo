# Script Layout

The executable implementations under `scripts/` are grouped by workflow.
Build the supported `apollo-qvp` images through the root Yocto entrypoint:

```bash
./yocto_build.sh --bsp
./yocto_build.sh
```

## Directories

- `analyze/`: log, trace, and boot timing analysis helpers.
- `build/`: isolated validation-build helpers; not product build entrypoints.
- `debug/`: GDB, Iris, and debug-session helpers.
- `inspect/`: source, image, firmware, and environment inspection helpers.
- `run/`: FVP and QBox runtime launchers, including tmux wrappers.
- `setup/`: bootstrap, provisioning, and debug-manifest setup helpers.
- `test/`: audit, validation, and completion-check helpers.

## Entrypoints

The supported user-facing root entrypoints are:

```text
yocto_build.sh
run_fvp.sh
run_qbox_yocto.sh
run_test.sh
```

Use categorized helpers directly only for their focused validation contracts,
for example:

```bash
scripts/test/validate_qbox_apollo_fvp_full_map.py
scripts/build/run_gic720ae_qbox_platform_tests.py --list
scripts/build/run_qemu_gic720ae_qtests.sh --list
```

## Run Scripts

`run_qbox_apollo_fvp_full.py`, its tmux wrapper, and
`qbox_apollo_runtime.py` are implementation details behind
`./run_qbox_yocto.sh`. Use the root launcher so the deployed Yocto
`.qboxconf`, provider sysroot, images, and runtime environment remain
consistent.

`runfvp_log_boot.py` is the headless FVP log-capture runner used for FVP
baseline and QBox comparison.

## Cleanup Policy

Generated files such as `__pycache__/` and `*.pyc` are not source. Tracked
scripts should only be deleted after repository search proves they are
obsolete and no longer user-facing entrypoints.
