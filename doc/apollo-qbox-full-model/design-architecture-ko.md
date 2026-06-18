# Apollo QBox Full Model Promotion Design / Architecture

작성일: 2026-06-14

## 설계 목표

Apollo QBox의 full-system target은 다음 네 실행 도메인을 유지한다.

```text
RSE TF-M
  -> SI CL0 SCP-firmware
  -> SI CL1 Zephyr
  -> AP TF-A / OP-TEE / U-Boot / Linux
```

이 설계는 boot path를 바꾸지 않고, `gs_memory`로 열려 있던 register window를
관찰 가능한 SystemC/TLM model로 교체한다. 기존 QEMU CPU/GIC/virtio backend는
유지하고, safety/security/system-management control surface만 좁게
승격한다.

## Component Architecture

```text
                    +-----------------------+
                    | scripts/run/run_qbox_* |
                    | result.json/coverage  |
                    +-----------+-----------+
                                |
                      Lua platform wiring
                                |
    +---------------------------+---------------------------+
    |                           |                           |
+---v----+              +-------v-------+           +-------v-------+
| RSE    |              | Safety CL0    |           | Primary AP    |
| TF-M   |              | SCP firmware  |           | Linux/FW      |
+---+----+              +-------+-------+           +-------+-------+
    |                           |                           |
    | rse_protection_ctrl       | zena_fmu/zena_ssu         |
    | rse_atu                  | host_rgm/host_pik         |
    | rse_kmu/lcm/sam          | future host_apu_filter    |
    |                           | gicx00_multiview          |
    +---------------------------+---------------------------+
                                |
                         host_router / addrtr
                                |
                  +-------------v-------------+
                  | SMD / RoS / I/O surfaces |
                  +---------------------------+
```

## 신규/확장 모델

| Module | 위치 | 책임 |
| --- | --- | --- |
| `zena_fmu` | `tools/qbox/systemc-components/zena_fmu/` | FMU error records, group status, fault injection, critical/non-critical IRQ |
| `zena_ssu` | `tools/qbox/systemc-components/zena_ssu/` | FMU input aggregation, SSU state, external safety status |
| `rse_protection_ctrl` | `tools/qbox/systemc-components/rse_protection_ctrl/` | SACFG/NSACFG/MPC/SIC secure access behavior |
| `rse_atu` | `tools/qbox/systemc-components/rse_atu/` | First-wave APU/ATU translation, permission, mismatch/error evidence |
| `host_apu_filter` | `tools/qbox/systemc-components/host_apu_filter/` | Follow-up NI-710AE APU-style requester/security filtering |
| `host_rgm` | `tools/qbox/systemc-components/host_rgm/` | Reset Generation Manager control/status/syndrome |
| `host_pik` | `tools/qbox/systemc-components/host_pik/` | SYSTOP/DBGTOP power integration status and reset/power events |
| `host_io_regbank` | `tools/qbox/systemc-components/host_io_regbank/` | I/O block error/PMU interrupt control subset |
| `zena_error_record` | common helper under `tools/qbox/systemc-components/common/` | W1C status, PID/CID, error injection, group status helper |

## Lua Integration

| Lua file | 변경 방향 |
| --- | --- |
| `tools/qbox-platform/platforms/apollo/hw-block/si_cl0.lua` | `si_cl0_ssu`, `si_cl0_fmu`를 `zena_ssu`, `zena_fmu`로 교체 |
| `tools/qbox-platform/platforms/apollo/hw-block/rse.lua` | RSE SACFG/MPC/SIC, AP secure watchdog, host SYSTOP/COUNTER windows를 model로 교체 |
| `tools/qbox-platform/platforms/apollo/hw-block/system_mgmt.lua` | ownership ledger에 full/service/register/memory 분류 추가 |
| `tools/qbox-platform/platforms/apollo/hw-block/ros.lua` | RoS missing peripheral을 `absent`, `accepted-placeholder`, `full-model`로 명시 |
| `tools/qbox-platform/platforms/apollo/apollo-qvp.lua` | model backend/fidelity CCI parameters를 runner result로 노출 |

## Fault Flow

FMU/SSU 구현 후 기본 fault flow는 다음과 같다.

```text
software injection or modeled IP fault
  -> zena_fmu ERR<n>STATUS.V set
  -> ERRGSR_L/H group status update
  -> critical/non-critical IRQ asserted
  -> zena_ssu CR/NCR input observed
  -> SSU SYS_STATUS moves to ERRN or ERRC
  -> SI CL0 GIC receives IRQ
  -> SCP-firmware handler/log/probe observes fault
  -> runner records marker and register snapshot
```

실제 IP fault source가 아직 없는 경우에도 software injection register를 통해
동일한 downstream path를 검증한다. 이 방식은 fault source model과 fault
aggregation model을 분리해 review와 regression 범위를 줄인다.

## Access-Control Flow

First-wave APU/ATU access-control path는 다음 정책을 따른다.

```text
initiator domain + security attribute + target address
  -> rse_atu region/security-domain lookup
  -> allowed: translate and forward to target socket
  -> denied: return TLM error and latch mismatch status
  -> optional follow-up: host_apu_filter raises configured fault interrupt
```

초기 정책 source는 Lua의 `rse_atu` backend와 CCI parameter로 둔다.
RSE/SCP firmware가 NI-710AE APU programming을 수행하는 sequence가
확인되면 후속 `host_apu_filter`의 register-written policy로 전환한다.

## Reset/Power Flow

`host_rgm`과 `host_pik`는 기존 `reset_gpio`, `reset_fanout`, `host_ppu`,
`mhu320ae` reset hook을 대체하지 않는다. 대신 firmware-visible register
surface와 reset/power event metadata를 제공한다.

```text
RSE/SCP write RGM or PIK register
  -> host_rgm/host_pik updates status/syndrome
  -> optional reset_fanout pulse
  -> host_ppu state remains source of power polling compatibility
  -> runner captures reset/power event counters
```

## 유지할 Memory Model

다음 항목은 full model 승격 대상이 아니다.

- AP DRAM bank
- RSE ROM, ITCM, DTCM, VM0, VM1
- SI CL0/CL1 SRAM
- AP/RSE/SI mailbox shared SRAM
- SCMI shared memory
- HIPC resource table, vring, RPMsg buffer
- SMCF SRAM backing store
- reserved GICR frame backing window

필요한 경우 이 memory 뒤에 access filter를 배치한다. 저장공간 자체를 register
model로 바꾸지는 않는다.

## Review Boundaries

- P0/P1 모델은 SystemC component tests가 없으면 merge하지 않는다.
- Lua wiring change는 map validator와 full-system boot evidence 없이 완료로
  보지 않는다.
- FVP와 다른 intentional behavior는 `doc/apollo-qbox-hardware-ko.md`와
  coverage output에 같이 기록한다.
- Performance fast path는 fidelity test가 pass한 뒤 opt-in 또는 documented
  default로만 적용한다.
