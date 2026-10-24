# QBox MHU-320AE SystemC Component Spec

작성일: 2026-06-09
갱신일: 2026-10-23

상태: doorbell 기반 구현·부팅 검증 완료. 2026-10-23 FCE/AE 확장의
구현 및 실행 결과는 [AE 검증 기록](qbox-ae-gic720-mhu320-validation-ko.md) 참조.

관련 문서:

- `doc/qbox-mhu320ae-systemc-design-ko.md`
- `doc/qbox-mhu320ae-systemc-plan-ko.md`
- `doc/qbox-mhu320ae-systemc-tasks-ko.md`
- `doc/apollo-fvp-hardware-analysis-ko.md`
- `doc/apollo-qbox-hardware-ko.md`
- `doc/arm_zena_css_dev_guide/08-fixed-virtual-platform.md`
- `doc/arm_zena_css_dev_guide/09-programmers-model-for-zena-css.md`
- `doc/arm-zena-css-hardware-blocks.md`

## 목표

Arm Zena CSS FVP에서 Safety Island와 system management 통신에 사용되는
Arm MHU-320AE Message Handling Unit을 QBox SystemC/TLM component로 모델링한다.
목표는 Linux/Zephyr/TF-M/SCP-firmware가 보는 `arm,mhuv3` programming model,
PBX/MBX doorbell 상태, combined interrupt, SCMI shared-memory transport,
PFDI monitor, AP-SI/RSE doorbell bridge를 QEMU 없이 SystemC component에서
제공하는 것이다.

## 완료 목표

이번 구현의 완료 지점은 다음이며 2026-06-09 기준 모두 만족했다.

- Lua-visible component `mhu320ae`가 `hsoc-stack/tools/qbox-platform/systemc-components/mhu320ae/`
  아래에 생성되고 dynamic module로 빌드된다.
- 기존 MHUv3 compatibility path에 있던 reusable PBX/MBX register frame behavior와
  Apollo/RD-Aspen boot에 필요한 service hooks가 `mhu320ae`로 이동된다.
- AP SCMI MHU, RSE/AP secure doorbell, RSE/SI SCMI, AP/SI CL1 HIPC, CL1 PFDI
  경로의 default module type이 `mhu320ae`로 전환된다.
- Component test가 MHU-320AE 이름으로 존재하고 PBX/MBX register, interrupt,
  SCMI, reset, PFDI, doorbell bridge, RPMsg name-service path를 검증한다.
- Apollo full-system QBox boot에서 RSE, Safety Island CL0/CL1, TF-A,
  U-Boot, Linux login, post-login probe가 통과한다.

## 기준 IP와 근거

Zena CSS 개발 가이드는 FVP가 Safety Island에 Arm MHU-320AE Message Handling
Unit을 포함한다고 명시한다. Linux와 Zephyr에서 보이는 device-tree compatible은
`arm,mhuv3`이다. 따라서 QBox component 이름은 제품 IP 기준의 `mhu320ae`로
두고, programming model은 MHUv3-compatible PBX/MBX frame으로 노출한다.

주요 FVP/QBox visible address와 IRQ:

| Path | Frame | Address | Size | IRQ |
| --- | --- | --- | --- | --- |
| AP SCMI TX | PBX | `0x40020000` | `0x30000` | SPI 112 |
| AP SCMI RX | MBX | `0x40050000` | `0x30000` | SPI 113 |
| AP-SI CL1 HIPC TX | PBX | `0x400b0000` AP view, `0x39000000` CL1 local | `0x30000` | SPI 120 / CL1 SPI 40 |
| AP-SI CL1 HIPC RX | MBX | `0x400e0000` AP view, `0x39040000` CL1 local | `0x30000` | SPI 121 / CL1 SPI 41 |
| CL1 PFDI monitor | PBX | `0x39200000` | `0x20000` | CL1 SPI 50 |
| RSE local CMU MHU2 | PBX/MBX | `0x501a0000`-class secure PPC view | `0x10000` each | TF-M IRQ 44/45 |

The AP DTS exposes `mailbox@40020000`, `mailbox@40050000`, `mailbox@400b0000`, and
`mailbox@400e0000` as `compatible = "arm,mhuv3"`. The Safety Island CL1 DTS exposes
local HIPC and PFDI MHU nodes with the same compatible string.

## 범위

- MHUv3 PBX/MBX register window, channel decode, feature/ID registers.
- Configurable channel count. Apollo CL1 uses 32 channels; generic AP/RSE paths
  keep the previous 128-channel default unless platform data overrides it.
- PBX `DBCW_SET`, `DBCW_INT_ST`, `DBCW_INT_CLR`, `DBCW_INT_EN`, `DBCW_CTRL`
  behavior.
- MBX `DBCW_ST`, masked status, clear, mask set/clear, combined interrupt
  behavior.
- Combined DBCH interrupt status words and SystemC signal output.
- Pair-isolated PBX to MBX routing by `pair`.
- SCMI Base, Power Domain, System Power, and PFDI monitor protocol responses
  used by the existing Apollo/RD-Aspen firmware stack.
- AP/SI CL1 doorbell bridge behavior needed for HIPC resource table seeding,
  RPMsg name-service injection, and synthetic TX completion.
- Trace hooks and log files compatible with existing `mhuv3-trace.log` tools.
- 2026-10-23 확장: configurable 32/64-bit fast channel, 그룹별 IRQ,
  read-clear 및 latest-value 의미, pair/reset 격리.
- 선택적 SRAS/RRAS error record, CE/UC insertion 및 W1C acknowledge.
- 별도 `zena_device_fmu` MHU profile의 보호 메커니즘 설정, injection,
  criticality, parent FMU 전파 및 lock/key 규약.
- 실제 `apollo-qvp` SCP MHU3 driver 수정 및 SI0 FCE IRQ echo 진단.

## 비범위

- Full MHU-320AE TRM parity for every optional register and safety/RAS feature.
- Linux/Zephyr/TF-M의 새 FCE API. 현재 제품의 FCE 진단은 SCP MHU3
  driver와 AP MMIO를 사용한다.
- Modeling analog timing or interconnect arbitration delay.

## 기능 요구사항

### FR1. SystemC/TLM component

`mhu320ae`는 pure SystemC/TLM dynamic module로 빌드되어야 한다. Lua platform은
`moduletype = "mhu320ae"`로 component를 생성한다.

### FR2. MHUv3-compatible register identity

Linux `arm-mhuv3-mailbox`와 Zephyr `arm,mhuv3` driver가 사용하는 ID,
feature, DBCH config, PBX/MBX doorbell register 동작을 제공해야 한다.

### FR3. Pair-isolated doorbell routing

동일한 `pair` 값을 가진 PBX/MBX만 서로 신호를 전달한다. 이름이 있는 pair가
없으면 global fallback을 사용하지 않는다.

### FR4. SCMI and PFDI transport

SCMI shared-memory request를 channel range에 따라 decode하고 Base, Power
Domain, System Power, PFDI monitor response를 작성한다. Response 후 configured
ACK bit를 paired MBX에 signal한다.

### FR5. Runtime observability

Trace file은 기존 `mhuv3-trace.log` 소비 도구와 호환되어야 한다. Component
이름은 `mhu320ae`여도 event token은 `mhu_trace`를 유지할 수 있다.

### FR6. Fast Channel Extension

PBX payload write는 같은 pair의 MBX payload와 pending bit를 갱신한다.
미수신 payload를 덮어쓰면 최신 값 하나를 유지한다. MBX payload read는
해당 채널의 pending을 지우며 그룹/combined IRQ도 갱신한다. 64-bit 채널은
정렬된 64-bit 및 두 번의 32-bit 접근을 지원한다. Apollo 기본 geometry는
64채널, 그룹당 32채널, 32-bit이며 실제 실리콘 구성값을 의미하지 않는다.

### FR7. Functional safety programming model

RAS를 켠 endpoint는 기능과 record 수를 광고하고 CE count, overflow,
W1C 및 error summary를 일관되게 제공한다. RAM ERRINS는 payload를
훼손하지 않는 소프트웨어 진단이며 물리 ECC 검출 또는 FMU hardware event와
동일시하지 않는다. FMU에는 Secure access, one-shot KEY, criticality,
record queue, interrupt enable, reset과 parent acknowledge 의미를 적용한다.

## 검증 기준

- `cmake --build build/local-apollo-fvp/work/qbox-platform --target mhu320ae mhu320ae-tests platforms-vp`
  성공.
- `ctest --test-dir build/local-apollo-fvp/work/qbox-platform -R 'mhu320ae' --output-on-failure` 성공.
- `scripts/run/run_qbox_apollo_fvp_full.py --skip-build --si-mode live-cl1
  --post-login-probe`에서 integrated CL1 Zephyr, AP HIPC/RPMsg, PFDI
  marker가 통과.
- `scripts/run/run_qbox_apollo_fvp_full.py --skip-build --si-mode live-cl0-cl1
  --post-login-probe`에서 full-system marker와 post-login probe가 통과.
- Runtime result JSON에 `mhu_backend = "systemc-mhu320ae"` 또는 동등한
  fidelity label이 기록된다.
