# HSOC Component Architecture

[세미나 본문](../README.md) · [전체 draw.io 편집본](../apollo-build-architecture.drawio) · [recipe·산출물 연결표](../ENGINEERING-MAP.md)

각 그림은 **왼쪽: SW subsystem과 인터페이스 / 오른쪽: 소스 구성과 확장점 / 하단: build input과 artifact consumer**로 구성한다. 흰 배경의 native draw.io 도형이며, SVG에도 편집용 XML이 포함되어 있다.

각 컴포넌트는 다음 네 절로 구성한다. **Source → Build → Deploy**를 따라가면 수정할 파일, 다시 생성할 출력, 다음 소비자를 연결할 수 있다.

| 절 | 다루는 내용 |
|---|---|
| Component SW Architecture | 내부 subsystem, API·데이터 경로, 실행 도메인 |
| Source Architecture | 실제 디렉터리·대표 파일·Apollo 확장점과 외부 소스 소유권 |
| Build Architecture | 선택 recipe·설정, source/build 디렉터리, toolchain·ABI, 선행 task |
| Deploy artifacts | 파일명·배치 위치·후속 소비자; 최종 이미지와 sysroot·중간 출력을 구분 |

| draw.io 페이지 | 컴포넌트 | SW Architecture의 초점 | Source Architecture의 초점 |
|---|---|---|---|
| C01 | [Linux](primary-compute.md#1-linux--ap-실행-환경과-도메인-간-드라이버) | RT kernel, PSCI/SCMI/FF-A, HIPC | DT/defconfig, firmware transport, 외부 HIPC/PFDI modules |
| C02 | [U-Boot](primary-compute.md#2-u-boot--슬롯-선택과-uefi-실행서비스) | slot 선택, UEFI, 보안 변수, FWU client | board, cmd, EFI/FWU library, 제품 fragment |
| C03 | [TF-A](primary-compute.md#3-tf-a--ap-인증-부트와-el3-runtime) | BL2, BL31, PSCI/SPMD, PFDI/RAS | Apollo platform, image descriptor, EL3 service |
| C04 | [OP-TEE](primary-compute.md#4-op-tee--s-el1-spmc와-secure-partition-실행) | SPMC, SP lifecycle, memory sharing | 재사용 platform, SP 생성기, FF-A dispatcher |
| C05 | [TF-M](system-management.md#trusted-firmware-m--rse-부트와-보안-서비스) | RSE boot, SPM/PSA, SCMI, FWU | 공통 SPM, Apollo platform/stage/HAL |
| C06 | [SCP-firmware](system-management.md#scp-firmware--si-cl0-시스템-관리) | framework, SCMI, power, PFDI, PMIC | 공통 module, Apollo product/module/config |
| C07 | [Zephyr kernel](system-management.md#zephyr-kernel--cl1-실행-기반) | SMP, networking, HIPC, mailbox | kernel/arch, Arm sample/module, Yocto composition |
| C08 | [zephyr_hsoc_src](system-management.md#zephyr_hsoc_src--apollo-cl1-board-확장) | board 등록, timer/network hook | module.yml, DTS/defconfig, overlays, 선택 sample |
| C09 | [zephyr_vmcu_src](system-management.md#zephyr_vmcu_src--외부-tc397-companion) | 관리 RPC, safety, UART/SPI, CAN | app, protocol library, board/driver, TriCore port |
| C10 | [QEMU/libqemu](virtual-platform.md#1-qemu--libqemu) | QOM, CPU/TCG, memory, host I/O | libqemu, target/accel, qom/system, hw/backend |
| C11 | [QBox core](virtual-platform.md#2-qbox-core) | CCI, QemuInstance, TLM/DMI, sync | factory, wrappers, transport, common models |
| C12 | [QBox platform](virtual-platform.md#3-qbox-platform--apollo-overlay) | SoC/VP/board, Apollo 모델 구성 | CMake, Lua hierarchy, SystemC/QEMU extensions |
| C13 | [meta-hsoc-bsp](build-integration.md#meta-hsoc-bsp--플랫폼과-로컬-소스-통합) | 플랫폼·component·firmware 통합 | source registry, machine, recipe adapters, WKS |
| C14 | [meta-hsoc-auto-solutions](build-integration.md#meta-hsoc-auto-solutions--nexios-제품과-실행-계약) | 제품 image, storage, UKI, qboxconf | distro/template, recipe, class, dynamic layers |
| C15 | [Buildroot](build-integration.md#buildroot--보존-중인-별도-빌드-시스템) | 보존된 Make/Kconfig 빌드 시스템 | package, toolchain, board, filesystem generator |

Trusted Services는 HSOC 로컬 component checkout이 아닌 외부 recipe 소스다. OP-TEE의 SP 공급자로 다루며 [펌웨어 조립](../README.md#51-펌웨어-여러-컴포넌트의-결과를-저장-매체로-조립)에서 연결한다. Buildroot는 현재 지원하는 root 빌드 흐름에 포함되지 않는다.

## 경로·산출물 표기

현재 `build/conf/`의 `MACHINE=apollo-qvp`, `DISTRO=auto-ad-nexios`, `TMPDIR=${TOPDIR}/tmp_baremetal`을 기준으로 한다. 아래 변수는 **각 recipe의 문맥**에서 해석한다.

| 표기 | 의미 / 현재 기준 위치 |
|---|---|
| `${S}`, `${B}` | 해당 recipe의 소스와 빌드 디렉터리. `EXTERNALSRC`는 로컬 checkout을 가리키며 `${B}`는 recipe별로 결정 |
| `${D}` | `do_install`이 파일을 배치하는 임시 설치 루트 |
| `${DEPLOYDIR}` → `${DEPLOY_DIR_IMAGE}` | recipe별 deploy staging → `build/tmp_baremetal/deploy/images/apollo-qvp/` |
| `${IMGDEPLOYDIR}` | image recipe의 중간 배포 영역; 완료 후 machine deploy 디렉터리로 전달 |
| `${RECIPE_SYSROOT}` / `${RECIPE_SYSROOT_NATIVE}` | 소비 recipe에 준비된 target 의존 입력 / host 도구·라이브러리 |
| `${COMPONENTS_DIR}` | `build/tmp_baremetal/sysroots-components/`; recipe별 설치 결과를 모아 다른 recipe의 sysroot에 전달 |

Deploy artifacts는 `do_deploy` 출력에만 한정하지 않는다. OP-TEE 같은 firmware의 sysroot 입력, QBox의 native 설치 결과, 디버그 ELF를 각각 명시한다. 독립 빌드 대상이 아닌 board module·metadata layer에는 별도 실행 바이너리가 없음을 표시했다.

기준은 현재 checkout의 정적 구조다. 각 소스 표의 파일 링크와 [설계 근거](../SOURCES.md)를 통해 확인할 수 있다.
