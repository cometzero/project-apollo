# Apollo QBox Full Model Promotion Spec

작성일: 2026-06-14

## 모델 승격 원칙

`gs_memory` window와 FVP-visible missing surface는 다음 네 가지 중 하나로
분류한다.

| 분류 | 의미 | 처리 |
| --- | --- | --- |
| `memory-backing` | RAM, SRAM, TCM, vring, shared memory, firmware image area | `gs_memory` 유지 |
| `accepted-placeholder` | 현재 software가 접근하지만 side effect가 아직 acceptance에 필요하지 않은 register window | coverage ledger에 debt 기록 |
| `full-model-required` | status, fault, reset, interrupt, access-control side effect가 필요한 IP | SystemC/QEMU model로 승격 |
| `unsupported-gap` | FVP-visible IP이지만 현재 implementation wave의 목표가 아닌 missing model 또는 stub | 별도 owner decision 또는 후속 epic 없이는 final parity gate에서 pass 불가 |

## 기능 요구사항

### FR-001 FMU model

`zena_fmu` model은 Safety Island FMU register summary를 기준으로 다음
동작을 제공해야 한다.

- `ERR<n>FR`, `ERR<n>CTLR`, `ERR<n>STATUS`, `ERRIMPDEF<n>` register decode
- RO, RW, W1C, RAZ/WI field behavior
- `SYS_KEY` protected write sequence
- `ERRGSR_L/H` group status generation
- software error injection path
- critical/non-critical interrupt output
- configurable record count and reset values
- AP/SMD/GIC/MHU/NI-710AE FMU instance profile

### FR-002 SSU model

`zena_ssu` model은 Safety Status Unit register summary를 기준으로 다음
동작을 제공해야 한다.

- `ERR_FR`, `ERR_CTRL`, `ERR_STATUS`, `ERR_IMPDEF`, `SYS_KEY`,
  `SYS_STATUS`, `SYS_CTRL`, `STATUS_DETAIL` decode
- FMU critical/non-critical input aggregation
- `TEST`, `SAFE`, `ERRN`, `ERRC` state reporting
- external safety status output을 log/result metadata로 노출
- CL0 firmware polling과 write sequence compatibility

### FR-003 RSE protection model

RSE protection model은 다음 register window를 `gs_memory`에서 대체한다.

- `rse_nsacfg_regs`
- `rse_sacfg_regs`
- `rse_mpc_vm0_regs`
- `rse_mpc_vm1_regs`
- `rse_sic_regs`
- `rse_mpc_sic_regs`

요구 동작:

- secure/non-secure alias별 접근 권한 분리
- SIE-300 MPC style `BLK_MAX`, `BLK_CFG`, PID/CID reset values
- region lock/write mask behavior
- illegal access에 대한 RAZ/WI 또는 error response 선택
- TF-M boot가 사용하는 register sequence 유지

### FR-004 NI-710AE APU와 ATU error model

SMD 52-bit address map은 기본적으로 RSE 외 접근이 차단된다. QBox는 다음을
모델링해야 한다.

- APU region enable/disable state
- requester domain(AP/RSE/SI/SMD)과 security attribute 구분
- AP-to-SMD, SMDExp-to-SMD, CLUSMGT-to-SMD ATU access permission
- blocked access의 DECERR/SLVERR 또는 fault record generation
- ATU error record read/clear behavior

### FR-005 System management control model

다음 System Management control surface는 memory window가 아니라 register
model이어야 한다.

- Reset Generation Manager
- SYSTOP/DBGTOP Power Integration
- REFCLK counter control/read
- system generic timer synchronization control
- SMD UART/GPIO/System ID register subset

초기 구현은 firmware-visible reset values, polling status, W1C error record,
reset pulse output에 집중한다.

### FR-006 AP secure watchdog

`ap_secure_wdog`는 `gs_memory`가 아니라 secure SBSA watchdog-compatible
control/refresh frame으로 동작해야 한다.

- secure control frame과 refresh frame 분리
- interrupt/reset output wiring
- panic/error path refresh가 원래 failure를 숨기지 않도록 log metadata 기록
- non-secure watchdog과 state isolation

### FR-007 GIC/RAS/AP topology

현재 QBox는 AP 4-core cfg2 path를 기준으로 한다. Full FVP parity 단계에서는
다음 gap을 검증 가능한 상태로 만들어야 한다.

- 16 GIC redistributor frame visibility
- AP 16-core topology option
- SI GIC view0/view1/view2 isolation
- RAS FFH notification, CPER buffer, SPI routing
- PFDI per-core channel과 AP topology의 일관성

### FR-008 RoS/I/O/debug extension

다음 IP는 정상 full-system boot보다 SystemReady, board peripheral, debug
parity 목적에서 활성화한다.

- RoS System Registers
- Virtio P9
- VSI0/VSI1
- RoS UART0/UART1
- RoS DMA-350
- TRNG
- Trusted nvCounter
- SMSC91C111 Ethernet
- RoS/SMD Strata Flash
- IO_REGBANK, PCIe PHY/controller config
- CoreSight ROM table, CTI, ETF, ATF, STM, CATU

## 비기능 요구사항

| ID | 요구사항 |
| --- | --- |
| NFR-001 | SystemC/TLM response status를 사용해 silent success를 피한다. |
| NFR-002 | 기존 Apollo full-system boot pass를 regression하지 않는다. |
| NFR-003 | model 선택과 fidelity level은 runner `result.json`에 남긴다. |
| NFR-004 | QEMU-native fast path는 secure/safety semantics를 우회하지 않는다. |
| NFR-005 | Lua object name, socket direction, CCI parameter naming은 기존 QBox 관례를 따른다. |
| NFR-006 | negative tests는 pass/fail뿐 아니라 observed register/IRQ/log evidence를 저장한다. |

## 수락 기준

| ID | 기준 |
| --- | --- |
| AC-SPEC-001 | `si_cl0_fmu`와 `si_cl0_ssu`가 `gs_memory`가 아닌 full model로 배치된다. |
| AC-SPEC-002 | RSE protection register windows가 secure/non-secure access behavior를 가진다. |
| AC-SPEC-003 | APU/ATU blocked access가 QBox에서 관찰 가능한 error/fault로 남는다. |
| AC-SPEC-004 | `ap_secure_wdog`가 watchdog model로 교체되고 AP secure firmware boot가 유지된다. |
| AC-SPEC-005 | coverage audit이 remaining placeholder를 분류하고 unclassified gap을 fail 처리한다. |
| AC-SPEC-006 | full-system live CL0/CL1 boot와 post-login probe가 pass한다. |
