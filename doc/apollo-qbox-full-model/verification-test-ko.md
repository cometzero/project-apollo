# Apollo QBox Full Model Promotion Verification / Test Plan

작성일: 2026-06-14

## 검증 원칙

이 작업의 성공 기준은 QBox가 계속 부팅되는 것만이 아니다. Full model 승격은
positive boot regression과 negative fault/access-control behavior를 모두
통과해야 한다.

검증 결과는 tmux 화면이 아니라 파일 기반 evidence로 남긴다.

```text
build/qbox-apollo-fvp/<run-id>/
  result.json
  coverage-audit.json
  final-verification.json
  qbox-platform.log
  per-uart logs
```

## Verification Ladder

| 단계 | 목적 | 대표 명령 |
| --- | --- | --- |
| V0 Static | 문법, whitespace, markdown placeholder 검사 | `git diff --check`, `rg` |
| V1 Component | SystemC model 단위 semantics 검증 | `ctest -R 'zena_fmu|zena_ssu'` |
| V2 Platform | Lua wiring, map, coverage 검증 | map/coverage scripts |
| V3 Runtime | Apollo full-system live boot regression | `scripts/run/run_qbox_apollo_fvp_full.py` |
| V4 Negative | fault/access-control/error path 검증 | component tests + fault injection run |
| V5 FVP Compare | FVP/QBox marker와 gap 비교 | compare/verifier scripts |

## V0 Static Checks

Commands:

```bash
git diff --check
git -C tools/qbox diff --check
python3 -m py_compile scripts/test/audit_qbox_apollo_fvp_full_coverage.py \
  scripts/test/verify_qbox_apollo_fvp_full_completion.py
python3 - <<'PY'
from pathlib import Path

patterns = [
    "TB" + "D",
    "TO" + "DO",
    "implement " + "later",
    "fill in " + "details",
    "Similar to " + "Task",
]

failed = False
for path in Path("doc/apollo-qbox-full-model").glob("*.md"):
    for line_no, line in enumerate(path.read_text().splitlines(), 1):
        for pattern in patterns:
            if pattern in line:
                print(f"{path}:{line_no}: placeholder phrase: {pattern}")
                failed = True
if failed:
    raise SystemExit(1)
PY
```

Pass criteria:

- Diff whitespace check exits 0.
- Changed Python scripts compile.
- New docs do not contain placeholder wording.

## V1 Component Tests

Commands:

```bash
cmake --build tools/qbox/build \
  --target zena_fmu zena_fmu-tests zena_ssu zena_ssu-tests \
  --parallel 8
ctest --test-dir tools/qbox/build -R 'zena_(fmu|ssu)' --output-on-failure
cmake --build tools/qbox/build \
  --target rse_protection_ctrl rse_protection_ctrl-tests \
  --parallel 8
ctest --test-dir tools/qbox/build -R 'rse_protection_ctrl' --output-on-failure
cmake --build tools/qbox/build \
  --target rse_atu rse_atu-tests \
  --parallel 8
ctest --test-dir tools/qbox/build -R 'rse_atu' --output-on-failure
```

Pass criteria:

- Reset values, read/write masks, W1C, RAZ/WI, IRQ assertion/deassertion, and
  access denial behavior are covered.
- Tests fail if model silently behaves like writable RAM.

## V2 Platform Validation

Commands:

```bash
cmake --build tools/qbox/build --target platforms-vp --parallel 8
python3 scripts/test/validate_qbox_fvp_rd_aspen_map.py
python3 scripts/test/audit_qbox_apollo_fvp_full_coverage.py \
  --check hardware-blocks \
  --output build/qbox-apollo-fvp/full-model-platform/coverage-audit.json
```

Pass criteria:

- Apollo Lua object names are unique.
- Replaced FMU/SSU/RSE protection windows do not overlap existing memory
  backing windows.
- `full-model-required` item backed by `gs_memory` fails coverage.
- `memory-backing` item backed by `gs_memory` passes coverage.

## V3 Full-System Runtime Regression

Command:

```bash
python3 scripts/run/run_qbox_apollo_fvp_full.py \
  --timeout 1200 \
  --post-login-probe \
  --si-mode live-cl0-cl1 \
  --out-dir build/qbox-apollo-fvp/full-model-runtime
```

Pass criteria:

- `result.json` records `verdict: pass`.
- RSE boot markers pass.
- SI CL0 SCP-firmware markers pass.
- SI CL1 Zephyr markers pass.
- TF-A BL2/BL31, OP-TEE, U-Boot, Linux markers pass.
- Linux login and root shell are reached.
- Post-login probes for PFDI, remoteproc, RPMsg, network, and kernel modules
  pass.
- Backend labels include FMU, SSU, RSE protection, and secure watchdog status.

## V4 Negative Behavior Tests

Negative tests must prove the new models are not passive RAM.

| Test | Stimulus | Expected observation |
| --- | --- | --- |
| FMU critical injection | Write configured `ERRIMPDEF<n>` injection bit | `ERR<n>STATUS.V=1`, `ERRGSR` bit set, critical IRQ asserted |
| FMU non-critical injection | Inject non-critical record | non-critical IRQ asserted, SSU `SYS_STATUS=ERRN` |
| SSU critical escalation | Assert critical FMU input | SSU `SYS_STATUS=ERRC` |
| RSE non-secure blocked write | Non-secure access to secure-only protected region | RAZ/WI or TLM error, no backing memory mutation |
| APU default-block | AP/SI requester accesses unopened SMD region | DECERR/SLVERR or modeled fault record |
| Watchdog refresh/control | Secure firmware refreshes secure watchdog | secure watchdog state changes, no non-secure watchdog mutation |

Recommended command shape after test runner support is added:

```bash
python3 scripts/run/run_qbox_apollo_fvp_full.py \
  --timeout 1200 \
  --post-login-probe \
  --si-mode live-cl0-cl1 \
  --fault-injection fmu-critical,fmu-noncritical,rse-ns-deny,apu-deny \
  --out-dir build/qbox-apollo-fvp/full-model-negative
```

Pass criteria:

- Negative tests fail on the current `gs_memory` baseline.
- Negative tests pass after the relevant model is enabled.
- `result.json` records injected fault names, observed IRQ/status, and final
  recovery or expected-stop state.

## V5 FVP Comparison And Final Gate

Commands:

```bash
python3 scripts/run/runfvp_log_boot.py \
  --machine apollo-fvp \
  --fvpconf build/local-apollo-fvp/deploy/apollo-fvp-local.fvpconf \
  --out-dir build/local-apollo-fvp/fvp-boot \
  --timeout 900 \
  --require all \
  --min-runtime 70 \
  --no-login
python3 scripts/analyze/compare_fvp_qbox_rse_logs.py \
  --fvp build/local-apollo-fvp/fvp-boot \
  --qbox build/qbox-apollo-fvp/full-model-runtime \
  --output build/qbox-apollo-fvp/full-model-runtime/comparison.json
python3 scripts/test/verify_qbox_apollo_fvp_full_completion.py \
  --strict-final \
  --run-dir build/qbox-apollo-fvp/full-model-runtime
```

Pass criteria:

- FVP baseline boot evidence exists for the same local artifact set.
- QBox missing markers are either fixed or classified as reviewed non-goals.
- `final-verification.json` authorizes completion.

## Regression Guardrails

Run these before commit:

```bash
python3 scripts/run/run_qbox_apollo_fvp_linux.py \
  --skip-build \
  --timeout 600 \
  --post-login-probe \
  --out-dir build/qbox-apollo-fvp/full-model-direct-guardrail
python3 scripts/run/run_qbox_apollo_fvp_full.py \
  --skip-build \
  --timeout 1200 \
  --post-login-probe \
  --si-mode live-cl0-cl1 \
  --out-dir build/qbox-apollo-fvp/full-model-final-guardrail
```

Pass criteria:

- Direct AP Linux path remains usable.
- Full-system path remains usable.
- New fidelity models do not require changing local build artifacts.
