# Apollo GIC-720AE FVP 대비 QBox 구현 분석

작성일: 2026-07-29

기준 구성: `apollo-qvp`, `cfg2`, Primary Compute 4 CPU

## 1. 결론

**QBox에는 FVP의 GIC-720AE 기능이 모두 구현되어 있지 않다.**

현재 QBox는 Apollo가 부팅하는 데 필요한 GICv3/ITS 기반 AP 경로,
4 CPU redistributor, Linux가 관측하는 GICv4.1 feature 정보, AP 및 SI의
multiview register 호환 창을 제공한다. FVP와 QBox의 Linux discovery
로그도 현재 비교 항목에서 일치한다.

그러나 다음 기능은 FVP와 동등하지 않다.

1. Safety Island의 하나의 물리 GIC를 세 programming view가 공유하는
   interrupt ownership/routing/state 의미론
2. GIC-720AE FuSa, FMU 내부 fault, RAS, GSPV, parity/CRC 및 fault
   containment
3. `GICR_PWRR`, `GICR_WAKER` sleep/quiescence, Q/P channel과
   reset/power state 연동
4. SPI Collator와 `RGIC2LGIC_MESSREG`의 실제 message/interrupt 의미론
5. real-time SPI의 우선순위 보호 및 timing 의미론
6. 현재 image에서 실행 가능한 AP MSI/LPI delivery와 virtual LPI
   injection의 현재 시점 검증
7. SI의 64 extended PPI, PMU PPI 및 GIC maintenance PPI 경로

따라서 올바른 표현은 다음과 같다.

> QBox는 Apollo cfg2의 4-CPU 부팅에 필요한 GICv3/ITS와 Linux-visible
> GICv4.1 discovery, 그리고 일부 multiview programming register를
> 구현한다. 이는 GIC-720AE 전체 기능 또는 FVP 기능 동등성을 의미하지
> 않는다.

## 2. 조사 범위와 판정 방법

### 2.1 조사한 기준

- Arm GIC-720AE TRM Issue 11, Document ID `102666_0201_11_en`,
  2025-04-10:
  [Arm GIC-720AE TRM](https://documentation-service.arm.com/static/681dc5f30aae2a5d8f0441dc)
- 로컬 변환 TRM:
  [`doc/gic-720ae/`](../../gic-720ae/)
- Zena CSS 개발 가이드:
  [`doc/arm_zena_css_dev_guide/`](../../arm_zena_css_dev_guide/)
- RD-Aspen/FVP 구성과 DT:
  [`arm-zena-css/`](../../../arm-zena-css/)
- QBox core, QBox platform, local QEMU, Linux, SCP-firmware, Zephyr source
- 설치된 `FVP_Zena_CSS_Cfg2`의 `--list-params`와 `--list-instances`
- 현재 및 보존된 FVP/QBox UART/runtime artifact

TRM의 제품 최대값은 Apollo cfg2의 활성 기능과 분리했다. confidential
Configuration and Integration Manual 및 Safety Manual의 비공개 세부
구현은 공개 TRM과 실제 FVP model introspection으로 확인 가능한
범위까지만 판정했다.

### 2.2 소스 기준선

| 저장소 | SHA |
| --- | --- |
| top | `74a840983c4588e07c6fb31d1c89ddbafc5b49a4` |
| arm-zena-css | `bf34d9e71f674e11beea3b8e84ea54486f555d2a` |
| QBox | `e2fbcd3b013a10f7dceef0330528b5e06007f911` |
| qbox-platform | `ccd75e80d48e8958dd78fc9b21d775b18600367d` |
| local QEMU | `cd894169c8c1ce6aee4c43642a9fd4ef51045e12` |
| Linux | `708806bb9328ab6c2b2994fe59d48c80df28682c` |
| SCP-firmware | `6d2e1e8094c7575c8a9b7fb2410dc2748a550882` |
| Zephyr | `69df4c76c5bb62c764d6cc3d860fd6fe699f2e50` |
| Zephyr HSOC source | `b6108117918314755d00fa969175cb64c1942e58` |

활성 Yocto 구성은
[`build/conf/local.conf`](../../../build/conf/local.conf),
[`build/conf/bblayers.conf`](../../../build/conf/bblayers.conf),
[`build/conf/templateconf.cfg`](../../../build/conf/templateconf.cfg)를
직접 확인했다.

## 3. FVP의 활성 GIC 기준

설치된 모델은 Fast Models `11.31.25 (Feb 25 2026)`이며 executable
SHA-256은
`246dfb8637d6d4264ce6817089e55a4b8335e47d9f46f92cb128b6eed2df2b37`이다.
FVP package는 AP와 SI를 각각 `GIC720AE` instance로 식별한다.
원본 introspection은
[`fvp-gic-introspection.txt`](../../../build/qbox-apollo-qvp/gic-720ae-validation-20260729-195140/fvp-gic-introspection.txt),
핵심 값은
[`fvp-gic-params-concise.txt`](../../../build/qbox-apollo-qvp/gic-720ae-validation-20260729-195140/fvp-gic-params-concise.txt)에
보존했다.

### 3.1 Primary Compute GIC

| 항목 | FVP cfg2 기준 |
| --- | --- |
| model/IIDR | `GIC720AE`, `0x0700143b` |
| architecture | GICv4.1 활성, two security states |
| interrupt 수 | 960 SPI, 16 PPI, EPPI 0, NMI 비활성 |
| ITS | 1개, ID bits 16, collection ID bits 8, device bits 20 |
| multiview | 활성, View 0-3 register inventory |
| CPU/GICR | DT/model 16개, 현재 runtime 활성 CPU는 4개 |
| safety/RAS | `fmu-blktype-num=6` |
| power | `redistributor-power-managed-by-pwrr=1` |
| wake output | `add-output-cpu-wake-request...=0` |
| invalidate registers | `GICR-invalidate-registers-implemented=0` |

마지막 두 항목은 중요하다. 제품 TRM에 있는 모든 optional 기능을 현재
Apollo FVP가 켠 것은 아니다. 예를 들어 별도 CPU wake request output과
`GICR_INVLPIR/INVALLR/SYNCR` 구현은 현재 FVP parameter에서 꺼져 있으므로
그 자체를 QBox의 활성 parity gap으로 계산하지 않았다.

AP 주소는 GICD `0x20800000`, ITS `0x20840000`, 16개의 256 KiB GICR
영역 `0x20880000` 이후이다. Linux DT의 16개 region은 제품 topology를
표현하지만 현재 cfg2 runtime은 CPU0-3만 활성화한다.

### 3.2 Safety Island GIC

FVP에는 AP GIC와 별도의 하나의 SI `GIC720AE` instance가 있다.

| 항목 | FVP cfg2 기준 |
| --- | --- |
| PE | CL0 1개 + CL1 4개, 총 5개 affinity |
| view | View0 boot/config, View1 CL0, View2 CL1 |
| interrupt 수 | 62 SPI block, 16 PPI, 64 extended PPI |
| safety/RAS | `fmu-blktype-num=6` |
| power | `redistributor-power-managed-by-pwrr=1` |
| NMI | 비활성 |

View0은 GICD `0x30000000`, CL0 View1은 GICD/GICR
`0x30100000/0x30140000`, CL1 View2는 GICD `0x30200000`과 네 GICR
`0x30260000` 이후를 사용한다. 핵심 계약은 주소 alias만이 아니라 하나의
물리 GIC state를 여러 view가 공유하고 view policy가 interrupt routing을
제어한다는 점이다.

## 4. QBox 구현 구조

### 4.1 AP

[`ap_compute.lua`](../../../hsoc-stack/tools/qbox-platform/platforms/apollo/hw-block/ap_compute.lua)는
QEMU `arm-gicv3`와 `arm-gicv3-its`를 기능 backend로 사용한다. QBox
wrapper는 distributor, redistributor, SPI/PPI, IRQ/FIQ/vIRQ/vFIQ socket을
QEMU에 연결한다.

- [`arm_gicv3.h`](../../../hsoc-stack/tools/qbox/qemu-components/irq-ctrl/arm_gicv3/include/arm_gicv3.h)
- [`arm_gicv3_its.h`](../../../hsoc-stack/tools/qbox/qemu-components/irq-ctrl/arm_gicv3_its/include/arm_gicv3_its.h)
- [`arm_gicv3_common.c`](../../../hsoc-stack/tools/qemu/hw/intc/arm_gicv3_common.c)
- [`arm_gicv3_its.c`](../../../hsoc-stack/tools/qemu/hw/intc/arm_gicv3_its.c)

Apollo는 이 generic QEMU model에 960 SPI, revision 4, security, LPI,
GICv4.1/DirectLPI/RVPEID/Valid+Dirty discovery property를 설정한다.
AP view0 호환 창은 별도 SystemC
[`gicx00_multiview`](../../../hsoc-stack/tools/qbox-platform/systemc-components/gicx00_multiview/include/gicx00_multiview.h)가
제공하고, active region의 표준 GIC 접근은 QEMU backend로 forward한다.

### 4.2 Safety Island

QBox는 FVP와 달리 SI0과 SI1에 **독립적인 QEMU GIC instance**를 만든다.

- [`si_cl0.lua`](../../../hsoc-stack/tools/qbox-platform/platforms/apollo/hw-block/si_cl0.lua)
- [`si_cl1.lua`](../../../hsoc-stack/tools/qbox-platform/platforms/apollo/hw-block/si_cl1.lua)

SystemC multiview component에는 MMIO target/backend socket만 있고 SPI input,
view별 output, shared pending/active state가 없다. `GICD_IVIEWR`, `VIEWR`,
`PWRR`, `FLUSHR`는 shadow register 또는 forwarding 동작이며 실제 SI0/SI1
interrupt ownership을 바꾸지 않는다. SI interrupt는 Lua에서 두 독립 GIC로
정적으로 연결된다.

[`gic720ae_messreg`](../../../hsoc-stack/tools/qbox-platform/systemc-components/gic720ae_messreg/include/gic720ae_messreg.h)는
64 KiB byte array read/write model이다. message 송수신, SPI Collator,
AXI5-Stream ordering, wake/power handshake 또는 interrupt effect가 없다.

## 5. 기능별 판정

판정은 `구현·현재 검증`, `구현·부분 검증`, `구현·현재 미검증`,
`부분 구현`, `미구현`, `검증 불가`로 나눴다.

| 기능 | FVP cfg2 | QBox 판정 | 근거와 한계 |
| --- | --- | --- | --- |
| AP GICD/GICR/ITS 주소 | 활성 | 구현·현재 검증 | map validator 80/80, Linux boot |
| AP 4 CPU redistributor | 활성 | 구현·현재 검증 | CPU0-3 init와 4 CPU online |
| AP 960 SPI/16 PPI discovery | 활성 | 구현·현재 검증 | FVP/QBox Linux parity |
| AP GICv3 CPU interface | 활성 | 구현·현재 검증 | Linux boot, per-CPU arch_timer IRQ counter |
| AP 기본 SPI delivery | 활성 | 구현·부분 검증 | UART/virtio/MHU counter는 non-zero, controlled delta/affinity 없음 |
| AP physical MSI/ITS/LPI | 활성 model, 정상 DT에는 consumer 없음 | 구현·현재 미검증 | QEMU ITS는 실모델, 과거 문서만 있고 현재 artifact 없음 |
| GICv4.1 feature discovery | 활성 | 구현·현재 검증 | DirectLPI/RVPEID/Valid+Dirty, Linux GICv4.1 |
| GICv4.1 virtual injection | 활성 architecture | 부분 구현 | active Linux에 KVM/VFIO 없음, VMAPP/vPE 의미론 미검증 |
| AP multiple view register | 활성 | 부분 구현 | 호환 창/forwarding은 있음, view policy 동작 자극 없음 |
| AP two security states | 활성 | 부분 구현 | QEMU security 활성, group/security negative test 없음 |
| GIC-720AE identity | 활성 | 미구현 | FVP IIDR `0x0700143b`, QEMU functional ID는 generic GIC 계열 |
| AP 16 CPU capacity | DT/model capacity | 구현·현재 미검증 | 4개 active, 4-15는 synthetic discovery |
| SI 하나의 공유 multiview GIC | 활성 | 미구현 | 독립 SI0/SI1 QEMU GIC와 정적 route |
| SI View register 접근 | 활성 | 부분 구현 | component 11 tests 통과, routing effect 없음 |
| SI CL0 기본 GIC/SCP boot | 활성 | 부분 구현 | multiview config/liveness marker, controlled IRQ 없음 |
| SI CL1 기본 GIC/Zephyr boot | 활성 | 부분 구현 | 4 CPU/PFDI/RPMsg liveness, directed IPI 시험은 별도 |
| SI 1984 SPI capacity | 활성 | 미구현 | QBox CL0 384 SPI, CL1 128 SPI의 독립 instance |
| SI 64 extended PPI | 활성 | 미구현 | QBox wrapper는 CPU당 기본 PPI socket만 노출 |
| SI PMU PPI23/maintenance PPI25 | reference map | 미구현 | Cortex-R82 wrapper에 해당 output 없음 |
| `RGIC2LGIC_MESSREG` | 활성 map | 미구현 | byte storage만 구현 |
| GICR PWRR 연동 | 활성 | 미구현 | `PWRR=0`, shadow storage, power effect 없음 |
| reset 일관성 | 활성 | 부분 구현 | QEMU는 reset되나 multiview/messreg shadow는 reset 입력 없음 |
| generic System FMU/SSU | 플랫폼 기능 | 부분 구현 | synthetic fault/APU denial vertical path가 있으나 전체 topology 아님 |
| GIC 전용 FMU/RAS/GSPV | 활성 | 미구현 | GIC 내부 error model/injection/containment 없음 |
| real-time SPI/priority protection | product/config 기능 | 미구현 | timing/collator/priority protection model 없음 |
| CPU wake request output | FVP에서 비활성 | 범위 밖 | 활성 FVP parity 요구 아님 |
| NMI | FVP에서 비활성 | 범위 밖 | 활성 FVP parity 요구 아님 |

## 6. 도메인별 분석

### 6.1 Primary Compute: Linux

Linux DT는 GICD, 16개 GICR region, ITS를 기술한다.

- [`apollo-qvp.dtsi`](../../../hsoc-stack/components/primary_compute/linux/arch/arm64/boot/dts/arm/apollo-qvp.dtsi)
- [`apollo-qvp.dts`](../../../hsoc-stack/components/primary_compute/linux/arch/arm64/boot/dts/arm/apollo-qvp.dts)

현재 kernel은 `CONFIG_ARM_GIC_V3=y`, `CONFIG_ARM_GIC_V3_ITS=y`, SMP,
CPU hotplug, PCI MSI를 활성화한다. 그러나 normal DT에는 PCI `msi-parent`
또는 `msi-map` consumer가 없고 KVM/VFIO가 비활성이다. 따라서 boot
로그의 LPI table 생성, DirectLPI, GICv4.1 문구는 초기화와 capability
discovery 증거이지 physical LPI 전달이나 virtual LPI injection 증거가
아니다.

이번 검증은 FVP/QBox가 다음 Linux marker에서 일치함을 확인했다.

- 960 SPI, 16 PPI
- DirectLPI, RVPEID, Valid+Dirty
- GICv4.1 ITS
- 32768 collection
- VPE invalidation setup
- CPU0-3 redistributor 초기화

그러나 canonical runner에는 임의 post-login command hook이 없고
`--no-post-login-probe` keep-alive 실행에는 UART input FIFO가 생성되지
않았다. 그래서 `/proc/interrupts`의 controlled delta, affinity 변경,
CPU hotplug는 이번 실행에서 자극하지 못했다.

### 6.2 Safety Island CL0: SCP-firmware

SCP-firmware의 QVP/FVP product configuration은 build-name 등의 차이를
제외하고 의도적으로 정렬되어 있다. 현재 runtime은 다음을 관측한다.

- `GIC-multiview configured successfully`
- AP GIC multiview 구성 marker
- SCP framework/module 초기화
- PFDI monitoring 시작

이는 SCP가 QBox의 register 호환 창을 사용해 부팅함을 증명한다. 하지만
CL0-owned interrupt를 의도적으로 발생시켜 handler counter가 증가하는
시험, `GICD_IVIEWR` 변경 후 delivery view가 바뀌는 시험, GIC FMU
fault injection은 없다. 일부 실행에서는 SI1 core 대상 PFDI monitor
timeout도 반복되므로 SI GIC health 완료로 해석할 수 없다.

### 6.3 Safety Island CL1: Zephyr

CL1 DT는 GICD `0x30200000`과 네 GICR region을 사용하며 SMP 4 CPU,
virtual timer PPI와 SGI 기반 scheduler 경로를 구성한다. 보존 runtime은
네 CPU, PFDI service, RPMsg attach를 확인한다.

그러나 기존 marker gate는 directed IPI counter 또는
timer-interrupt-to-IPI 동작 자체를 확인하지 않는다. Zephyr upstream의
`tests/kernel/multiprocessing/smp`와 `ipi_work`가 적합한 후보이지만,
현재 Apollo CL1 image에서 동일 시험의 실행 결과가 확보되기 전에는
기본 GIC/Zephyr liveness를 넘어선 완료 판정을 하지 않는다.

## 7. 테스트 증거의 해석

이번 실행의 구체적인 결과는
[`test-completion.md`](test-completion.md)에 기록한다. 증거 계층은
다음과 같이 해석한다.

1. static/map validator는 주소와 wiring contract만 증명한다.
2. component test는 register storage, RAZ/WI, address translation,
   backend forwarding만 증명한다.
3. Linux log parity는 discovery/init 문자열만 증명한다.
4. full-system boot는 AP/SI domain liveness와 통합 회귀를 증명한다.
5. interrupt delivery, cross-view isolation, power/reset, FuSa/RAS는
   각각 별도 stimulus와 negative observation이 있어야 증명된다.

## 8. 구현 우선순위

1. SI0/SI1 독립 GIC를 공유-state multiview signal plane으로 교체하고
   `GICD_IVIEWR`가 실제 routing을 제어하도록 한다.
2. GIC view/messreg component에 reset 입력과 reset-domain test를 추가한다.
3. SI extended PPI, PMU PPI23, maintenance PPI25를 모델링한다.
4. opt-in PCI profile로 현재 MSI-X→ITS→LPI와 INTx artifact를 재생성한다.
5. AP/SI에서 controlled SGI/PPI/SPI counter, affinity, CPU hotplug 시험을
   공식 runner hook으로 제공한다.
6. GIC FMU/RAS/GSPV와 PWRR/WAKER 내부 power effect를 구현하고
   fault/power transition negative test를 추가한다. FVP에서 비활성인
   외부 local CPU wake output과는 구분한다.
7. GICv4.1 광고 bit마다 실제 VMAPP/vPE/direct injection 의미론을 시험하고
   미구현 bit는 구현 전까지 광고하지 않는다.

## 9. 남은 검증 불가 경계

- confidential GIC-720AE Configuration and Integration Manual과 Safety
  Manual의 내부 safety mechanism 세부
- FVP 내부 구현과 cycle/timing의 bit-exact 비교
- 현재 normal image에서 guest가 소비할 수 없는 KVM/VFIO virtual LPI
- 현재 미제공 runner command hook을 요구하는 controlled Linux IRQ 자극

이 항목들은 “구현됨”으로 추정하지 않았으며 각각 공개 정보 부족,
모델 성격, image 구성 또는 실행 도구 blocker로 분리했다.
