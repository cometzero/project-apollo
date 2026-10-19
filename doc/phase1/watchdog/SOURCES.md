# Apollo Watchdog SW Implementation Report — Source References

[본문](README.md) · [상세표](WATCHDOG-MAP.md)

<a id="hardware"></a>

## HW 계약 / register

| ID | 근거 | 확인 내용 |
|---|---|---|
| H1 | [Zena programmer’s model](../../../doc/arm_zena_css_dev_guide/09-programmers-model-for-zena-css.md) 102–106·1228–1229·1414–1418·1524–1526·1661·1788–1791행 | AP/SI 주소·IRQ, RSE NS/Secure/NMI 경로 |
| H2 | [Zena reset / RSE](../../../doc/arm_zena_css_dev_guide/09-programmers-model-for-zena-css.md) 4560–4584·14954–14968·16526–16557행 | EXP0RESETEN bit24, RSE PD_AON/SYS-RSS/PPC0, NSWDRSTREQEN |
| H3 | [Watchdog operation](../../../doc/corstone-reference-system-architecture/0255-Watchdog-operation.md), [WCS](../../../doc/corstone-reference-system-architecture/0260-WCS-Watchdog-Control-and-Status-register.md), [WOR](../../../doc/corstone-reference-system-architecture/0261-WOR-Watchdog-Offset-register.md), [WCV](../../../doc/corstone-reference-system-architecture/0262-WCV-Watchdog-Compare-Value-register.md), [WRR](../../../doc/corstone-reference-system-architecture/0264-WRR-Watchdog-Refresh-register.md) | timestamp 기반 두 watch period, refresh·status·compare의 architectural 의미 |
| H4 | [Zena core / SLOWCLK WDT](../../../doc/arm_zena_css_dev_guide/09-programmers-model-for-zena-css.md) 220·802·5555–5558·7146–7175·8828–8857행 | E_CPU_CSR +0x200..20C/+0xF24, SLOWCLK watchdog 0x5802E000 |

H3는 Arm Corstone 문서의 로컬 보관본이며 원문 URL을 각 파일에 포함한다. Zena의 power/reset/access 계약은 H2를 우선한다. QVP WCV write 제약은 architectural 의미와 별도로 M1에서 확인했다.


<a id="reference"></a>

## Arm design / FVP 비교

| ID | 근거 | 확인 내용 |
|---|---|---|
| F3 | [Validation scope](../../../arm-zena-css/documentation/design/validation.rst) 144–146행 | watchdog validation의 장치·driver·filesystem 접근 범위 |
| F4 | [FVP base](../../../arm-zena-css/yocto/meta-zena-css-bsp/conf/machine/include/fvp/fvp.inc) 26–98행, [Cfg2 machine](../../../arm-zena-css/yocto/meta-zena-css-bsp/conf/machine/include/fvp/fvp-rd-aspen-cfg2.inc) 14–20행 | DISABLE_GATING parameter와 Cfg2 executable; watchdog clock/reset override 미발견 |

FVP 설정값과 실행 frequency·waveform은 구분한다.


<a id="platform"></a>

## Platform 조립 / CPU / IRQ / reset

| ID | 근거 | 확인 내용 |
|---|---|---|
| P1 | [canonical entry](../../../hsoc-stack/tools/qbox-platform/platforms/apollo/apollo-qvp-saturn-v.lua), [full profile](../../../hsoc-stack/tools/qbox-platform/platforms/apollo/vp/profiles/full-system.lua), [descriptor helper](../../../scripts/test/apollo_lua_descriptor.py) 244–250행 | 선택된 full-system descriptor의 watchdog 5개 평가 |
| P2 | [AP watchdog](../../../hsoc-stack/tools/qbox-platform/platforms/apollo/soc/hw-block/ap_compute/system.lua) 41–77·117–138·180–199행, [AP router](../../../hsoc-stack/tools/qbox-platform/platforms/apollo/soc/hw-block/ap_compute/interconnect.lua) 115–126·192–198행 | AP NS/S 125MHz; NS WS1 fanout; 최종 ap_router binding |
| P3 | [SI CL0 watchdog](../../../hsoc-stack/tools/qbox-platform/platforms/apollo/soc/hw-block/si_cl0/system.lua) 1–14·41–43·154–174행 | CL0 125MHz, WS0 INTID37, WS1 controller input |
| P4 | [RSE watchdog](../../../hsoc-stack/tools/qbox-platform/platforms/apollo/soc/hw-block/rse/system.lua) 43–100·287–329행, [RSE routing](../../../hsoc-stack/tools/qbox-platform/platforms/apollo/soc/hw-block/rse/interconnect.lua) 118–148행, [PPC filters](../../../hsoc-stack/tools/qbox-platform/platforms/apollo/soc/hw-block/rse/security.lua) 310–350행 | NS/S 32MHz; NS NVIC1/0; S outputs unbound; timer PPC filter와 구분 |
| P5 | [Reset controller bind](../../../hsoc-stack/tools/qbox-platform/platforms/apollo/soc/hw-block/system_mgmt/system.lua) 46–62행, [Reset fanouts](../../../hsoc-stack/tools/qbox-platform/platforms/apollo/soc/hw-block/fabric/reset.lua) 13–38·72–143행 | ap_reset만 output bind; AP WD clear가 reset_gpio보다 앞; 전체 reset scope |
| P6 | [AP reset adapters](../../../hsoc-stack/tools/qbox-platform/platforms/apollo/soc/hw-block/ap_compute/system.lua) 379–410행, [VP reset](../../../hsoc-stack/tools/qbox-platform/platforms/apollo/vp/reset.lua) 12–18·38–45행, [AP-only delta](../../../hsoc-stack/tools/qbox-platform/platforms/apollo/vp/profiles/linux-direct.lua) 46–59행 | loader/reset_gpio chain, linux-direct의 SI recovery 제거 |
| P7 | [CPU0 PPU](../../../hsoc-stack/tools/qbox-platform/platforms/apollo/soc/hw-block/si_cl0/power.lua) 154–205·229–240행 | power-on sequencing, AP CPU0 power-on ordering |
| P8 | [AP CPU defaults](../../../hsoc-stack/tools/qbox-platform/platforms/apollo/vp/options/execution.lua) 14–21행, [AP CPU](../../../hsoc-stack/tools/qbox-platform/platforms/apollo/soc/hw-block/ap_compute/cpu.lua) 17–26행, [CL0 CPU](../../../hsoc-stack/tools/qbox-platform/platforms/apollo/soc/hw-block/si_cl0/cpu.lua) 19행, [CL1 CPU](../../../hsoc-stack/tools/qbox-platform/platforms/apollo/soc/hw-block/si_cl1/cpu.lua) 29행, [RSE CPU](../../../hsoc-stack/tools/qbox-platform/platforms/apollo/soc/hw-block/rse/cpu.lua) 23–30행 | full defaults와 CPU type; CPU별 Generic Timer와 공유 WD 구분 |

<a id="models"></a>

## QBox / SystemC 구현

| ID | 근거 | 확인 내용 |
|---|---|---|
| M1 | [zena_watchdog](../../../hsoc-stack/tools/qbox-platform/systemc-components/zena_watchdog/include/zena_watchdog.h) 23–35·49–149·151–223·231–270·284–326행 | 48-bit WOR, sc_time clock, SC_THREAD, WCV 저장만, reset/generation, 4KiB/32bit/DMI 제약 |
| M2 | [QEMU MMIO initiator](../../../hsoc-stack/tools/qbox/qemu-components/common/include/ports/initiator.h) 660–758행, [QEMU target signal](../../../hsoc-stack/tools/qbox/qemu-components/common/include/ports/qemu-target-signal-socket.h) 28–50행 | 정상 MMIO의 run_on_sysc, QEMU lock 해제/획득, GPIO callback |
| M3 | [signal_fanout](../../../hsoc-stack/tools/qbox-platform/systemc-components/signal_fanout/include/signal_fanout.h) 15–45행, [GIC wrapper](../../../hsoc-stack/tools/qbox/qemu-components/irq-ctrl/arm_gicv3/include/arm_gicv3.h) 206–226행 | queued fanout, SPI/PPI 번호와 CPU IRQ/FIQ |
| M4 | [zena_reset_ctrl](../../../hsoc-stack/tools/qbox-platform/systemc-components/zena_reset_ctrl/include/zena_reset_ctrl.h) 215–281행, [reset_fanout](../../../hsoc-stack/tools/qbox-platform/systemc-components/reset_fanout/include/reset_fanout.h) 52–72행, [reset_gpio](../../../hsoc-stack/tools/qbox/qemu-components/reset_gpio/include/reset_gpio.h) 46–95행 | AP aggregate, SI mask bit24, RSE reset capability, 1ps fanout ordering와 QEMU reset handshake |
| M5 | [unused SBSA wrapper](../../../hsoc-stack/tools/qbox-platform/qemu-components/sbsa_gwdt/include/sbsa_gwdt.h) 19–56행, [QEMU SBSA](../../../hsoc-stack/tools/qemu/hw/watchdog/sbsa_gwdt.c) 99–123·193–219행, [QEMU CMSDK](../../../hsoc-stack/tools/qemu/hw/watchdog/cmsdk-apb-watchdog.c) 183–244행 | 사용 가능한 다른 backend; 현재 Apollo의 활성 WD 구현이 아님 |

<a id="linux"></a>

## AP Linux

| ID | 근거 | 확인 내용 |
|---|---|---|
| L1 | [AP DTS](../../../hsoc-stack/components/primary_compute/linux/arch/arm64/boot/dts/hsoc/apollo-qvp-saturn-v.dts) 8행, [base DTS](../../../hsoc-stack/components/primary_compute/linux/arch/arm64/boot/dts/hsoc/apollo.dtsi) 718–723행, [kernel fragment](../../../hsoc-stack/yocto/meta-hsoc-bsp/recipes-kernel/linux/apollo-kmeta/bsp/arm-platforms-extra/apollo-qvp.cfg) 10행 | arm,sbsa-gwdt, 두 frame, GIC_SPI50, built-in driver 선택 |
| L2 | [sbsa_gwdt driver](../../../hsoc-stack/components/primary_compute/linux/drivers/watchdog/sbsa_gwdt.c) 101–118·153–169·199–272·306–397행 | action0/1, WOR 환산, WRR ping, CNTFRQ/timeleft, optional panic ISR, probe는 start 아님 |
| L3 | [watchdog core](../../../hsoc-stack/components/primary_compute/linux/drivers/watchdog/watchdog_dev.c) 795–815·864–895·942–975행 | open/start, ioctl KEEPALIVE, magic-close/nowayout와 close 동작 |
| L4 | [guest diagnostics](../../../scripts/autosd_demo/watchdog_guest.py) 31–66·149–180행 | inactive timeleft 회피, systemd policy 조회, FD 유지한 feeding 중단의 시험 설계 |

<a id="ap-firmware"></a>

## AP TF-A / U-Boot / OP-TEE

| ID | 근거 | 확인 내용 |
|---|---|---|
| A1 | [platform def](../../../hsoc-stack/components/primary_compute/trusted-firmware-a/plat/arm/board/automotive_rd/platform/apollo_qvp/include/platform_def.h) 178–180행, [platform hooks](../../../hsoc-stack/components/primary_compute/trusted-firmware-a/plat/arm/board/automotive_rd/platform/apollo_qvp/apollo_qvp_plat.c) 44–51행, [platform build](../../../hsoc-stack/components/primary_compute/trusted-firmware-a/plat/arm/board/automotive_rd/platform/apollo_qvp/platform.mk) 27·50행 | 100ms secure helper; NEED_BL1=0 / RESET_TO_BL2=1 |
| A2 | [BL1 callers](../../../hsoc-stack/components/primary_compute/trusted-firmware-a/plat/arm/common/arm_bl1_setup.c) 80–82·258–260행, [SBSA helper](../../../hsoc-stack/components/primary_compute/trusted-firmware-a/drivers/arm/sbsa/sbsa.c) 21–47행, [error handler](../../../hsoc-stack/components/primary_compute/trusted-firmware-a/plat/arm/board/automotive_rd/platform/apollo_qvp/apollo_qvp_err.c) 13–21행 | normal BL1 소비와 Apollo 구분; error helper의 실제 control WCS write |
| A3 | [U-Boot config](../../../hsoc-stack/components/primary_compute/u-boot/configs/apollo_qvp_defconfig) 1–36행, [OP-TEE platform](../../../hsoc-stack/components/primary_compute/optee_os/core/arch/arm/plat-automotive_rd/conf.mk) 1–40행 | Apollo 명시적 WDT 선택/소비 경로 미확인; 공통 driver capability와 구분 |

<a id="scp"></a>

## SI CL0 / AP recovery

| ID | 근거 | 확인 내용 |
|---|---|---|
| S1 | [IRQ number](../../../hsoc-stack/components/system_mgmt/scp-firmware/product/automotive-rd/apollo-qvp/si0_ramfw/include/si0_irq.h) 31행, [policy](../../../hsoc-stack/components/system_mgmt/scp-firmware/product/automotive-rd/apollo-qvp/si0_ramfw/config_si0_platform.c) 29–46행, [ISR / rearm](../../../hsoc-stack/components/system_mgmt/scp-firmware/product/automotive-rd/apollo-qvp/module/si0_platform/src/mod_si0_platform.c) 361–433·467–540·866–870행 | IRQ321 mask/event, 재진입 방지, rearm100ms / poll10ms |
| S2 | [power state machine](../../../hsoc-stack/components/system_mgmt/scp-firmware/product/automotive-rd/apollo-qvp/module/si0_platform/src/mod_si0_platform.c) 301–344·876–946·1015–1069·1093–1116·1189–1227행 | 모든 core/cluster OFF→reload→context/mailbox→CPU0 ON; 전체30s; 실패 시 OFF/mask 유지 |
| S3 | [RSE async reload](../../../hsoc-stack/components/system_mgmt/scp-firmware/product/automotive-rd/apollo-qvp/module/si0_platform/src/platform_rse.c) 88–164행 | 10ms alarm,10s deadline, notify/ACK timestamp·generation |
| S4 | [RSE SCMI handler](../../../hsoc-stack/components/system_mgmt/trusted-firmware-m/platform/ext/target/arm/rse/automotive_rd/apollo-qvp/scmi/scmi_hal.c) 338–346행, [BL2 runtime load](../../../hsoc-stack/components/system_mgmt/trusted-firmware-m/platform/ext/target/arm/rse/automotive_rd/apollo-qvp/bootloader/rse_image_loader/src/rse_image_load_util.c) 1011–1058·1071–1117행 | BL2 load/decrypt/hash/signature 성공 후 ACK; RSE reboot와 구분 |

<a id="rse"></a>

## RSE TF-M

| ID | 근거 | 확인 내용 |
|---|---|---|
| R1 | [RSE addresses](../../../hsoc-stack/components/system_mgmt/trusted-firmware-m/platform/ext/target/arm/rse/common/partition/platform_base_address.h) 71–72·141–144행, [device config](../../../hsoc-stack/components/system_mgmt/trusted-firmware-m/platform/ext/target/arm/rse/common/device/config/device_cfg.h) 118–119행, [device definition](../../../hsoc-stack/components/system_mgmt/trusted-firmware-m/platform/ext/target/arm/rse/common/device/source/device_definition.c) 415–426행 | timestamp S/NS와 CMSDK SLOWCLK의 별도 주소·device 정의 |
| R2 | [startup](../../../hsoc-stack/components/system_mgmt/trusted-firmware-m/platform/ext/target/arm/rse/common/device/source/startup_rse.c) 87–88·175–176행, [IRQ enum](../../../hsoc-stack/components/system_mgmt/trusted-firmware-m/platform/ext/target/arm/rse/common/device/include/platform_irq.h) 33–36행 | NS watchdog reset_req/IRQ 기본 weak handlers; NVIC0/1 |
| R3 | [SAM config](../../../hsoc-stack/components/system_mgmt/trusted-firmware-m/platform/ext/target/arm/rse/common/rse_sam_config.c) 70–77·145–152·289–301행, [SAM NMI](../../../hsoc-stack/components/system_mgmt/trusted-firmware-m/platform/ext/target/arm/rse/common/sam_interrupts.c) 20–23행, [SAM init](../../../hsoc-stack/components/system_mgmt/trusted-firmware-m/platform/ext/target/arm/rse/common/tfm_hal_platform.c) 109행 | SAM 자체 watchdog·NMI/attack 대응 SW 정책. timestamp WD 출력 연결 또는 SAM runtime expiry 증거가 아님 |
| R4 | [RSE Lua](../../../hsoc-stack/tools/qbox-platform/platforms/apollo/soc/hw-block/rse/system.lua) 43–100·287–329행, [RSE console](../../../hsoc-stack/tools/qbox-platform/platforms/apollo/vp/rse/console.lua) | Secure WD output 미연결, local reset scope, host UART IRQ0 다중 bind 경계 |

<a id="validation"></a>

## Existing Verification Tools

| ID | 근거 | 확인 내용 |
|---|---|---|
| V1 | [watchdog model test](../../../hsoc-stack/tools/qbox-platform/tests/components/zena_watchdog/zena_watchdog-tests.cc) 110–200행 | 기존 시험 소스: 두 stage·WRR·WCV·disable·reset. 실행 결과는 본문 Chapter 5에 기록 |
| V2 | [AP power ordering test](../../../hsoc-stack/tools/qbox-platform/tests/components/zena_reset_ctrl/ap_watchdog_power_sequence-tests.cc) 69–143행 | 기존 시험 소스: 두 cycle의 WD clear→CPU release. sink 기반 test이며 guest reboot 증거 아님 |
| V3 | [OEQA device check](../../../hsoc-stack/yocto/meta-hsoc-auto-solutions/lib/oeqa/runtime/cases/test_63_linux_fvp_devices.py) 183–186행, [WD04 evidence](../../../scripts/autosd_dashboard/watchdog_scenarios.py) 43–58·100–170행 | 장치 확인과 full-system expiry/recovery 검증 기준 구분; 실행 결과는 본문 Chapter 5에 기록 |

<a id="zephyr-watchdog"></a>

## Zephyr HW Watchdog

| 소스 | 반영 내용 |
|---|---|
| [Watchdog API](../../../hsoc-stack/components/system_mgmt/zephyrproject/zephyr/include/zephyr/drivers/watchdog.h) | timeout window·설치 순서·setup/feed/disable·reset flags |
| [CMSDK driver](../../../hsoc-stack/components/system_mgmt/zephyrproject/zephyr/drivers/watchdog/wdt_cmsdk_apb.c) | IP별 register·driver operations; Apollo Generic Watchdog 선택과 구분 |
| [CL1 board](../../../hsoc-stack/components/system_mgmt/zephyrproject/zephyr_hsoc_src/boards/hsoc/apollo_qvp_safety_island_c1/apollo_qvp_safety_island_c1.dts) | 전용 watchdog node 없음 |
| [CL1 QVP hardware](../../../hsoc-stack/tools/qbox-platform/platforms/apollo/soc/hw-block/si_cl1/system.lua) | 전용 HW watchdog instance 없음 |

<a id="tfm-watchdog"></a>

## TF-M HW Watchdog Driver

| 소스 | 반영 내용 |
|---|---|
| [CMSDK driver](../../../hsoc-stack/components/system_mgmt/trusted-firmware-m/platform/ext/target/arm/drivers/watchdog/arm_watchdog_drv.c) | init·lock·enable·LOAD feed·INTCLR·VALUE 동작 |
| [Driver API](../../../hsoc-stack/components/system_mgmt/trusted-firmware-m/platform/ext/target/arm/drivers/watchdog/arm_watchdog_drv.h) | timeout·상태·오류 반환 규약 |
| [RSE device definition](../../../hsoc-stack/components/system_mgmt/trusted-firmware-m/platform/ext/target/arm/rse/common/device/source/device_definition.c) | SLOWCLK_WATCHDOG_DEV_S 정의 |
| [SAM configuration](../../../hsoc-stack/components/system_mgmt/trusted-firmware-m/platform/ext/target/arm/rse/common/rse_sam_config.c) | NMI response counter 0xFF·watchdog cold-reset 정책 |
