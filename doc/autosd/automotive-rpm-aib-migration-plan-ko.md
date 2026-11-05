# Apollo AutoSD: Yocto 커널 RPM 및 Automotive AIB 전환 계획

작성일: 2026-11-05. 상태: **현재 결정에 따른 구현·빌드·부팅·대표 시나리오 검증 완료**.
실제 완료 여부와 로그 위치는 [검증 보고서](automotive-source-build-validation-20261105-ko.md)를 따른다.

## 현재 결정: 커널은 Yocto 바이너리 RPM 패키징

2026-11-05 실제 qemu-user 커널 컴파일 시간이 길어 사용자 요청으로 방향을 변경했다.
커널·in-tree/외부 모듈·DTB는 Yocto에서 준비하고 native RPM 도구로 패키징한다.
`Image`의 release/IKCONFIG와 모듈 ABI·서명을 검증하며 서명된 모듈은 수정하지 않는다.
작은 PFDI/workload/latency-probe의 ARM64 빌드와 Native AIB 이미지 조립은 유지한다.
`build_autosd.sh` 기본 Automotive와 옵션 minimal QM, 빌드 시 UKI/ESP 생성,
완성 이미지를 변경하지 않는 런처·Dashboard 계약도 유지한다.

커널 입력 준비 명령:

```bash
./yocto_build.sh virtual/kernel arm-si-rproc-mod rpmsg-net-mod pfdi-misc-mod
./build_autosd.sh --build-only
```

`--firmware-only`는 별도 플랫폼 준비 명령으로 남는다. 이제 전체 AutoSD 빌드는
Yocto 커널 산출물에도 의존한다. `--deploy-dir`/`--kernel-artifacts`로 matching 입력을
지정하고 `--rpm-build-dir`로 패키징 cache를 선택한다. 중단한 kernel qemu-user
컴파일은 정상 빌드나 자동 fallback으로 재개하지 않는다.

아래 1~10절은 최초 전환 설계 기록이다. 그중 qemu-user 커널 컴파일, Yocto 커널
독립성, source RPM 관련 목표는 위 결정으로 대체된다. 현재 실행 명령은
[통합 Quick Guide](../autosd-minimal-qm-build-ko.md)를 따른다.

구현 중 확정한 사항: 외부 모듈은 ABI가 같은 `kernel-apollo` RPM에 함께 넣는다.
아래 `kmod-apollo` 별도 패키지 제안은 적용하지 않는다. 개발용 모듈 서명은 기존
공개 개발 키를 사용하며 제품용 키 관리 기능이나 제품 서명 검증은 포함하지 않는다.

## 1. 확정할 구조와 범위

| 구분 | 결정 |
|---|---|
| 커널·모듈 컴파일 | Ubuntu x86_64의 Podman이 AArch64 컨테이너를 시작하고 qemu-user/binfmt로 AArch64 GCC·binutils·rpmbuild 실행 |
| 컴파일러 | 컨테이너의 `gcc`; x86_64 호스트의 `aarch64-linux-gnu-gcc`를 호출하지 않음 |
| 커널 소스·설정 | 기존 Linux submodule과 `apollo_qvp_defconfig` 재사용. 소스 복제와 별도 defconfig 유지 금지 |
| 기타 AP 바이너리 | 외부 모듈, PFDI 사용자 공간, workload, latency-probe도 같은 방식으로 빌드 |
| 이미지 조립 | 기존 x86_64 Native AIB/OSBuild 유지. ARM64 RPM scriptlet·대상 프로그램만 qemu-user 실행 |
| Yocto | AutoSD용 경로에서는 RSE/SI/AP 펌웨어와 필요한 플랫폼 산출물만 준비. 기존 Yocto 제품/BSP 이미지 기능은 보존 |
| 빌드 진입점 | `build_autosd_minimal_qm.sh`를 `build_autosd.sh`로 변경 |
| 이미지 정의 | Git에 보관하는 `autosd/customization/automotive.aib.yml`이 Root/QM 구성의 원본 |
| manifest 선택 | 기본 Automotive; `--aib-manifest PATH`로 명시적 선택. `--minimal`은 공식 `minimal_qm.aib.yml` 선택의 단축 옵션 |
| AP OS 디스크 | AutoSD AIB의 GPT/UKIBoot 레이아웃 유지 |
| 부팅 | 완성 이미지 + 일치하는 플랫폼 manifest를 런처가 검증·실행. 커널 교체와 패키지 설치 없음 |
| 우선 완료 대상 | regular Automotive 이미지와 QBox full-system 데모. bootc/OTA의 신규 qualification은 별도 범위 |
| 기존 선택 기능 | custom crun, iceoryx2 데모를 기본 빌드에 추가하지 않음. Root/QM crun과 UKIBoot는 AutoSD 패키지 우선 |

여기서 AArch64 컨테이너의 compiler는 ARM64 실행 파일이며 qemu-user로 동작한다.
ARM64 머신 전체를 가상화하는 QBox 빌더와 구분한다. 컨테이너 namespace 생성은
호스트 native Podman/crun이 담당한다. ARM64 컨테이너 안에서 `mock`, Podman,
OSBuild/bwrap을 중첩 실행하는 구조로 바꾸지 않는다.

이 결정은 기존 ARM64 bwrap의 namespace clone `EINVAL` 문제를 피하기 위한 것이다.
Native AIB의 rootless SELinux xattr 제한은 별개로 남는다.
[기존 Native AIB 검증 보고서](../autosd-native-builder-20261102-ko.md)를 참고한다.
AutoSD 공식 커널 가이드는 실제 AArch64 호스트를 전제로 한다. qemu-user 빌드를
공식 지원으로 간주하지 않고 Apollo에서 별도로 검증한다.
[공식 커스텀 커널 가이드](https://sigs.centos.org/automotive/latest/building/building_an_os_image_that_uses_a_custom_kernel/)

## 2. 현재 구현과 이전할 의존성

2026-11-05 소스 확인 기준 Linux HEAD는 `3aaef1b10255`, AIB HEAD는 `997b7b06a7ac`이다.
작업 트리의 vanilla crun 전환 변경을 보존하고 이를 기준으로 계획했다.
`build/conf`에는 `apollo-qvp`, `auto-ad-nexios`, cfg2, AP 4 CPU,
PFDI/monitor, modsign, EFI capsule 설정이 있다. 이는 설정 파일 확인이며
이번 문서 작성에서 BitBake의 최종 datastore나 task graph를 평가하지 않았다.

| 현재 경로 | 현재 동작 | 이전할 내용 |
|---|---|---|
| [kernel_rpm_build.sh](../../scripts/autosd_demo/kernel_rpm_build.sh), [kernel_rpm_payload.py](../../scripts/autosd_demo/kernel_rpm_payload.py) | Yocto `Image`, modules tar, build artifacts를 RPM으로 재포장. 버전 하드코딩, Docker 사용 | 소스 컴파일부터 수행하는 AArch64 Podman RPM 빌드로 대체 |
| [Apollo kernel recipe](../../hsoc-stack/yocto/meta-hsoc-bsp/recipes-kernel/linux/linux-yocto-apollo-common.inc) | 로컬 Linux 소스와 defconfig로 빌드 | 동일 입력을 독립 RPM 빌더에서 사용; Yocto workdir 참조 제거 |
| [prepare.py](../../autosd/customization/prepare.py) | 호스트 cross GCC로 바이너리 생성 후 Automotive YAML과 runtime-files 생성 | 바이너리는 ARM64 빌더로 이전; checked-in YAML을 읽어 입력 경로·버전만 결합 |
| [build_minimal_qm.py](../../scripts/autosd_demo/build_minimal_qm.py) | minimal_qm AIB 빌드 후 QBox에서 DNF/모듈/Automotive/RT 설치 | 이미지 빌드와 런타임 검증을 분리; guest 설치 단계 제거 |
| [native_build.py](../../scripts/autosd_demo/native_build.py), [builder_podman.py](../../scripts/autosd_demo/builder_podman.py) | 동일 manifest를 ARM64/x86_64로 각각 compose, `qemu` target 고정 | Apollo 대상 compose와 중립 native build compose 분리; RPM·OCI·payload 마운트 추가 |
| [autosd_fullsystem_modules.py](../../scripts/run/autosd_fullsystem_modules.py), [autosd_fullsystem_pfdi.py](../../scripts/run/autosd_fullsystem_pfdi.py) | Yocto workdir에서 HIPC/PFDI 바이너리를 찾아 guest에 설치 | 이미지에 RPM으로 설치; 부팅 후에는 실행 상태·드라이버·통신만 검증 |
| [run_qbox_autosd.py](../../scripts/run/run_qbox_autosd.py) | 실행 디스크의 UKI/ESP 교체, offline modules 설치, 부팅마다 SSH provisioning | 완성 이미지 검증·실행과 부팅 epoch별 readiness 확인 |
| [run_qbox_yocto.sh](../../run_qbox_yocto.sh), [qboxboot include](../../hsoc-stack/yocto/meta-hsoc-auto-solutions/recipes-core/images/include/nexios-apollo-qboxboot.inc) | BSP 이미지의 `.qboxconf`, DTB, UKI/provider 배포에 결합 | AutoSD의 플랫폼 입력을 제품 OS 이미지 없이 제공 |
| [Dashboard server](../../scripts/autosd_dashboard/server.py), [watchdog scenarios](../../scripts/autosd_dashboard/watchdog_scenarios.py) | reboot/WD04 완료가 `provision.status`와 boot epoch에 의존 | 설치 대신 readiness 증거를 소비하도록 함께 변경 |

## 3. 소스·설정·생성물 배치

새 외부 저장소가 필요할 때는 `autosd/` 아래에 고정 revision으로 추가한다.
이미 보유한 소스를 다시 clone하지 않는다. `arm-zena-css/`와 외부 Yocto layer는
읽기 전용 참조로 유지한다. 루트 tooling과 nested repository 변경을 구분한다.

| 위치 | 역할 | 처리 |
|---|---|---|
| `autosd/build/Containerfile.aarch64-rpm` | AArch64 RPM 도구 환경 | 신규; 기반 이미지 digest와 설치 패키지 기록 |
| `autosd/rpm/` | 커널, 외부 모듈, PFDI spec | 신규; source build·install·RPM metadata의 원본 |
| `autosd/config/automotive.json` | builder digest, 소스 입력, 병렬도, timeout, 서명 키 경로 참조 | 신규; 기존 기본 설정에서 전환 |
| `autosd/customization/automotive.aib.yml` | Root/QM 패키지·서비스·파일·컨테이너 정책 | 신규; 생성 디렉토리에만 존재하던 정책을 소스 관리 |
| `autosd/sig-docs/demos/minimal_qm/minimal_qm.aib.yml` | 옵션으로 선택하는 minimal QM 원본 | 기존 파일 재사용; Automotive 앱·RT 구성 자동 추가 없음 |
| `autosd/customization/{root,qm,rt,apps}/` | 기존 앱·서비스·진단 소스 | 재사용 |
| `scripts/autosd_demo/` | 빌드 orchestration, RPM 저장소 생성, AIB 호출, 결과 검사 | 기존 helper 재사용·수정 |
| `build/autosd/rpm/<input-id>/` | 커널 O= 디렉토리, module/PFDI build, RPM, 로그 | 삭제 가능한 중간 결과 |
| `build/autosd/cache/` | 입력 다운로드, 패키지 캐시 | 삭제 가능; checksum 검증 후 재사용 |
| `build/autosd/automotive/<build-id>/` | local repo, payload/OCI, resolved manifest, OSBuild store, 최종 이미지·receipt | 삭제 가능한 실행별 생성물 |
| `build/autosd/automotive/regular.json` | 완성 이미지 선택용 manifest | 검증된 새 산출물로 원자적 갱신 |
| `build/autosd/minimal-qm/regular.json` | minimal QM 선택 시 결과 manifest | Automotive 기본 산출물과 분리 |
| `build/qbox-apollo-qvp/autosd-<run-id>/` | full-system 실행 복사본·UART·검증 결과 | 기존 증거 위치 유지 |

서명 개인 키를 Git이나 삭제 가능한 build 디렉토리의 유일한 사본으로 두지 않는다.
설정에는 사용자가 관리하는 키 경로만 둔다. 개발용 새 키 생성은 명시적 준비 단계로
분리하고, 기존 키를 자동 교체하지 않는다. 공개 인증서 fingerprint를 provenance에 기록한다.

## 4. AArch64 RPM 빌드 계약

### 4.1 실행 환경과 권한

호스트에서 AArch64 binfmt 등록과 interpreter 경로·버전을 확인한다. 컨테이너
architecture, `gcc -dumpmachine`, GCC 실행 파일과 시험 산출물의 ELF machine을
확인하고 짧은 ARM64 프로그램을 실제 실행한다. `uname -m`만으로 판정하지 않는다.
`ARCH=arm64`, 컨테이너의 `CC=gcc`, `HOSTCC=gcc`를 사용하고 `CROSS_COMPILE`은 비운다.
Kbuild의 host tool도 이 컨테이너 안에서는 AArch64 실행 파일이어야 한다.

RPM 컴파일은 일반 사용자/rootless Podman을 우선하고 loop device나 privileged
권한을 요구하지 않도록 구성한다. rootless가 불가능하면 원인과 실패 단계에서
중단하며 cross compiler나 QBox 빌더로 자동 우회하지 않는다. Native AIB 조립은
기존 rootful 경로를 사용하므로 **전체 빌드의 sudo 제거를 완료 조건으로 삼지 않는다**.
호스트 패키지 설치·binfmt 등록은 기존 최초 준비 절차를 재사용한다.

컨테이너에는 GCC/binutils, make, RPM build 도구, flex/bison, bc, OpenSSL,
elfutils, pahole/dwarves, Python, CMake 및 각 spec의 BuildRequires를 설치한다.
static workload/probe를 유지할 경우 AArch64 glibc-static 가용성을 먼저 확인한다.
컨테이너 준비 후 compilation에는 다운로드가 필요하지 않도록 입력을 준비한다.
병렬도는 명시적으로 제한하고 커널의 BTF 생성·링크 구간 RSS와 wall time을 측정한다.

### 4.2 패키지와 ABI

| 패키지 | 내용 | 주요 계약 |
|---|---|---|
| `kernel-apollo` | Image, in-tree modules, config, System.map, 선택 DTB | `/usr/lib/modules/<kernel-release>/vmlinuz` 등 AIB 기대 경로 제공 |
| `kmod-apollo` | `arm_si_rproc`, `rpmsg_net`, `pfdi_misc` | 정확한 kernel release/ABI에 의존; 같은 빌드의 Module.symvers 사용 |
| `apollo-pfdi` | libpfdi, CLI/sample app, Python 도구, pack, 서비스 | AutoSD 10 AArch64 사용자 공간 ABI; AP CPU 수와 pack 일치 |

처음부터 배포판의 kernel-core/modules-extra 패키지 분할을 복제하지 않는다.
외부 모듈은 완료된 커널 build directory로 빌드하므로 별도 devel RPM은 초기 필수가
아니다. 독립적인 외부 모듈 배포가 필요해질 때만 `kernel-apollo-devel`을 추가한다.
workload/probe는 동일 ARM64 builder의 산출물을 AIB payload와 OCI에 사용한다.

소스 선택은 기존 recipe의 실제 입력·override를 확인한 후 고정한다.
HIPC/PFDI 모듈의 기본 소스 경로는 `sw-ref-stack/components/primary_compute/linux_drivers/`
아래이며, 사용자 공간 PFDI는
[기존 recipe](../../sw-ref-stack/yocto/meta-arm-auto-solutions/recipes-demos/pfdi/platform-fault-detection.bb)의
revision·패치·생성 설정을 먼저 대조한다. Yocto download/workdir의 우연한 잔존 파일을
새 빌드의 필수 입력으로 사용하지 않는다.

`make kernelrelease`를 단일 버전 기준으로 삼고 RPM EVR과 kernel release를 각각
기록한다. 기존 `6.18.5-rt3-yocto-preempt-rt` 문자열을 helper에 하드코딩하지 않는다.
첫 전환에서는 release 이름 변경과 기능 이전을 분리하고 현재 defconfig 값을 유지한다.
AIB의 기존 `kernel.uname_r` 지원으로 실제 modules directory를 지정한다.
RPM 갱신 시 동일 NEVRA에 다른 payload를 덮어쓰지 않는다.

커널은 [기존 defconfig](../../hsoc-stack/components/primary_compute/linux/arch/arm64/configs/apollo_qvp_defconfig)의
PREEMPT_RT, BPF LSM/BTF, SELinux, cgroup, virtio-MMIO, bridge netfilter,
SCMI/remoteproc/RPMsg, PFDI, SBSA watchdog, EFI, timerlat/osnoise 기능을 유지한다.
필요한 수정은 해당 defconfig에 반영하며 별도 Apollo `.cfg/.scc`를 만들지 않는다.

`CONFIG_MODULE_SIG_FORCE=y`를 유지한다. 커널이 신뢰하는 키로 in-tree 및 외부
모듈을 서명하며, 필요한 strip 작업은 서명 전에 끝낸다. RPM 후처리가 서명된
`.ko`를 변경하지 않는지 설치 payload와 `modinfo`로 확인한다. RPM 저장소 서명과
커널 모듈 서명은 별개로 관리한다. 빌드 도구 RPM의 GPG 검증을 끄지 않고, 로컬
패키지의 서명 여부·신뢰 설정은 명시적으로 기록한다.

표준 Kbuild install을 사용하되 upstream `binrpm-pkg` 결과를 무검증으로 채택하지
않는다. 이름, usr-merge 경로, dependency, 자동 strip, kernel-install scriptlet을
AIB와 맞춘다. 이미지 생성 중 실행되는 scriptlet이 호스트 `/boot`를 수정하거나
호스트 kernel release로 initramfs를 만들지 않아야 한다. initramfs·UKI 생성 책임은 AIB에 둔다.

## 5. Automotive AIB manifest 구성

`automotive.aib.yml`이 정책 원본이고, `prepare.py`는 입력 경로·RPM version·OCI digest를
결합하는 역할만 맡는다. 기존 Python 안의 패키지 목록과 source YAML에 같은 정책을
중복 유지하지 않는다. resolved manifest는 build 아래에 생성하고 원본을 덮어쓰지 않는다.

| 영역 | 기본 이미지에 포함할 내용 |
|---|---|
| Root | Apollo kernel/kmod/PFDI, Python, Podman, vanilla crun, BlueChi controller/agent/ctl/SELinux 정책, Safety Monitor |
| ADAS 실행 영역 | `apollo-asil-b.slice`, ADAS Quadlet, workload OCI; 기존 CPU 1·메모리 제한 유지 |
| QM | Podman, vanilla crun, BlueChi agent, QM app·nested container, workload OCI; CPU 2–3·기존 자원 제한 유지 |
| RT | Root의 realtime-tests/rtla/trace-cmd/stress-ng/util-linux/procps-ng, QM stress-ng, 양쪽 latency-probe, trace/experiment 도구 |
| Full-system | modules-load, HIPC/PFDI 서비스·health check, `apollo.fullsystem=1` 조건, AP CPU 수에 맞는 PFDI pack |
| Watchdog·mixed criticality | 기존 진단 프로그램·시나리오 입력을 내장. 장애 주입이나 watchdog owner는 기본 부팅에서 자동 실행하지 않음 |
| 콘솔·진단 | PL011 earlycon/console, systemd 상태 출력, journal/서비스 로그, RT 정상 부팅 cmdline |
| 접근 설정 | 기존 개발용 SSH/로그인 정책을 소스 설정으로 명시. 빌드 성공을 위해 guest UART에서 설정을 추가하지 않음 |

Root/ADAS/QM은 논리 실행 영역이며 GPT partition 세 개를 뜻하지 않는다.
`ASIL-B`는 데모 영역 이름이며 safety certification을 의미하지 않는다.
ADAS와 QM 서비스는 첫 부팅부터 준비되되 benchmark·fault injection은 명시적 실행으로 남긴다.

workload와 latency-probe는 ARM64 GCC로 빌드한다. `FROM scratch` workload OCI는
호스트 native Podman으로 조립하고 ARM64 architecture와 digest를 기록한다.
Root와 QM에 같은 OCI digest를 넣으며 AIB 컨테이너의 숨은 containers-storage 상태에
의존하지 않는다. 고정 경로의 OCI archive를 전달하고, 필요하면 Native AIB의 해당
실행 전용 storage에 명시적으로 import한다. guest의 `Pull=never`로 오프라인 첫 부팅을 검증한다.

vanilla crun에서 관찰됐던 SELinux cgroup2 mount 경고는 runtime 검증 항목으로 남긴다.
빌드 성공을 위해 custom crun을 자동 삽입하거나 SELinux를 permissive로 바꾸지 않는다.
`br_netfilter` 모듈과 기존 modules-load 설정을 이미지에 포함한다.

### 5.1 Native AIB와 ARM64 대상 분리

대상 compose는 `target=apollo-qvp`, `arch=aarch64`, Automotive manifest와 로컬
RPM 저장소를 사용한다. native build-root compose는 `arch=x86_64`의 도구 전용
중립 manifest를 사용하여 ARM64 `kernel-apollo`를 x86_64 RPM으로 resolve하지 않는다.

기존 native/target OSBuild 결합 helper를 재사용하고 `ignorearch`는 대상 RPM stage에만
적용한다. local RPM/source transport와 checksum 항목도 중복·충돌 검사하며 결합한다.
실제로 실행하는 AIB가 Apollo target과 `kernel.uname_r`를 포함하는 workspace revision인지
확인한다. 공식 builder 컨테이너에 없는 로컬 AIB 변경을 당연히 사용한다고 가정하지 않는다.

첫 결과는 regular disk이다. AIB가 Apollo kernel + AutoSD dracut/initramfs + cmdline으로
UKI를 생성하고 ESP/UKI slot/boot control을 구성한다. 정상 부팅 후 RPM 설치를 요구하는
미완성 rootfs는 산출물로 발행하지 않는다. 나중에 bootc를 활성화할 때도 같은 RPM을
OS deployment 생성 전에 넣고, composefs/OSTree root를 사후 수정하지 않는다.

### 5.2 파티션·UKIBoot·DTB

AutoSD 기본 `efi` 100 MiB, `ukiboot_a/b` 각 128 MiB, `ukibootctl` 1 MiB,
`root` 구성을 기준으로 한다. 크기 변경이 필요하면 source 설정에 반영한다.
Apollo 제품용 `misc`, `rootro_a/b`, `rootrw`를 혼합하지 않는다.
UKI A/B가 regular rootfs 전체의 A/B update를 제공한다고 해석하지 않는다.

ESP의 AutoSD UKIBoot loader·addon과 guest ukibootctl을 일치하는 패키지에서 가져온다.
AIB가 정의하는 boot-control 초기 상태를 검증하고 초기 슬롯 채움 정책도 AIB에 맡긴다.
양쪽 슬롯에 같은 UKI를 런처가 강제로 기록하지 않는다. GPT type GUID, 제어 데이터
형식, slot 용량·선택 상태를 검사하며 `bootctl partition is invalid`를 실패로 판정한다.
vendor UKIBoot가 Apollo U-Boot에서 실패하면 실제 원인을 먼저 분리하고, 수정이
필요한 경우에도 명시적으로 버전 관리한 패키지를 빌드 단계에서 선택한다.

AP OS DTB는 커널 RPM 빌드에서 나온 matching DTB를 artifact에 내보내고 현재
full-system의 `--ap-dtb` 전달 경로로 제공한다. UKI에 별도 DTB를 중복 주입하지 않는다.
펌웨어 초기 FDT와 Linux용 DTB를 구분하고 실제 guest의 compatible/memory/CPU/IRQ
구성이 canonical QBox platform과 맞는지 검증한다.

## 6. Yocto 펌웨어 전용 경로와 실행 계약

[firmware-apollo-qvp](../../hsoc-stack/yocto/meta-hsoc-bsp/recipes-bsp/images/firmware-apollo-qvp.bb)를
기반으로 `yocto_build.sh --firmware-only` 경로를 추가한다. 구체적 target 집합은
BitBake graph로 확정하며 필요한 RSE ROM/flash/OTP, SCP, SI CL1, AP flash/FIP,
TF-A/OP-TEE/U-Boot, EFI capsule 디스크를 포함한다. QBox native provider와
vMCU/QEMU/SIL Kit는 host/runtime 산출물로 구분하여 필요한 target만 함께 준비한다.

현재 image task에 묶인 `.qboxconf` 및 provider 배포를 플랫폼 경로에서도 생성한다.
이를 위해 firmware 또는 공통 deploy metadata를 확장하고 가짜 rootfs/UKI를 만들지 않는다.
이 경로의 task graph에 `virtual/kernel`, `nexios-image`, `nexios-bsp-initramfs`,
Linux 외부 모듈이나 AP PFDI 사용자 공간 recipe가 끌려오지 않는 것을 확인한다.
Zephyr와 펌웨어용 toolchain은 이 제외 대상에 해당하지 않는다.

완성 이미지 manifest는 기존 `regular.json` 처리기를 확장한 명시적 새 schema로 한다.
별도 경쟁 포맷을 만들지 않고 기존 parser/launcher/dashboard 소비자를 같이 변경한다.
최소 정보는 mode, target, image path/format/SHA256, build ID, kernel release/RPM
NEVRA, DTB path/hash, source/AIB/builder revision, 요구 AP CPU 수와 플랫폼 입력 참조이다.
펌웨어 manifest에는 각 이미지 hash, cfg2/AP CPU 수, PFDI 기능, QBox provider/Lua
식별자를 기록하고 실행 시 두 manifest의 호환성을 검증한다.

빌드가 UKI를 포함하므로 런처의 외부 `initrd`, Yocto UKI, loader/addon 요구를 없앤다.
raw/qcow2 format은 manifest대로 확인하고 필요 시 실행 복사본을 raw로 변환한다.
실행 복사본 생성과 정상 guest 쓰기는 허용하되 source 이미지 hash는 유지한다.
Reboot는 같은 실행 디스크를 사용하고, 새로운 base image 선택과 세션 재개를 구분한다.
기존 `default_rootfs()`의 최근 PASS 디스크 자동 선택은 새 기본 경로에서 제거한다.
세션 재개가 필요하면 base build ID·firmware binding이 일치하는 명시적 상태만 사용한다.

`prepare_uki`, `prepare_disk`, offline module install과 SSH `provision()` 호출을
정상 boot 경로에서 제거한다. 기존 nightly import/실험 helper는 호출자를 조사하여
build/import 도구로 남길 수 있으나 실행 중 자동 변환 fallback은 제공하지 않는다.
구형 manifest는 버전별로 식별하고, 새 launcher에서 부족한 입력을 명확히 안내한다.
기존 디스크를 제자리에서 변환하거나 삭제하지 않는다.

## 7. Dashboard와 readiness 연동

설치 완료를 기다리던 `provision` 상태를 **현재 boot epoch의 readiness 검사**로
이전한다. HIPC/PFDI 서비스 시작은 이미지에 설치된 systemd 설정이 담당하고,
검사기는 패키지 설치·서비스 파일 업로드 없이 다음을 확인한다.

- guest boot ID, kernel release, 필수 RPM, SELinux Enforcing.
- matching 모듈 load, `ethsi1`/RPMsg endpoint, PFDI per-CPU 진단 결과.
- Root/QM BlueChi online, Safety Monitor, ADAS/QM 앱·컨테이너 상태.
- RT 도구와 tracer 준비 상태; benchmark 결과는 별도 시나리오 실행에서 판정.

`domains.json`, `modules.json`의 소비자를 모두 추적한다. 새 readiness 필드로 바꾸면
server reboot 판정, watchdog WD04, monitor 시나리오, build pipeline과 fixture를
함께 수정한다. 과도기 호환 필드가 필요해도 실제 검사 결과를 전달하고 빈 PASS를
만들지 않는다. 오래된 epoch의 결과로 새 boot를 완료 처리하지 않는다.

기본 이미지 선택을 새 Automotive manifest로 변경한다. minimal QM 결과는 Automotive
기본 이미지 선택을 덮어쓰지 않는다. 이미지 manifest에 선택한 구성과 지원 기능을
기록하고, minimal QM에는 없는 Automotive/RT 시나리오를 PASS로 표시하지 않는다.
readiness 검사도 이미지 구성에 맞춰 공통 부팅/QM 검사와 Automotive 검사를 구분한다.
Power off/Reboot 시 상태 초기화,
부팅 단계 1·2 자동 진행, Host/Guest 로그·서비스별 로그, RT histogram/time series,
각 CPU/subsystem monitoring과 QBox topology 기능은 회귀 검사한다.
서버가 provisioning worker나 ready-file을 영원히 기다리지 않는 테스트를 포함한다.

## 8. 단계별 구현과 완료 기준

| 단계 | 변경·산출물 | 종료 조건 | 선행 |
|---|---|---|---|
| P0 입력 확정 | 소스/revision, active kernel config, 펌웨어 task graph, 컨테이너 digest, ABI·키 입력 기록 | 빌드 범위와 필수 입력 누락 없음 | 없음 |
| P1 ARM64 빌더 | Containerfile, binfmt/compiler preflight, source RPM spec, 작업·cache 디렉토리 | ARM64 GCC·Kbuild host tool·작은 RPM 빌드/실행 PASS | P0 |
| P2 커널·모듈 | 독립 kernel/kmod/PFDI RPM, workload/probe/OCI, repository | Image/모듈 ABI·서명·의존성·ARM64 실행 검사 PASS | P1 |
| P3 플랫폼 경로 | firmware-only target 집합, platform manifest/provider deploy | kernel/OS image task 없는 graph, 필요한 펌웨어·DTB 전달 계약 확보 | P0 |
| P4 Automotive AIB | source YAML, 새 진입점과 manifest 선택, payload 준비, native/target 분리, final image manifest | 기본 Automotive와 옵션 minimal QM의 이미지 생성·오프라인 검사 PASS | P2 |
| P5 런처·Dashboard | 이미지 무수정 부팅, readiness, manifest·epoch 연동 | 새 이미지 부팅과 lifecycle/UI 회귀 PASS | P3, P4 |
| P6 전체 검증·정리 | 전 시나리오 실행, 실패 수정, cold rebuild, Quick Guide 갱신 | 아래 acceptance 증거와 남은 제한 보고 | P5 |

구현은 단계별로 검증 가능한 변경으로 나누고, 기존 정상 이미지가 있는 상태에서
새 경로를 먼저 검증한다. 기본값 전환은 P6의 필수 항목 완료 후 수행한다.
공유 BitBake는 직렬 실행하고 빌드 도중 해당 입력을 수정하지 않는다.

### 8.1 수정 파일과 테스트

| 변경 묶음 | 주요 기존 파일 | 검증 |
|---|---|---|
| 입력·orchestration | root wrapper를 `build_autosd.sh`로 변경, `bootstrap.py`, `build_minimal_qm.py`, `autosd/config`, 호출자 | 기존 bootstrap/pipeline tests; 기본 Automotive, 명시적 minimal QM, 단축 옵션·충돌·산출물 분리 검사 |
| RPM·payload | `kernel_rpm_build.sh`, `kernel_rpm_payload.py`, `prepare.py` | ARM64 source build, RPM query/설치, dependency·signature·잘못된 arch/release 거부 |
| AIB | `native_build.py`, `builder_podman.py`, `aib_compose_kernel.sh`, AIB target/schema 관련 코드 | `test_autosd_native_build.py`, `test_autosd_builder_podman.py`, `test_autosd_customization.py`; 실제 compose/build |
| 펌웨어 | `yocto_build.sh`, owned BSP/product metadata, 공통 provider deploy | CLI 회귀, `bitbake -g` graph, clean firmware build 산출물 |
| 런처 | `run_qbox_autosd.py`, `autosd_manifest.py`, full-system readiness helper, 공통 launcher | `test_run_qbox_autosd.py`, `test_autosd_manifest.py`, modules/PFDI·boot-policy·disk/UKI tests |
| Dashboard | `server.py`, `watchdog_scenarios.py`, readiness 소비자와 UI fixture | dashboard·watchdog·mixed-criticality·monitor·UI tests, 실제 브라우저/API 실행 |
| 가이드·정리 | 기존 전체 Quick Guide, config/runtime README, cleanup 스크립트의 보호 경로 | 링크/명령/설정 대조, active run 보호와 cold rebuild |

테스트 파일은 루트 `tests/` 아래의 기존 파일을 뜻한다. 신규 로직에는 의미 있는
실패 사례를 추가하되 단순 파일 이동을 위한 형식적 테스트를 늘리지 않는다.
ARM64 emulation build 통과 없이 mock 기반 unit test만으로 P1/P2를 완료 처리하지 않는다.

## 9. Acceptance와 결과 기록

| 영역 | 필요한 증거 | PASS가 아닌 상태 |
|---|---|---|
| 컴파일 | ARM64 compiler/산출물, source config/hash, kernel/modules/PFDI 빌드 로그 | 컨테이너 실행 또는 uname 출력만 확인 |
| 패키지 | NEVRA/Requires/Provides, payload hash, 모듈 vermagic/서명, depmod 결과 | RPM 파일 존재만 확인 |
| 이미지 | RPM 설치 목록, Root/QM 파일·서비스·OCI, SELinux label, GPT/ESP/UKI/bootctl, qemu-img 검사 | YAML/schema 통과만 확인 |
| 독립성 | Yocto kernel/workdir와 오래된 실행 디스크를 입력으로 제공하지 않은 새 build | 기존 Yocto 바이너리를 암묵적으로 읽음 |
| 첫 부팅 | 두 이미지의 네 도메인 UART, UKIBoot 정상 상태, matching kernel, SSH, Root/QM; Automotive는 ADAS·Safety Monitor까지 | QBox PID 또는 login 문자열만 확인 |
| 무설치 실행 | 최종 image hash 유지, base에 없는 바이너리 upload/DNF/OCI pull 없음 | 첫 부팅 설치 후 동작 |
| 통신·진단 | HIPC 실제 ping/traffic, PFDI per-CPU 결과와 SI 연계 | 모듈 load/장치 열거/서비스 active만 확인 |
| RT·mixed criticality | 기존 시나리오별 원시 로그·결과, timerlat histogram/osnoise 시계열, QM 부하 시 monitor/ADAS 상태 | RT 도구 설치 또는 준비 검사만 PASS |
| Watchdog | WS0와 WS1 관측, reset 경로, 새 AP boot ID와 예상 domain epoch, 복구 readiness | watchdog 설정값이나 reset 명령 반환만 확인 |
| 전원 제어 | 정상 shutdown/poweroff, reboot 후 재접속·새 epoch, Pause/Resume | `reboot: Power down` 한 줄만 확인 |
| Dashboard | 개별 case 진행/종료, Host/Guest 로그, 결과 표·그래프, CPU/subsystem telemetry | API HTTP 200만 확인 |
| 재빌드·cache | 비어 있는 새 AutoSD output에서 생성, 동일 입력 cache hit, 변경 입력 cache 무효화 | 이전 build 디렉토리 수동 복원 필요 |

guest 외부 네트워크를 차단한 첫 부팅에서도 서비스/OCI 실행이 가능해야 한다.
검증용 SSH와 QBox monitor 연결은 유지한다. 결함 유도 시험은 실행 복사본에서 수행하고
복구/재부팅 후 시나리오 간 상태를 초기화한다. full-system VM은 동시에 두 개 실행하지 않는다.

기존 native 이미지 검증에는 TF-A poweroff assertion이 기록되어 있다.
이미 해결되었다고 가정하지 않고 새 firmware/image 조합으로 재검증한다.
필수 poweroff가 실패하면 이 전환의 전체 결과도 FAIL이다.
[기존 부팅 결과](../autosd-native-boot-20261102-ko.md)

결과는 `PASS`, `FAIL`, `SKIP`, `UNSUPPORTED`, `NOT_RUN`을 구분한다.
시나리오마다 build ID/firmware ID, boot ID/epoch, argv, exit code, 시작·종료 시각,
host/guest 로그와 결과 JSON을 연결한다. QBox 결과는 기능 검증이며 실제 하드웨어
latency 또는 안전 인증을 의미하지 않는다. RT 기준을 빌드 방식 변경만으로 완화하지 않는다.

## 10. 캐시·재현성·사용 절차

커널 O= directory와 다운로드/RPM/AIB store는 서로 분리해 실패 시 재사용한다.
cache key에 source tree/revision·dirty content hash, defconfig, compiler/container digest,
kernel release, 모듈 소스, 서명 인증서, spec을 포함한다. 입력이 달라졌을 때 옛
Module.symvers나 서명된 모듈을 재사용하지 않는다. sstate 삭제나 전체 clean을
정상 빌드 단계로 넣지 않는다.

SOURCE_DATE_EPOCH와 입력 기록을 고정하되 repository snapshot, 파일시스템 생성,
서명까지 검증하기 전에는 byte-identical image를 보장하지 않는다. 키를 제외한 필수
설정은 Git 소스에서 복원하고 다운로드 입력은 URL/digest로 다시 준비한다.
OSBuild cache hit와 중단 지점부터의 자동 resume을 구분한다. phase receipt와 산출물
hash를 검증한 재실행만 허용하며 실행 간 무조건 resume을 약속하지 않는다.

### 10.1 빌드 진입점과 manifest 선택

`build_autosd_minimal_qm.sh`를 **`build_autosd.sh`로 변경**한다. 기존 이름을 유지한다는
초기 계획은 이 결정으로 대체한다. bootstrap/pipeline을 재사용하고 동일 로직의 두
master script를 유지하지 않는다. 실제 구현 시 활성 호출자, `--help`, 오류 안내,
테스트와 통합 Quick Guide의 명령을 함께 변경한다. 과거 실행 증거의 명령 기록은 보존한다.

| 호출 방식 | 선택하는 source manifest | 구성 |
|---|---|---|
| `./build_autosd.sh` | `autosd/customization/automotive.aib.yml` | 기본 Automotive·RT 구성 |
| `./build_autosd.sh --aib-manifest PATH` | 지정한 AIB YAML | 지정한 정책으로 이미지 생성 |
| `./build_autosd.sh --minimal` | `autosd/sig-docs/demos/minimal_qm/minimal_qm.aib.yml` | minimal QM; Automotive·RT 앱 설치 생략 |

기존 `--aib-manifest`를 재사용하고, `--manifest`는 기존 JSON 입력 옵션과 구분한다.
`--minimal`과 `--aib-manifest` 동시 지정은 모호하므로 입력 단계에서 거부한다.
선택 우선순위는 명시적 CLI 선택, 명시적 `--config`의 AIB manifest, 기본 Automotive
설정 순서이다. 선택한 source 경로·hash·결합 후 manifest와 결과 경로를 `--dry-run`과
provenance에 기록한다.

minimal QM도 동일한 Apollo kernel/kmod와 full-system 부팅·검증 지원을 사용한다.
공통 target/kernel/repository 및 필요한 SSH·HIPC/PFDI 설정은 resolved manifest에
결합하고 공식 minimal YAML을 직접 수정하지 않는다. Automotive의 Safety Monitor,
ADAS/QM 데모 앱·컨테이너와 RT 패키지는 minimal 선택에 자동으로 추가하지 않는다.
명시적 공식 minimal manifest 선택과 `--minimal`의 결과 정책은 같아야 한다.
원본 YAML에 명시된 값과 공통 플랫폼 설정이 충돌하면 조용히 덮어쓰지 말고 오류로 알린다.

기본 출력은 Automotive의 `build/autosd/automotive/`와 minimal QM의
`build/autosd/minimal-qm/`로 분리하며 기존 `--output` 재정의를 유지한다.
native 모드에서 더 이상 필수 아닌 nightly 이미지 다운로드는 기본 입력에서 제거하고
명시적 import 경로에만 남긴다.

아래는 **전환 완료 후 목표 Quick Guide**이며 새 진입점, manifest 선택 정책과
`--firmware-only`는 현재 미구현이다.

```bash
# 1. 플랫폼 펌웨어/provider 준비: 새 CLI 구현 후 사용
./yocto_build.sh --machine apollo-qvp --firmware-only

# 2. 소스 설정·고정 입력과 실제 단계 확인
./build_autosd.sh --dry-run
./build_autosd.sh --prepare-inputs-only

# 3. ARM64 RPM → native AIB → 완성 이미지 → QBox 검증
./build_autosd.sh

# 4. 동일 완성 이미지 재실행: 빌드·설치·UKI 교체 없음
./run_qbox_autosd.sh --autosd build/autosd/automotive/regular.json

# 5. 선택 사항: 공식 minimal QM manifest로 빌드
./build_autosd.sh --aib-manifest autosd/sig-docs/demos/minimal_qm/minimal_qm.aib.yml

# 위 minimal QM 선택의 단축 옵션: 둘 중 하나만 실행
./build_autosd.sh --minimal

# minimal QM 결과 실행
./run_qbox_autosd.sh --autosd build/autosd/minimal-qm/regular.json
```

최종 구현에서는 전체 실행 명령, 기본 경로, 최초 권한 준비, 실패 단계별 재실행,
보존해야 할 키와 삭제 가능한 cache, Dashboard 시작·개별 데모 실행을
[기존 통합 Quick Guide](../autosd-minimal-qm-build-ko.md)에 반영한다.
이 계획을 실행 가이드로 복제하지 않고 완료 결과·검증 리포트를 여기에 연결한다.

## 11. 계획 자체의 검토

| 검토 항목 | 이번 문서의 결론 | 구현 시 남은 확인 |
|---|---|---|
| 사용자가 선택한 컴파일 방식 | 커널·모듈·AP 바이너리에 ARM64 GCC/qemu-user 적용 | 실제 전체 커널 컴파일 시간·메모리·호환성 |
| 빌드 명령·manifest 선택 | `build_autosd.sh`, 기본 Automotive, 명시적 minimal QM 및 단축 옵션 | 선택 우선순위·옵션 충돌·구성별 출력/검증 테스트 |
| 이전 namespace 실패 | image assembler를 native로 유지하고 ARM64 nested namespace 도구를 배제 | rootless compiler container 및 native AIB capability probe |
| Yocto 완전 분리 | AP userspace/PFDI와 외부 모듈도 이전 범위 포함 | 최종 task graph와 recipe override |
| 서비스의 build-time 구성 | Root/QM·ADAS·RT·watchdog 도구를 manifest/payload에 포함 | 부팅 없이 완성 가능한 AIB 경로와 첫 부팅 동작 |
| 커널 ABI·보안 | matching build, 강제 모듈 서명, SELinux label을 보존 | 실제 RPM 설치·module load·AVC 분석 |
| 런처·Dashboard 누락 | provisioning/epoch 소비자와 default disk 선택까지 범위 포함 | migration fixture와 실제 재부팅/UI |
| 삭제 가능한 build | source 설정, key 외부 관리, cache contract 구분 | clean output 재빌드 |
| 증거 범위 | 과거 PASS/FAIL과 이번 NOT_RUN을 구분 | P1–P6 실행 증거 확보 |

문서 작성 단계에서는 소스 경로·참조 링크와 변경 범위를 확인한다.
컴파일·이미지 생성·서버 재시작·VM 실행은 이 문서의 완료 사실에 포함하지 않는다.
