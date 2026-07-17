# I7 - Local 및 Yocto 통합 검증 완료 보고서

- 완료일: 2026-07-17
- 판정: `complete`
- 대상: `apollo-qvp`, RD-Aspen CFG2, AP CPU0~CPU3
- 성능 기준: 없음

## 구현 결과

`scripts/run/run_qbox_apollo_fidelity.py`를 4 CPU smoke의 단일 진입점으로
추가했다. 이 runner는 다음 계약을 강제한다.

- `--artifacts local|yocto`를 명시하고 두 artifact 계열의 혼합을 거부한다.
- AP CPU 수는 4만 허용하며 Linux에서 관찰한 CPU ID가 정확히
  `[0, 1, 2, 3]`인지 검사한다.
- 실제 입력 파일, 크기와 SHA-256, source repository revision/dirty-state hash,
  backend와 resolved topology를 `manifest.json`에 기록한다.
- 기존 full-system coverage audit와 fidelity contract를 실행하고 모두 통과해야
  최종 `fidelity-summary.json`을 pass로 만든다.
- smoke에서 실행하지 않은 negative/fault slice는 pass로 합성하지 않고
  `executed=false`와 targeted evidence 사유를 기록한다.

## Local 검증

빌드와 단위 검증:

```text
./local_build.sh qbox --qbox-unit-tests --no-package --jobs 8
결과: PASS
  qbox/QBox-platform full target build 완료
  QBox-platform SystemC component CTest 33/33 PASS

cmake --build build/qbox-core-tests \
  --target request-context-tests --parallel 8
ctest --test-dir build/qbox-core-tests \
  -R '^request-context-tests$' --output-on-failure
결과: PASS, 1/1
```

full-system smoke:

```text
/usr/bin/python3 scripts/run/run_qbox_apollo_fidelity.py \
  --artifacts local --cpus 4 --profile smoke \
  --timeout 600 --jobs 8 \
  --out-dir build/qbox-apollo-qvp/fidelity-4cpu-local-20260717
결과: PASS
```

핵심 결과:

- `result.json`: `passed=true`, `verdict=pass`, `blocker=null`
- `manifest.json`: `artifact_family=local`,
  `linux_online_cpu_ids=[0,1,2,3]`, `artifact_family_errors=[]`
- `full-coverage-audit.json`: `passed=true`
- `fidelity-contract.json`: `status=pass`
- `fidelity-summary.json`: `passed=true`

보호 NI‑710AE 통합 결함을 분리하기 위해 direct-router A/B 실행을 먼저 수행했다.
최종 protected-path 진단은 reset-owner DMI, APU enable 뒤 programmed secure DMI,
SI CL0 NI programming, SI CL1 Zephyr/PFDI와 AP Linux login을 모두 통과했다.

- `build/qbox-apollo-qvp/diagnostic-i2-direct-router-20260716/`
- `build/qbox-apollo-qvp/diagnostic-i2-secure-context-20260717/`

## Yocto 검증

active config는 `MACHINE=apollo-qvp`, `RD_ASPEN_VARIANT=cfg2`,
`PC_CPUS_COUNT_DEFAULT=4`, `TMPDIR=build/tmp_baremetal`,
`nexios-image`임을 확인했다.

```text
./yocto_build.sh
결과: PASS
  7,293 tasks attempted
  7,236 tasks did not need rerun
  all succeeded
  qbox-libqemu-native compile/install/populate_sysroot PASS
  qbox-apollo-qvp-native configure/compile/check/install/populate_sysroot PASS
  nexios-image do_build PASS
```

Yocto artifact smoke:

```text
/usr/bin/python3 scripts/run/run_qbox_apollo_fidelity.py \
  --artifacts yocto --cpus 4 --profile smoke \
  --timeout 600 --jobs 8 \
  --out-dir build/qbox-apollo-qvp/fidelity-4cpu-yocto-20260717
결과: PASS
```

실행은 다음 Yocto-owned 경로만 사용했다.

- `build/tmp_baremetal/sysroots-components/x86_64/qbox-apollo-qvp-native/`
- `build/tmp_baremetal/deploy/images/apollo-qvp/`
- `build/tmp_baremetal/work/apollo_qvp-poky-linux/`

핵심 결과:

- `result.json`: `passed=true`, `verdict=pass`, `blocker=null`
- `manifest.json`: `artifact_family=yocto`,
  `linux_online_cpu_ids=[0,1,2,3]`, `artifact_family_errors=[]`
- `full-coverage-audit.json`: `passed=true`
- `fidelity-contract.json`: `status=pass`
- `fidelity-summary.json`: `passed=true`

## Targeted 회귀 검증

```text
/usr/bin/python3 -m pytest -q \
  tests/test_run_qbox_apollo_fidelity.py \
  tests/test_validate_qbox_apollo_fidelity_contract.py \
  tests/test_apollo_qvp_fault_event_plane.py \
  tests/test_apollo_qvp_pcie_irq_profile.py \
  tests/test_apollo_qvp_smmuv3_wiring.py \
  tests/test_apollo_qvp_software_abi_recovery.py \
  tests/test_run_qbox_apollo_fvp_linux.py \
  tests/test_validate_qbox_apollo_topology.py
결과: PASS, 65 passed

/usr/bin/python3 scripts/test/validate_qbox_apollo_fvp_full_map.py
/usr/bin/python3 scripts/test/validate_qbox_apollo_topology.py
/usr/bin/python3 scripts/test/audit_qbox_core_boundary.py
결과: PASS

git diff --check
git -C hsoc-stack/tools/qbox diff --check
git -C hsoc-stack/tools/qbox-platform diff --check
git -C hsoc-stack/tools/qemu diff --check
결과: PASS
```

## FVP 비교 판정

이번 source 상태에는 계획했던 `compare_qbox_fvp_fidelity.py`, 실행 가능한
`FVP_Zena_CSS_Cfg2`, local FVP result/config가 없었다. 따라서 새 전체 비교를
성공으로 표시하지 않고 `deferred`로 분류한다. 기존 A4 검증의 FVP SCMI v2.0
marker 비교는 참고 근거지만 I7 전체 fidelity 비교를 대체하지 않는다.

이 deferred 항목은 계획상 V0~V8 완료를 막지 않으며, FVP 실행 환경과 비교 도구가
준비되면 같은 CPU0~CPU3 marker 범위로 수행한다.

## 최종 범위

- I0~I6 구현 slice의 local/Yocto 정상 통합: `complete`
- AP CPU0~CPU3 online과 CPU4 이상 비활성: `complete`
- local/Yocto artifact provenance 분리: `complete`
- 전체 FVP focused differential: `deferred`
- 16 CPU, 성능 기준, stress/soak와 exhaustive matrix: 후속 범위

`hsoc-stack/components/**` 소스는 수정 대상에 포함하지 않았다. 최종 무변경
확인은 I8 완료 보고서에 기록한다.
