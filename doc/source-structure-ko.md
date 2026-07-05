# 현재 소스 구조

Updated: 2026-07-04

이 문서는 현재 `project-apollo` 체크아웃의 소스 소유권과 생성물 경계를
정리한다. 현재 루트 디렉터리는 Git 저장소이며, 구현 소스의 대부분은 루트
저장소가 고정하는 submodule에 있다. 파일을 수정할 때는 먼저 어느 저장소가
그 파일을 소유하는지 확인해야 한다.

## 루트 저장소

| 경로 | 역할 |
| --- | --- |
| `AGENTS.md` | Codex/agent 작업 규칙과 현재 Apollo FVP 기준. |
| `README.md` | 사용자용 clean checkout, Yocto/local build, QBox boot 가이드. |
| `.gitmodules` | 루트 저장소가 고정하는 submodule 목록과 기본 branch. |
| `yocto_build.sh` | 전통적인 Yocto `TEMPLATECONF` 기반 `nexios-image` 빌드 진입점. |
| `local_build.sh` | QBox와 로컬 소스 기반 firmware/kernel/rootfs 빌드 진입점. |
| `run_fvp.sh` | Yocto 빌드 산출물을 Apollo FVP tmux 세션에서 실행하는 사용자용 진입점. |
| `run_qbox_local.sh` | 로컬 빌드 산출물을 QBox tmux 세션에서 실행하는 사용자용 진입점. |

## Arm 제공 소스

| 경로 | 역할 | 소유권 |
| --- | --- | --- |
| `arm-zena-css/` | Arm Zena CSS BSP, RD-Aspen FVP 문서, Safety Island 통합, firmware 및 historical kas 조각. | Arm GitLab submodule |
| `sw-ref-stack/` | Arm Automotive Solutions reference stack, EWAOL 이미지, demo, test automation, HIPC/PFDI 통합. | Arm GitLab submodule |

이 두 저장소는 upstream Arm 소스의 기준점이다. Apollo 포팅 전용 변경은
가능하면 `hsoc-stack/` 아래에 두고, Arm upstream 변경이 명확할 때만 이
저장소를 직접 수정한다.

## Apollo 로컬 소스

Primary Compute 소스는 `hsoc-stack/components/primary_compute/` 아래에 있다.

| 경로 | 역할 |
| --- | --- |
| `hsoc-stack/components/primary_compute/linux/` | Apollo FVP용 Linux kernel source, DTS, `apollo_fvp_defconfig`, PREEMPT_RT 기준. |
| `hsoc-stack/components/primary_compute/u-boot/` | Apollo FVP용 U-Boot source와 local build 대상. |
| `hsoc-stack/components/primary_compute/trusted-firmware-a/` | Apollo FVP용 TF-A source와 platform 포팅. |
| `hsoc-stack/components/primary_compute/optee_os/` | Apollo FVP용 OP-TEE OS source. |
| `hsoc-stack/components/primary_compute/buildroot/` | 로컬 initramfs/rootfs 생성을 위한 Buildroot source. |

System Management와 Safety Island 소스는
`hsoc-stack/components/system_mgmt/` 아래에 있다.

| 경로 | 역할 |
| --- | --- |
| `hsoc-stack/components/system_mgmt/trusted-firmware-m/` | RSE Cortex-M55용 TF-M source와 Apollo FVP platform 포팅. |
| `hsoc-stack/components/system_mgmt/scp-firmware/` | Safety Island CL0/System Control Processor firmware source. |
| `hsoc-stack/components/system_mgmt/zephyrproject/zephyr/` | Zephyr RTOS source submodule. |
| `hsoc-stack/components/system_mgmt/zephyrproject/zephyr_hsoc_src/` | Apollo Safety Island CL1 Zephyr board, DTS, Kconfig, overlays, HSOC integration source. |
| `arm-zena-css/components/safety_island/zephyr/src/` | 공통 Safety Island Zephyr drivers, libraries, subsystems, sample app source. |
| `hsoc-stack/components/system_mgmt/zephyrproject/apollo-modules.list` | local build가 Yocto-unpacked Zephyr dependency tree, 공통 `arm_zena_safety_island` module, Apollo `zephyr_hsoc_src` module을 조합할 때 사용하는 module 목록. |

## Apollo Yocto 메타데이터

| 경로 | 역할 |
| --- | --- |
| `hsoc-stack/yocto/meta-hsoc-auto-solutions/` | Apollo distro/template layer. `conf/templates/apollo-fvp/`와 `conf/templates/apollo-qvp/`를 소유하며 dynamic-layer patch도 이곳에 둔다. |
| `hsoc-stack/yocto/meta-hsoc-bsp/` | Apollo BSP layer. `apollo-fvp`와 `apollo-qvp` machine, firmware recipes, QBox native recipes, externalsrc 설정, Linux kernel metadata, module signing, OP-TEE 통합을 소유한다. |

현재 active build는 `build/conf/templateconf.cfg`가 가리키는
`hsoc-stack/yocto/meta-hsoc-auto-solutions/conf/templates/apollo-fvp/`를 사용한다.
`build/conf/local.conf`의 active machine은 `MACHINE = "apollo-fvp"`이다.
`apollo-fvp` machine은 현재 `fvp-rd-aspen`을 상속하지만, 향후 Apollo 전용
하드웨어 차이를 분리하기 위한 포팅 지점이다.

Apollo QVP는 별도 machine인 `apollo-qvp`와 별도 권장 build directory
`build-apollo-qvp/`를 사용한다. QVP template은
`hsoc-stack/yocto/meta-hsoc-auto-solutions/conf/templates/apollo-qvp/`에 있고,
deploy root는
`build-apollo-qvp/tmp_baremetal/deploy/images/apollo-qvp/`이다. QVP 산출물은
`nexios-image-apollo-qvp.*`, `apollo-qvp.dtb`,
`efi-capsule-update-disk-image-apollo-qvp.img`, `firmware-apollo-qvp`,
`uefi-capsule-apollo-qvp`, `qbox-apollo-qvp/`처럼 deploy-visible 이름에
`apollo-qvp` 또는 `qbox-apollo-qvp`를 사용해야 한다.

QBox Yocto native recipe는
`hsoc-stack/yocto/meta-hsoc-bsp/recipes-devtools/qbox/`가 소유한다.
`qbox-libqemu-native`는 local `hsoc-stack/tools/qemu/`에서
`libqemu-system-aarch64.so`를 만들고,
`qbox-apollo-qvp-native`는 local `hsoc-stack/tools/qbox-platform/`,
`hsoc-stack/tools/qbox/`, `hsoc-stack/tools/qemu/`를 묶어
`qbox-apollo-qvp/` runtime bundle을 deploy한다. Bundle의 durable contract는
`qbox-apollo-qvp-env.sh`와 `qbox-apollo-qvp-manifest.json`으로 확인한다.

## 외부 Yocto Layer

`layers/` 아래는 pinned external layer submodule이다. 기본 정책은
직접 수정하지 않는 것이다.

주요 layer:

- `layers/poky/`
- `layers/meta-arm/`
- `layers/meta-openembedded/`
- `layers/meta-ewaol/`
- `layers/meta-cassini/`
- `layers/meta-bluechi/`
- `layers/meta-clang/`
- `layers/meta-mender/`
- `layers/meta-ptx/`
- `layers/meta-secure-core/`
- `layers/meta-security/`
- `layers/meta-virtualization/`
- `layers/meta-zephyr/`

외부 layer에 필요한 Apollo 전용 patch는 가능한 한
`hsoc-stack/yocto/meta-hsoc-auto-solutions/dynamic-layers/` 또는
`hsoc-stack/yocto/meta-hsoc-bsp/`로 옮긴다.

## QBox와 QEMU

| 경로 | 역할 |
| --- | --- |
| `hsoc-stack/tools/qbox/` | active upstream-friendly QBox core submodule. `platforms-vp`, libqbox/libqemu integration, reusable SystemC/TLM components, reusable QEMU-backed components, tests, examples를 소유한다. |
| `hsoc-stack/tools/qbox-platform/` | active Apollo/RD-Aspen platform overlay submodule. Apollo/RD-Aspen Lua, Zena/RSE SystemC model, Apollo-specific QEMU wrapper, platform tests, `apollo_fvp_full_system` aggregate target을 소유한다. |
| `hsoc-stack/tools/qbox-platform/platforms/apollo/` | Apollo full-system QVP, primary-compute direct boot, SI CL1 isolated boot Lua entrypoint. |
| `hsoc-stack/tools/qbox-platform/platforms/apollo/hw-block/` | RSE, Primary Compute, AP compute, SI CL0/CL1, ROS, system management block Lua 구성. |
| `hsoc-stack/tools/qbox-platform/systemc-components/` | Apollo/RD-Aspen overlay가 소유하는 QBox SystemC/TLM hardware models. Apollo에서 사용하는 `mhu320ae`, `mmu720ae`, `cc3xx`, `rse_*`, `zena_*`, `gicx00_multiview` 등이 있다. |
| `hsoc-stack/tools/qbox-platform/qemu-components/` | Apollo/RD-Aspen overlay가 소유하는 QEMU/libqemu-backed wrapper. Apollo-specific `qemu_cc3xx` 같은 wrapper를 포함한다. |
| `hsoc-stack/tools/qemu/` | active QBox local build가 사용하는 local QEMU/libqemu source submodule. |

새 Apollo hardware model이나 Lua wiring 변경은 대부분
`hsoc-stack/tools/qbox-platform/`이 소유한다. 재사용 가능한 QBox core 변경은
`hsoc-stack/tools/qbox/`가 소유하고, QEMU device/backend 변경은
`hsoc-stack/tools/qemu/`가 소유한다. 기본 Apollo overlay build output은
`build/local-apollo-fvp/work/qbox-platform/`이며, `QBOX_BUILD_DIR`는
`QBOX_PLATFORM_BUILD_DIR`의 호환 alias로만 사용한다.

## Scripts와 Tests

`scripts/`는 workflow별로 분리되어 있다.

| 경로 | 역할 |
| --- | --- |
| `scripts/build/` | `local_build.sh`가 호출하는 stage별 build script. |
| `scripts/run/` | FVP/QBox headless runner와 tmux runner. |
| `scripts/setup/` | bootstrap, RSE OTP provisioning, debug manifest 생성. |
| `scripts/debug/` | GDB/Iris/FVP debug helper. |
| `scripts/inspect/` | image, firmware, source inspection helper. |
| `scripts/analyze/` | trace, log, boot timing 분석 helper. |
| `scripts/test/` | memory map, coverage, completion validator. |

`tests/`에는 repository-local helper test가 있다. 새 Python helper를 추가하거나
runner behavior를 바꾸면 `python3 -m py_compile`과 관련 pytest/validator를
같이 실행한다.

## 생성물 경계

| 경로 | 취급 |
| --- | --- |
| `build/conf/` | active Yocto local configuration. build/runtime claim 전에 반드시 확인한다. |
| `build-apollo-qvp/tmp_baremetal/deploy/images/apollo-qvp/` | Apollo QVP Yocto deploy 산출물 위치. `qbox-apollo-qvp/` bundle도 여기에 배치된다. generated evidence이다. |
| `build/local-apollo-fvp/` | local build 산출물과 debug manifest. generated evidence이다. |
| `build/qbox-apollo-fvp/` | QBox runtime logs, result.json, summary, per-UART log. generated evidence이다. |
| `build/qbox-apollo-qvp/` | Apollo QVP QBox runtime logs, result.json, summary, per-UART log의 목표 위치. runtime evidence가 생기기 전에는 runtime 성공 근거로 취급하지 않는다. |
| `build/tmp_baremetal/` | BitBake task output, deploy, sysroot, logs, sstate 관련 산출물. generated evidence이다. |

`build/conf/`을 제외한 `build/` 하위 파일은 소스가 아니다. 검증 증거로
읽을 수는 있지만, durable change는 소유 source repository나 project-local
docs/scripts에 반영한다.

## 문서 업데이트 규칙

- 소스 구조나 ownership을 바꾸면 `AGENTS.md`, `README.md`, 이 문서를 함께
  확인한다.
- QBox Apollo platform 경로가 바뀌면
  `hsoc-stack/tools/qbox-platform/platforms/apollo/README.md`와
  `doc/apollo-qbox-hardware-ko.md`도 확인한다.
- Yocto layer/machine/recipe ownership이 바뀌면
  `doc/yocto-layer-and-recipe-map.md`를 확인한다.
- generated evidence 위치가 바뀌면 `doc/generated-artifacts-and-risks.md`를
  확인한다.
