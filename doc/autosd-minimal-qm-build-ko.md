# AutoSD 전체 빌드 및 실행 가이드

이 문서는 Apollo BSP 준비부터 외부 입력 다운로드, AutoSD 이미지 생성,
Automotive 설치, QEMU/QBox 부팅 검증, 캐시 재사용까지의 통합 Quick Guide이다.
모든 명령은 workspace 최상위에서 실행한다.

Dashboard의 실제 데모 검증 결과는
[빌드 이미지 Dashboard 검증 리포트](autosd-dashboard-image-validation-20260929-ko.md)를
참고한다. 해당 리포트에서 발견한 RT 준비 누락을 보완하여 기본 Automotive
빌드에는 이제 RT 패키지·probe·health-check 설치와 QEMU/QBox 준비 검사가 포함된다.
준비 검사 PASS와 실제 RT 시나리오/latency 판정 PASS는 구분한다.
통합 후 실제 빌드·QBox Dashboard RT 측정 결과는
[RT 빌드 통합 검증 리포트](autosd-rt-build-validation-20260929-ko.md)를 참고한다.

## 원칙

`build/autosd/`는 전부 삭제 가능한 생성물이다. 필수 설정이나 수동으로 보관해야만
재빌드할 수 있는 바이너리를 두지 않는다. VM/웹 서버가 사용하는 동안 삭제하면
안 되며, 삭제하면 실행 이력·다운로드 캐시·검증 결과는 사라진다.

설정의 원본은 다음과 같다.

| 원본 | 역할 |
|---|---|
| `autosd/config/minimal-qm.json` | nightly/AIB 선택, AIB manifest 경로, Automotive 기본 활성화 |
| `autosd/sig-docs/demos/minimal_qm/minimal_qm.aib.yml` | 기본 AutoSD/QM 이미지 구성 |
| `autosd/customization/` | Safety Monitor, ADAS, QM app/container, BlueChi 설정 |
| `autosd/customization/runtime/` | crun 소스 빌드 절차·패치·CentOS 빌더 선택 |
| `scripts/autosd_demo/` | 다운로드, 빌더 부팅, 이미지 생성·검증 절차 |

`inputs.json`, `regular.json`, `provenance.json` 등 build 아래 JSON은 이 설정으로
생성한 결과/기록이다. 이를 수정하여 설정 원본으로 사용하지 않는다.

## 1. 최초 환경 준비

기존 Apollo QVP BSP/provider 빌드는 사용 가능해야 한다. `build/autosd` 초기화와
Yocto의 `build/tmp_baremetal` 초기화는 별개다. BSP가 없다면 순서대로 실행한다.

```bash
git submodule update --init --recursive -- autosd/sig-docs autosd/automotive-image-builder autosd/crun
./yocto_build.sh --machine apollo-qvp --bsp
./yocto_build.sh --keep-conf qemu-apollo-native
```

공유 BitBake는 직렬 실행한다. 기존 matching BSP가 있으면 다시 빌드할 필요 없다.
현재 지원하는 준비 호스트는 Ubuntu/Debian x86_64이며 다음 시스템 도구가 필요하다.

- Python3: paramiko, PyYAML, jsonschema
- qemu-img, mtools, dosfstools, kmod
- libguestfs appliance, supermin, qemu-system-x86, 설치된 호스트 커널 모듈
- Automotive crun 빌드: Docker 접근 권한, AArch64 binfmt, cross GCC,
  autoconf/automake/libtool, pkg-config, make, patch, git

스크립트는 sudo를 실행하거나 호스트 패키지·binfmt 설정을 변경하지 않는다.
부족한 선행 도구는 오류와 함께 안내한다. guestfish 실행 파일과 읽기 가능한
appliance 커널은 필요 시 APT에서 다운로드·추출한다.

시작 전 디스크 여유와 도구를 확인한다. 스크립트의 최소 여유 공간 검사는
32 GiB이며, 여러 실행 디스크를 보관하면 더 많은 공간이 필요하다. 빌더 scratch는
24 GiB 가상 디스크이고 실제 사용량과 가상 크기는 다를 수 있다.

```bash
df -h build
command -v qemu-img mcopy mdir fsck.fat modinfo aarch64-linux-gnu-gcc
python3 -c 'import paramiko, yaml, jsonschema'
docker info >/dev/null
```

기본 SSH 포트는 builder `2226`, QEMU `2224`, QBox `2244`이며 loopback에 바인딩한다.
다른 VM이 사용 중이면 정상 종료하거나 `--builder-port`, `--qemu-port`,
`--qbox-port`를 각각 다른 포트로 지정한다. QBox full-system은 공유 리소스 때문에
포트만 바꿔 동시에 실행하지 않는다. `--dry-run`은 계획 출력이지 전체 선행 조건
검사나 부팅 검증이 아니다.

## 2. 설정 확인과 입력 준비

```bash
./build_autosd_minimal_qm.sh --dry-run
# 다운로드/도구/crun 준비만 수행. VM은 시작하지 않는다.
./build_autosd_minimal_qm.sh --prepare-inputs-only
```

기본 설정은 최초 다운로드 시 최신 official nightly와 최신 ARM64 AIB를 선택한다.
선택된 URL, manifest digest, checksum은 캐시에 기록한다. 같은 캐시에서는 그
입력을 검증해 재사용한다. 새 캐시에서는 새 버전이 선택될 수 있다.

고정 입력을 원하면 `autosd/config/minimal-qm.json`의 `nightly_build_id`와
`builder_reference`에 build ID와 registry SHA256 digest를 지정하거나 CLI를 사용한다.

```bash
./build_autosd_minimal_qm.sh --prepare-inputs-only \
  --nightly-build-id BUILD_ID \
  --builder-reference quay.io/centos-sig-automotive/automotive-image-builder@sha256:DIGEST
```

외부 서버가 특정 버전을 삭제하면 그 버전의 재다운로드는 불가능하다. 이 경우
명시적으로 소스 설정을 갱신한다. RPM 저장소 snapshot까지 고정하지 않으므로
byte-identical 재현이나 완전한 offline 빌드를 보장하지 않는다.

## 3. 이미지 생성부터 실제 부팅 검증까지

```bash
./build_autosd_minimal_qm.sh
```

입력 준비 후 격리된 ARM64 builder VM에서 AIB 빌드 → qcow2 회수/SHA 비교 →
QEMU UKI 부팅 → 필수 패키지·모듈 설치 → Automotive 구성 → 정상 종료 →
QBox full-system 네 도메인 부팅/guest 검사 → 정상 종료를 수행한다.

| 단계 | 확인하는 결과 |
|---|---|
| 입력 준비 | nightly checksum, ARM64 AIB digest, guestfish 동작, crun 소스/바이너리 hash |
| builder/AIB | matching 모듈 배포, 공식 manifest 빌드, qcow2·osbuild manifest 생성 |
| 결과 회수 | guest/host SHA256 일치, `qemu-img check`, builder 정상 종료 |
| QEMU | EFI/UKIBoot, 커널 release, SELinux Enforcing, QM PID namespace |
| Automotive | BlueChi root/QM online, Safety Monitor HEALTHY, ADAS/QM 서비스 |
| RT 준비 | root RT 패키지, QM stress-ng, 양쪽 probe 실행/hash 일치, RT 커널 및 timerlat/osnoise tracer |
| QBox full-system | RSE·SI CL0·SI CL1·AP 부팅 표식, HIPC/PFDI 모듈, guest 정상 상태 |
| 종료 | guest poweroff 및 QBox 정상 종료 receipt |

빌드는 ARM64 TCG VM에서 수행하므로 오래 걸릴 수 있다. 터미널에는 단계 명령이
표시되고 상세 출력은 작업 디렉터리에 기록된다. builder의 SELinux는 이미지 라벨
생성 동안만 일시 Permissive로 전환하고 복원한다. 최종 guest의 Enforcing 상태는
별도로 검사한다.

기본은 Automotive와 RT 도구 포함이다. 기본 minimal QM만 필요하면 `--minimal`을 사용한다.
Root에는 `realtime-tests`, `rtla`, `trace-cmd`, `stress-ng`, `util-linux`,
`procps-ng`를 설치한다. QM에는 정지된 rootfs를 대상으로 `stress-ng`를 설치하고,
RT bundle에서 Root/QM 양쪽으로 static `latency-probe`를 배치한다. Root의
`/usr/libexec/apollo/`에는 `rt-experiment.py`, `rt-trace.py`,
`check-automotive.sh`도 설치한다. 설치 절차 원본은
`autosd/customization/rt/prepare-guest.sh`이며 OSTree guest에서는 거부한다.

`customization-rt-packages/`, `qemu-rt-readiness/`, `qbox-rt-readiness/`에
패키지 버전·probe hash·실행 결과를 남긴다. 어느 단계든 실패하면 빌드 PASS로
처리하지 않는다. RT benchmark 자동 기동이나 watchdog 정책 변경은 없다.
실제 측정은 정상 종료된 최종 QBox `rootfs.wic`를 Dashboard의 `--rootfs`로
지정하고 Feature 04/05/06에서 실행한다. `regular.raw`는 준비한 기본 이미지이므로
customization이 적용된 최종 실행 디스크와 혼동하지 않는다.

공식 최소 이미지에는 SSH 서버와 tar가 없으므로 콘솔 자동 로그인 후 설치한다.
root/password SSH와 privileged AIB는 disposable guest에서만 사용하며, host
forwarding은 loopback으로 한정한다. 운영 환경의 인증 정책으로 사용하지 않는다.

```bash
# 기존 캐시·검증 결과를 보존하고 새 캐시에서 처음부터 재구성
./build_autosd_minimal_qm.sh --cache-dir build/autosd/new-build
# 이미 생성한 qcow2에서 부팅 및 customization부터 재검증
./build_autosd_minimal_qm.sh --image /path/minimal_qm.aarch64.qcow2 \
  --output build/autosd/recheck-prepared
```

기존 출력은 덮어쓰지 않는다. 재실행 때 `--output`, `--work-dir`, 필요 시
`--qbox-out-dir`에 새 경로를 지정한다. 실패한 VM은 진단을 위해 보존되므로 정상
종료한 뒤 재시도한다. `--prepare-inputs-only`는 완성된 입력 캐시를 검증해 재사용한다.

## 4. 실행

기본 경로로 빌드/검증을 마쳤다면:

```bash
./run_qbox_autosd.sh --dry-run
./run_qbox_autosd.sh
```

별도 `--cache-dir`를 사용했다면 `--autosd CACHE/demo-minimal-qm-prepared/regular.json`
을 실행기에 전달한다. 실행기는 동일 manifest의 full-system PASS 및 정상 종료
receipt를 가진 private 디스크를 선택한다. 변환 직후 raw와 customization을 설치한
실행 디스크는 다르다.

## 5. 생성 디렉터리와 삭제 영향

기본 캐시는 `build/autosd`이고 `--cache-dir`로 바꿀 수 있다.

```text
build/autosd/
  downloads/nightly/       # 다운로드 xz/checksum, qcow2, 선택 기록
  host-tools/              # 다운로드 deb, 추출 도구/커널, smoke 결과
  builder-base/            # nightly를 변환한 빌더 시작 이미지
  builder/                 # ARM64 AIB OCI archive, digest/checksum
  crun/                    # 소스 기반 빌드 결과, base image archive, provenance
  inputs.json              # 선택된 입력 기록 (설정 원본 아님)
  demo-minimal-qm-prepared/ # minimal_qm raw/initrd/BLS/manifest
  minimal-qm-build-*/      # 빌드/프로비저닝 로그, private builder/QEMU 디스크
```

QBox 실행 디스크와 네 도메인 UART는 `build/qbox-apollo-qvp/autosd-*/`에 생성된다.
모두 재생성할 수 있지만, 삭제하면 이전 실행 상태/증거도 없어진다. 설정 보존을
위해 예전 날짜 디렉터리의 archive나 `crun-cgroup-fix/crun`을 남길 필요는 없다.

이전 이미지의 실제 부팅 결과는 [검증 리포트](autosd-minimal-qm-validation-20260929-ko.md)에
있다. 새 cold-bootstrap 검증은 리포트의 후속 절을 참고한다. ASIL 인증, 전체
RT/IPC/OTA/watchdog fault-injection suite는 기본 정상 부팅 검사의 범위가 아니다.

## 6. 중간 결과물과 캐시 재사용

**입력 캐시 재사용과 AIB 증분 빌드는 다르다.** 현재 통합 스크립트는 이전 실행의
AIB 작업 디스크를 자동으로 이어받지 않는다.

| 호스트 위치 (`CACHE` = `--cache-dir`) | 내용 | 다음 실행에서의 처리 |
|---|---|---|
| `CACHE/downloads/nightly/` | 압축 이미지, qcow2, checksum | 요청 build ID 및 hash 일치 시 재사용 |
| `CACHE/builder/` | AIB OCI archive | 요청 reference 및 archive hash 확인 후 재사용 |
| `CACHE/builder-base/` | 시작용 raw/initrd | 원본 및 생성물 hash 확인 후 재사용 |
| `CACHE/host-tools/` | 도구·커널 패키지와 추출 파일 | 준비 절차와 실제 appliance 검사를 다시 수행 |
| `CACHE/crun/` | 소스, sysroot, 바이너리, base image archive | 소스/패치/빌드 스크립트/hash 일치 시 완성된 바이너리 재사용 |
| `WORK/builder/` | 빌더 OS와 scratch 디스크 | 실행마다 새로 생성, 자동 resume 없음 |
| `WORK/fetch/` | 완성된 qcow2 및 osbuild manifest | 명시적 `--image` 입력으로 재사용 가능 |
| `WORK/qemu/rootfs.wic` | 모듈·Automotive를 설치한 QEMU 디스크 | 해당 실행의 QBox 입력으로 복사 |

`WORK`는 `--work-dir`이며 기본값은 `CACHE/minimal-qm-build-<UTC시간>`이다.
AIB 중간 결과는 호스트 디렉터리에 직접 펼쳐지지 않고 아래 디스크에 저장된다.

```text
WORK/builder/scratch.raw       # 24 GiB 가상 디스크
  guest /srv/aib/work/cache/  # AIB 컨테이너 /work/cache, osbuild 캐시 한도 10GB
  guest /srv/aib/outer/       # 외부 AIB Podman 저장소
  guest /srv/aib/nested/      # AIB 내부 컨테이너 저장소
  guest /srv/aib/work/        # 생성 qcow2 및 osbuild manifest
```

같은 builder VM 안에서 AIB를 재시도하면 남은 캐시를 사용할 수 있지만, 통합
진입점은 기존 `--work-dir` 재사용을 거부한다. **현재 `--resume` 옵션이나 실행 간
공유 osbuild 캐시는 없다.** crun도 소스 변경 시 기존 object를 증분 컴파일하는
방식이 아니라 새 출력 경로에서 빌드한다.

### 6.1 같은 입력 캐시로 새 이미지 빌드

아래 예제의 출력 경로는 존재하지 않아야 한다. 이후 반복 시 `run-02`처럼 바꾼다.

```bash
./build_autosd_minimal_qm.sh \
  --cache-dir build/autosd \
  --output build/autosd/prepared-run-01 \
  --work-dir build/autosd/run-01 \
  --qbox-out-dir build/qbox-apollo-qvp/autosd-run-01
```

nightly/AIB/crun 입력은 재사용하지만 AIB OS 빌드와 부팅 검증은 새로 수행한다.
완료 후 실행:

```bash
./run_qbox_autosd.sh --autosd build/autosd/prepared-run-01/regular.json
```

### 6.2 완성된 qcow2로 AIB 빌드 생략

```bash
./build_autosd_minimal_qm.sh \
  --image build/autosd/run-01/fetch/minimal_qm.aarch64.qcow2 \
  --cache-dir build/autosd \
  --output build/autosd/prepared-recheck-01 \
  --work-dir build/autosd/recheck-01
```

builder VM/AIB 생성 단계만 생략한다. 이미지 변환, 필수 도구·모듈 설치,
Automotive 구성 및 QEMU/QBox 검사는 다시 수행한다. 이는 qcow2에서 시작하는
재검증이지 이전 private VM의 실행 상태 복원이 아니다.

### 6.3 설정·소스 변경 또는 완전 재생성

nightly ID, builder reference, crun 소스/패치가 기존 캐시와 다르면 불일치 오류가
발생한다. 자동 덮어쓰기 대신 새 캐시를 지정한다.

```bash
./build_autosd_minimal_qm.sh --cache-dir build/autosd/fresh-run-01
```

`build/autosd` 전체를 삭제한 경우에도 기본 명령으로 재생성할 수 있다. 다만
관련 VM/웹 서버를 정상 종료하고 필요한 결과를 보관한 뒤 정리해야 한다.
원본 설정은 `autosd/`·`scripts/`에 남아 있어야 하며, Apollo BSP와 호스트 도구는
앞 절의 선행 조건이다. 기존 캐시를 없애면 최초 선택 시점의 upstream 버전이
달라질 수 있다.

## 7. 진행 로그, 완료 판정, 실패 후 재시도

위 `run-01` 예제로 실행했다면 별도 터미널에서 확인한다. 해당 단계가 시작되기
전에는 로그 파일이 아직 없을 수 있다.

```bash
# AIB 상세 빌드 출력
tail -f build/autosd/run-01/aib/console.log
# QEMU 부팅 출력
tail -f build/autosd/run-01/qemu/linux-uart.log
# QBox AP 부팅 출력 (RSE/SI UART도 같은 출력 디렉터리에 존재)
tail -f build/qbox-apollo-qvp/autosd-run-01/linux-uart.log
```

입력 준비 단계는 콘솔 출력과 `CACHE/inputs.json`, `builder/metadata.json`,
`host-tools/environment.json`, `crun/provenance.json`으로 확인한다.
전체 실행의 최종 판정은 다음 파일이다.

```bash
python3 -m json.tool build/autosd/run-01/result.json
python3 -m json.tool build/qbox-apollo-qvp/autosd-run-01/result.json
```

`WORK/result.json`의 `status=PASS`, `live_owned_launchers=[]`를 확인한다.
QBox receipt는 `status=POWERED_OFF`, `passed=true`, `poweroff_observed=true`,
`domains.status=PASS`여야 한다. 개별 guest 로그의 QM/Automotive PASS도 함께
확인한다. 전체 PASS가 모든 warning이 없다는 뜻은 아니다.

| 증상 | 확인 및 대응 |
|---|---|
| 출력 경로가 이미 존재 | 기존 결과를 보존하고 새 output/work 경로 지정 |
| checksum/hash 불일치 | 로그를 보존하고 새 캐시에서 재다운로드; 검증 우회 금지 |
| registry digest가 사라짐 | 명시한 버전의 가용성 확인 후 소스 설정을 갱신 |
| host 도구/BSP 누락 | 1절의 선행 조건 준비; build/autosd만으로 BSP를 대체할 수 없음 |
| guest 패키지 다운로드 실패 | 네트워크·RPM repository 상태 확인, 해당 단계 로그 보존 |
| VM 단계 실패 | `live_owned_launchers`와 UART 확인, 해당 VM 정상 종료 후 새 작업 경로로 재시도 |

실패한 VM은 자동 강제 종료하지 않는다. 접속 가능하면 해당 VM의 SSH 포트로
로그인하여 `systemctl poweroff`를 실행하고 프로세스 종료를 확인한다. 접속이
안 되면 UART와 launcher 로그로 먼저 원인을 확인한다. 실행 중인 디스크를 삭제하거나
동일 포트·공유 리소스로 중복 부팅하지 않는다.
