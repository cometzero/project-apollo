# Global 및 domain-local memory map

기준 snapshot은 [README](README.md), 연결 방향은
[fabric routing](fabric-routing.md)을 따른다. 주소 범위의 끝은 inclusive이다.
`base + size` 표에서는 끝 주소가 `base + size - 1`이다. KiB/MiB/GiB는
2의 거듭제곱 단위이며, hardware aperture 크기가 실제 RAM 용량을 뜻하지 않는다.

## 1. 52비트 system-management namespace

[Hardware programmer's model][map] §9.1.4는 독립된 52비트 주소 공간에서
`[51:48]`로 대상 도메인을 선택한다. AP의 48비트 physical map,
RSE의 32비트 map, SI의 40비트 map은 이 공간에 노출되는 별도 view이다.
SMD 자체의 영역(selector 2)과 이 전체 global namespace를 구분한다.

| Selector | Hardware global aperture / 해석 | QVP `system_router`의 실제 범위 |
| --- | --- | --- |
| `0x0` | `0x0000000000000–0x0FFFFFFFFFFFF`, AP physical access | 일부 AP shared/GIC/flash bridge와 CMN/cluster-control target. AP 전체를 통째로 전달하는 bridge는 없음 |
| `0x1` | `0x1000000000000–0x1FFFFFFFFFFFF`, AP through TCU | 이 selector 전체의 forwarding 구성 없음. AP PCIe SMMU 경로와 별개 |
| `0x2` | `0x2000000000000–0x2FFFFFFFFFFFF`, SMD selector | 전 범위를 `system_to_smd_nci`로 `smd_router`에 전달; 실제 target은 아래 부분집합 |
| `0x3` | RSE base `0x3000000000000`; 32비트 local map | AP↔RSE MHU 등 명시적 target. RSE local 전체를 그대로 전달하는 bridge는 없음 |
| `0x4` | SI base `0x4000000000000`; 40비트 local map | SI SRAM/control/ATU/MHU 등 명시적 target. CL0/CL1 local 전체의 identity mapping은 아님 |
| `0x5–0xF` | Reserved | 지원 대상으로 정의되지 않음 |

Hardware Table 9-8의 SI 행은 끝 주소 `0x04_0000_FFFF_FFFF`(4 GiB 범위),
크기 `256 TB`, 본문의 40비트 SI 설명이 서로 일치하지 않는다. 이 문서는
selector와 확인된 개별 target만 사용하며 해당 행의 끝 주소를 확정하지 않는다.
예를 들어 CFG2 CL1 SRAM global 주소 `0x4000140000000`은 그 표의 인쇄된
끝 주소를 넘는다. 이는 참조 자료의 불일치이지 QVP의 잘못된 주소라는 증거가 아니다.

Hardware는 이 global 경로에 NI-710AE APU gating을 두고 reset에서 RSE만
허용한다. QVP의 router 존재만으로 이 보안 정책이 전체 구현되었다고 볼 수 없다.

## 2. AP map: hardware aperture 대 QVP

근거: [hardware Tables 9-3/9-4][map], [AP_ADDRESS/AP_SIZE 및 최종 rebind][ap],
[RoS 구성][ros], [CL0가 정의하는 CMN/control target][cl0].

| Hardware AP 영역 / 범위 | QVP의 주요 구현 / view | 비교 |
| --- | --- | --- |
| Shared SRAM `0x00000000–0x07FFFFFF` | ap `0x00000000–0x001FFFFF`의 여러 SRAM 객체 | 128 MiB aperture 중 2 MiB subset |
| Expansion1 `0x08000000–0x0FFFFFFF` | 본 분석 경로에 전면 backing 없음 | 미구현 aperture |
| System NoC0–3 GPV `0x10000000–0x13FFFFFF` | 해당 4×16 MiB 전체 GPV decode 없음 | SI local NCI 모델과 혼동 금지 |
| UART `0x1A400000`, `0x1A410000` | ap, 각 64 KiB | NS/S UART 주소 대응 |
| AP timer `0x1A810000–0x1A83FFFF` | ap `ap_timer_mem` 관련 MMIO | counter/control/security semantics는 장치별 검사 필요 |
| FMU aperture `0x1D000000–0x1DEFFFFF` | ap `0x1D000000 + N*0x100000`, 각 `0x50000`, N=0..3 | 일부 cluster FMU만 구현 |
| GIC aperture `0x20000000–0x27FFFFFF` | ap GICD `0x20800000`, ITS `0x20840000`, GICR `0x20880000`부터 | frame별 target; aperture 전체 RAM 아님 |
| AP expansion `0x30000000–0x3FFFFFFF` | ap RoS peripherals, flash `0x38000000 + 0x08000000` | RoS/flash 배치는 FVP software 구성 |
| AP→SMD `0x40000000–0x4FFFFFFF` | ap `host_ap_atu`: `0x40000000 + 0x00800000` | 256 MiB 중 8 MiB ATU data aperture; PFDI 예외 bridge 포함 |
| AP_EXP_I_1 NoC config `0x50000000–0x5000FFFF` | 해당 GPV 전체 기능 모델 없음 | 미구현 |
| RGIC2LGIC `0x5FFF0000–0x5FFFFFFF` | ap `ap_rgic2lgic_messreg` | MMIO 모델; NoC data mesh와 별도 |
| PCIe low `0x60000000–0x7FFFFFFF` | ap PIO `0x60200000 + 0x100000`, MMIO `0x60300000 + 0x1FD00000` | 일부 aperture; QVP GPEX 구성 |
| DRAM low `0x80000000–0xFFFFFFFF` | ap DRAM1 `0x80000000 + 0x7F000000`와 아래 carveout | 2 GiB 전체가 단일 RAM 아님 |
| CMN GPV `0x100000000–0x13FFFFFFF` | **system** `si_cl0_cmn_cyprus`가 같은 범위 decode | AP router에 이 CMN target으로 가는 일반 bridge 없음 |
| Cluster management `0x140000000–0x17FFFFFFF` | system cluster utility subset 및 ap SBIST target | view별 subset. 하나의 전면 공유 window 아님 |
| DMC control `0x180000000–0x1BFFFFFFF` | 전면 controller/PHY fabric 없음 | 실제 DRAM backend와 구분 |
| I/O config `0x1C0000000–0x21FFFFFFF` | ap SMMU `0x1C0000000 + 0x08000000` 등 | 전체 NI/PCIe PHY aperture 구현 아님 |
| Expansion2 `0x600000000–0x7FFFFFFFF` | 전면 backing 없음 | QVP PCIe high MMIO와 별개 |
| Debug `0x800000000–0x87FFFFFFF` | 전면 debug fabric 없음 | 미구현 aperture |
| DRAM `0x880000000–0xDFFFFFFFF` | 해당 bank 전체 backing 없음 | hardware aperture와 populated RAM 구분 |
| PCIe high space2/3 `0x10000000000–0x1FFFFFFFFFF` | GPEX high MMIO는 **`0x400000000 + 0x200000000`** | hardware high PCIe 주소 배치와 차이 |
| DRAM high `0x20000000000–0xBFFFFFFFFFFF` | ap DRAM2 `0x20000000000 + 0x80000000` | high aperture 중 2 GiB backing |
| Expansion3 `0xC00000000000–0xFFFFFFFFFFFF` | 전면 backing 없음 | 미구현 aperture |

QVP GPEX ECAM은 `0x43B50000 + 0x10000000`에 배치된다. 이는 hardware의
AP→SMD/예약 영역과 비교해 차이가 있는 QVP/FVP 호환용 배치다. PCIe endpoint
controller 모델은 ap `0x30300000 + 0x1000`, outbound
`0x30400000 + 0x400000`에 있다. 이 주소들을 hardware NI/PHY register
map의 동등 구현으로 해석하지 않는다.

### 실제 AP SRAM / low DRAM carveout

| AP base | Size | 객체 / 용도 |
| --- | --- | --- |
| `0x00000000` | `0x100000` | `host_ap_shared_sram`, boot/SDS/SCMI |
| `0x00100000` | `0x80000` | `host_ap_bl2_header_sram`, HIPC alias의 backing |
| `0x00180000` | `0x1000` | `host_ap_mhu_ns_shared_sram` |
| `0x00181000` | `0x7F000` | `host_ap_peripheral_ns_sram_tail` |
| `0x80000000` | `0x7F000000` | `host_ap_dram1`, 끝 `0xFEFFFFFF` |
| `0xFFA00000` | `0x100000` | `host_ap_cper` |
| `0xFFBF0000` | `0x2000` | `host_ap_ffa_mm_comm_buffer` |
| `0xFFC00000` | `0x3E0000` | `host_ap_spmc_sdram`, 끝 `0xFFFDFFFF` |
| `0xFFFE0000` | `0x20000` | system RSE pointer-access memory로 연결하는 bridge |

`0xE0130000–0xE01AFFFF`는 low DRAM 안에 수치상 포함되지만, priority 0의
HIPC alias가 선택되어 `0x00100000–0x0017FFFF`로 간다. 따라서 위 DRAM1
크기는 할당 backing 크기이며, 모든 주소가 그 RAM으로 decode된다는 뜻은 아니다.
표에 없는 low-DRAM hole은 자동으로 RAM으로 채워지지 않는다.

## 3. Global SMD / RSE / SI target ledger

아래는 도메인 간 접근에 중요한 구현 target을 묶은 표다. 모든 peripheral
register의 전수 목록은 아니며, 같은 aperture 내부의 reserved 부분까지
구현된 것으로 보지 않는다. 근거: [system-management Lua][smd],
[fabric Lua][fabric], [CL0 Lua][cl0], [CL1 Lua][cl1].

| Global base | Size | 최종 decode / target |
| --- | --- | --- |
| `0x2000060000000` | `0x100000` | smd / `host_smd_shared_sram` |
| `0x20000D0010000` | `0x10000` | smd / CSS reset control |
| `0x20000D0070000` | `0x10000` | smd / `host_smdexp2smd_atu` registers |
| `0x20000D0080000` | `0x10000` | smd / `host_ap_atu` registers |
| `0x20000D0100000` | 3 × `0x10000` | smd / CSS counter control/read/sync |
| `0x20000D0200000` | `0x10000` | smd / SYSTOP PIK |
| `0x20000D0310000` | `0x1000` | smd / SMD GPIO |
| `0x20000D0400000` | `0x10000` | smd / system ID |
| `0x20000D2000000 + N*0x100000` | `0x50000` each | smd → ap cluster NI FMU, N=0..3 |
| `0x20000D2400000` | `0x100000` | smd / NI system-control FMU window |
| `0x20000D2600000` | `0x100000` | smd / NI SMD FMU window |
| `0x20000D8000000` | `0x20000` | smd / SMD expansion window, subtargets 포함 |
| `0x300001B600000` | `0x30000` per frame | system / AP↔RSE MHU PBX, MBX는 다음 frame |
| `0x4000028000000` | `0x800000` | system / CL0 cluster utility, PPU subtarget 포함 |
| `0x4000028800000` | `0x800000` | system / CL1 cluster utility, PPU subtarget 포함 |
| `0x400002A600000` | `0x10000` | system / SI PIK |
| `0x400002A6B0000` | `0x10000` | system / SI SCR |
| `0x4000031000000` | `0x10000` | system / `host_si_atu` registers |
| `0x400003B000000`, `0x400003B040000` | `0x30000` each | system / AP↔CL0 NS SCMI PBX/MBX |
| `0x400003B080000`, `0x400003B0C0000` | `0x30000` each | system / AP↔CL0 SCMI PBX/MBX |
| `0x400003B100000`, `0x400003B140000` | `0x30000` each | system / AP↔CL1 HIPC PBX/MBX |
| `0x400003B380000`, `0x400003B3C0000` | `0x30000` each | system / AP PFDI monitor PBX/MBX |
| `0x400003C000000` | `0x20000` per frame | system / RSE↔CL0 MHU PBX, MBX는 다음 frame |
| `0x4000040000000` | `0x40000` | system / RSE↔SI shared SRAM |
| `0x4000120000000` | `0x1000000` | system / CL0 global SRAM window |
| `0x4000140000000` | `0x1000000` | system / CL1 global SRAM window, CFG2 |

Global의 AP selector `0x0`에 DRAM2가 숫자상 포함되어도 `system_router`에는
AP DRAM 전체를 전달하는 bridge가 없다. RSE/SI에서 임의의 AP PA를 ATU로
만들어 보내는 것과 해당 target이 global view에 연결되어 있는 것은 별도 조건이다.

## 4. RSE local map와 외부 접근

근거: [RSE Lua][rse], [reference RSE design][components], [hardware RSE map][map].

| RSE local base / 범위 | QVP 의미 | 비교/주의 |
| --- | --- | --- |
| `0x11000000 + 0x20000` | Secure ROM | RSE local target |
| `0x10000000 + 0x8000` | ITCM secure; NS `0x0`, CPU0 S/NS `0x1A000000/0x0A000000` | split-alias 옵션에 따라 CPU0 backing 분리 가능 |
| `0x30000000 + 0x8000` | DTCM secure; NS `0x20000000`, CPU0 S/NS `0x34000000/0x24000000` | 동일한 옵션 주의 |
| `0x31000000` | VM0; VM1은 VM0 + VM size | VM size=`2^rse_vmaddrwidth`, 기본 256 KiB |
| `0x50150000 + 0x1000` | ATU registers | local programming interface |
| `0x60000000–0x6FFFFFFF` | NS host-access data window | `rse_atu_regs` → system |
| `0x70000000–0x7FFFFFFF` | Secure host-access data window | 같은 translation socket의 alias |
| `0xB0000000 + 0x04000000` | RSE boot flash | local/backend 옵션에 따른 구성 |

Hardware의 secure ATU **code** window `0x12000000–0x12FFFFFF`는 위 QVP
host-access **data** aperture와 같지 않다. 이 문서에서 해당 code window의
완전한 fetch translation 구현을 주장하지 않는다. Local peripheral의 일부는
RSE QEMU container 안에서 처리되므로 바깥 `rse_router`만으로 모든 CPU
접근을 설명할 수 없다.

## 5. SI local map 및 ATU

근거: [CL0][cl0], [CL1][cl1], [system-management][smd],
[hardware SI map][map], [CFG2][components].

| 기능 | CL0 local | CL1 local | QVP 구현 경계 |
| --- | --- | --- | --- |
| 실행 SRAM | `0x120000000 + 0x800000` | `0x140000000 + 0x800000` | global 16 MiB window와 각각 별도 backing |
| UART | `0x2A400000 + 0x10000` | `0x2A410000 + 0x10000` | 각 local router |
| GICD | View0 `0x30000000`, View1 `0x30100000` | View2 `0x30200000` | multiview와 backend routing; aperture 전체 RAM 아님 |
| GICR | View1 `0x30140000` | `0x30260000 + N*0x20000`, N=0..3 | frame마다 `0x20000` |
| Primary/secondary/MHU NCI | `0x2A000000/0x2A200000/0x2A300000` | 같은 전체 NCI 구성 없음 | 각 CL0 NCI `0x10000` |
| SSU / FMU | `0x2A500000 / 0x2A510000` | CL0가 safety 기능 관리 | SSU `0x1000`, FMU `0x50000` |
| AP NS MHU PBX/MBX | `0x38000000 / 0x38040000` | `0x39000000 / 0x39040000` | HIPC/SCMI endpoint의 로컬 view |
| RSE MHU PBX/MBX | `0x38100000 / 0x38140000` | 이 pair 없음 | CL0↔RSE |
| CL0↔CL1 PFDI PBX/MBX | `0x38200000 / 0x38240000` | `0x39200000 / 0x39240000` | 각 frame `0x20000` |
| RSE shared buffer | `0x40000000 + 0x40000` | 직접 bridge 없음 | CL0 → global RSE/SI SRAM |
| PFDI shared buffer | `0x48000000 + 0x1000` | `0x48000000 + 0x1000` | CL0 bridge → CL1 memory |
| HIPC shared buffer | ATW 영역 `0xE0130000` | `0xE0130000 + 0x80000` | CL0는 ATU 상태 의존, CL1은 고정 AP bridge |

Hardware PCMA/PCPA ATU register는 SI local `0x31000000/0x31010000`에
기술되며 RSEMM 접근과 APU gating 제약이 있다. QVP는 `host_si_atu` register를
global `0x4000031000000`에 두고 data socket을 CL0 local router에 연결한다.
PCMA/PCPA의 모든 hardware route가 각각 구현되었다는 뜻은 아니다.

### 실제 ATU data aperture와 대표 ATW 의도

| QVP ATU | Register view / base | Data 입력 view / base / size | 출력 |
| --- | --- | --- | --- |
| `rse_atu_regs` | rse `0x50150000` | rse `0x60000000` 및 secure alias `0x70000000`, 각 `0x10000000` | system |
| `host_ap_atu` | global→smd `0x20000D0080000` | ap `0x40000000 + 0x800000` | system |
| `host_si_atu` | system `0x4000031000000` | cl0 `0x80000000 + 0x60340000` | system |
| `host_smdexp2smd_atu` | global→smd `0x20000D0070000` | cl0 `0xE0340000 + 0x2000` | system |

CL0 Lua에는 다음 대표 ATW의 논리/목적지 상수가 있다. 이는 firmware가 해당
window를 설정했을 때의 대응이며 이번 작업에서 runtime register를 읽은 값이 아니다.

| CL0 logical base | 목적지 global base | 용도 |
| --- | --- | --- |
| `0x80000000` | `0x100000000` | CMN GPV |
| `0xC0000000` | `0x140000000` | AP cluster utility |
| `0xD0000000` | `0x20000D8000000` | SMD expansion |
| `0xD0030000` | `0x20000D0400000` | System ID |
| `0xD0040000` | `0x20000D0100000` | CSS counters/timers |
| `0xE0030000` | `0x00000000` | AP peripheral SRAM |
| `0xE0130000` | `0x00100000` | AP peripheral NS SRAM |
| `0xE0240000` | `0x2000060000000` | SMD SRAM |

ATU register의 enable/offset/permission과 downstream binding을 모두 확인해야
실제 접근 가능 여부를 판단할 수 있다. 특히 global CMN과 SI CL1 SRAM은
숫자 `0x140000000` 주변을 서로 다른 view에서 사용하므로 주소에서
도메인 정보를 생략하면 충돌처럼 보일 수 있다.

## 6. 해석 시 지켜야 할 경계

- Hardware reserved/expansion aperture, FVP RoS 배치, QVP의 실제 장치
  backing을 구분한다. Virtio/flash 배치를 CSS hardware IP 목록으로 옮기지 않는다.
- CMN-S3AE/NI-710AE control map이 존재하는 것과 해당 NoC가 메모리 traffic을
  전달하는 것은 다르다. 상세 경로는 [routing 문서](fabric-routing.md)를 따른다.
- 하드웨어 secure/NS 속성은 주소 숫자만으로 결정되지 않는다. 실제 QVP
  request context와 endpoint/filter 구현을 함께 검사해야 한다.
- 미구현 aperture와 이미 연결된 target 내부의 reserved register는 다른
  경우다. 정확한 실패 응답은 router 및 장치 구현/실제 transaction으로 확인한다.
- 현재 문서는 소스 정적 분석이다. 동적 ATU map, DMI 허용 범위, CPU/DMA
  접근 성공과 거부 결과는 별도 실행 증거가 필요하다.

[map]: ../arm_zena_css_dev_guide/09-programmers-model-for-zena-css.md
[ap]: ../../hsoc-stack/tools/qbox-platform/platforms/apollo/hw-block/ap_compute.lua
[ros]: ../../hsoc-stack/tools/qbox-platform/platforms/apollo/hw-block/ros.lua
[smd]: ../../hsoc-stack/tools/qbox-platform/platforms/apollo/hw-block/system_mgmt.lua
[fabric]: ../../hsoc-stack/tools/qbox-platform/platforms/apollo/hw-block/fabric.lua
[rse]: ../../hsoc-stack/tools/qbox-platform/platforms/apollo/hw-block/rse.lua
[cl0]: ../../hsoc-stack/tools/qbox-platform/platforms/apollo/hw-block/si_cl0.lua
[cl1]: ../../hsoc-stack/tools/qbox-platform/platforms/apollo/hw-block/si_cl1.lua
[components]: ../../arm-zena-css/documentation/design/components.rst
