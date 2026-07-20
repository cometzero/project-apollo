# Apollo QVP FVP 대비 잔여 Fidelity 부채 정리

- 작성일: 2026-07-18
- 대상: `apollo-qvp`, RD-Aspen cfg2, Primary Compute 4 CPU
- 비교 기준: Arm Zena CSS 문서와 FVP 관찰점 대 현재 QBox/QEMU/SystemC 구현
- 목적: 이미 닫힌 항목을 제외하고 다음 구현·검증에서 처리할 잔여 부채만 정리
- 성능 기준: 에뮬레이터 성능 수치와 절대 부팅 시간은 acceptance에서 제외
- source 경계: components는 기대 동작 확인에만 사용하고 구현 owner는
  QBox/QEMU/qbox-platform과 top-level validation으로 한정

## 1. 결론

현재 QBox Apollo QVP에는 RSE, live SI0/SI1, TF-A, OP-TEE, U-Boot와 Linux를
4 CPU로 부팅하는 경로가 있다. 최신 Yocto QBox 실행은 RSE image load, AP power-on,
PFDI, SI1 RPMsg attach, measured boot, Linux login까지 도달한다
(`build/qbox-apollo-qvp/yocto-apollo-qvp-20260718-160644/result.json:532-538`,
`build/qbox-apollo-qvp/yocto-apollo-qvp-20260718-160644/result.json:650-726`).
현재 로그에서 RSE, SI0, SI1, TF-A/OP-TEE 또는 Primary Compute의 새로운
happy-path 부팅 회귀는 확인되지 않았다.

그러나 이 결과를 FVP 완전 동등성으로 해석할 수는 없다. 남은 핵심 부채는 다음과
같다.

1. AP watchdog 주소 의미·2단계 출력과 topology contract 3건처럼 현재
   source에서 바로 재현되는 정확성 부채가 있다.
2. RGM, DCLS, watchdog, 전체 FMU/SSU fault-to-reset 경로와 일부 RSE/SI/SMD
   주변장치는 기능 모델이 없거나 memory placeholder다.
3. CMN/DSU/NI-710AE/GIC multiview는 programmer-view와 discovery 중심의
   부분 모델이며 coherent fabric과 safety 의미를 재현하지 않는다.
4. 정상 SCMI/PFDI/HIPC/RPMsg는 동작하지만 peer-offline, reset, timeout,
   malformed/denied와 PSCI/FF-A 오류 matrix는 부분적이다.
5. Secure FWU는 ABI 1.0, Linux가 요청한 full-system reset, RSE/SI/AP의 두 번째
   Regular State 부팅까지 증명됐다. 그러나 capsule 자동 적용, bank-1, rollback과
   cross-reboot metadata persistence는 열려 있다.
6. 최신 FVP/QBox 실행은 storage state와 실행 gate가 같지 않으며, 현재 QBox
   결과도 G1/G2/G3/G5 및 post-login probe를 실행하지 않았다.

따라서 현재 상태는 **4 CPU nominal full-system boot complete, FVP hardware 및
error-path fidelity partial**로 판정한다.

## 2. 분석 기준

### 2.1 Source revision

| 영역 | revision |
| --- | --- |
| top-level | `8374e72f57be33f69535a0a882251fbfc0b3f6af` |
| `arm-zena-css` | `bf34d9e71f674e11beea3b8e84ea54486f555d2a` |
| QBox | `85573d0cab08daab2a57d088e596b5f55012a233` |
| qbox-platform | `f87e2da7298451c3e676e5e1b4cd4d13300a0979` |
| QEMU | `795bb94366f90e0cf68174c3c6c960ff116efc48` |

활성 Yocto 설정은 cfg2, `apollo-qvp`, 4 CPU이며 PFDI와 capsule build가
활성화되어 있다(`build/conf/local.conf:5-18`,
`build/conf/local.conf:29-30`). 이 문서에서는 CPU4~CPU15를 구현 우선순위에
넣지 않는다.

### 2.2 판정 용어

| 분류 | 의미 |
| --- | --- |
| confirmed gap | 현재 source 또는 재현 시험으로 기능 부재·불일치를 확인 |
| partial model | 정상 경로나 register subset은 동작하지만 FVP 의미가 불완전 |
| validation gap | 구현 부재로 단정할 수 없지만 동등성 증거가 없음 |
| stale/closed | 이전 문서에는 열려 있으나 더 최신 source·실행에서 닫힘 |
| out of scope | 4 CPU 현재 목표에서 의도적으로 제외 |

주소가 존재하거나 `gs_memory`가 decode를 제공하는 것만으로 하드웨어 모델이
구현됐다고 판정하지 않는다. 실제 register side effect, IRQ, reset, access
control과 software-visible 오류를 기준으로 한다.

### 2.3 최신 실행 증거의 한계

최신 Yocto QBox 결과는 `passed=true`지만 G0/G4만 pass이고 G1/G2/G3/G5는
`not_run`이다. Linux login은 확인했으나 root shell은 false이고
`post_login_probe`는 비어 있다
(`build/qbox-apollo-qvp/yocto-apollo-qvp-20260718-160644/result.json:532-548`,
`build/qbox-apollo-qvp/yocto-apollo-qvp-20260718-160644/result.json:655-662`,
`build/qbox-apollo-qvp/yocto-apollo-qvp-20260718-160644/result.json:713-726`).
이 실행 디렉터리에는 coverage audit도 없다.

가장 최근 FVP capture
`build/fvp-tmux/apollo-qvp-20260717-223809/`에는 `result.json`, summary,
exit-status와 coverage가 없다. 실행 명령은 mutable deploy fvpconf를 가리킨다
(`build/fvp-tmux/apollo-qvp-20260717-223809/runfvp.cmd:1`). FVP는 fresh
ITS/PS로 시작했지만 최신 QBox는 preserved RSE flash state를 재사용했다
(`build/qbox-apollo-qvp/yocto-apollo-qvp-20260718-160644/summary.txt:10-18`).
두 실행은 firmware generation은 비교할 수 있지만 state/hash까지 같은 실행은
아니다(`build/fvp-tmux/apollo-qvp-20260717-223809/uarts/rse.log:97-98`).

## 3. 우선순위 요약

P0는 현재 4 CPU nominal boot가 막힌다는 뜻이 아니라, 다음 구현 전에 먼저
정합을 맞춰야 하는 확인된 정확성 또는 acceptance 부채다.

| 우선순위 | 항목 | 분류 | 주 owner |
| --- | --- | --- | --- |
| P0 | topology validator의 AP-RSE backing/reset 계약 3건 | confirmed gap | top-level/qbox-platform |
| P0 | AP non-secure watchdog frame·WS1 출력과 secure watchdog | confirmed gap + probe 필요 | qbox-platform/QEMU |
| P0 | 동일 state·artifact FVP/QBox differential와 current coverage | validation gap | top-level runners/tests |
| P0 | Linux post-login PFDI/remoteproc/RPMsg/service gate | validation gap | top-level runners/tests |
| P1 | RGM/PIK/PPU/reset/power ownership | partial/missing | qbox-platform |
| P1 | watchdog/DCLS/APU→FMU→SSU→reset safety vertical | partial/missing | QBox/qbox-platform |
| P1 | RSE DCLS, MHU1/3~8, GPIO/timer/watchdog와 placeholder register | partial/missing | QBox/qbox-platform |
| P1 | SI0/SI1 local safety·DMA·watchdog·interconnect 주변장치 | partial/missing | QBox/qbox-platform |
| P1 | DSU/CMN/NI-710AE/GIC multiview와 access-control 의미 | partial model | QBox/qbox-platform/QEMU |
| P1 | SMMU/PCIe/ITS full-chain 오류·invalidation matrix | validation gap | QBox/qbox-platform |
| P1 | SCMI/PFDI/HIPC/RPMsg/PSCI/FF-A reset·negative matrix | partial/validation gap | QBox/qbox-platform |
| P1 | Secure services와 capsule A/B FWU | validation/functional gap | QBox/qbox-platform/runners |
| P2 | AP 9.1.1 deferred map, SMD/RoS peripheral subset | explicit deferred/missing | qbox-platform |
| P2 | timer secure-frame와 crash durability | validation gap | QEMU/QBox/runners |
| P3 | CHI/NoC timing, contention, analog/PHY | out of current scope | future |

### 3.1 도메인별 영향과 종료 기준

아래 표는 이후 절의 source·실행 근거를 실제 작업 항목으로 연결한 acceptance
요약이다. `FVP 기대`는 모든 cycle을 재현한다는 뜻이 아니라 현재 firmware와
driver가 관찰할 수 있는 동작을 뜻한다.

| 도메인 | FVP 기대 | 현재 QBox 상태 | 미해결 영향 | 종료 기준 |
| --- | --- | --- | --- | --- |
| AP topology | AP-RSE carveout과 cold-reset 대상이 하나의 machine contract를 따름 | validator 3건 실패 | reset 재실행과 shared backing alias가 암묵적 구현에 의존 | 19개 topology test, full-map, local/Yocto boot 통과 |
| Watchdog/reset | control/refresh, WS0/SPI50, WS1/SPI51과 RGM escalation | AP NS frame 의미 불일치 가능, 단일 IRQ와 global WS1 action만 존재하며 secure/SI0/RSE watchdog과 RGM은 부분·부재 | SPI51과 timeout-to-safety-reset 경로를 FVP와 비교할 수 없음 | FVP probe 뒤 WS0와 WS1 각각의 IRQ/reset-to-recovery differential 통과 |
| RSE | DCLS M55, MHU/timer/watchdog/GPIO와 보호 register side effect | 단일 실행 CPU와 핵심 boot path는 기능, 나머지 일부 placeholder | RSE fault, reset과 부가 채널 오류 경로 미검증 | 대표 DCLS/watchdog/MHU reset 시나리오와 register contract 통과 |
| SI0 | DCLS, DMA, watchdog, BIST와 interconnect fault가 FMU/SSU에 연결 | 정상 SCP 실행 및 대표 control plane은 기능, 주변·safety 경로 부분 | safety monitor와 reset recovery의 system-level 증거 부재 | 선택한 fault source가 FMU/SSU 기록, IRQ, reset, recovery까지 도달 |
| SI1 | 4 CPU 실행 외 local safety/diagnostic IP와 AP service lifecycle | 정상 PFDI/HIPC/RPMsg는 기능, peer/reset/error 경로 부분 | 정상 boot 성공만으로 service resilience를 보장하지 못함 | peer-offline/reset/malformed 뒤 재연결과 정상 요청 복구 통과 |
| AP CPU/DSU/CMN/GIC | A720AE feature view, DSU/CMN coherency 및 GIC-720AE multiview 의미 | 4 CPU 실행·IRQ delivery와 discovery view는 기능, safety/coherency는 부분 | ID/discovery는 맞아도 fabric·RAS·isolation 오류를 재현하지 못함 | 사용 중 feature/register와 대표 RAS/isolation 경로를 FVP와 비교 |
| NI/SMMU/PCIe/ITS | requester ID, translation, permission, invalidation과 MSI/LPI 전달 | 단위 기능과 focused slice는 존재, RSE-first full chain 검증 부족 | DMA 격리와 fault propagation에 회귀 검출 공백 | 정상 DMA와 invalid ID/STE/CD/TLBI/queue 오류 matrix 통과 |
| SMD | RGM/PIK, debug, UART/GPIO/System ID, ATU/APU와 counter semantics | 1 MiB SRAM 및 일부 control/counter 기능, 여러 block 부재·부분 | system reset·debug·access-control 계약이 placeholder에 의존 | 실제 consumer가 있는 block부터 side effect/IRQ/reset 검증 통과 |
| Software contract | SCMI/PFDI/HIPC/RPMsg/PSCI/FF-A가 reset·timeout·denied 뒤 복구 | nominal path와 일부 malformed path만 검증 | service hang 또는 stale completion 회귀를 놓칠 수 있음 | bounded negative matrix와 post-error 정상 요청 통과 |
| Secure service/FWU | PSA storage와 capsule A/B trial, commit, rollback persistence | Regular State와 preserved storage는 확인, update lifecycle 미검증 | update 및 secure storage parity를 주장할 수 없음 | fresh state PSA/TS와 capsule apply→trial→commit/rollback 통과 |
| Map/timer/RoS | programmer map, secure/safety timer IRQ와 사용 peripheral 동작 | required-now map은 통과, 20개 row와 일부 peripheral은 deferred | 새로운 firmware consumer가 inert aperture를 밟을 위험 | consumer 기반 승격, secure timer/IRQ 및 필요한 row의 기능 검증 |
| Differential | 같은 artifact와 writable state에서 동일 marker·오류 비교 | 최신 두 실행의 state와 gate가 다르고 FVP result schema가 없음 | `passed=true`가 FVP parity를 보장하지 않음 | artifact/state hash, per-domain result, coverage와 failed-service 자동 비교 |

## 4. P0: 먼저 정리할 정확성 및 Acceptance 부채

### 4.1 Apollo topology contract 3건

현재 checkout에서 다음 명령은 `3 failed, 16 passed`로 재현된다.

```bash
/home/cometzero/.local/bin/python3.12 -m pytest -q \
  tests/test_validate_qbox_apollo_topology.py
```

두 실패는 `system_ap_mhu_pointer_data`와 `system_ap_rse_mailbox`의
AP-RSE carveout backing size이고, 나머지 하나는 AP cold reset 대상에서
`host_ap_bl2_header_sram.reset`이 빠진 계약이다
(`tests/test_validate_qbox_apollo_topology.py:100-105`,
`tests/test_validate_qbox_apollo_topology.py:490-493`). 이 부채는 cold-init
완료 보고서에도 선행 architecture debt로 남아 있다
(`doc/apollo-qvp-cold-initialization-profile-report-2026-07-18-ko.md:245-255`).

완료 조건:

1. 두 carveout의 physical range, shared backing size와 AP/RSE view를 하나의
   machine contract에서 계산한다.
2. BL2 header SRAM이 AP cold reset에서 보존되어야 하는지 초기화되어야 하는지
   FVP reset 관찰점과 TF-A owner 기준으로 결정한다.
3. topology test 전체가 pass하고 full-map validator 및 local/Yocto boot가
   계속 pass해야 한다.

### 4.2 AP watchdog frame

Zena programmer model은 `0x1a42_0000`을 non-secure watchdog CONTROL,
`0x1a43_0000`을 REFRESH로 정의한다
(`doc/arm_zena_css_dev_guide/09-programmers-model-for-zena-css.md:100-106`).
현재 QBox는 같은 주소에 각각 QEMU `sbsa_gwdt.refresh_mem`과
`control_mem`을 반대로 연결한다
(`hsoc-stack/tools/qbox-platform/platforms/apollo/hw-block/ap_compute.lua:376-392`).

이 차이는 이름만의 문제인지 실제 MMIO frame이 반대인지 FVP read/write probe로
확정해야 한다. 확인 전에는 source를 임의로 뒤집지 않는다.

frame 주소와 별도로 two-stage 출력도 partial이다. Zena interrupt map은
non-secure watchdog WS0 `WDOGINT`를 SPI50, WS1 `WDOGRES`를 SPI51로 정의한다
(`doc/arm_zena_css_dev_guide/09-programmers-model-for-zena-css.md:1417-1418`).
현재 QBox wrapper는 QEMU SysBus IRQ 하나만 노출하고
(`hsoc-stack/tools/qbox-platform/qemu-components/sbsa_gwdt/include/sbsa_gwdt.h:19-55`),
Apollo는 이를 SPI50 하나에만 연결한다
(`hsoc-stack/tools/qbox-platform/platforms/apollo/hw-block/signal_routes.lua:3-10`).
QEMU device는 WS0에서 이 IRQ를 올리지만 WS1에서는 별도 SPI51 출력 없이 global
`watchdog_perform_action()`을 호출한다
(`hsoc-stack/tools/qemu/hw/watchdog/sbsa_gwdt.c:193-219`). 따라서 현재 구현은
FVP의 WS1 interrupt와 RGM/reset escalation 의미를 대체했다고 볼 수 없다.

secure watchdog `0x1a46_0000/0x1a47_0000`은 현재 `gs_memory`이고 source도
fuller model이 pending임을 명시한다
(`hsoc-stack/tools/qbox-platform/platforms/apollo/hw-block/ap_compute.lua:463-487`).

완료 조건:

1. FVP와 QEMU SBSA watchdog frame을 동일한 control/refresh access sequence와
   WS0/WS1 두 expiry 단계로 probe한다.
2. non-secure frame 주소가 다르면 Lua와 AP-map audit를 함께 수정한다.
3. WS0/SPI50과 WS1/SPI51을 각각 노출하거나, FVP probe로 확인된 동등한
   WS1→RGM/reset route를 구현한다.
4. secure watchdog에 expiry, IRQ SPI, refresh와 reset side effect를 구현한다.
5. 정상 refresh, 두 단계 expiry와 reset/recovery를 FVP/QBox에서 비교한다.

### 4.3 동일 조건 differential과 current coverage

2026-07-17 whole-system 비교로 주요 부팅 차이는 닫혔지만, 최신 2026-07-18
실행은 exact same-state differential이 아니다. 또한 최신 QBox 결과는 일부
gate가 `not_run`이어도 pass가 될 수 있다. older coverage audit도 boot-critical
항목을 `planned`로, 일부 `not_run` gate를 pass로 수용하므로 최신 parity
증거를 대신할 수 없다
(`scripts/test/audit_qbox_apollo_fvp_full_coverage.py:81-100`,
`scripts/test/audit_qbox_apollo_fvp_full_coverage.py:165-184`).

완료 조건:

1. FVP/QBox에 동일 deploy artifact hash, writable flash/OTP/PS/ITS 초기 hash,
   CPU count와 backend를 기록한다.
2. 양쪽 runner가 per-domain result, exit status와 canonical marker timestamp를
   동일 schema로 출력한다.
3. RSE, SI0, SI1, secure console, primary console뿐 아니라 memory map, IRQ,
   driver probe와 failed-service 목록을 자동 비교한다.
4. 비교에 사용한 최신 QBox run에서 coverage audit를 생성하고 `not_run`을
   parity pass로 승격하지 않는다.

### 4.4 Linux post-login contract

SI1 firmware 로그의 RPMsg attach만으로 AP Linux remoteproc/RPMsg/PFDI service가
완성됐다고 볼 수 없다. 최신 Yocto QBox 로그에는 `pfdi_misc` load가 보이지만
structured root-shell/post-login probe가 없다. 따라서 다음 항목은 현재-run
qualification gap이다.

- PFDI version/capability 및 CPU0~CPU3 device/ioctl
- SI remoteproc attach와 resource table
- RPMsg channel 및 `ethsi1`
- SCMI/PFDI 정상 요청 뒤 서비스가 계속 응답하는지
- SMMU/GIC/ITS/PCIe driver 상태

완료 조건은 root shell을 획득하고 위 항목을 구조화된 JSON으로 남기며, 하나라도
누락되면 full-system pass를 실패시키는 것이다.

## 5. P1: 하드웨어 모델 부채

### 5.1 Reset Generation Manager와 power/reset ownership

FVP architecture에서 RGM은 RSE, SI와 AP reset sequence의 공유 owner다
(`doc/arm_zena_css_dev_guide/06-boot-flow-of-zena-css.md:9-25`,
`doc/arm_zena_css_dev_guide/09-programmers-model-for-zena-css.md:287-303`).
현재 QBox는 reset GPIO/fanout, PPU와 MHU service hook을 조합해 결과를 재현하며
독립 RGM register, syndrome, mask와 sequencer가 없다. SYSTOP PIK도
`gs_memory`다
(`hsoc-stack/tools/qbox-platform/platforms/apollo/hw-block/system_mgmt.lua:390-399`).

`host_ppu`는 timed state transition subset을 제공하지만 RGM→PIK→PPU→CPU
reset/clock 관계 전체를 나타내지 않는다. SI image loader도 인증 완료 결과를
capability로 전달할 뿐 FVP의 hardware-mediated secure load sequence 전체를
모델링하지 않는다.

완료 조건은 RGM/PIK/PPU owner와 signal route를 machine contract로 선언하고,
reset reason, mask, release ordering, failed authentication 시 release 차단을
검증하는 것이다.

### 5.2 Safety vertical: watchdog, DCLS, FMU/SSU와 reset

현재 SMMU event→FMU→SSU 대표 경로와 software injection은 존재하지만 다음
수직 경로는 남아 있다.

- AP DSU/A720AE cache RAS와 DCLS fault
- SI0/RSE DCLS compare 및 mismatch injection
- AP secure, SI0, RSE secure/non-secure watchdog expiry
- NI-710AE APU violation
- FMU severity/mask/record/clear
- SSU ESM 및 RGM reset escalation

SI0 watchdog은 활성 Lua에 dedicated model이 없고, RSE timer/watchdog도 없다
(`doc/apollo-fvp-qvp-hardware-comparison-ko.md:127-139`,
`doc/apollo-fvp-qvp-hardware-comparison-ko.md:195-212`). AP FMU도 각 1 MiB
aperture의 active bank 영역만 모델링한다
(`hsoc-stack/tools/qbox-platform/platforms/apollo/hw-block/ap_compute.lua:522-545`).

완료 조건은 최소 한 source씩 `source → FMU record/IRQ → SSU state/ESM →
RGM/PPU reset → firmware recovery`를 실제 signal route로 검증하는 것이다.

### 5.3 RSE

현재 RSE는 한 Cortex-M55 실행 경로, DMA-350, KMU/LCM/SAM, ATU, crypto,
system counter, MHU0/2와 QEMU-local CFI boot flash의 기능 subset을 제공한다.
다음은 남아 있다.

- redundant M55 DCLS pair/compare/fault
- GPIO0/1, timestamp timer, timer0~3와 secure/non-secure watchdog
- MHU1 및 MHU3~8의 독립 frame/IRQ
- OTP wrapper의 register/lock/error semantics
- CPU security/power/identity register
- TRAM과 integration-layer side effect

현재 OTP wrapper, CPU security/power/identity, TRAM과 integration layer는
`gs_memory`다
(`hsoc-stack/tools/qbox-platform/platforms/apollo/hw-block/rse.lua:173-227`,
`hsoc-stack/tools/qbox-platform/platforms/apollo/hw-block/rse.lua:434-443`,
`hsoc-stack/tools/qbox-platform/platforms/apollo/hw-block/rse.lua:538-547`).
MHU도 현재 RSE-local MHU0/2만 조립한다
(`hsoc-stack/tools/qbox-platform/platforms/apollo/hw-block/rse.lua:445-519`).

QEMU-local CFI는 cold-init 병목을 닫았지만 비정상 host 종료 시 25 ms deferred
writeback window의 crash durability는 미검증이다
(`doc/apollo-qvp-cold-initialization-profile-report-2026-07-18-ko.md:245-250`).

### 5.4 Safety Island CL0

현재 R82 execution, GIC/UART/MHU, generic timer, PPU, SSU/FMU, CMN discovery와
NI-710AE policy subset은 동작한다. FVP map과 비교하면 다음이 빠지거나 inert하다.

- CL0 DCLS pair와 compare
- local watchdog
- GPIO와 local DMA-350
- BIST/MBIST/SBISTC
- 전체 5 FMU source와 SSU/ESM/reset matrix
- 실제 primary/secondary/MHU interconnect GPV routing
- 여러 SMD expansion, cluster utility, NI control과 AP cluster AE/control

일부 control aperture는 `gs_memory`로 남아 있다
(`hsoc-stack/tools/qbox-platform/platforms/apollo/hw-block/si_cl0.lua:716-779`,
`hsoc-stack/tools/qbox-platform/platforms/apollo/hw-block/si_cl0.lua:903-930`).
CMN r3p0 discovery graph은 완료됐지만 coherent data fabric을 의미하지 않는다.

### 5.5 Safety Island CL1

현재 4개 R82 CPU, GICv3, UART, PFDI/HIPC MHU와 SRAM은 실제 firmware를
실행한다. 남은 부채는 local interconnect/SCR, detailed PPU/AE, timer/watchdog,
DMA, FMU/SSU와 diagnostic IP다. host-facing cluster utility는 broad memory
window이고 PPU transition timing도 FVP block-level 의미보다 단순하다
(`hsoc-stack/tools/qbox-platform/platforms/apollo/hw-block/si_cl1.lua:19-44`).

latest QBox는 SI1 RPMsg attach에 도달하지만 latest FVP capture에는 같은 marker가
없다. 이는 현재 QBox failure가 아니라 same-artifact FVP evidence 부재다.

### 5.6 AP CPU, DSU, CMN과 GIC multiview

4 CPU의 A720AE instruction execution과 SMP boot는 동작한다. 다음은 부분 모델이다.

- QEMU A720AE profile은 지원 가능한 feature만 광고하며 MTE/AMU/MPAM은 없다.
- DSU-120AE L3, snoop filter, DCLS와 cluster safety 의미의 dedicated model이 없다.
- `host_cmn_cyprus`는 r3p0 topology/discovery register model이며 CHI coherent
  mesh, ordering, cache와 latency를 모델링하지 않는다.
- 실제 IRQ delivery는 QEMU GICv3/ITS가 담당하며 `gicx00_multiview`는
  programming-view facade다. GIC-720AE view isolation, distributed/multichip,
  safety 의미는 부분적이다.

CMN topology 자체의 과거 node/revision 차이는 닫혔지만 coherency gap은 그대로다
(`hsoc-stack/tools/qbox-platform/systemc-components/host_cmn_cyprus/include/host_cmn_cyprus.h:408-431`).
GIC multiview도 reserved/inactive redistributor discovery를 포함한 control-plane
facade이며 full distributed GIC를 대체하지 않는다
(`hsoc-stack/tools/qbox-platform/systemc-components/gicx00_multiview/include/gicx00_multiview.h:22-67`,
`hsoc-stack/tools/qbox-platform/systemc-components/gicx00_multiview/include/gicx00_multiview.h:169-232`).
관련 closure와 현재 목표는
(`doc/qbox-fvp-emulation-project.md:135-146`,
`doc/qbox-fvp-emulation-project.md:360-377`).

### 5.7 NI-710AE, SMMU, PCIe와 ITS

활성 기본 이름은 `systemc-mmu720ae`이지만 실제 Lua는 QBox core
`smmuv3`를 조립한다
(`hsoc-stack/tools/qbox-platform/platforms/apollo/hw-block/config.lua:269-271`,
`hsoc-stack/tools/qbox-platform/platforms/apollo/hw-block/config.lua:614-648`).
따라서 qbox-platform local `mmu720ae`의 STE/CD walker 미구현을 활성 기본
dataplane의 P0로 계산하지 않는다. local component가 남아 있는 것과 backend
이름이 실제 module type과 다른 점은 maintenance/documentation debt다.
local component를 제거하거나 승격하기 전에는 CMake/Lua reachability를 별도로
확인해야 한다.

활성 `smmuv3`의 stage-1/2, two-level STE, translated DMI 단위 기능은 존재하지만
Apollo full RSE-first chain의 다음 조합은 아직 qualification gap이다.

- 다른 ASNI/AMNI ingress, permission과 DMI matrix
- PCIe requester/StreamID별 DMA isolation
- EVTQ/PRIQ overflow, invalid STE/CD와 TLBI ordering
- invalid DeviceID/EventID, ITS affinity와 invalidation
- SMMU event→NI-710AE FMU→SSU physical route
- QEMU `arm_smmuv3` backend와 SystemC backend의 동일 fault behavior

현재 PCIe MSI-X/LPI/INTx와 SMMU fault observer는 opt-in focused profile이며
normal RSE-first full chain 전체를 증명하지 않는다
(`hsoc-stack/tools/qbox-platform/platforms/apollo/README.md:209-274`).

### 5.8 SMD/System Management

SMD shared SRAM은 현재 1 MiB로 수정되어 과거 8 KiB gap은 닫혔다
(`hsoc-stack/tools/qbox-platform/platforms/apollo/hw-block/config.lua:551-553`,
`hsoc-stack/tools/qbox-platform/platforms/apollo/hw-block/system_mgmt.lua:434-443`).
남은 부채는 다음과 같다.

- RGM register/sequencer
- SYSTOP PIK의 register/IRQ semantics
- DBGTOP power integration
- SMD UART, GPIO와 System ID
- ATU/APU filter와 error record 전체
- CSS counter control/read/sync의 cross-domain 시간 동등성

DBGTOP, SMD UART/GPIO/System ID의 현재 미구현 분류는 programmer map과 현재
active Lua 비교에도 기록되어 있다
(`doc/apollo-fvp-qvp-hardware-comparison-ko.md:234-243`).

## 6. P1: System Software와 Firmware 계약 부채

### 6.1 MHU/SCMI/PFDI/HIPC/RPMsg 오류 경로

정상 live peer와 malformed descriptor 일부는 동작한다. 다음 matrix는 남아 있다.

- peer offline 전·중·후 request
- SI0/AP/RSE reset 중 pending request cancellation
- duplicate notification, BUSY channel과 timeout
- malformed/oversized SCMI 뒤 정상 recovery
- invalid RPMsg descriptor 뒤 recovery
- PFDI fault injection, partial CPU availability와 retry
- PSCI off/suspend failure 및 FF-A malformed/denied/timeout

MHU model은 doorbell register뿐 아니라 SCMI/PFDI/RPMsg service hook도 포함한다.
장기적으로 hardware frame과 protocol/service completer를 분리해 register-faithful
reset/error semantics를 독립 검증해야 한다. 현재 남은 PFDI 범위는 기존 문서에도
peer-offline, reset cancellation과 fault injection으로 명시되어 있다
(`doc/apollo-qvp-fvp-qbox-non-ap-pfdi-analysis-2026-07-17-ko.md:243-249`,
`doc/qbox-fvp-emulation-project.md:350-358`).

### 6.2 Secure storage와 Trusted Services

과거 RSE-focused 증거에는 PSA IAT/ITS/PS timeout, PS403 incomplete와
Trusted Services test 누락이 기록되어 있다
(`doc/qbox-fvp-emulation-project.md:246-266`). 2026-07-18 fresh full-system
재검증에서는 IAT와 ITS API test가 return code 0으로 통과했고 PS binary도
존재했다. 따라서 IAT/ITS timeout은 닫혔으며, 이 항목의 현재 gap은 PS exhaustive,
TS/UEFI binary 부재와 동일-state FVP 비교다.

OP-TEE/SMMGW `error -4`와 logging fallback은 FVP와 QBox 양쪽에 공통이므로
QBox 고유 하드웨어 gap으로 단정하지 않는다
(`build/fvp-tmux/apollo-qvp-20260717-223809/uarts/tf_a.log:268-272`,
`build/qbox-apollo-qvp/yocto-apollo-qvp-20260718-160644/qbox-secure-console.log:265-269`).
fresh 동일 storage state에서 PS exhaustive와 Trusted Services를 다시 실행해야
한다.

### 6.3 Secure FWU A/B

현재 부팅은 FWU ABI 1.0, 첫 Regular State, Linux reboot 요청과 RSE/SI/AP의
두 번째 Regular State까지 증명한다. 그러나 capsule 적용, RSE image 1, AP
`FIP_B`, U-Boot Trial State, `whichImageSet`, rollback, anti-rollback과
cross-reboot metadata persistence는 증명하지 않았다. capsule 파일 자체는
per-run ESP에서 확인돼 남은 경계는 update discovery 이후다.

완료 조건은 같은 bounded workflow에서 다음을 순서대로 증명하는 것이다.

1. bank-0 정상 부팅과 capsule 발견
2. capsule apply 및 metadata writeback
3. reset 후 bank-1 trial boot
4. success commit 또는 의도적 실패 뒤 bank-0 rollback
5. FVP/QBox의 bank/metadata marker와 flash diff 비교

## 7. P2: Memory Map, Peripheral과 검증 부채

### 7.1 AP programmer model 9.1.1

현재 AP map audit는 required-now row를 통과하지만 다음 20개 row를
`deferred_epic`으로 non-gating 처리한다
(`scripts/test/audit_qbox_apollo_ap_memory_map.py:134-172`).

- AP Memory Expansion 1/2
- System NoC0~3 GPV
- AP secure SCMI/RSE/SI MHU sender/receiver windows
- STM
- SMD AP expansion NoC config
- PCIe NI-710AE memory space
- CMN GPV
- cluster management domain
- memory-controller control
- debug memory map
- DRAM high programmer-model span

required-now 안에서도 AP secure watchdog와 RGIC2LGIC는 explicit placeholder이며,
shared SRAM/FMUs/GIC/RoS/SMD access/low DRAM/SMMU aggregate는 partial이다.
audit pass는 full memory-map fidelity pass가 아니다.

### 7.2 RoS와 synthetic peripheral

현재 RoS는 virtio block 0~3, net, RNG와 PL031 RTC를 모델링한다. system
register, P9, VSI0/1과 UART0/1은 truth table에서 `modeled=false`다
(`hsoc-stack/tools/qbox-platform/platforms/apollo/hw-block/ros.lua:119-148`).
FVP-only test convenience가 필요한지 guest software usage부터 확인한 후 구현한다.

### 7.3 Timer와 clock

AP per-core architectural timer, non-secure MMIO timer와 125 MHz REFCLK
frame wiring은 존재한다. 다음 직접 증거가 없다.

- secure MMIO frame expiry와 SPI48
- RSE/SI/CSS `host_gtimer` control/read/sync cross-domain semantics
- reset 전후 counter continuity와 compare IRQ
- clock tree/divider/PLL lock behavior

clock tree와 analog timing은 현재 기능 fidelity 범위 밖이지만 secure/safety
timeout에 필요한 counter/IRQ는 기능 검증 대상이다.

### 7.4 QEMU-local CFI crash durability

정상 종료, reset, migration과 cold/reuse hash는 검증됐다. abrupt host power
loss 또는 `SIGKILL`이 25 ms deferred-writeback window 안에서 발생할 때
dirty sector durability는 아직 검증되지 않았다. 이 시험은 성능 기준이 아니라
storage correctness 시험이다.

## 8. 폐기하거나 재분류한 과거 항목

다음 항목은 최신 source와 실행 기준에서 그대로 open으로 세면 안 된다.

| 과거 주장 | 현재 판정 | 남은 실제 부채 |
| --- | --- | --- |
| SI0 CMN graph가 r0p0/축약 | closed | CFG2 r3p0 discovery는 완료, CHI coherency는 partial |
| SMD shared SRAM이 8 KiB | closed | 현재 1 MiB, alias/coherency negative matrix는 별도 |
| QBox SMMU page walk 전체 미구현 | reclassified | 활성 기본은 QBox core `smmuv3`; Apollo full-chain exhaustive qualification이 남음 |
| PCIe requester/MSI/LPI 경로 없음 | closed for focused slice | RSE-first full-chain 오류/invalidation matrix가 남음 |
| SI1 HIPC/RPMsg peer 없음 | closed | peer-offline/reset/fault path가 남음 |
| AP-RSE measured boot/FWU proxy | closed | actual MHU2/ATU가 default, capsule A/B는 open |
| AP secure timer가 `gs_memory` | closed | QEMU MMIO generic timer, secure-frame runtime evidence가 남음 |
| RGIC2LGIC가 broad memory | reclassified | named model은 있으나 stream/collator semantics가 partial |
| CSS/RSE counter가 `gs_memory` | closed | `host_gtimer` 기능 subset, sync/reset matrix가 남음 |
| SACFG/NSACFG/MPC/SIC 전체 inert | reclassified | `rse_protection_ctrl` subset, exhaustive policy가 남음 |
| full-system QBox 기본이 16 CPU | closed | active default 4 CPU, CPU4~15는 out of scope |
| SI1 PFDI timeout과 MHU RX warning | closed | current logs에서 재현 안 됨, negative matrix가 남음 |
| RSE cold initialization 미완료 | closed | QEMU-local CFI가 default, crash durability만 open |

최신 closure 근거는
`doc/apollo-qvp-fvp-qbox-yocto-system-log-comparison-2026-07-17-ko.md:1019-1033`,
`doc/qbox-fvp-emulation-project.md:123-163`과 current Lua source를 우선한다.

## 9. 권장 실행 순서

### Stage 0: Evidence와 contract 정상화

1. topology validator 3건 수정
2. latest QBox run에 coverage audit 생성
3. root-shell post-login PFDI/remoteproc/RPMsg/service gate 복원
4. FVP/QBox artifact와 initial writable-state hash 고정
5. automated same-state differential 생성

#### Stage 0 완료 기록 (2026-07-18)

상태는 **완료**다. topology 3건, post-login qualification, pre-run state hash,
same-state differential과 current coverage를 하나의 4 CPU acceptance 흐름으로
정리했다.

- `system_ap_mhu_pointer_data`와 `system_ap_rse_mailbox`는 전체 128 KiB backing
  크기를 명시하고, AP cold reset fanout에 BL2 header SRAM을 포함했다.
  `tests/test_validate_qbox_apollo_topology.py`는 19건 모두 통과했다.
- primary UART input FIFO를 host `std::thread`에서 polling하며 SystemC socket을
  호출하던 경로는 MULTI QEMU 실행을 BL31 PFDI 직후 정지시켰다. polling과
  enqueue를 SystemC `rcv_thread`로 이동했고, FIFO off/on 원인 토글 및 실제
  부팅으로 확인했다. QBox local build와 Yocto native provider build가 모두
  통과했다.
- lower/full runner는 shell prompt offset 기준으로 40개 명령을 순차 전송한다.
  PFDI CPU0~CPU3, remoteproc/RPMsg/`ethsi1`, SMMUv3, DSU PMU, virtio, PL011과
  failed systemd unit 수를 JSON과 console log에 남긴다. fresh Yocto QBox 결과는
  G0/G1/G4 pass, `post_login_probe.passed=true`, `first_failing_marker=null`이다.
- FVP runner도 rootfs/EFI를 reflink하고 실행 전 artifact hash를 기록하며,
  terminal-status 응답과 shell prompt를 분리해 post-login 명령을 순차 전송한다.
  입력 echo가 아닌 독립 done marker만 완료로 인정한다.
- FVP와 QBox는 각각 fresh writable copy와 ephemeral RSE state로 실행했다.
  `ap_flash`, provisioning bundle, rootfs, RSE ROM/flash/OTP의 6개 공통 hash가
  모두 같았다. provider별 capsule disk container는 공통 byte-hash 판정에서
  제외하고 이후 FWU stage에서 payload/lifecycle로 검증한다.
- 이 SHA-256 기록은 same-state qualification의 명시적 비용이다. 이후 일반
  `run_qbox_yocto.sh` 실행은 20 GiB 이상인 sparse WIC의 논리 영역 전체를 매번
  읽지 않으며, 동일 상태 비교를 수행할 때만 `--record-initial-state`를 사용해
  기존 `initial-state.json` 증거를 생성한다.
- automated differential은 RSE, SI0, SI1, secure, primary 5개 domain, 공통
  canonical timestamp 4개, SMMU/ITS/PFDI 4 CPU, failed service 0건과 map
  contract를 비교해 전 항목 통과했다.
- coverage auditor는 더 이상 `not_run`을 pass로 기록하지 않는다. 현재
  live-cl0-cl1 실행에 적용되는 G0/G1/G4만 gating이고, 다른 실행 mode의
  G2/G3 및 differential sidecar 이전 G5는 `passed=false, gating=false`로
  명시된다.

완료 증거:

- QBox Yocto fresh-state:
  `build/qbox-apollo-qvp/stage0-same-state-v2-20260718-1906/result.json`
- FVP fresh-state:
  `build/fvp-boot-logs/stage0-same-state-v3-20260718-1855/result.json`
- differential:
  `build/qbox-apollo-qvp/stage0-same-state-v2-20260718-1906/same-state-differential.json`
- coverage:
  `build/qbox-apollo-qvp/stage0-same-state-v2-20260718-1906/full-coverage-audit.json`
- 4 CPU contract:
  `build/qbox-apollo-qvp/stage0-same-state-v2-20260718-1906/fidelity-contract.json`
- regression suite: topology/runner/FVP/coverage/differential 관련 103건 통과
- build: `./local_build.sh qbox`, `bitbake qbox-apollo-qvp-native` 통과

### Stage 1: Watchdog와 reset owner

1. AP non-secure watchdog FVP MMIO probe
2. address/frame 정합 수정
3. AP secure watchdog 기능 모델
4. SI0/RSE watchdog 기능 모델
5. RGM/PIK/PPU/reset signal topology

#### Stage 1 완료 기록 (2026-07-18)

상태는 **완료**다. AP, SI0, RSE watchdog를 동일한 2단계 SystemC 모델로
통일하고, AP WS1에서 CSS RGM을 거쳐 cold-reset fanout으로 이어지는 reset
owner 경로를 추가했다.

- FVP의 AP non-secure watchdog는 Linux `sbsa-gwdt` probe로 control frame
  `0x1A420000`, 125 MHz counter와 10초 timeout을 확인했다
  (`build/fvp-boot-logs/stage1-ap-watchdog-frame-probe-v2-20260718/
  terminal_ns_uart0_5004.log`). 해당 image에는 `devmem`/BusyBox `devmem`
  applet이 없어 register write probe 결과는 증거로 채택하지 않았다.
- QBox의 기존 QEMU SBSA watchdog 연결은 SysBus MMIO frame 순서와 Apollo
  address contract가 반대로 기록돼 있었다. AP non-secure control/refresh를
  각각 `0x1A420000`/`0x1A430000`으로 바로잡고, QEMU-local 수정 없이
  `zena_watchdog` C++14 SystemC/TLM 모델로 교체했다.
- 같은 기능 모델을 AP secure `0x1A460000/0x1A470000`, SI0
  `0x2A700000/0x2A710000`, RSE NS/S watchdog에 적용했다. WCS/WOR/WCV/WRR,
  refresh re-arm, WS0/WS1 2단계 만료와 reset 입력을 모델링했다.
- `zena_reset_ctrl`은 CSS RGM syndrome/mask, SYSTOP PIK clock-force와
  power/reset request/ack의 firmware 사용 subset을 구현한다. 기존 broad
  `gs_memory` PIK를 4 KiB 기능 frame으로 교체하고, 인접
  `0x20000D0201000` SYS0 PPU는 기존 `host_ppu`를 유지했다.
- AP NS WS1은 SPI51과 CSS RGM에 fan-out하고, secure WS1도 RGM으로
  전달한다. RGM AP reset 출력은 BL2 loader, BL2 header SRAM, reset GPIO와
  활성 SMMU를 소유한 `ap_cold_reset_fanout`으로 이어진다. SI0 WS1은 RGM
  syndrome/mask 입력에 연결했다. RSE NS WS0/WS1은 architected NVIC IRQ1/0
  경로를 유지한다.
- QBox와 QEMU core에는 watchdog/reset 모델을 추가하지 않았다. 새 기능은
  Apollo overlay인 `hsoc-stack/tools/qbox-platform`에 한정해 upstream 대비
  core delta를 최소화했다.

완료 증거:

- SystemC component tests: `zena_watchdog-tests`,
  `zena_reset_ctrl-tests` 2건 통과
- topology contract: `tests/test_validate_qbox_apollo_topology.py` 20건 통과
- map validation:
  `build/qbox-apollo-qvp/full-map-validation.json`,
  `build/qbox-apollo-qvp/stage1-ap-map-audit-v2.json`
- local build: `./local_build.sh qbox` 통과
- 4 CPU local full-system boot:
  `build/qbox-apollo-qvp/stage1-watchdog-reset-20260718/result.json`,
  `passed=true`; RSE, SI0, SI1, TF-A와 Linux boot marker 유지
- QBox Linux watchdog probe:
  `build/qbox-apollo-qvp/stage1-watchdog-reset-20260718/
  qbox-primary-console.log`의 `sbsa-gwdt 1a420000.watchdog`, 125 MHz,
  10초 timeout 초기화

### Stage 2: Safety vertical

1. DCLS fault source
2. NI-710AE APU violation
3. CPU/DSU/CMN RAS source
4. FMU/SSU/ESM clear와 escalation
5. reset/recovery acceptance

#### Stage 2 완료 기록 (2026-07-18)

상태는 **대표 APU fault 수직 슬라이스 완료**다. 이 단계의 acceptance는 모든
silicon safety source를 흉내 내는 것이 아니라, 실제 permission denial 한 건이
reset/recovery까지 끊기지 않는지 검증하는 것으로 제한했다.

- `host_ni710ae_nci`가 reset-owner 또는 programmed APU policy에 의해 access를
  거부하면 `apu_fault` level pulse를 발생시킨다. QEMU 실행 thread에서 fault가
  발생해도 FMU 상태를 직접 건드리지 않도록 `runonsysc`를 통해 SystemC kernel
  thread에서 signal을 전달한다.
- SI0 primary NI-710AE의 `apu_fault`를 root `si_cl0_fmu` record 0에 연결했다.
  FMU critical IRQ는 SPI128, critical status는 SSU로 전달되고 SSU
  `safety_status`는 CSS RGM `safety_fault_reset` 입력으로 이어진다.
- CSS RGM은 EXP0 syndrome bit 24를 latch하고 같은 mask bit가 enable된 경우
  AP cold-reset fanout을 assert한다. FMU와 SSU W1C clear 뒤 reset 출력이
  deassert되는 recovery도 검증했다.
- 정상 Apollo 부팅에서는 owner access가 허용되므로 새 fault path가 assert되지
  않는다. RSE, SI0, SI1, TF-A와 4 CPU Linux boot marker가 그대로 통과했다.

완료 증거:

- end-to-end component acceptance:
  `zena_safety_vertical-tests`의
  `APU denial → FMU V/CI → SSU ERRC → RGM EXP0 → AP reset → W1C recovery`
  통과
- 관련 component regression: `host_ni710ae_nci-tests`, `zena_fmu-tests`,
  `zena_reset_ctrl-tests` 포함 4건 통과
- topology contract: `tests/test_validate_qbox_apollo_topology.py` 21건 통과
- local build: `./local_build.sh qbox` 통과
- normal-boot non-regression:
  `build/qbox-apollo-qvp/stage2-safety-vertical-20260718/result.json`,
  `passed=true`

DCLS comparator와 CPU/DSU/CMN RAS는 실제 fault-producing CPU/cluster 모델이
없어 이 단계에서 synthetic signal source로 채우지 않았다. AP RAS의 SPI89
software notification과 기존 `ras_ffh_stub`도 hardware FHI/ERI source를
증명하지 않는다. 이 두 항목은 source register/interrupt 의미를 갖춘 모델과
FVP injection oracle이 확보될 때까지 section 5.2의 명시적 잔여 부채로 유지한다.

### Stage 3: Memory, I/O와 interrupt

1. active SMMU backend의 RSE-first DMA/MSI/ITS qualification
2. ASNI/AMNI permission 및 DMI negative matrix
3. invalid ID/TLBI/EVTQ/PRIQ ordering
4. AP 9.1.1 deferred row를 software usage에 따라 승격

#### Stage 3 완료 기록 (2026-07-18)

상태는 **4 CPU active-path 최소 qualification 완료**다. 정상 PCIe DMA와
MSI-X/LPI는 RSE-first full-system에서, legacy INTx와 상세 오류 matrix는 focused
slice/component test에서 검증했다.

- 활성 `systemc-mmu720ae` profile은 qbox-platform의 과거 local
  `mmu720ae` dataplane이 아니라 QBox core `smmuv3`와 `smmuv3_tbu`를 사용한다.
  따라서 invalid STE/CD, stage-1/stage-2, stream isolation, TLBI, EVTQ/PRIQ,
  GERROR와 translated DMI 판정은 실제 활성 backend의 153개 test로 검증했다.
- NI-710AE의 ASNI/AMNI discovery, reset owner, programmed secure/non-secure
  permission, debug access, region lock와 DMI allow/deny가 포함된 9개 test가
  통과했다. permission denial이 downstream side effect를 만들지 않는 것도
  함께 확인했다.
- full-system과 direct AP profile의 SMMU capability가 각각 PAMAX/SIDSIZE
  52/32와 48/8로 달랐던 계약을 52/32로 통일했다. GICv4.1 collection entry는
  FVP와 같은 2 byte를 유지한다. 현재 QEMU는 configured entry size만큼만
  CTE를 read/write하므로 인접 entry를 덮지 않으며, Linux에서
  `32768 Interrupt Collections`, `esz 2`가 실제로 확인됐다.
- 4 CPU RSE-first 실행은 RSE, live SI0/SI1, TF-A/U-Boot를 거쳐 Linux에서
  `0000:00:01.0` endpoint, SID `0x40`, DeviceID `0x8`을 사용했다. 실제 network
  traffic 뒤 CPU0 MSI-X LPI가 8 증가했고 PFDI/RPMsg marker와 Linux login도
  유지됐다.
- 같은 endpoint의 focused `pci=nomsi` 실행에서 GPEX SPI input 301,
  architectural INTID 333이 CPU0에서 9 증가했다. direct runner는 WIC 안의
  U-Boot boot script를 사용하지 않으므로 `pci=nomsi`를 `--bootargs`에도
  명시하도록 README의 실행 계약을 수정했다. 두 실행 모두 4 CPU를 명시한다.
- AP 9.1.1 audit는 required-now 18개 row가 모두 통과했고 deferred 20개 row는
  active DT에 consumer가 없었다. 주소만 채우는 placeholder를 추가하지 않고
  20개 모두 deferred로 유지했다.

완료 증거:

- active SMMUv3 component regression: 153건 통과
- NI-710AE permission/DMI regression: 9건 통과
- Python wiring/profile/runner regression: 34건 통과
- local build: `./local_build.sh qbox` 통과
- RSE-first MSI-X/LPI full-system:
  `build/qbox-apollo-qvp/stage3-rse-first-pcie-msix-20260718/result.json`,
  `passed=true`
- RSE-first MSI-X와 focused INTx 통합 판정:
  `build/qbox-apollo-qvp/stage3-rse-first-pcie-irq-validation-20260718.json`,
  `status=pass`
- 4 CPU direct MSI-X/INTx pair:
  `build/qbox-apollo-fvp/stage3-pcie-irq-runtime-validation-4cpu-20260718.json`,
  `status=pass`
- AP map:
  `build/qbox-apollo-qvp/stage3-ap-map-audit-20260718.json`,
  `passed=true`, required-now 18, deferred 20

invalid DeviceID/EventID를 실제 GPEX/ITS에 주입하는 full-system 시험과
QEMU `arm_smmuv3` 대 SystemC backend의 fault-by-fault differential은 이번 빠른
acceptance에 넣지 않았다. 기능을 구현한 것으로 간주하지 않고 section 5.7의
잔여 exhaustive qualification 부채로 유지한다.

### Stage 4: Firmware service

1. PFDI/HIPC/RPMsg peer-offline/reset matrix
2. PSCI/FF-A negative matrix
3. secure-service post-login tests
4. capsule apply, bank-1, rollback과 persistence
5. CFI crash durability

#### Stage 4 1차 완료 기록 (2026-07-18)

상태는 **reset/service 최소 수직 슬라이스 완료, capsule A/B acceptance 미완료**다.
빠른 acceptance는 peer reset 복구, 실제 secure-service 두 건, full-system reset 뒤
두 번째 4 CPU 부팅에 한정했다. A/B lifecycle을 통과한 것으로 확대 해석하지 않는다.

- AP cold reset은 AP 소유 MHU frame의 doorbell, IRQ, pending requester와 retry
  상태를 지우되 SMD 소유 shared SRAM은 보존한다. reset 중인 peer는 offline으로
  취급하며 synthetic completion을 만들지 않고, deassert 뒤 정상 retry가 requester를
  release하는 것을 component test로 확인했다.
- fresh secure-service 진단에서 IAT/ITS/PS binary가 존재하고 TS/UEFI binary가
  부재함을 확인했다. 이 중 실제 IAT와 ITS API test는 각각 return code 0으로
  통과했다. PS exhaustive, TS와 UEFI는 이번 최소 acceptance에서 통과했다고
  주장하지 않는다.
- RSE SYSCTRL `SWRESET` bit 5는 이제 reset syndrome을 보존하면서 Apollo
  full-system reset pulse를 발생시킨다. reset fan-out은 RSE CPU accelerator,
  QEMU instance, KMU/CC3XX, NI-710AE, SI0/SI1 QEMU와 PPU/MHU 상태를 초기화한다.
- SI0의 두 번째 부팅 Data Abort 원인은 NI-710AE discovery/APU 상태가 reset되지
  않은 것이었고, model reset과 DMI invalidation을 추가해 제거했다. AP가 RSE MHU
  receiver 초기화보다 먼저 measured-boot request를 보내던 deadlock은 AP PPU를
  full-system reset 대상에 포함해 해소했다.
- AP PPU power-on load pulse는 정상 AP cold reset의 일부이므로 PPU 자신까지
  reset하면 feedback loop가 된다. 이를 막기 위해 `ap_cold_reset_bind_targets()`와
  `ap_system_reset_bind_targets()`를 분리했다. 최초 부팅은 기존 순서를 유지하고,
  RSE full-system reset에서만 AP core PPU state를 OFF/reset으로 되돌린다.
- Yocto FWU probe는 첫 Linux login, capsule copy, reboot 요청 뒤 RSE, SI0, SI1,
  TF-A/U-Boot와 Linux가 모두 두 번째 부팅에 도달했다. 이전의 `SCP is not ready`,
  NI-710AE Data Abort, FW_CONFIG MHU wait deadlock은 재현되지 않았다.

완료 증거:

- MHU reset/peer-offline component regression: `mhu320ae-tests` 통과
- RSE reset register/component regression: `rse_sysctrl-tests`와
  `rse_sysctrl-reset-tests` 통과
- NI-710AE/PPU reset regression: `host_ni710ae_nci-tests`, `host_ppu-tests` 통과
- secure-service diagnostic:
  `build/qbox-apollo-qvp/stage4-secure-diag-20260718/result.json`, `passed=true`
- actual IAT/ITS:
  `build/qbox-apollo-qvp/stage4-secure-iat-its-green-20260718/result.json`,
  `secure_psa_iat_api_test_rc=0`, `secure_psa_its_api_test_rc=0`
- full-system second-boot evidence:
  `build/qbox-apollo-qvp/stage4-fwu-bank1-reset-pass-20260718/`의 UART 로그에서
  RSE TF-M, SI0 module init, SI1 Zephyr와 U-Boot가 각각 두 번 관찰되고 두 번째
  U-Boot도 `FWU: System booting in Regular State`까지 진행
- pre-staged cold non-regression:
  `build/qbox-apollo-qvp/stage4-fwu-prestaged-cold-20260718/result.json`,
  `passed=true`, post-login 4 CPU PFDI/remoteproc/RPMsg/service probe 통과

명시적 잔여 항목:

- Linux가 복사한 `EFI/UpdateCapsule/fw.cap`은 host FAT 검사에서 실제 WIC에
  존재했다. 같은 WIC의 cold start에서도 U-Boot는 capsule을 자동 적용하지 않아
  `FWU: Updating`, RSE image 1, `FIP_B`, Trial State가 0건이었다. 따라서 disk
  writeback 부재가 아니라 QBox full reset 이후 capsule discovery/boot-device
  lifecycle 또는 그 상위 firmware contract의 차이로 범위를 좁혔다.
- capsule apply→bank-1 trial→commit/rollback→metadata/flash persistence와 CFI
  crash durability는 여전히 open이다.
- PSCI/FF-A negative semantics는 TF-A/OP-TEE owner이며 QBox가 synthetic error를
  만들지 않는다. 동일 firmware의 denied/invalid matrix와 PS exhaustive,
  TS/UEFI binary를 포함한 image 검증은 후속 qualification이다.

### Stage 5: 비필수 FVP peripheral

RoS, SMD debug/UART/GPIO/System ID와 나머지 programmer-map row는 실제 firmware,
driver 또는 validation consumer가 있는 순서대로 구현한다. 단순 address fill을
완료로 인정하지 않는다.

#### Stage 5 완료 기록 (2026-07-18)

상태는 **consumer-driven 승격 감사 완료, 신규 peripheral 구현 없음**이다.
활성 Yocto DTB를 DTS로 역변환해 실제 consumer를 다시 확인한 결과, 현재 사용 중인
AP block은 MMIO timer, UART, watchdog, RTC, 네 MHU frame과 virtio 계열이다.

- AP programmer-map required-now 18개 row는 모두 gating 판정을 통과했다. 분류는
  covered 10, partial model 7, explicit placeholder 1이며 마지막 항목은 broad
  memory가 아니라 제한된 `gic720ae_messreg` 구현이다.
- deferred 20개 row에는 활성 DT consumer가 없으며 기존 `deferred_epic` 분류와
  owner를 유지했다.
- RoS, SMD debug/UART/GPIO/System ID와 NoC/CMN 확장 window를 inert memory로
  채우지 않았다. 향후 firmware/driver consumer가 생기는 row만 register side
  effect, IRQ, reset acceptance와 함께 required-now로 승격한다.
- `placeholder`를 pass로 세거나 `not_run`을 성공으로 바꾸는 예외는 추가하지
  않았다.

완료 증거:

- AP map audit:
  `build/qbox-apollo-qvp/stage5-ap-map-audit-20260718.json`, `passed=true`,
  required-now 18, deferred 20, covered/partial/explicit-placeholder 10/7/1
- full-map validator:
  `build/qbox-apollo-qvp/full-map-validation.json`, `passed=true`
- QBox core boundary audit 통과

### Stage 0~5 최종 통합 검증 (2026-07-19)

권장 순서의 구현과 stage별 acceptance를 모두 적용한 뒤 다음 통합 검증을
수행했다.

- 변경된 Python runner, topology, profile, coverage와 same-state 도구 회귀
  124건이 모두 통과했다.
- watchdog, reset, PPU, MHU, NI-710AE, FMU/SSU와 safety vertical을 포함한
  SystemC component test 11건이 모두 통과했다.
- `python3 -m py_compile scripts/*/*.py`, full-map validator와 QBox core boundary
  audit가 모두 통과했다.
- 최종 소스 기준 `./local_build.sh qbox`가 통과했고,
  `bitbake qbox-apollo-qvp-native`도 1,056 task 전부 성공했다.
  Yocto task 증거는
  `build/tmp_baremetal/log/cooker/apollo-qvp/20260718144038.log`에 남아 있다.
- `run_qbox_local.sh --uboot-only --exit-after-pass --no-attach`의 4 CPU 최종
  실행은
  `build/qbox-apollo-fvp/stage-final-local-uboot-pass2-20260718/result.json`에
  `passed=true`, `blocker=null`, `validation_scope=uboot-only`,
  `runtime_elapsed_s=26.7894`를 기록했다. RSE, SI0, SI1, measured boot,
  TF-A/OP-TEE/U-Boot와 `FWU: System booting in Regular State` marker가 모두
  확인됐다. 성능 수치는 pass/fail 기준이 아니라 실행 참고값이다.

최종 검증 중 U-Boot-only 모드가 Linux post-login probe를 잘못 실행해 timeout을
기다리고, probe를 끄면 상위 output 정리가 tmux 소유 UART FIFO를 삭제하는 runner
오류를 발견했다. U-Boot-only에서는 post-login probe를 전달하지 않고, 상위
정리 단계는 tmux가 생성한 `primary-uart-input.fifo`를 보존하도록 수정했다.
관련 runner/tmux 회귀 51건과 실제 U-Boot 부팅으로 재검증했다.

따라서 **권장 Stage 0~5 실행 캠페인은 완료**다. 다만 Stage 4의 capsule
A/B apply/trial/commit/rollback과 아래 명시한 exhaustive qualification은
아키텍처 fidelity 최종 완료 조건으로 남아 있다.

## 10. 명시적 비범위

- CPU4~CPU15 enablement와 16 CPU lifecycle
- KVM backend
- 에뮬레이터 wall-clock 성능 pass/fail
- CHI/NoC cycle-accurate latency와 contention
- analog/PHY 및 silicon safety coverage 수치
- FVP 자체가 제공하지 않는 CoreSight block

4 CPU 성능 수치는 측정 참고로만 사용할 수 있으며 fidelity acceptance에는 넣지
않는다.

## 11. 최종 완료 조건

Apollo QBox가 FVP 수준이라고 주장하려면 최소한 다음 조건이 모두 필요하다.

1. topology, map, route, IRQ와 reset contract validator가 clean하다.
2. placeholder와 missing block이 owner, 영향과 replacement plan을 가진다.
3. watchdog/DCLS/APU 중 선택한 safety source가 reset/recovery까지 이어진다.
4. RSE/SI/AP firmware와 Linux post-login service가 동일 초기 state에서 동작한다.
5. SMMU/PCIe/ITS 정상·오류 경로가 RSE-first full chain에서 검증된다.
6. capsule A/B update와 rollback/persistence가 검증된다.
7. FVP/QBox automated differential이 같은 artifact/state를 비교하고 `not_run`을
   pass로 처리하지 않는다.
8. 관련 변경은 QBox/QEMU/qbox-platform에 한정하고 component source 우회가 없다.

현재 이 조건 중 nominal 4 CPU boot, 주요 live peer, measured boot, full-system
reset 뒤 두 번째 Regular State, cold/reuse storage preservation, 대표 safety
vertical과 active PCIe/SMMU/ITS path는 완료됐다. capsule A/B와 exhaustive
negative/fault matrix는 완료되지 않았으며 이 문서의 잔여 P1/P2로 유지한다.
