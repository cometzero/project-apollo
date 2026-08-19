# Apollo QA validation

This directory owns the `run_test.sh` orchestration package, validation
profiles, schema data, and unit tests. Runtime tests remain in the owning
Yocto layers, while the runner resolves profiles into run-scoped OEQA
configuration below `build/tests/`.

The validation model is split into five categories:

- `basic`: one Apollo FVP boot, UART marker checks, fatal log scanning, and
  FVP cleanup.
- `functional`: basic boot followed by single-boot Apollo OEQA checks.
- `power`: opt-in FVP power, measured-boot, poweroff, and reboot checks.
- `extended`: long-running, image-mutating, or conformance validation.
- `stress`: repeated reset, reboot, PFDI, HIPC, CPU power, and soak tests.

The public entrypoint is run from the workspace root:

```bash
./run_test.sh --list
./run_test.sh --fvp --headless --test-profile ras_cpu
```

The Python package can also be invoked directly:

```bash
PYTHONPATH=qa-tests python3 -m apollo_validation.cli list --format json
```

Profile files use the JSON-compatible subset of YAML so the runner can parse
them with the Python standard library. Validate profiles against
`schema/test-profile.schema.json` before use.

`ras_cpu` validates the complete Primary Compute CPU RAS flow, including the
`rasdaemon` systemd journal check. It therefore uses the product image rather
than the BusyBox BSP initramfs:

```bash
./run_test.sh --fvp --headless --test-profile ras_cpu
```
