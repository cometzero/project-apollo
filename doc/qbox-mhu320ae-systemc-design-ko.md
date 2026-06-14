# QBox MHU-320AE SystemC Component Design

작성일: 2026-06-09

## 설계 요약

`mhu320ae`는 Arm MHU-320AE 제품 IP를 QBox에 노출하는 SystemC component다.
소프트웨어가 보는 programming model은 `arm,mhuv3` PBX/MBX doorbell frame이다.
기존 `mhuv3_stub`의 검증된 PBX/MBX register frame과 Apollo boot service hook을
보존하되, default platform wiring은 `mhu320ae`로 전환한다.

## Component 구조

파일 배치:

- `tools/qbox/systemc-components/mhu320ae/CMakeLists.txt`
- `tools/qbox/systemc-components/mhu320ae/include/mhu320ae.h`
- `tools/qbox/systemc-components/mhu320ae/src/mhu320ae.cc`
- `tools/qbox/tests/components/mhu320ae/CMakeLists.txt`
- `tools/qbox/tests/components/mhu320ae/mhu320ae-tests.cc`

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
| `CTRL_FEAT_SPT0` | `0x010` | CCI-configurable feature word |
| `CTRL_FEAT_SPT1` | `0x014` | CCI-configurable feature word |
| `CTRL_DBCH_CFG0` | `0x020` | channel count minus one |
| `CTRL_DBCH_INT_ST0..3` | `0x400` | combined interrupt summary |
| `CTRL_IIDR` | `0xfc8` | CCI-configurable implementer ID |
| `CTRL_AIDR` | `0xfcc` | CCI-configurable architecture ID |
| `DBCWn_ST` | `0x1000 + n*0x20` | channel doorbell status |
| `DBCWn_SET` | `+0x0c` | PBX doorbell set |
| `DBCWn_CLR` | `+0x08` | MBX doorbell clear |
| `DBCWn_INT_*` | `+0x10..0x18` | PBX interrupt or MBX mask behavior |

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
- `protocol = "doorbell"`: direct boot compatibility, AP/SI CL1 HIPC
  resource-table seed, RPMsg name-service injection에 사용한다.
- `protocol = "doorbell-bridge"`: AP/RSE secure service와 live CL1 HIPC
  cross-domain doorbell forwarding에 사용한다.

이 hook들은 장기적으로 별도 transport adapter로 분리할 수 있지만, 현재
Apollo full-system 부팅 검증에서는 MHU register model과 함께 원자적으로
검증되어야 한다.

## Platform wiring

Default 전환 대상:

- `tools/qbox/platforms/fvp-rd-aspen/conf.lua`: AP SCMI TX/RX.
- `tools/qbox/platforms/fvp-rd-aspen-rse/conf.lua`: RSE local MHU0/MHU2,
  AP/RSE secure mailbox, RSE/SI SCMI, AP/SI SCMI/CL1/PFDI paths.
- `tools/qbox/platforms/apollo/apollo-qvp.lua`: live CL1 HIPC/PFDI override.
- `tools/qbox/platforms/apollo/apollo-si-cl1.lua`: isolated CL1 HIPC/PFDI.

`mhuv3_rproc_stub`는 standalone primary-compute remoteproc path의 separate
compatibility component로 남긴다.

## Fidelity gap

이번 단계는 boot-critical MHU-320AE/MHUv3 behavior를 SystemC component로
전환하는 단계다. Full TRM parity gap은 다음으로 남긴다.

- 모든 optional ID/feature register의 TRM reset value 대조.
- MHU safety/RAS/fault-management register block.
- clock/reset/security attribute와 PPC/NSP/SP access-control side effect.
- multi-chip CMU MHU 전체 topology 자동 생성.
- `mhuv3_rproc_stub`와의 기능 통합.
