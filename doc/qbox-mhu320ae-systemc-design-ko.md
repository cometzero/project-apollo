# QBox MHU-320AE SystemC Component Design

작성일: 2026-06-09
갱신일: 2026-10-23

## 설계 요약

`mhu320ae`는 Arm MHU-320AE 제품 IP를 QBox에 노출하는 SystemC component다.
소프트웨어가 보는 programming model은 `arm,mhuv3` PBX/MBX doorbell 및
fast-channel frame이다. Fast Channel Extension(FCE)은 공유 SRAM을 polling하는
SCMI fast channel과 별개이며, PBX payload write를 상대 MBX에 전달한다.
기존 `mhuv3_stub`의 검증된 PBX/MBX register frame과 Apollo boot service hook을
보존하되, default platform wiring은 `mhu320ae`로 전환한다.

## Component 구조

파일 배치:

- `hsoc-stack/tools/qbox-platform/systemc-components/mhu320ae/CMakeLists.txt`
- `hsoc-stack/tools/qbox-platform/systemc-components/mhu320ae/include/mhu320ae.h`
- `hsoc-stack/tools/qbox-platform/systemc-components/mhu320ae/src/mhu320ae.cc`
- `hsoc-stack/tools/qbox-platform/tests/components/mhu320ae/CMakeLists.txt`
- `hsoc-stack/tools/qbox-platform/tests/components/mhu320ae/mhu320ae-tests.cc`

주요 클래스:

- `mhu320ae`: Lua/CCI-visible SystemC module.
- `mhu320ae::mhu320ae_frame_model`: PBX/MBX register storage, DBCH state,
  mask, interrupt status, control, combined interrupt status 계산을 담당하는
  reusable frame model.

## Socket과 signal

| Port | Direction | Purpose |
| --- | --- | --- |
| `target_socket` | target | MHU register access |
| `initiator_socket` | initiator | SCMI/RPMsg shared memory access |
| `irq` | signal out | combined interrupt output |
| `fault_irq`, `error_irq` | optional signal out | SRAS/RRAS FHI/ERI; Apollo 기본 배선 없음 |
| `power_on_reset` | signal out | SCMI Power Domain AP reset release |
| `power_domain_reset[N]` | signal out | AP core power-domain reset |
| `system_reset` | signal out | SCMI System Power reset pulse |

## Register model

The model exposes a `0x30000` register aperture by default. The current
implemented register surface is the subset used by Linux, Zephyr, TF-M, and
SCP-firmware in Apollo/RD-Aspen:

| Register | Offset | Behavior |
| --- | --- | --- |
| `CTRL_BLK_ID` | `0x000` | PBX/MBX identity |
| `CTRL_FEAT_SPT0` | `0x010` | 설정된 FCE/RASE만 광고; 나머지는 CCI feature word |
| `CTRL_FEAT_SPT1` | `0x014` | CCI-configurable feature word |
| `CTRL_DBCH_CFG0` | `0x020` | channel count minus one |
| `CTRL_DBCH_INT_ST0..3` | `0x400` | combined interrupt summary |
| `CTRL_IIDR` | `0xfc8` | CCI-configurable implementer ID |
| `CTRL_AIDR` | `0xfcc` | CCI-configurable architecture ID |
| `DBCWn_ST` | `0x1000 + n*0x20` | channel doorbell status |
| `DBCWn_SET` | `+0x0c` | PBX doorbell set |
| `DBCWn_CLR` | `+0x08` | MBX doorbell clear |
| `DBCWn_INT_*` | `+0x10..0x18` | PBX interrupt or MBX mask behavior |
| `PBX/MBX_FCH_CFG0` | `0x040` | 채널 수, 그룹 크기, payload 폭 discovery |
| `MBX_FCH_CTRL` | `0x140` | fast-channel combined IRQ enable |
| `MBX_FCG_INT_EN/ST` | `0x144/0x470` | 그룹별 combined interrupt enable 및 status |
| `MBX_FCH_GRP_INT_STn` | `0x480 + n*4` | 그룹 내 미수신 채널 bitmap |
| `PBX/MBX_FCWn_PAY` | `0x3000 + n*(width/8)` | 32/64-bit latest-value payload; MBX read가 pending clear |
| `MBX_DB_ERRINS`, `MBX_FST_ERRINS` | `0xf010`, `0xf018` | 비파괴적 RAM 오류 시뮬레이션 |
| SRAS/RRAS | `0x10000` | `ras_enable=true`일 때 local error record, W1C, CE count |

FCE synthesis parameter는 `fast_channel_count`, `fast_channels_per_group`,
`fast_channel_word_bits`이다. 일반 모델은 FCE를 끈 상태로 시작하며 Apollo의
실제 PBX/MBX pair에는 양쪽 모두 64채널, 그룹당 32채널, 32-bit를 지정한다.
이 수치는 QVP 기능 구성으로서 실리콘 synthesis 값에 대한 주장이 아니다.
`ras_enable` 모델 기본값은 false다. Apollo AP/SI0 non-secure의 두 방향,
네 endpoint에는 true를 지정하여 RAS polling 진단을 제공한다. Local RAS IRQ는
연결하지 않으며 기본 ERRCTLR은 interrupt-disabled다.
Security-control extension을 광고하지 않으므로
RAS frame은 PBX/MBX 다음 64 KB frame에 위치한다.

## Pair routing

각 MHU instance는 `pair` CCI parameter로 peer를 찾는다. PBX write는 같은
pair의 MBX에 doorbell status를 반영한다. 이름 있는 pair가 매칭되지 않으면
다른 global MBX/PBX로 fallback하지 않는다. 이 동작은 AP/RSE secure service,
AP/SI CL1 HIPC, CL1 PFDI monitor가 서로의 mailbox state를 오염시키지 않기
위한 필수 조건이다.

## Protocol hooks

Register model 위에 다음 protocol hook을 얹는다.

- `protocol = "scmi"`: SCMI shared-memory request를 읽고 response를 작성한다.
- `scmi_transport = "pfdi-monitor"`: PFDI monitor protocol `0x90`을 허용한다.
- `protocol = "doorbell"`: AP/SI CL1 HIPC resource-table seed와 RPMsg
  name-service injection에 사용한다.
- `protocol = "doorbell-bridge"`: AP/RSE secure service와 live CL1 HIPC
  cross-domain doorbell forwarding에 사용한다.

이 hook들은 장기적으로 별도 transport adapter로 분리할 수 있지만, 현재
Apollo full-system 부팅 검증에서는 MHU register model과 함께 원자적으로
검증되어야 한다.

## Platform wiring

현재 소유 경로는 `hsoc-stack/tools/qbox-platform/platforms/apollo/`다.
`soc/hw-block/system_mgmt/{ap_rse_mailbox,ap_si_mailbox,rse_si_mailbox}.lua`,
`si_cl0/mailbox.lua`, `si_cl1/mailbox.lua`, `rse/system.lua`에서 실제 peer를
정의한다. Full-system에는 15개 pair, 30개 endpoint가 있으며 양쪽의 FCE
채널 수와 payload 폭이 같아야 한다. 불일치는 elaboration 오류다.

SCP의 `apollo-qvp/si0_ramfw`는 MHU3 FCE를 켜고 AP non-secure pair의
채널 32를 IRQ echo 진단에 예약한다. `SCMI_PERF_FAST_CHANNELS`는 계속 꺼져
있으며 Linux SCMI/mailbox의 기존 doorbell 통신을 유지한다.
AP MBX의 FCE IRQ는 현재 Linux driver가 처리하지 않으므로 진단 중에는
`FCH_CTRL.COMB_EN`을 마스킹하고 응답을 polling한다. SI0의 수신은 실제
MHU combined IRQ와 기존 MHU3 ISR callback을 사용한다.

검증 명령과 TRM별 구현 범위는
[AE 구현·검증 기록](qbox-ae-gic720-mhu320-validation-ko.md)을 따른다.

`mhuv3_rproc_stub`는 legacy primary-compute remoteproc compatibility
component로 남아 있지만, 현재 Apollo full-system 검증 경로의 gate나
platform wiring contract는 아니다.

## Fidelity gap

Boot/doorbell과 FCE, local RAS, FMU의 소프트웨어 관찰 가능한 동작을 모델링한다.
Full TRM parity gap은 다음으로 남긴다.

- 모든 optional ID/feature register의 TRM reset value 대조.
- Local RAS 및 별도 `zena_device_fmu`의 MHU profile은 기능 모델이다.
  ERRINS는 물리 오류 검출이 아니며, FMU protection event로 자동 변환하지 않는다.
- ECC encoder, 실제 lockstep 비교, AXI parity/CRC 및 clock-cycle 검증.
- Local RAS `fault_irq/error_irq`의 Apollo CPU interrupt 배선 및 guest handler.
- clock/reset/security attribute와 PPC/NSP/SP access-control side effect.
- multi-chip CMU MHU 전체 topology 자동 생성.
- `mhuv3_rproc_stub`와의 기능 통합.
