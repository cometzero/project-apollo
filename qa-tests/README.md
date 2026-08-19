# Apollo QA test profiles

This directory owns validation profile selection and schema data. Runtime
tests remain in the owning Yocto layers, while `run_test.sh` resolves these
profiles into run-scoped OEQA configuration below `build/tests/`.

Profile files use the JSON-compatible subset of YAML so the runner can parse
them with the Python standard library. Validate profiles against
`schema/test-profile.schema.json` before use.

`ras_cpu` validates the complete Primary Compute CPU RAS flow, including the
`rasdaemon` systemd journal check. It therefore uses the product image rather
than the BusyBox BSP initramfs:

```bash
./run_test.sh --fvp --headless --test-profile ras_cpu
```
