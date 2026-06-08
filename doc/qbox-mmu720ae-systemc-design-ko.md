# QBox MMU-720AE SystemC Component Design

작성일: 2026-06-08

상태: 구현 진행 중, register/boot path landed, translation parity 미완료

## 설계 요약

`mmu720ae`는 Apollo/RD-Aspen AP I/O Block의 MMU-720AE를 QBox SystemC/TLM
component로 모델링한다. 현재 runtime path는 SystemC `mmu720ae`를 기본 SMMU
backend로 사용하며, 기존 QEMU `arm_smmuv3`는 Linux-visible SMMUv3 behavior
비교와 fallback 기준으로 남긴다. 최종 parity 상태에서는 SystemC `mmu720ae`가
AP I/O requester의 DMA translation까지 처리해야 한다.

```text
Linux arm-smmu-v3 driver
  -> AP router
  -> mmu720ae.reg_socket
      -> TCU register bank
      -> command/event/PRI queues
      -> IRQ/MSI outputs

I/O requester DMA
  -> mmu720ae.tbu_<name>_target_socket
      -> TBU attribute capture
      -> TCU translation service                (planned)
      -> TLB/uTLB/ATC lookup                    (planned)
      -> page-table walk via ptw_socket         (planned)
      -> translated downstream_socket           (planned)
```

Current implementation note: TBU requester traffic bypasses only while
`SMMUEN` is clear. Once software enables the SMMU, TBU traffic is blocked with
a SMMU-visible translation fault event when EVTQ is configured, or a global
event-queue abort error when EVTQ is unavailable, until the STE/CD table
walker is implemented. This prevents silent translation bypass in the enabled
state.

## 파일 구조

| 파일 | 역할 |
| --- | --- |
| `tools/qbox/systemc-components/mmu720ae/CMakeLists.txt` | `gs_create_dymod(mmu720ae)` target |
| `tools/qbox/systemc-components/mmu720ae/include/mmu720ae.h` | top-level `sc_module`, sockets, CCI params |
| `tools/qbox/systemc-components/mmu720ae/include/mmu720ae_core.h` | QEMU-free register/queue/translation state owner |
| `tools/qbox/systemc-components/mmu720ae/include/mmu720ae_regs.h` | TRM/spec-derived register offsets, fields, reset policy |
| `tools/qbox/systemc-components/mmu720ae/include/mmu720ae_tlm_extensions.h` | requester SID/SSID/security attribute TLM extension |
| `tools/qbox/systemc-components/mmu720ae/include/mmu720ae_queue.h` | planned CMDQ/EVTQ/PRIQ ring helpers |
| `tools/qbox/systemc-components/mmu720ae/include/mmu720ae_tbu.h` | planned TBU ingress, uTLB, SID/SSID/default attribute mapping |
| `tools/qbox/systemc-components/mmu720ae/include/mmu720ae_table_walker.h` | planned STE/CD/stage1/stage2 page-table walk |
| `tools/qbox/systemc-components/mmu720ae/include/mmu720ae_tlb.h` | planned TLB/uTLB/ATC cache and invalidation |
| `tools/qbox/systemc-components/mmu720ae/include/mmu720ae_trace.h` | planned trace/stat JSON structures |
| `tools/qbox/systemc-components/mmu720ae/src/mmu720ae.cc` | module registration and top-level transport methods |
| `tools/qbox/systemc-components/mmu720ae/src/mmu720ae_core.cc` | register side effects and queue orchestration |
| `tools/qbox/systemc-components/mmu720ae/src/mmu720ae_queue.cc` | planned queue memory access and record packing |
| `tools/qbox/systemc-components/mmu720ae/src/mmu720ae_tbu.cc` | planned TBU transaction path |
| `tools/qbox/systemc-components/mmu720ae/src/mmu720ae_table_walker.cc` | planned translation table walker |
| `tools/qbox/tests/components/mmu720ae/` | unit, integration, negative, DMI tests |

## Public module surface

Lua module type:

```lua
moduletype = "mmu720ae"
```

Required sockets:

| Socket | Direction | Purpose |
| --- | --- | --- |
| `reg_socket` | target | TCU SMMUv3 register frame at `0x1c0000000` |
| `tbu_ace1_socket` | target | ACE1 requester ingress |
| `tbu_ace2_socket` | target | ACE2 requester ingress |
| `tbu_lti00_socket` | target | LTI00 requester ingress |
| `tbu_lti01_socket` | target | LTI01 requester ingress |
| `tbu_lti02_socket` | target | LTI02 requester ingress |
| `downstream_socket` | initiator | translated transaction to AP memory/interconnect |
| `ptw_socket` | initiator | page-table walk reads and queue memory access |
| `irq_combined` | initiator signal | AP GIC SPI 65 |
| `msi_socket` | initiator | optional MSI write path to ITS-visible memory |
| `reset` | target signal | reset and DMI invalidate |

Compatibility socket:

| Socket | Direction | Purpose |
| --- | --- | --- |
| `mem` | target alias | Existing `arm_smmuv3.mem` Lua binding compatibility; internally binds to `reg_socket` |

The compatibility alias lets existing map validation and platform wiring move
incrementally. New code should bind `reg_socket` explicitly.

## CCI parameters

| Parameter | Default | Purpose |
| --- | --- | --- |
| `profile` | `zena-css-cfg2` | Select Apollo cfg2 ID/reset/TBU profile |
| `stage` | `1` | `1`, `2`, or `nested`; mirrors existing QEMU wrapper surface |
| `sid_bits` | profile-derived | SMMUv3 SID width exposed through `IDR1` |
| `ssid_bits` | profile-derived | SMMUv3 SSID width exposed through `IDR1` |
| `queue_log2_entries_cmdq` | profile-derived | Command queue size exposed through `IDR1` |
| `queue_log2_entries_evtq` | profile-derived | Event queue size exposed through `IDR1` |
| `queue_log2_entries_priq` | profile-derived | PRI queue size when PRI is exposed |
| `features` | profile-derived | Explicit feature mask for S1/S2/MSI/ATS/PRI/STALL/RANGE_INV |
| `trace_file` | empty | JSONL trace output |
| `stats_file` | empty | Summary JSON output |
| `strict_unimplemented_feature` | true | Abort elaboration if profile exposes an unsupported feature |
| `default_sid_<tbu>` | profile-derived | SID fallback for requester without SID extension |
| `enable_dmi` | true | Allow translated DMI grants |

## Core decomposition

### `mmu720ae_core`

`mmu720ae_core` owns register state, queue state, feature bits, TLB state,
fault state, sideband state, and statistics. It has no QEMU dependency.
SystemC-specific objects stay in the top module or adapters.

Main API shape:

```cpp
namespace qbox::mmu720ae {

struct bus_access {
    uint64_t address;
    uint32_t size;
    bool write;
    bool debug;
    uint8_t data[16];
};

struct request_attr {
    uint32_t sid;
    uint32_t ssid;
    bool ssid_valid;
    bool secure;
    bool privileged;
    bool instruction;
    bool ats_request;
};

struct translation_result {
    bool ok;
    uint64_t output_address;
    uint64_t page_mask;
    bool read_allowed;
    bool write_allowed;
    uint32_t event_code;
};

class memory_if {
public:
    virtual ~memory_if() = default;
    virtual bool read(uint64_t address, uint8_t* data, uint32_t size) = 0;
    virtual bool write(uint64_t address, const uint8_t* data, uint32_t size) = 0;
};

class core {
public:
    void reset();
    access_status reg_read(bus_access& access);
    access_status reg_write(const bus_access& access);
    translation_result translate(uint64_t iova, uint32_t size,
                                 const request_attr& attr, access_type type);
    void process_command_queue(memory_if& memory);
    void write_stats_json(std::ostream& out) const;
};

} // namespace qbox::mmu720ae
```

### Register bank

Register decode is table-driven. Each register entry records offset, width,
reset value, access policy, write mask, read side effect, write side effect, and
trace name. The table is generated manually from the non-confidential TRM/spec
into `mmu720ae_regs.h`; the review gate checks every implemented register
against the traceability matrix.

### Queue engine

Queue memory is accessed through `ptw_socket` because queue descriptors live in
guest memory. `CMDQ_PROD` writes schedule a SystemC event. The queue process
runs in simulation time and performs:

1. Fetch command record.
2. Decode operation.
3. Mutate state or invalidate caches.
4. Update consumer index.
5. Complete `CMD_SYNC` and raise event/interrupt if required.

Event and PRI queues use the same ring helper with separate record formats.

### Table walker

The table walker reads STE and CD entries through `ptw_socket`, then walks
AArch64 stage 1 and stage 2 page tables according to the SMMUv3/SMMU
architecture profile. Walker failures return event codes, not generic TLM
address errors. TLM address errors are reserved for malformed register access
or downstream bus decode failures.

### TBU ingress

Each TBU has its own target socket and uTLB. TBU captures requester attributes,
calls `core.translate()`, then forwards a cloned payload to `downstream_socket`
with translated address. The original IOVA, SID, SSID, and translation result
are attached to a trace record.

Current implementation detail: `request_attrs_extension` carries SID, optional
SSID, security, privilege, instruction, and ATS intent. The enabled-SMMU guard
currently consumes only SID. If the requester extension has `sid_valid=true`,
that SID is used in the generated translation fault event. If the extension is
missing, the TBU-specific CCI default SID is used and the fallback counter is
incremented. This keeps the missing-SID compatibility path observable while
leaving SSID/security/permission semantics for the table-walker phase.

Atomic/exclusive transactions are passed only if the downstream target and
translation attributes allow them. Unsupported atomics generate an event when
the TRM/spec requires SMMU-visible failure; otherwise they return TLM command
error.

## DMI policy

DMI is granted only after a successful translation. The DMI object records:

- input IOVA range
- output physical range
- SID/SSID/security key
- permission mask
- TLB generation

Any invalidation that covers the key increments the generation and calls
`invalidate_direct_mem_ptr()` upstream for the original IOVA range. A DMI grant
is never shared across different SID/SSID/security attributes.

## Interrupt model

The default Apollo path uses combined IRQ:

```text
mmu720ae.irq_combined -> ap_gic.spi_in_65
```

The combined IRQ is asserted when any enabled event, PRI, global error, PMU, or
RAS interrupt source is pending. The signal is deasserted only when all
corresponding status bits are cleared or masked.

Current implementation covers GERROR pending and EVTQ pending sources on the
combined IRQ. PRI, PMU, RAS, and MSI delivery remain planned work.

MSI mode is modeled as a separate path. If MSI is exposed in ID registers and
enabled by the driver, queue/event signaling writes to the ITS-visible MSI
target through `msi_socket`. If MSI is not implemented in the current phase,
the profile must clear the MSI capability bit.

## Zena CSS SMD_CSR and IO_REGBANK

The local Zena CSS programmer model defines:

- `IO_MMU_CFG` reset `0x00000AA8`
- `IO_TBU_NS_SID` reset `0x1C8EAC78`
- `IO_TBU_S_SID` reset `0x1C8EAC78`
- `IO_TCU_SID` reset `0x00000000`
- `IO_TCU_SID_CHK` reset `0xFFFFFFFF`

These registers configure TBU uTLB policy and SID high bits. The design keeps
their state in `mmu720ae_core` and exposes getter/setter methods for an
IO_REGBANK/SMD_CSR SystemC component. This prevents register mirror drift.

## Platform wiring

Direct RD-Aspen path:

```lua
smmu_0 = {
    moduletype = smmu_backend == "systemc-mmu720ae" and "mmu720ae" or "arm_smmuv3";
    mem = {
        address = 0x1c0000000;
        size = 0x8000000;
        bind = "&router.initiator_socket";
    };
    irq_combined = { bind = "&gic_0.spi_in_65" };
    downstream_socket = { bind = "&router.target_socket" };
    ptw_socket = { bind = "&router.target_socket" };
    stage = "1";
    profile = "zena-css-cfg2";
}
```

Full Apollo path uses the same module under `ap_smmu_0`. The integration keeps
QEMU `arm_smmuv3` as a comparison fallback and selects the SystemC backend by
default:

```bash
QBOX_RDASPEN_SMMU_BACKEND=systemc-mmu720ae
```

The boot-regression validated default is now `systemc-mmu720ae`; this is not a
FVP-parity claim until register, transaction, and system comparison gates pass.

## FVP parity strategy

Parity is checked at three levels.

| Level | Evidence |
| --- | --- |
| Register | Linux/FVP and QBox register trace for probe, queue enable, command sync, fault injection |
| Transaction | Synthetic DMA requester compares bypass, translated, abort, permission fault, stale DMI |
| System | Direct Linux and full Apollo boot compare dmesg, `/proc/interrupts`, `/sys/kernel/iommu_groups`, module load, RSE/SI/AP boot markers |

FVP parity claim is only allowed when all three levels pass.

## Design risks

| Risk | Mitigation |
| --- | --- |
| QEMU-backed requester bypasses SystemC TBU path | Add explicit requester adapters or keep that requester on QEMU SMMU until a SystemC DMA path exists; do not claim full parity for that requester |
| ID register exposes unsupported feature | `strict_unimplemented_feature=true` aborts elaboration |
| DMI bypasses translation after invalidation | Generation-tagged DMI and unit tests for stale-DMI-negative cases |
| Queue processing order differs from Linux expectations | SystemC event-driven queue process and driver trace comparison |
| FVP feature bits are not known before implementation | First task builds a TRM/FVP traceability matrix and locks profile values before coding |
