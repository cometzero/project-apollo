> Runtime pytest는 [qa-tests](../../qa-tests/README.md)를 사용합니다. 이 디렉터리는 기존 OEQA/profile CLI, dashboard adapter와 validation contract를 유지합니다.

# Legacy Apollo QA validation

This directory owns the `run_test.sh` orchestration package, validation
profiles and schema data. Its host tests live in `qa-tests/unittests`.
FVP runtime tests use the owning Yocto
layers through run-scoped OEQA configuration below `build/tests/`. QBox runtime
profiles use the UART probes and evaluators in `scripts/run/qbox_validation/`.

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
./run_test.sh --machine apollo-qvp --bsp --test-profile bsp-core
./run_test.sh --machine apollo-qvp --test-profile ras_cpu
./run_test.sh --machine apollo-qvp --test-profile platform-devices
```

The QBox backend selects `apollo-qvp`, validates the deployed `qboxconf`, and
runs the canonical Yocto QBox launcher in headless full-system mode. Add
`--bsp` to boot `nexios-bsp-initramfs`. Every implemented named QBox profile
can run standalone from current QBox provenance. `--fvp-reference
<summary.json>` is optional comparison evidence; when supplied, the runner
still rejects failed, skipped, stale, image-mismatched, CPU-count-mismatched,
or contract-drifted references before launching QBox. Unknown and FVP-only
profiles remain selection errors. Basic QBox boot without a named profile
remains available through the normal QBox launcher path.

## Public Profiles

| Profile | Image | FVP command | QBox state |
| --- | --- | --- | --- |
| `bsp-core` | BSP | `./run_test.sh --machine apollo-fvp --bsp --test-profile bsp-core` | Implemented standalone QBox BSP profile; FVP reference optional. |
| `si-cl1` | BSP | `./run_test.sh --machine apollo-fvp --bsp --test-profile si-cl1` | Implemented standalone QBox BSP profile; FVP reference optional. |
| `smcf` | BSP | `./run_test.sh --machine apollo-fvp --bsp --test-profile smcf` | Implemented standalone QBox BSP profile; FVP reference optional. |
| `pfdi` | BSP | `./run_test.sh --machine apollo-fvp --bsp --test-profile pfdi` | Implemented standalone QBox BSP profile; FVP reference optional. |
| `pfdi-si-cl1` | BSP | `./run_test.sh --machine apollo-fvp --bsp --test-profile pfdi-si-cl1` | Implemented standalone QBox SI CL1/monitor profile; FVP reference optional. |
| `safety-diagnostics-tests` | BSP | `./run_test.sh --machine apollo-fvp --bsp --test-profile safety-diagnostics-tests` | Implemented standalone QBox BSP profile; FVP reference optional. |
| `cpuidle` | BSP | `./run_test.sh --machine apollo-fvp --bsp --test-profile cpuidle` | Standalone QBox preflight is implemented; final current-SHA runtime is deferred. |
| `cpufreq` | BSP | `./run_test.sh --machine apollo-fvp --bsp --test-profile cpufreq` | Standalone QBox preflight is implemented; final current-SHA runtime is deferred. |
| `platform-devices` | product | `./run_test.sh --machine apollo-fvp --test-profile platform-devices` | FVP and standalone QBox PASS. QBox transport/network coverage is semantic; an FVP reference is optional. |
| `trusted-services` | product | `./run_test.sh --machine apollo-fvp --test-profile trusted-services` | Implemented standalone QBox PSA profile; FVP reference optional. Runtime qualification must use matching current artifacts. |
| `crypto-extension` | product | `./run_test.sh --machine apollo-fvp --test-profile crypto-extension` | Deferred. QBox coverage is semantic: deterministic crypto and instruction-use evidence, not FVP plugin wall-time comparison. |
| `ras_cpu` | product | `./run_test.sh --machine apollo-fvp --test-profile ras_cpu` | Implemented standalone QBox product profile; FVP reference optional. |
| `hipc` | product | `./run_test.sh --machine apollo-fvp --test-profile hipc` | Blocked on final FVP HIPC reference. |
| `mbpp` | product, 16 CPU only | `./run_test.sh --machine apollo-fvp --test-profile mbpp` from the isolated 16-CPU lane | Blocked on isolated 16-CPU FVP and QBox prerequisites. |

## Validation Matrix

`scripts/validation/validation/arm-zena-css-v2.2-non-xen.yaml` is the source of truth
for the v2.2 non-Xen matrix:

- 15 validation areas
- 14 unique public profiles
- 100 documented action IDs: 99 required and 1 explicit exclusion
- 0 Xen selectors in scope
- 1 explicit Xen exclusion
- `primary-ping` explicitly excluded for FVP user networking
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
PYTHONPATH=scripts/validation python3 -m apollo_validation.cli list --format json
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

## Host pytest execution and reports

Run all Apollo-owned host pytest suites from the workspace root:

```bash
python3 scripts/test/run_pytest.py -ra
```

The root `pytest.ini` selects `qa-tests/unittests`, `tests`, and `scripts/gem5`
and provides their repository-local Python import paths. External nested
repositories such as `arm-zena-css` and `sw-ref-stack` are outside this default
scope. Use Python 3.12 or newer (the validation package uses PEP 695 type aliases).
The runner uses the current Python interpreter and its installed pytest;
it does not install dependencies or build images.

The default suite includes two real `bitbake -e scp-firmware` metadata parses
in `tests/test_fvp_si_pfdi_policy.py`; it is not entirely mocked. Enable the
four additional image metadata parsing checks for `TEST_TARGET` and
`TEST_SUITES` with:

```bash
APOLLO_RUN_BITBAKE_MATRIX_TESTS=1 python3 scripts/test/run_pytest.py -ra
```

Do not run these suites concurrently with another BitBake build using the
shared build directory. These checks parse metadata; they do not build images
or establish guest runtime behavior.

Each invocation creates a unique UTC-stamped directory at
`build/qbox-apollo-qvp/pytest-<timestamp>-<suffix>/` containing:

- `console.log`: streamed, combined pytest stdout and stderr.
- `junit.xml`: pytest's machine-readable case results for CI.
- `report.md`: command, timestamps, Python version, the
  `APOLLO_RUN_BITBAKE_MATRIX_TESTS` opt-in value, exit code, result counts,
  failure/error/skip details, and the test suites actually recorded in JUnit.

The runner preserves pytest's exit code, including collection errors and the
no-tests-selected result. Ctrl+C forwards SIGINT to the pytest process group;
after five seconds, remaining group processes are killed and pytest is reaped. The
runner retains available logs/JUnit, writes an INTERRUPTED report, and exits
with code 130. Missing or malformed JUnit results never produce a PASS report.
Arguments are passed to pytest, so focused checks use the same report path:

```bash
python3 scripts/test/run_pytest.py -q qa-tests/unittests
python3 scripts/test/run_pytest.py -q tests/test_qbox_validation_registry.py
python3 scripts/test/run_pytest.py -q scripts/gem5
```

Direct `python3 -m pytest` is also supported, but does not generate the retained
Markdown report or console log. These are host-side tool, parser, contract and
fixture tests; their PASS result does not establish QBox/FVP boot or guest
UART/SSH behavior. Run named `run_test.sh --machine apollo-qvp --test-profile`
profiles separately for platform runtime evidence.
