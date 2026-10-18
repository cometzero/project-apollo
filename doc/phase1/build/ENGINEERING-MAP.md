# Apollo Build Architecture — 구현 연결표

[세미나 본문](README.md)의 상세 추적 자료. 현재 QVP/Nexios metadata를 기준으로 **소스 → 설정 → recipe → 산출물 → 소비자**를 연결한다. 아래 recipe 이름과 설정은 정적 소스에서 확인했으며, recipe의 `PV`는 로컬 checkout의 Git revision을 대신하지 않는다.

컴포넌트별 내부 subsystem, Source Architecture, Build Architecture, Deploy artifacts는 [Component Architecture](components/README.md)에서 볼 수 있다. 이 문서는 여러 컴포넌트를 잇는 전체 전달 관계를 정리한다.

## 1. Component → recipe → artifact → consumer

경로 약어: `PC=hsoc-stack/components/primary_compute`, `SM=hsoc-stack/components/system_mgmt`, `HB=hsoc-stack/yocto/meta-hsoc-bsp`. 표의 링크는 실제 파일을 가리킨다.

| 컴포넌트 | 코드·플랫폼 구성 | 빌드 접점 | 산출물과 다음 소비자 |
|---|---|---|---|
| Linux | `PC/linux`; `apollo_qvp_defconfig`, `hsoc/apollo-qvp-saturn-v.dts` | `linux-yocto-rt` + [Apollo common](../../../hsoc-stack/yocto/meta-hsoc-bsp/recipes-kernel/linux/linux-yocto-apollo-common.inc); `do_kernel_configme`에서 defconfig/fragment 적용 | `Image`, OS DTB → UKI; modules → rootfs; kernel build metadata → 외부 module |
| U-Boot | `PC/u-boot`; `apollo_qvp_defconfig` | [Apollo common](../../../hsoc-stack/yocto/meta-hsoc-bsp/recipes-bsp/u-boot/u-boot-apollo-common.inc), [제품 fragment](../../../hsoc-stack/yocto/meta-hsoc-bsp/recipes-bsp/u-boot/files/apollo-qvp-auto-ad-nexios.cfg) | `u-boot.bin` → TF-A BL33; 실행 시 ESP·misc 소비 |
| TF-A | `PC/trusted-firmware-a`; `TFA_PLATFORM=apollo_qvp` | [QVP 설정](../../../hsoc-stack/yocto/meta-hsoc-bsp/recipes-bsp/trusted-firmware-a/trusted-firmware-a-apollo-qvp.inc); `TFA_BUILD_TARGET=bl2 fip`, `SPD=spmd` | `bl2.bin`, `fip.bin` → firmware 조립; `bl2.elf` → QVP AP reset loader |
| OP-TEE | `PC/optee_os`; `automotive_rd-rdaspen` | [Apollo common](../../../hsoc-stack/yocto/meta-hsoc-bsp/recipes-security/optee/optee-os-apollo-common.inc), [SP 선택](../../../layers/meta-arm/meta-arm/recipes-security/optee/optee-os-ts.inc); `CFG_CORE_SEL1_SPMC`, `CFG_CORE_FFA`, `CFG_WITH_SP` | SP가 포함된 `tee-pager_v2.bin` → TF-A BL32; `tee.elf`는 심볼 |
| Trusted Services | upstream Git → Yocto WORKDIR; **HSOC externalsrc 대상 아님** | [Arm TS 설정](../../../arm-zena-css/yocto/meta-zena-css-bsp/recipes-security/trusted-services/ts-fvp-rd-aspen.inc); `ts-sp-se-proxy`, `ts-sp-smm-gateway`, `ts-sp-ras-inject-bridge`; SP는 `TS_ENV=opteesp`, client library는 `arm-linux` | UUID별 `.stripped.elf` + manifest `.dtb` → OP-TEE `SP_PATHS`; `libts`/`libpsats` → Linux packages |
| TF-M | `SM/trusted-firmware-m`; `arm/rse/automotive_rd/apollo-qvp` | [QVP 설정](../../../hsoc-stack/yocto/meta-hsoc-bsp/recipes-bsp/trusted-firmware-m/trusted-firmware-m-apollo-qvp.inc), [참조 export](../../../arm-zena-css/yocto/meta-zena-css-bsp/recipes-bsp/trusted-firmware-m/trusted-firmware-m-fvp-rd-aspen.inc) | `bl1_1.bin`, `bl2_signed.bin`, `tfm_s_signed.bin`, `rom_dma_ics.bin`, keys/provisioning → firmware/OTP; `tfm_fwu_impl_info.h` → TS |
| SCP-firmware | `SM/scp-firmware`; `automotive-rd/apollo-qvp/si0_ramfw` | [QVP 설정](../../../hsoc-stack/yocto/meta-hsoc-bsp/recipes-bsp/scp-firmware/scp-firmware-apollo-qvp.inc); `FW_TARGETS=si0`, `FW_INSTALL=ramfw` | `si0_ramfw.bin/.elf` → firmware sysroot/deploy; signed bin → RSE flash; bin → QVP PPU loader |
| Zephyr CL1 | kernel: `SM/zephyrproject/zephyr`; board/module: `zephyr_hsoc_src`; sample app: Arm `components/safety_island/zephyr/src/apps/sample` | [Apollo common](../../../hsoc-stack/yocto/meta-hsoc-bsp/recipes-kernel/zephyr-kernel/zephyr-demos-cl1-apollo-common.inc), [QVP 설정](../../../hsoc-stack/yocto/meta-hsoc-bsp/recipes-kernel/zephyr-kernel/zephyr-demos-cl1-apollo-qvp.inc); `apollo_qvp_safety_island_c1` | `zephyr-demos-cl1.bin/.elf` → firmware/runner; ELF entry → CL1 RVBAR; bin → SRAM loader |
| QBox provider | `tools/qbox-platform` + `tools/qbox` | [qbox-apollo-qvp-native.bb](../../../hsoc-stack/yocto/meta-hsoc-bsp/recipes-devtools/qbox/qbox-apollo-qvp-native.bb); aggregate target `apollo_fvp_full_system` | `platforms-vp`, `libqbox.so`, models, installed Lua → native sysroot → launcher |
| libqemu | `tools/qemu` | [qbox-libqemu-native.bb](../../../hsoc-stack/yocto/meta-hsoc-bsp/recipes-devtools/qbox/qbox-libqemu-native.bb); `LIBQEMU_TARGETS=aarch64`, configure `--disable-download` | `libqemu-system-aarch64.so`, headers, CMake package → QBox build/runtime |

### 파일 전달 경로의 차이


| 전달 경로 | 구체 예 | 설계 의미 |
|---|---|---|
| target sysroot | TS SP → OP-TEE, OP-TEE `.bin` → TF-A, firmware payload → 조립 recipe | `DEPENDS`와 `do_populate_sysroot`가 소비 recipe의 입력을 준비 |
| deploy task | `u-boot:do_deploy`의 `u-boot.bin` → TF-A `BL33` | 의존성을 선언하고 deploy 파일을 직접 소비 |
| image task | rootfs verity → 제품 initramfs → UKI → WIC | 패키지 빌드와 최종 이미지 변환의 의존성은 별도 |
| native sysroot | libqemu → QBox, QBox provider → qboxconf | 실행기는 타깃 rootfs 패키지가 아닌 호스트 도구 |

## 2. 툴체인·ABI·sysroot 경계

| 실행 대상 | 선택되는 툴체인 계열 | 결과 |
|---|---|---|
| AP Linux / U-Boot / TF-A / OP-TEE | AArch64 target cross toolchain | Linux ABI 또는 각 firmware의 freestanding/secure build 옵션 |
| RSE Cortex-M55 / TF-M | `gcc-arm-none-eabi-native` | Cortex-M bare-metal firmware |
| SI CL0 / SCP | `gcc-aarch64-none-elf-native` | AArch64 bare-metal firmware |
| SI CL1 / Zephyr | `zephyr-sdk-native`, `ZEPHYR_TOOLCHAIN_VARIANT=zephyr` | Zephyr board와 Kconfig/DT에 따른 firmware |
| QBox / libqemu | host native compiler | 개발 호스트용 ELF executable / shared library |

`LIBQEMU_TARGETS=aarch64`는 에뮬레이션 대상 선택이며, `.so`가 Arm 호스트에서만 실행된다는 뜻이 아니다. `recipe-sysroot`는 소비 recipe의 target 의존 입력, `recipe-sysroot-native`는 호스트 도구 입력, `sysroots-components`는 다른 recipe가 가져갈 설치 결과다.

[externalsrc.bbclass](../../../layers/poky/meta/classes/externalsrc.bbclass)는 기본 `do_fetch/do_unpack/do_patch`를 로컬 소스 경로로 대체하고 `SSTATE_SKIP_CREATION=1`을 설정한다. local file 및 `type=git-dependency` 등의 보조 입력은 남는다. 따라서 **참조 patch가 로컬 checkout에 자동 재적용되거나 모든 로컬 component 결과가 sstate로 복원된다고 가정하면 안 된다.**

Zephyr는 Arm Safety Island module을 작업 디렉터리에 복사한 뒤 별도 patch task를 적용한다. QBox provider의 CMake configure는 네트워크가 허용되어 있고 CPM 의존성도 있으므로, BitBake `SRC_URI`만으로 native 소스 집합 전체를 설명하지 않는다.

## 3. Firmware 저장 매체의 초기 내용

[firmware.cfg](../../../arm-zena-css/yocto/meta-zena-css-bsp/recipes-bsp/images/files/fvp-rd-aspen/firmware.cfg)의 offset은 **파일 내부 offset**이며 CPU 주소와 다르다.

| 매체 | 초기 배치 | 채움 정책 |
|---|---|---|
| RSE ROM | `bl1_1` 영역 75 KiB; `rom_dma_ics.bin`은 `0x1F000`에 배치, 영역 크기 `0x400` | raw image |
| RSE Flash | metadata 복제본 `0x5000/0x6000`; RSE BL2 `0x7000`; runtime `0x27000`; SI0 `0x67000`; SI1 `0x167000` | primary에 실제 이미지 포함; secondary는 크기 예약 |
| AP Flash | FWU metadata `0x5000/0x6000`; FIP_A `0x7000`; FIP_B `0x247000` | FIP_A만 초기 이미지 포함; FIP_B는 예약 |
| QVP OTP | TF-M `CMakeCache.txt` + `otp_config.pickle` → provisioning script | 참조 genimage의 빈 placeholder를 별도 생성한 64 KiB OTP로 치환 |
| 제품 WIC root A/B | 같은 `.ext4.verity`를 두 root partition에 rawcopy | **양쪽 OS root 슬롯을 채움**; firmware bank 정책과 다름 |

[OTP recipe](../../../hsoc-stack/yocto/meta-hsoc-bsp/recipes-bsp/images/firmware-apollo-qvp.bb)는 root의 [provision_rse_otp_image.py](../../../scripts/setup/provision_rse_otp_image.py)를 사용한다. 여기서 만들어지는 이미지 구조와 이후 FWU 동작 검증은 별개의 증거다.

## 4. U-Boot 구성의 결합 사례

```text
apollo_qvp_defconfig
  직접 UKI 선택·bootefi 기본 경로
       + auto-ad-nexios distro일 때 product fragment merge
apollo-qvp-auto-ad-nexios.cfg
  auto-ad-nexios-systemd-boot.scr 우선 실행
       ├─ script: LoaderEntryOneShot 설정 → EFI/BOOT/bootaa64.efi
       │                                      → systemd-boot → nexios-{a,b}.efi
       └─ script 로드 실패: 직접 slot UKI → fallback UKI → bootflow scan
```

같은 `u-boot` recipe라도 machine defconfig와 distro fragment의 조합으로 동작이 달라진다. 제품 `nexios-image`의 ESP에는 systemd-boot discovery용 `EFI/Linux/nexios-{a,b}.efi`와 direct fallback용 `EFI/Linux/{a-slot,b-slot}/auto-ad-nexios-{a,b}.efi`가 함께 배치된다. aliases/script는 `pn-nexios-image` override로 추가되므로 BSP는 직접 slot UKI 경로를 사용한다.

## 5. qboxconf → launcher → 실행 입력

| 계약 필드 | 해석 결과 |
|---|---|
| `provider.bindir` + `exe` | 설치된 `platforms-vp` 절대 경로 |
| `provider.libdir`, `module_dir` | `libqbox.so`, runtime library, 모델 `.so` 검색 경로 |
| `provider.data_dir` + `config` | 설치된 Apollo Lua 경로 |
| `sysroot.recipe_sysroot_native` | provider의 의존 library 및 도구 환경 |
| `images` | qboxconf가 있는 deploy 디렉터리 기준 이미지 경로 |
| `env.QBOX_APOLLO_NUM_CPUS` | 환경변수 → qboxconf → local.conf → 4 순서로 AP 수 결정 |

[공통 reader](../../../scripts/run/qbox_qboxconf_common.sh)가 경로와 계약을 읽고 [launcher](../../../run_qbox_yocto.sh)가 실행 환경을 구성한다. 현재 image 매핑에는 모든 실행 입력이 포함되어 있지 않다. BL1_2/BL2 ELF, AP BL2 ELF, provisioning blob, CL1 ELF는 deploy 또는 Yocto WORKDIR 탐색으로 보완한다. 실행에 필요한 집합은 **deploy + native provider/sysroot + 필요한 ELF·보조 입력**이다.

### 입력 파일과 실제 소비자

| 입력 | QVP 소비자 | 의미 |
|---|---|---|
| `rse-rom-image.img` | `rse_rom.load`, ROM `0x11000000` | RSE 초기 코드 |
| `rse-otp-image.img` | OTP wrapper 및 LCM/KMU | 보안 상태·키/설정 입력 |
| `combined_provisioning_message.bin` | `rse_vm1.load`, VM1 offset `0x20000` | provisioning 입력 |
| `rse-flash-image.img` | 기본 `qemu-cfi-local` 경로 | RSE CPU와 TLM 측이 공유하는 Flash 상태 |
| `ap-flash-image.img` | `host_ap_flash` backing/load | AP firmware가 FIP를 읽음 |
| AP `bl2.elf` | `ap_bl2_reset_loader` | `.data` 복원, stack/BSS/xlat 초기화 |
| `si0_ramfw.bin` | `si_cl0_loader` → SRAM `0x120000000` | `host_si_cl0_core0_ppu.power_on_load`에 연결 |
| `zephyr-demos-cl1.bin/.elf` | `si_cl1_loader` → SRAM `0x140000000`; ELF entry → RVBAR | bin/ELF 검증 후 PPU load/reset 순서로 실행 |
| WIC | `ap_virtioblk_0` raw block backend | ESP/UEFI/UKI를 거쳐 Linux 실행 |
| 별도 kernel 항목 | image metadata; reader/launcher는 직접 소비하지 않음 | 실제 kernel payload는 UKI에서 소비 |
| 별도 DTB 항목 | 존재 확인 후 `--ap-dtb` identity로 전달 | full-system의 OS DTB도 UKI에서 소비; 직접 메모리 적재 경로가 아님 |

[AP loader](../../../hsoc-stack/tools/qbox-platform/platforms/apollo/vp/ap_compute/boot.lua), [CL0 연결](../../../hsoc-stack/tools/qbox-platform/platforms/apollo/vp/si_cl0/si_cl0.lua), [CL1 연결](../../../hsoc-stack/tools/qbox-platform/platforms/apollo/vp/si_cl1/si_cl1.lua), [RSE load](../../../hsoc-stack/tools/qbox-platform/platforms/apollo/vp/rse/boot.lua), [VirtIO backend](../../../hsoc-stack/tools/qbox-platform/platforms/apollo/vp/ros/virtio.lua)를 근거로 한다.

### 실행 파일과 변경 가능한 상태

| 항목 | 기본 처리 |
|---|---|
| WIC / capsule disk | 기본 원본 경로 사용. `--copy-disks`에서 reflink/sparse 사본 준비 |
| BSP + UART vMCU | 별도 `*-vmcu.wic` 사본의 UKI cmdline에 `apollo.vmcu=1` 추가; 기본 `--bsp` tmux도 해당 |
| AP Flash / OTP | runtime `writable-images/` 사본 |
| RSE Flash | 영속 상태, lock 및 source/OTP fingerprint 확인; 호환 갱신 시 PS/ITS 보존 |
| RSE state 위치 | `build/qbox-apollo-fvp/state/yocto-apollo-qvp/`; dashboard는 별도 out/state |
| 부트 종료 | 기본 keep-running-after-pass; PASS 이후에도 runtime child가 QBox·로그 reader 소유 |

실행 입력과 상태 정책은 [runtime engine](../../../scripts/run/qbox_apollo_runtime.py), BSP 디스크 수정은 [vMCU boot helper](../../../scripts/run/qbox_vmcu_boot.py)에 구현되어 있다. 기본 가속에는 SRAM DMI와 RSE crypto/BL2 hotpath 등이 포함된다. loader capability의 `authenticated_image` 명칭 자체는 암호학적 인증 시험 결과가 아니다.

## 6. 변경의 전파 범위

| 변경 | 다시 확인할 빌드·배포 연결 | 실행에서 확인할 대상 |
|---|---|---|
| Linux driver / OS DTS | Image·DTB → UKI; modules → 제품 rootfs 또는 BSP initramfs; 최종 WIC | 실제 UKI와 rootfs/initramfs modules의 일치 |
| U-Boot / OP-TEE / SP | SP → OP-TEE → TF-A FIP → AP Flash | 부팅한 Flash·FIP와 실행 바이너리 |
| TF-M / SCP / CL1 | component → sign/firmware → RSE Flash; 관련 개별 bin/ELF도 갱신 | Flash와 host loader 입력의 일치; OTP/RSE state 호환성 |
| QEMU/libqemu | native libqemu → QBox provider의 의존 sysroot | 실제 로드한 `.so` |
| QBox 모델 / Lua | provider compile/install/populate_sysroot → installed modules/Lua | checkout이 아닌 provider 설치 사본 |
| image 정책 / WKS / UKI cmdline | rootfs·initramfs·UKI·WIC 재조립 | partition labels, 두 UKI 경로, 선택 root 슬롯 |

빌드 성공은 위 소비자가 새 파일을 사용했다는 증거를 대신하지 않는다. 이 연결표의 검증 범위는 현재 metadata·스크립트·Lua의 정적 추적이다.
