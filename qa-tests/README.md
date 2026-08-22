# Apollo QA validation

This directory owns the `run_test.sh` orchestration package, validation
profiles, schema data, and unit tests. Runtime tests remain in the owning
Yocto layers, while the runner resolves profiles into run-scoped OEQA
configuration below `build/tests/`.

The current public profile set covers the Arm Zena CSS v2.2 run-time
integration scope except Xen. The contract is 15 non-Xen validation areas,
represented by 14 public profiles because `pfdi-si-cl1` owns both the Safety
Island CL1 PFDI flow and the Safety Island PFDI monitoring row.

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
./run_test.sh --machine apollo-fvp --bsp --test-profile bsp-core
./run_test.sh --machine apollo-fvp --test-profile trusted-services
./run_test.sh --machine apollo-qvp --bsp --test-profile bsp-core \
  --fvp-reference build/tests/<fvp-bsp-core-run>/summary.json
./run_test.sh --machine apollo-qvp --test-profile ras_cpu \
  --fvp-reference build/tests/<fvp-ras-cpu-run>/summary.json
```

The QBox backend selects `apollo-qvp`, validates the deployed `qboxconf`, and
runs the canonical Yocto QBox launcher in headless full-system mode. Add
`--bsp` to boot `nexios-bsp-initramfs`. A named QBox profile must provide
`--fvp-reference <summary.json>` from the matching FVP run. The runner rejects
missing, failed, skipped, stale, image-mismatched, CPU-count-mismatched, or
contract-drifted references before launching QBox. Basic QBox boot without a
named profile remains available through the normal QBox launcher path.

## Public Profiles

| Profile | Image | FVP command | QBox state |
| --- | --- | --- | --- |
| `bsp-core` | BSP | `./run_test.sh --machine apollo-fvp --bsp --test-profile bsp-core` | Implemented QBox BSP profile; requires matching `--fvp-reference`. |
| `si-cl1` | BSP | `./run_test.sh --machine apollo-fvp --bsp --test-profile si-cl1` | Implemented QBox BSP profile; requires matching `--fvp-reference`. |
| `smcf` | BSP | `./run_test.sh --machine apollo-fvp --bsp --test-profile smcf` | Implemented QBox BSP profile; requires matching `--fvp-reference`. |
| `pfdi` | BSP | `./run_test.sh --machine apollo-fvp --bsp --test-profile pfdi` | Implemented QBox BSP profile; requires matching `--fvp-reference`. |
| `pfdi-si-cl1` | BSP | `./run_test.sh --machine apollo-fvp --bsp --test-profile pfdi-si-cl1` | Implemented QBox BSP profile; requires matching `--fvp-reference`. |
| `safety-diagnostics-tests` | BSP | `./run_test.sh --machine apollo-fvp --bsp --test-profile safety-diagnostics-tests` | Implemented QBox BSP profile; requires matching `--fvp-reference`. |
| `cpuidle` | BSP | `./run_test.sh --machine apollo-fvp --bsp --test-profile cpuidle` | Implemented QBox BSP profile; final current-SHA runtime is deferred. |
| `cpufreq` | BSP | `./run_test.sh --machine apollo-fvp --bsp --test-profile cpufreq` | Implemented QBox BSP profile; final current-SHA runtime is deferred. |
| `platform-devices` | product | `./run_test.sh --machine apollo-fvp --test-profile platform-devices` | Deferred. QBox uses semantic network transport, not FVP-identical host ping/SSH. |
| `trusted-services` | product | `./run_test.sh --machine apollo-fvp --test-profile trusted-services` | Deferred until current-SHA FVP reference is regenerated. |
| `crypto-extension` | product | `./run_test.sh --machine apollo-fvp --test-profile crypto-extension` | Deferred. QBox coverage is semantic: deterministic crypto and instruction-use evidence, not FVP plugin wall-time comparison. |
| `ras_cpu` | product | `./run_test.sh --machine apollo-fvp --test-profile ras_cpu` | Implemented QBox product profile; requires matching `--fvp-reference`. |
| `hipc` | product | `./run_test.sh --machine apollo-fvp --test-profile hipc` | Blocked on final FVP HIPC reference. |
| `mbpp` | product, 16 CPU only | `./run_test.sh --machine apollo-fvp --test-profile mbpp` from the isolated 16-CPU lane | Blocked on isolated 16-CPU FVP and QBox prerequisites. |

## Validation Matrix

`qa-tests/validation/arm-zena-css-v2.2-non-xen.yaml` is the source of truth
for the v2.2 non-Xen matrix:

- 15 validation areas
- 14 unique public profiles
- 100 mapped action IDs
- 0 Xen selectors in scope
- 1 explicit Xen exclusion
- 2 semantic QBox areas: `platform-devices` and `crypto-extension`

The area-to-profile mapping is:

| Validation area | Profile |
| --- | --- |
| OEQA tests in the BSP | `bsp-core` |
| FVP device tests | `platform-devices` |
| PSA APIs | `trusted-services` |
| Primary Compute PFDI | `pfdi` |
| PFDI Safety Island CL1 | `pfdi-si-cl1` |
| Safety Diagnostics | `safety-diagnostics-tests` |
| Primary Compute CPU RAS | `ras_cpu` |
| Safety Island Cluster 1 | `si-cl1` |
| Crypto Extension performance | `crypto-extension` |
| CPU idle C-states | `cpuidle` |
| CPU Frequency Scaling | `cpufreq` |
| MBPP | `mbpp` |
| HIPC Baremetal Network | `hipc` |
| SMCF | `smcf` |
| PFDI Monitoring on Safety Island | `pfdi-si-cl1` |

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

## Final Artifact Status

The real 28-run aggregate for 14 FVP and 14 QBox results is not complete in
the current checkout. Do not link or consume a final `coverage.json` as current
runtime evidence until Todo 23 completes. Current blockers and deferred
profile handoffs are tracked in
`.work/validation-plan/final-review-backlog.md`.
