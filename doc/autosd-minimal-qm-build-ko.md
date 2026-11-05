# AutoSD 전체 빌드 및 실행 Quick Guide

새 진입점은 `./build_autosd.sh`이다. 기본은
`autosd/customization/automotive.aib.yml`이며 `--minimal`로 공식 minimal QM
manifest를 선택한다. 명령은 workspace 최상위에서 실행한다.

Yocto 커널 RPM 기반 Automotive/minimal QM 이미지 빌드와 QBox full 부팅을 검증했다.
실제 실행한 시나리오와 제외 범위는
[검증 리포트](autosd/automotive-source-build-validation-20261105-ko.md)를 확인한다.

## 1. 빌드 구조

| 단계 | 실행 환경 | 결과 |
|---|---|---|
| 플랫폼 준비 | Yocto | RSE/SI/AP 펌웨어, QBox/provider, 플랫폼 manifest |
| 커널·모듈 준비 | Yocto | matching Image, modules, 외부 모듈, DTB |
| 커널 RPM 패키징 | 호스트 native Podman | Yocto 바이너리를 보존한 kernel-apollo RPM |
| PFDI·workload·probe | AArch64 Podman + qemu-user | 작은 사용자 공간 바이너리·RPM |
| 이미지 조립 | 호스트 native AIB/OSBuild | Automotive 또는 minimal QM 완성 디스크 |
| 실행 검증 | QBox full-system | 네 도메인 부팅, guest readiness, 정상 poweroff |

커널은 Yocto toolchain으로 빌드하고 완성 바이너리를 RPM으로 패키징한다.
커널 qemu-user 컴파일은 사용하지 않는다. 작은 사용자 공간 바이너리에만 ARM64
GCC/qemu-user를 사용하며, namespace와 OSBuild 조립은 호스트 native 도구가 담당한다.
제품 Yocto 이미지와 기존 `--bsp` 기능은 별도로 유지한다.

## 2. 최초 준비

```bash
git submodule update --init --recursive -- \
  autosd/automotive-image-builder autosd/sig-docs autosd/pfdi
command -v podman qemu-img mdir mcopy modinfo
python3 -c 'import paramiko, yaml, jsonschema'
cat /proc/sys/fs/binfmt_misc/qemu-aarch64
podman info --format '{{.Host.Security.Rootless}}'
sudo -n podman info --format '{{.Host.Security.Rootless}}'
df -h build
```

호스트에는 Podman, qemu-user/binfmt, qemu-img, mtools, kmod와 Python 의존성이 필요하다.
호스트 패키지 설치와 binfmt 등록에는 관리자 권한이 필요하다. 기존 준비를 재사용하며
스크립트가 호스트 SELinux 정책을 변경하지 않는다.

RPM compiler 컨테이너는 rootless Podman, Native AIB는 rootful Podman을 사용한다.
전체 build script에 sudo를 붙이지 않는다. `sudo -n podman`이 허용되어 있어야 한다.
rootless AIB는 이 호스트에서 SELinux xattr 권한 문제로 검증되지 않았으며 기본 경로가 아니다.

ARM64 도구 환경은 `autosd/build/Containerfile.aarch64-rpm`에 정의된다.
CentOS CRB의 glibc-static을 사용해 scratch workload 컨테이너용 정적 바이너리를 만든다.
커널 모듈은 Yocto가 생성한 서명을 보존한다. RPM 패키징 단계에서 strip하거나
다른 키로 다시 서명하지 않는다.

## 3. 펌웨어·커널·모듈 준비

```bash
./yocto_build.sh --machine apollo-qvp --firmware-only
./yocto_build.sh --machine apollo-qvp virtual/kernel arm-si-rproc-mod rpmsg-net-mod pfdi-misc-mod
```

첫 명령은 펌웨어·플랫폼만 준비한다. 두 번째 명령은 커널·외부 모듈을 준비하며
변경 없는 입력은 Yocto 캐시를 재사용한다. AutoSD rootfs는 AIB가 생성한다. 입력은
`build/tmp_baremetal/deploy/images/apollo-qvp/`에 생성한다.
`apollo-autosd-platform-apollo-qvp.qboxconf`와
`apollo-autosd-platform.json`이 provider 경로와 펌웨어 hash/구성을 전달한다.
공유 BitBake는 직렬 실행한다.

## 4. 기본 Automotive 이미지

```bash
./build_autosd.sh --dry-run
./build_autosd.sh --prepare-inputs-only
./build_autosd.sh
```

기본 명령은 Yocto 커널 RPM 패키징, 사용자 공간 payload 준비, AIB 이미지 생성, QBox readiness 확인과 정상
종료까지 수행한다. Runtime readiness는 전체 데모 시나리오 PASS와 구분한다.

이미지만 만들고 VM 실행은 나중에 하려면:

```bash
./build_autosd.sh --build-only
./run_qbox_autosd.sh --autosd build/autosd/automotive/regular.json
```

기본 이미지에는 Root의 Safety Monitor/Podman/BlueChi, ADAS 실행 영역,
QM 앱·nested container, HIPC/PFDI, RT 도구와 진단 프로그램이 포함된다.
장애 주입, RT benchmark, watchdog owner는 기본 부팅에서 자동 실행하지 않는다.
Root/QM은 vanilla AutoSD crun을 사용한다.
공통 부팅 정책은 `ethsi1`의 자동 DHCP만 막아 명시적인 HIPC/VLAN 연결은 허용한다.
ESP는 `boot-efi.mount` drop-in의 `umask=0077`로 마운트한다.

## 5. minimal QM 선택

다음 두 방법은 같은 manifest를 선택한다. 둘 중 하나를 실행한다.

```bash
./build_autosd.sh --minimal
# 또는
./build_autosd.sh --aib-manifest autosd/sig-docs/demos/minimal_qm/minimal_qm.aib.yml
```

`--minimal`과 `--aib-manifest`는 동시에 지정할 수 없다. minimal QM에는 공통 Apollo
부팅 지원을 넣되 Automotive 앱·RT 도구는 자동 추가하지 않는다. 기본 결과는
`build/autosd/minimal-qm/regular.json`이며 Automotive 결과와 분리한다.

```bash
./run_qbox_autosd.sh --autosd build/autosd/minimal-qm/regular.json
```

## 6. 입력 고정과 캐시 재사용

```bash
./build_autosd.sh --build-only \
  --builder-reference quay.io/centos-sig-automotive/automotive-image-builder@sha256:DIGEST \
  --rpm-build-dir build/autosd/rpm-yocto \
  --work-dir build/autosd/automotive-build-new \
  --output build/autosd/automotive-new
```

`DIGEST`는 사용할 호스트 native AIB의 실제 digest로 바꾼다. 기본 AIB 참조는 검증한 amd64 digest로 고정돼 있다. 다른 digest를 쓰면 기존 cache receipt와 충돌할 수 있으므로
새 `--cache-dir`를 사용한다. 다른 Yocto 배포 경로는 `--deploy-dir`,
matching kernel build artifacts는 `--kernel-artifacts`로 지정한다.

| 위치 | 내용 |
|---|---|
| `autosd/config/automotive.json` | 기본 source manifest와 AIB 입력 설정 |
| `autosd/customization/automotive.aib.yml` | 패키지·서비스 정책 원본 |
| `build/autosd/rpm-yocto/` | Yocto 입력 hash, RPM/repo, 사용자 공간 payload, inputs/result receipt |
| 지정한 `--work-dir` | resolved manifest, AIB fetch/cache/export, 실행 로그 |
| `build/autosd/automotive/` | 기본 완성 raw 이미지, DTB, regular.json |
| `build/qbox-apollo-qvp/autosd-*/` | 실행용 복사본, 네 도메인 로그, readiness/result |

RPM 캐시는 Yocto Image·모듈·설정·도구·산출물 hash가 일치할 때만 재사용한다. 입력이
변하면 새 RPM 작업 디렉토리를 선택한다. 같은 NEVRA의 다른 바이너리를 임의로
덮어쓰거나 result.json을 수동으로 고쳐 검사를 우회하지 않는다.

OSBuild cache와 실행 간 자동 resume은 다른 기능이다. 실패한 생성 디렉토리를
무조건 성공한 입력으로 채택하지 않으며, 오류 원인과 receipt를 먼저 확인한다.
`--aib-cache-dir PATH`로 기존 AIB의 `fetch/cache`를 지정하면 패키지 다운로드와
OSBuild store를 재사용할 수 있다. `--cache-dir`는 입력·기본 출력의 루트이고
`--aib-cache-dir`와 역할이 다르다. 재시도 시 새 `--work-dir`와 존재하지 않는
`--output`을 사용하며 같은 AIB 캐시를 사용하는 빌드는 직렬 실행한다.
입력 기록은 재현성을 돕지만 RPM 저장소 snapshot까지 고정하지 않으면 완전히 같은
바이트의 이미지를 보장하지 않는다.

## 7. 부팅과 Dashboard 검증

완성 이미지 런처는 base 이미지 hash와 DTB/플랫폼 입력을 검증한 뒤 실행 복사본을
만든다. 준비된 이미지의 UKI/ESP를 교체하거나 guest에 모듈·패키지를 설치하지 않는다.
Native AIB는 target rootfs의 ARM64 EFI stub로 UKI를 생성한다. 이미지 게시 전
EFI loader·채워진 UKI·내장 커널의 ARM64 여부를 검사한다.
Reboot는 해당 실행 디스크를 사용한다. 이전 실행 디스크를 자동으로 최신 이미지 대신
선택하지 않는다. QBox full-system VM은 하나씩 실행한다.
펌웨어를 다시 빌드하면 이전 실행 디스크의 platform hash와 달라 재사용이 거부될 수 있다.
VM을 정상 종료하고 Dashboard를 재시작해 원본 이미지에서 새 실행 복사본을 만든다.
이때 이전 실행 디스크의 변경 내용은 새 복사본으로 자동 이관되지 않는다.
Watchdog reset 후 ESP dirty 검사로 private 디스크 재사용이 거부되면 실패 디스크를
보존하고 base 이미지의 새 복사본으로 부팅한다. 자동 파일시스템 수리는 수행하지 않는다.

```bash
python3 scripts/autosd_dashboard/server.py \
  --manifest build/autosd/automotive/regular.json \
  --rootfs build/autosd/automotive/rootfs.img \
  --allow-private-guest --backend qbox-full \
  --listen 127.0.0.1 --listen 192.168.0.13 --allow-unauthenticated-lan
```

LAN IP는 현재 호스트 인터페이스에 존재하는 주소로 지정한다.
브라우저에서 `http://127.0.0.1:8765/` 또는 `http://192.168.0.13:8765/`를 연다.
이미 tmux VM이 실행 중이면 정상 종료한 후 Dashboard Power on을 실행한다.

검증 순서는 부팅/readiness, Automotive 정상·장애·복구, RT, mixed-criticality,
watchdog, Pause/Resume, Reboot, Power off이다. 각 시나리오의 host/guest 로그와
결과를 확인한다. monitor fault injection을 사용할 때만 서버에 `--runtime-injection`을
추가한다. 상세 UI 설명은 [Dashboard 가이드](autosd-dashboard-guide-ko.md)를 참조한다.

## 8. 실패와 증거

- `builder.log`: ARM64 컨테이너 패키지 준비. architecture/CRB/binfmt를 확인한다.
- RPM `build.log`: Yocto 입력의 release/설정/서명 일치, PFDI 및 패키징 오류를 확인한다.
- AIB 로그: manifest schema, repository resolve, native namespace와 대상 scriptlet을 구분한다.
- QBox 로그: RSE, SI CL0, SI CL1, AP 중 가장 먼저 실패한 도메인을 확인한다.
- `domains.json`, `modules.json`: 현재 boot epoch의 실제 readiness 결과를 확인한다.
- `result.json`: Linux powerdown과 secure firmware assertion을 함께 확인한다.

`bootctl partition is invalid`, 커널/모듈 불일치, module signature 실패,
SELinux Enforcing 실패, TF-A assertion을 무시하고 PASS로 처리하지 않는다.
RT 측정 결과는 QBox 기능·시뮬레이션 결과이며 실제 하드웨어 latency 보증이 아니다.

`build/autosd/`는 삭제 가능한 생성물이지만 실행 중인 VM/서버의 디스크를 삭제하면
안 된다. 정리는 기존 `scripts/cleanup_run_images.py`의 dry-run으로 대상과 보호 경로를
먼저 확인한다. 과거 native builder 실험은
[기존 빌더 보고서](autosd-native-builder-20261102-ko.md)와
[기존 부팅 보고서](autosd-native-boot-20261102-ko.md)에 보존되어 있다.
