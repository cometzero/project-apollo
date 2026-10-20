# SCP-firmware Source Index

본문과 다이어그램의 구현 위치를 연결한다. 경로는 repository root 기준이다.

- SCP source revision: `b17d6d0873b9979cee8720616866fa2cae2a2b4f`
- 기존 QVP CMakeCache 생성 시각: `2026-10-04 23:53:16 +0900`
- 기존 cache·ELF는 문서 대조에 사용했으며 현재 source 재빌드 결과는 아니다.

## Framework / Architecture

| 파일 |
|---|
| [hsoc-stack/components/system_mgmt/scp-firmware/CMakeLists.txt](../../../hsoc-stack/components/system_mgmt/scp-firmware/CMakeLists.txt) |
| [hsoc-stack/components/system_mgmt/scp-firmware/doc/framework.md](../../../hsoc-stack/components/system_mgmt/scp-firmware/doc/framework.md) |
| [hsoc-stack/components/system_mgmt/scp-firmware/doc/aarch64.md](../../../hsoc-stack/components/system_mgmt/scp-firmware/doc/aarch64.md) |
| [hsoc-stack/components/system_mgmt/scp-firmware/framework/src/fwk_arch.c](../../../hsoc-stack/components/system_mgmt/scp-firmware/framework/src/fwk_arch.c) |
| [hsoc-stack/components/system_mgmt/scp-firmware/framework/src/fwk_module.c](../../../hsoc-stack/components/system_mgmt/scp-firmware/framework/src/fwk_module.c) |
| [hsoc-stack/components/system_mgmt/scp-firmware/framework/src/fwk_core.c](../../../hsoc-stack/components/system_mgmt/scp-firmware/framework/src/fwk_core.c) |
| [hsoc-stack/components/system_mgmt/scp-firmware/framework/src/fwk_delayed_resp.c](../../../hsoc-stack/components/system_mgmt/scp-firmware/framework/src/fwk_delayed_resp.c) |
| [hsoc-stack/components/system_mgmt/scp-firmware/framework/src/fwk_notification.c](../../../hsoc-stack/components/system_mgmt/scp-firmware/framework/src/fwk_notification.c) |
| [hsoc-stack/components/system_mgmt/scp-firmware/framework/src/fwk_mm.c](../../../hsoc-stack/components/system_mgmt/scp-firmware/framework/src/fwk_mm.c) |
| [hsoc-stack/components/system_mgmt/scp-firmware/framework/src/fwk_io.c](../../../hsoc-stack/components/system_mgmt/scp-firmware/framework/src/fwk_io.c) |
| [hsoc-stack/components/system_mgmt/scp-firmware/framework/src/fwk_log.c](../../../hsoc-stack/components/system_mgmt/scp-firmware/framework/src/fwk_log.c) |
| [hsoc-stack/components/system_mgmt/scp-firmware/arch/arm/aarch64/src/arch_crt0.S](../../../hsoc-stack/components/system_mgmt/scp-firmware/arch/arm/aarch64/src/arch_crt0.S) |
| [hsoc-stack/components/system_mgmt/scp-firmware/arch/arm/aarch64/src/arch_main.c](../../../hsoc-stack/components/system_mgmt/scp-firmware/arch/arm/aarch64/src/arch_main.c) |
| [hsoc-stack/components/system_mgmt/scp-firmware/arch/arm/aarch64/src/arch_gic.c](../../../hsoc-stack/components/system_mgmt/scp-firmware/arch/arm/aarch64/src/arch_gic.c) |
| [hsoc-stack/components/system_mgmt/scp-firmware/arch/arm/aarch64/src/arch_exceptions.S](../../../hsoc-stack/components/system_mgmt/scp-firmware/arch/arm/aarch64/src/arch_exceptions.S) |
| [hsoc-stack/components/system_mgmt/scp-firmware/arch/arm/aarch64/src/arch_exceptions.c](../../../hsoc-stack/components/system_mgmt/scp-firmware/arch/arm/aarch64/src/arch_exceptions.c) |
| [hsoc-stack/components/system_mgmt/scp-firmware/arch/arm/aarch64/include/arch_interrupt.h](../../../hsoc-stack/components/system_mgmt/scp-firmware/arch/arm/aarch64/include/arch_interrupt.h) |
| [hsoc-stack/components/system_mgmt/scp-firmware/arch/arm/common/src/arch.ld.S](../../../hsoc-stack/components/system_mgmt/scp-firmware/arch/arm/common/src/arch.ld.S) |

## Product / Build

| 파일 |
|---|
| [hsoc-stack/components/system_mgmt/scp-firmware/product/automotive-rd/apollo-qvp/si0_ramfw/Firmware.cmake](../../../hsoc-stack/components/system_mgmt/scp-firmware/product/automotive-rd/apollo-qvp/si0_ramfw/Firmware.cmake) |
| [hsoc-stack/components/system_mgmt/scp-firmware/product/automotive-rd/apollo-qvp/si0_ramfw/Buildoptions.cmake](../../../hsoc-stack/components/system_mgmt/scp-firmware/product/automotive-rd/apollo-qvp/si0_ramfw/Buildoptions.cmake) |
| [hsoc-stack/components/system_mgmt/scp-firmware/product/automotive-rd/apollo-qvp/si0_ramfw/CMakeLists.txt](../../../hsoc-stack/components/system_mgmt/scp-firmware/product/automotive-rd/apollo-qvp/si0_ramfw/CMakeLists.txt) |
| [hsoc-stack/components/system_mgmt/scp-firmware/product/automotive-rd/apollo-qvp/si0_ramfw/Toolchain-GNU.cmake](../../../hsoc-stack/components/system_mgmt/scp-firmware/product/automotive-rd/apollo-qvp/si0_ramfw/Toolchain-GNU.cmake) |
| [hsoc-stack/components/system_mgmt/scp-firmware/product/automotive-rd/apollo-qvp/si0_ramfw/include/fmw_memory.h](../../../hsoc-stack/components/system_mgmt/scp-firmware/product/automotive-rd/apollo-qvp/si0_ramfw/include/fmw_memory.h) |
| [hsoc-stack/components/system_mgmt/scp-firmware/product/automotive-rd/apollo-qvp/si0_ramfw/include/fmw_notification.h](../../../hsoc-stack/components/system_mgmt/scp-firmware/product/automotive-rd/apollo-qvp/si0_ramfw/include/fmw_notification.h) |
| [hsoc-stack/components/system_mgmt/scp-firmware/product/automotive-rd/apollo-qvp/si0_ramfw/include/si0_mmap.h](../../../hsoc-stack/components/system_mgmt/scp-firmware/product/automotive-rd/apollo-qvp/si0_ramfw/include/si0_mmap.h) |
| [hsoc-stack/components/system_mgmt/scp-firmware/product/automotive-rd/apollo-qvp/si0_ramfw/include/si0_irq.h](../../../hsoc-stack/components/system_mgmt/scp-firmware/product/automotive-rd/apollo-qvp/si0_ramfw/include/si0_irq.h) |
| [hsoc-stack/components/system_mgmt/scp-firmware/product/automotive-rd/apollo-qvp/si0_ramfw/include/si0_cfgd_scmi.h](../../../hsoc-stack/components/system_mgmt/scp-firmware/product/automotive-rd/apollo-qvp/si0_ramfw/include/si0_cfgd_scmi.h) |
| [hsoc-stack/components/system_mgmt/scp-firmware/product/automotive-rd/apollo-qvp/si0_ramfw/config_si0_platform.c](../../../hsoc-stack/components/system_mgmt/scp-firmware/product/automotive-rd/apollo-qvp/si0_ramfw/config_si0_platform.c) |
| [hsoc-stack/components/system_mgmt/scp-firmware/product/automotive-rd/apollo-qvp/si0_ramfw/config_gicx00.c](../../../hsoc-stack/components/system_mgmt/scp-firmware/product/automotive-rd/apollo-qvp/si0_ramfw/config_gicx00.c) |
| [hsoc-stack/components/system_mgmt/scp-firmware/product/automotive-rd/apollo-qvp/si0_ramfw/config_gtimer.c](../../../hsoc-stack/components/system_mgmt/scp-firmware/product/automotive-rd/apollo-qvp/si0_ramfw/config_gtimer.c) |
| [hsoc-stack/components/system_mgmt/scp-firmware/product/automotive-rd/apollo-qvp/si0_ramfw/config_timer.c](../../../hsoc-stack/components/system_mgmt/scp-firmware/product/automotive-rd/apollo-qvp/si0_ramfw/config_timer.c) |
| [hsoc-stack/components/system_mgmt/scp-firmware/product/automotive-rd/apollo-qvp/si0_ramfw/config_scmi.c](../../../hsoc-stack/components/system_mgmt/scp-firmware/product/automotive-rd/apollo-qvp/si0_ramfw/config_scmi.c) |
| [hsoc-stack/components/system_mgmt/scp-firmware/product/automotive-rd/apollo-qvp/si0_ramfw/config_mhu3.c](../../../hsoc-stack/components/system_mgmt/scp-firmware/product/automotive-rd/apollo-qvp/si0_ramfw/config_mhu3.c) |
| [hsoc-stack/components/system_mgmt/scp-firmware/product/automotive-rd/apollo-qvp/si0_ramfw/config_transport.c](../../../hsoc-stack/components/system_mgmt/scp-firmware/product/automotive-rd/apollo-qvp/si0_ramfw/config_transport.c) |
| [hsoc-stack/components/system_mgmt/scp-firmware/product/automotive-rd/apollo-qvp/si0_ramfw/config_sds.c](../../../hsoc-stack/components/system_mgmt/scp-firmware/product/automotive-rd/apollo-qvp/si0_ramfw/config_sds.c) |
| [hsoc-stack/components/system_mgmt/scp-firmware/product/automotive-rd/apollo-qvp/si0_ramfw/config_gpio.c](../../../hsoc-stack/components/system_mgmt/scp-firmware/product/automotive-rd/apollo-qvp/si0_ramfw/config_gpio.c) |
| [hsoc-stack/components/system_mgmt/scp-firmware/product/automotive-rd/apollo-qvp/si0_ramfw/config_pmic.c](../../../hsoc-stack/components/system_mgmt/scp-firmware/product/automotive-rd/apollo-qvp/si0_ramfw/config_pmic.c) |
| [hsoc-stack/components/system_mgmt/scp-firmware/product/automotive-rd/apollo-qvp/si0_ramfw/config_tps6594.c](../../../hsoc-stack/components/system_mgmt/scp-firmware/product/automotive-rd/apollo-qvp/si0_ramfw/config_tps6594.c) |

## Driver / Service

| 파일 |
|---|
| [hsoc-stack/components/system_mgmt/scp-firmware/module/timer/src/mod_timer.c](../../../hsoc-stack/components/system_mgmt/scp-firmware/module/timer/src/mod_timer.c) |
| [hsoc-stack/components/system_mgmt/scp-firmware/module/gtimer/src/mod_gtimer.c](../../../hsoc-stack/components/system_mgmt/scp-firmware/module/gtimer/src/mod_gtimer.c) |
| [hsoc-stack/components/system_mgmt/scp-firmware/module/mhu3/src/mod_mhu3.c](../../../hsoc-stack/components/system_mgmt/scp-firmware/module/mhu3/src/mod_mhu3.c) |
| [hsoc-stack/components/system_mgmt/scp-firmware/module/transport/src/mod_transport.c](../../../hsoc-stack/components/system_mgmt/scp-firmware/module/transport/src/mod_transport.c) |
| [hsoc-stack/components/system_mgmt/scp-firmware/module/scmi/src/mod_scmi.c](../../../hsoc-stack/components/system_mgmt/scp-firmware/module/scmi/src/mod_scmi.c) |
| [hsoc-stack/components/system_mgmt/scp-firmware/module/pl011/src/mod_pl011.c](../../../hsoc-stack/components/system_mgmt/scp-firmware/module/pl011/src/mod_pl011.c) |
| [hsoc-stack/components/system_mgmt/scp-firmware/module/gpio/src/mod_gpio.c](../../../hsoc-stack/components/system_mgmt/scp-firmware/module/gpio/src/mod_gpio.c) |
| [hsoc-stack/components/system_mgmt/scp-firmware/module/i2c/src/mod_i2c.c](../../../hsoc-stack/components/system_mgmt/scp-firmware/module/i2c/src/mod_i2c.c) |
| [hsoc-stack/components/system_mgmt/scp-firmware/module/pmic/src/mod_pmic.c](../../../hsoc-stack/components/system_mgmt/scp-firmware/module/pmic/src/mod_pmic.c) |
| [hsoc-stack/components/system_mgmt/scp-firmware/module/tps6594/src/mod_tps6594.c](../../../hsoc-stack/components/system_mgmt/scp-firmware/module/tps6594/src/mod_tps6594.c) |
| [hsoc-stack/components/system_mgmt/scp-firmware/product/automotive-rd/apollo-qvp/module/si0_platform/src/mod_si0_platform.c](../../../hsoc-stack/components/system_mgmt/scp-firmware/product/automotive-rd/apollo-qvp/module/si0_platform/src/mod_si0_platform.c) |
| [hsoc-stack/components/system_mgmt/scp-firmware/product/automotive-rd/apollo-qvp/module/safety_island_platform/src/mod_safety_island_platform.c](../../../hsoc-stack/components/system_mgmt/scp-firmware/product/automotive-rd/apollo-qvp/module/safety_island_platform/src/mod_safety_island_platform.c) |
| [hsoc-stack/components/system_mgmt/scp-firmware/product/automotive-rd/apollo-qvp/module/vmcu_safety/README.md](../../../hsoc-stack/components/system_mgmt/scp-firmware/product/automotive-rd/apollo-qvp/module/vmcu_safety/README.md) |
| [hsoc-stack/components/system_mgmt/scp-firmware/tools/image_crc_patcher.py](../../../hsoc-stack/components/system_mgmt/scp-firmware/tools/image_crc_patcher.py) |

## Test

| 파일 |
|---|
| [hsoc-stack/components/system_mgmt/scp-firmware/framework/test/CMakeLists.txt](../../../hsoc-stack/components/system_mgmt/scp-firmware/framework/test/CMakeLists.txt) |
| [hsoc-stack/components/system_mgmt/scp-firmware/framework/test/test_fwk_core.c](../../../hsoc-stack/components/system_mgmt/scp-firmware/framework/test/test_fwk_core.c) |
| [hsoc-stack/components/system_mgmt/scp-firmware/framework/test/test_fwk_idle.c](../../../hsoc-stack/components/system_mgmt/scp-firmware/framework/test/test_fwk_idle.c) |
| [hsoc-stack/components/system_mgmt/scp-firmware/framework/test/test_fwk_module.c](../../../hsoc-stack/components/system_mgmt/scp-firmware/framework/test/test_fwk_module.c) |
| [hsoc-stack/components/system_mgmt/scp-firmware/framework/test/test_fwk_notification.c](../../../hsoc-stack/components/system_mgmt/scp-firmware/framework/test/test_fwk_notification.c) |
| [hsoc-stack/components/system_mgmt/scp-firmware/unit_test/user_guide.md](../../../hsoc-stack/components/system_mgmt/scp-firmware/unit_test/user_guide.md) |
| [hsoc-stack/components/system_mgmt/scp-firmware/module/pmic/README.md](../../../hsoc-stack/components/system_mgmt/scp-firmware/module/pmic/README.md) |

## Integration / Verification

| 파일 |
|---|
| [hsoc-stack/yocto/meta-hsoc-bsp/recipes-bsp/scp-firmware/scp-firmware_%.bbappend](../../../hsoc-stack/yocto/meta-hsoc-bsp/recipes-bsp/scp-firmware/scp-firmware_%.bbappend) |
| [hsoc-stack/yocto/meta-hsoc-bsp/recipes-bsp/scp-firmware/scp-firmware-apollo-qvp.inc](../../../hsoc-stack/yocto/meta-hsoc-bsp/recipes-bsp/scp-firmware/scp-firmware-apollo-qvp.inc) |
| [hsoc-stack/yocto/meta-hsoc-bsp/recipes-bsp/scp-firmware/scp-firmware-apollo-common.inc](../../../hsoc-stack/yocto/meta-hsoc-bsp/recipes-bsp/scp-firmware/scp-firmware-apollo-common.inc) |
| [arm-zena-css/yocto/meta-zena-css-bsp/recipes-bsp/scp-firmware/scp-firmware-fvp-rd-aspen.inc](../../../arm-zena-css/yocto/meta-zena-css-bsp/recipes-bsp/scp-firmware/scp-firmware-fvp-rd-aspen.inc) |
| [layers/meta-arm/meta-arm/recipes-bsp/scp-firmware/scp-firmware_2.15.0.bb](../../../layers/meta-arm/meta-arm/recipes-bsp/scp-firmware/scp-firmware_2.15.0.bb) |
| [arm-zena-css/yocto/meta-zena-css-bsp/recipes-bsp/images/firmware-fvp-rd-aspen.bb](../../../arm-zena-css/yocto/meta-zena-css-bsp/recipes-bsp/images/firmware-fvp-rd-aspen.bb) |
| [hsoc-stack/yocto/meta-hsoc-auto-solutions/recipes-core/images/include/nexios-apollo-qboxboot.inc](../../../hsoc-stack/yocto/meta-hsoc-auto-solutions/recipes-core/images/include/nexios-apollo-qboxboot.inc) |
| [hsoc-stack/components/system_mgmt/trusted-firmware-m/platform/ext/target/arm/rse/automotive_rd/css-aspen/bl2/boot_hal_bl2.c](../../../hsoc-stack/components/system_mgmt/trusted-firmware-m/platform/ext/target/arm/rse/automotive_rd/css-aspen/bl2/boot_hal_bl2.c) |
| [hsoc-stack/tools/qbox-platform/platforms/apollo/vp/si_cl0/boot.lua](../../../hsoc-stack/tools/qbox-platform/platforms/apollo/vp/si_cl0/boot.lua) |
| [arm-zena-css/documentation/design/boot_process.rst](../../../arm-zena-css/documentation/design/boot_process.rst) |
| [doc/arm_zena_css_dev_guide/06-boot-flow-of-zena-css.md](../../../doc/arm_zena_css_dev_guide/06-boot-flow-of-zena-css.md) |
| [hsoc-stack/yocto/meta-hsoc-auto-solutions/lib/oeqa/runtime/cases/test_00_si_cl0_boot.py](../../../hsoc-stack/yocto/meta-hsoc-auto-solutions/lib/oeqa/runtime/cases/test_00_si_cl0_boot.py) |
| [hsoc-stack/yocto/meta-hsoc-auto-solutions/lib/oeqa/runtime/cases/test_70_power_scmi.py](../../../hsoc-stack/yocto/meta-hsoc-auto-solutions/lib/oeqa/runtime/cases/test_70_power_scmi.py) |
| [hsoc-stack/yocto/meta-hsoc-bsp/lib/oeqa/runtime/cases/test_20_si_cl0_diagnostics.py](../../../hsoc-stack/yocto/meta-hsoc-bsp/lib/oeqa/runtime/cases/test_20_si_cl0_diagnostics.py) |
| [qa-tests/profiles/pfdi-si-cl1.yaml](../../../qa-tests/profiles/pfdi-si-cl1.yaml) |
| [scripts/test/measure_scp_idle.py](../../../scripts/test/measure_scp_idle.py) |
| [scripts/test/verify_qbox_si_pmic.py](../../../scripts/test/verify_qbox_si_pmic.py) |

## 기존 Build Artifact

아래 파일은 local build output이며 repository 문서에 포함하지 않는다.

```text
build/tmp_baremetal/work/apollo_qvp-poky-linux/scp-firmware/2.16.0+git/build/ramfw/si0/
├── CMakeCache.txt
├── framework/include/fwk_module_idx.h
└── bin/
    ├── apollo-qvp-si0-bl2.elf
    ├── apollo-qvp-si0-bl2.bin
    └── apollo-qvp-si0-bl2.map
```

상위 Framework 개념: [Arm SCP-firmware Framework Guide](https://github.com/ARM-software/SCP-firmware/blob/master/doc/framework.md). Apollo 실행 흐름은 위 로컬 구현을 기준으로 기술했다.
