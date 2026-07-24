# Nexios BSP 전용 최소 initramfs 구현 계획

- 문서 상태: 구현 및 검증 완료
- 작성일: 2026-07-23
- 대상 머신: `apollo-fvp`, `apollo-qvp`
- 신규 BitBake 이미지: `nexios-bsp-initramfs`
- 대상 진입점: `yocto_build.sh`, `run_qbox_yocto.sh`

## 1. 목적

현재 `nexios-image`의 정상 부팅은 Linux가 dm-verity용 initramfs를
실행한 다음 검증된 root filesystem으로 `switch_root`하는 제품 부팅
경로이다. 이 경로는 제품 동작 검증에는 필요하지만, Linux BSP의 반복
검증에서는 root filesystem 생성·전송·검증·userspace 기동 시간이
불필요하게 포함된다.

본 계획의 목적은 다음과 같다.

1. BusyBox 기반 `nexios-bsp-initramfs`를 별도 이미지로 만든다.
2. Linux가 이 initramfs의 `/init`를 실행한 뒤 BusyBox 셸에서 부팅을
   완료하도록 한다.
3. RSE, Safety Island, TF-A, U-Boot, UKI, Linux까지의 기존 전체 시스템
   부팅 경로는 유지한다.
4. dm-verity rootfs와 제품 userspace는 BSP 빠른 검증 경로에서만
   제외하고, 기존 `nexios-image` 동작은 변경하지 않는다.
5. `apollo-fvp`와 `apollo-qvp`가 공통으로 사용할 수 있는 최소 패키지와
   재현 가능한 콘솔 검증 계약을 제공한다.

## 2. 결론 요약

권장 구현은 `nexios-bsp-initramfs` 한 recipe가 다음 산출물을 함께
생성하는 방식이다.

- BusyBox root filesystem: `nexios-bsp-initramfs-${MACHINE}.cpio.gz`
- A/B BSP UKI가 들어 있는 boot-only WIC:
  `nexios-bsp-initramfs-${MACHINE}.wic`
- QVP 실행 메타데이터:
  `nexios-bsp-initramfs-apollo-qvp.qboxconf`
- 이미지 manifest와 테스트 결과

raw CPIO만 생성하는 방식은 채택하지 않는다. 현재
`run_qbox_yocto.sh`는 WIC를 `--rootfs`로 전체 시스템 runner에 전달하며
(`run_qbox_yocto.sh:934-951`, `run_qbox_yocto.sh:1182-1197`), QVP에서는
이미지 이름에 대응하는 `.qboxconf`도 요구한다
(`run_qbox_yocto.sh:875-896`,
`scripts/run/qbox_qboxconf_common.sh:26-60`). 따라서 raw CPIO 직접 부팅을
추가하려면 QEMU 직접 kernel/initrd 로더 또는 QBox platform 로더를 새로
만들어야 하고, 이 경우 U-Boot/UKI 경로를 우회하여 BSP 검증 범위도
줄어든다.

boot-only WIC는 단일 `boot` ESP와 기존 A/B 상태를 보존하는 `misc`
partition만 유지한다. A/B UKI는 `boot` 안의 `EFI/Linux/a-slot`과
`EFI/Linux/b-slot`에 배치하고 각 디렉터리의 `metadata`로 slot identity를
검증한다. 8 GiB dm-verity root partition 두 개와 `rootrw`, `data`
partition은 만들지 않는다. 현재 제품 WKS의 partition 구성은
`hsoc-stack/yocto/meta-hsoc-bsp/wic/apollo-qvp-auto-ad-nexios-ab.wks.in:11-20`
및
`hsoc-stack/yocto/meta-hsoc-bsp/wic/apollo-fvp-auto-ad-nexios-ab.wks.in:11-20`
에 정의되어 있다.

## 3. 요구사항별 외부 계약

| 요구사항 | 구현 계약 |
| --- | --- |
| 신규 이미지 이름 | BitBake target과 artifact basename 모두 `nexios-bsp-initramfs` |
| 기본 `yocto_build.sh` | `nexios-image`와 `nexios-bsp-initramfs`를 한 BitBake 호출로 빌드 |
| 기존 dm-verity initramfs | `nexios-image`가 기존 dependency로 계속 생성 |
| `yocto_build.sh --bsp` | top-level target은 `nexios-bsp-initramfs` 하나만 전달 |
| `run_qbox_yocto.sh --bsp` | image basename, WIC, QVP qboxconf, 성공 마커를 BSP profile로 전환 |
| 정상 부팅 | 옵션이 없으면 현재 `nexios-image` 동작과 로그인 판정을 그대로 유지 |
| BSP 완료 지점 | `/init`의 self-test 후 `NEXIOS_BSP_INITRAMFS_READY` 출력 및 콘솔 셸 진입 |
| dm-verity | BSP UKI command line과 init script에서 사용하지 않음 |
| FVP/QVP 공통성 | recipe와 init script는 공통, WKS와 일부 검증 항목만 machine override |

예상 CLI는 다음과 같다.

```bash
# 제품 이미지 + 기존 dm-verity initramfs + BSP initramfs
./yocto_build.sh --machine apollo-qvp

# BSP 이미지 산출물만 생성
./yocto_build.sh --machine apollo-qvp --bsp
./yocto_build.sh --machine apollo-fvp --bsp

# QBox에서 BSP initramfs 부팅
./run_qbox_yocto.sh --bsp --headless --exit-after-pass --timeout 180
```

`--dm-verity=on|off`를 명시한 경우에는 현재와 동일한 multiconfig를
사용하되 BSP recipe 자체는 `APOLLO_DM_VERITY` 값과 무관하게 동일한
산출물을 만들어야 한다. 예를 들어 `--dm-verity=on --bsp`는
`mc:apollo-qvp-dm-verity:nexios-bsp-initramfs` 하나만 빌드한다. 이 규칙은
기존 build directory/TMPDIR 선택 계약을 유지하면서 BSP 이미지가 제품
dm-verity image를 dependency로 끌어오는 것을 막는다.

## 4. 현재 상태와 목표 부팅 흐름

현재 distro는 `APOLLO_DM_VERITY=1`일 때
`INITRAMFS_IMAGE=nexios-initramfs-image`와 `INITRD_ARCHIVE`를 설정한다
(`hsoc-stack/yocto/meta-hsoc-auto-solutions/conf/distro/auto-ad-nexios.conf:20-28`).
현재 initramfs는 `cryptsetup`, dm-verity init script, LVM, udev를 포함하고
있다
(`hsoc-stack/yocto/meta-hsoc-auto-solutions/recipes-core/images/nexios-initramfs-image.bb:7-17`).

```mermaid
flowchart LR
    A[RSE / SI firmware] --> B[TF-A]
    B --> C[U-Boot]
    C --> D[boot ESP의 a-slot / b-slot UKI]
    D --> E[Linux kernel]
    E --> F[nexios-initramfs-image]
    F --> G[dm-verity rootro]
    G --> H[switch_root]
    H --> I[nexios-image userspace]
```

목표 BSP 흐름은 다음과 같다.

```mermaid
flowchart LR
    A[RSE / SI firmware] --> B[TF-A]
    B --> C[U-Boot]
    C --> D[BSP boot ESP의 a-slot / b-slot UKI]
    D --> E[Linux kernel]
    E --> F[nexios-bsp-initramfs /init]
    F --> G[mount + mdev + module load]
    G --> H[non-destructive BSP self-test]
    H --> I[NEXIOS_BSP_INITRAMFS_READY]
    I --> J[BusyBox console shell]
```

두 흐름의 차이는 Linux 이후 root filesystem handoff뿐이다. BSP profile도
RSE/SI firmware, AP flash, U-Boot, DTB와 CPU topology를 동일하게 사용한다.

## 5. 산출물 설계

### 5.1 CPIO

`nexios-bsp-initramfs.bb`는 `cpio.gz`를 생성한다.

```text
tmp_baremetal/deploy/images/${MACHINE}/
└── nexios-bsp-initramfs-${MACHINE}.cpio.gz
```

필수 내용은 다음과 같다.

- 실행 가능한 `/init`
- BusyBox와 applet link
- `/etc/passwd`, `/etc/group`, 기본 filesystem hierarchy
- `kmod`, `mount`, `lsblk`, `ip`, `perf`
- 선택한 Apollo 외부 kernel module과 그 dependency
- `/usr/libexec/nexios-bsp/`의 비파괴 self-test

`/init`는 PID 1이므로 마지막에 종료해서는 안 된다. 초기화와 self-test를
마친 후 준비 마커를 출력하고 `/dev/console`에 BusyBox `sh`를 `exec`한다.

### 5.2 boot-only WIC

machine별 신규 WKS를 추가한다.

- `hsoc-stack/yocto/meta-hsoc-bsp/wic/apollo-fvp-nexios-bsp-initramfs.wks.in`
- `hsoc-stack/yocto/meta-hsoc-bsp/wic/apollo-qvp-nexios-bsp-initramfs.wks.in`

partition은 다음 두 개만 둔다.

| Partition | 목적 | 초기 크기 |
| --- | --- | ---: |
| `boot` | a-slot/b-slot UKI와 slot별 `metadata`를 포함하는 단일 ESP | 256 MiB |
| `misc` | 기존 A/B boot-state 계약 유지 | 4 MiB |

초기 ESP 크기는 기존 두 128 MiB ESP의 합계를 유지한다. 이에 따라 두
UKI의 성장 여유와 `misc` 이후 partition offset을 모두 보존한다. root
partition이 없으므로 WIC 크기는 제품 WIC보다 크게 줄어든다.

### 5.3 BSP UKI

각 slot은 같은 kernel, DTB, CPIO를 사용하되 이름을 제품 UKI와 분리한다.

```text
nexios-bsp-initramfs-a.efi
nexios-bsp-initramfs-b.efi
```

내장 command line은 다음 의미를 가져야 한다.

```text
rdinit=/init rw console=${KERNEL_CONSOLE} ${BOOTLOADER_LINUX_APPEND}
```

다음 항목은 없어야 한다.

- `root=PARTLABEL=rootro_a` 또는 `rootro_b`
- `rootwait`
- `ro`
- dm-verity parameter

현재 A/B UKI class의 제품 기본값은 root partition을 명시한다
(`hsoc-stack/yocto/meta-hsoc-auto-solutions/classes/auto-ad-nexios-uki-ab.bbclass:42-46`).
BSP recipe에서만 별도의 파일명과 command line을 설정한다.

### 5.4 QVP qboxconf

`apollo-qvp`에서는 BSP image가 자신의 `.qboxconf`를 생성해야 한다.
`qboxboot.bbclass`는 image name을 기준으로 qboxconf와 link를 생성한다
(`hsoc-stack/yocto/meta-hsoc-auto-solutions/classes/qboxboot.bbclass:141-153`).

현재 `nexios-image.bbappend:6-23`의 QBox provider, executable, Lua config,
CPU count, firmware image mapping은 두 image가 공유해야 한다. 해당 설정을
다음 include로 이동하는 것을 권장한다.

```text
hsoc-stack/yocto/meta-hsoc-auto-solutions/
└── recipes-core/images/include/nexios-apollo-qboxboot.inc
```

include는 `nexios-image`와 `nexios-bsp-initramfs`에 각각 적용하되,
`QBOX_IMAGES[rootfs_wic]`는 각 recipe의 `${IMAGE_LINK_NAME}.wic`를
가리키게 한다. `rootfs_verity`와 `rootfs_verity_env` key는 제품 image에만
남긴다. 이를 통해 `yocto_build.sh --bsp`가 이전 `nexios-image` 산출물에
의존하지 않고 단독으로 실행된다.

## 6. 이미지 패키지 목록

### 6.1 기본 포함 패키지

초기 `PACKAGE_INSTALL`은 다음으로 고정한다. 전역
`EXTRA_IMAGE_FEATURES`에 설정된 demos/OpenSSH가 유입되지 않도록
`PACKAGE_INSTALL`, `IMAGE_FEATURES`, `EXTRA_IMAGE_FEATURES`를 recipe에서
명시한다. 현재 active `local.conf`에는 baremetal, login, OpenSSH, demos가
전역으로 추가되어 있으므로 이 차단이 필요하다
(`build/conf/local.conf:17-24`, `build/conf/local.conf:45-46`).

| 패키지 | 용도 | 필수 이유 |
| --- | --- | --- |
| `base-files` | 기본 directory와 설정 | initramfs filesystem 골격 |
| `base-passwd` | root 사용자/group | BusyBox 셸과 파일 소유권 |
| `busybox` | `sh`, `dmesg`, `cat`, `grep`, `mdev`, `hwclock`, `watchdog` 등 | 최소 userspace |
| `nexios-bsp-init` | 신규 `/init`와 self-test | 준비 마커, mount, module load, console shell |
| `kmod` | `modprobe`, `modinfo`, `depmod` | 외부 BSP module의 결정적 로딩 |
| `util-linux-mount` | filesystem mount | proc/sysfs/debugfs/configfs 검증 |
| `util-linux-lsblk` | virtio block와 WIC partition 확인 | boot media/block BSP 확인 |
| `iproute2-ip` | link/address/statistics 확인 | virtio-net 및 RPMsg network 확인 |
| `perf` | DSU PMU event 측정 | 기존 DSU 테스트가 `perf stat` 사용 |
| `arm-si-rproc-mod` | Safety Island remoteproc driver | HIPC/RPMsg bring-up |
| `kernel-module-virtio-rpmsg-bus` | RPMsg virtio transport | `NO_RECOMMENDATIONS=1`에서도 명시적으로 포함 |
| `rpmsg-net-mod` | RPMsg network driver | AP-SI network smoke test |
| `pfdi-misc-mod` | PFDI misc kernel driver | PFDI driver probe와 device-node 확인 |
| `pfdi-bsp-app` | `pfdi-sample-app` C 실행 파일과 Apollo 설정 | SI0 PFDI monitor에 AP heartbeat를 주기적으로 전송 |

`kernel-module-virtio-rpmsg-bus`의 현재 pkgdata dependency는
`kernel-module-rpmsg-core`와 `kernel-module-rpmsg-ns`를 함께 가져온다.
구현 시 `oe-pkgdata-util`과 최종 manifest로 두 machine 모두에서 이
dependency가 유지되는지 확인한다. `arm-mhuv3`는 현재 QVP kernel에서
built-in이므로 존재하지 않는 `kernel-module-arm-mhuv3`를 강제로
`PACKAGE_INSTALL`에 추가하지 않는다. FVP/QVP 최종 kernel config가
다르면 machine override로만 보완한다.

DSU PMU 검증에 `perf`가 필요한 근거는 기존 테스트의
`perf stat -e arm_dsu_*` 호출이다
(`arm-zena-css/yocto/meta-zena-css-bsp/lib/oeqa/runtime/cases/test_20_aspen_ap_dsu.py:67-84`).

### 6.2 기본 제외 패키지

| 제외 항목 | 이유 |
| --- | --- |
| `cryptsetup` | dm-verity rootfs를 열지 않음 |
| `initramfs-module-dmverity` | BSP profile은 dm-verity handoff가 없음 |
| `initramfs-module-udev` | BusyBox `mdev` 사용 |
| `lvm2` | BSP initramfs에 논리 볼륨이 없음 |
| `udev`, `systemd` | PID 1과 device population을 BusyBox로 처리 |
| `ssh-server-openssh`, `ssh-pregen-hostkeys` | 콘솔 검증으로 대체하고 image 크기/기동 시간 절감 |
| `packagegroup-core-boot` | 제품 userspace 구성의 암묵적 유입 방지 |
| `kernel-modules` | 전체 module 설치 금지, 필요한 package만 명시 |
| container/cloud/demo packagegroup | BSP bring-up 범위 밖 |
| `pfdi-demo-app` | Python 3, PyYAML, systemd service metadata를 동반 |

실제 FVP 장기 실행에서 PFDI misc driver probe만 수행하면 SI0 monitor가
AP 4개 core의 heartbeat timeout을 보고하는 것을 확인했다. 이에 기존
`platform-fault-detection` recipe의 산출물을 `pfdi-bsp-app`으로 분리해
`pfdi-sample-app`과 설정 파일만 포함했다. 기존 `pfdi-demo-app`은 이
패키지에 의존하므로 제품 이미지 동작은 유지되며, BSP 이미지에는
`python3` 실행 환경, PyYAML, systemd metadata가 유입되지 않는다.
단, DSU PMU 검증용 `perf`의 동적 링크 의존으로 `libpython3.13`은
manifest에 남는다.

### 6.3 조건부 진단 패키지

다음은 기본 이미지에 넣지 않고, 실제 acceptance가 요구할 때만 추가한다.

| 패키지 | 추가 조건 |
| --- | --- |
| `ethtool` | link feature/driver statistics가 BSP 판정 조건일 때 |
| `iperf2` | HIPC/RPMsg throughput이 smoke test가 아니라 필수 조건일 때 |
| `iputils-ping` | 대상 BusyBox에 `ping` applet이 없을 때 |
| `trace-cmd` | kernel trace 기반 원인 분석 image가 필요할 때 |
| `strace` | userspace syscall 분석이 필요할 때 |
| `pfdi-demo-app` | PFDI reference application의 end-to-end 실행이 명시적으로 필요할 때 |
| OpenSSH | 콘솔 runner로 수행할 수 없는 원격 OEQA가 반드시 필요할 때 |

조건부 패키지를 기본 목록에 섞지 않는다. 필요한 경우 별도
`NEXIOS_BSP_EXTRA_INSTALL` 변수나 후속 debug image를 사용하고, 기본
`nexios-bsp-initramfs`의 재현성과 크기를 유지한다.

## 7. `/init` 및 self-test 설계

신규 recipe와 파일은 다음 위치를 사용한다.

```text
hsoc-stack/yocto/meta-hsoc-auto-solutions/
└── recipes-core/initrdscripts/
    ├── nexios-bsp-init_1.0.bb
    └── nexios-bsp-init/
        ├── init
        └── nexios-bsp-selftest
```

`/init` 처리 순서는 다음과 같다.

1. `/proc`, `/sys`, `/dev`, `/run`을 준비한다.
2. 가능한 filesystem만 `debugfs`, `configfs`에 mount한다.
3. BusyBox `mdev -s`로 device node를 만든다.
4. `/lib/modules/$(uname -r)`가 있으면 `depmod -a`를 실행한다.
5. machine 공통 module과 transport를 dependency 순서대로 `modprobe`한다.
6. `pfdi-sample-app`을 시작하고 PID와 log를 `/run` 아래에 보존한다.
7. self-test를 실행하고 각 항목을 `PASS`, `FAIL`, `SKIP`으로 기록한다.
8. 필수 항목 실패가 없으면 `NEXIOS_BSP_INITRAMFS_READY`를 출력한다.
9. `PS1='nexios-bsp# '`를 설정하고 `/dev/console`에서 BusyBox 셸을
   `exec`한다.

마커는 다음처럼 machine-readable해야 한다.

```text
NEXIOS_BSP_TEST name=pl011 result=PASS
NEXIOS_BSP_TEST name=arch_timer result=PASS
NEXIOS_BSP_TEST name=dsu_cache result=PASS
NEXIOS_BSP_TEST name=si_remoteproc result=PASS
NEXIOS_BSP_TEST name=rpmsg_net result=PASS
NEXIOS_BSP_TEST name=pfdi_misc result=PASS
NEXIOS_BSP_TEST name=pfdi_service result=PASS
NEXIOS_BSP_INITRAMFS_READY machine=apollo-qvp
nexios-bsp#
```

초기 필수 self-test는 비파괴 검사만 수행한다.

- kernel command line에 `rdinit=/init`가 있고 `root=`가 없음
- PL011 console과 Linux boot 완료
- online CPU 수가 `${PC_CPUS_COUNT}`와 일치
- generic timer/clocksource와 timer interrupt가 등록됨
- RTC PL031와 `/dev/rtc*` 존재
- watchdog device와 driver 존재
- `/dev/hwrng` 읽기 가능
- virtio block와 BSP WIC partition 확인
- virtio network interface 존재
- DSU cache sysfs 값 및 `perf stat` 동작
- SI remoteproc driver probe
- RPMsg transport와 network interface probe
- PFDI misc driver와 device node probe
- PFDI sample application, 설정 파일, 실행 중인 service 확인

watchdog reset, CPU offline, PFDI fault injection처럼 대상 상태를 바꾸는
검사는 자동 기본 경로에서 수행하지 않는다. 별도 명령으로만 제공한다.

기존 `fvp_devices` 테스트의 RTC/watchdog/network/virtiorng 항목은 모두
SSH test에 의존한다
(`sw-ref-stack/yocto/meta-arm-auto-solutions/lib/oeqa/runtime/cases/test_20_fvp_devices.py:31-59`).
minimal image에 OpenSSH를 다시 넣어 기존 OEQA를 억지로 재사용하지 않고,
동일한 관측점을 console self-test와 log parser로 옮긴다.

## 8. Yocto metadata 구현 단계

### 8.1 `nexios-bsp-initramfs.bb`

신규 파일:

```text
hsoc-stack/yocto/meta-hsoc-auto-solutions/
└── recipes-core/images/nexios-bsp-initramfs.bb
```

핵심 변수와 제약:

- `inherit core-image auto-ad-nexios-uki-ab`
- `PACKAGE_INSTALL`은 6.1 목록으로 고정
- `IMAGE_FEATURES:auto-ad-nexios = ""`
- `EXTRA_IMAGE_FEATURES:auto-ad-nexios = ""`
- `IMAGE_LINGUAS = ""`
- `NO_RECOMMENDATIONS = "1"`
- `IMAGE_FSTYPES = "cpio.gz wic"`
- `INITRAMFS_IMAGE:auto-ad-nexios = ""`로 distro의 제품 initramfs
  override를 지우고 self-cycle 차단
- `WKS_FILE:apollo-fvp:auto-ad-nexios`와
  `WKS_FILE:apollo-qvp:auto-ad-nexios`에 BSP WKS를 지정하여 distro의
  제품 WKS override보다 BSP recipe 값이 최종 선택되게 함
- BSP UKI 파일명과 command line override
- QVP에서만 `qboxboot` 상속 및 공통 include 적용

`PACKAGE_INSTALL`의 최종 값은 parse history까지 확인한다. 현재
`nexios-initramfs-image`는 `PACKAGE_INSTALL`을 직접 설정하므로
(`nexios-initramfs-image.bb:7-17`), 동일한 패턴이 전역 image feature
유입을 차단하는 가장 단순한 방법이다.

`busybox --list`로 `sh`, `mdev`, `dmesg`, `cat`, `grep`, `hwclock` applet을
확인한다. 필수 applet이 없을 때만 layer-local BusyBox config fragment를
추가하고, 이미 활성화된 applet을 위해 BusyBox 구성을 별도로 복제하지
않는다.

### 8.2 기존 UKI class의 제한적 확장

새 UKI class를 복제하지 않고
`auto-ad-nexios-uki-ab.bbclass`에 다음 선택 변수를 추가하는 방식을
권장한다.

- initrd 입력 path override
- UKI output/source directory override
- 기본값은 현재 `${DEPLOY_DIR_IMAGE}/${INITRD_ARCHIVE}`와 동일

BSP recipe만 initrd 입력을
`${IMGDEPLOYDIR}/${IMAGE_NAME}.cpio.gz`로 지정하고 `do_uki`가
`do_image_cpio` 뒤에 실행되도록 task edge를 추가한다. 기존 class는
upstream `uki` class를 상속하며
`do_uki`가 `do_rootfs` 뒤, `do_image_wic` 앞에 배치된다
(`layers/poky/meta/classes-recipe/uki.bbclass:91-100`,
`layers/poky/meta/classes-recipe/uki.bbclass:194`). 현재 class는
`INITRD_ARCHIVE`를 `DEPLOY_DIR_IMAGE`에서만 찾기 때문에
(`auto-ad-nexios-uki-ab.bbclass:146-150`) 이 확장이 필요하다.

이 설계의 조건은 다음과 같다.

- 변수 기본값에서는 `nexios-image` task graph와 산출물 hash가 바뀌지 않음
- BSP recipe에서만 `do_image_cpio -> do_uki -> do_image_wic` 순서가 생김
- `INITRAMFS_IMAGE=nexios-bsp-initramfs` 같은 self-dependency를 만들지 않음
- `bitbake -g`의 `task-depends.dot`에 순환 dependency가 없어야 함

### 8.3 machine별 WKS

두 신규 WKS는 기존 제품 WKS의 boot partition과 `misc` 정의만 재사용한다.
WKS를 `meta-hsoc-bsp`에 두는 이유는 Apollo machine/firmware boot media의
소유권이 BSP layer에 있기 때문이다. product root filesystem 정책은
복사하지 않는다.

`WKS_FILE_DEPENDS`에는 기존과 같이 `auto-ad-nexios-boot-state`를
유지한다
(`auto-ad-nexios.conf:39-42`).

### 8.4 qboxboot 설정 공통화

`nexios-image.bbappend`의 QBox 공통 부분만 include로 옮긴다.

- 공통: provider, executable, Lua config, CPU count, kernel, DTB, AP/RSE/SI
  firmware artifact
- 제품 전용: dm-verity rootfs와 verity environment
- BSP 전용: BSP boot-only WIC

`qboxboot.bbclass`의 `QBOX_IMAGES` flag는 safe relative path만 허용한다
(`qboxboot.bbclass:93-112`). 따라서 qboxconf에는 stable deploy link
basename만 기록한다.

## 9. `yocto_build.sh` 변경 계획

현재 script는 단일 `BITBAKE_TARGET=nexios-image`를 사용하고
multiconfig 선택 시 그 문자열 하나만 치환한다
(`yocto_build.sh:215-243`). 이를 target array로 바꾼다.

신규 상태:

```text
BSP_ONLY=0
BITBAKE_TARGETS=(nexios-image nexios-bsp-initramfs)
```

argument parser에 `--bsp`를 추가한다.

- 기본: 두 top-level target
- `--bsp`: `nexios-bsp-initramfs` 하나
- multiconfig: 배열의 각 원소에 `mc:${DM_VERITY_MC}:` prefix 적용
- `--dry-run`: 실제 배열 순서대로 한 줄 출력

기본 빌드가 만드는 논리 산출물은 다음 세 종류이다.

1. `nexios-image` root filesystem/WIC
2. `nexios-image`가 의존하는 기존 `nexios-initramfs-image`
3. 신규 `nexios-bsp-initramfs` CPIO/WIC

`--bsp`에서는 1과 2가 dependency graph에 나타나지 않아야 한다.
특히 `bitbake -g nexios-bsp-initramfs` 결과에
`nexios-image:do_rootfs`, `dm-verity-img`, `cryptsetup`, `lvm2`가 없어야
한다.

## 10. `run_qbox_yocto.sh` 변경 계획

신규 `BSP_MODE=0`을 추가하고 `--bsp`에서 다음 값을 설정한다.

```text
IMAGE_BASENAME=nexios-bsp-initramfs
PRIMARY_LOGIN_PROMPT=NEXIOS_BSP_INITRAMFS_READY
PRIMARY_SHELL_MARKER=nexios-bsp#
PRIMARY_SHELL_PROMPT_RE=(?:^|\n)nexios-bsp#\s*$
```

설정은 qboxconf와 WIC 경로를 resolve하기 전에 적용해야 한다. 현재 basename
기본값은 `nexios-image`이며(`run_qbox_yocto.sh:558-564`), QVP qboxconf
탐색은 basename에 의존한다. BSP profile 적용이 늦으면 제품 qboxconf와
BSP WIC가 섞일 수 있다.

argument 우선순위는 다음으로 고정한다.

1. `--bsp`가 profile 기본값을 선택
2. 명시적인 artifact override(`--rootfs`, `--qboxconf`)는 기존처럼 우선
3. `--bsp`와 `--image-basename nexios-image`처럼 모순되는 조합은 오류
4. 환경변수 `IMAGE_BASENAME`이 BSP profile과 충돌해도 오류

실행 요약에는 다음을 추가한다.

```text
boot profile:  bsp-initramfs
image:         nexios-bsp-initramfs
pass marker:   NEXIOS_BSP_INITRAMFS_READY
```

정상 profile의 현재 login prompt와 shell prompt 기본값
(`run_qbox_yocto.sh:927-928`)은 바꾸지 않는다. `--bsp`도 QBox runner에
WIC를 `--rootfs`로 전달하므로 기존 writable disk copy, artifact
resolution, RSE state 처리와 full-system firmware 경로를 그대로 쓴다.

## 11. 테스트 계획

### 11.1 정적 및 unit test

변경 대상:

- `tests/test_yocto_build_sh_dm_verity.py`
- 신규 `tests/test_yocto_build_sh_bsp.py` 또는 위 파일의 BSP case
- `tests/test_run_qbox_yocto_sh.py`
- `tests/test_run_qbox_yocto_qboxconf_images.py`
- 필요 시 신규 metadata contract test

검증 항목:

1. `bash -n yocto_build.sh run_qbox_yocto.sh`
2. 기본 dry-run에 두 target이 정확한 순서로 존재
3. `--bsp --dry-run`에 BSP target만 존재
4. on/off multiconfig에서 모든 target prefix가 정확
5. `--bsp` QVP가 BSP qboxconf와 WIC를 선택
6. `--bsp` FVP가 BSP WIC를 선택
7. 정상 profile은 기존 artifact와 marker를 선택
8. 충돌하는 basename/profile 조합은 exit code 2
9. qboxconf의 `images.rootfs_wic`가 BSP WIC stable link를 가리킴

예상 명령:

```bash
python3 -m pytest -q \
  tests/test_yocto_build_sh_dm_verity.py \
  tests/test_yocto_build_sh_bsp.py \
  tests/test_run_qbox_yocto_sh.py \
  tests/test_run_qbox_yocto_qboxconf_images.py
```

### 11.2 BitBake parse 및 task graph

```bash
source layers/poky/oe-init-build-env build

MACHINE=apollo-qvp bitbake -p
MACHINE=apollo-fvp bitbake -p

MACHINE=apollo-qvp bitbake-getvar -r nexios-bsp-initramfs \
  PACKAGE_INSTALL
MACHINE=apollo-qvp bitbake-getvar -r nexios-bsp-initramfs \
  IMAGE_FSTYPES
MACHINE=apollo-qvp bitbake-getvar -r nexios-bsp-initramfs \
  WKS_FILE

MACHINE=apollo-qvp bitbake -g nexios-bsp-initramfs
```

같은 변수 검사를 `apollo-fvp`에도 수행한다. `PACKAGE_INSTALL` 최종값과
history에서 demos, OpenSSH, dm-verity package가 유입되지 않았음을
확인한다.

### 11.3 targeted build

좁은 단계부터 실행한다.

```bash
source layers/poky/oe-init-build-env build

MACHINE=apollo-qvp bitbake nexios-bsp-initramfs -c rootfs
MACHINE=apollo-qvp bitbake nexios-bsp-initramfs

MACHINE=apollo-fvp bitbake nexios-bsp-initramfs -c rootfs
MACHINE=apollo-fvp bitbake nexios-bsp-initramfs
```

그 다음 wrapper 계약을 검증한다.

```bash
./yocto_build.sh --keep-conf --machine apollo-qvp --bsp
./yocto_build.sh --keep-conf --machine apollo-fvp --bsp
./yocto_build.sh --keep-conf --machine apollo-qvp
```

마지막 기본 명령은 기존 제품 image와 신규 BSP image의 결합 빌드 회귀
검증이다.

### 11.4 artifact 검사

각 machine에 대해 다음을 확인한다.

```bash
test -s build/tmp_baremetal/deploy/images/${MACHINE}/\
nexios-bsp-initramfs-${MACHINE}.cpio.gz

test -s build/tmp_baremetal/deploy/images/${MACHINE}/\
nexios-bsp-initramfs-${MACHINE}.wic

gzip -dc build/tmp_baremetal/deploy/images/${MACHINE}/\
nexios-bsp-initramfs-${MACHINE}.cpio.gz | cpio -it
```

검사 내용:

- `/init`와 BusyBox가 존재
- 필수 module/package가 존재
- 금지 package/file이 없음
- WIC partition이 `boot`, `misc` 두 개뿐
- 단일 ESP의 `a-slot`, `b-slot`에 BSP UKI와 올바른 `metadata`가 존재
- UKI inspect 결과에 BSP CPIO와 `rdinit=/init` 포함
- UKI command line에 `root=`, `dm-verity`가 없음
- QVP `.qboxconf`가 BSP WIC와 현재 QBox provider를 가리킴

최종 manifest는 allowlist 방식으로 검사한다. dependency가 추가될 수
있으므로 exact package count만 고정하지 않고, 필수 package set과 금지
package set을 각각 assertion한다. image 크기와 package count는 결과
artifact에 기록하여 증가 추세를 감시한다.

### 11.5 QBox 부팅

```bash
./run_qbox_yocto.sh \
  --bsp \
  --headless \
  --exit-after-pass \
  --timeout 180 \
  --out-dir build/qbox-apollo-qvp/bsp-initramfs
```

반드시 log/result artifact를 확인한다.

- RSE 및 Safety Island 필수 boot marker
- U-Boot/UKI 선택 marker
- Linux `Run /init as init process`
- 각 `NEXIOS_BSP_TEST`
- `NEXIOS_BSP_INITRAMFS_READY`
- `switch_root`, dm-verity mount, 제품 login prompt가 없을 것

`apollo-fvp` image도 QBox 비교 경로와 실제 FVP 경로에서 같은 CPIO/UKI
계약을 확인한다. QBox의 `--machine apollo-fvp` 경로는 local QBox build를
사용하므로(`run_qbox_yocto.sh:897-903`), QVP의 Yocto-native qboxconf
검증과 구분하여 결과를 기록한다.

### 11.6 부팅 시간

구현 전에 같은 host 부하 조건으로 다음 timestamp를 baseline으로
기록한다.

- QBox process 시작
- Linux `Run /init as init process`
- 제품 `nexios-image` shell/login 준비
- BSP `NEXIOS_BSP_INITRAMFS_READY`

초기 성능 acceptance는 다음으로 한다.

```text
T(BSP_READY) <= 0.5 * T(NEXIOS_PRODUCT_SHELL_READY)
```

각 profile을 3회 실행하여 median을 비교하고, raw log와 측정 JSON을
`build/qbox-apollo-fvp/` 아래에 보존한다. host 성능과 firmware 시간이
달라질 수 있으므로 근거 없는 절대 초 제한만으로 pass/fail하지 않는다.

## 12. 완료 조건

다음 조건을 모두 만족해야 구현 완료로 판정한다.

1. `apollo-fvp`, `apollo-qvp`에서 `nexios-bsp-initramfs`가 parse/build됨
2. 두 machine의 CPIO와 boot-only WIC가 생성됨
3. QVP BSP qboxconf가 독립 생성됨
4. `yocto_build.sh` 기본 호출이 제품 image와 BSP image를 함께 빌드함
5. `yocto_build.sh --bsp` task graph에 제품 rootfs/dm-verity가 없음
6. `run_qbox_yocto.sh --bsp`가 BSP WIC를 선택함
7. 전체 firmware/U-Boot/Linux 경로 후 BusyBox 셸에 도달함
8. 준비 마커와 필수 self-test가 모두 PASS함
9. dm-verity와 `switch_root`가 BSP log에 없음
10. 기본 `nexios-image` 빌드와 부팅 test가 회귀 없이 통과함
11. BSP median 준비 시간이 제품 shell 준비 시간의 50% 이하임
12. 변경 repo별 diff check와 관련 pytest가 통과함

## 13. 위험과 대응

| 위험 | 영향 | 대응 |
| --- | --- | --- |
| image가 자기 CPIO를 UKI에 넣으며 task cycle 발생 | parse/build 불가 | `INITRAMFS_IMAGE=""`, 직접 initrd path, 명시적 `do_image_cpio -> do_uki` edge, `bitbake -g` 확인 |
| 제품 UKI class 회귀 | 정상 부팅 손상 | 기본값 유지, BSP override만 사용, 기존 `nexios-image` build/boot 재검증 |
| QVP qboxconf가 제품 WIC를 가리킴 | 잘못된 rootfs 부팅 | image별 stable link와 dry-run/unit test |
| 전역 demos/OpenSSH가 유입 | 크기·부팅 시간 증가 | `PACKAGE_INSTALL` allowlist, `NO_RECOMMENDATIONS`, manifest denylist |
| `NO_RECOMMENDATIONS`로 RPMsg transport 누락 | HIPC probe 실패 | `kernel-module-virtio-rpmsg-bus` 명시, pkgdata dependency 검사 |
| FVP/QVP kernel built-in/module 차이 | 한 machine에서 modprobe 실패 | 두 machine config/manifest 비교, machine override 최소화 |
| 기존 OEQA의 SSH dependency | minimal image에서 test 미실행 | console self-test와 log parser 제공 |
| PFDI reference app의 Python 의존 | initramfs 비대화 | C 실행 파일과 설정만 `pfdi-bsp-app`으로 분리하고 Python/systemd 제외 |
| a-slot/b-slot에 같은 BSP payload | slot 차이 검증 부족 | slot별 metadata identity를 검사하고, A/B update 검증은 제품 profile 유지 |

## 14. 변경 소유권과 커밋 단위

실제 구현 시 source 소유 repository 경계를 유지한다.

1. `hsoc-stack/yocto/meta-hsoc-auto-solutions`
   - image recipe, init recipe/script, UKI class extension, qboxboot include
2. `hsoc-stack/yocto/meta-hsoc-bsp`
   - FVP/QVP boot-only WKS
3. top-level `arm-auto-solutions`
   - `yocto_build.sh`, `run_qbox_yocto.sh`, tests, 문서

권장 atomic commit 순서:

1. `feat(yocto): add BSP initramfs image`
2. `feat(bsp): add BSP initramfs boot disks`
3. `feat(scripts): add BSP image workflows`
4. `test: cover BSP initramfs workflows`
5. `docs: add BSP initramfs plan` 또는 구현 문서 갱신

모든 commit은 Conventional Commit, 영어 메시지, `git commit -s`를
사용한다.

## 15. 비범위

이번 구현에는 다음을 포함하지 않는다.

- 제품 `nexios-image`의 dm-verity 제거 또는 기본값 변경
- QEMU `-kernel/-initrd` 직접 부팅 경로 추가
- QBox platform의 firmware/U-Boot 우회 로더
- OpenSSH 기반 전체 OEQA suite 이식
- PFDI fault injection, watchdog reset, destructive CPU hotplug 자동 실행
- initramfs 크기 최적화를 위한 BusyBox/kernel config 대규모 변경

이 비범위를 유지해야 BSP 빠른 경로가 제품 부팅 경로와 병존하고,
변경 범위가 image metadata와 두 wrapper에 한정된다.

## 16. 구현 순서

1. 두 machine의 현재 package manifest, kernel config, 제품 부팅 시간을
   baseline artifact로 저장한다.
2. `nexios-bsp-init`와 `/init`/self-test를 구현하고 rootfs task까지
   검증한다.
3. `nexios-bsp-initramfs.bb`와 UKI 직접-initrd path를 구현하고 task graph의
   순환 여부를 확인한다.
4. FVP/QVP boot-only WKS를 추가하고 CPIO, UKI, WIC artifact를 검사한다.
5. QVP qboxboot 설정을 공통화하고 BSP `.qboxconf` 단독 생성을 확인한다.
6. `yocto_build.sh` target array와 `--bsp`를 구현하고 dry-run test를
   통과시킨다.
7. `run_qbox_yocto.sh --bsp` profile과 console marker 판정을 구현한다.
8. QVP headless 부팅, Apollo FVP/QVP 비교 부팅, 제품 profile 회귀 부팅을
   수행한다.
9. 3회 median 부팅 시간을 비교하고 package/크기/로그 artifact를 최종
   보고서에 기록한다.

## 17. 구현 및 검증 결과

2026-07-23에 본 계획의 구현과 검증을 완료하였다.

| 항목 | 결과 |
| --- | --- |
| QVP BSP 전용 빌드 | 4,872 tasks, 전체 성공 |
| FVP BSP 전용 빌드 | 4,438 tasks, 전체 성공 |
| 기본 제품+BSP 빌드 | 7,336 tasks, 전체 성공 |
| 관련 pytest | 61 passed |
| QVP BSP 부팅 | persistent RSE 조건 3/3 pass |
| FVP BSP 부팅 | 180초 유지 실행 pass |
| 기존 제품 부팅 | 성능 표본 3/3 pass, 최종 통합 산출물 회귀 pass |
| BSP self-test | QVP/FVP 매 실행 23 PASS, 0 FAIL |
| QVP BSP 120초 유지 실행 | pass, PFDI timeout 없음 |
| BSP 준비 시간 median | 40.395초 |
| 제품 로그인 시간 median | 87.862초 |
| 시간 감소 | 47.467초, 54.02% |

최종 BSP 산출물은 QVP/FVP 각각 13,792,953/13,792,946 byte CPIO와
37,404,672 byte UKI를 생성한다. boot-only WIC는 `boot` 256 MiB와
`misc` 4 MiB의 두 partition만 포함하며, 단일 ESP의 `a-slot`과
`b-slot`에는 각각 BSP UKI와 slot identity metadata가 존재한다. BSP UKI
command line은 `rdinit=/init`을 포함하고 `root=`는 포함하지 않는다.

검증 근거는 다음 경로에 보존한다.

- 빌드 로그:
  `build/nexios-bsp-initramfs-apollo-qvp-pfdi-final-build.log`,
  `build/nexios-bsp-initramfs-apollo-fvp-pfdi-final-build.log`,
  `build/nexios-default-product-plus-bsp-pfdi-final-build.log`
- BSP 부팅:
  `build/qbox-apollo-qvp/bsp-pfdi-timing-final-{1,2,3}/`,
  `build/qbox-apollo-qvp/bsp-pfdi-soak-final/`,
  `build/qbox-apollo-qvp/bsp-pfdi-combined-final/`,
  `build/fvp-bsp-initramfs-pfdi-final/`
- 제품 부팅:
  `build/qbox-apollo-qvp/product-timing-persistent-{1,2,3}/`,
  `build/qbox-apollo-qvp/product-pfdi-final/`
- BSP 전용 dependency graph:
  `build/nexios-bsp-initramfs-apollo-qvp-task-depends.dot`,
  `build/nexios-bsp-initramfs-apollo-fvp-task-depends.dot`

초기 FVP 유지 실행은 AP의 BSP 검사와 준비 마커까지 통과한 뒤 SI0에서
PFDI monitor timeout을 노출했다. 이를 근거로 `pfdi-bsp-app` 분리와
서비스 기동 검사를 추가했다. 수정 후 QVP 120초 유지 실행과 FVP 180초
유지 실행에서 timeout이 재발하지 않았다. FVP runner의 표준 primary
console 판정은 제품 이미지의 `login:`을 기대하므로 `--require none`을
사용했고, BSP 판정은 23개 PASS, 준비 마커, 셸 prompt를 log에서 별도로
검증했다.

ephemeral RSE 상태를 사용한 별도 한 차례 실행에서는 AP 검사가
통과했지만 SI CL1의 PFDI service marker가 늦어 전체 runner가
대기했다. 이 표본은 성능 비교에서 제외했으며, 위 3회 비교는 BSP와
제품 모두 persistent RSE 상태를 사용해 동일 조건으로 수행했다.
