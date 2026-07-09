# Apollo QVP IP Unit Test 구성 조사

작성일: 2026-07-09

## 범위

이 보고서는 `hsoc-stack/tools/qbox-platform/platforms/apollo/apollo-qvp.lua`
가 조합하는 Apollo QVP 플랫폼을 기준으로 한다. 진입점은 다음
hw-block을 로드한다.

- `hsoc-stack/tools/qbox-platform/platforms/apollo/hw-block/config.lua`
- `hsoc-stack/tools/qbox-platform/platforms/apollo/hw-block/fabric.lua`
- `hsoc-stack/tools/qbox-platform/platforms/apollo/hw-block/ros.lua`
- `hsoc-stack/tools/qbox-platform/platforms/apollo/hw-block/system_mgmt.lua`
- `hsoc-stack/tools/qbox-platform/platforms/apollo/hw-block/rse.lua`
- `hsoc-stack/tools/qbox-platform/platforms/apollo/hw-block/ap_compute.lua`
- `hsoc-stack/tools/qbox-platform/platforms/apollo/hw-block/si_cl0.lua`
- `hsoc-stack/tools/qbox-platform/platforms/apollo/hw-block/si_cl1.lua`

동일 `moduletype`이 여러 인스턴스로 반복되는 경우 같은 IP로 묶었다.
전체 인스턴스 추출 결과는
`build/qbox-apollo-qvp-unit-test-report/apollo-qvp-ip-inventory.txt`에
저장했다.

## 요약

Apollo QVP는 SystemC register/TLM 모델, qbox core 공통 모델, QEMU-backed
dynamic module, 그리고 QBox 인프라 객체가 섞여 있다.

기존 Test가 구성된 영역은 다음과 같다.

- qbox-platform SystemC IP: 25개 component 모두 CTest로 등록되어 있다.
  `ras_ffh_stub`는 이번 정적 Apollo QVP 인벤토리에는 직접 등장하지 않지만,
  component 단위 signal socket smoke test가 추가되었다.
- qbox core 공통 SystemC IP: `router`, `addrtr`, `gs_memory`, `loader`,
  `Pl011`, `char_backend_file` 등은 `hsoc-stack/tools/qbox/tests` 또는
  qbox-platform mirror test에 기존 Test가 있다.
- QEMU-backed IP: `cpu_arm_cortexA720AE`, `cpu_arm_cortexR82`,
  `arm_gicv3`, `arm_gicv3_its`, `qemu_gpex`, `virtio_mmio_*`,
  `pl031`, `sbsa_gwdt`, `reset_gpio`, `global_peripheral_initiator`,
  `qemu_arm_arch_timer_mmio`, `arm_smmuv3`, `ApolloRseCPU`는 dynamic
  module build target은 있지만 IP 단위 CTest unit test는 확인되지 않았다.
  이 항목은 구성 필요로 분류한다.

local build qbox의 기본값은 unit test를 끄지만,
`./local_build.sh qbox --qbox-unit-tests`를 사용하면
`build/local-apollo-qvp/work/qbox-platform/CMakeCache.txt`가
`BUILD_TESTING:BOOL=ON`으로 구성된다. 이 모드에서
`ctest --test-dir build/local-apollo-qvp/work/qbox-platform -N -L qbox-platform-systemc-components`
를 실행하면 label 기준 `Total Tests: 33`이 등록된다.

## IP별 Unit Test 현황

| IP / `moduletype` | Apollo QVP 사용 위치 | Unit test 상태 | Test 경로와 커버리지 |
|---|---|---|---|
| `cc3xx` | `rse.lua`의 `rse_cc3xx`, 기본 `QBOX_RDASPEN_CC3XX_BACKEND=systemc` | 기존 Test 있음 | `hsoc-stack/tools/qbox-platform/tests/components/cc3xx/cc3xx-tests.cc`: reset/readiness, RNG, PKA, SHA-256, AES DMA, interrupt, trace/stat, unsupported access. `cc3xx_core-tests.cc`: helper/core crypto path. |
| `qemu_cc3xx` | `config.lua`의 `rse_cc3xx_component()`, `QBOX_RDASPEN_CC3XX_BACKEND=qemu-native`일 때 | 부분 Test 있음 | `hsoc-stack/tools/qbox-platform/tests/components/cc3xx/qemu_cc3xx-tests.cc`: QEMU CC3XX type export만 확인한다. 실제 MMIO/crypto 동작 unit test는 구성 필요. |
| `dma350` | `rse.lua`의 `rse_dma350` | 기존 Test 있음 | `hsoc-stack/tools/qbox-platform/tests/components/dma350/dma350-tests.cc`: reset value, command complete, fill/copy, high bits, trace filter, unsupported/out-of-range access. |
| `gic720ae_messreg` | `ap_compute.lua`의 `ap_rgic2lgic_messreg` | 기존 Test 있음 | `hsoc-stack/tools/qbox-platform/tests/components/gic720ae_messreg/gic720ae_messreg-tests.cc`: reset zero, read/write store, invalid size/range/command, debug transport. |
| `gicx00_multiview` | `si_cl0.lua`의 SI/AP GIC multiview windows | 기존 Test 있음 | `hsoc-stack/tools/qbox-platform/tests/components/gicx00_multiview/gicx00_multiview-tests.cc`: view/power reset, Apollo SPI range, AP/SI view table, redistributor view, invalid access, debug transport. |
| `host_cmn_cyprus` | `si_cl0.lua`의 `si_cl0_cmn_cyprus` | 기존 Test 있음 | `hsoc-stack/tools/qbox-platform/tests/components/host_cmn_cyprus/host_cmn_cyprus-tests.cc`: discovery node, HNS/RN-SAM, range comparison, firmware writes, zero default, range reject. |
| `host_gtimer` | CSS/RSE/SI counter control/read/sync windows | 기존 Test 있음 | `hsoc-stack/tools/qbox-platform/tests/components/host_gtimer/host_gtimer-tests.cc`: counter advance/frequency, control/read/sync register behavior, monotonic read, ID reset, invalid access. |
| `host_ni710ae_nci` | `si_cl0.lua`의 NI-710AE NCI windows | 기존 Test 있음 | `hsoc-stack/tools/qbox-platform/tests/components/host_ni710ae_nci/host_ni710ae_nci-tests.cc`: MHU/secondary/primary topology, Apollo component exposure, APU writes, IIDR read-only, distinct APU blocks. |
| `host_ppu` | system management, SI CL0/CL1 PPU windows | 기존 Test 있음 | `hsoc-stack/tools/qbox-platform/tests/components/host_ppu/host_ppu-tests.cc`: power policy/status, emulator register, dynamic policy, reset/load signal ordering. CMake target은 `host_ppu-tests`, `host_ppu-signal-tests`. |
| `host_scr` | system config, SI SCR, AP SID | 기존 Test 있음 | `hsoc-stack/tools/qbox-platform/tests/components/host_scr/host_scr-tests.cc`: CL0/CL1 config reset, writable controls, Apollo SID/PCID identity, read-only identity, out-of-window access. |
| `host_smcf_mgi` | `si_cl0.lua`의 SMCF MGI | 기존 Test 있음 | `hsoc-stack/tools/qbox-platform/tests/components/host_smcf_mgi/host_smcf_mgi-tests.cc`: reset, monitor count, monitor/mode request, sample enable, W1C IRQ, mapped-region read. |
| `host_system_pll` | `si_cl0.lua`의 SI CL0 PLL | 기존 Test 있음 | `hsoc-stack/tools/qbox-platform/tests/components/host_system_pll/host_system_pll-tests.cc`: write-to-locked behavior, configurable lock mask. |
| `mhu320ae` | RSE/AP/SI/HIPC/PFDI MHU windows | 기존 Test 있음 | `hsoc-stack/tools/qbox-platform/tests/components/mhu320ae/mhu320ae-tests.cc`: reusable PBX/MBX doorbell frame, RSE BL2 power-domain transport/ack. Apollo-specific multi-pair bridge stress는 추가 구성 권장. |
| `mmu720ae` | `config.lua`의 `ap_smmu_component()`, 기본 `QBOX_RDASPEN_SMMU_BACKEND=systemc-mmu720ae` | 기존 Test 있음 | `hsoc-stack/tools/qbox-platform/tests/components/mmu720ae/mmu720ae-register-tests.cc`, `mmu720ae-queue-tests.cc`, `mmu720ae-tbu-tests.cc`: feature/reset, CR0/queue/MSI, command completion, error clear, TBU bypass/fault/SID. |
| `rse_atu` | RSE ATU, host SI/AP ATU, SMD expansion ATU | 기존 Test 있음 | `hsoc-stack/tools/qbox-platform/tests/components/rse_atu/rse_atu-tests.cc`: build config, page size/region count, register writes, translation, high SI PIK, mismatch status, DMI, trace. |
| `rse_integrity_checker` | `rse.lua`의 integrity checker | 기존 Test 있음 | `hsoc-stack/tools/qbox-platform/tests/components/rse_integrity_checker/rse_integrity_checker-tests.cc`: TF-M reset expectations, writable/read-only registers, start/clear completion, out-of-range. |
| `rse_kmu` | RSE KMU local/remote crypto path | 기존 Test 있음 | `hsoc-stack/tools/qbox-platform/tests/components/rse_kmu/rse_kmu-tests.cc`: reset, seed/interrupt, reset signal, key ready/export/invalidate, key slots, OTP image slot load, out-of-range. |
| `rse_lcm` | RSE lifecycle controller | 기존 Test 있음 | `hsoc-stack/tools/qbox-platform/tests/components/rse_lcm/rse_lcm-tests.cc`: provisioned lifecycle reset, TCI/TP mode, provisioning magic, OTP window/image/writeback/lock, invalid access. |
| `rse_protection_ctrl` | RSE NSA/SACFG/MPC/SIC protection control windows | 기존 Test 있음 | `hsoc-stack/tools/qbox-platform/tests/components/rse_protection_ctrl/rse_protection_ctrl-tests.cc`: MPC profile reset, lock behavior, non-secure write deny/allow compatibility. |
| `rse_sam` | RSE SAM registers | 기존 Test 있음 | `hsoc-stack/tools/qbox-platform/tests/components/rse_sam/rse_sam-tests.cc`: TF-M reset expectations, programming writes, read-only ignore, event clear, out-of-range. |
| `rse_sysctrl` | RSE system control | 기존 Test 있음 | `hsoc-stack/tools/qbox-platform/tests/components/rse_sysctrl/rse_sysctrl-tests.cc`: FVP boot reset values, CCI overrides, touched register R/W, secure debug status, SW reset write, invalid access. |
| `strata_flash_j3` | RSE boot flash, AP flash | 기존 Test 있음 | `hsoc-stack/tools/qbox-platform/tests/components/strata_flash_j3/strata_flash_j3-tests.cc`: image load, RSE boot flash path, read-id/status, program/erase/write-buffer, DMI, backing file, stats, invalid DMI. |
| `zena_fmu` | AP NI-710AE FMUs, SI CL0 FMU | 기존 Test 있음 | `hsoc-stack/tools/qbox-platform/tests/components/zena_fmu/zena_fmu-tests.cc`: PCID reset, SYSKEY-gated registers, W1C status, critical/non-critical fault output. |
| `zena_ssu` | SI CL0 SSU | 기존 Test 있음 | `hsoc-stack/tools/qbox-platform/tests/components/zena_ssu/zena_ssu-tests.cc`: documented reset registers, SYSKEY gating, status detail, sysctrl state, fault-to-safety output. |
| `reset_fanout` | Apollo QBox required target, reset fanout helper | 기존 Test 있음 | `hsoc-stack/tools/qbox-platform/tests/components/reset_fanout/reset_fanout-tests.cc`: reset broadcast and pulse ordering. 정적 Apollo QVP 인벤토리에는 직접 인스턴스가 없다. |
| `ras_ffh_stub` | qbox-platform SystemC component tree | 기존 Test 있음 | `hsoc-stack/tools/qbox-platform/tests/components/ras_ffh_stub/ras_ffh_stub-tests.cc`: optional IRQ initiator socket 생성, sink binding, true/false signal propagation. 이번 `apollo-qvp.lua` 정적 인벤토리에는 직접 등장하지 않는다. |
| `router` | root/RSE/AP view routers | 기존 Test 있음 | `hsoc-stack/tools/qbox/tests/components/router/*.cc`, `hsoc-stack/tools/qbox-platform/tests/components/router/*.cc`: address map, overlap/priority, cache, shadow warning, thread-safety, coverage tests. |
| `addrtr` | AP logical passthrough | 기존 Test 있음 | `hsoc-stack/tools/qbox/tests/components/addrtr/addrtr-tests.cc`, `hsoc-stack/tools/qbox-platform/tests/components/addrtr/addrtr-tests.cc`: address translation behavior. |
| `gs_memory` | SRAM/DRAM/MMIO placeholder windows | 기존 Test 있음 | `hsoc-stack/tools/qbox/tests/components/memory/memory-tests.cc`, `memory-blocs`, `gs_register`, mirror tests under `hsoc-stack/tools/qbox-platform/tests/components`: memory services/shared memory/register access. |
| `loader` | AP BL2 reset loader, SI CL0/CL1 loaders | 기존 Test 있음 | `hsoc-stack/tools/qbox/tests/components/loader/loader-test.cc`, `hsoc-stack/tools/qbox-platform/tests/components/loader/loader-test.cc`: binary/ELF/CSV/data load and target memory readback. |
| `Pl011` | RSE, AP secure/primary, SI CL0/CL1 UARTs | 기존 Test 있음 | `hsoc-stack/tools/qbox-platform/tests/components/uart/pl011-aperture-tests.cc`, `file-backend-test.cc`, `uart-biflow-stdio-test.cc`, `uart-biflow-backend-socket-test.cc`: PL011 aperture, file backend, stdio/socket biflow. |
| `char_backend_file` | UART log/read backends | 기존 Test 있음 | `hsoc-stack/tools/qbox-platform/tests/components/uart/file-backend-test.cc`, qbox core mirror: file read/write backend behavior. |
| `Container`, `QemuInstance`, `QemuInstanceManager`, `keep_alive`, `LocalPass` | platform hierarchy and QEMU orchestration infrastructure | 부분/간접 Test | `container_builder-tests`와 qbox utility tests는 Lua construction을 일부 검증하지만, Apollo QVP의 QEMU instance topology 단위 test는 없다. 구성 필요 항목으로 남긴다. |
| `cpu_arm_cortexA720AE` | AP CPU loop, `QBOX_APOLLO_NUM_CPUS` 기준 | 구성 필요 | `hsoc-stack/tools/qbox-platform/qemu-components/cpu_arm/cpu_arm_cortex_a720ae/CMakeLists.txt`는 build target만 등록한다. `hsoc-stack/tools/qbox/tests/qbox/cpu/aarch64`의 generic CPU integration tests는 참고 가능하지만 A720AE-specific unit test는 없다. |
| `cpu_arm_cortexR82` | SI CL0 CPU | 구성 필요 | `hsoc-stack/tools/qbox-platform/qemu-components/cpu_arm/cpu_arm_cortex_r82/CMakeLists.txt`는 build target만 등록한다. R82-specific reset/timer/GIC wiring unit test가 필요하다. |
| `ApolloRseCPU` / `rse_cpu_accel` | RSE CPU pass 내부 plugin | 부분 Test 있음 | `rse_lms_accel`, `rse_mcuboot_image`, `rse_p256_ecdsa` helper tests는 `hsoc-stack/tools/qbox-platform/tests/components/cc3xx`에 있다. `ApolloRseCPU` 자체의 TLM/interrupt/local peripheral integration unit test는 구성 필요. |
| `arm_gicv3`, `arm_gicv3_its` | AP/SI GIC and ITS | 구성 필요 | qbox core `qemu-components/irq-ctrl/*`는 dynamic module만 등록한다. `gicx00_multiview`와 `gic720ae_messreg` tests는 보조 register model tests이지 QEMU GIC unit test가 아니다. |
| `arm_smmuv3` | `QBOX_RDASPEN_SMMU_BACKEND=qemu-arm-smmuv3`일 때 AP SMMU | 구성 필요 | `hsoc-stack/tools/qbox-platform/qemu-components/arm_smmuv3/CMakeLists.txt`는 build target만 등록한다. 기본 backend는 `mmu720ae`라 그쪽 test는 존재하지만 QEMU SMMUv3 path test는 별도 필요. |
| `qemu_gpex` | AP PCIe root complex | 구성 필요 | `hsoc-stack/tools/qbox/qemu-components/pci/qemu_gpex/CMakeLists.txt`는 build target만 등록한다. ECAM/MMIO/IRQ smoke unit test가 필요하다. |
| `global_peripheral_initiator` | AP global peripheral initiator | 구성 필요 | `hsoc-stack/tools/qbox/qemu-components/global_peripheral_initiator/CMakeLists.txt`는 build target만 등록한다. AP view router와 global initiator binding unit test가 필요하다. |
| `reset_gpio` | AP reset GPIO | 구성 필요 | `hsoc-stack/tools/qbox/qemu-components/reset_gpio/CMakeLists.txt`는 build target만 등록한다. GPIO reset fanout과 QEMU reset request behavior test가 필요하다. |
| `sbsa_gwdt` | AP watchdog | 구성 필요 | `hsoc-stack/tools/qbox-platform/qemu-components/sbsa_gwdt/CMakeLists.txt`는 build target만 등록한다. refresh/control mirror aperture와 IRQ behavior unit test가 필요하다. |
| `qemu_arm_arch_timer_mmio` | AP REFCLK MMIO generic timer | 구성 필요 | `hsoc-stack/tools/qbox/qemu-components/timer/qemu_arm_arch_timer_mmio/CMakeLists.txt`는 build target만 등록한다. frame 0/1, 125MHz frequency, SPI 49/48 wiring smoke test가 필요하다. |
| `virtio_mmio_blk`, `virtio_mmio_net`, `virtio_mmio_rng`, `pl031` | RoS virtio block/net/rng and RTC | 구성 필요 | qbox/qbox-platform qemu-components에 build target은 있지만 직접 unit test는 없다. Device creation, MMIO aperture, IRQ line, argument propagation test를 구성해야 한다. |

## Unit Test 구성 제안

구성 필요 항목은 다음 순서로 추가하는 것이 좋다.

1. QEMU-backed IP smoke test 공통 harness를 만든다.
   `QemuInstanceManager`와 `QemuInstance`를 test fixture에서 생성하고,
   device wrapper의 construction, socket exposure, IRQ signal socket 이름,
   CCI parameter propagation을 확인한다.
2. CPU IP는 full firmware boot가 아니라 minimal reset/load-store image로
   시작한다. 기존 `hsoc-stack/tools/qbox/tests/qbox/cpu/aarch64` test
   harness를 참고해 `cpu_arm_cortexA720AE`와 `cpu_arm_cortexR82` target을
   별도 CTest로 분리한다.
3. AP GIC/ITS, AP SMMU, GPEX, virtio, PL031, watchdog은 device creation과
   MMIO aperture, IRQ route, qemu argument propagation을 먼저 확인한다.
4. `ApolloRseCPU`는 RSE local peripheral pass, remote signal mapping,
   local crypto/boot flash plugin registration을 fixture에서 검증한다.
5. qbox-platform SystemC IP는 이미 등록된 test를 유지하되,
   MHU bridge multi-pair, AP/SI cross-view, Apollo-specific register profile
   같은 플랫폼 조합 test를 추가하면 coverage gap을 줄일 수 있다.

## Unit test 실행 가이드

현재 local build qbox 기본값은 test를 끈다. 테스트가 필요한 경우에는
명시적으로 `--qbox-unit-tests`를 켠다.

```bash
./local_build.sh qbox --qbox-unit-tests
ctest --test-dir build/local-apollo-qvp/work/qbox-platform \
  -N -L qbox-platform-systemc-components
# Total Tests: 33
```

QBox 빌드와 함께 qbox-platform SystemC component unit test를 실행하려면
다음 명령을 사용한다.

```bash
./local_build.sh qbox --qbox-unit-tests
```

이 옵션은 `scripts/build/modules/build_qbox.sh`에서 다음 동작을 한다.

- `-DBUILD_TESTING=ON`으로 `build/local-apollo-qvp/work/qbox-platform`을
  configure한다.
- `cmake --build build/local-apollo-qvp/work/qbox-platform --target apollo_fvp_full_system`
  를 실행한다.
- `cmake --build build/local-apollo-qvp/work/qbox-platform --target qbox_platform_systemc_component_tests`
  를 실행한다.
- `ctest --test-dir build/local-apollo-qvp/work/qbox-platform -L qbox-platform-systemc-components --output-on-failure`
  를 실행한다.

Yocto native recipe에서 같은 unit test를 실행하려면
`qbox-apollo-qvp-native`의 `unit-tests` PACKAGECONFIG를 켠 뒤 `do_check`
task를 실행한다. 예를 들어 CI나 임시 config fragment에서 다음 중 하나를
설정할 수 있다.

```bitbake
QBOX_APOLLO_RUN_UNIT_TESTS:pn-qbox-apollo-qvp-native = "1"
# 또는
PACKAGECONFIG:append:pn-qbox-apollo-qvp-native = " unit-tests"
```

이후 targeted 실행은 다음과 같다.

```bash
source layers/poky/oe-init-build-env build
bitbake qbox-apollo-qvp-native -c check -f
```

CTest 결과는 BitBake task 로그인
`build/tmp_baremetal/work/x86_64-linux/qbox-apollo-qvp-native/1.0/temp/log.do_check.*`
에 남는다. `do_check`는 `qbox_platform_systemc_component_tests` target을
빌드하고 `ctest --test-dir "${B}" -L qbox-platform-systemc-components
--output-on-failure`를 실행한다.

이미 test-enabled build tree가 있다면 직접 실행할 수 있다.

```bash
ctest --test-dir build/local-apollo-qvp/work/qbox-platform \
  -L qbox-platform-systemc-components \
  --output-on-failure
```

특정 IP만 실행하려면 `-R`을 추가한다.

```bash
ctest --test-dir build/local-apollo-qvp/work/qbox-platform \
  -R 'rse_atu-tests|host_gtimer-tests|strata_flash_j3-tests' \
  --output-on-failure
```

현재 어떤 테스트가 등록되어 있는지 확인하려면:

```bash
ctest --test-dir build/local-apollo-qvp/work/qbox-platform \
  -N -L qbox-platform-systemc-components
```

현재 작업 시점의 증거:

- `build/qbox-apollo-qvp-unit-test-report/qbox-platform-cache-relevant.txt`:
  `BUILD_TESTING:BOOL=ON`.
- `build/qbox-apollo-qvp-unit-test-report/ctest-qbox-platform-component-list.txt`:
  `qbox-platform-systemc-components` label 기준 `Total Tests: 33`.
- `./local_build.sh qbox --qbox-unit-tests --no-package --jobs 6`:
  `qbox_platform_systemc_component_tests` target을 빌드하고 33개 label
  test가 모두 통과함.
- `build/qbox-apollo-qvp-unit-test-report/bitbake-qbox-do-check-tail.log`:
  Yocto `do_check`에서 같은 label test 33개가 모두 통과함.

## 조사 명령과 산출물

주요 정적 분석 산출물:

- `build/qbox-apollo-qvp-unit-test-report/apollo-qvp-ip-inventory.txt`
- `build/qbox-apollo-qvp-unit-test-report/apollo-qvp-moduletype-counts.txt`
- `build/qbox-apollo-qvp-unit-test-report/component-test-registry.txt`
- `build/qbox-apollo-qvp-unit-test-report/key-testcases.txt`
- `build/qbox-apollo-qvp-unit-test-report/analyze-qbox-platform-systemc-tests.json`
- `build/qbox-apollo-qvp-unit-test-report/analyze-qbox-platform-systemc-tests-stale.txt`
- `build/qbox-apollo-qvp-unit-test-report/qemu-components-files.txt`

검증용 명령:

```bash
python3 scripts/analyze_qbox_platform_systemc_tests.py --check-stale
python3 scripts/analyze_qbox_platform_systemc_tests.py --json
ctest --test-dir build/local-apollo-qvp/work/qbox-platform \
  -N -L qbox-platform-systemc-components
./local_build.sh qbox --qbox-unit-tests
bitbake qbox-apollo-qvp-native -c check -f
```

## 결론

Apollo QVP의 project-owned SystemC IP는 모두 component-level unit test가
구성되어 있다. 특히 RSE, MHU, timer, PPU/SCR, NI-710AE, FMU/SSU, flash,
MMU720AE는 CTest 기반 검증 경로가 있다.

반면 QEMU-backed IP는 build target과 runtime wiring은 있지만, IP별
unit test는 대부분 구성되어 있지 않다. 따라서 Apollo QVP test coverage를
넓히려면 QEMU-backed IP smoke/unit harness와 `ApolloRseCPU` fixture를
우선 추가하는 것이 가장 효과적이다.
