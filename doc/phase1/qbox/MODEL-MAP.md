# Apollo QVP Model Map

## 소유 경계

이 표는 **canonical full-system 실행의 기본 선택과 대표 모델**을 현재 Lua 및 구현 소스에서 추적한 결과다. 전체 모델 목록이나 runtime PASS 목록은 아니다. 객체 이름은 공통 접두사 `platform.`을 생략했다.

| 소유 영역 | 책임 | 소스 |
|---|---|---|
| QBox core | 범용 Container·router·memory·bus 및 QEMU wrapper | [qbox/](../../../hsoc-stack/tools/qbox/) |
| Apollo overlay | Apollo Lua 구성, CPU 확장 wrapper, Zena/RSE 모델·reset adapter | [qbox-platform/](../../../hsoc-stack/tools/qbox-platform/) |
| QEMU/libqemu | CPU 실행·QEMU device 구현; wrapper가 호출하는 backend | [qemu/](../../../hsoc-stack/tools/qemu/) |

`QEMU wrapper`도 SystemC module이지만 장치 동작은 QEMU backend를 호출한다. 표의 `SystemC`는 모델 동작을 SystemC/TLM으로 구현한 경우다. Core 소유라는 표기는 upstream 무수정 상태를 뜻하지 않는다.

## 기본 full-system의 주요 모델

| 실제 moduletype | 종류 / 소유 | 실제 객체·선택 조건 | 구현 소스 |
|---|---|---|---|
| `cpu_arm_cortexA720AE` | QEMU wrapper / overlay | `ap_cpu_0..N-1` · AP 활성화 시; 기본 full runner N=4 | [구현](../../../hsoc-stack/tools/qbox-platform/qemu-components/cpu_arm/cpu_arm_cortex_a720ae/src/cortex-a720ae.cc) |
| `cpu_arm_cortexR82` | QEMU wrapper / overlay | `si_cl0_cpu_0`, `si_cl1_cpu_0..3` | [구현](../../../hsoc-stack/tools/qbox-platform/qemu-components/cpu_arm/cpu_arm_cortex_r82/src/cortex-r82.cc) |
| `ApolloRseCPU` | 복합 QEMU wrapper / overlay | `rse_cpu_pass.cpu_0` · 내부 core M55와 router 결합 | [구현](../../../hsoc-stack/tools/qbox-platform/platforms/apollo/rse-cpu/src/apollo_rse_cpu.h) |
| `arm_gicv3` | QEMU wrapper / core | `ap_gic`, `si_cl0_gic`, `si_cl1_gic` | [구현](../../../hsoc-stack/tools/qbox/qemu-components/irq-ctrl/arm_gicv3/src/arm_gicv3.cc) |
| `pl031` | QEMU wrapper / core | `ap_rtc_0` · AP RTC | [구현](../../../hsoc-stack/tools/qbox/qemu-components/pl031/src/pl031.cc) |
| `router` | SystemC / core | `host_router`, `system_router`, `ap_router`, `rse_router` 등 | [구현](../../../hsoc-stack/tools/qbox/systemc-components/router) |
| `gs_memory` | SystemC / core | `host_ap_shared_sram`, `host_ap_dram1` 등 메모리 구간 | [구현](../../../hsoc-stack/tools/qbox/systemc-components/gs_memory) |
| `dw_apb_i2c` | SystemC / core | `ap_dw_i2c_0..5`, `si_cl0_dw_i2c_0` | [구현](../../../hsoc-stack/tools/qbox/systemc-components/i2c/src/dw-apb-i2c.cc) |
| `tps6594` | SystemC / core | `board_tps6594` · SI I2C 주소 `0x48` | [구현](../../../hsoc-stack/tools/qbox/systemc-components/i2c/tps6594/src/tps6594.cc) |
| `pca9539` | SystemC / core | `board_pca9539` · AP I2C0 주소 `0x74` | [구현](../../../hsoc-stack/tools/qbox/systemc-components/i2c/pca9539/src/pca9539.cc) |
| `smmuv3` | SystemC / core | `ap_smmu_0` · `systemc-mmu720ae` 선택 시 | [구현](../../../hsoc-stack/tools/qbox/systemc-components/smmuv3) |
| `smmuv3_tbu` | SystemC / core | `ap_smmu_lti00` · 위 SMMU의 transaction bridge | [구현](../../../hsoc-stack/tools/qbox/systemc-components/smmuv3) |
| `mhu320ae` | SystemC / overlay | `host_ap_rse_mhu_pbx/mbx` 등 도메인 간 mailbox | [구현](../../../hsoc-stack/tools/qbox-platform/systemc-components/mhu320ae) |
| `rse_atu` | SystemC / overlay | `host_ap_atu`, `host_si_atu`, `host_smdexp2smd_atu` 등 주소 변환 | [구현](../../../hsoc-stack/tools/qbox-platform/systemc-components/rse_atu) |
| `dma350` | SystemC / overlay | `rse_dma350` · RSE DMA; AP DMA와 backend가 다름 | [구현](../../../hsoc-stack/tools/qbox-platform/systemc-components/dma350) |
| `hsoc_gpio` | SystemC / overlay | `pinctrl_peri0`, `pinctrl_peri1` · GPIO/pinmux | [구현](../../../hsoc-stack/tools/qbox-platform/systemc-components/hsoc_gpio) |
| `host_ppu` | SystemC / overlay | `host_si_pik` 및 AP/SI power unit | [구현](../../../hsoc-stack/tools/qbox-platform/systemc-components/host_ppu) |
| `gicx00_multiview` | SystemC / overlay | `ap_gic_multiview` · GIC 주소 view 변환 | [구현](../../../hsoc-stack/tools/qbox-platform/systemc-components/gicx00_multiview) |
| `qemu_cc3xx` | QEMU wrapper / overlay | `rse_cpu_pass.rse_cc3xx` · launcher/performance preset의 기본 crypto | [구현](../../../hsoc-stack/tools/qbox-platform/qemu-components/cc3xx_native) |
| `strata_flash_j3` | SystemC / overlay | AP secure flash; RSE에서는 `systemc-strata` 대안 | [구현](../../../hsoc-stack/tools/qbox-platform/systemc-components/strata_flash_j3) |
| `zena_reset_ctrl` | SystemC / overlay | `host_reset_ctrl` · RGM/PIK reset 경로 | [구현](../../../hsoc-stack/tools/qbox-platform/systemc-components/zena_reset_ctrl) |
| `qemu_dma350` | QEMU wrapper / overlay | `dma350_0`, `dma350_1` · VP가 초기 SystemC 모델을 교체 | [구현](../../../hsoc-stack/tools/qbox-platform/qemu-components/qemu_dma350/src/qemu_dma350.cc) |
| `qemu_dw_apb_i2s` | QEMU wrapper / overlay | `ap_dw_i2s_0..1` · peer와 `dma350_1` 연결 | [구현](../../../hsoc-stack/tools/qbox-platform/qemu-components/qemu_dw_apb_i2s/src/qemu_dw_apb_i2s.cc) |
| `pflash_cfi` | QEMU wrapper / core | `rse_cpu_pass.rse_boot_flash_qemu` · 기본 RSE flash | [구현](../../../hsoc-stack/tools/qbox/qemu-components/pflash_cfi) |

선택 근거: [AP GIC/SMMU](../../../hsoc-stack/tools/qbox-platform/platforms/apollo/soc/hw-block/ap_compute/system.lua), [ROS I/O](../../../hsoc-stack/tools/qbox-platform/platforms/apollo/soc/hw-block/ros/io_peri.lua), [DMA](../../../hsoc-stack/tools/qbox-platform/platforms/apollo/soc/hw-block/ros/dma.lua), [RSE crypto](../../../hsoc-stack/tools/qbox-platform/platforms/apollo/soc/hw-block/rse/security.lua), [RSE flash](../../../hsoc-stack/tools/qbox-platform/platforms/apollo/soc/hw-block/rse/boot.lua), [board population](../../../hsoc-stack/tools/qbox-platform/platforms/apollo/board/saturn-v.lua).

VP의 [audio.connect](../../../hsoc-stack/tools/qbox-platform/platforms/apollo/vp/backends/audio.lua)는 routed MMIO·IRQ와 객체 이름을 보존하면서 AP DMA/I2S backend를 교체한다. I2S0/1은 master/peer로 결합하고 I2S pinmux gate 연결을 제거한다.

AP controller는 AP enable 조건을 따른다. RSE crypto/flash의 local 배치는 [VP model options](../../../hsoc-stack/tools/qbox-platform/platforms/apollo/vp/options/models.lua)가 선택하며, `soc/config.lua`의 standalone 기본값과 다르다.

## Backend 선택에서 주의할 네 가지 이름

| 구분 | 정확한 해석 | 근거 |
|---|---|---|
| `systemc-mmu720ae` | backend 정책 문자열이다. 실제 생성은 core `smmuv3` + `smmuv3_tbu`; overlay `mmu720ae`가 아니다. QEMU 대안은 `arm_smmuv3` | [ap_smmu_component / define_iommu](../../../hsoc-stack/tools/qbox-platform/platforms/apollo/soc/hw-block/ap_compute/system.lua) |
| RSE flash 기본값 | standalone SoC는 `systemc-strata`; full runner/VP는 `qemu-cfi-local` → `pflash_cfi`. AP secure flash는 SystemC strata 유지 | [VP options](../../../hsoc-stack/tools/qbox-platform/platforms/apollo/vp/options/models.lua), [runner defaults](../../../scripts/run/run_qbox_apollo_fvp_full.py) |
| 초기 descriptor ≠ 최종 모델 | ROS는 SystemC DMA/I2S를 먼저 정의하지만 full-system VP가 **`qemu_dma350`·`qemu_dw_apb_i2s`**로 교체한다. RSE `rse_dma350`는 SystemC 유지 | [audio.connect](../../../hsoc-stack/tools/qbox-platform/platforms/apollo/vp/backends/audio.lua), [RSE DMA](../../../hsoc-stack/tools/qbox-platform/platforms/apollo/soc/hw-block/rse/io_peri.lua) |
| `moduletype` ≠ 라이브러리 파일명 | I2C는 `dw_apb_i2c` / `dylib_path="dw-apb-i2c"`. `dw_apb_i2s` / `dw-apb-i2s`는 초기 SystemC descriptor의 이름이며 최종 QEMU I2S와 구분 | [I2C 등록](../../../hsoc-stack/tools/qbox/systemc-components/i2c/src/dw-apb-i2c.cc), [I2S 등록](../../../hsoc-stack/tools/qbox-platform/systemc-components/dw-apb-i2s/src/dw-apb-i2s.cc) |

RSE crypto의 **실제 기본 full 실행은 `qemu_cc3xx`**다. [root launcher](../../../run_qbox_yocto.sh)는 performance preset/native backend를 전달하고, [canonical runner](../../../scripts/run/run_qbox_apollo_fvp_full.py)는 기본 preset에서 native backend를 활성화한다. Preset/native 선택을 끈 경우에는 Lua 기본 대안인 [SystemC `cc3xx`](../../../hsoc-stack/tools/qbox-platform/systemc-components/cc3xx)를 사용할 수 있다.

Native DMA-350의 구현 범위는 1D copy/fill/wrap과 외부 handshake이며 **command-link descriptor chain, security attribution, bus timing은 미구현**이다. [QEMU 모델 범위](../../../hsoc-stack/tools/qemu/hw/dma/arm-dma350.c).

## AP I2C0: Lua에서 실제 연결까지

**주소 `0x30100000`, 크기 `0x10000`, GIC SPI socket index `320`, architectural INTID `352`.** 마지막 두 숫자는 `INTID = SPI index + 32` 관계이며 서로 바꿔 쓰면 안 된다. [주소/IRQ 상수](../../../hsoc-stack/tools/qbox-platform/platforms/apollo/soc/hw-block/ros/map.lua).

```text
AP CPU.mem → ap_router → ap_dw_i2c_0.target_socket
                            ├─ irq → ap_gic.spi_in_320  [INTID 352]
                            └─ i2c_socket → board_i2c0
                                              ├─ EEPROM 0x50/0x51/0x52
                                              └─ board_pca9539 0x74
```

| 구성 단계 | 소유·구체 동작 | 근거 |
|---|---|---|
| Controller 정의 | SoC가 `ap_dw_i2c_0`의 type·주소·IRQ를 정의. 초기 target bind는 host_router | [io_peri.define](../../../hsoc-stack/tools/qbox-platform/platforms/apollo/soc/hw-block/ros/io_peri.lua) |
| 최종 AP view 연결 | AP interconnect가 controller target을 `ap_router.initiator_socket`에 재배선. 초기 descriptor만 읽으면 최종 CPU 경로를 놓친다 | [bind_ap_view_targets](../../../hsoc-stack/tools/qbox-platform/platforms/apollo/soc/hw-block/ros/address_view.lua), [enable_ap_router](../../../hsoc-stack/tools/qbox-platform/platforms/apollo/soc/hw-block/ap_compute/interconnect.lua) |
| Pinmux / reset | `pinctrl_peri0.peripheral_enable_0` → controller.pinmux_enable; AP cold reset target 목록에 controller.reset 포함 | [pinmux](../../../hsoc-stack/tools/qbox-platform/platforms/apollo/soc/hw-block/ros/pinctrl.lua), [reset targets](../../../hsoc-stack/tools/qbox-platform/platforms/apollo/soc/hw-block/fabric/reset.lua) |
| Board 연결 | Board가 I2C bus·EEPROM·PCA9539를 연결. PCA9539의 INT_N은 SMD GPIO1, RESET_N은 SMD GPIO0와 연결 | [board.connect](../../../hsoc-stack/tools/qbox-platform/platforms/apollo/board/hw-block/pca9539.lua) |

Controller/MMIO/IRQ는 **SoC**, 외부 chip·bus population은 **Board**, loopback·host backend는 **VP** 소유다. [full-system profile](../../../hsoc-stack/tools/qbox-platform/platforms/apollo/vp/profiles/full-system.lua)이 순서대로 결합한다. Saturn-V 실제 회로 일치도는 [board source](../../../hsoc-stack/tools/qbox-platform/platforms/apollo/board/saturn-v.lua)에서 `UNVERIFIED`로 표시한다.

소스에서 모델과 연결을 확인했으며 이번 문서 작업에서 빌드·부팅·IRQ traffic 시험은 실행하지 않았다. 실제 장치 기능, reset 순서의 runtime 결과, timing fidelity는 해당 시험 증거로 확인해야 한다.
