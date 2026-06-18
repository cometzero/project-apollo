# Apollo QBox Full Model First Wave Status

작성일: 2026-06-14

## 요약

`review-notes-ko.md`의 권장안을 그대로 채택했고,
`decision-record-ko.md`에 확정 decision으로 고정했다. 첫 wave 범위는
`MODEL-000`부터 `MODEL-060`까지이며, GIC/RAS/AP16/RoS/debug parity는
후속 epic으로 분리한다.

현재 상태는 다음과 같다.

| 항목 | 상태 |
| --- | --- |
| 문서 decision | 완료 |
| coverage ledger | 완료 |
| FMU/SSU SystemC component | 구현 및 component test 통과 |
| RSE protection control component | 구현 및 component test 통과 |
| RSE ATU/APU first-wave gate | 기존 `rse_atu` backend와 component evidence로 고정 |
| Apollo Lua backend wiring | FMU/SSU/RSE protection/ATU backend audit 통과 |
| Apollo full-system runtime | `live-cl0-cl1` no-trace runtime 및 post-login probe 통과 |

## 확정 결정

- 첫 wave는 `MODEL-000`부터 `MODEL-060`까지로 제한한다.
- `si_cl0_fmu`는 `zena_fmu`, `si_cl0_ssu`는 `zena_ssu`로 승격한다.
- `rse_nsacfg_regs`, `rse_sacfg_regs`, `rse_mpc_vm0_regs`,
  `rse_mpc_vm1_regs`, `rse_sic_regs`, `rse_mpc_sic_regs`는
  `rse_protection_ctrl`로 승격한다.
- `host_si_atu`, `host_ap_atu`, `host_smdexp2smd_atu`는 first wave에서
  기존 `rse_atu`의 translation/error/permission evidence를 사용한다.
- Strict NI-710AE requester policy model은 후속 `host_apu_filter` epic으로
  분리한다.
- Full GIC-720AE multiview parity, AP 16-core topology, RoS/I/O/debug
  parity는 first wave 완료 조건이 아니다.

## 구현 산출물

문서 산출물:

- `doc/apollo-qbox-full-model/index.md`
- `doc/apollo-qbox-full-model/decision-record-ko.md`
- `doc/apollo-qbox-full-model/coverage-ledger.md`
- `doc/apollo-qbox-full-model/first-wave-status-ko.md`
- `doc/apollo-qbox-hardware-ko.md`
- `doc/README.md`

QBox 산출물:

- `tools/qbox/systemc-components/zena_fmu/`
- `tools/qbox/systemc-components/zena_ssu/`
- `tools/qbox/systemc-components/rse_protection_ctrl/`
- `tools/qbox/tests/components/zena_fmu/`
- `tools/qbox/tests/components/zena_ssu/`
- `tools/qbox/tests/components/rse_protection_ctrl/`
- `tools/qbox-platform/platforms/apollo/hw-block/si_cl0.lua`
- `tools/qbox-platform/platforms/apollo/hw-block/rse.lua`
- `scripts/test/audit_qbox_apollo_fvp_full_coverage.py`

## 검증 Evidence

통과한 정적/빌드/component 검증:

```bash
cmake -S tools/qbox -B build/local-apollo-fvp/work/qbox-platform
cmake --build build/local-apollo-fvp/work/qbox-platform \
  --target zena_fmu zena_ssu zena_fmu-tests zena_ssu-tests \
  --parallel 8
ctest --test-dir build/local-apollo-fvp/work/qbox-platform \
  -R 'zena_(fmu|ssu)-tests' --output-on-failure
cmake --build build/local-apollo-fvp/work/qbox-platform \
  --target rse_protection_ctrl rse_protection_ctrl-tests \
  --parallel 8
ctest --test-dir build/local-apollo-fvp/work/qbox-platform \
  -R 'rse_protection_ctrl-tests' --output-on-failure
cmake --build build/local-apollo-fvp/work/qbox-platform --target rse_atu-tests --parallel 8
ctest --test-dir build/local-apollo-fvp/work/qbox-platform -R 'rse_atu-tests' --output-on-failure
python3 -m py_compile scripts/test/audit_qbox_apollo_fvp_full_coverage.py
git -C tools/qbox diff --check
cmake --build build/local-apollo-fvp/work/qbox-platform \
  --target zena_fmu-tests zena_ssu-tests rse_protection_ctrl-tests platforms-vp \
  --parallel 8
python3 scripts/test/audit_qbox_apollo_fvp_full_coverage.py \
  --output build/qbox-apollo-fvp/full-model-first-wave-coverage.json
```

Backend audit 결과:

- `si_cl0_ssu`: `zena_ssu`
- `si_cl0_fmu`: `zena_fmu`
- `rse_nsacfg_regs`: `rse_protection_ctrl`
- `rse_sacfg_regs`: `rse_protection_ctrl`
- `rse_mpc_vm0_regs`: `rse_protection_ctrl`
- `rse_mpc_vm1_regs`: `rse_protection_ctrl`
- `rse_sic_regs`: `rse_protection_ctrl`
- `rse_mpc_sic_regs`: `rse_protection_ctrl`
- `rse_atu_regs`: `rse_atu`
- `host_si_atu`: `rse_atu`
- `host_ap_atu`: `rse_atu`
- `host_smdexp2smd_atu`: `rse_atu`

Evidence file:

- `build/qbox-apollo-fvp/full-model-first-wave-coverage.json`

## Runtime Verification

Full-system runtime 검증은 완료했다.

실행:

```bash
env QBOX_RDASPEN_NETDEV=type=user \
python3 scripts/run/run_qbox_apollo_fvp_full.py \
  --skip-build --timeout 180 --post-login-probe \
  --si-mode live-cl0-cl1 \
  --out-dir build/qbox-apollo-fvp/full-model-debug-no-trace
```

결과:

- `passed: True`
- `blocker: none`
- RSE boot marker: pass
- RSE to SCP/AP power-on handoff: pass
- SI CL0 SCP-firmware marker: pass
- SI CL1 Zephyr marker: pass
- AP BL2/BL31/OP-TEE/U-Boot marker: pass
- Linux login/root shell marker: pass
- post-login probe: pass

Coverage audit:

```bash
python3 scripts/test/audit_qbox_apollo_fvp_full_coverage.py \
  --result-json build/qbox-apollo-fvp/full-model-debug-no-trace/result.json \
  --output build/qbox-apollo-fvp/full-model-debug-no-trace/coverage-audit.json
```

Coverage audit 결과:

- backend checks: pass
- `gate:G0`: pass
- `gate:G4`: pass
- `runtime_result_passed`: pass
- `markers:rse`: pass
- `markers:si_cl0`: pass
- `markers:si_cl1`: pass
- `markers:ap_firmware`: pass
- `markers:linux`: pass
- `markers:post_login`: pass

Evidence files:

- `build/qbox-apollo-fvp/full-model-debug-no-trace/result.json`
- `build/qbox-apollo-fvp/full-model-debug-no-trace/summary.txt`
- `build/qbox-apollo-fvp/full-model-debug-no-trace/coverage-audit.json`
- `build/qbox-apollo-fvp/full-model-debug-no-trace/qbox-rse.log`
- `build/qbox-apollo-fvp/full-model-debug-no-trace/qbox-safety-island-cl0.log`
- `build/qbox-apollo-fvp/full-model-debug-no-trace/qbox-safety-island-cl1.log`
- `build/qbox-apollo-fvp/full-model-debug-no-trace/qbox-primary-console.log`

추가로 `--live-trace` run도 같은 artifact set으로 통과했다.

- `build/qbox-apollo-fvp/full-model-debug-live-trace/result.json`
- `build/qbox-apollo-fvp/full-model-debug-live-trace/summary.txt`

## 최종 문서 위치

이 first-wave 문서 세트의 최종 진입점은 다음 파일이다.

```text
doc/apollo-qbox-full-model/index.md
```

권장 결정 자체의 canonical record는 다음 파일이다.

```text
doc/apollo-qbox-full-model/decision-record-ko.md
```
