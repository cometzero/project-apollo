# I2 - NI-710AE APU Data-path 완료 보고서

- 완료일: 2026-07-16
- 통합 보강 검증일: 2026-07-17
- 판정: `complete`
- 대상: SI CL0 primary NI-710AE NCI의 ASNI 0 보호 경로

## 근거와 구현 범위

register layout과 동작은 다음 로컬 Arm 소스를 기준으로 확인했다.

- `doc/arm_zena_css_dev_guide/09-programmers-model-for-zena-css.md`
- `hsoc-stack/components/system_mgmt/scp-firmware/module/ni_710ae/`
- `hsoc-stack/components/system_mgmt/scp-firmware/product/automotive-rd/apollo-qvp/si0_ramfw/config_ni_710ae.c`

FVP와 QVP의 `config_ni_710ae.c`가 동일함을 확인했다. Arm BSD-3-Clause
driver가 정의하는 32개 region, 0x20 stride, 64-byte address granularity,
PRBAR/PRLAR/PRID, enable/background/lock, secure/non-secure read/write permission과
sync-error 동작만 구현했다. 공식 근거가 없는 fault register는 추가하지 않았다.

`host_ni710ae_nci`의 discovery/APU register 저장소와 실제 transaction verdict를
하나로 연결했다. SI CL0 CPU 요청은 primary NCI의 ASNI 0 정책을 거치며 다음
규칙을 적용한다.

- reset 상태에서는 SI CL0 owner 또는 인증된 loader capability만 통과한다.
- APU enable 뒤에는 foreground 우선, background 후순위로 주소와 requester ID,
  security state, read/write permission을 판정한다.
- deny는 downstream 호출 없이 address 또는 generic TLM error를 반환한다.
- debug access도 같은 정책을 사용하며 암묵적인 우회 권한을 주지 않는다.
- lock된 region은 reset 전까지 재프로그래밍할 수 없다.
- reset 상태 DMI는 owner/trusted context만 허용한다.
- APU enable 뒤 DMI는 downstream range 전체가 하나의 허용 region 안에 있고
  security/read/write permission이 모두 일치할 때만 허용한다.
- APU enable 또는 실행 중 policy 변경은 protected DMI를 다음 SystemC delta에
  병합 무효화한다. register programming 중 동기 무효화로 현재 CPU instruction을
  재실행하지 않는다.
- SI CL0 CPU의 고정 secure context는 QEMU의 미지정/default memory attribute보다
  우선한다.

정책 target socket은 QBox module-factory가 사용하는
`simple_target_socket_b<..., SC_ZERO_OR_MORE_BOUND>` 형식으로 만들었다. primary
NCI에는 CPU 보호 경로를 연결하고, register discovery만 제공하는 secondary/MHU
NCI는 불필요한 보호 소켓 바인딩을 요구하지 않는다.

## 변경 파일

QBox platform:

- `systemc-components/host_ni710ae_nci/include/host_ni710ae_nci.h`
- `tests/components/host_ni710ae_nci/host_ni710ae_nci-tests.cc`
- `platforms/apollo/hw-block/si_cl0.lua`
- `platforms/apollo/hw-block/topology.lua`
- `platforms/apollo/hw-block/transaction_routes.lua`

QBox core:

- `systemc-components/common/include/tlm-extensions/request-context.h`
- `qemu-components/common/include/cpu.h`
- `tests/components/request-context/request-context-tests.cc`

최상위 검증과 문서:

- `scripts/test/validate_qbox_apollo_topology.py`
- `tests/test_validate_qbox_apollo_topology.py`
- `scripts/test/validate_qbox_apollo_fidelity_contract.py`
- `tests/test_validate_qbox_apollo_fidelity_contract.py`
- `doc/apollo-qbox-full-model/coverage-ledger.md`
- 이 완료 보고서

`hsoc-stack/components/**`는 수정하지 않았다.

## 최소 기능 검증

`host_ni710ae_nci-tests`의 내부 GoogleTest 9개가 다음 핵심 동작을 검증한다.

1. discovery topology와 APU block 배치
2. reset owner allow 및 AP normal/debug deny
3. deny 시 downstream side effect가 없고 context 없는 DMI가 거부됨
4. programming 뒤 secure normal/debug allow
5. reset owner와 programmed secure DMI allow, non-secure DMI deny
6. lock 뒤 write 무시와 reset 뒤 해제
7. 사용하지 않는 protected path의 0-binding socket 계약

```text
cmake --build build/local-apollo-qvp/work/qbox-platform \
  --target host_ni710ae_nci-tests --parallel 8
ctest --test-dir build/local-apollo-qvp/work/qbox-platform \
  -R '^host_ni710ae_nci-tests$' --output-on-failure
결과: PASS, 1/1 CTest, 내부 GoogleTest 9개

cmake --build build/qbox-core-tests --target request-context-tests --parallel 8
ctest --test-dir build/qbox-core-tests \
  -R '^request-context-tests$' --output-on-failure
결과: PASS, 1/1 CTest, 고정 secure context 우선순위 포함

/usr/bin/python3 -m pytest -q \
  tests/test_validate_qbox_apollo_topology.py \
  tests/test_validate_qbox_apollo_fidelity_contract.py
결과: PASS, 22 passed in 0.89s

/usr/bin/python3 scripts/test/validate_qbox_apollo_topology.py
/usr/bin/python3 scripts/test/validate_qbox_apollo_fvp_full_map.py
git -C hsoc-stack/tools/qbox diff --check
git -C hsoc-stack/tools/qbox-platform diff --check
결과: PASS

./local_build.sh qbox
결과: PASS
  qbox-configure: 5초
  qbox-build: 0초(증분 빌드)
  최종 target: platforms-vp, apollo_fvp_full_system
```

## 런타임 진단 증거

정책 경로 통합 중 네 가지 계약 오류를 실제 실행으로 찾아 수정했다.

- 누락된 `si_cl0_ni710ae_primary_nci` topology bridge
- QEMU forward path에서 호출되지 않은 convenience optional socket 형식
- policy 변경 때 instruction 수행 중 동기 DMI invalidate를 반복한 문제
- QEMU default `MemTxAttrs.secure=0`이 명시된 SI CL0 secure context를 덮은 문제

직접 router 연결 A/B 실행으로 protected path가 원인임을 분리한 뒤, 최종 진단은
CPU의 첫 fetch DMI `0x120000000`을 reset-owner 정책으로 허용하고 APU enable 뒤
`0x12001df0c` DMI를 programmed secure policy로 다시 허용했다. deny trace는
opt-in bounded trace로 유지하며 기본 실행에서는 출력하지 않는다.

- `build/qbox-apollo-qvp/diagnostic-i2-direct-router-20260716/result.json`
- `build/qbox-apollo-qvp/diagnostic-i2-secure-context-20260717/qbox-platform.log`
- `build/qbox-apollo-qvp/diagnostic-i2-secure-context-20260717/result.json`

최종 보호 경로 full-system 실행은 RSE, SI CL0 NI programming, SI CL1 Zephyr/PFDI,
AP Linux login까지 통과했다. 성능 수치는 acceptance로 사용하지 않는다. 정식
local/Yocto artifact 판정은 I7 보고서에서 관리한다.

## 잔여 범위

- secondary/MHU NCI는 이번 단계에서 register/discovery 모델로 유지한다.
- primary NCI의 다른 ASNI/AMNI별 실제 물리 ingress 배치는 후속 topology 확대
  범위다.
- APU violation을 FMU/SSU event plane으로 전달하는 동작은 I5 범위다.
- 여러 region에 걸친 DMI와 permission이 부분적으로만 일치하는 DMI는 의도적으로
  거부한다. exhaustive DMI matrix와 세부 timing은 후속 검증 범위다.
