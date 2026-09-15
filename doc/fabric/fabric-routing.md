# Fabric 및 bus routing

기준 snapshot과 검증 범위는 [README](README.md)를 따른다. 아래 경로는
source Lua의 최종 binding을 추적한 정적 결과이다.

## 1. Hardware 구조와 QVP 대응

| Hardware block / 역할 | 현재 QVP 구성 | 대응 수준 |
| --- | --- | --- |
| AP: DSU-120AE 4 clusters × Cortex-A720AE 4 cores | 별도 AP QEMU instance와 `ap_router`; AP CPU 수 설정 가능 | CPU/MMIO 기능 구성. 실제 DSU cache hierarchy의 동등성은 별도 문제 |
| CMN-S3AE: coherent mesh, CHI/AXI/APB, RN/SAM 및 home node | `si_cl0_cmn_cyprus` (`host_cmn_cyprus`) | CMN 제어/discovery register view; 데이터 mesh 아님 |
| CMN SBSX: CHI에서 외부 memory 측 ACE5-Lite로 변환 | AP RAM target으로 직접 TLM 접근 | CHI packet, snoop, SBSX 및 memory controller bus 전달을 재현하지 않음 |
| NI-710AE: 비일관성 interconnect, expansion/I/O, APU gating | 일반 router + CL0 primary NCI/APU + NCI/FMU 객체 | 선택된 기능과 접근 검사만 모델링 |
| System Management Block: RSE + SI + SMD | RSE/CL0/CL1 독립 QEMU, global `system_router`, SMD `smd_router` | 소프트웨어 도메인과 주소 view 분리 |
| RSE: Cortex-M55, trust root, ATU로 외부 접근 | `rse_cpu_pass`, RSE local router와 `rse_atu_regs` | local memory/peripheral 및 translated access |
| SI CL0: Cortex-R82AE DCLS, SCP 관리 firmware | 단일 R82 CPU, primary APU를 거쳐 CL0 router | 관리 firmware 실행; 물리 lockstep pair 비교/고장 동작과는 구분 |
| SI CL1: FVP CFG2의 4-core SMP | 별도 QEMU instance와 4 R82 CPU, `si_cl1_router` | CFG2 확장. 현재 guide의 hardware SI 구성에는 없음 |

근거: [hardware blocks][hw], [FVP CFG2][fvp],
[reference components][components], [AP Lua][ap], [CL0 Lua][cl0], [CL1 Lua][cl1].

Hardware의 `System Management Block`은 RSE·SI·SMD를 포함하는 블록이다.
반면 `SMD`는 그 내부 관리 도메인이고, 52비트 system-management 주소 공간의
상위 selector `0x2`로 접근하는 대상이다. QVP `system_router`와
`smd_router`를 같은 이름의 버스로 취급하지 않는다.

## 2. 최종 연결 구조

`apollo-qvp.lua`는 `fabric.create()` 후 RSE/AP/RoS/system-management를
정의하고 `ap_compute.enable_ap_router()`에서 AP target과 master를 다시
binding한다. 이후 CL0/CL1을 enable하면서 SI ATU data socket과 bridge를
완성한다. 따라서 초기 `define()`의 `system_router` binding만 읽으면
AP CPU, DRAM, GIC, PCIe 등의 최종 소속을 잘못 판단하게 된다.

| 출발 initiator | 실제 순방향 경로 | 도착 / 조건 |
| --- | --- | --- |
| RSE CPU | `rse_cpu_pass` local/remote 전달 → `rse_router` | ROM/TCM/VM, 보안 peripheral; 일부 QEMU-local 경로는 container 안에서 처리 |
| RSE 외부 접근 | `rse_router` → `rse_atu_regs.translation_socket` → `system_router` | firmware가 설정한 ATU window의 global target |
| AP CPU | `ap_cpu_N.mem` → `ap_router` | AP RAM/GIC/RoS/MMIO 직접 decode |
| AP의 관리 접근 | `ap_router` → `host_ap_atu` → `system_router` | AP ATU aperture의 등록된 변환; 아래 예외 bridge 우선 |
| SI CL0 CPU | `si_cl0_cpu_0.mem` → `si_cl0_ni710ae_primary_nci.protected_target_socket` → `si_cl0_router` | CPU 접근에 inline APU 검사 |
| CL0의 외부 접근 | `si_cl0_router` → `host_si_atu` 또는 `host_smdexp2smd_atu` → `system_router` | 프로그래밍된 ATW에 한함 |
| SI CL1 CPU | `si_cl1_cpu_N.mem` → `si_cl1_router` | CL1 SRAM/GIC/UART/MHU; CL0 primary APU를 통과하지 않음 |
| Global SMD 접근 | `system_router` → `system_to_smd_nci` → `smd_router` | selector `0x2` 전체 aperture; 내부 hole은 SMD decode에서 종료 |
| PCIe GPEX DMA, 기본 SystemC MMU backend | `ap_gpex_0.bus_master` → `ap_smmu_lti00.upstream_socket` → `ap_router` | I/O translation 경로; global selector `0x1` 전체 구현과는 다름 |

`system_to_smd_nci`의 실제 `moduletype`은 `addrtr`이다. 이름에 NCI가 있어도
NI-710AE packet network 또는 APU를 내장한 인스턴스가 아니다.

QBox socket 명명은 transaction 방향으로 읽는다. CPU의 initiator는 router의
`target_socket`에 연결되고, 장치의 `target_socket`은 router의
`initiator_socket`에 연결된다. Lua의 `bind` 문자열만 보고 방향을 뒤집지 않는다.

## 3. 명시적 bridge와 공유 통신

주소는 byte address이고 `size`는 바이트 수다. `addrtr`은
`out = mapped_base_addr + (in - target_socket.address)`로 변환한다.
아래 bridge는 역방향 접근을 자동으로 만들지 않는다.

| Bridge 객체 | 입력 view / base / size | 출력 view / base |
| --- | --- | --- |
| `system_to_smd_nci` | system / `0x2000000000000` / `0x1000000000000` | smd / 동일 주소 |
| `system_to_ap_shared_bridge` | system / `0x0` / `0x200000` | ap / `0x0` |
| `system_to_ap_gic_bridge` | system / `0x20000000` / `0x08000000` | ap / `0x20000000` |
| `system_to_ap_flash_bridge` | system / `0x38000000` / `0x08000000` | ap / `0x38000000` |
| `ap_to_system_rse_carveout_bridge` | ap / `0xFFFE0000` / `0x20000` | system / `0xFFFE0000` |
| `ap_to_system_pfdi_monitor_mhu_bridge` | ap / `0x40110000` / `0x30000` | system / `0x400003B380000` |
| `ap_hipc_alias` | ap / `0xE0130000` / `0x80000` | ap / `0x00100000` |
| `si_cl1_hipc_bridge` | cl1 / `0xE0130000` / `0x80000` | ap / `0x00100000` |
| `si_cl0_rse_shared_bridge` | cl0 / `0x40000000` / `0x40000` | system / `0x4000040000000` |
| `si_cl0_to_si_cl1_scmi_bridge` | cl0 / `0x48000000` / `0x1000` | cl1 / `0x48000000` |
| `smd_ap_clN_ni710ae_fmu_alias` | smd / `0x20000D2000000 + N*0x100000` / `0x50000` | ap / `0x1D000000 + N*0x100000`, N=0..3 |

근거: [fabric Lua][fabric], [AP 최종 router 구성][ap],
[CL0 bridge 구성][cl0], [CL1 HIPC 구성][cl1], [addrtr 구현][addrtr].

예를 들어 CL1의 `0xE0130120`은 `ap_router`의 `0x00100120`으로 전달된다.
AP도 같은 HIPC alias로 해당 backing에 접근한다. CL0의 `0x48000000`은
CL1의 `si_cl1_scmi_shmem`에 연결되어 PFDI 공유 버퍼를 사용한다.

MHU `pair`와 `protocol="doorbell-bridge"`는 endpoint 사이의 알림 관계이고,
메모리 payload의 주소 변환과는 별도이다. AP↔RSE, RSE↔CL0, AP↔CL0/CL1,
CL0↔CL1 통신은 MHU register/IRQ 및 위 공유 버퍼 경로를 함께 보아야 한다.
IRQ signal binding은 메모리 bus transaction이 아니다.

### SI firmware staging과 실행 SRAM

| 용도 | QVP 객체 / base / size | backing 관계 |
| --- | --- | --- |
| Global CL0 SRAM window | `host_si_cl0_sram` / `0x4000120000000` / 16 MiB | 별도 `gs_memory`, 선택적 map file |
| CL0 실행 SRAM | `si_cl0_sram` / `0x120000000` / 8 MiB | 별도 `gs_memory`; `si_cl0_loader`가 image 적재 |
| Global CL1 SRAM window | `host_si_cl1_sram` / `0x4000140000000` / 16 MiB | 별도 `gs_memory`, 선택적 map file |
| CL1 실행 SRAM | `si_cl1_sram` / `0x140000000` / 8 MiB | 별도 `gs_memory`; `si_cl1_loader`가 image 적재 |

따라서 RSE가 global SRAM에 image를 기록했다는 사실만으로 SI CPU가 그
바이트를 fetch했다고 주장할 수 없다. CL0/CL1 loader 및 PPU release 연결은
있지만 이 네 SRAM 객체를 하나로 합치는 alias binding은 해당 Lua에 없다.
이는 reset/release sequencing과 end-to-end firmware 전달을 평가할 때
명시해야 하는 기능 모델 경계이다.

## 4. CMN-S3AE의 모델 범위

`si_cl0_cmn_cyprus`는 global `0x100000000`, size `0x40000000`에 연결된다.
이름에 CL0가 붙은 것은 CL0 firmware가 CMN을 설정하는 코드의 소유 위치이며,
hardware CMN이 SI 내부에 있다는 뜻이 아니다.

[CMN C++][cmn]은 24 XP topology 및 RN-SAM/HN-S/SBSX 등의 node 정보를
seed하고 sparse register storage의 read/write를 제공한다. 공개 socket은
`target_socket` 하나이며 downstream memory initiator가 없다. `b_transport`
는 delay를 사용하지 않고 DMI도 허용하지 않는다.

따라서 RN-SAM register 쓰기는 저장되지만 AP DRAM decode를 재구성하지 않는다.
AP CPU의 DRAM 경로는 `ap_router → host_ap_dram1/2`이다. 하드웨어의
CHI coherence, snoop/DVM 전달, HN-S cache, RN-SAM hashing에 따른 memory
분산, congestion/QoS/bandwidth를 이 모델로 검증할 수 없다.

[참조 RTL map 패치][rtl]는 mesh 6×4, HN-S/SBSX 순서와 hashing mask `0x7`을
설정한다. QVP의 discovery node 정보가 firmware를 만족하는 것과, 이 설정이
실제 트래픽 목적지를 바꾸는 것은 별개의 검증 항목이다.

## 5. NI-710AE 및 접근 제어

| 모델 | 주소 view | 데이터 경로 참여 |
| --- | --- | --- |
| `si_cl0_ni710ae_primary_nci`, topology=4 | cl0 `0x2A000000`, 64 KiB | CL0 CPU가 `protected_target_socket`을 통과; APU0 사용 |
| `si_cl0_ni710ae_secondary_nci`, topology=2 | cl0 `0x2A200000`, 64 KiB | 이 구성에서는 register target |
| `si_cl0_ni710ae_mhu_nci`, topology=1 | cl0 `0x2A300000`, 64 KiB | 이 구성에서는 register target |
| `zena_ni710ae_fmu` | AP cluster local FMU 및 SMD system-control/SMD windows | FMU fault/status 기능; 범용 NoC forwarding 아님 |

[APU C++][ni]는 request context, address region, security 및 read/write
permission을 검사하며 실패를 fault로 보고한다. DMI도 정책에 따라 검사하고
무효화한다. 다만 보호 대상은 실제 `protected_target_socket`에 연결된
initiator로 한정된다. CL0 loader는 CL0 router에 직접 연결되어 있고,
CL1 CPU, RSE global 접근, AP CPU 전체를 이 APU가 검사하지 않는다.

Hardware system-management NI APU의 reset 정책은 RSE만 허용하는 것이지만,
QVP CL0 primary APU의 reset owner는 `si_cl0` domain이고 trusted loader
허용 옵션도 있다. 이 두 정책은 대상 경로가 다르므로 혼동하면 안 된다.
`request_domain_id`는 QVP provenance 값으로 global 주소의 `[51:48]`
selector와 동일한 필드가 아니다.

## 6. ATU, decode 및 fidelity 경계

[ATU C++][atu]는 region start/end, enable, offset, security 조건을 검사하고
`physical = logical + offset`으로 변환한다. 비활성/미매핑/범위 초과 등의
실패를 기록한다. bridge와 달리 단순히 aperture가 존재한다고 통과하지
않으며, 실제 목적지는 firmware가 프로그래밍한 register 상태에 의존한다.

[Router C++][router]에서 priority 숫자가 작을수록 우선한다.
`relative_addresses=true`가 기본이며 장치에 offset을 전달한다. ATU/addrtr
입구는 `false`를 사용해 원래 주소를 유지한다. 예를 들어 AP PFDI bridge
priority 0은 같은 범위를 포함하는 AP ATU priority 10보다 우선하고,
AP HIPC alias는 DRAM 안의 주소를 별도 SRAM으로 돌린다.

| 검증 주제 | 현재 정적으로 확인한 범위 | 남은 경계 |
| --- | --- | --- |
| Domain 분리 | 별도 router와 제한된 bridge, SMD 전용 decode | 모든 hardware global aperture의 전면 연결 아님 |
| Address translation | RSE/AP/SI/SMDExp ATU 및 고정 bridge | 실제 boot의 window 값은 runtime register/trace 필요 |
| NI 보안 | CL0 CPU inline APU 및 request context | 모든 NoC port의 RSE-only reset policy 동등성 없음 |
| Memory 공유 | HIPC/SCMI/RSE-SI bridge | SI staging SRAM과 실행 SRAM은 별도 객체 |
| CMN | topology discovery와 register read/write | coherent data fabric 및 timing 미모델링 |
| I/O | 기본 SystemC MMU-720AE LTI/TBU DMA 연결 | global AP-through-TCU selector 전체 구현과 구분 |
| 시간/성능 | TLM 및 QEMU synchronization 설정 | hardware contention/latency/대역폭 판정 불가 |

후속 runtime 검증은 각 initiator에서 허용/거부 주소를 실제 접근하고,
ATU translation 및 APU fault, 상대 도메인의 payload 관측을 함께 수집해야
한다. 특히 CMN SAM 변경 전후 DRAM 전달과 SI global/local SRAM 동일성은
boot 성공으로 대체할 수 없는 항목이다.

[hw]: ../arm_zena_css_dev_guide/05-functional-blocks-in-zena-css.md
[fvp]: ../arm_zena_css_dev_guide/08-fixed-virtual-platform.md
[components]: ../../arm-zena-css/documentation/design/components.rst
[rtl]: ../../arm-zena-css/yocto/meta-zena-css-bsp/recipes-bsp/scp-firmware/files/fvp-rd-aspen/0089-prod-rdaspen-Use-Arm-RTL-memory-map.patch
[fabric]: ../../hsoc-stack/tools/qbox-platform/platforms/apollo/hw-block/fabric.lua
[ap]: ../../hsoc-stack/tools/qbox-platform/platforms/apollo/hw-block/ap_compute.lua
[cl0]: ../../hsoc-stack/tools/qbox-platform/platforms/apollo/hw-block/si_cl0.lua
[cl1]: ../../hsoc-stack/tools/qbox-platform/platforms/apollo/hw-block/si_cl1.lua
[cmn]: ../../hsoc-stack/tools/qbox-platform/systemc-components/host_cmn_cyprus/include/host_cmn_cyprus.h
[ni]: ../../hsoc-stack/tools/qbox-platform/systemc-components/host_ni710ae_nci/include/host_ni710ae_nci.h
[atu]: ../../hsoc-stack/tools/qbox-platform/systemc-components/rse_atu/include/rse_atu.h
[router]: ../../hsoc-stack/tools/qbox/systemc-components/router/include/router.h
[addrtr]: ../../hsoc-stack/tools/qbox/systemc-components/addrtr/include/addrtr.h
