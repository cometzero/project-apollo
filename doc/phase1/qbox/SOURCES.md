# QVP Architecture — 조사 근거와 검증 범위

**조사일: 2026-10-16.** Arm 설계 문서·원본 도면을 읽고 현재 Lua의 최종 composition, C++ wrapper/model, QEMU backend, launcher를 교차 확인했다. 디렉터리에 파일이 있다는 사실만으로 active model을 판정하지 않았다.

| 저장소 | 조사 시 HEAD |
|---|---|
| Workspace root | `a37dcba0d32d` |
| `arm-zena-css` | `bf34d9e71f67` |
| `hsoc-stack/tools/qbox` | `b8a0499359ba` |
| `hsoc-stack/tools/qbox-platform` | `17ac742e2257` |
| `hsoc-stack/tools/qemu` | `2d83203dc366` |

위 저장소의 tracked 파일 변경은 없었다. 현재 [local.conf](../../../build/conf/local.conf)의 `MACHINE=apollo-qvp`, `RD_ASPEN_VARIANT=cfg2`, `PC_CPUS_COUNT_DEFAULT=4`, `TMPDIR=tmp_baremetal`을 확인했다. 이 값은 파일의 설정이며 BitBake 최종 변수 평가나 실행 중인 provider의 상태를 새로 확인한 결과는 아니다.

Codebase index는 관계 탐색에 활용했다. Apollo platform index는 2026-09-30 기준이고 최신 Lua 경로 일부가 미포함되어 있어, 최종 근거는 아래 직접 소스에 두었다.

<a id="s1"></a>
## S1. Arm 참조 구조와 FVP 비교

| 읽은 근거 | 본문에 반영한 내용 |
|---|---|
| [design/components.rst](../../../arm-zena-css/documentation/design/components.rst) | RSE/SMB/SI 책임, Cfg1·Cfg2, SCP, GIC multiple views |
| [design/boot_process.rst](../../../arm-zena-css/documentation/design/boot_process.rst) | RSE-first boot, 이미지 저장 매체, Chain of Trust, handoff |
| [System Block Diagram](../../../arm-zena-css/documentation/images/aspen_compute_complex.png) | Primary Compute와 System Management의 분리 |
| [System Management Block](../../../arm-zena-css/documentation/images/aspen_system_management_block.png) | RSE·SI·interconnect의 연결 |
| [RSE-oriented Boot Flow](../../../arm-zena-css/documentation/images/rse_oriented_boot_flow.png) | 인증/적재, program flow, power/reset의 화살표 의미 구분 |
| [Zena CSS 개발 가이드 8장](../../arm_zena_css_dev_guide/08-fixed-virtual-platform.md) | FVP Cfg1/2, CL1 확장 범위, RoS와 CSS 경계, 모델링 제외 IP |
| [FVP machine config](../../../arm-zena-css/yocto/meta-zena-css-bsp/conf/machine/fvp-rd-aspen.conf) | 변형·CPU 수·이미지 입력의 참조 설정 |

FVP 자체도 모든 Zena CSS IP를 모델링하지 않는다. 개발 가이드에는 CoreSight SoC-600/STM-500/SDC-600/ELA-600 제외가 명시되어 있다. 비교표의 참조 IP 이름을 “모든 기능의 완전한 구현”으로 읽지 않는다.

일반 개념은 [Arm Fast Models/FVP 안내](https://learn.arm.com/install-guides/fm_fvp/), [Fast Models User Guide의 glossary·timing 설명](https://documentation-service.arm.com/static/5f48df7d6e73485d721ea02e), [QEMU system emulation 개요](https://www.qemu.org/docs/master/system/introduction.html), [TCG translator 설계](https://www.qemu.org/docs/master/devel/tcg.html)를 확인했다. QEMU 최신 문서는 개념 설명에만 사용하고 Apollo fork의 구체 경로는 현재 checkout을 따랐다.

<a id="s2"></a>
## S2. QBox 생성·libqemu 경계

| 소스 | 확인 지점 |
|---|---|
| [platforms/src/main.cc](../../../hsoc-stack/tools/qbox/platforms/src/main.cc) | `sc_main`: broker → ArgParser → platform → `sc_start` |
| [argparser.h](../../../hsoc-stack/tools/qbox/systemc-components/common/include/argparser.h), [luautils.cc](../../../hsoc-stack/tools/qbox/systemc-components/common/src/luautils.cc) | `-l`/`-p`, Lua global table → CCI |
| [module_factory_container.h](../../../hsoc-stack/tools/qbox/systemc-components/common/include/module_factory_container.h) | `ModulesConstruct`, dependency/priority, constructor와 `name_bind` |
| [qemu-instance.h](../../../hsoc-stack/tools/qbox/qemu-components/common/include/qemu-instance.h) | `-M none -m 0`, QEMU arguments, sync 정책, lifecycle callback |
| [libqemu-cxx.cc](../../../hsoc-stack/tools/qbox/qemu-components/common/src/libqemu-cxx/libqemu-cxx.cc), [dynlib_loader.cc](../../../hsoc-stack/tools/qbox/systemc-components/common/src/dynlib_loader.cc) | `LibQemu::init`, export API, 추가 instance의 임시 library 사본 |
| [device.h](../../../hsoc-stack/tools/qbox/qemu-components/common/include/device.h), [cpu.h](../../../hsoc-stack/tools/qbox/qemu-components/common/include/cpu.h) | QOM 생성·realize, CPU memory property, reset/soft-stop |
| [qemu/libqemu.c](../../../hsoc-stack/tools/qemu/libqemu/libqemu.c) | `libqemu_init`, `qemu-iothread`, `qemu_init`/main loop |

<a id="s3"></a>
## S3. TLM·DMI·주소 변환

| 소스 | 확인 지점 |
|---|---|
| [ports/initiator.h](../../../hsoc-stack/tools/qbox/qemu-components/common/include/ports/initiator.h) | `init_payload` 133행, DMI hint 448행, `do_regular_access` 660행, callback 790행, invalidation 944행 이후 |
| [ports/target.h](../../../hsoc-stack/tools/qbox/qemu-components/common/include/ports/target.h) | `b_transport`, QEMU BQL, AddressSpace, 미구현 `nb_transport_fw`, debug 재사용 |
| [runonsysc.h](../../../hsoc-stack/tools/qbox/systemc-components/common/include/runonsysc.h) | queue/async event/future, SystemC thread의 job 처리 |
| [router.h](../../../hsoc-stack/tools/qbox/systemc-components/router/include/router.h) | 주소 decode·offset 복원, DMI range clamp |
| [gs_memory.h](../../../hsoc-stack/tools/qbox/systemc-components/gs_memory/include/gs_memory.h), [dmi-manager.h](../../../hsoc-stack/tools/qbox/qemu-components/common/include/dmi-manager.h) | host pointer grant, RAM alias, read-only 접근 |
| [rse_atu.h](../../../hsoc-stack/tools/qbox-platform/systemc-components/rse_atu/include/rse_atu.h), [strata_flash_j3.h](../../../hsoc-stack/tools/qbox-platform/systemc-components/strata_flash_j3/include/strata_flash_j3.h) | translation/enable 조건, flash mode/range, invalidation |
| [global_peripheral_initiator.h](../../../hsoc-stack/tools/qbox/qemu-components/global_peripheral_initiator/include/global_peripheral_initiator.h) | DMA master의 외부 TLM 연결; 비어 있는 async/TLB hook 경계 |

<a id="s4"></a>
## S4. 최종 Lua composition

| 소스 | 확인 지점 |
|---|---|
| [apollo-qvp-saturn-v.lua](../../../hsoc-stack/tools/qbox-platform/platforms/apollo/apollo-qvp-saturn-v.lua), [full-system.lua](../../../hsoc-stack/tools/qbox-platform/platforms/apollo/vp/profiles/full-system.lua) | canonical entry, 순차적인 최종 연결 |
| [vp/composition.lua](../../../hsoc-stack/tools/qbox-platform/platforms/apollo/vp/composition.lua) | SoC 이전 configure와 이후 apply |
| [soc/apollo.lua](../../../hsoc-stack/tools/qbox-platform/platforms/apollo/soc/apollo.lua), [soc/config.lua](../../../hsoc-stack/tools/qbox-platform/platforms/apollo/soc/config.lua) | standalone API, domain assembly, 16-PE 기본값 |
| [execution.lua](../../../hsoc-stack/tools/qbox-platform/platforms/apollo/vp/options/execution.lua), [models.lua](../../../hsoc-stack/tools/qbox-platform/platforms/apollo/vp/options/models.lua) | host 기본 4 PE, AP enable, DMI/flash/crypto 선택 |
| [board/saturn-v.lua](../../../hsoc-stack/tools/qbox-platform/platforms/apollo/board/saturn-v.lua) | AP/SI board population, 실제 회로 일치도 `UNVERIFIED` |
| [vp/backends/audio.lua](../../../hsoc-stack/tools/qbox-platform/platforms/apollo/vp/backends/audio.lua) | 초기 AP SystemC DMA/I2S를 QEMU wrapper로 교체, native peer·trigger 연결 |
| [runner preset](../../../scripts/run/run_qbox_apollo_fvp_full.py), [RSE security.lua](../../../hsoc-stack/tools/qbox-platform/platforms/apollo/soc/hw-block/rse/security.lua) | 기본 performance preset → native CC3XX, 최종 `qemu_cc3xx` 선택 |

<a id="s5"></a>
## S5. 모델과 실제 연결

[MODEL-MAP.md](MODEL-MAP.md)에 대표 24개 model과 구현 소스를 연결했다. 특히 아래 경로로 “존재하는 모델”과 “현재 선택된 모델”을 구분했다.

| 경로 | 확인 지점 |
|---|---|
| [ap_compute/system.lua](../../../hsoc-stack/tools/qbox-platform/platforms/apollo/soc/hw-block/ap_compute/system.lua) | GIC 구성, `systemc-mmu720ae` → `smmuv3`/`smmuv3_tbu` |
| [ros/dma.lua](../../../hsoc-stack/tools/qbox-platform/platforms/apollo/soc/hw-block/ros/dma.lua), [rse/io_peri.lua](../../../hsoc-stack/tools/qbox-platform/platforms/apollo/soc/hw-block/rse/io_peri.lua) | AP 초기 descriptor와 RSE SystemC DMA |
| [qemu_dma350.h](../../../hsoc-stack/tools/qbox-platform/qemu-components/qemu_dma350/include/qemu_dma350.h), [qemu_dw_apb_i2s.h](../../../hsoc-stack/tools/qbox-platform/qemu-components/qemu_dw_apb_i2s/include/qemu_dw_apb_i2s.h) | wrapper·QOM·socket, 동일 instance의 native GPIO req/ACK |
| [arm-dma350.c](../../../hsoc-stack/tools/qemu/hw/dma/arm-dma350.c), [dw-apb-i2s.c](../../../hsoc-stack/tools/qemu/hw/audio/dw-apb-i2s.c) | QEMU device 상태기계·DMA memory access·frame timer |
| [mhu320ae.h](../../../hsoc-stack/tools/qbox-platform/systemc-components/mhu320ae/include/mhu320ae.h), [host_ppu.h](../../../hsoc-stack/tools/qbox-platform/systemc-components/host_ppu/include/host_ppu.h) | mailbox/IRQ와 power/reset state machine |

<a id="s6"></a>
## S6. Instance와 thread

| 소스 | 확인 지점 |
|---|---|
| [rse/cpu.lua](../../../hsoc-stack/tools/qbox-platform/platforms/apollo/soc/hw-block/rse/cpu.lua) | helper + `rse_cpu_pass.qemu_inst`, M55 공개 경로 |
| [ap_compute/cpu.lua](../../../hsoc-stack/tools/qbox-platform/platforms/apollo/soc/hw-block/ap_compute/cpu.lua), [si_cl0/cpu.lua](../../../hsoc-stack/tools/qbox-platform/platforms/apollo/soc/hw-block/si_cl0/cpu.lua), [si_cl1/cpu.lua](../../../hsoc-stack/tools/qbox-platform/platforms/apollo/soc/hw-block/si_cl1/cpu.lua) | instance 3개, CPU 수, 초기 hold/reset, IRQ 배선 |
| [tcg-accel-ops-mttcg.c](../../../hsoc-stack/tools/qemu/accel/tcg/tcg-accel-ops-mttcg.c), [tcg-accel-ops-rr.c](../../../hsoc-stack/tools/qemu/accel/tcg/tcg-accel-ops-rr.c) | MULTI vCPU thread와 SINGLE RR thread |
| [qemu-initiator-signal-socket.h](../../../hsoc-stack/tools/qbox/qemu-components/common/include/ports/qemu-initiator-signal-socket.h), [qemu-target-signal-socket.h](../../../hsoc-stack/tools/qbox/qemu-components/common/include/ports/qemu-target-signal-socket.h) | IRQ direct/queue, 대상 instance BQL |
| [qbox_tc397.py](../../../scripts/run/qbox_tc397.py) | 선택 standalone TriCore process와 socket 연결 |

<a id="s7"></a>
## S7. 시간 정책

| 소스 | 확인 지점 |
|---|---|
| [vp/qvp.lua](../../../hsoc-stack/tools/qbox-platform/platforms/apollo/vp/qvp.lua) | `quantum_ns=10000000` |
| [AP](../../../hsoc-stack/tools/qbox-platform/platforms/apollo/vp/ap_compute/qemu.lua), [RSE](../../../hsoc-stack/tools/qbox-platform/platforms/apollo/vp/rse/qemu.lua), [CL0](../../../hsoc-stack/tools/qbox-platform/platforms/apollo/vp/si_cl0/qemu.lua), [CL1](../../../hsoc-stack/tools/qbox-platform/platforms/apollo/vp/si_cl1/qemu.lua) | accel/TCG/sync/time strategy 기본값과 환경 override |
| [cpu.h](../../../hsoc-stack/tools/qbox/qemu-components/common/include/cpu.h) | `sync_with_kernel`, local time, deadline callback |
| [qkmulti-freerunning.h](../../../hsoc-stack/tools/qbox/systemc-components/common/include/qkmulti-freerunning.h) | `need_sync=false`, 외부 thread는 tick notify |
| [qkmulti-quantum.h](../../../hsoc-stack/tools/qbox/systemc-components/common/include/qkmulti-quantum.h), [qkmultithread.cc](../../../hsoc-stack/tools/qbox/systemc-components/common/src/libgssync/qkmultithread.cc) | 별도 quantum 정책의 budget과 condition-variable wait |

<a id="s8"></a>
## S8. Launcher·이미지·로그

| 소스 | 확인 지점 |
|---|---|
| [run_qbox_yocto.sh](../../../run_qbox_yocto.sh) | provider/image 선택, CPU 수, persistent path, copy-disks 기본, `--skip-build`, `--no-post-login-probe` |
| [qbox_qboxconf_common.sh](../../../scripts/run/qbox_qboxconf_common.sh) | qboxconf reader, provider와 native dependency의 library path |
| [run_qbox_apollo_fvp_full.py](../../../scripts/run/run_qbox_apollo_fvp_full.py) | `--runtime-child` 재실행/dispatch, artifact 검증, runner 기본값 |
| [qbox_apollo_runtime.py](../../../scripts/run/qbox_apollo_runtime.py) | `platforms-vp -l/-p`, Popen, nonblocking log polling, writable/persistent image 준비 |
| [qbox_vmcu_boot.py](../../../scripts/run/qbox_vmcu_boot.py) | BSP+vMCU UART의 private WIC 예외 |
| [vp/ros/virtio.lua](../../../hsoc-stack/tools/qbox-platform/platforms/apollo/vp/ros/virtio.lua) | raw/writeback block backend, MMIO/IRQ 연결 |
| [run_qbox_apollo_fvp_full_tmux.sh](../../../scripts/run/run_qbox_apollo_fvp_full_tmux.sh) | 동일 runner 진입, console별 tail 표시 |

<a id="s9"></a>
## S9. Boot와 reset

| 소스 | 확인 지점 |
|---|---|
| [loader.h](../../../hsoc-stack/tools/qbox/systemc-components/common/include/loader.h) | `end_of_elaboration` 초기 preload와 `reset=true` 재호출 |
| [TF-M boot_hal_bl2.c](../../../hsoc-stack/components/system_mgmt/trusted-firmware-m/platform/ext/target/arm/rse/automotive_rd/apollo-qvp/bl2/boot_hal_bl2.c) | CL0 post-load, CL1 pre-load의 PPU ON, SCP readiness, `boot_platform_finish` |
| [BL2 image loop](../../../hsoc-stack/components/system_mgmt/trusted-firmware-m/bl2/ext/mcuboot/bl2_main.c), [Apollo image ID](../../../hsoc-stack/components/system_mgmt/trusted-firmware-m/platform/ext/target/arm/rse/automotive_rd/apollo-qvp/bl2_image_id.h) | image ID 역순 처리: CL1=4 → CL0=3 → AP=2 |
| [SCP safety_island_platform](../../../hsoc-stack/components/system_mgmt/scp-firmware/product/automotive-rd/apollo-qvp/module/safety_island_platform/src/mod_safety_island_platform.c), [CL1 core PPU 연결](../../../hsoc-stack/tools/qbox-platform/platforms/apollo/soc/hw-block/si_cl0/power.lua) | SCP의 CL1 core별 ON → PPU power_on_reset → CPU reset 해제 |
| [vp/rse/boot.lua](../../../hsoc-stack/tools/qbox-platform/platforms/apollo/vp/rse/boot.lua) | ROM·OTP·provisioning 초기 입력 |
| [vp/si_cl0/si_cl0.lua](../../../hsoc-stack/tools/qbox-platform/platforms/apollo/vp/si_cl0/si_cl0.lua), [vp/si_cl1/si_cl1.lua](../../../hsoc-stack/tools/qbox-platform/platforms/apollo/vp/si_cl1/si_cl1.lua) | PPU `power_on_load`와 loader reset 연결 |
| [vp/ap_compute/boot.lua](../../../hsoc-stack/tools/qbox-platform/platforms/apollo/vp/ap_compute/boot.lua), [vp/reset.lua](../../../hsoc-stack/tools/qbox-platform/platforms/apollo/vp/reset.lua) | AP BL2 ELF data/stack/BSS/xlat, AP cold reset 보조 초기화 |
| [host_ppu.h](../../../hsoc-stack/tools/qbox-platform/systemc-components/host_ppu/include/host_ppu.h), [vp/si_cl1/reset.lua](../../../hsoc-stack/tools/qbox-platform/platforms/apollo/vp/si_cl1/reset.lua) | cold/warm ON, load/reset/status 순서, system reset fanout |
| [TF-A AP BL2 descriptors](../../../hsoc-stack/components/primary_compute/trusted-firmware-a/plat/arm/board/automotive_rd/platform/apollo_qvp/apollo_qvp_bl2_mem_params_desc.c) | BL31/BL32/BL33 handoff |

<a id="validation"></a>
## 문서 검증과 실행 증거의 경계

검증 대상은 이 디렉터리의 Markdown·draw.io·SVG다. **Markdown 3개, 로컬 링크 172개, 도면 11개를 확인했다.** 실제 실행은 수행하지 않았으며 기존 성공 기록을 이번 측정 결과로 옮기지 않았다.

| 항목 | 확인 범위 |
|---|---|
| 소스 추적 | 구성→wrapper/model→runner 연결, 기본값과 override, 최종 audio backend |
| 도면 | draw.io 편집본 11페이지 전체 렌더링·시각 검토 완료; white theme와 325개 XML cell 참조 확인; SVG 11개의 내장 편집 데이터가 원본과 일치 |
| 문서 | 상대 경로·anchor·그림 링크 172개 통과; 요청한 6개 주제 포함; diagram validator 오류 0개 |
| 수행하지 않음 | BitBake/native build, 설치 provider와 source의 binary 일치, QVP/FVP boot, traffic/IRQ, 시간·성능 측정 |

재현 시에는 machine/config, source revision, 설치 provider, 이미지 hash, 실행 명령, 도메인별 log와 `result.json`을 묶어야 한다. **구현된 연결, boot/login, 서비스 시험, 전체 시스템 qualification, 물리 타이밍/안전성 검증을 별도 수준으로 보고한다.**
