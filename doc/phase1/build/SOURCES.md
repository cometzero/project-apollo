# 설계 근거와 검토 범위

이 문서는 [Build Architecture](README.md), [컴포넌트 구조](components/README.md), [구현 연결표](ENGINEERING-MAP.md)의 근거 색인이다. 2026-10-16 checkout을 읽어 작성했으며, 참조 설계의 기능 설명과 현재 Apollo 설정·실행 검증을 구분한다.

## 원본 문서·그림의 적용

아래 문서와 연결된 PNG 원본을 실제로 열어 확인했다. 원본은 투명 배경이므로 검토 시 흰 배경에서 표시했다. 새 그림은 원본의 도메인·저장 매체·의존성 구분을 참고하고 Apollo 구현에 맞춰 다시 구성했다.

| Arm 설계 문서 | 확인한 원본 그림 | 본문 반영 |
|---|---|---|
| [components.rst](../../../arm-zena-css/documentation/design/components.rst), [secure_services.rst](../../../arm-zena-css/documentation/design/secure_services.rst) | [Primary Compute Secure Services](../../../arm-zena-css/documentation/images/primary_compute_secure_services.png) | AP Normal/Secure, OP-TEE SPMC, SE Proxy/SMM Gateway, RSE의 경계 |
| [components.rst](../../../arm-zena-css/documentation/design/components.rst) | [SCMI RSE/TF-A/SCP](../../../arm-zena-css/documentation/images/scmi_comm_rse_tfa_scp.png) | RSE의 기동 요청과 CL0의 전원 제어 |
| [hipc.rst](../../../arm-zena-css/documentation/design/hipc.rst) | [HIPC baremetal](../../../arm-zena-css/documentation/images/hipc_baremetal_design.png) | remoteproc attach, shared-memory 데이터와 MHU 알림 분리 |
| [power_and_performance_control.rst](../../../arm-zena-css/documentation/design/power_and_performance_control.rst) | [Power and Performance Control](../../../arm-zena-css/documentation/images/power_and_performance_control.png) | PSCI·SCMI 경로와 현재 QVP 기본 정책 구분 |
| [boot_process.rst](../../../arm-zena-css/documentation/design/boot_process.rst) | [RSE-oriented boot flow](../../../arm-zena-css/documentation/images/rse_oriented_boot_flow.png), [Image layouts](../../../arm-zena-css/documentation/images/image-layouts.png) | 로딩/실행/전원 제어, firmware bank, 저장 매체별 이미지 |
| [integration.rst](../../../arm-zena-css/documentation/design/integration.rst) | [Yocto layer dependency](../../../arm-zena-css/documentation/images/yocto_layers_dependency_diagram.png) | 참조 레이어의 저장소 소유권·의존성에 HSOC 추가 |

원본의 layer 그림과 현재 checkout의 이름·위치가 다른 부분은 현재 `bblayers.conf`와 `layer.conf`를 우선했다. 예를 들어 현재 SI layer는 `meta-zena-css-safety-island`, Zephyr core layer는 `layers/meta-zephyr/meta-zephyr-core`다.

## S1. 소프트웨어 도메인과 통신

- [components.rst](../../../arm-zena-css/documentation/design/components.rst): RSE/SI/AP 구성, TF-A `RESET_TO_BL2`, FIP 구성, MHUv3/SCMI, OP-TEE SPMC.
- [secure_services.rst](../../../arm-zena-css/documentation/design/secure_services.rst): `libpsats`/`libts`, FF-A, SE Proxy, SMM Gateway와 RSE 저장 서비스.
- [참조 machine](../../../arm-zena-css/yocto/meta-zena-css-bsp/conf/machine/fvp-rd-aspen.conf): FF-A 및 Trusted Services machine features.
- [Apollo OP-TEE 소스 연결](../../../hsoc-stack/yocto/meta-hsoc-bsp/recipes-security/optee/optee-os-apollo-common.inc).

## S2. HIPC와 PFDI

- [hipc.rst](../../../arm-zena-css/documentation/design/hipc.rst): CL1 독립 부팅, Linux `RPROC_DETACHED`/attach, resource table, vring, RPMsg buffer, MHU doorbell.
- [platform_fault_detection_interface.rst](../../../arm-zena-css/documentation/design/platform_fault_detection_interface.rst): CL0 monitor, AP/CL1 agent, SCMI vendor protocol. 참조 backend의 placeholder를 실제 STL 진단으로 주장하지 않는다.
- [Apollo Zephyr QVP 설정](../../../hsoc-stack/yocto/meta-hsoc-bsp/recipes-kernel/zephyr-kernel/zephyr-demos-cl1-apollo-qvp.inc): board, HIPC/PFDI overlay와 module.

## S3. 전원·타이밍 정책

- [power_and_performance_control.rst](../../../arm-zena-css/documentation/design/power_and_performance_control.rst): PSCI와 SCMI 경로.
- [현재 QVP DTS](../../../hsoc-stack/components/primary_compute/linux/arch/arm64/boot/dts/hsoc/apollo-qvp.dtsi): WFI 기본, PSCI CPU/cluster idle opt-in.
- [QBox timing include](../../../hsoc-stack/yocto/meta-hsoc-bsp/conf/machine/include/apollo-qvp-qbox-timing.inc): 가상 플랫폼용 PFDI timing.
- [SCP QVP 설정](../../../hsoc-stack/yocto/meta-hsoc-bsp/recipes-bsp/scp-firmware/scp-firmware-apollo-qvp.inc): fast channel 비활성화.

## S4. 부트와 펌웨어 조립

- [boot_process.rst](../../../arm-zena-css/documentation/design/boot_process.rst): RSE-first 부트, 이미지 로딩, CL0의 AP/CL1 기동, FIP 구성.
- [firmware-apollo-common.inc](../../../hsoc-stack/yocto/meta-hsoc-bsp/recipes-bsp/images/firmware-apollo-common.inc): 참조 firmware recipe `require` 및 파일 검색 경로 재사용.
- [firmware-fvp-rd-aspen.bb](../../../arm-zena-css/yocto/meta-zena-css-bsp/recipes-bsp/images/firmware-fvp-rd-aspen.bb): `DEPENDS`, `do_sign_images`, `fiptool`, FWU metadata와 `genimage` 선행 관계.
- [firmware-apollo-qvp.bb](../../../hsoc-stack/yocto/meta-hsoc-bsp/recipes-bsp/images/firmware-apollo-qvp.bb): TF-M 구성에서 OTP 생성, 최종 이미지 반영.
- [firmware.cfg](../../../arm-zena-css/yocto/meta-zena-css-bsp/recipes-bsp/images/files/fvp-rd-aspen/firmware.cfg): ROM DMA ICS offset, RSE primary/secondary, AP FIP_A/FIP_B의 위치·초기 채움 정책.
- [OP-TEE SP 통합](../../../layers/meta-arm/meta-arm/recipes-security/optee/optee-os-ts.inc): TS UUID ELF/manifest를 `SP_PATHS`로 전달. [TF-A 설정](../../../hsoc-stack/yocto/meta-hsoc-bsp/recipes-bsp/trusted-firmware-a/trusted-firmware-a-apollo-qvp.inc)은 BL32/BL33의 FIP 통합을 구성한다.
- [QVP 이미지 설정](../../../hsoc-stack/yocto/meta-hsoc-auto-solutions/recipes-core/images/include/nexios-apollo-qboxboot.inc): firmware FDT와 구분한 OS DTB, QBox 이미지 매핑.

## S5. Yocto 레이어와 설정

- [Arm integration](../../../arm-zena-css/documentation/design/integration.rst), [Arm reproduce](../../../arm-zena-css/documentation/user_guide/reproduce.rst): 참조 kas/Yocto/FVP 경로.
- [BSP layer.conf](../../../hsoc-stack/yocto/meta-hsoc-bsp/conf/layer.conf): `LAYERDEPENDS`, `HSOC_APOLLO_*_SRC`; BSP 명시 우선순위는 없음.
- [Product layer.conf](../../../hsoc-stack/yocto/meta-hsoc-auto-solutions/conf/layer.conf): priority 12, `BBFILES_DYNAMIC`, Cassini Mender 상속 제거.
- [apollo-qvp.conf](../../../hsoc-stack/yocto/meta-hsoc-bsp/conf/machine/apollo-qvp.conf): 참조 머신 상속과 compatibility override, `KMACHINE`, firmware/WKS 선택.
- [auto-ad-nexios.conf](../../../hsoc-stack/yocto/meta-hsoc-auto-solutions/conf/distro/auto-ad-nexios.conf): Cassini 기반, PREEMPT_RT provider, dm-verity 정책.
- [QVP template](../../../hsoc-stack/yocto/meta-hsoc-auto-solutions/conf/templates/apollo-qvp/): 지속 관리되는 설정 원본.
- [U-Boot common](../../../hsoc-stack/yocto/meta-hsoc-bsp/recipes-bsp/u-boot/u-boot-apollo-common.inc), [Nexios fragment](../../../hsoc-stack/yocto/meta-hsoc-bsp/recipes-bsp/u-boot/files/apollo-qvp-auto-ad-nexios.cfg): defconfig와 제품 부팅 정책의 결합.
- 로컬 `build/conf/{local.conf,bblayers.conf,templateconf.cfg}`를 직접 확인했다. `bitbake -e`의 최종 확장 결과를 얻은 것은 아니다.

## S6. 로컬 소스 통합

- [Linux common](../../../hsoc-stack/yocto/meta-hsoc-bsp/recipes-kernel/linux/linux-yocto-apollo-common.inc): externalsrc, 참조 kmeta 제거, defconfig/fragment 및 checksum.
- [TF-A common](../../../hsoc-stack/yocto/meta-hsoc-bsp/recipes-bsp/trusted-firmware-a/trusted-firmware-a-apollo-common.inc), [TF-M common](../../../hsoc-stack/yocto/meta-hsoc-bsp/recipes-bsp/trusted-firmware-m/trusted-firmware-m-apollo-common.inc): 로컬 소스 및 추가 dependency.
- [SCP common](../../../hsoc-stack/yocto/meta-hsoc-bsp/recipes-bsp/scp-firmware/scp-firmware-apollo-common.inc), [Zephyr common](../../../hsoc-stack/yocto/meta-hsoc-bsp/recipes-kernel/zephyr-kernel/zephyr-demos-cl1-apollo-common.inc): 관리 도메인의 로컬 코드·module 조합.
- [QBox provider](../../../hsoc-stack/yocto/meta-hsoc-bsp/recipes-devtools/qbox/qbox-apollo-qvp-native.bb), [libqemu provider](../../../hsoc-stack/yocto/meta-hsoc-bsp/recipes-devtools/qbox/qbox-libqemu-native.bb): native source/build/sysroot 구성.
- [externalsrc class](../../../layers/poky/meta/classes/externalsrc.bbclass): fetch/unpack/patch 대체, 보조 입력 유지, sstate 생성 제외.
- [TS 참조 통합](../../../arm-zena-css/yocto/meta-zena-css-bsp/recipes-security/trusted-services/ts-fvp-rd-aspen.inc), [TF-M export](../../../arm-zena-css/yocto/meta-zena-css-bsp/recipes-bsp/trusted-firmware-m/trusted-firmware-m-fvp-rd-aspen.inc): upstream TS fetch/patch와 FWU interface header 전달.
- 도메인별 툴체인·ABI 및 source→recipe→consumer 대응은 [구현 연결표 1–2절](ENGINEERING-MAP.md#1-component--recipe--artifact--consumer)에 수록했다.

## S7. UKI, rootfs와 디스크 조립

- [nexios-image.bbappend](../../../hsoc-stack/yocto/meta-hsoc-auto-solutions/recipes-core/images/nexios-image.bbappend): 제품 저장 정책, verity metadata deploy, UKI class.
- [nexios-initramfs-image.bb](../../../hsoc-stack/yocto/meta-hsoc-auto-solutions/recipes-core/images/nexios-initramfs-image.bb): 제품 verity 태스크 의존, `.verity.env`의 initramfs 포함.
- [auto-ad-nexios-uki-ab.bbclass](../../../hsoc-stack/yocto/meta-hsoc-auto-solutions/classes/auto-ad-nexios-uki-ab.bbclass): kernel/initrd/DTB/stub 입력, A/B cmdline, ESP 파일, UEFI 서명 기본 정책.
- [upstream uki.bbclass](../../../layers/poky/meta/classes-recipe/uki.bbclass): initramfs 및 native 도구 의존, `do_uki` 순서.
- [제품 WKS](../../../hsoc-stack/yocto/meta-hsoc-bsp/wic/apollo-qvp-auto-ad-nexios-ab.wks.in): 파티션 크기·label, verity rawcopy.
- [BSP recipe](../../../hsoc-stack/yocto/meta-hsoc-auto-solutions/recipes-core/images/nexios-bsp-initramfs.bb): cpio.gz/WIC, dm-verity 제거, BSP UKI 명칭과 태스크 순서.
- [Apollo machine](../../../hsoc-stack/yocto/meta-hsoc-bsp/conf/machine/apollo-qvp.conf): `pn-nexios-image`에서 systemd-boot aliases/script 추가. BSP는 직접 slot UKI 경로다.

## S8. qboxconf 계약

- [qboxboot.bbclass](../../../hsoc-stack/yocto/meta-hsoc-auto-solutions/classes/qboxboot.bbclass): JSON 필드, 상대 경로 검증, provider sysroot dependency, 생성 태스크 및 symlink.
- [공통 QVP 이미지 설정](../../../hsoc-stack/yocto/meta-hsoc-auto-solutions/recipes-core/images/include/nexios-apollo-qboxboot.inc): `QBOX_PROVIDER`, `QBOX_EXE`, `QBOX_CONFIG`, images/env.
- [공통 reader](../../../scripts/run/qbox_qboxconf_common.sh): provider·sysroot 경로 해석과 image lookup. kernel metadata와 DTB identity의 실제 소비 차이를 대조했다.
- 기존 `build/tmp_baremetal/deploy/images/apollo-qvp/`와 제품 `.qboxconf`도 대조했다. 해당 파일의 존재를 새 빌드 성공 증거로 사용하지 않는다.

## S9. 빌드 진입점과 task 연결

- [yocto_build.sh](../../../yocto_build.sh): machine/target, `KEEP_CONF`, 환경 초기화, 자원 제한과 BitBake 호출. dry-run 전에 conf 쓰기가 발생한다.
- [QVP 이미지 include](../../../hsoc-stack/yocto/meta-hsoc-auto-solutions/recipes-core/images/include/nexios-apollo-qboxboot.inc): `ukiboot`·vMCU 관련 deploy 의존성.
- [QBox native recipe](../../../hsoc-stack/yocto/meta-hsoc-bsp/recipes-devtools/qbox/qbox-apollo-qvp-native.bb): core checksum, configure 네트워크 정책, `do_check`·제외 테스트 및 install/populate_sysroot.
- 그림 10은 recipe 정적 분석으로 재구성한 주요 데이터·태스크 의존성이다. sstate hit, 실제 실행 순서, 전체 DAG는 이번 작업에서 측정하지 않았다.

## S10. Launcher와 QBox 구성

- [run_qbox_yocto.sh](../../../run_qbox_yocto.sh): `.qboxconf` 해석, provider·image·library 경로, tmux/headless 분기, BSP companion, probe 비활성화.
- [full runner](../../../scripts/run/run_qbox_apollo_fvp_full.py): preflight, runtime child, 부팅 관측, 결과 기록.
- [runtime engine](../../../scripts/run/qbox_apollo_runtime.py): `platforms-vp -l … -p …` 실행, writable/영속 상태와 keep-running 정책.
- [vMCU boot helper](../../../scripts/run/qbox_vmcu_boot.py): BSP + UART vMCU의 private WIC 생성과 UKI cmdline 주입.
- [installed Lua의 소스 entrypoint](../../../hsoc-stack/tools/qbox-platform/platforms/apollo/apollo-qvp-saturn-v.lua), [full-system profile](../../../hsoc-stack/tools/qbox-platform/platforms/apollo/vp/profiles/full-system.lua), [composition](../../../hsoc-stack/tools/qbox-platform/platforms/apollo/vp/composition.lua): VP/SoC/board의 생성·적용 순서.
- [SoC](../../../hsoc-stack/tools/qbox-platform/platforms/apollo/soc/apollo.lua), [QBox platform README](../../../hsoc-stack/tools/qbox-platform/README.md): 하드웨어 구성과 core/overlay/QEMU 소유권.
- [AP loader](../../../hsoc-stack/tools/qbox-platform/platforms/apollo/vp/ap_compute/boot.lua), [RSE boot](../../../hsoc-stack/tools/qbox-platform/platforms/apollo/vp/rse/boot.lua), [CL0](../../../hsoc-stack/tools/qbox-platform/platforms/apollo/vp/si_cl0/si_cl0.lua), [CL1](../../../hsoc-stack/tools/qbox-platform/platforms/apollo/vp/si_cl1/si_cl1.lua): 이미지 입력, PPU load/reset, SRAM 및 ELF entry의 실제 연결.

## S11. Component SW / Source / Build / Deploy Architecture

상세 문서의 각 Source 표는 실제 구현 파일에 연결된다. 그림의 소스 경로는 기준 저장소 아래 경로이며 외부 소유 소스·metadata는 별도 표시한다.

각 컴포넌트의 Build Architecture와 Deploy artifacts 절은 owning recipe/include 및 build system의 configure/compile/install/deploy 규칙을 대조해 작성했다. `${S}`·`${B}`·toolchain과 task 선행 관계, deploy·sysroot·중간 출력의 배치 위치를 구분하며, recipe 최종 확장을 실행하거나 새 산출물을 생성한 결과는 아니다.

| 문서 | 추가로 추적한 연결 |
|---|---|
| [Primary Compute](components/primary-compute.md) | Linux 외부 HIPC/PFDI 모듈; U-Boot slot/CRC·EFI·PSA FWU; TF-A image descriptor·PSCI override·RSE measurement; OP-TEE SP 생성·manifest boot-order·FF-A dispatcher |
| [System Management](components/system-management.md) | TF-M platform별 stage·SPM·SCMI; SCP lifecycle·module 순서·PMIC; Zephyr kernel/Arm app/HSOC board; vMCU worker·protocol·TriCore compatibility port |
| [Virtual Platform](components/virtual-platform.md) | libqemu C API와 C++ binding; QOM/TCG/MemoryRegion; QBox thread/TLM/DMI; Apollo SoC/VP/board 및 모델 설치 |
| [Build Integration](components/build-integration.md) | HSOC source registry·machine·adapter; 제품 image/class; 별도 보존 Buildroot의 Make/Kconfig/package/rootfs 구조 |

그림은 [draw.io XML 형식](https://raw.githubusercontent.com/jgraph/drawio-mcp/main/shared/xml-reference.md)의 native 도형·connector로 작성했다. 전체 편집본은 [apollo-build-architecture.drawio](apollo-build-architecture.drawio)이며, 27페이지의 배경·도형을 흰색으로 지정하고 자동 색상 변환을 사용하지 않는다.

## 검증 범위

수행: 문서·원본 그림 검토, component 구현·recipe/스크립트/config 대조, Markdown 상대 링크·anchor 확인, 27페이지 draw.io XML과 SVG export, 렌더 결과 확인.

미수행: BitBake 파싱/`-e`/`-g`, 컴파일, 새 이미지 빌드, QBox/FVP 부팅, 하드웨어·타이밍·보안 qualification. 원본 Arm 설계에 등장하는 기능을 Apollo의 검증 완료 기능으로 승격하지 않았다.
