# Reset 구조, 순서와 영향 범위

기준 snapshot은 [README](README.md)를 따른다. 이 문서에서 assert는 QVP
bool signal의 `true`, deassert/release는 `false`이다. Hardware의 active-low
reset pin 이름과 signal 극성을 그대로 대응시키지 않는다.

## 1. Hardware reset 종류와 제어면

[Programmer's model][hwmap]은 RSE 내부 reset tree와 CSS RGM을 구분한다.

| Hardware 항목 | 계약 / 의미 | QVP 비교 포인트 |
| --- | --- | --- |
| RSE `nPORESETAON` | RESET_SYNDROME 등 AON register의 reset 기준 | 실행 중 full fanout이 모든 AON 상태를 POR로 만드는 것은 아님 |
| RSE cold / warm / CPU0 warm | reset source와 merge mask, retention 범위가 구분됨 | 별도의 전체 warm/cold tree가 구현되어 있지 않음 |
| RSE `SWRESET` | `SWRESETREQ` bit5 cold reset 요청; SWSYN bits31:24 | QVP는 SYSCTRL→Apollo full fanout pulse로 연결 |
| CSS RGM | global `0x20000D0010000`; syndrome/mask | RSE SYSCTRL과 별도 객체 및 주소 |
| AP standalone reset | AP만 재부팅하며 RSE·SI runtime 유지 | AP cold/system helper와 full Apollo fanout을 구분 |
| Per-core power cycle | PPU로 power/reset 및 release 제어 | QVP `host_ppu`에서 CPU reset bool 제어 |

Hardware RGM의 `RGM_CTRL +0x10`은 RO/reserved이므로 software reset
command register가 아니다. `RST_SYNDROME +0x20`은 EXP0 bit24,
RSEWARM bit9, RSECOLD bit8, EXTCOLD bit5를 구분한다. `RST_MASK +0x30`의
문서화된 enable은 EXP0 bit24이다.

QVP [zena_reset_ctrl][rgm]은 EXP0/RSECOLD/EXTCOLD syndrome subset을
모델링하고 RSEWARM bit9는 처리하지 않는다. RSE [rse_sysctrl][sysctrl]도
hardware의 모든 reset-source latch, mask merge, retention semantics를
구현한 것은 아니다. 특히 SYSCTRL reset callback은 register array를
초기화한 뒤 pending software syndrome을 복원한다.

## 2. Trigger → 실제 reset 대상

근거: [config.lua][config]의 reset helper들, [system_mgmt.lua][smd],
[RSE Lua][rse], [AP Lua][ap], [CL0 Lua][cl0].

| Trigger | QVP 경로 | 실제 범위 / 제한 |
| --- | --- | --- |
| RSE SYSCTRL `0x58021108`, bit5 | `rse_sysctrl.system_reset` → `apollo_system_reset_fanout.reset_in` | AP + RSE SYS/RSS subset + SI CL0/CL1 및 지정 주변장치 |
| AP NS watchdog WS1 | `host_reset_ctrl.ap_ns_watchdog_reset` → `ap_reset` → `ap_cold_reset_fanout` | AP 범위. AP NS WS1 IRQ 경로도 fanout |
| AP secure watchdog WS1 | `host_reset_ctrl.ap_s_watchdog_reset` → 같은 AP cold fanout | AP 범위 |
| AP CPU0 PPU power-on load pulse | `host_reset_ctrl.ap_power_reset` → AP cold fanout | AP QEMU reset 및 BL2 복원 준비 |
| AP SCMI MHU system-power 처리 | `host_ap_si_scmi_mhu_pbx.system_reset` → `ap_system_reset_bind_targets()` | 활성 AP core PPU + AP cold 대상. Apollo 전체 reset과 다름 |
| SI SSU safety status | `host_reset_ctrl.safety_fault_reset` → EXP0 mask가 enable일 때 `ap_reset` | AP cold fanout; syndrome은 mask와 별개로 latch |
| SI watchdog WS1 | `host_reset_ctrl.si_watchdog_reset` | controller의 `si_reset` 출력이 현재 Lua에서 미연결; SI CPU reset 완료 경로 아님 |
| RSE NS watchdog | WS0/WS1 → RSE CPU-pass signal 1/0 | `host_reset_ctrl.rse_watchdog_reset`에 연결되지 않음 |
| RSE secure watchdog | local MMIO 모델 | 현재 RSE Lua에 WS output binding 없음 |
| Optional runtime injection | `apollo_runtime_injection.system_reset` → full fanout | opt-in 시험용 경로; hardware reset pin 아님 |

`host_reset_ctrl` C++에 `si_reset`, `rse_reset`, request/ack socket이 있어도
실제 [system-management Lua][smd]에는 `ap_reset`만 reset 출력으로 연결되어
있다. 클래스의 capability와 현재 플랫폼 연결을 구분해야 한다.

## 3. AP cold reset과 AP standalone reset

`ap_cold_reset_bind_targets()`의 순서는 다음과 같다.

| 순서 | Target group | 동작 의미 |
| --- | --- | --- |
| 1 | `dma350_0/1`, `pinctrl_peri0/1` | 지정 SystemC 장치 reset |
| 2 | `ap_bl2_reset_loader`, `host_ap_bl2_header_sram` | BL2 일부 실행 상태 복원; header SRAM은 `init_mem=false`로 내용 보존 |
| 3 | `ap_reset_gpio.reset_in` | AP QEMU instance의 system reset 요청 |
| 4 | AP↔SI/RSE MHU endpoints | mailbox 상태 reset |
| 5 | SystemC MMU backend 선택 시 `ap_smmu_0` | MMU model reset |
| 6 | I2C/EEPROM, SSI, DW UART, I2S 및 optional fault injector | 명시된 주변장치 reset |

[reset_gpio][gpio]는 SystemC 요청을 QEMU `system_reset()`으로 전달하고,
QEMU reset signal을 `ap_cpu_reset_bind_targets(AP_NUM_CPUS)`의 CPU reset
pulse로 전달한다. 재진입 방지 상태와 상대측 완료 대기를 사용한다.
AP QEMU에 속한 장치 reset과 SystemC fanout 대상은 서로 다른 집합이다.

`ap_system_reset_bind_targets()`는 이 cold 목록 앞에 **활성 AP core PPU**의
reset을 추가한다. `apollo_system_reset_bind_targets()`는 다시 그 목록을
포함해 RSE/SI 대상으로 확장한다. `cold`라는 helper 이름이 hardware의 모든
cold reset retention 규칙을 뜻하지는 않는다.

[Reference AP standalone reset][refboot]은 다음 handoff를 요구한다.

1. AP Linux/U-Boot 요청이 TF-A PSCI를 거쳐 CL0 SCP에 전달된다.
2. CL0가 AP core PPU power cycle을 수행하고 RSE runtime에 BL2 reload를 요청한다.
3. RSE가 AP peripheral SRAM을 reset하고 secure flash에서 AP BL2를 다시 적재한다.
4. RSE가 CL0에 AP-ready를 통지하고 CL0가 AP를 power-on한다.
5. RSE와 SI runtime은 계속 실행되고 AP는 BL2부터 재부팅한다.

참조 문서는 이 standalone reset 지원을 **baremetal use case**로 한정한다.
QVP의 AP cold fanout, BL2 host 복원 loader, live RSE MHU가 존재한다는 사실만으로
이 전체 handoff가 현재 product image에서 검증됐다고 볼 수 없다.
일반 guest reboot와 RSE SYSCTRL 전체 reset도 서로 다른 시나리오이다.

## 4. Apollo full reset의 순서

[CL1 Lua][cl1]의 `finalize_reset_order()`가 최종 full fanout의 선두를 변경한다.
CL0/CL1 QEMU reset 항목을 원래 목록에서 제거한 뒤 다음 순서로 추가한다.

| 순서 | 대상 |
| --- | --- |
| 1 | `si_gic_multiview.reset` |
| 2 | `si_cl0_qemu_inst.reset` |
| 3 | `si_cl1_qemu_inst.reset` |
| 4 | `ap_rgic2lgic_messreg.reset` |
| 5 | 기존 나머지 목록: AP core PPU 및 AP cold 대상 |
| 6 | RSE SYSCTRL/watchdog/MHU, RSE↔SI MHU, SMD GPIO |
| 7 | 선택한 RSE crypto backend의 KMU/CC3XX, RSE accel, SYS/RSS fanout |
| 8 | CL0 host PPU, NI primary/secondary/MHU NCI, CL0 MHU |
| 9 | CL1 host/local PPU, CL1 MHU 및 CL0↔CL1 PFDI MHU |
| 10 | optional runtime-injection service reset |

이 순서는 SI GIC view 상태를 먼저 다루도록 명시한 **dispatch 목록**이다.
[reset_fanout][fanout]은 입력 변화를 queue에 넣고 1 ps 뒤
`async_write_vector()`로 전달한다. [MultiInitiatorSignalSocket][multi]는
각 level을 binding 순서대로 쓰고 level 사이에 delta-cycle을 기다린다.
중첩 fanout과 QEMU reset은 비동기로 진행하므로, 위 목록을 모든 장치의
reset 완료가 순차적으로 확인되는 hardware handshake로 해석하면 안 된다.

[QemuInstance][instance]의 `.reset=true`는 QEMU `system_reset()`을 요청하고
`.reset=false` 자체로 CPU power-on sequence를 수행하지 않는다. CPU별
`start_in_reset` 및 PPU release가 이후 실행 가능 상태를 결정한다.

## 5. RSE SYS/RSS와 AON 분리

| Fanout | 명시된 대상 | 현재 연결 |
| --- | --- | --- |
| `rse_sys_rss_reset_fanout` | M55 CPU, NVIC cold-reset wrapper, timer0/1/2, GPIO0/1 wrappers 및 GPIO; 선택 시 local QEMU CFI flash wrapper | Apollo full fanout에서 입력 연결 |
| `rse_aon_reset_fanout` | timer3; SMD counter mirror 미사용 시 local system counter | 객체는 생성되지만 현재 Apollo Lua에 입력 binding 없음 |

Timer3/AON이 SYS/RSS reset에서 빠져 있는 것은 소스에서 확인되지만,
완전한 hardware AON reset 진입 경로까지 구현되었다는 뜻은 아니다.
전역 CSS counter도 Apollo full fanout의 reset 대상이 아니다.

RSE SYSCTRL `SWRESETREQ`는 `{true,false}` pulse를 발생시키고 software
syndrome을 pending 값으로 보존한다. Hardware의 warm-source merge 및
CPU-only warm reset과 별도이다. RSE CPU reset은 ROM vector table로 돌아가는
CPU reset 동작이며, OTP/flash와 모든 peripheral state를 새 프로세스 상태로
재생성하는 것이 아니다.

## 6. 도메인별 reset/retention 비교

| Subsystem / 상태 | QVP full fanout의 명시적 처리 | 동등성 한계 |
| --- | --- | --- |
| RSE CPU, NVIC, timer0..2 | SYS/RSS fanout | warm/cold/AON source tree 전체 아님 |
| RSE timer3 / CSS counter | full fanout 대상 아님 | POR/clock restart와 구분 |
| SI CL0 | QEMU instance, host PPU, NCI 및 MHU reset | ROM/BIST 기반의 silicon reset sequence와 다름 |
| SI CL1 | QEMU instance, host/local PPU, MHU reset | CFG2 확장; hardware baseline에는 CL1 없음 |
| AP | PPU + QEMU reset bridge + 명시된 SystemC 장치 | AP-only 및 전체 reset에서 영향 범위 구분 필요 |
| CMN-S3AE GPV | `host_cmn_cyprus`에 reset input 없음 | constructor/elaboration seed와 runtime reset은 다름; SAM 저장값 자동 초기화 경로 없음 |
| NI primary/secondary/MHU NCI | 세 객체 `.reset` 연결 | reset register/APU policy 처리; 모든 NoC node의 reset 아님 |
| NI cluster/system-control/SMD FMU | `zena_ni710ae_fmu`에 reset signal input 없음 | NCI reset과 함께 FMU fault state가 초기화된다고 가정하지 않음 |
| RSE/AP/SI/SMDExp ATU | `rse_atu`에 reset signal input 없음 | constructor 초기화는 있으나 full fanout으로 translation register를 초기화하지 않음 |
| AP/SI RAM | 지정 loader/header 외 RAM 전체 clear 없음 | DRAM/SRAM retention이나 보안 erase를 hardware와 동등하다고 판정할 수 없음 |
| AP/CL1 HIPC backing | header SRAM reset 입력은 연결되지만 `init_mem=false`, 별도 load 항목 없음 | `gs_memory` reset에서 zero-clear하지 않음; protocol 재동기화는 별도 검증 |

근거: [CMN C++][cmn], [NI NCI C++][nci], [NI FMU C++][nifmu],
[ATU C++][atu], [gs_memory C++][memory], [reset 목록][config]. 위 표는 객체를 새로 생성하는 process
restart와 실행 중 reset을 구분한다. 새 QBox process가 성공적으로 부팅해도
기존 process 안의 반복 reset 후 register/IRQ/DMI 상태가 올바르다는 증거는 아니다.

## 7. 후속 검증 항목

| 시나리오 | 필요한 관측 | 현재 문서 판정 |
| --- | --- | --- |
| 최초 부팅 | RSE→CL0 release, AP-ready, AP/CL1 첫 PC와 각 secondary 실행 | 정적 연결 확인, runtime 미실행 |
| AP standalone reset | AP BL2 재실행, RSE/SI liveness 유지, 실제 RSE reload 통신 | runtime 미실행 |
| RSE SWRESET | full fanout dispatch, SI GIC/QEMU/PPU 순서, 재부팅 및 syndrome | runtime 미실행 |
| SI watchdog | controller syndrome과 미연결 `si_reset` 경계 | CPU reset 전파 미구현 경로로 기록 |
| AON reset | 실제 assert source, timer3/counter와 SYS/RSS 구분 | Lua 입력 경로 미연결 |
| CMN/ATU/NI FMU 반복 reset | reset 전후 register와 fault 상태, 재프로그래밍 영향 | full reset 초기화 경로 제한 |

실행 증거는 `build/qbox-apollo-qvp/` 아래에 binary/Lua/image hash,
reset source, 횟수, per-domain log, PPU/MHU/reset trace 및 PASS/FAIL/SKIP를
함께 남겨야 한다. 이 문서 작업에서는 실제 reset이나 fault를 주입하지 않았다.

[hwmap]: ../arm_zena_css_dev_guide/09-programmers-model-for-zena-css.md
[refboot]: ../../arm-zena-css/documentation/design/boot_process.rst
[config]: ../../hsoc-stack/tools/qbox-platform/platforms/apollo/hw-block/config.lua
[smd]: ../../hsoc-stack/tools/qbox-platform/platforms/apollo/hw-block/system_mgmt.lua
[rse]: ../../hsoc-stack/tools/qbox-platform/platforms/apollo/hw-block/rse.lua
[ap]: ../../hsoc-stack/tools/qbox-platform/platforms/apollo/hw-block/ap_compute.lua
[cl0]: ../../hsoc-stack/tools/qbox-platform/platforms/apollo/hw-block/si_cl0.lua
[cl1]: ../../hsoc-stack/tools/qbox-platform/platforms/apollo/hw-block/si_cl1.lua
[rgm]: ../../hsoc-stack/tools/qbox-platform/systemc-components/zena_reset_ctrl/include/zena_reset_ctrl.h
[sysctrl]: ../../hsoc-stack/tools/qbox-platform/systemc-components/rse_sysctrl/include/rse_sysctrl.h
[gpio]: ../../hsoc-stack/tools/qbox/qemu-components/reset_gpio/include/reset_gpio.h
[fanout]: ../../hsoc-stack/tools/qbox-platform/systemc-components/reset_fanout/include/reset_fanout.h
[multi]: ../../hsoc-stack/tools/qbox/systemc-components/common/include/ports/multiinitiator-signal-socket.h
[instance]: ../../hsoc-stack/tools/qbox/qemu-components/common/include/qemu-instance.h
[cmn]: ../../hsoc-stack/tools/qbox-platform/systemc-components/host_cmn_cyprus/include/host_cmn_cyprus.h
[nci]: ../../hsoc-stack/tools/qbox-platform/systemc-components/host_ni710ae_nci/include/host_ni710ae_nci.h
[nifmu]: ../../hsoc-stack/tools/qbox-platform/systemc-components/zena_ni710ae_fmu/include/zena_ni710ae_fmu.h
[atu]: ../../hsoc-stack/tools/qbox-platform/systemc-components/rse_atu/include/rse_atu.h
[memory]: ../../hsoc-stack/tools/qbox/systemc-components/gs_memory/include/gs_memory.h
