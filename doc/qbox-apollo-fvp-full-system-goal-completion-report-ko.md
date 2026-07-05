# QBox Apollo FVP Full-System Goal 완료 리포트

작성 시각: 2026-06-08 21:30 KST

## 요약

이번 Goal의 목적은 Apollo FVP local build 산출물을 QBox에서 full-system
형태로 부팅하고, RSE, Safety Island CL0, Safety Island CL1, Primary Compute
domain이 한 실행 안에서 모두 동작함을 검증하는 것이었다. 완료 기준은 단순한
Linux login이 아니라, canonical evidence directory의 strict final verifier가
`G0`부터 `G5`까지 모두 `pass`로 판정하는 것이다.

최종 결과는 다음과 같다.

| 항목 | 결과 |
| --- | --- |
| 최종 evidence directory | `build/qbox-apollo-fvp/full-live-cl0-cl1/` |
| 최종 verifier | `final-verification.json` |
| `completion_claim_allowed` | `true` |
| `completion_ready` | `true` |
| `G0..G5` | 모두 `pass` |
| 최종 수정 커밋 | `cef0fc00dd3f fix(qbox): build Apollo live modules` |
| push 상태 | `origin/main`에 push 완료 |

## 목표와 완료 기준

이번 Goal은 다음 체인이 QBox에서 실제로 이어지는지 확인하는 것이었다.

```text
RSE TF-M
  -> Safety Island CL0 SCP-firmware
  -> Safety Island CL1 Zephyr
  -> AP TF-A / OP-TEE / U-Boot / Linux
```

완료 기준은 `doc/qbox-apollo-fvp-full-system-tasks.md`와
`doc/qbox-apollo-fvp-full-system-goal-verification.md`의 final acceptance
정책을 따랐다. 특히 다음 조건이 필수였다.

- `build/qbox-apollo-fvp/full-live-cl0-cl1/result.json`이 `pass`여야 한다.
- `comparison.json`, `map-comparison.json`, `coverage-audit.json`이 생성되고
  각각 통과해야 한다.
- `final-verification.json`은 strict final verifier로 생성되어야 한다.
- `final-verification.json`은 `completion_claim_allowed: true`와
  `completion_ready: true`를 기록해야 한다.
- `overall_gates.G0..G5`가 모두 `pass`여야 한다.

## 진행 단계

### 1. G0 계약 및 입력 조건 재확인

먼저 현재 코드와 로컬 산출물이 full-system 검증 계약을 만족하는지 확인했다.

실행한 주요 명령:

```bash
python3 scripts/run/run_qbox_apollo_fvp_full.py \
  --check-only \
  --skip-build \
  --out-dir build/qbox-apollo-fvp/full-check-only

python3 scripts/inspect/probe_qemu_cortex_r82.py --source-root .

python3 scripts/test/validate_qbox_apollo_fvp_full_map.py \
  --check memory,irq,atu \
  --out build/qbox-apollo-fvp/full-check-only/map-validation.json

python3 scripts/test/audit_qbox_apollo_fvp_full_coverage.py \
  --check hardware-blocks \
  --output build/qbox-apollo-fvp/full-check-only/coverage-audit.json

cmake --build build/local-apollo-fvp/work/qbox-platform \
  --target cpu_arm_cortexR82 \
  --parallel 8
```

결과:

- Cortex-R82 QEMU model, EL2/MPU sysreg, PMSAv8 64-bit storage, QBox CPU
  wrapper probe가 통과했다.
- memory, interrupt, ATU map validator가 통과했다.
- hardware coverage audit contract가 생성됐다.
- `cpu_arm_cortexR82` targeted build가 통과했다.

### 2. G1 direct boot guardrail 재검증

`scripts/run/run_qbox_apollo_fvp_linux.py` direct boot 경로가 여전히 Linux login과
post-login probe를 통과하는지 확인했다. 첫 `--skip-build` 실행에서는 현재
build tree에 `char_backend_stdio.so`가 없어서 platform load 전에 실패했다.
이는 runtime 기능 문제가 아니라 필요한 QBox module 산출물이 없는 상태였다.

이후 build를 포함해 다시 실행했다.

```bash
python3 scripts/run/run_qbox_apollo_fvp_linux.py \
  --timeout 600 \
  --post-login-probe \
  --out-dir build/qbox-apollo-fvp/direct-guardrail
```

결과:

- `passed: True`
- `duration_s: 44.755`
- `post_login_probe: True`
- `probe_complete: True`
- `Booting Linux on physical CPU` marker 확인
- `apollo-fvp login:` marker 확인

### 3. G2 service-model full-system milestone 재검증

RSE-first AP boot path가 service-model Safety Island 구성에서 여전히 통과하는지
확인했다.

```bash
python3 scripts/run/run_qbox_apollo_fvp_full.py \
  --si-mode service-model \
  --skip-build \
  --timeout 1200 \
  --rootfs-bootargs-profile none \
  --post-login-probe \
  --cc3xx-qemu-native-backend \
  --rse-lms-accel \
  --rse-fast-boot-aliases \
  --rse-bl2-libc-hotpath \
  --rse-bl2-delay-accel \
  --rse-bl2-load-accel \
  --rse-bl2-boot-enc-accel \
  --rse-bl2-img-hash-accel \
  --rse-bl2-verify-sig-accel \
  --out-dir build/qbox-apollo-fvp/full-service-model
```

결과:

- `passed: True`
- `verdict: pass`
- `safety_island_mode: service-model`
- `range_limited_flash_dmi: True`
- `blocker: null`
- `completion_gates.G2: pass`
- `rse_start_to_runtime_handoff_s: 27.309`
- `rse_start_to_linux_boot_s: 57.894`
- `rse_start_to_login_prompt_s: 68.113`

FVP/QBox RSE log comparison도 통과했다.

```bash
python3 scripts/analyze/compare_fvp_qbox_rse_logs.py \
  --fvp build/local-apollo-fvp/fvp-boot \
  --qbox build/qbox-apollo-fvp/full-service-model \
  --output build/qbox-apollo-fvp/full-service-model/comparison.json
```

### 4. G3 live CL1 integration 재검증

CL0는 service-model로 유지하고, CL1 Zephyr를 live로 올리는 integration
milestone을 재확인했다.

```bash
python3 scripts/run/run_qbox_apollo_fvp_full.py \
  --si-mode live-cl1 \
  --skip-build \
  --timeout 1200 \
  --rootfs-bootargs-profile none \
  --post-login-probe \
  --cc3xx-qemu-native-backend \
  --rse-lms-accel \
  --rse-fast-boot-aliases \
  --rse-bl2-libc-hotpath \
  --rse-bl2-delay-accel \
  --rse-bl2-load-accel \
  --rse-bl2-boot-enc-accel \
  --rse-bl2-img-hash-accel \
  --rse-bl2-verify-sig-accel \
  --out-dir build/qbox-apollo-fvp/full-live-cl1
```

결과:

- `passed: True`
- `completion_gates.G3: pass`
- CL1 `Out of Reset (OoR)` marker 확인
- Zephyr boot marker 확인
- `PFDI Agent setup complete` 확인
- `PFDI service ready` 확인
- `si_net_init: Network interface configured` 확인
- Linux post-login probe에서 `arm_si_rproc`, `rpmsg`, `hipc_ethsi1` 확인
- `rse_start_to_login_prompt_s: 48.624`

### 5. G4 live CL0/CL1 full integration 문제 분석 및 수정

G4는 Safety Island CL0 SCP-firmware와 CL1 Zephyr를 모두 live로 실행하는
첫 completion candidate다. 초기 실행은 platform load 단계에서 실패했다.

관측된 실패 순서:

1. `gicx00_multiview.so` 누락
2. `addrtr.so` 누락
3. `reset_fanout.so` 누락

`addrtr.so`는 기존 required target에 있었지만, `--skip-build` 상태의 build
tree에 산출물이 없어서 발생한 문제였다. 반면 `reset_fanout`과 일부 Apollo
full-system live module은 runner의 `REQUIRED_TARGETS`에 없었다.

`tools/qbox-platform/platforms/apollo/apollo-qvp.lua`의 `moduletype` 목록과
`scripts/run/run_qbox_fvp_rd_aspen_rse.py`의 `REQUIRED_TARGETS`를 대조했다.
그 결과 live CL0/CL1에서 직접 로딩하는 다음 dynamic module들이 누락되어
있음을 확인했다.

- `host_cmn_cyprus`
- `host_gtimer`
- `host_ni710ae_nci`
- `host_smcf_mgi`
- `host_system_pll`
- `reset_fanout`

수정 파일:

```text
scripts/run/run_qbox_fvp_rd_aspen_rse.py
```

수정 내용:

- Apollo live full-system Lua가 로딩하는 위 dynamic module들을
  `REQUIRED_TARGETS`에 추가했다.
- 이후 build wrapper와 runner의 non-skip build 경로가 동일한 필수 module
  set을 준비할 수 있게 했다.

검증한 build 명령:

```bash
python3 -m py_compile \
  scripts/run/run_qbox_fvp_rd_aspen_rse.py \
  scripts/run/run_qbox_apollo_fvp_full.py

cmake --build build/local-apollo-fvp/work/qbox-platform \
  --target gicx00_multiview host_cmn_cyprus \
  --parallel 8

cmake --build build/local-apollo-fvp/work/qbox-platform \
  --target host_gtimer host_ni710ae_nci host_smcf_mgi \
           host_system_pll reset_fanout \
  --parallel 8

JOBS=8 ./local_build.sh qbox
```

최종 G4 실행:

```bash
python3 scripts/run/run_qbox_apollo_fvp_full.py \
  --si-mode live-cl0-cl1 \
  --skip-build \
  --timeout 1200 \
  --rootfs-bootargs-profile none \
  --post-login-probe \
  --cc3xx-qemu-native-backend \
  --rse-lms-accel \
  --rse-fast-boot-aliases \
  --rse-bl2-libc-hotpath \
  --rse-bl2-delay-accel \
  --rse-bl2-load-accel \
  --rse-bl2-boot-enc-accel \
  --rse-bl2-img-hash-accel \
  --rse-bl2-verify-sig-accel \
  --out-dir build/qbox-apollo-fvp/full-live-cl0-cl1
```

결과:

- `passed: True`
- `verdict: pass`
- `safety_island_mode: live-cl0-cl1`
- `completion_gates.G4: pass`
- `blocker: null`

주요 marker group 결과:

| Marker group | 결과 |
| --- | --- |
| `rse` | `tfm_bl1_1`, `first_image_slot`, `scmi_handoff` 모두 true |
| `si_cl0` | SCP log, SCP start, module init, GIC multiview, live strategy 모두 true |
| `si_cl1` | OoR, Zephyr boot, PFDI agent/service, network configured 모두 true |
| `ap_firmware` | AP BL2, BL31, OP-TEE, U-Boot 모두 true |
| `linux` | login prompt, root shell 모두 true |
| `post_login` | `arm_si_rproc`, `rpmsg`, `hipc_ethsi1`, probe complete 모두 true |

최종 runtime timing:

| 항목 | 시간 |
| --- | --- |
| `rse_start_to_runtime_handoff_s` | 28.331 |
| `rse_start_to_ap_power_on_s` | 28.230 |
| `rse_start_to_linux_boot_s` | 40.220 |
| `rse_start_to_login_prompt_s` | 50.045 |
| `bl1_1_to_bl2_s` | 8.543 |
| `bl2_to_rse_runtime_handoff_s` | 19.788 |

가장 긴 구간은 SI CL0 image load 이후 SI CL1 image load까지의
`14.562s` 구간이었다.

### 6. G5 final closure 생성

G4 pass 후 canonical evidence directory에서 G5 산출물을 생성했다.

```bash
python3 scripts/analyze/compare_fvp_qbox_rse_logs.py \
  --fvp build/local-apollo-fvp/fvp-boot \
  --qbox build/qbox-apollo-fvp/full-live-cl0-cl1 \
  --output build/qbox-apollo-fvp/full-live-cl0-cl1/comparison.json

python3 scripts/test/validate_qbox_apollo_fvp_full_map.py \
  --check memory,irq,atu \
  --out build/qbox-apollo-fvp/full-live-cl0-cl1/map-comparison.json

python3 scripts/test/audit_qbox_apollo_fvp_full_coverage.py \
  --result-json build/qbox-apollo-fvp/full-live-cl0-cl1/result.json \
  --output build/qbox-apollo-fvp/full-live-cl0-cl1/coverage-audit.json

python3 scripts/test/verify_qbox_apollo_fvp_full_completion.py \
  --strict-final \
  --output build/qbox-apollo-fvp/full-live-cl0-cl1/final-verification.json
```

결과:

- `comparison.json`: `passed: true`
- `map-comparison.json`: `passed: true`
- `coverage-audit.json`: `passed: true`
- `final-verification.json`: `verdict: pass`
- `overall_gates.G0..G5`: 모두 `pass`

## 최종 Evidence Bundle

최종 검증 bundle:

```text
build/qbox-apollo-fvp/full-live-cl0-cl1/
  result.json
  comparison.json
  map-comparison.json
  coverage-audit.json
  final-verification.json
  qbox-rse.log
  qbox-safety-island-cl0.log
  qbox-safety-island-cl1.log
  qbox-secure-console.log
  qbox-primary-console.log
```

`final-verification.json`의 핵심 값:

```json
{
  "completion_claim_allowed": true,
  "completion_ready": true,
  "overall_gates": {
    "G0": "pass",
    "G1": "pass",
    "G2": "pass",
    "G3": "pass",
    "G4": "pass",
    "G5": "pass"
  },
  "blocker": null
}
```

## 커밋 및 Push

이번 Goal 완료 과정에서 최종적으로 추가한 수정은 runner의 required QBox
module target 보강이다.

```text
cef0fc00dd3f fix(qbox): build Apollo live modules
```

커밋 내용:

- `scripts/run/run_qbox_fvp_rd_aspen_rse.py`에 Apollo live full-system dynamic
  module target 6개를 추가했다.
- DCO sign-off 포함.
- `origin/main`에 push 완료.

push 결과:

```text
4f917ef43f09..cef0fc00dd3f  main -> main
```

`tools/qbox`와 `tools/qemu` submodule에는 이번 마무리 단계에서 새 커밋이
없었다.

## 남은 상태와 주의 사항

- top-level `main`은 `origin/main`과 동기화되어 있다.
- 기존 untracked `.omc/` 디렉터리는 남아 있으나 이번 Goal 산출물에는
  포함하지 않았다.
- `build/` 아래 evidence는 생성 산출물이며 source commit에는 포함하지 않았다.
- 사용자가 명시적으로 요청한 대로 컴퓨터 종료는 수행하지 않았다.

## 결론

이번 Goal은 strict final verifier 기준으로 완료되었다. QBox Apollo FVP
full-system은 `live-cl0-cl1` 모드에서 RSE TF-M, SI CL0 SCP-firmware,
SI CL1 Zephyr, AP TF-A/OP-TEE/U-Boot/Linux, Linux post-login driver probe까지
한 실행 안에서 통과했다. 최종 완료 주장은
`build/qbox-apollo-fvp/full-live-cl0-cl1/final-verification.json`의
`completion_claim_allowed: true`와 `G0..G5: pass`에 근거한다.
