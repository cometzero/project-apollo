# Apollo QVP Machine Architecture 개선 계획

작성일: 2026-07-15

상태: 실행 계획

상위 설계: [Apollo QVP Machine Architecture 비교 및 개선안](apollo-qvp-machine-architecture-ko.md)

## 1. 목표

현재 Apollo QVP의 단일 `host_router` 중심 구조를 Arm Zena CSS의 AP, SMD,
RSE, Safety Island address-space 경계와 ATU/APU 정책이 드러나는 계층형 machine
구조로 전환한다. 부팅을 유지하는 것뿐 아니라 잘못된 접근이 실패하고,
interrupt/reset/fault route가 검증 가능해야 한다.

### 1.1 From / To

| 현재 | 목표 |
| --- | --- |
| AP/SMD/SI local map과 system map이 `host_router`에 혼재 | `system_router`, `ap_router`, `smd_router`, `rse_router`, `si_cl0_router`, `si_cl1_router` 분리 |
| priority와 alias로 도메인 주소 충돌 해결 | 명시적 address view와 ATU/APU bridge로 해결 |
| 조립 중 다른 블록의 target priority 변경 | declarative contract를 검증한 뒤 topology freeze |
| 정상 boot 중심 validation | positive/negative access, IRQ, reset, fault, boot의 다층 validation |
| CPU/DRAM 값이 Lua와 Yocto/FVP에 분산 | build manifest 또는 명시 option으로 단일 resolve |
| block 존재 여부 중심 coverage | fidelity와 외부 side effect 중심 coverage |

## 2. 실행 원칙

- 변경은 주소 topology부터 시작하고 새 peripheral 추가를 먼저 하지 않는다.
- 기존 QBox core `router`와 `addrtr`를 재사용한다.
- Apollo 전용 map, APU policy와 route data는
  `hsoc-stack/tools/qbox-platform`에 둔다.
- 한 단계마다 좁은 정적/단위 검사를 통과한 뒤 build와 runtime으로 넓힌다.
- 기존 live CL0/CL1 boot path는 단계별 전환 동안 비교 기준으로 보존하되,
  최종 단계에서 broad pass-through와 priority hack을 제거한다.
- 생성물은 `build/qbox-apollo-fvp/` 아래에 두고 source와 섞지 않는다.
- 각 commit은 owning repository 경계에서 Conventional Commit과 `-s`를 사용한다.

## 3. 성공 기준

1. 모든 initiator와 target이 정확히 하나의 local/system view에 소속된다.
2. 문서화되지 않은 overlap, alias, dangling route가 정적 검사에서 실패한다.
3. RSE 이외 initiator의 reset 직후 cross-domain 접근이 `DECERR` 또는 정책에
   맞는 오류로 실패한다.
4. ATU/APU programming 후 허용된 window만 접근할 수 있다.
5. active Yocto 설정의 CPU 수와 deploy DTB의 memory bank가 QVP result와 같다.
6. AP, RSE, SI CL0/CL1 boot와 주요 MHU/SCMI/PFDI handoff가 유지된다.
7. IRQ, reset, power, safety fault의 source-to-sink route가 machine-readable
   evidence로 남는다.
8. FVP/QVP 비교 결과가 memory map, 접근 정책, IRQ와 boot milestone별로 기록된다.

## 4. 산출물 구조

아래 경로명은 계획안이며 실제 구현 전 owning repository의 기존 naming과 CMake
구조를 다시 확인한다.

| 산출물 | 제안 경로 | 역할 |
| --- | --- | --- |
| topology contract | `hsoc-stack/tools/qbox-platform/platforms/apollo/hw-block/topology.lua` | domain, view, bridge와 target 정의 |
| address contract | `.../platforms/apollo/hw-block/address_map.lua` | 문서 근거가 있는 range와 access policy |
| signal contract | `.../platforms/apollo/hw-block/signal_routes.lua` | IRQ/reset/clock/power/fault route |
| topology validator | `scripts/test/validate_qbox_apollo_topology.py` | overlap, width, route, policy 정적 검사 |
| generated manifest | `build/qbox-apollo-fvp/topology/topology.json` | resolved machine topology 증거 |
| route evidence | `build/qbox-apollo-fvp/topology/{address,irq,reset}-routes.json` | runtime/static route 증거 |
| differential report | `build/qbox-apollo-fvp/comparison/<timestamp>/` | FVP/QVP 비교 결과 |
| fidelity ledger | 기존 `doc/apollo-qbox-full-model/coverage-ledger.md` 갱신 | 기능/호환/backing/placeholder 상태 |

`...`는 `hsoc-stack/tools/qbox-platform`을 뜻한다.

## 5. 단계 및 의존성

```text
A0 기준선 고정
  |
A1 선언적 contract/validator
  |
A2 AP view 분리 ----+
  |                 |
A3 SI CL0/CL1 분리  |
  |                 |
A4 system/SMD + APU/ATU 정책
  |
A5 memory/DMI/config 정합
  |
A6 IRQ/reset/power/fault route
  |
A7 기능 gap 승격
  |
A8 FVP differential + 완료 gate
```

A2와 A3의 준비 작업은 병렬 가능하지만, `host_router`의 broad 경로를 제거하는
전환은 A4의 system bridge와 APU 정책이 준비된 뒤 수행한다.

## 6. 상세 작업 계획

### A0. 기준선과 현재 topology 고정

목적은 구현 변경 전 현재 machine이 무엇을 제공하는지 재현 가능한 자료로
고정하는 것이다.

#### 작업

- `ARCH-000`: active `local.conf`, `bblayers.conf`, `templateconf.cfg`의 machine,
  variant, CPU 수, TMPDIR를 manifest에 기록한다.
- `ARCH-001`: 현재 Lua instance, socket binding, address/size/priority/alias를
  추출해 baseline JSON을 생성한다.
- `ARCH-002`: AP/RSE/SI CPU 수, GIC type, memory bank, enabled live domain을
  full-system result에 기록한다.
- `ARCH-003`: 기존 architecture/coverage 문서의 stale 항목을 현재 revision과
  대조한다. 특히 QBox CPU 기본값과 FMU/SSU/RGIC 모델 상태를 바로잡는다.

#### 완료 조건

- 동일 checkout에서 baseline JSON을 반복 생성해 내용이 안정적이다.
- 현재 full map validator와 core-boundary audit가 통과한다.
- runtime을 수행한 경우 모든 log와 result 경로가 manifest에 연결된다.

### A1. 선언적 topology contract와 정적 validator

#### 작업

- `ARCH-100`: domain/view, local/system range, target, bridge, owner, access,
  fidelity 필드를 정의한다.
- `ARCH-101`: 현재 `config.lua`의 주소 상수를 contract로 옮기되 한 번에 runtime
  binding을 바꾸지 않는다.
- `ARCH-102`: 다음 오류를 검출하는 validator를 추가한다.
  - 같은 view의 문서화되지 않은 overlap
  - target range overflow와 32/40/48/52-bit 경계 위반
  - 존재하지 않는 target/bridge/initiator 참조
  - cross-domain route에 ATU/APU가 없는 경우
  - priority/alias에 이유, source 또는 owner가 없는 경우
  - backing 복제와 DMI alias 불일치
- `ARCH-103`: resolved topology를 정렬된 JSON으로 내보내 diff 가능한 evidence로
  만든다.

#### 완료 조건

- 현재 map을 contract로 표현해 기존 주소 검사와 같은 범위를 통과한다.
- 의도적으로 overlap 또는 잘못된 width를 넣은 fixture가 반드시 실패한다.
- validator는 QBox 실행 없이 동작한다.

### A2. AP physical address view 분리

#### 작업

- `ARCH-200`: 현재 `ap_view_router`를 조건부 보조 router가 아닌 `ap_router`로
  승격한다.
- `ARCH-201`: AP CPU/global initiator, GIC/ITS, SMMU, GPEX, DRAM, flash, AP
  peripheral과 RoS를 모두 AP view에 직접 bind한다.
- `ARCH-202`: AP→SMD logical window를 명시적 ATU target으로만 연결한다.
- `ARCH-203`: `prepare_live_cl0_integration()`이 AP target priority를 변경하지
  않도록 조립 순서를 제거한다.
- `ARCH-204`: AP view의 unmapped/reserved/error-response unit test를 추가한다.

#### 완료 조건

- live CL0 유무가 AP bus topology를 바꾸지 않는다.
- AP initiator가 SI local target을 같은 숫자 주소로 직접 접근할 수 없다.
- AP 단독 direct-boot와 full-system boot가 모두 기존 milestone에 도달한다.

### A3. Safety Island CL0/CL1 address view 분리

#### 작업

- `ARCH-300`: `si_cl0_router`와 `si_cl1_router`를 만들고 CPU, loader, local SRAM,
  GIC view, timer, UART, MHU를 해당 view에 bind한다.
- `ARCH-301`: CL0/CL1 local address와 SMD/system address를 분리한다.
- `ARCH-302`: SI ATU window와 40-bit system bridge를 명시한다.
- `ARCH-303`: `si_cl1.lua`의 `temporary merged bus` 및 관련
  `lower_decode_priority()` 호출을 제거한다.
- `ARCH-304`: GIC view 0/1/2의 register visibility와 interrupt ownership test를
  추가한다.
- `ARCH-305`: CL0-only, CL1-only, live CL0+CL1 세 구성의 topology test를 만든다.

#### 완료 조건

- SI local target이 root/system router에 직접 등록되지 않는다.
- 같은 local 주소의 CL0/CL1/AP target이 priority 없이 구분된다.
- CL0과 CL1 firmware의 UART, MHU, timer, GIC boot evidence가 유지된다.

### A4. System/SMD router와 ATU/APU 접근 정책

#### 작업

- `ARCH-400`: 52-bit top nibble만 decode하는 `system_router`를 도입한다.
- `ARCH-401`: SMD shared SRAM, CSS control, counter, RGM/PPU와 ATU를
  `smd_router`로 이동한다.
- `ARCH-402`: AP, RSE, SI bridge의 address width와 target domain을 검증한다.
- `ARCH-403`: initiator identity와 secure/non-secure 속성을 받는 APU policy
  component를 구현한다.
- `ARCH-404`: reset 상태의 RSE-only access, RSE programming 후 allow-list와
  lock 동작을 구현한다.
- `ARCH-405`: 차단, 범위 밖, reserved, read-only write에 대한 응답을
  `DECERR`/`SLVERR`/RAZ/WI contract에 맞게 시험한다.
- `ARCH-406`: broad AP 1:1 passthrough를 제거하고 모든 cross-domain route를
  manifest와 일치시킨다.

#### 완료 조건

- reset 직후 RSE만 SMD/RSE/SI 관리 자원에 접근 가능하다.
- ATU window 밖과 APU deny 접근이 target side effect 없이 실패한다.
- RSE가 구성한 허용 window만 AP/SI에서 성공한다.
- system router의 reserved top-level region은 항상 오류를 반환한다.

### A5. Memory backing, DMI와 build configuration 정합

#### 작업

- `ARCH-500`: AP shared SRAM 128 MiB aperture와 실제 allocated backing 정책을
  분리해 선언한다.
- `ARCH-501`: SMD/AP/RSE/SI가 공유하는 메모리 view를 단일 backing에 연결한다.
- `ARCH-502`: low/high DRAM bank를 deploy DTB, FVP config와 local build manifest에서
  resolve한다.
- `ARCH-503`: single-chip과 multichip high DRAM layout을 명시 구성으로 분리한다.
- `ARCH-504`: ATU/alias DMI range translation, clipping, invalidation test를
  추가한다.
- `ARCH-505`: active Yocto `PC_CPUS_COUNT_DEFAULT=4`와 QBox source default 16의
  불일치를 제거한다. runner가 결정한 값을 result JSON에 기록한다.
- `ARCH-506`: DT CPU node, GIC redistributor 수, PPU/reset signal 수의 일관성을
  정적 검사한다.

#### 완료 조건

- CPU 수와 DRAM bank가 DT/manifest/QVP result에서 동일하다.
- 모든 shared memory view가 같은 backing content를 관찰한다.
- remap과 write 후 stale DMI가 남지 않는다.

### A6. IRQ, reset, clock, power, safety route 명시화

#### 작업

- `ARCH-600`: AP GIC, SI GIC view와 RSE NVIC route를 선언적 manifest로 옮긴다.
- `ARCH-601`: CPU generic timer PPI와 AP REFCLK SPI 48/49를 분리 검증한다.
- `ARCH-602`: MHU peer, receiver IRQ, SCMI/PFDI channel을 쌍으로 검증한다.
- `ARCH-603`: FMU critical/non-critical→SSU→GIC/reset escalation route를
  end-to-end로 시험한다.
- `ARCH-604`: RGM/PPU에서 domain/core reset까지의 signal graph와 reset order를
  모델링한다.
- `ARCH-605`: clock-disabled 또는 power-off target의 접근/IRQ 동작을 정의한다.
- `ARCH-606`: duplicate interrupt ID, dangling signal, 잘못된 GIC view를
  validator failure로 만든다.

#### 완료 조건

- 모든 source가 하나의 의도된 sink 또는 명시적 fan-out을 가진다.
- reset 전후 pending IRQ, timer와 MHU state가 규정된 값으로 돌아간다.
- fault injection 결과가 QVP log와 route evidence에 남는다.

### A7. 우선 기능 gap 승격

topology 안정화 후 software가 실제로 관찰하는 placeholder를 순서대로
기능 모델로 바꾼다.

| 순서 | 대상 | 필요한 최소 동작 |
| --- | --- | --- |
| 1 | AP secure watchdog | control/refresh, expiry, IRQ/reset, lock/security |
| 2 | SMD RGM/SYSTOP/DBGTOP | reset cause, request/ack, PPU/clock 연계 |
| 3 | RSE OTP/identity/control/integration | lifecycle/identity 값, write policy, reset state |
| 4 | SI DCLS/fault path | lock-step error injection과 FMU/SSU escalation |
| 5 | NI/CMN/APU semantics | discovery를 넘어 access deny/error/fault state |
| 6 | RoS 누락 항목 | 실제 image/DT가 요구하는 system register, p9/VSI/UART만 선택 구현 |

각 모델은 register coverage보다 firmware-visible state transition과 외부
side effect를 acceptance criterion으로 삼는다.

### A8. FVP differential validation과 완료 판정

#### 작업

- `ARCH-800`: 동일한 build artifact로 FVP와 QVP를 실행하고 topology/config
  manifest를 함께 보존한다.
- `ARCH-801`: UART milestone, MHU/SCMI/PFDI handoff, CPU 수, DT probe를 비교한다.
- `ARCH-802`: 주소별 read/write/error, ATU/APU allow/deny와 IRQ/fault injection
  test vector를 양쪽에서 실행한다.
- `ARCH-803`: 차이를 `동등`, `의도된 추상화`, `부분 모델`, `blocker`로 분류한다.
- `ARCH-804`: coverage ledger와 roadmap을 최신 evidence에 맞춰 갱신한다.
- `ARCH-805`: broad pass-through, temporary merged bus와 undocumented priority가
  소스에서 사라졌음을 검사한다.

#### 완료 조건

- 아래 G0–G5 gate가 모두 통과한다.
- 남은 fidelity gap은 주소, 영향, 근거, 대체 계획과 함께 문서화된다.
- source revision, command, result JSON, log와 판정이 한 evidence bundle에 있다.

## 7. 검증 Gate

| Gate | 범위 | 필수 증거 |
| --- | --- | --- |
| G0 | 정적 map/topology | 기존 map validator, 신규 topology validator, core boundary audit |
| G1 | domain isolation | AP/SI/RSE view positive/negative unit test와 overlap 없음 |
| G2 | ATU/APU policy | reset deny, RSE program, allow/deny/error response trace |
| G3 | IRQ/reset/fault | route manifest, injection test, reset-state 검증 |
| G4 | QBox full-system | RSE, SI CL0/CL1, AP boot result와 coverage audit |
| G5 | FVP comparison | 같은 artifact의 FVP/QVP differential report와 gap ledger |

### 7.1 단계별 명령

현재 존재하는 기본 검사는 다음과 같다.

```bash
python3 scripts/test/validate_qbox_apollo_fvp_full_map.py
python3 scripts/test/audit_qbox_core_boundary.py
git -C hsoc-stack/tools/qbox-platform diff --check
git -C hsoc-stack/tools/qbox diff --check
```

A1에서 추가할 검사는 다음 interface를 목표로 한다.

```bash
python3 scripts/test/validate_qbox_apollo_topology.py \
  --emit build/qbox-apollo-fvp/topology/topology.json
```

구현 단계의 targeted build와 test는 다음 순서로 확대한다.

```bash
cmake --build build/local-apollo-qvp/work/qbox-platform \
  --target platforms-vp --parallel "$(nproc)"

./local_build.sh qbox

python3 scripts/run/run_qbox_apollo_fvp_full.py \
  --si-mode live-cl0-cl1 --timeout 600

python3 scripts/test/audit_qbox_apollo_fvp_full_coverage.py \
  --result-json <runtime-result.json> \
  --output build/qbox-apollo-fvp/full-coverage-audit.json
```

FVP 비교는 local artifact를 만든 뒤 log 기반으로 수행한다.

```bash
python3 scripts/run/runfvp_log_boot.py \
  --machine apollo-fvp \
  --fvpconf build/local-apollo-fvp/deploy/apollo-fvp-local.fvpconf \
  --out-dir build/local-apollo-fvp/fvp-boot \
  --timeout 900 --require all --min-runtime 70 --no-login
```

build directory 이름은 실제 `local_build.sh` 산출물에서 확인하고 사용한다.
존재하지 않는 경로를 고정값으로 가정하지 않는다.

## 8. Test matrix

| 축 | 최소 조합 |
| --- | --- |
| AP CPU | active 기본 4, 최대 topology 16 |
| Safety Island | CL0 only, CL1 only, live CL0+CL1 |
| address | local hit, local miss, cross-domain allow, cross-domain deny, width overflow |
| security | secure/non-secure, RSE owner/non-owner |
| ATU | reset, programmed, locked, out-of-window |
| memory | low DRAM, high DRAM, shared SRAM alias, DMI on/off |
| interrupt | AP PPI/SPI, SI GIC view 0/1/2, RSE NVIC, MHU, FMU/SSU |
| lifecycle | cold reset, warm reset, CPU/domain reset, watchdog expiry |
| runtime | AP direct boot, RSE-focused, full-system, FVP reference |

## 9. 위험과 대응

| 위험 | 대응 |
| --- | --- |
| router 분리 직후 firmware의 암묵적 alias가 깨짐 | baseline trace로 실제 initiator/address를 수집하고 한 domain씩 전환 |
| APU 도입으로 초기 boot가 모두 차단됨 | RSE reset allow-list와 firmware programming 시점을 unit test로 먼저 고정 |
| shared memory를 합치면서 file-backed IPC가 회귀 | backing identity와 map file을 manifest에 남기고 CL0/CL1 동시 test 수행 |
| DMI가 bridge 정책을 우회함 | deny 영역은 DMI 금지, translated range clip/invalidate test 의무화 |
| FVP와 QVP의 추상화 수준 차이로 false mismatch 발생 | register 값, side effect, timing tolerance를 각각 분리 판정 |
| 기존 문서가 source보다 뒤처짐 | revision을 문서에 고정하고 generated topology를 source of truth로 사용 |
| QBox core에 Apollo 전용 코드가 유입됨 | `audit_qbox_core_boundary.py`와 owning-repository review를 gate로 유지 |

## 10. 변경 및 commit 경계

예상 변경은 다음 경계로 나눈다.

1. **최상위 저장소**: validator, runner, project 문서와 generated evidence 규약
2. **qbox-platform**: Apollo topology/map/policy, platform-specific SystemC 모델,
   Lua binding과 platform test
3. **qbox core**: 재사용 가능한 router/addrtr/APU 기능이 기존 API로 불가능한
   경우에만 최소 변경
4. **qemu**: QEMU device가 실제로 필요하고 generic upstream path가 있을 때만
   별도 atomic 변경

한 commit에 여러 저장소 변경을 섞지 않는다. 예시 commit 단위는 다음과 같다.

- `docs(apollo): define target machine architecture`
- `test(apollo): validate topology contract`
- `refactor(apollo): isolate AP address view`
- `refactor(apollo): isolate safety address views`
- `feat(apollo): enforce system APU policy`
- `test(apollo): compare FVP and QVP routes`

## 11. 단계별 중단 및 복구 기준

각 단계는 이전 단계의 evidence를 보존한다. 다음 상태에서는 다음 단계로
진행하지 않는다.

- 정적 topology가 중복 target 또는 undocumented overlap을 포함함
- negative access가 실제 target의 side effect를 발생시킴
- CPU/DRAM topology가 DT와 다름
- RSE, CL0, CL1 또는 AP 중 하나의 earliest boot milestone이 기준선보다 후퇴함
- runtime result가 source revision과 resolved config를 기록하지 않음

복구는 변경한 domain의 binding만 이전 topology로 되돌리는 atomic revert가
가능해야 한다. user/generated state나 다른 submodule을 reset하지 않는다.

## 12. 최종 완료 체크리스트

- [ ] `system_router`가 system-wide address만 담당하며, 현 `host_router`의
      local-map 역할은 제거되어 있다.
- [ ] AP, SMD, RSE, SI CL0, SI CL1 router가 분리되어 있다.
- [ ] `ap_view_passthrough` broad mapping이 없다.
- [ ] `temporary merged bus`와 도메인 충돌 해소용 priority 변경이 없다.
- [ ] 모든 cross-domain route가 ATU/APU manifest에 존재한다.
- [ ] reset default-deny와 RSE programming test가 통과한다.
- [ ] CPU, GIC, PPU와 DT topology가 일치한다.
- [ ] memory backing/view/DMI test가 통과한다.
- [ ] IRQ/reset/power/fault route가 machine-readable evidence로 생성된다.
- [ ] AP secure watchdog, SMD RGM 등 P1 placeholder가 기능 모델로 승격된다.
- [ ] QBox full-system G0–G4가 통과한다.
- [ ] FVP differential G5가 통과하고 남은 gap이 명시되어 있다.
- [ ] roadmap, Apollo platform README와 fidelity ledger가 최신 상태다.

## 13. 이번 문서화 시점의 검증 상태

2026-07-15 기준 다음 정적 검사는 통과했다.

```text
python3 scripts/test/validate_qbox_apollo_fvp_full_map.py
  -> passed: true

python3 scripts/test/audit_qbox_core_boundary.py
  -> QBox core boundary audit passed
```

이 결과는 현재 주소 상수와 binding 패턴 및 core 경계를 확인한 것이다. 독립
address view, APU negative access, IRQ/fault side effect 또는 FVP functional
parity 완료를 의미하지 않는다. 이번 작업은 architecture와 plan 문서 작성
범위이므로 QBox/FVP runtime은 새로 실행하지 않았다.
