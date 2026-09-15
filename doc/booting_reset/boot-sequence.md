# 부팅 구조와 순서

분석 기준은 [README](README.md)를 따른다. 이 문서의 순서 표는 의존 관계를
설명하며, QVP 실행 trace의 timestamp 순서를 재현한 것이 아니다.

## 1. Hardware와 참조 소프트웨어의 역할

[Hardware boot guide][hwboot] §6은 RSE를 trust root로 두며, RGM을
RSE·SI·Primary Compute에 걸친 공유 구성 요소로 설명한다. ESM 및 block
device controller는 CSS 외부 구성이다.

| 순서 | 주체 | Hardware / RD-Aspen reference 계약 |
| --- | --- | --- |
| 1 | RSE BL1_1 | Power-up의 첫 실행 요소. ROM에서 시작하여 critical RSE 초기화, OTP의 BL1_2 검증·SRAM 적재 |
| 2 | RSE BL1_2 | 나머지 RSE 및 boot device 초기화, RSE BL2 검증·적재·분기 |
| 3 | RSE BL2 | System management 초기화와 SI self-test. CFG2에서는 CL1 image를 먼저, CL0 image를 다음에 load/authenticate |
| 4 | RSE → CL0 | CL0 image가 준비되면 CL0 power-on/reset release |
| 5 | CL0 SCP-firmware | Primary Compute self-test 및 CMN-S3AE, GIC-720AE, peripheral 초기화. CFG2 CL1 power-on도 CL0가 수행 |
| 6 | RSE BL2 | AP BL2를 AP secure SRAM으로, RSE runtime을 RSE SRAM으로 적재. NI-710AE APU 설정 및 AP-ready 통지 |
| 7 | RSE / CL0 | RSE는 runtime 진입. CL0는 준비된 primary AP CPU reset 해제 |
| 8 | AP | TF-A BL2 → BL31 → BL32(OP-TEE) 초기화 → BL31 → BL33(U-Boot), boot manager 및 Linux |

Hardware guide는 CL0-only 기본 구조를 설명하고,
[reference boot_process.rst][refboot]의 CFG2 단계는 CL1을 추가한다.
CL1의 모든 초기화가 끝난 후에만 AP image loading이 시작된다는 완전 직렬
관계는 가정하지 않는다. AP release의 핵심 조건은 CL0의 관리 초기화와
RSE의 AP-ready handoff이다.

CL1은 Linux remoteproc이 처음 부팅하는 processor가 아니다.
[HIPC reference][hipc]에서는 독립 부팅된 CL1에 Linux가 `RPROC_DETACHED`
상태로 연결한다. Linux 실행 이전의 CL1 power/reset owner는 CL0이다.

Hardware BIST 요구와 FVP 구현도 구분한다. [safety_boot.rst][safety]는
Aspen FVP의 LBIST test controller 및 MBIST controller가 구현되지 않아
dummy 처리가 수행된다고 명시한다. BIST 관련 출력만으로 물리 검사 완료를
주장할 수 없다.

## 2. QVP 객체 생성과 최초 실행 상태

[Entrypoint][entry]는 `fabric.create`, RSE/AP/RoS/system-management 정의,
AP router rebind, CL0/CL1 정의 및 enable 순서로 플랫폼을 조합한다.
이는 **객체 생성 순서**이며 CPU들의 부팅 순서가 아니다.

| Domain | CPU / 초기 상태 | 실행 vector와 image |
| --- | --- | --- |
| RSE | `rse_cpu_pass.cpu_0`의 M55; `start_powered_off=false` | `init_svtor=init_nsvtor=0x11000000`; `rse-rom-image.img` ROM의 vector table 사용 |
| SI CL0 | 별도 QEMU instance, R82 1개; `start_in_reset=true`, `reset_power_on=true` | `rvbar=0x120000000`; `si_cl0_loader`가 `si0_ramfw.bin`을 동일 base에 적재 |
| SI CL1 | 별도 QEMU instance, R82 4개; 모두 `start_in_reset=true` | `rvbar=0x14000647c`; `si_cl1_loader`가 `zephyr-demos-cl1.bin`을 `0x140000000`에 적재 |
| AP | 별도 QEMU instance; 모든 CPU `start_in_reset=true`; secondary는 `start_powered_off=true` | `rvbar=0x00082000`; AP BL2 entry. CPU0 power-on이 최초 AP 실행 경로 |

근거: [RSE Lua][rse], [CL0 Lua][cl0] `define_loader_and_cpu`,
[CL1 Lua][cl1] `define_loader_and_cpus`, [AP Lua][ap] CPU 정의.
RSE의 `0x11000000`은 M-profile vector-table base이며 PC 자체가 아니다.
CL1 entry와 AP BL2 복원 offset은 고정 상수이므로 실제 firmware ELF와
일치하는지 별도 확인해야 한다. Hardware RVBAR register write가 곧바로
이 Lua `rvbar`를 갱신한다고 가정하지 않는다.

CL0/CL1/AP QEMU instance는 `managed_start_in_reset_release=true`를 사용한다.
[QemuCpu][cpu]의 release 경로는 QEMU thread에서 power state와 CPU reset을
처리하고 완료 event를 기다린다. 이것은 co-simulation 동기화 장치이며
물리 reset synchronizer/clock/power-good timing을 재현하는 계약은 아니다.

## 3. QVP power-on과 reset release 연결

| 단계 | 실제 QVP trigger와 연결 | 결과 |
| --- | --- | --- |
| CL0 준비 | RSE가 global CL0 PPU에 접근; core0 PPU `0x4000028040000` | `host_si_cl0_core0_ppu` power-on sequence 시작 |
| CL0 load/release | `power_on_load → si_cl0_loader.reset`, 이후 `power_on_reset → si_cl0_cpu_0.reset=false` | 실행 SRAM을 load하고 CL0 CPU 해제 |
| CL1 image 준비 | global cluster PPU `0x4000028810000`의 `host_si_cl1_clus_ppu.power_on_load` | `si_cl1_loader.reset` 실행. 이 객체 자체에는 CPU reset 출력이 연결되지 않음 |
| CL1 CPU 해제 | CL0 local core PPU `0x28840000 + N*0x100000`, N=0..3 | `si_cl1_coreN_ppu.power_on_reset → si_cl1_cpu_N.reset` |
| AP CPU0 준비 | CL0가 AP core0 PPU `0x141080000` power-on | `power_on_load → host_reset_ctrl.ap_power_reset → ap_cold_reset_fanout` |
| AP CPU release | AP per-core PPU `0x141080000 + cluster*0x4000000 + core*0x100000` | 활성 CPU의 `.reset=false`; CPU0 이외는 전역 load trigger 없음 |

`host_si_cl1_clus_ppu`의 global view와 `si_cl1_cluster_ppu`의 CL0-local view는
별도 객체다. Global cluster load trigger와 CL0-local core release를 구분한다.
AP cluster PPU도 core PPU와 별도이며, 현재 CPU reset은 core PPU에 연결된다.

[host_ppu C++][ppu]에서 ON 요청의 순서는 다음과 같다.

1. 설정되어 있으면 `power_on_load=true`를 출력한다.
2. load pulse 폭만큼 기다린 뒤 `power_on_load=false`를 출력한다.
3. load-to-reset delay 후 `power_on_reset=false`를 출력한다.
4. status delay 후 PWSR에 ON 완료 상태를 반영한다.

OFF 전환은 reset을 assert할 수 있다. PPU register는 `PWPR +0x0`,
`PWSR +0x8`, ON 상태는 `0x8`이다. CL0 및 AP CPU0 load 관련 Lua delay는
0 ns이고, CL0 PPU access latency fallback은 100 ns이다. 이 값은
hardware settling time이나 firmware 완료 시간으로 해석하지 않는다.

## 4. Image 적재와 boot handoff의 구현 차이

[Generic loader][loader]는 elaboration에서 파일을 적재하고,
`reset=true`에서도 적재 동작을 다시 실행한다. 즉 SI image는 PPU release
직전에만 처음 적재되는 구조가 아니라 사전 load 및 재-load가 가능한 구조다.

| 대상 | QVP 동작 | Hardware 계약과의 차이 |
| --- | --- | --- |
| RSE ROM/OTP/flash | host image를 backing에 준비하고 RSE firmware 실행 | provisioning/authentication 성공은 firmware trace와 실제 backend 검증 필요 |
| SI CL0/CL1 | host loader가 CPU 실행용 SRAM에 별도 binary 적재 | RSE가 인증하여 global SRAM에 기록한 바이트와 CPU fetch 바이트의 동일성은 자동 보장되지 않음 |
| AP BL2 | RSE handoff 경로 외에 `ap_bl2_reset_loader`가 ELF의 `.data` 일부 및 stack/BSS/xlat 영역 복원 | 전체 AP BL2를 flash에서 재인증·재적재하는 동작과 같지 않음 |
| AP HIPC/header SRAM | `host_ap_bl2_header_sram.reset` 포함, `init_mem=false` | reset 대상이어도 backing을 zero-clear하지 않음; HIPC buffer 보존 의도 |

Global SI SRAM은 `host_si_cl0_sram/host_si_cl1_sram` 각각 16 MiB,
실행 SRAM은 `si_cl0_sram/si_cl1_sram` 각각 8 MiB로 별도 생성된다.
자세한 backing 차이는 [fabric 문서](../fabric/fabric-routing.md)를 따른다.

AP reset loader는 [AP Lua][ap]의 `AP_BL2_RESET`에 따라 `AP_BL2_ELF`의
파일 offset `0x17000`에서 `0xF35` bytes를 AP `0x98000`에 복원한다.
Stack `0x98F40`, BSS `0x9A000`, translation table `0xA2000`을 초기화하고
SDS `0x50`에 reset syndrome `0x8`을 기록한다. 이것은 선택된 BL2 image와
강하게 결합된 구현이다.

## 5. CMN-S3AE와 NI-710AE의 boot 역할

| 항목 | Hardware / reference | QVP |
| --- | --- | --- |
| CMN 초기화 owner | CL0가 AP release 전에 CMN을 설정 | CL0가 `si_cl0_cmn_cyprus` GPV를 접근할 수 있음 |
| CMN 준비 상태 | coherent fabric/SAM 구성 후 AP memory 사용 | `host_cmn_cyprus`는 discovery node 및 sparse register storage; AP memory traffic은 직접 router 경로 |
| NI 보호 설정 | RSE가 boot 중 APU 설정, 초기 global 접근은 RSE만 허용 | CL0 primary NCI의 APU는 CL0 CPU 경로에 inline; reset owner는 CL0 domain |
| NI NCI 초기화 | 각 fabric node의 구성 | primary/secondary/MHU NCI topology register 모델 |
| Reset 후 재설정 | reset domain과 retention에 따라 firmware 재초기화 필요 | NCI 세 객체는 full fanout reset 대상, CMN/ATU/NI FMU는 같은 reset 연결이 없음 |

CMN 객체가 elaboration에서 register를 seed하는 것과 CL0 firmware가 CMN을
프로그램하는 것은 다른 단계다. 현재 모델에는 CMN-ready를 AP CPU release의
필수 hardware signal로 강제하는 연결이 없다. NI APU의 일부 구현을
시스템 전체 보안 gate와 동일하게 볼 수도 없다.

## 6. 순서 검증 시 필요한 runtime 증거

실행 검증에서는 image hash/ELF, RSE load·authentication 결과, CL0 PPU
load/release, CL0 CMN/NI setup, AP-ready MHU, AP CPU0 첫 PC,
CL1 core0 및 secondary 실행을 함께 수집해야 한다. UART 출력은 buffering과
도메인별 QEMU scheduling의 영향을 받으므로 콘솔 줄 순서만으로 hardware
handoff 완료 순서를 판정하지 않는다.

PFDI timeout은 reset propagation 시간이 아니라 firmware 감시 정책이다.
현재 [QVP timing include][timing]의 AP OoR/boot/online 기본값은
10 s / 180 s / 60 s, CL1은 1 s / 10 s / 500 ms이다. 실제 image 값은
BitBake override와 빌드 결과를 확인해야 하며, 과거 설정이나 FVP timeout을
현재 QVP에 그대로 적용하면 안 된다.

[hwboot]: ../arm_zena_css_dev_guide/06-boot-flow-of-zena-css.md
[refboot]: ../../arm-zena-css/documentation/design/boot_process.rst
[hipc]: ../../arm-zena-css/documentation/design/hipc.rst
[safety]: ../../arm-zena-css/documentation/design/safety_boot.rst
[entry]: ../../hsoc-stack/tools/qbox-platform/platforms/apollo/apollo-qvp.lua
[rse]: ../../hsoc-stack/tools/qbox-platform/platforms/apollo/hw-block/rse.lua
[cl0]: ../../hsoc-stack/tools/qbox-platform/platforms/apollo/hw-block/si_cl0.lua
[cl1]: ../../hsoc-stack/tools/qbox-platform/platforms/apollo/hw-block/si_cl1.lua
[ap]: ../../hsoc-stack/tools/qbox-platform/platforms/apollo/hw-block/ap_compute.lua
[cpu]: ../../hsoc-stack/tools/qbox/qemu-components/common/include/cpu.h
[ppu]: ../../hsoc-stack/tools/qbox-platform/systemc-components/host_ppu/include/host_ppu.h
[loader]: ../../hsoc-stack/tools/qbox/systemc-components/common/include/loader.h
[timing]: ../../hsoc-stack/yocto/meta-hsoc-bsp/conf/machine/include/apollo-qvp-qbox-timing.inc
