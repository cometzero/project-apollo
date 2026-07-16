# Apollo QVP Machine Architecture 개선 계획

작성일: 2026-07-15, 최종 갱신 2026-07-16

상태: QBox / system hardware / system software / QEMU 및 Arm Zena CSS
하드웨어 블록 다이어그램 리뷰 반영, A0–A4 구조 전환 구현·검증 완료

상위 설계: [Apollo QVP Machine Architecture 비교 및 개선안](apollo-qvp-machine-architecture-ko.md)

4 CPU 우선 후속 fidelity 계획:

- [Fidelity 부채 아키텍처 설계](apollo-qvp-fidelity-debt-architecture-design-ko.md)
- [Fidelity 부채 구현 계획](apollo-qvp-fidelity-debt-implementation-plan-ko.md)
- [Fidelity 부채 검증 계획](apollo-qvp-fidelity-debt-validation-plan-ko.md)

## 1. 목표

Apollo QVP의 기존 단일 `host_router` 중심 구조를 Arm Zena CSS의 AP, SMD,
RSE, Safety Island address-space 경계와 ATU/APU 정책이 드러나는 계층형 machine
구조로 전환한다. A2/A3의 AP/SI local view와 A4의 SMD runtime router,
ATU/static allow-list 전환까지 완료했다. 다음 단계는 완전한 APU/request context,
interrupt/reset/fault side effect와 software error ABI를 닫는 것이다.

### 1.1 From / To

| 현재 | 목표 |
| --- | --- |
| `system_router`, AP/SMD/RSE/SI local router와 ATU/static window 분리 완료 | 완전한 APU/request context와 fault side effect까지 정책화 |
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
  A4에서 broad pass-through와 priority hack을 제거했으며 이후 회귀로 다시
  도입하지 않는다.
- 신규 full-system QVP 생성물의 표준 경로는 `build/qbox-apollo-qvp/`로
  통일한다. full-system runner, coverage audit와 README는 이전됐고 직접 부팅
  legacy runner의 경로는 실제 provenance를 유지한 채 별도 후속 정리한다.
- 각 commit은 owning repository 경계에서 Conventional Commit과 `-s`를 사용한다.

## 3. 성공 기준

1. 모든 initiator와 target이 정확히 하나의 local/system view에 소속된다.
2. 문서화되지 않은 overlap, alias, dangling route가 정적 검사에서 실패한다.
3. RSE 이외 initiator의 reset 직후 cross-domain 접근이 `DECERR` 또는 정책에
   맞는 오류로 실패한다.
4. ATU/APU programming 후 허용된 window만 접근할 수 있다.
5. active Yocto 설정의 CPU 수와 deploy DTB의 memory bank가 QVP result와 같다.
6. AP, RSE, SI CL0/CL1 boot와 주요 MHU/SCMI/PFDI handoff가 유지된다.
7. 구현한 IRQ, reset, power 또는 safety fault의 source-to-sink smoke evidence가
   남는다.
8. FVP/QVP focused marker를 비교하거나 `deferred` 사유를 기록한다.
9. 변경한 QBox/QEMU access path가 대표 allow/deny에서 동일한 보안·도메인 정책을
   따른다.
10. CPU뿐 아니라 PCIe/GPEX DMA initiator의 requester/StreamID가 SMMU와 APU
    정책까지 보존되고 MSI/LPI/ITS 경로가 검증된다.
11. RSE가 설정하는 ATU/APU와 SI CL0가 설정·검증하는 CMN/GIC/peripheral의
    소유권 및 순서가 boot contract와 runtime trace에서 일치한다.
12. 변경한 software protocol의 대표 오류와 다음 정상 request가 firmware/OS-visible
    ABI와 side effect 기준으로 통과한다.

## 4. 네 관점 및 하드웨어 다이어그램 리뷰 결과

### 4.1 관점별 판정

| 관점 | 기존 계획의 부족한 점 | 이번 계획의 보완 방향 |
| --- | --- | --- |
| QBox/SystemC | router 분리는 있었지만 TLM payload extension, debug/DMI 경로, lifecycle와 관측성이 gate가 아니었음 | 기존 `router`/`addrtr`와 `QemuMemTxAttrsTlmExtension`을 재사용하고, 속성 보존·응답 변환·DMI 무효화·trace를 별도 acceptance로 둠 |
| system hardware | 주소 view 중심이라 CMN/NCI 계층, DMA/SMMU/ITS, clock/reset/power 및 FMU/SSU/RAS 경로가 약했음 | Zena CSS 블록 경계를 유지한 계층형 fabric과 transaction/signal contract를 분리하고, PCIe DMA부터 SMMU·ITS까지 end-to-end 검증함 |
| system software | boot marker는 있었지만 RSE/SI CL0의 제어권 분담과 SCMI/PFDI/HIPC 등의 ABI가 상세 gate가 아니었음 | boot/control ownership, DT와 firmware 상수, shared-memory layout, protocol error/timeout까지 software contract로 관리함 |
| QEMU | CPU/GIC 존재 여부 위주였고 qdev reset, BQL, async job, quantum keeper, RAM/AddressSpace 소유권과 MemTx 오류 전달이 빠졌음 | QEMU instance별 backend와 RAM owner를 명시하고 reset·WFI·MTTCG timing 및 `MemTxResult`→TLM→CPU abort 경로를 시험함 |

### 4.2 Arm Zena CSS 블록 다이어그램에서 도출한 설계 제약

검토한 high-level, System Management Block, Compute Complex, SCMI, SI GIC
multiple-view, boot/reset, FMU/SSU 및 PFDI 그림은 다음 제약을 공통으로
보여준다.

1. AP, RSE, Safety Island와 Debug/System Control은 한 평면 bus가 아니라
   CMN/NCI/NI를 경계로 연결된다. QVP도 편의를 위한 단일 root decode가 아니라
   각 initiator view와 명시적 bridge를 유지해야 한다.
2. RSE는 image 인증·적재와 ATU/APU 설정을 담당하고, SI CL0는 CMN, GIC,
   peripheral을 구성한 뒤 AP reset을 해제한다. SI는 RSE가 설정한 ATU와 SCR을
   read-back 검증하므로, 설정 동작만 모델링해서는 충분하지 않다.
3. GIC-720AE의 SI multiple view, AP GIC/ITS, I/O TCU/TBU와 PCIe/GPEX는 주소
   블록만이 아니라 requester identity, StreamID, MSI/LPI 및 fault route까지
   하나의 transaction graph로 연결되어야 한다.
4. RGM/PPU, clock/reset, FMU/SSU/ESM과 RAS는 독립 register island가 아니라
   boot, power, interrupt와 reset escalation을 바꾸는 signal graph다.
5. FVP CFG2의 추가 SI CL1은 reference-platform extension이다. 현재 silicon
   architecture contract와 FVP-only CFG2 extension을 manifest에서 구분하고,
   CL1을 모든 Zena CSS 구현의 필수 하드웨어로 오인하지 않는다.

### 4.3 리뷰 후 고정한 구현 결정

- 사람이 각각 유지하는 Lua/JSON 사본을 만들지 않는다. 하나의 declarative
  source에서 runtime binding과 정렬된 JSON evidence를 생성하거나, 기존 Lua를
  source로 유지할 경우 동일 Lua를 읽는 extractor를 사용한다.
- QBox core에 이미 있는 `QemuMemTxAttrsTlmExtension`과 router initiator ID
  stamping을 우선 사용한다. 현재 `MemTxAttrs`가 제공하지 않는 domain,
  requester와 StreamID만 재사용 가능한 최소 extension으로 보강한다.
- Apollo APU/ATU 정책과 boot ownership은 `qbox-platform`에 둔다. generic
  extension이나 bridge 수정이 다른 platform에도 유효할 때만 QBox core를
  변경한다.
- `transport_dbg`, image loader와 QEMU direct/reentrant access는 일반 functional
  access와 분리한다. 정책을 우회할 수 있는 경로는 신뢰된 loader/debug
  capability로 제한하고 manifest와 negative test에 남긴다.
- CMN/CHI는 cycle-accurate 구현을 1차 목표로 삼지 않는다. cache/coherency와
  ordering에 대해 software가 관찰할 수 있는 functional contract를 먼저
  만족하고, timing fidelity는 별도 gap으로 기록한다.
- QEMU source 변경은 기존 libqemu/QBox API로 표현할 수 없고 upstream 가능한
  generic 결함이 확인된 경우에만 수행한다.

## 5. 산출물 구조

아래 contract와 validator 경로는 이번 전환에서 구현됐다. focused comparison과
fidelity ledger는 후속 단계 산출물이다.

| 산출물 | 제안 경로 | 역할 |
| --- | --- | --- |
| topology contract | `hsoc-stack/tools/qbox-platform/platforms/apollo/hw-block/topology.lua` | 구현됨: domain, view, bridge와 target 정의 |
| address contract | `.../platforms/apollo/hw-block/address_map.lua` | 구현됨: 문서 근거가 있는 range와 access policy |
| transaction contract | `.../platforms/apollo/hw-block/transaction_routes.lua` | 선언 구현됨: initiator, security/domain, requester/StreamID, SMMU와 response 정의 |
| signal contract | `.../platforms/apollo/hw-block/signal_routes.lua` | 선언 구현됨: IRQ/MSI/LPI/reset/clock/power/fault route |
| boot/control contract | `.../platforms/apollo/hw-block/boot_control.lua` | 선언 구현됨: RSE/SI/AP 소유권, reset release와 read-back 순서 |
| software ABI contract | `.../platforms/apollo/hw-block/software_contract.lua` | 선언 구현됨: DT, SCMI/PSCI/MHU/PFDI/HIPC/FF-A/RAS 계약 |
| topology validator | `scripts/test/validate_qbox_apollo_topology.py` | 구현됨: overlap, width, route, policy 정적 검사 |
| generated manifest | `build/qbox-apollo-qvp/topology/topology.json` | resolved machine topology 증거 |
| route evidence | `build/qbox-apollo-qvp/topology/{address,transaction,irq,reset,boot,software}-routes.json` | runtime/static route 증거 |
| artifact manifest | `build/qbox-apollo-qvp/topology/artifacts.json` | source revision, image hash, QEMU backend, CCI와 runtime option |
| differential report | `build/qbox-apollo-qvp/comparison/<timestamp>/` | FVP/QVP 비교 결과 |
| fidelity ledger | 기존 `doc/apollo-qbox-full-model/coverage-ledger.md` 갱신 | 기능/호환/backing/placeholder 상태 |

`...`는 `hsoc-stack/tools/qbox-platform`을 뜻한다.

## 6. 단계 및 의존성

```text
A0 기준선 고정
  |
A1 선언적 contract + QBox/TLM 기반
  |
A2 AP view 분리 ----+
  |                 |
A3 SI CL0/CL1 분리  |
  |                 |
A4 system/SMD + APU/ATU 정책
  |
A5 memory/DMA/IOMMU/QEMU 정합
  |
A6 IRQ/reset/timing/power/safety route
  |
A7 기능 gap + system software ABI
  |
A8 local/Yocto smoke + focused FVP/완료 gate
```

A2와 A3의 준비 작업은 병렬 가능하지만, `host_router`의 broad 경로를 제거하는
전환은 A4의 system bridge와 APU 정책이 준비된 뒤 수행한다.

## 7. 상세 작업 계획

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
- `ARCH-004`: TF-M, SCP-firmware, TF-A, OP-TEE, U-Boot, Linux, Zephyr, DTB와
  rootfs의 path, revision, SHA-256 및 provenance를 artifact manifest에 남긴다.
- `ARCH-005`: 각 QEMU instance의 target architecture, machine/device, CPU model,
  acceleration, MTTCG/quantum, RAM/AddressSpace owner와 CCI parameter를 기록한다.
- `ARCH-006`: 4 CPU UART milestone과 종료 사유를 기록한다. simulated/wall time은
  hang 진단용 telemetry로만 남기고 performance 기준선이나 budget을 만들지 않는다.
- `ARCH-007`: 현재 runner/README/audit의 `build/qbox-apollo-fvp/` 기본값을
  `build/qbox-apollo-qvp/`로 이전하는 범위와 기존 evidence 보존 규칙을 고정한다.

#### 완료 조건

- 동일 checkout에서 baseline JSON을 반복 생성해 내용이 안정적이다.
- 현재 full map validator와 core-boundary audit가 통과한다.
- runtime을 수행한 경우 모든 log와 result 경로가 manifest에 연결된다.
- artifact hash와 QEMU/SystemC 실행 구성이 없으면 기준선 완료로 판정하지 않는다.
- 출력 경로 이전 전후 결과가 혼동되지 않고 각각 source revision에 연결된다.

### A1. 선언적 topology contract와 QBox/TLM 기반

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
- `ARCH-104`: secure/debug, initiator/domain, requester/StreamID, privilege와
  access kind를 포함하는 transaction contract를 정의한다. 기존
  `QemuMemTxAttrsTlmExtension` 및 router initiator ID와 중복되는 필드는 새로
  만들지 않는다.
- `ARCH-105`: `b_transport`, `transport_dbg`, DMI, loader와 QEMU
  direct/reentrant path별 정책 및 허용 capability를 contract에 명시한다.
- `ARCH-106`: IRQ/PPI/SPI/MSI/LPI, reset, clock, power, fault source와 sink를
  signal contract에 정의한다.
- `ARCH-107`: RSE, SI CL0, TF-A/Linux의 boot·power·reset 제어권과 설정/read-back
  순서를 boot/control contract에 정의한다.
- `ARCH-108`: DT 및 firmware header의 주소, IRQ, shared-memory, SCMI protocol와
  channel ID를 software ABI contract와 대조한다.
- `ARCH-109`: silicon architecture, RD-Aspen variant, FVP-only extension과 QVP
  abstraction을 각 block/range/route의 `scope` 필드로 구분한다.
- `ARCH-110`: SystemC module hierarchy, stable CCI path, socket direction과
  binding cardinality를 topology contract에서 검증하고 elaboration 종료 때
  unbound/multiply-bound socket을 fail-fast 처리한다.
- `ARCH-111`: router/addrtr가 `b_transport`뿐 아니라 `transport_dbg`와 DMI에서도
  initiator/domain extension을 보존·갱신하는 규칙을 unit test로 고정한다.
- `ARCH-112`: router/bridge별 hit, miss, deny, error, DMI grant/invalidate와
  latency counter를 bounded trace 및 result JSON으로 노출한다.

#### 완료 조건

- 현재 map을 contract로 표현해 기존 주소 검사와 같은 범위를 통과한다.
- 의도적으로 overlap 또는 잘못된 width를 넣은 fixture가 반드시 실패한다.
- validator는 QBox 실행 없이 동작한다.
- Lua/runtime binding과 JSON evidence는 동일 source에서 생성되고 수동 복제
  contract가 없다.
- 잘못된 requester/StreamID, dangling signal, boot owner와 software ABI fixture가
  정적 검사에서 실패한다.
- SystemC elaboration 종료 시 모든 필수 socket과 signal의 연결이 결정되어 있고,
  runtime 조립 순서에 따라 CCI path나 decode priority가 달라지지 않는다.

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
- `ARCH-205`: QEMU CPU와 GPEX initiator부터 `ap_router`를 거쳐 target까지 TLM
  extension이 복제·누락 없이 전달되는지 시험한다.
- `ARCH-206`: QEMU `MemTxOK`, `MemTxDecodeError`, `MemTxError`와 TLM response 및
  guest data/prefetch abort의 대응을 고정한다.
- `ARCH-207`: GPEX INTx SPI 300–303뿐 아니라 MSI→ITS→LPI 및 PCIe DMA→SMMU
  transaction 경로를 AP view에 포함한다.
- `ARCH-208`: AP SMMU의 `systemc-mmu720ae`와 `qemu-arm-smmuv3` 중 normative
  backend를 지정하고, 다른 backend는 호환 test matrix로 유지한다.
- `ARCH-209`: AP CPU 내부 generic timer PPI와 platform AP REFCLK 125 MHz
  MMIO frame/SPI 48·49의 소유권을 중복 없이 검사한다.

#### 완료 조건

- live CL0 유무가 AP bus topology를 바꾸지 않는다.
- AP initiator가 SI local target을 같은 숫자 주소로 직접 접근할 수 없다.
- AP 단독 direct-boot와 full-system boot가 모두 기존 milestone에 도달한다.
- PCIe DMA가 requester/StreamID 없이 SMMU/APU를 우회하지 않는다.
- AP access failure가 target side effect 없이 guest가 관찰하는 abort/error로
  전달된다.

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
- `ARCH-306`: CL0/CL1 CPU와 loader/debug access의 initiator/domain 속성 및
  trusted bypass 차이를 명시하고 negative test를 추가한다.
- `ARCH-307`: AP↔SI CL1 HIPC 512 KiB SRAM을 resource table 128 KiB, vring 2개
  각 128 KiB, buffer 128 KiB의 단일 backing으로 고정한다.
- `ARCH-308`: Linux remoteproc가 SI CL1을 AP가 부팅하는 대상이 아닌
  `detached` remote processor로 관찰하는지 검증한다.
- `ARCH-309`: SI GIC multiple-view의 접근 권한, interrupt owner와 view별 reset
  state를 firmware 실행 순서와 함께 시험한다.
- `ARCH-310`: CL1 관련 block과 route에 FVP CFG2 extension scope를 붙이고,
  architecture-only 구성에서도 validator가 동작하도록 한다.

#### 완료 조건

- SI local target이 root/system router에 직접 등록되지 않는다.
- 같은 local 주소의 CL0/CL1/AP target이 priority 없이 구분된다.
- CL0과 CL1 firmware의 UART, MHU, timer, GIC boot evidence가 유지된다.
- HIPC shared-memory 내용과 vring notification이 AP/SI 양쪽에서 동일하게
  관찰되고 remoteproc state가 contract와 일치한다.

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
- `ARCH-407`: Arm diagram의 SMD NCI, SI 내부 NCI와 system bridge 경계를
  manifest hierarchy로 표현하고 한 router로 flatten하지 않는다.
- `ARCH-408`: RSE BL2의 image 인증·적재와 NI-710AE APU 설정, 그리고
  RSE-owned firmware의 ATU 설정·lock state transition을 구분해 모델링한다.
- `ARCH-409`: SI CL0가 RSE의 ATU 및 SCR 설정을 read-back 검증하고 실패 시 AP
  reset을 해제하지 않는 경로를 구현·시험한다.
- `ARCH-410`: SI CL0의 CMN, GIC, peripheral 초기화와 AP reset release 순서를
  boot trace로 검증한다.
- `ARCH-411`: APU deny, unmapped, target failure와 read-only write를 각각 QEMU
  `MemTxResult`, TLM response, firmware-visible syndrome까지 추적한다.
- `ARCH-412`: functional access와 trusted debug/loader access가 정책상 구분되고,
  `transport_dbg`가 암묵적으로 보안 정책을 우회하지 않게 한다.
- `ARCH-413`: topology freeze 이후 runtime priority 변경과 다른 block target의
  재정렬을 금지하고 검출한다.
- `ARCH-414`: RSE/SI/AP control ownership 위반과 순서 위반을 fault-injection
  fixture로 검증한다.

#### 완료 조건

- reset 직후 RSE만 SMD/RSE/SI 관리 자원에 접근 가능하다.
- ATU window 밖과 APU deny 접근이 target side effect 없이 실패한다.
- RSE가 구성한 허용 window만 AP/SI에서 성공한다.
- system router의 reserved top-level region은 항상 오류를 반환한다.
- 설정값 read-back 또는 ownership 검증이 실패하면 AP reset release가 발생하지
  않고 원인이 evidence에 기록된다.
- debug/loader 예외는 명시된 capability에만 허용되고 일반 CPU/DMA path에서
  재사용되지 않는다.

### A5. Memory/DMA/IOMMU/QEMU backing과 build configuration 정합

#### 작업

- `ARCH-500`: AP shared SRAM 128 MiB aperture와 실제 allocated backing 정책을
  분리해 선언한다.
- `ARCH-501`: SMD/AP/RSE/SI가 공유하는 메모리 view를 단일 backing에 연결한다.
- `ARCH-502`: low/high DRAM bank를 deploy DTB, FVP config와 local build manifest에서
  resolve한다.
- `ARCH-503`: single-chip과 multichip high DRAM layout을 명시 구성으로 분리한다.
- `ARCH-504`: ATU/alias DMI range translation, clipping, invalidation test를
  추가한다.
- `ARCH-505`: active Yocto `PC_CPUS_COUNT_DEFAULT=4`와 full-system QBox source
  기본값을 4로 정렬한다. direct-boot 16-core 실험값과 구분하고 runner가 결정한
  값을 result JSON과 local guest `maxcpus=`에 기록한다. 기본/override bootargs
  정렬은 완료됐고 artifact 자동 대조는 계속 보강한다. direct-boot 16-core
  profile은 이번 fidelity acceptance에서 실행하지 않는다.
- `ARCH-506`: DT CPU node, GIC redistributor 수, PPU/reset signal 수의 일관성을
  정적 검사한다.
- `ARCH-507`: QEMU `MemoryRegion`/`AddressSpace`, QBox `gs_memory`와 file-backed
  memory 중 각 backing의 유일한 owner 및 alias/view 관계를 manifest에 기록한다.
- `ARCH-508`: GPEX bus master의 requester/StreamID를 SMMU translation과 fault
  reporting까지 전달하고, 허용·차단 IOVA 및 ATS 미지원 동작을 시험한다.
- `ARCH-509`: byte enable, streaming width, unaligned access, exclusive access와
  endian 변환이 router/addrtr/QEMU bridge에서 보존되는지 시험한다.
- `ARCH-510`: APU/ATU reprogram, reset 및 backing remap 때 관련 DMI grant를
  회수하고 deny 영역에 새 DMI가 발급되지 않게 한다.
- `ARCH-511`: `b_transport`와 DMI의 read/write 결과 및 side effect가 같고,
  `transport_dbg`만 명시된 debug semantics를 갖는지 비교한다.
- `ARCH-512`: CMN/CHI의 1차 functional coherency contract를 공유 DRAM visibility,
  ordering barrier와 DMA/CPU 관찰 순서로 정의한다.
- `ARCH-513`: SMMU translation/permission fault가 guest driver, GIC와 QVP trace에
  같은 requester/StreamID 및 syndrome으로 나타나는지 검증한다.
- `ARCH-514`: 4 CPU에서 선택한 SMMU backend의 mapped DMA 하나와 fault 하나를
  확인한다. DMI/backend 조합 matrix는 extended validation으로 미룬다.

#### 완료 조건

- CPU 수와 DRAM bank가 DT/manifest/QVP result에서 동일하다.
- 모든 shared memory view가 같은 backing content를 관찰한다.
- remap과 write 후 stale DMI가 남지 않는다.
- CPU·DMA·debug path가 memory owner를 중복 생성하지 않고 요청 속성과 오류를
  target에서 guest까지 보존한다.
- functional coherency 및 SMMU fault test가 두 AP CPU topology에서 재현된다.

### A6. IRQ, reset, clock, power, timing과 safety route 명시화

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
- `ARCH-607`: GPEX MSI→ITS→LPI, SMMU event/PRI fault와 legacy SPI route를
  source-to-vCPU까지 시험한다.
- `ARCH-608`: AP corrected/deferred RAS의 TF-A/Linux FFH와 software notification
  SPI 89 경로, SI uncorrected error의 ERI 경로를 서로 독립적으로 검증한다.
- `ARCH-609`: 각 FMU의 fault input, threshold, critical/non-critical output,
  SCP serialization queue, SSU FSM과 ESM status 변화를 순서대로 기록한다.
- `ARCH-610`: QEMU CPU의 start/hold/finish reset state와 QBox SystemC reset
  thread, qdev reset callback 및 DMI flush 순서를 고정한다.
- `ARCH-611`: BQL 보유 구간, reentrant access, async job 종료와 QEMU kick의
  순서를 race/deadlock test로 검증한다.
- `ARCH-612`: MTTCG quantum keeper, WFI wake deadline와 reset/power-off CPU의
  simulated-time 진행을 AP 및 SI QEMU instance별로 시험한다.
- `ARCH-613`: cold, warm, CPU, cluster, domain, watchdog 및 fault escalation
  reset마다 보존·초기화되는 memory/IRQ/device state를 표로 고정한다.
- `ARCH-614`: Linux cpuidle/cpufreq→TF-A PSCI→SCP SCMI→PPU/clock/power의
  request/ack/error 경로와 per-cluster performance domain을 검증한다.
- `ARCH-615`: reset·power·fault transition에 transaction ID, source/sink,
  simulated timestamp와 wall timestamp를 남기는 bounded trace를 추가한다.
- `ARCH-616`: 각 shared-memory backing의 lifecycle owner와 domain reset별
  preserve/clear 정책을 선언한다. SI0가 AP release 전에 초기화하는 non-secure
  MHU SRAM은 SMD-owned로 두고 AP reset에서 보존한다.

#### 완료 조건

- 모든 source가 하나의 의도된 sink 또는 명시적 fan-out을 가진다.
- reset 전후 pending IRQ, timer와 MHU state가 규정된 값으로 돌아간다.
- fault injection 결과가 QVP log와 route evidence에 남는다.
- QEMU/SystemC reset과 timing test에서 BQL deadlock, orphan async job 또는
  reset-held CPU의 시간 진행이 없다.
- FMU threshold부터 SSU/ESM, GIC 또는 reset까지 상태 전이와 event 순서가
  hardware contract에 맞는다.

### A7. 우선 기능 gap 승격과 system software ABI

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

#### system software 검증 작업

- `ARCH-700`: TF-M, SCP-firmware, TF-A, OP-TEE, U-Boot, Linux, Zephyr와 deploy
  DTB의 주소/IRQ/channel/shared-memory 상수를 software contract와 대조한다.
- `ARCH-701`: RSE secure boot의 image provenance, 인증, measurement와 AP/SI
  release 조건을 artifact hash 및 event log로 검증한다.
- `ARCH-702`: RSE↔SCP boot confirmation/AP primary power, TF-A↔SCP secondary
  CPU/system power/reset 및 SCP→RSE notification의 SCMI channel을 시험한다.
- `ARCH-703`: PFDI agent별 전용 MHU/shared-memory channel, per-CPU watchdog,
  SCMI vendor protocol `0x90`, FDTI 주기와 timeout/error recovery를 시험한다.
- `ARCH-704`: HIPC MHUv3 notification, resource table/vring/buffer ABI와 Linux
  remoteproc/RPMsg driver state를 guest log와 shared-memory dump로 검증한다.
- `ARCH-705`: TF-A/OP-TEE/Linux의 FF-A endpoint, shared-memory descriptor,
  interrupt와 denied/invalid request 응답을 검증한다.
- `ARCH-706`: RAS corrected/deferred/uncorrected error가 TF-A, Linux FFH와
  Safety Island firmware에서 예상 경로로 분기되는지 fault injection한다.
- `ARCH-707`: TF-A가 FIP에 포함한 DT를 U-Boot/Linux가 동일하게 사용하고,
  SystemReady DT v3.1/ACS 및 주요 driver probe 결과를 report에 남긴다.
- `ARCH-708`: protocol success뿐 아니라 timeout, malformed descriptor,
  duplicate notification, power/reset 중 request와 peer-offline을 시험한다.
- `ARCH-709`: SI ATU region 14 translation, SMD-owned mailbox 초기화와 AP reset
  보존을 함께 검증하고 Linux SCMI v2.0 probe를 FVP software-contract marker와
  비교한다.
- `ARCH-710`: AP/CL1 requester가 SI0 transport init보다 먼저 유효한 secure
  request를 게시해도 status/payload를 보존하고, trace-off startup ordering에서
  PFDI `PROTOCOL_VERSION` 응답을 보장한다.

#### 완료 조건

- 각 필수 block은 register read 성공이 아니라 firmware/OS-visible state
  transition, interrupt/reset 또는 protocol response를 증명한다.
- 모든 software ABI는 producer/consumer 양쪽 상수와 runtime evidence가
  일치하고, error path가 무한 대기 없이 종료된다.

### A8. Focused FVP comparison과 완료 판정

#### 작업

- `ARCH-800`: FVP와 QVP의 실제 artifact hash와 topology/config manifest를 함께
  보존한다.
- `ARCH-801`: UART milestone, MHU/SCMI/PFDI handoff, CPU 수, DT probe를 비교한다.
- `ARCH-802`: 변경한 기능의 대표 allow/deny 또는 IRQ/fault marker 하나를
  비교한다.
- `ARCH-803`: 차이를 `동등`, `의도된 추상화`, `부분 모델`, `blocker`로 분류한다.
- `ARCH-804`: coverage ledger와 roadmap을 최신 evidence에 맞춰 갱신한다.
- `ARCH-805`: broad pass-through, temporary merged bus와 undocumented priority가
  소스에서 사라졌음을 검사한다.
- `ARCH-806`: firmware, DTB, kernel과 rootfs hash 차이를 기록한다. 동일 hash는
  MVP comparison의 선행 조건으로 강제하지 않는다.
- `ARCH-807`: CMN/NCI/NI hierarchy를 cycle timing이 아닌 initiator/target,
  translation, security와 signal route 관점에서 비교한다.
- `ARCH-808`: 이번 구현에서 변경한 protocol의 대표 message/state marker만
  비교한다.
- `ARCH-809`: elapsed time은 hang 진단용으로만 기록하고 성능 판정에는 사용하지
  않는다.
- `ARCH-810`: architecture contract와 FVP CFG2-only CL1 extension 결과를 별도
  열로 보고해 FVP 전용 동작을 hardware parity로 오판하지 않는다.
- `ARCH-811`: injection interface가 양쪽에 있을 때 대표 QVP 오류 하나를 FVP의
  syndrome/side effect와 비교한다.
- `ARCH-812`: final bundle에 command, environment, source/submodule revision,
  artifact hash, resolved CCI, route manifest, logs와 verdict를 포함한다.

#### 완료 조건

- 아래 G0–G6 최소 gate가 통과한다. G7은 수행하거나 `deferred` 사유를 기록한다.
- 남은 fidelity gap은 주소, 영향, 근거, 대체 계획과 함께 문서화된다.
- source revision, command, result JSON, log와 판정이 한 evidence bundle에 있다.

## 8. 검증 Gate

| Gate | 범위 | 필수 증거 |
| --- | --- | --- |
| G0 | contract/static | map/topology/software ABI validator, source scope, artifact hash와 core boundary audit |
| G1 | QBox/TLM 기반 | 변경한 request path의 context 보존과 대표 allow/deny unit test |
| G2 | domain/boot policy | AP/SI/RSE isolation, RSE APU/ATU 설정, SI read-back, AP reset release trace |
| G3 | memory/DMA/IOMMU/QEMU | single backing, mapped GPEX DMA 하나와 SMMU fault 하나 |
| G4 | signal/lifecycle/safety | 구현한 IRQ/fault 수직 slice의 source→sink→clear smoke |
| G5 | system software/ABI | 변경한 protocol의 대표 오류와 다음 정상 request |
| G6 | QBox full-system smoke | local과 Yocto에서 RSE/SI/AP/4 CPU boot 및 coverage 각 1회 |
| G7 | focused FVP comparison | 변경한 marker를 한 번 비교하거나 `deferred` 사유 기록 |

### 8.1 단계별 명령

현재 존재하는 기본 검사는 다음과 같다.

```bash
python3 scripts/test/validate_qbox_apollo_fvp_full_map.py
python3 scripts/test/audit_qbox_core_boundary.py
git -C hsoc-stack/tools/qbox-platform diff --check
git -C hsoc-stack/tools/qbox diff --check
```

A1에서 추가한 topology 검사는 다음 interface를 제공한다.

```bash
python3 scripts/test/validate_qbox_apollo_topology.py \
  --emit build/qbox-apollo-qvp/topology/topology.json
```

구현 단계의 targeted build와 test는 다음 순서로 확대한다.

```bash
cmake --build build/local-apollo-qvp/work/qbox-platform \
  --target platforms-vp --parallel "$(nproc)"

./local_build.sh qbox

python3 scripts/run/run_qbox_apollo_fvp_full.py \
  --si-mode live-cl0-cl1 --timeout 600 \
  --out-dir "build/qbox-apollo-qvp/full-$(date +%Y%m%d-%H%M%S)"

python3 scripts/test/audit_qbox_apollo_fvp_full_coverage.py \
  --result-json <runtime-result.json> \
  --output build/qbox-apollo-qvp/full-coverage-audit.json
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

## 9. MVP smoke matrix

| 축 | 필수 조합 |
| --- | --- |
| AP CPU | CPU0–CPU3, 총 4 |
| policy | 변경한 경로의 allow 하나와 deny 하나 |
| SMMU | mapped DMA 하나와 unmapped IOVA fault 하나 |
| interrupt | endpoint MSI→CPU0 LPI 하나와 legacy INTx 하나 |
| fault | 구현한 source→sink→clear 한 번 |
| software ABI | 변경한 protocol 오류 하나와 다음 정상 request 하나 |
| runtime | local build/boot 한 번, Yocto build/boot 한 번 |

나머지 CPU topology, initiator/attribute 조합, DMI/backend matrix, reset stress,
protocol 전체 오류와 FVP 전체 differential은 extended validation backlog다.

## 10. 위험과 대응

| 위험 | 대응 |
| --- | --- |
| router 분리 직후 firmware의 암묵적 alias가 깨짐 | baseline trace로 실제 initiator/address를 수집하고 한 domain씩 전환 |
| APU 도입으로 초기 boot가 모두 차단됨 | RSE reset allow-list와 firmware programming 시점을 unit test로 먼저 고정 |
| shared memory를 합치면서 file-backed IPC가 회귀 | backing identity와 map file을 manifest에 남기고 CL0/CL1 동시 test 수행 |
| DMI가 bridge 정책을 우회함 | deny 영역은 DMI 금지, translated range clip/invalidate test 의무화 |
| addrtr/router 경계에서 TLM extension이 손실됨 | CPU와 GPEX에서 target까지 속성 보존을 G1 unit test와 bounded trace로 검증 |
| debug/loader 경로가 APU를 무조건 우회함 | trusted capability를 별도 선언하고 일반 `transport_dbg` negative test 수행 |
| QEMU와 SystemC가 같은 RAM을 각각 소유함 | backing owner를 하나로 제한하고 AddressSpace/view/alias identity를 manifest로 검사 |
| TLM 오류가 QEMU에서 성공이나 일반 오류로 축소됨 | `MemTxResult`·TLM response·guest syndrome 대응표와 negative vector 유지 |
| GPEX DMA가 requester/StreamID 없이 정책을 우회함 | initiator extension과 SMMU fault trace가 없는 DMA를 gate에서 실패 처리 |
| qdev reset/BQL/async 작업의 교착 또는 race | SystemC thread와 BQL 경계를 문서화하고 reset·reentrant·peer-offline stress 수행 |
| MTTCG/quantum 변경으로 WFI 또는 timer가 멈춤 | instance별 quantum과 wake deadline을 baseline 대비 검증 |
| FVP CFG2 CL1 동작이 silicon 필수 계약으로 유입됨 | 모든 block/route에 architecture/variant/extension scope를 부여 |
| firmware와 DT의 protocol/channel 상수가 drift함 | producer/consumer 상수를 software contract에서 정적으로 대조 |
| QVP evidence 경로 이름이 FVP 결과와 혼동됨 | A0에서 `qbox-apollo-qvp`로 이전하고 manifest에 실제 root와 schema version 기록 |
| FVP와 QVP의 추상화 수준 차이로 false mismatch 발생 | register 값, side effect, timing tolerance를 각각 분리 판정 |
| 기존 문서가 source보다 뒤처짐 | revision을 문서에 고정하고 generated topology를 source of truth로 사용 |
| QBox core에 Apollo 전용 코드가 유입됨 | `audit_qbox_core_boundary.py`와 owning-repository review를 gate로 유지 |

## 11. 변경 및 commit 경계

예상 변경은 다음 경계로 나눈다.

1. **최상위 저장소**: validator, runner, project 문서와 generated evidence 규약
2. **qbox-platform**: Apollo topology/map/policy, platform-specific SystemC 모델,
   Lua binding과 platform test
3. **qbox core**: 재사용 가능한 router/addrtr/APU 기능이 기존 API로 불가능한
   경우에만 최소 변경
4. **qemu**: 기존 libqemu/QBox 경계로 표현할 수 없는 generic device 또는
   `MemTxAttrs`/reset 결함이 재현되고 upstream path가 있을 때만 별도 atomic 변경

한 commit에 여러 저장소 변경을 섞지 않는다. 예시 commit 단위는 다음과 같다.

- `docs(apollo): define target machine architecture`
- `test(apollo): validate topology contract`
- `refactor(apollo): isolate AP address view`
- `refactor(apollo): isolate safety address views`
- `feat(apollo): enforce system APU policy`
- `test(apollo): compare FVP and QVP routes`

## 12. 단계별 중단 및 복구 기준

각 단계는 이전 단계의 evidence를 보존한다. 다음 상태에서는 다음 단계로
진행하지 않는다.

- 정적 topology가 중복 target 또는 undocumented overlap을 포함함
- negative access가 실제 target의 side effect를 발생시킴
- CPU/DMA requester, security/domain 또는 StreamID가 target 전에 손실됨
- debug/DMI/direct access가 선언되지 않은 policy bypass를 허용함
- 하나의 RAM backing을 QEMU와 SystemC가 중복 소유하거나 stale DMI가 남음
- CPU/DRAM topology가 DT와 다름
- QEMU reset/BQL/async/quantum test에서 deadlock, orphan job 또는 timer 정지가 발생함
- SCMI/PFDI/HIPC/FF-A error path가 timeout 없이 무한 대기함
- RSE, CL0, CL1 또는 AP 중 하나의 earliest boot milestone이 기준선보다 후퇴함
- runtime result가 source revision과 resolved config를 기록하지 않음

복구는 변경한 domain의 binding만 이전 topology로 되돌리는 atomic revert가
가능해야 한다. user/generated state나 다른 submodule을 reset하지 않는다.

## 13. 최종 완료 체크리스트

- [x] `system_router`가 system-wide address만 담당하며, 현 `host_router`의
      local-map 역할은 제거되어 있다.
- [x] AP, SMD, RSE, SI CL0, SI CL1 router가 분리되어 있다.
- [x] `ap_view_passthrough` broad mapping이 없다.
- [x] `temporary merged bus`와 도메인 충돌 해소용 priority 변경이 없다.
- [x] 모든 현재 cross-domain route가 ATU/static-window manifest에 존재한다.
- [x] ATU reset default-deny와 RSE programming 기반 boot test가 통과한다.
- [x] SI CL0의 ATU/SCR read-back, CMN/GIC/peripheral 설정과 AP reset release
      순서가 boot contract와 일치한다.
- [x] architecture/RD-Aspen/FVP CFG2 extension scope가 구분되어 있다.
- [x] 기본 4 CPU, GIC, PPU와 DT topology가 정상 boot에서 일치한다.
- [x] A4 범위의 memory backing/view와 ATU DMI test가 통과한다.
- [ ] QEMU/SystemC RAM owner가 하나이며 변경한 CPU/DMA/debug 대표 경로의 TLM
      속성과 `MemTxResult`/guest syndrome이 보존된다.
- [ ] GPEX requester/StreamID, mapped/unmapped SMMU와 MSI→CPU0 LPI smoke가 통과한다.
- [ ] 구현한 IRQ/reset/power/fault route의 source→sink→clear evidence가 생성된다.
- [x] TCG 기본 경로의 qdev reset, BQL, async job, MTTCG quantum와 WFI wake
      회귀 및 full boot가 통과한다.
- [ ] 변경한 software ABI의 대표 error와 다음 정상 request가 통과한다.
- [ ] AP secure watchdog, SMD RGM 등 P1 placeholder가 기능 모델로 승격된다.
- [ ] QBox G0–G6 최소 smoke가 통과한다.
- [ ] focused FVP G7을 수행하거나 `deferred` 사유와 남은 gap을 기록한다.
- [x] 신규 evidence가 `build/qbox-apollo-qvp/`에 있고 기존
      `build/qbox-apollo-fvp/` 결과와 provenance로 구분된다.
- [x] roadmap, Apollo platform README와 fidelity ledger가 최신 상태다.

## 14. 리뷰 근거

이번 리뷰는 source와 다음 로컬 문서/그림을 함께 대조했다.

| 근거 | 계획에 반영한 항목 |
| --- | --- |
| [`02-block-diagram-for-zena-css.md`](arm_zena_css_dev_guide/02-block-diagram-for-zena-css.md), [`figure-2-1`](arm_zena_css_dev_guide/assets/figure-2-1-zena-css-high-level-block-diagram.png) | AP/RSE/SI/Debug, CMN/NCI/NI 및 외부 memory/I/O 경계 |
| [`aspen_high_level_arch.png`](../arm-zena-css/documentation/images/aspen_high_level_arch.png), [`aspen_system_management_block.png`](../arm-zena-css/documentation/images/aspen_system_management_block.png), [`aspen_compute_complex.png`](../arm-zena-css/documentation/images/aspen_compute_complex.png) | SMD NCI, SI 내부 NCI, GIC/ATU, I/O TCU/TBU/ITS와 계층형 router |
| [`06-boot-flow-of-zena-css.md`](arm_zena_css_dev_guide/06-boot-flow-of-zena-css.md), [`rse_oriented_boot_flow.png`](../arm-zena-css/documentation/images/rse_oriented_boot_flow.png), [`safety_boot.rst`](../arm-zena-css/documentation/design/safety_boot.rst), [`boot_process.rst`](../arm-zena-css/documentation/design/boot_process.rst) | RSE image 인증/ATU·APU 설정, SI 검증/CMN·GIC 설정과 AP release 순서 |
| [`components.rst`](../arm-zena-css/documentation/design/components.rst), [`scmi_comm_rse_tfa_scp.png`](../arm-zena-css/documentation/images/scmi_comm_rse_tfa_scp.png), [`power_and_performance_control.rst`](../arm-zena-css/documentation/design/power_and_performance_control.rst) | RSE/SCP/TF-A의 SCMI/PSCI 및 power/reset 소유권 |
| [`si_gic_multiple_view.png`](../arm-zena-css/documentation/images/si_gic_multiple_view.png), [`pc_domain_reset.png`](../arm-zena-css/documentation/images/pc_domain_reset.png) | GIC view, reset state와 source-to-sink signal contract |
| [`fmu.rst`](../arm-zena-css/documentation/design/fmu.rst), [`ssu.rst`](../arm-zena-css/documentation/design/ssu.rst), [`ras.rst`](../arm-zena-css/documentation/design/ras.rst), [`fmu_ssu_integration.png`](../arm-zena-css/documentation/images/fmu_ssu_integration.png) | FMU threshold/queue, SSU FSM/ESM, AP FFH SPI 89와 SI ERI |
| [`platform_fault_detection_interface.rst`](../arm-zena-css/documentation/design/platform_fault_detection_interface.rst), [`platform_fault_detection_interface.png`](../arm-zena-css/documentation/images/platform_fault_detection_interface.png) | PFDI 전용 MHU/shared memory, watchdog, SCMI 0x90와 FDTI |
| [`hipc.rst`](../arm-zena-css/documentation/design/hipc.rst), [`systemready_devicetree.rst`](../arm-zena-css/documentation/design/systemready_devicetree.rst) | HIPC 512 KiB ABI, detached remoteproc, DT/driver/SystemReady 검증 |
| [`08-fixed-virtual-platform.md`](arm_zena_css_dev_guide/08-fixed-virtual-platform.md) | CFG2 SI CL1의 FVP-only extension scope |

source 검토에는 QBox `router`/`addrtr`, QEMU initiator bridge와
`QemuMemTxAttrsTlmExtension`, Apollo AP GPEX/GIC/SMMU, CPU reset/quantum 및
current runner/README의 evidence path도 포함했다.

## 15. 2026-07-16 구현 및 검증 상태

### 15.1 단계별 판정

| 단계 | 상태 | 이번 구현 | 다음 완료 조건 |
| --- | --- | --- | --- |
| A0 | 완료 | active QVP 기본값 4 CPU, `qbox-apollo-qvp` evidence root, runtime/artifact 경로와 현재 map 고정 | direct-boot legacy evidence path는 별도 정리 |
| A1 | 초기 기반 완료 | 여섯 Lua contract, JSON exporter, topology validator, scope/backing/address/route 정적 검사 | request-context의 실제 TLM extension, debug/DMI policy와 bounded trace는 G1에서 보강 |
| A2 | 전환 완료 | `system_router`와 52-bit `ap_router`, AP CPU/GPEX/loader/target rebinding, HIPC alias, runtime priority mutation 제거 | 완료 상태 유지 |
| A3 | 전환 완료 | 40-bit SI CL0/CL1 router, AP HIPC bridge, CL0→CL1 SCMI bridge, local target/CPU/loader rebinding | 완료 상태 유지 |
| A4 | 구조 완료 | runtime SMD router, broad bridge 제거, SI/AP/SMDEXP ATU 실경로, canonical backing, GPEX TBU route | 완전한 APU permission은 A5/A7 fidelity로 분리 |
| A5 | 부분 | full-system CPU 기본과 local `maxcpus=4`, `addrtr` DMI 회귀, GPEX LTI00와 reset-state ATU deny | requester/StreamID, SMMU fault와 전 access-kind DMI 정책 |
| A6 | 부분 | signal/reset/fault contract, MHU/GIC/PPU route, reset-held CPU QK lifecycle 50회, SMD-owned mailbox AP-reset 보존 | 구현한 FMU/SSU/RAS source-to-sink 대표 smoke; 전체 taxonomy와 KVM/16 CPU는 후속 |
| A7 | 부분 | 정상 boot ABI, mailbox reset/startup ordering, secure pending request 보존, QVP/FVP secondary SCMI v2.0 focused differential | malformed/deny/timeout/error side effect와 placeholder 승격 |
| A8 | 부분 | local 5회·Yocto 3회 기준 boot/coverage, acceptance 2회와 최종 trace-off local/Yocto 각 3회 | 신규 fidelity 변경의 local/Yocto smoke 각 1회와 focused FVP G7 또는 `deferred` 사유 |

현재 contract의 migration phase는 `A4_policy_routing`이다.
`forbid_broad_passthrough=true`이며 compatibility debt는 빈 목록이다. 후속 fidelity
구현은
[`apollo-qvp-remaining-architecture-debt-design-ko.md`](apollo-qvp-remaining-architecture-debt-design-ko.md)의
리뷰 승인 구조와
[`apollo-qvp-architecture-debt-implementation-plan-ko.md`](apollo-qvp-architecture-debt-implementation-plan-ko.md)의
P1–P10 결과를 기준선으로 삼는다. broad bridge를 다시 추가하는 변경은 validator가
실패해야 한다.

### 15.2 정적·단위·빌드 검증

```text
python3 scripts/test/validate_qbox_apollo_fvp_full_map.py
  -> passed: true

python3 scripts/test/validate_qbox_apollo_topology.py
  -> status: pass; topology/address/transaction/IRQ/reset/boot/software/
     artifacts/validation JSON generated

python3 scripts/test/audit_qbox_core_boundary.py
  -> QBox core boundary audit passed

ctest --test-dir build/qbox-core-tests \
  -R '^aarch64-start-in-reset-release-test$' --repeat until-fail:50
  -> 50/50 passed

pytest -q tests/test_probe_qemu_cortex_r82.py \
  tests/test_run_qbox_apollo_fvp_full.py \
  tests/test_run_qbox_fvp_rd_aspen_rse.py \
  tests/test_validate_qbox_apollo_topology.py
  -> probe test 포함 최종 변경 test 64개 통과

./local_build.sh qbox --qbox-unit-tests
  -> QBox/QBox-platform build passed; SystemC component tests 33/33 passed

make -f Makefile.cmake mod_test BUILD_PATH=<repo>/build/tests/scp-firmware-unit
  -> SCP module tests 77/77 passed; transport 24 tests passed
```

### 15.3 local source image 검증

```text
python3 scripts/run/run_qbox_apollo_fvp_full.py ... (5회)
  -> result.json 5/5 passed
  -> full-coverage-audit.json 5/5 passed, 각 49 checks
```

RSE BL1/BL2/runtime, live SI CL0 SCP-firmware, 4-core SI CL1 Zephyr/PFDI/network,
4-core AP TF-A/OP-TEE/U-Boot와 Linux login/root shell marker가 모두 관찰됐다.

구현 후 리뷰 acceptance도 두 번 수행했다.

```text
architecture-debt-qk-fix-local-maxcpus-r1-20260716
  -> Linux 4 CPUs online, CPU4–CPU15 PSCI release 시도 없음, coverage 49/49

architecture-debt-review-scmi-reset-owner-r1-20260716
  -> SMD-owned mailbox AP reset 보존, SCMI v2.0 marker, coverage 49/49

architecture-debt-final-pfdi-preserve-local-r1..r3-20260716
  -> trace-off 3/3, PFDI ready (4 CPUs), 각 coverage 49/49
```

두 번째 결과의 SCMI protocol/vendor/firmware marker는 기존 FVP Linux log와
일치한다. 이는 focused software-contract 비교이며 전체 G7 완료는 아니다.

### 15.4 Yocto `nexios-image` 검증

```text
./yocto_build.sh
  -> 7,290 tasks attempted, 7,259 did not rerun, all succeeded

python3 scripts/run/run_qbox_apollo_fvp_full.py \
  --qbox-build-dir <Yocto native provider> \
  --rootfs <Yocto nexios-image WIC> ... (3회)
  -> result.json 3/3 passed
  -> full-coverage-audit.json 3/3 passed, 각 49 checks

architecture-debt-final-pfdi-preserve-yocto-r1..r3-20260716
  -> 새 SCP/WIC trace-off 3/3, PFDI/4 CPU/SCMI/login, 각 coverage 49/49
```

Yocto WIC는
`build/tmp_baremetal/deploy/images/apollo-qvp/nexios-image-apollo-qvp.wic`에서
사용했고 RSE/SI/AP/Linux login까지 통과했다. headless runner는 guest UART에
명령을 주입하지 않으므로 login prompt 또는 root shell 중 하나를 Linux 완료
조건으로 사용한다.

상세 증거와 명시적 gap은
[2026-07-16 아키텍처 부채 구현·검증 보고서](apollo-qvp-architecture-debt-validation-2026-07-16.md)에
기록한다. 이번 결과를 완전한 APU permission, 전체 IRQ/fault side effect 또는
FVP functional parity 완료로 해석하지 않는다.

## 16. 4 CPU Fidelity 후속 계획

A0–A4 구조 전환과 P1–P10 구현 결과를 기준선으로 유지하면서 남은 부채는 다음
연계 문서에 따라 진행한다.

- [Fidelity 부채 아키텍처 설계](apollo-qvp-fidelity-debt-architecture-design-ko.md)
- [Fidelity 부채 구현 계획](apollo-qvp-fidelity-debt-implementation-plan-ko.md)
- [Fidelity 부채 검증 계획](apollo-qvp-fidelity-debt-validation-plan-ko.md)

구현 순서는 I0 4 CPU contract, I1 request context, I2 NI-710AE APU, I3
MMU-720AE/SMMUv3, I4 MSI/ITS/LPI, I5 fault plane, I6 software ABI recovery, I7
local/Yocto smoke와 focused FVP comparison, I8 closeout이다. 검증은 V0–V9 최소
gate로 추적한다.

모든 gate의 CPU scope는 CPU0–CPU3이다. CPU4–CPU15가 online되거나 16 CPU 결과가
4 CPU evidence와 혼합되면 실패한다. 반복 stress, soak, 16 CPU
enablement/lifecycle과 전체 FVP differential은 MVP 완료 조건이 아니다. emulator
성능 budget은 별도 acceptance로 추가하지 않는다.
