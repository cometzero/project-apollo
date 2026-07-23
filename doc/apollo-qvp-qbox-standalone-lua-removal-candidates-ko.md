# Apollo QVP QBox 단독 실행 Lua 제거 후보 분석

작성일: 2026-07-23

분석 기준:

- 상위 저장소: `8749c95bb1819ed1e35e6f51f0e6dabf8350fb81`
- `hsoc-stack/tools/qbox-platform`:
  `14b73e8e95582eec665814fb492d7ae49bc5b34a`
- 활성 machine: `apollo-qvp`
- 활성 variant: RD-Aspen CFG2
- 기본 AP CPU 수: 4

## 1. 목적과 범위

이 문서는 Apollo QVP QBox 구현에서 다음 두 단독 실행 경로를 제거할 때의
후보 파일, 연쇄 영향, 유지해야 할 full-system 구현과 검증 기준을 정리한다.

1. Primary Compute(AP) Linux direct boot 단독 실행
2. Safety Island CL1 Zephyr 단독 실행

대상은 단순히 파일 이름에 `standalone` 또는 `isolated`가 들어간 코드만이
아니다. 전용 Lua를 호출하는 runner, 해당 경로의 존재를 요구하는 validator,
독립 실행 결과를 완료 gate로 사용하는 검증 계약과 현재 사용법 문서까지
포함한다.

이 분석에서 소스 삭제나 runner 변경은 수행하지 않았다. 제거 구현 전에
사용할 후보와 경계를 확정하는 것이 목적이다.

## 2. 결론

직접 제거할 핵심 Lua 후보는 다음 네 파일이다.

| 우선순위 | 파일 | 현재 역할 | 판정 |
| --- | --- | --- | --- |
| P0 | `platforms/apollo/apollo-pc.lua` | `primary_compute.lua`를 로드하는 11줄 AP 단독 진입점 | 삭제 후보 |
| P0 | `platforms/apollo/hw-block/primary_compute.lua` | AP direct boot platform 전체를 별도로 구성하는 603줄 monolithic Lua | 삭제 후보 |
| P0 | `platforms/apollo/apollo-si-cl1.lua` | `si_cl1_isolated.lua`를 로드하는 11줄 CL1 단독 진입점 | 삭제 후보 |
| P0 | `platforms/apollo/hw-block/si_cl1_isolated.lua` | CL1 isolated platform 전체를 별도로 구성하는 311줄 Lua | 삭제 후보 |

네 파일은 합계 936줄이다. 이 파일들은 full-system
`platforms/apollo/apollo-qvp.lua`의 구성 경로에 포함되지 않는다.

다만 현재 저장소에서 완전히 도달 불가능한 dead code는 아니다.
`scripts/run/run_qbox_apollo_fvp_linux.py`와
`scripts/run/run_qbox_apollo_fvp_si_cl1.py`가 각각 전용 진입점을
사용한다. 따라서 제거는 다음과 같이 정의해야 한다.

> 두 standalone 실행 기능을 제품 및 검증 계약에서 제거하고,
> `apollo-qvp.lua`를 Apollo QVP의 유일한 runtime platform 진입점으로
> 만든다.

Lua 네 파일만 삭제하면 runner와 정적 validator가 즉시 깨진다. P0 Lua 삭제와
P1 호출자·검증 계약 정리는 같은 변경 묶음에서 완료해야 한다.

## 3. 현재 실행 구조

### 3.1 유지할 full-system 경로

현재 full-system 진입점은 다음 모듈을 직접 조립한다.

```text
apollo-qvp.lua
  |
  +-- machine_contract.lua
  +-- config.lua
  +-- fabric.lua
  +-- rse.lua
  +-- ap_compute.lua
  +-- ros.lua
  +-- system_mgmt.lua
  +-- si_cl0.lua
  `-- si_cl1.lua
```

`apollo-qvp.lua`는 `ap_compute.define()`과
`ap_compute.enable_ap_router()`를 호출한다. `si_cl1.define()`을 항상
호출하고, 선택한 live SI mode가 CL1 실행을 요구하면
`si_cl1.enable()`을 호출한다.

codebase graph에서도 다음 호출자는 모두 `apollo-qvp.lua` 하나로 확인됐다.

- `ap_compute.define()`
- `ap_compute.enable_ap_router()`
- `si_cl1.define()`
- `si_cl1.enable()`

따라서 full-system의 AP와 CL1 구현 주인은 각각
`hw-block/ap_compute.lua`와 `hw-block/si_cl1.lua`이다.

### 3.2 제거할 병렬 standalone 경로

```text
apollo-pc.lua
  `-- primary_compute.lua
        `-- AP kernel/DTB/initramfs direct load

apollo-si-cl1.lua
  `-- si_cl1_isolated.lua
        `-- CL1 Zephyr image direct load
```

두 경로는 full-system contract, domain별 router와 firmware handoff를
공유하지 않고 각각 독립 `platform`을 다시 만든다.

## 4. Primary Compute 단독 실행 분석

### 4.1 제거 근거

`primary_compute.lua`는 AP direct boot를 위해 다음을 한 파일에서 다시
정의한다.

- 독립 `Container`, `router`, QEMU instance와 GIC/ITS
- DRAM, SRAM, HIPC용 메모리와 broad fallback memory
- SMMU/TBU, GPEX, virtio block/net/RNG, RTC와 watchdog
- stdio UART backend
- Linux kernel, DTB, initramfs와 AArch64 boot stub 직접 적재
- 최대 16개 AP CPU의 생성, reset vector, PC/exception trace와 GDB

이 경로는 `primary_compute.lua:21`에서
`fw/arm64_bootloader.lua`를 읽고, `primary_compute.lua:481-488`에서
kernel, DTB와 boot stub를 직접 적재한다. RSE, TF-A, OP-TEE와 U-Boot
handoff를 통과하지 않는다.

반면 full-system은 `apollo-qvp.lua:25-54`에서 shared config, fabric,
RSE, AP, RoS, system management와 두 Safety Island를 조합한다. AP 장치와
CPU는 `ap_compute.lua`, RoS peripheral은 `ros.lua`, boot/reset 제어는
RSE와 system-management 경로가 소유한다.

병렬 AP platform을 유지하면 다음 문제가 계속 남는다.

1. 같은 AP 장치를 `primary_compute.lua`, `ap_compute.lua`,
   `ros.lua`에 중복 반영해야 한다.
2. direct boot 기본 CPU 수는 16이지만 full-system 기본값은 image와 활성
   설정을 따르는 4이므로 topology 기본 계약이 다르다.
3. direct boot의 단일 router와 fallback memory는 full-system의
   domain router, ATU/APU와 명시적 bridge 정책을 검증하지 못한다.
4. direct boot 성공은 RSE-first firmware chain, AP reset release,
   SCMI/PFDI/HIPC와 SI 상호작용의 회귀 방지 증거가 아니다.

### 4.2 Primary Compute 연쇄 제거 및 수정 후보

| 분류 | 파일 또는 인터페이스 | 필요한 후속 조치 |
| --- | --- | --- |
| runner | `scripts/run/run_qbox_apollo_fvp_linux.py` | 파일 삭제. direct DT overlay, extra disk, direct PC trace와 result contract도 함께 종료 |
| runner test | `tests/test_run_qbox_apollo_fvp_linux.py` | runner와 함께 삭제 |
| completion gate | `scripts/test/verify_qbox_apollo_fvp_full_completion.py` | G1 `Direct-boot guardrail`을 제거하거나 full-system AP gate로 재정의 |
| map validator | `scripts/test/validate_qbox_apollo_fvp_full_map.py` | `apollo-pc.lua`와 `primary_compute.lua` 존재 검사 제거 |
| AP map audit | `scripts/test/audit_qbox_apollo_ap_memory_map.py` | `direct_boot_ram_1_base` 비교 제거. full-system config와 DTS 비교는 유지 |
| ownership audit | `scripts/test/audit_qbox_apollo_lua_ownership.py` | `primary_compute.lua` 제외 예외 제거 |
| profile test | `tests/test_apollo_qvp_pcie_irq_profile.py` | direct path parity test만 제거하고 `ap_compute.lua` full-system test는 유지 |
| fault test | `tests/test_apollo_qvp_fault_event_plane.py` | direct path assertion만 제거하고 full-system fault route 검증은 유지 |
| active docs | QBox Platform README, Apollo README, `scripts/README.md`, `AGENTS.md`, qbox-dev workflow | direct boot 실행법과 guardrail 설명 제거 또는 full-system 명령으로 교체 |

G1은 단순히 삭제할 수도 있지만, 최종 completion gate 번호와 의미를
유지해야 한다면 다음과 같이 재정의하는 편이 낫다.

```text
기존 G1: AP Linux direct boot가 login과 post-login probe를 통과
권장 G1: apollo-qvp full-system에서 AP Linux와 AP 전용 probe가 통과
```

이렇게 해야 AP 검증을 없애지 않고 standalone platform만 제거할 수 있다.

### 4.3 direct boot 환경변수 후보

runner와 Lua를 삭제하면 다음 standalone 전용 interface도 제거 후보가 된다.

- `QBOX_APOLLO_PC_TRACE*`
- direct path의 `QBOX_APOLLO_GDB_CPU_INDEX`,
  `QBOX_APOLLO_GDB_PORT`, `QBOX_APOLLO_GDB_PORT_BASE`
- `QBOX_APOLLO_EXTRA_BLK1`부터 `QBOX_APOLLO_EXTRA_BLK3`
- direct-only `QBOX_APOLLO_QEMU_ARGS`, `QBOX_APOLLO_TCG_MODE`,
  `QBOX_APOLLO_SYNC_POLICY`
- direct kernel/DTB/initramfs/rootfs 전달과 direct DT overlay 출력

`QBOX_APOLLO_NUM_CPUS`, `QBOX_APOLLO_PCIE_IRQ_TEST`,
`QBOX_APOLLO_FAULT_EVENT_TEST`처럼 full-system에서도 사용하는 key는
제거 대상이 아니다.

## 5. SI CL1 단독 실행 분석

### 5.1 제거 근거

`si_cl1_isolated.lua`의 파일 머리말은 이 경로를 full AP/SI integration
이전의 `QAP-FULL-020` bring-up target으로 정의한다
(`si_cl1_isolated.lua:1-5`). 현재 full-system CL1 구현은 이미
`si_cl1.lua`에 존재하고 `apollo-qvp.lua`가 조합한다.

isolated 구현과 full-system 구현은 이름만 다른 동일 복사본도 아니다.

| 항목 | isolated `si_cl1_isolated.lua` | full-system `si_cl1.lua` |
| --- | --- | --- |
| platform 구조 | 독립 `Container`와 단일 router | system/AP/SI domain fabric에 결합 |
| QEMU CPU | `cpu_arm_cortexR82` | external counter를 쓰는 `cpu_arm_cortexR82_external_counter` |
| 시작/reset | 독립 실행 즉시 시작 | managed start-in-reset과 host PPU release |
| timer | CPU 내부 기본 연결 | CSS system counter bridge, 100 MHz contract |
| TCG 기본 | `SINGLE` | `MULTI` |
| sync 기본 | `multithread-unconstrained` | `multithread-quantum` |
| memory 오류 | 8 GiB catch-all `gs_memory` | domain router와 명시적 bridge/decode |
| HIPC/PFDI | isolated pair와 local shared memory | AP/SI0 peer, request context, requester hold와 실제 shared path |
| loader identity | 일반 loader | secure authenticated-image request context |

isolated 경로는 CL1 CPU와 UART 자체의 초기 bring-up에는 유용했지만, 현재
중요한 CL1 동작인 SI0 PFDI 응답, AP HIPC/RPMsg, reset/power sequencing,
shared counter와 cross-domain 접근 정책을 우회한다. “CL1은 항상 Apollo QVP에
포함해 실행한다”는 정책에서는 유지 가치보다 두 구현의 drift 위험이 크다.

### 5.2 SI CL1 연쇄 제거 및 수정 후보

| 분류 | 파일 또는 인터페이스 | 필요한 후속 조치 |
| --- | --- | --- |
| runner | `scripts/run/run_qbox_apollo_fvp_si_cl1.py` | 파일 삭제 |
| runner test | `tests/test_run_qbox_apollo_fvp_si_cl1.py` | runner와 함께 삭제 |
| full runner compatibility | `scripts/run/run_qbox_apollo_fvp_full.py` | `--isolated`, `isolated_command()`, `run_isolated()`와 `live-cl1` child 분기 제거 |
| full runner test | `tests/test_run_qbox_apollo_fvp_full.py` | isolated Lua의 `SINGLE` default assertion과 isolated command test 제거 |
| completion evidence | `scripts/test/verify_qbox_apollo_fvp_full_completion.py` | 선택형 `--si-cl1-isolated-dir`와 QAP-FULL-020 milestone parser 제거 |
| map validator | `scripts/test/validate_qbox_apollo_fvp_full_map.py` | standalone entrypoint와 isolated block 존재 검사 제거 |
| ownership audit | `scripts/test/audit_qbox_apollo_lua_ownership.py` | `si_cl1_isolated.lua` 제외 예외 제거 |
| active docs | QBox Platform README, Apollo README와 `scripts/README.md` | isolated 명령, `--isolated` 사용법과 유지 사유 제거 |

`--si-mode live-cl1`과 `--isolated --si-mode live-cl1`은 구분해야 한다.
제거 대상은 후자처럼 `apollo-si-cl1.lua`를 실행하는 standalone 분기다.
full-system `apollo-qvp.lua` 안에서 CL1을 활성화하는 mode와
`QBOX_APOLLO_FULL_SI_CL1_*` 환경변수는 유지 대상이다.

isolated runner와 Lua가 사라지면 `QBOX_APOLLO_SI_CL1_*` prefix도 제거한다.
full-system은 별도 `QBOX_APOLLO_FULL_SI_CL1_*` 계약을 사용한다.

## 6. 유지 대상

다음 항목은 이름이 유사하거나 standalone에서도 사용됐다는 이유로 함께
삭제하면 안 된다.

| 유지 대상 | 이유 |
| --- | --- |
| `platforms/apollo/apollo-qvp.lua` | 유일한 canonical full-system entrypoint |
| `hw-block/ap_compute.lua` | full-system AP CPU, GIC, SMMU/GPEX, timer와 reset 소유 |
| `hw-block/ros.lua` | full-system AP-visible virtio, RTC 등 RoS peripheral 소유 |
| `hw-block/si_cl1.lua` | full-system live CL1 구현 |
| `hw-block/config.lua`, `fabric.lua`, machine contract 파일 | topology, address view, route와 shared policy의 기준 |
| `QBOX_APOLLO_PCIE_IRQ_TEST` | `PC` 문자열과 무관하게 full-system `ap_compute.lua`와 `signal_routes.lua`도 사용 |
| `QBOX_APOLLO_FULL_SI_CL1_*` | full-system CL1 artifact, UART, TCG와 trace 계약 |
| `fw/arm64_bootloader.lua` | QBox core의 Ubuntu AArch64 platform도 사용 |
| Cortex-R82, GIC, UART, MHU, timer component | full-system CL0/CL1과 RSE child path에서도 사용 |

`CMakeLists.txt`의 `apollo_fvp_full_system` aggregate target에서도 Lua 파일
이름을 직접 나열하지 않는다. standalone 파일에서만 보이는
`char_backend_stdio`, `cpu_arm_cortexR82`, `sbsa_gwdt` literal만 보고
component target을 삭제해서는 안 된다. RSE child runner와 full-system의
external-counter CPU dynamic library가 같은 build target을 요구한다.
이번 제거 범위에서는 CMake component target 삭제 후보를 확정하지 않는다.

## 7. 문서 정리 정책

현재 `doc/`에는 standalone 경로를 현재 기능으로 설명하는 문서와 과거
bring-up 증거를 기록한 문서가 섞여 있다.

### 7.1 현재 상태 문서

다음 종류의 문서는 standalone 경로를 삭제한 동일 변경에서 갱신한다.

- Apollo machine architecture와 hardware inventory
- QBox bus/subsystem integration guide
- full-system runbook, goal verification와 task contract
- local GDB/debug 사용법
- QBox Platform 및 Apollo platform README
- project `AGENTS.md`와 project-local qbox-dev workflow

현재 구조를 설명하는 표에서 `apollo-pc.lua`, `primary_compute.lua`,
`apollo-si-cl1.lua`, `si_cl1_isolated.lua`를 제거하고
`apollo-qvp.lua`의 full-system 실행법으로 통일한다.

### 7.2 과거 계획 및 완료 보고서

날짜가 있는 plan, completion report와 coverage ledger는 과거 사실을
보존한다. 해당 문서의 과거 명령과 파일명을 모두 지우면 당시 증거의
추적성이 떨어진다.

필요하면 문서 머리에 다음과 같은 상태 주석만 추가한다.

```text
상태: 이 문서는 당시 standalone bring-up 증거를 기록한다.
현재 runtime에서는 해당 standalone 진입점이 제거됐으며
apollo-qvp full-system 경로를 사용한다.
```

## 8. 권장 제거 순서

저장소 경계를 지키기 위해 두 atomic change로 나누는 것이 적절하다.

### 8.1 qbox-platform 소유 변경

1. 네 개의 standalone Lua 파일을 삭제한다.
2. QBox Platform README와 Apollo README에서 두 진입점을 제거한다.
3. `apollo-qvp.lua`, `ap_compute.lua`, `si_cl1.lua`만 canonical
   platform 조립 경로로 남았는지 확인한다.
4. qbox-platform 저장소에서 standalone 파일명과 isolated 환경변수
   참조가 남지 않았는지 검사한다.

### 8.2 상위 저장소 소유 변경

1. 두 standalone runner와 전용 test를 삭제한다.
2. full runner의 `--isolated` 분기를 삭제한다.
3. map, ownership, AP memory audit와 profile/fault test를 full-system
   기준으로 수정한다.
4. completion verifier의 G1과 QAP-FULL-020 계약을 수정한다.
5. 활성 문서, `AGENTS.md`와 qbox-dev workflow를 갱신한다.

호환 wrapper나 존재하지 않는 Lua로 redirect하는 shim은 추가하지 않는다.
standalone 기능 제거가 목적이므로 실패를 숨기는 compatibility path는
복잡도만 남긴다.

## 9. 검증 기준

### 9.1 정적 검증

제거 구현 후 다음 문자열은 활성 소스, runner, test와 현재 상태 문서에서
사라져야 한다.

```text
apollo-pc.lua
primary_compute.lua
apollo-si-cl1.lua
si_cl1_isolated.lua
QBOX_APOLLO_SI_CL1_
--isolated
```

날짜가 있는 과거 보고서에 남은 문자열은 허용하되 현재 기능으로 안내하지
않아야 한다.

적용할 기본 검증은 다음과 같다.

```bash
python3 -m py_compile scripts/run/*.py scripts/test/*.py
python3 scripts/test/validate_qbox_apollo_fvp_full_map.py
python3 scripts/test/audit_qbox_apollo_lua_ownership.py
python3 scripts/test/audit_qbox_apollo_ap_memory_map.py
python3 scripts/test/audit_qbox_core_boundary.py

pytest -q \
  tests/test_run_qbox_apollo_fvp_full.py \
  tests/test_apollo_qvp_pcie_irq_profile.py \
  tests/test_apollo_qvp_fault_event_plane.py
```

### 9.2 build와 runtime 검증

Lua 구문과 component dependency는 실제 QBox build로 확인한다.

```bash
./local_build.sh qbox
```

최종 runtime은 standalone smoke가 아니라 live CL0/CL1을 포함한 canonical
full-system으로 검증한다.

```bash
python3 scripts/run/run_qbox_apollo_fvp_full.py \
  --si-mode live-cl0-cl1 \
  --timeout 600

python3 scripts/test/audit_qbox_apollo_fvp_full_coverage.py \
  --result-json <full-system-result.json> \
  --output build/qbox-apollo-qvp/full-coverage-audit.json
```

통과 조건은 다음과 같다.

- RSE, SI CL0, SI CL1과 AP가 같은 Apollo QVP process에서 실행된다.
- SI CL1 PFDI와 AP HIPC/RPMsg를 포함한 domain 간 상호작용이 통과한다.
- AP Linux login과 필요한 post-login probe가 통과한다.
- map validator, ownership audit와 coverage audit가 standalone 파일 없이
  통과한다.
- result JSON과 domain별 UART log가 저장된다.

## 10. 위험과 결정 사항

### 10.1 의도된 기능 손실

제거 후에는 firmware chain을 우회한 빠른 AP Linux boot와 CL1만 실행하는
짧은 Zephyr smoke test를 사용할 수 없다. AP와 CL1 문제도 full-system
artifact와 runner로 재현해야 한다. 이는 이번 정리의 의도된 결과다.

### 10.2 검증 시간 증가

full-system boot는 standalone보다 느리다. 대신 AP/SI/RSE 사이의 실제
reset, timer와 message path를 함께 검증한다. 빠른 정적·component test를
먼저 실행하고 full-system runtime을 최종 gate로 사용하는 방식으로
개발 시간을 관리한다.

### 10.3 completion gate 변경

현재 G1은 direct boot 결과를 필수 guardrail로 사용한다. Lua만 먼저
삭제하면 최종 검증은 구조적으로 통과할 수 없다. G1의 제거 또는
full-system AP probe로의 재정의는 선택 사항이 아니라 필수 후속 변경이다.

### 10.4 저장소 외부 사용자

저장소 내부 참조는 위 후보에 포함했지만 out-of-tree script가
`apollo-pc.lua`, `apollo-si-cl1.lua` 또는 두 Python runner를 직접
호출할 가능성은 로컬 검색으로 확인할 수 없다. 제거 commit과 release
note에는 네 Lua 경로, 두 runner와 환경변수 계약이 종료된다는 사실을
명시해야 한다.

## 11. 최종 권고

두 standalone 경로는 초기 bring-up과 full-system 회귀 guardrail로 실제
사용됐으므로 “원래부터 불필요했던 코드”라고 표현하면 안 된다. 현재
Apollo QVP가 RSE, live SI CL0/CL1과 AP를 통합 실행하는 단계에 도달했고,
사용 정책도 full-system 단일 진입점으로 바뀌었기 때문에 제거할 수 있는
정책 기반 후보다.

권고 범위는 다음과 같다.

1. 네 standalone Lua 파일을 삭제한다.
2. 두 standalone runner와 전용 test를 삭제한다.
3. full runner의 isolated compatibility 분기와 isolated milestone
   contract를 삭제한다.
4. direct boot G1은 full-system AP probe로 재정의한다.
5. full-system `ap_compute.lua`와 `si_cl1.lua`를 유일한 구현으로 유지한다.
6. 활성 문서와 project workflow를 full-system 명령으로 통일한다.

이 범위가 완료되면 Apollo QVP Lua의 subsystem 구현은 하나의
`apollo-qvp.lua` 조립 경로와 domain별 module로 수렴하고, AP와 SI CL1의
병렬 platform drift를 제거할 수 있다.
