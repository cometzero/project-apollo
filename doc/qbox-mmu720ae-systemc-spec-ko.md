# QBox MMU-720AE SystemC Component Spec

작성일: 2026-06-08

상태: 구현 진행 중, boot-validated default backend, FVP parity 미완료

관련 문서:

- `doc/qbox-mmu720ae-systemc-design-ko.md`
- `doc/qbox-mmu720ae-systemc-plan-ko.md`
- `doc/qbox-mmu720ae-systemc-tasks-ko.md`
- `doc/qbox-mmu720ae-traceability-matrix.md`
- `doc/apollo-fvp-hardware-analysis-ko.md`
- `doc/apollo-qbox-hardware-ko.md`
- `doc/arm_zena_css_dev_guide/05-functional-blocks-in-zena-css.md`
- `doc/arm_zena_css_dev_guide/09-programmers-model-for-zena-css.md`
- `doc/arm_zena_css_dev_guide/92-useful-resources.md`

## 목표

Arm Zena CSS FVP의 MMU-720AE SMMUv3 동작을 QEMU `arm-smmuv3` backend 없이
QBox SystemC/TLM component로 구현한다. 최종 모델은 Linux driver probe만
통과하는 register stub이 아니라 FVP에서 보이는 MMU-720AE 수준의 TCU/TBU,
translation, queue, fault, interrupt, RAS/PMU 동작을 제공해야 한다.

## 현재 구현 상태

2026-06-08 현재 `mmu720ae` SystemC component는 Apollo/RD-Aspen QBox
platform의 기본 SMMU backend로 연결되어 있고, QEMU `arm_smmuv3` backend는
명시적 fallback으로 남아 있다. 검증된 범위는 SMMUv3 Linux probe에 필요한
register/queue-compatible surface, SMMU enabled 상태에서 TBU silent-bypass를
막는 guard, Apollo full-system boot marker regression이다.

FVP 수준 parity는 아직 완료되지 않았다. STE/CD table walker, stage 1/2/nested
translation, full fault class coverage, translated DMI, RAS/PMU, SMD_CSR
sideband, FVP/QBox comparison report는 남은 필수 작업이다. 현재 구현은 TBU
translation fault EVTQ record, SID extension/default SID fallback, 관련
diagnostic counter까지만 부분 완료했다. 현재 완료/부분/미완료 상태는
`doc/qbox-mmu720ae-traceability-matrix.md`를 기준으로 추적한다.

## 기준 IP와 근거

Zena CSS 개발 가이드는 Arm CoreLink MMU-720AE TRM 문서 ID `109745`와
SMMUv3 Architecture Specification `IHI 0070`을 참조 문서로 제시한다.
Zena CSS functional block 설명은 I/O Block이 distributed TBU/TCU component로
구성되어 외부 I/O requester의 I/O virtualization을 제공한다고 설명한다.

Apollo/RD-Aspen DTS는 AP view에서 SMMU를 다음과 같이 노출한다.

```dts
smmu: iommu@1c0000000 {
    compatible = "arm,smmu-v3";
    reg = <0x1 0xc0000000 0x0 0x8000000>;
    dma-coherent;
    #iommu-cells = <1>;
    interrupts = <GIC_SPI 65 IRQ_TYPE_EDGE_RISING>;
    interrupt-names = "combined";
    msi-parent = <&its1 0x10000>;
};
```

따라서 구현 대상은 제품 관점으로는 MMU-720AE이고, OS/driver 관점으로는
generic `arm,smmu-v3` 장치다.

## 현재 QBox 상태

현재 QBox direct/full AP 경로는 `arm_smmuv3` QEMU-backed component를 사용한다.
`tools/qbox/qemu-components/arm_smmuv3/include/arm-smmuv3.h`는 QEMU
`arm-smmuv3` sysbus device를 만들고, `mem` target socket과 4개 IRQ output을
SystemC에 노출한다. `tools/qbox/platforms/fvp-rd-aspen/conf.lua`는
`smmu_0`을 `arm_smmuv3`로 생성하고 `0x1c0000000/0x08000000`, SPI 65,
`stage = "1"`로 연결한다.

이 스펙의 완료 상태에서는 Apollo/FVP 플랫폼의 SMMU module type을
`mmu720ae` SystemC component로 교체할 수 있어야 한다. QEMU backend는
초기 A/B 비교와 regression fallback으로만 남긴다.

## 범위

구현 범위는 다음이다.

- MMU-720AE TCU register frame 및 SMMUv3 architectural register behavior.
- Distributed TBU ingress 모델. Apollo cfg2 기본 TBU interface는 local
  Zena CSS SMD_CSR 문서에 나타나는 `TBUACE1`, `TBUACE2`, `TBULTI00`,
  `TBULTI01`, `TBULTI02` 다섯 개를 기준으로 한다.
- Stream ID, Substream ID, security attribute, requester attribute 전달.
- Stream table, context descriptor table, stage 1, stage 2, nested translation.
- AArch64 long-descriptor page-table walk와 permission/access fault.
- Command queue, event queue, PRI queue, global error, queue overflow.
- Combined SPI 65 interrupt, MSI delivery path to ITS, optional individual
  IRQ lines.
- ATS/PRI behavior. FVP cfg2에서 ID register가 해당 기능을 노출하지 않으면
  비활성 feature로 정확히 노출한다.
- TLB/uTLB/ATC cache와 DMI grant/invalidation.
- RAS/PMU visible surface와 Zena CSS IO_REGBANK/SMD_CSR 연동.
- QBox Lua/CCI parameter, trace/statistics, FVP comparison report.

## 비범위

- QEMU `arm-smmuv3` 소스 복사 또는 QEMU device wrapper 확장.
- Linux driver workaround, DTS compatible 변경, driver patch 기반 우회.
- Translation 결과를 항상 bypass하는 fast path.
- FVP 내부 구현을 reverse-engineering하는 방식의 동작 복제.
- MMU-500/SMMUv2 register model을 MMU-720AE로 이름만 바꾸는 접근.

## 기능 요구사항

### FR1. 순수 SystemC/TLM component

`mmu720ae`는 `tools/qbox/systemc-components/mmu720ae/` 아래에 위치한다.
QEMU object, QEMU MemoryRegion, QEMU AddressSpace, `QemuDevice`에 의존하지
않는다. AP CPU와 다른 QEMU-backed bus master가 직접 DMA를 수행해야 하는
경우에는 별도 SystemC/TLM adapter를 두고, MMU-720AE core 안에 QEMU 타입을
넣지 않는다.

### FR2. FVP-compatible register identity

TCU register model은 MMU-720AE TRM `109745`와 SMMUv3 spec `IHI 0070`에
근거한 ID, capability, queue, control, status, fault register reset value와
side effect를 제공한다. Linux `arm-smmu-v3` driver가 `IDR0`, `IDR1`, `IDR3`,
`IDR5`, `CR0/CR0ACK`, queue base/prod/cons, IRQ setup, `SMMUEN` enable
sequence를 FVP와 같은 observable result로 완료해야 한다.

### FR3. Apollo cfg2 integration profile

기본 CCI profile 이름은 `zena-css-cfg2`로 한다. 이 profile은 다음 AP-visible
연결을 제공한다.

| 항목 | 값 |
| --- | --- |
| Register base | `0x1c0000000` |
| Register size | `0x08000000` |
| Device-tree compatible | `arm,smmu-v3` |
| Combined interrupt | GIC SPI 65, edge-rising |
| MSI parent | ITS `its1`, device ID base `0x10000` |
| Default stage | Stage 1 |
| Default AP CPU count | 4 |
| Default TBU interfaces | `TBUACE1`, `TBUACE2`, `TBULTI00`, `TBULTI01`, `TBULTI02` |

### FR4. TBU transaction path

각 TBU는 TLM target socket으로 requester transaction을 받고, translation 후
downstream initiator socket으로 전달한다. Transaction attribute는 다음 정보를
운반해야 한다.

- Stream ID와 optional Substream ID.
- Secure/non-secure attribute.
- Read/write/atomic intent.
- Privileged/unprivileged and instruction/data attribute.
- ATS/PRI capability and PASID-like SSID information when enabled.

기존 requester가 Stream ID extension을 제공하지 않는 경우, TBU별 CCI parameter로
정의한 default SID를 사용한다. 현재 구현은 `request_attrs_extension`의 SID를
우선 사용하고 extension이 없을 때만 fallback counter를 증가시킨다. SSID,
security, privileged, instruction, ATS 속성은 extension 필드로 예약되어 있으나
translation semantics에 아직 반영되지 않았다. FVP parity 검증에서는 실제
requester SID가 확인된 뒤 기본값을 고정한다.

### FR5. Table walker와 translation semantics

Table walker는 STE, CD, stage 1 descriptor, stage 2 descriptor를 guest memory에서
읽는다. Permission, memory attribute, shareability, output address size,
translation granule, break-before-make, access flag, dirty state, invalid
descriptor, abort/bypass STE를 처리한다.

Translation 결과는 TLB/uTLB에 cache되고, command queue TLBI 계열 명령, CD/STE
변경, reset, queue error, DMI invalidation 요청으로 정확히 무효화된다.

### FR6. Queue engine

Command queue는 Linux driver가 producer index를 쓰면 SystemC process가 명령을
순서대로 실행하고 consumer index 및 `CMD_SYNC` completion을 갱신한다.
Event queue는 translation/fetch/permission/config fault를 SMMUv3 event record로
작성한다. 현재 구현은 STE/CD walker 미구현 guard에서 발생하는 TBU translation
fault record만 작성한다. PRI queue는 feature가 활성화된 경우 Page Request를
기록하고 PRI interrupt를 발생시킨다.

Queue overflow, illegal command, bad base alignment, disabled queue 접근은
TRM/spec에 맞는 status bit와 interrupt를 만든다.

### FR7. Interrupt and MSI

`mmu720ae`는 최소한 combined IRQ output을 제공한다. Optional output은 eventq,
priq, gerror, sync/PMU/RAS 분리를 위해 추가할 수 있다. Apollo DTS는
`interrupt-names = "combined"`이므로 기본 Linux path는 SPI 65 하나로 동작해야
한다. MSI mode가 ID register와 driver configuration으로 활성화되면 ITS에
MSI write를 발생시키는 SystemC/TLM initiator path를 제공한다.

### FR8. RAS, PMU, and Zena CSS sideband

Zena CSS programmer model은 SMMU PMU interrupt, TCU edge-triggered interrupt,
SMMU/TBU RAS ERI/FHI/CRI status, SMD_CSR TBU SID/uTLB configuration register를
제공한다. `mmu720ae`는 다음 두 경계를 가진다.

- TCU/TBU 내부 RAS/PMU state를 모델링한다.
- Zena CSS IO_REGBANK/SMD_CSR component가 동일 state를 읽고 쓸 수 있도록
  typed sideband API를 제공한다.

초기 구현에서 IO_REGBANK/SMD_CSR MMIO window가 별도 component에 남아 있더라도,
state ownership은 `mmu720ae` 쪽에 있어야 한다.

### FR9. DMI and performance

DMI는 translated range와 permission을 기준으로만 부여한다. TLB invalidation,
STE/CD write, queue reset, SMMU disable, fault recovery, address-space remap
시 기존 DMI grant를 무효화한다. 잘못된 DMI로 translation bypass가 발생하면
acceptance fail이다.

### FR10. Traceability and diagnostics

모델은 `result.json` 또는 sidecar JSON에 다음 정보를 남긴다.

- MMU-720AE profile, ID register values, enabled features.
- Queue command count, queue error count, event count.
- TBU별 translation hit/miss/fault count.
- DMI grant/invalidation count.
- SID/SSID fallback usage.
- FVP comparison mode에서 register trace mismatch.

## 비기능 요구사항

- **Fidelity:** FVP와 observable behavior가 같아야 한다. Probe success만으로
  완료 판정하지 않는다.
- **Reproducibility:** 모든 runtime 검증은 file-backed output directory에
  UART logs, QBox platform log, SMMU trace/stat JSON, result JSON을 남긴다.
- **Maintainability:** register decode, queue engine, table walker, TBU path,
  cache/DMI path를 분리한다.
- **Determinism:** SystemC simulation time과 delta-cycle ordering을 사용하고,
  host wall-clock wait로 queue completion을 만들지 않는다.
- **License:** TRM/spec에서 얻은 register/field knowledge를 구현하되, 문서
  본문을 대량 복사하지 않는다.

## 수락 기준

| ID | 기준 |
| --- | --- |
| AC1 | `mmu720ae` target이 QEMU dependency 없이 빌드된다. |
| AC2 | MMU-720AE TRM/SMMUv3 spec traceability matrix가 구현 register, reset, side effect, test와 연결된다. |
| AC3 | Unit tests가 ID/reset, CR0ACK, queue, table walk, STE/CD, TBU, fault, IRQ, DMI invalidation을 통과한다. |
| AC4 | `tools/qbox/platforms/fvp-rd-aspen/conf.lua`와 `tools/qbox/platforms/fvp-rd-aspen-rse/conf.lua`에서 opt-in으로 `arm_smmuv3` 대신 `mmu720ae`를 선택할 수 있다. |
| AC5 | Apollo direct Linux boot에서 `arm-smmu-v3` driver probe, sysfs registration, no probe error가 확인된다. |
| AC6 | Synthetic DMA requester test에서 bypass, translated, abort, permission fault, stale-DMI-negative cases가 모두 통과한다. |
| AC7 | FVP와 QBox의 SMMU register trace, Linux dmesg, `/sys/kernel/iommu_groups`, `/proc/interrupts`, fault injection 결과가 comparison report로 비교된다. |
| AC8 | Full-system Apollo boot에서 RSE, SI CL0/CL1, TF-A, U-Boot, Linux marker가 기존 QEMU-backed SMMU path 대비 regression 없이 유지된다. |
| AC9 | Any unsupported feature is disabled in ID registers or explicitly listed as a fidelity gap; exposed-but-unimplemented feature is not allowed. |

## 리뷰 기준

리뷰어는 다음을 fail 조건으로 본다.

- `mmu720ae` core가 QEMU header나 QEMU object lifetime에 의존한다.
- Linux probe를 위해 ID register bit를 노출했지만 해당 feature의 register
  side effect와 transaction behavior가 없다.
- Data path가 SMMU disabled 상태 외에 항상 bypass된다.
- TBU/TLB/DMI invalidation 없이 translated DMI를 유지한다.
- Fault가 event queue 없이 log-only로 처리된다.
- FVP comparison 없이 direct boot pass만으로 완료를 주장한다.
- SMD_CSR TBU SID/uTLB state와 TBU behavior가 분리되어 서로 다른 값을 가진다.
