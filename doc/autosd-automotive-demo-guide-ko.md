# AutoSD Automotive 데모 설계 및 전체 실행 가이드

2026-09-26 신규 이미지 빌드부터 실행까지의 결과는
[Quick Guide 재검증 리포트](autosd-quick-guide-revalidation-ko.md),
기존 regular 이미지 결과는 [초기 데모 검증 리포트](autosd-automotive-demo-validation-ko.md)에 기록했다.

브라우저 실행·로그·결과 그래프·CPU/subsystem 관측은
[웹 콘솔 Quick Guide](autosd-dashboard-guide-ko.md)를 참고한다.

## 1. 목적과 적용 범위

root의 safety monitor·Podman·BlueChi, ADAS 전용 실행 영역, QM native 앱과
nested container의 정상 실행·독립 제어·장애 감지·운영자 복구를 시연한다.
ADAS/QM 앱은 100 ms heartbeat 대체 프로그램이며 차량 제어 알고리즘이 아니다.
`asil-b`는 개발용 container/cgroup 이름이고 인증된 ASIL-B 파티션이 아니다.
CPU affinity와 메모리 설정 확인은 FFI, WCET, FTTI 보장이 아니다.

신규 AIB 전체 이미지 생성·native UKI 부팅·S01–S07은 실제 재검증했다.
기존 regular 이미지의 private copy + customization 설치 경로도 초기 검증에 사용했다.
OSTree OTA, Secure Boot 보안 검증, QBox는 이번 재검증 범위가 아니다.
구성 원본과 이미지 빌드 진입점은 [layer README](../autosd/customization/README.md),
기존 설치 검증은 [구성 리포트](autosd-customization-layer-ko.md)를 참고한다.

## 2. 데모 시나리오와 판정

PREEMPT_RT latency 측정과 원인 추적은 [RT 실험 Quick Guide](autosd-preempt-rt-guide-ko.md)의
선택 profile 및 R01–R08을 사용한다. 아래 S01–S07 서비스 기능 검증과 판정을 분리한다.

| ID | 조작 | PASS 조건 |
| --- | --- | --- |
| S01 | cold boot 후 서비스 검사 | root/ADAS/QM 자동 시작, BlueChi 두 노드 online, heartbeat 정상, Enforcing, CPU affinity 일치 |
| S02 | BlueChi로 QM native 앱 stop/start | 실제 inactive 확인, 정지 중 ADAS/nested heartbeat 정상, 재시작 후 전체 정상 |
| S03 | QM nested container에 SIGKILL | Restart 정책으로 새로운 container ID 생성, heartbeat 및 전체 상태 정상 |
| S04 | ADAS PID 1에 SIGSTOP | monitor 3회 실패 후 FAULT_LATCHED, ADAS container 부재, QM 서비스 계속 active |
| S05 | latch 상태에서 monitor restart | monitor failed, latch 유지, ADAS 재생성 없음, QM 두 heartbeat 정상 |
| S06 | 운영자가 상태 보존 후 latch 해제 | ADAS 먼저 시작, monitor HEALTHY, 전체 검사 통과 |
| S07 | 정상 전원 종료 후 새 copy cold boot | 설치나 수동 서비스 시작 없이 전체 검사 통과 |

S04의 `failed/exit-code/137`은 SIGSTOP으로 graceful stop이 불가능하여 SIGKILL로
종료된 결과다. 실제 container가 없어야 PASS다. S05의 monitor 실패도 의도된 판정이다.
S06은 실제 차량용 자동 복구 정책이 아니라 **운영자 명시적 복구 데모**다.
각 시험 제한은 240초이며 첫 실패에서 중단한다. 시간은 TCG 관찰값이지 deadline이 아니다.

## 3. Quick Guide — 이미지 빌드부터 실행·검증·종료까지

기존 실행 절차를 이 Quick Guide로 통합했다. 아래에서 경로 하나를 선택한다.

| 경로 | 시작점 | 진행 순서 | 검증 상태 |
| --- | --- | --- | --- |
| A: 새 OS 이미지 | BSP/kernel RPM + customization source | 3.1 → 3.2 → 3.3 A → 3.5 이후 | 전체 빌드·native UKI 부팅·S01–S07 재검증 PASS (console 자동 로그인은 미지원) |
| B: 기존 regular 이미지 | customization이 설치된 private disk | 3.1 → 3.3 B → 3.5 이후 | 실제 데모 검증 경로 |
| B-설치: 기존 minimal_qm | BlueChi/Podman이 준비된 regular disk | 3.1 → 3.2의 bundle 생성 → 3.3 B → 3.4 → 3.5 이후 | 기존 이미지 위 설치 검증 경로 |

명령은 Bash 기준이며 **host**, **native AArch64 builder**, **target guest**를 구분하여 실행한다.
A의 새 bootc/native UKI 디스크에 B의 regular initrd/manifest를 조합하지 않는다.
각 단계의 종료 코드/확인 조건이 성공한 경우에만 다음 단계로 진행한다.

### 3.1. 사전 준비 [host]

모든 host 명령은 workspace root `/build/arm/arm-auto-solutions`에서 실행한다.
Python3, Paramiko, 기존 Apollo QEMU provider/kernel을 준비한다. A의 host에는
Docker, `qemu-img`, SSH/SCP 및 ARM64 static GCC도 필요하다. B 실행에는
약 15 GiB 이상 여유 공간이 필요하며, A는 별도 native AArch64 builder의 OS/RPM/
container cache 공간이 추가로 필요하다. VM은 4 vCPU/4080 MiB를 사용한다. 아래 경로는 이 workspace의 로컬
산출물이며 Git clone만으로 생기지 않는다. 원본 VM이 종료되어 있는지 확인한다.

```sh
cd /build/arm/arm-auto-solutions
# 경로 B를 사용할 때만:
test -f build/autosd/automotive-scenario-coldboot/rootfs.wic
test -f build/autosd/demo-minimal-qm-prepared/regular.json
test -f build/tmp_baremetal/deploy/images/apollo-qvp/Image
ss -ltn 'sport = :2232'
python3 -m pytest -q tests/test_autosd_customization.py
```

2232가 이미 사용 중이면 기존 VM을 임의 종료하지 말고 다른 포트를 모든 명령에
일관되게 적용한다. SSH helper는 `127.0.0.1`의 root/password 데모 계정만 사용한다.
외부 네트워크 공개 또는 제품 계정으로 사용하지 않는다.
모든 `--out`/`--out-dir`은 **새 디렉터리**여야 한다. 재실행은 경로 접미사를 바꾼다.

### 3.2. BSP → kernel RPM → bundle → OS 이미지 빌드 [경로 A]

**① Apollo BSP 빌드 [host]** — 기존 산출물을 그대로 재현할 경우 생략한다.
공유 BitBake 빌드는 직렬 실행하고, 다른 빌드 중 설정을 변경하지 않는다.
`yocto_build.sh`는 `build/conf`를 template에서 다시 생성하므로 필요한 로컬 설정은
실행 전에 별도 보존하고 template과 비교한다.

```sh
./yocto_build.sh --machine apollo-qvp --bsp
test -f build/tmp_baremetal/deploy/images/apollo-qvp/Image
test -f build/tmp_baremetal/deploy/images/apollo-qvp/ukibootaa64.efi
```

확인: `build/conf/{local.conf,bblayers.conf,templateconf.cfg}`의 실제 machine/layer와
빌드 종료 상태. 이 명령은 BSP/kernel/U-Boot/UKIBoot를 준비하며 AutoSD OS 자체를
생성하지 않는다.

**② Apollo kernel RPM repository 생성 [host]** — Docker와 registry/RPM network
접근이 필요하다. 기존 일치하는 RPM repo가 있으면 재사용할 수 있다.

```sh
bash scripts/autosd_demo/kernel_rpm_build.sh \
  build/tmp_baremetal/deploy/images/apollo-qvp \
  build/tmp_baremetal/work-shared/apollo-qvp/kernel-build-artifacts \
  build/autosd/automotive-demo-kernel-rpm
test -f build/autosd/automotive-demo-kernel-rpm/repo/repodata/repomd.xml
```

이 packager와 manifest는 현재 `6.18.5-rt3-yocto-preempt-rt` /
`kernel-apollo-6.18.5-1.aarch64`에 맞춰져 있다. kernel release가 달라졌다면
패키징/manifest를 먼저 맞춘다. RPM 생성 성공은 새 커널의 AutoSD 부팅 PASS가 아니다.

**③ customization bundle 생성 [host, A/B-설치 공통]** — ARM64 static GCC,
Python yaml/jsonschema가 필요하다.

```sh
python3 autosd/customization/prepare.py --out build/autosd/automotive-demo-bundle
python3 -m pytest -q tests/test_autosd_customization.py
```

crun 1.29.1의 SELinux cgroup2 mount 메시지 보정까지 포함하려면 먼저
[런타임 빌드 절차](../autosd/customization/runtime/README.md)를 수행하고 위
`prepare.py`에 `--crun-binary build/autosd/crun-cgroup-fix/crun`을 추가한다.
root/QM 양쪽에 같은 SHA256의 런타임을 넣는다. 이 옵션 없는 번들은 vendor
런타임을 그대로 사용하며 해당 보정을 포함하지 않는다.

출력: `automotive.aib.yml`, `runtime-files.json`, `payload/workload`,
`build-guest.sh`, `install-private-guest.py`, `provenance.json`.
B-설치는 여기서 3.3 B로 이동한다. A는 아래 접근 설정 후 빌드한다.

**④ 새 이미지의 접근 설정 [host, A만]** — 생성된 `automotive.aib.yml`에는
공개 root password/SSH 설정이 없다. `content.rpms`에 `openssh-server`,
`content.systemd.enabled_services`에 `sshd.service`를 기존 목록을 보존하여 추가하고,
최상위에 아래 `auth`를 추가한다. 공개키 placeholder는 실제 시험용 공개키로 바꾼다.
개인키는 이미지에 넣지 않는다.

시험용 key가 없다면 host에서 다음과 같이 생성한다. 기존 key를 덮어쓰지 않는다.

```sh
AUTOSD_DEMO_KEY="$PWD/build/autosd/automotive-demo-key"
test ! -e "$AUTOSD_DEMO_KEY"
ssh-keygen -t ed25519 -N '' -C apollo-autosd-private-demo -f "$AUTOSD_DEMO_KEY"
cat "$AUTOSD_DEMO_KEY.pub"
```

```yaml
auth:
  root_ssh_keys:
    - "ssh-ed25519 REPLACE_WITH_YOUR_PUBLIC_KEY"
  sshd_config:
    PasswordAuthentication: false
    PermitRootLogin: prohibit-password
```

A는 아래 B 전용 `guest_exec.py`의 고정 password 인증을 사용하지 않는다.
SSH key로 root에 접속하고 같은 guest 검사 스크립트를 실행한다(3.5–3.7).
manifest를 편집했으므로 원래 bundle provenance와 함께 수정본도 보존한다.

**⑤ native builder에 입력 전달 [host → builder]** — 이미 준비한 격리된 native
AArch64 AIB builder를 사용한다. builder 자체를 새로 구축하는 절차는
[기존 AIB builder 작업 기록](autosd-ota-followup-ko.md)을 참고한다.
이 workspace의 종료된 기존 builder를 재사용할 때는 별도 host 터미널에서 다음을
실행한다. 디스크는 기존 builder 전용 디스크를 그대로 사용하고 UART만 새 경로에 남긴다.

```sh
python3 scripts/autosd_demo/ota_builder_resume.py --out build/autosd/automotive-guide-builder
```

builder 재부팅 후 scratch는 자동 mount되지 않을 수 있다. **입력 전달 전에**
builder에서 `lsblk -f`와 `blkid`로 기존 scratch의 LABEL/UUID를 확인한다.
이 workspace의 scratch label은 `apollo-aib-scrat`이다. 새 filesystem을 만들거나
디스크를 포맷하지 않는다. 확인된 기존 scratch만 다음과 같이 mount한다.

```sh
# native builder root에서 실행:
lsblk -f
mountpoint -q /srv/aib || mount /dev/disk/by-label/apollo-aib-scrat /srv/aib
findmnt /srv/aib
df -h /srv/aib
```

이번 재검증에서는 기존 cache가 있는 24 GiB scratch의 시작 여유 7.4 GiB로는
부족했다. OCI 생성 후 disk 변환 중 사용률 99%가 되어 변환을 중단하고 40 GiB로
확장했다. 총 크기만 보지 말고 기존 사용량과 변환 중 추가 사용량을 함께 확인한다.
아래는 **이 workspace의 확인된 기존 ext4 scratch** 확장 절차다. 다른 디스크에
그대로 적용하거나 `mkfs`를 실행하지 않는다.

```sh
# builder: 진행 중인 빌드를 중단하고 컨테이너 종료를 확인한 다음
systemctl poweroff
# host: UART Power down과 QEMU 프로세스 종료, host 여유 공간 확인 후
df -h /build
qemu-img info -f raw build/autosd/demo-builder-fullsystem/scratch.raw
qemu-img resize -f raw build/autosd/demo-builder-fullsystem/scratch.raw 40G
python3 scripts/autosd_demo/ota_builder_resume.py --out build/autosd/automotive-guide-builder-expanded
# 재부팅한 builder: lsblk/UUID로 대상 확인 후 기존 filesystem 확장
test "$(blkid -s UUID -o value /dev/disk/by-label/apollo-aib-scrat)" = 8c4d0da8-b098-4885-b027-4bc7c7d2af8f
mountpoint -q /srv/aib || mount /dev/disk/by-label/apollo-aib-scrat /srv/aib
resize2fs /dev/disk/by-label/apollo-aib-scrat
df -h /srv/aib
```

위 launcher는 별도 host 터미널에서 유지한다. 확장은 24→40 GiB의 증가에만
해당하며, 이미 40 GiB보다 큰 파일을 축소하지 않는다. OCI/cache는 삭제하지 않는다.

아래 `AUTOSD_BUILDER`는 실제 SSH alias로 설정하며 host x86_64에서 AIB native
명령을 직접 실행하지 않는다.

```sh
AUTOSD_BUILDER=your-native-aarch64-builder
tar -C build/autosd/automotive-demo-bundle -czf build/autosd/automotive-demo-bundle.tar.gz .
tar --exclude=.git -C autosd/automotive-image-builder \
  -czf build/autosd/automotive-demo-aib-source.tar.gz .
tar -C build/autosd/automotive-demo-kernel-rpm/repo \
  -czf build/autosd/automotive-demo-kernel-repo.tar.gz .
ssh "$AUTOSD_BUILDER" 'mkdir /srv/aib/automotive-demo-build'
scp build/autosd/automotive-demo-bundle.tar.gz \
  build/autosd/automotive-demo-aib-source.tar.gz \
  build/autosd/automotive-demo-kernel-repo.tar.gz \
  "$AUTOSD_BUILDER":/srv/aib/automotive-demo-build/
```

**⑥ helper 및 OS 이미지 빌드 [native AArch64 builder, root]** — `/srv/aib`는
충분한 여유 공간이 있는 기존 builder scratch mount여야 한다. 아래 privileged
container는 격리된 builder에서만 실행한다. 기존 builder 작업과 병렬 실행하지 않는다.

```sh
test "$(uname -m)" = aarch64
mountpoint /srv/aib
cd /srv/aib/automotive-demo-build
mkdir bundle source repo
tar -xzf automotive-demo-bundle.tar.gz -C bundle
tar -xzf automotive-demo-aib-source.tar.gz -C source
tar -xzf automotive-demo-kernel-repo.tar.gz -C repo
# 기존 builder의 검증된 helper/storage/cache 재사용 (공유 빌드 직렬 실행):
AUTOSD_NESTED=/srv/aib/ota/nested
AUTOSD_CACHE=/srv/aib/work/cache
test -d "$AUTOSD_NESTED/aib-tmp"
test -d "$AUTOSD_CACHE"
podman --root /srv/aib/outer --runroot /run/apollo-aib run --rm \
  --name apollo-automotive-build --privileged --network host \
  --security-opt label=disable \
  -e AIB_TMPDIR_BASE=/var/lib/containers/storage/aib-tmp \
  -v "$PWD/source:/src:ro" -v "$PWD/repo:/apollo-kernel-repo:ro" \
  -v "$PWD/bundle:/manifest" -v "$AUTOSD_NESTED:/var/lib/containers/storage" \
  -v "$AUTOSD_CACHE:/manifest/cache" \
  --workdir /manifest \
  quay.io/centos-sig-automotive/automotive-image-builder@sha256:179a58db45306498791d2011b7cbd4d5e20ace29d7e9d51e95bb987c98027c36 \
  /bin/bash -euc '
    /src/bin/aib build-builder --distro autosd10-sig --arch aarch64 \
      --build-dir /manifest/cache --cache-max-size 10GB --if-needed
    bash /manifest/build-guest.sh /manifest/automotive.qcow2
  '
test -s bundle/automotive.oci.tar
test -s bundle/automotive.qcow2
sha256sum bundle/automotive.oci.tar bundle/automotive.qcow2
```

helper는 disk 변환에 필요하며 workload image와 같은 persistent nested Podman
storage를 사용한다. OS RPM 다운로드에는 network가 필요하다. OCI만 생성되고
QCOW2 변환이 실패한 경우 전체 빌드 성공으로 표시하지 않는다. 기존 OCI/cache를
삭제하지 말고 오류를 확인한다. build script는 기존 output을 덮어쓰지 않는다.
OCI와 disk를 함께 요청한 경우 AIB는 임시 OCI를 먼저 container storage에 등록한 뒤
`automotive.oci.tar`로 이동한다. 따라서 osbuild의 `finished successfully`만 보고
최종 OCI 파일 회수가 끝났다고 판단하지 말고 위 `test -s`와 SHA 확인까지 수행한다.
새 builder라면 `AUTOSD_NESTED`/`AUTOSD_CACHE`를 새 전용 디렉터리로 지정하고
`aib-tmp` 하위 디렉터리도 만든다. 이 경우 helper/cache를 처음부터 생성하므로
기존 builder 재사용보다 시간과 디스크가 더 필요하다.
nightly repository 내용이 바뀌면 `--if-needed`도 helper를 재빌드한다. AArch64
TCG에서 helper와 대상 build environment를 모두 갱신하면 전체 빌드에 수 시간이
필요할 수 있으므로 명령 종료와 로그의 실제 진행을 확인한다.
nightly 입력은 고정 snapshot이 아니므로 이전 이미지와 동일한 digest를 기대하지 않는다.

**OCI 성공 후 disk 변환만 재시도 [native builder]** — 실패 로그를 먼저 보존하고
공간/오류 원인을 해결한다. 기존 build container가 종료됐는지 확인한다. 다음은
동일 source/helper/storage와 보존된 OCI를 사용하며 OS를 다시 빌드하지 않는다.
QCOW2가 이미 존재하면 아래 명령을 실행하지 말고 완성 여부부터 확인한다.

```sh
cd /srv/aib/automotive-demo-build
test -s bundle/automotive.oci.tar
test ! -e bundle/automotive.qcow2
podman --root /srv/aib/outer --runroot /run/apollo-aib run --rm \
  --name apollo-automotive-convert --privileged --network host \
  --security-opt label=disable \
  -e AIB_TMPDIR_BASE=/var/lib/containers/storage/aib-tmp \
  -v "$PWD/source:/src:ro" -v "$PWD/repo:/apollo-kernel-repo:ro" \
  -v "$PWD/bundle:/manifest" \
  -v /srv/aib/ota/nested:/var/lib/containers/storage \
  -v /srv/aib/work/cache:/manifest/cache --workdir /manifest \
  quay.io/centos-sig-automotive/automotive-image-builder@sha256:179a58db45306498791d2011b7cbd4d5e20ace29d7e9d51e95bb987c98027c36 \
  /src/bin/aib to-disk-image --no-vm --oci-archive \
    /manifest/automotive.oci.tar /manifest/automotive.qcow2
test -s bundle/automotive.qcow2
sha256sum bundle/automotive.oci.tar bundle/automotive.qcow2
```

**⑦ 이미지 회수 및 raw 변환 [host]**

```sh
scp "$AUTOSD_BUILDER":/srv/aib/automotive-demo-build/bundle/automotive.qcow2 \
  build/autosd/automotive-demo-bundle/automotive.qcow2
sha256sum build/autosd/automotive-demo-bundle/automotive.qcow2
test ! -e build/autosd/automotive-demo-bundle/automotive.raw
qemu-img convert -f qcow2 -O raw \
  build/autosd/automotive-demo-bundle/automotive.qcow2 \
  build/autosd/automotive-demo-bundle/automotive.raw
```

builder와 host의 QCOW2 SHA-256이 같아야 한다. 이후 3.3 A로 진행한다.

**선택: 로컬 ext4 scratch에서 빠르게 회수 [host]** — TCG의 SSH 전송이 느리면
builder에서 SHA-256을 기록한 뒤 `systemctl poweroff`한다. 반드시 UART `Power down`,
QEMU 프로세스 종료 및 scratch를 열고 있는 프로세스 부재를 확인한다.
아래는 partition table 없이 ext4가 직접 들어 있는 이 builder의 `scratch.raw`에만
해당한다. 실행 중인 VM 디스크에는 적용하지 않는다. `debugfs`에 `-w`를 주지 않는다.

```sh
test ! -e build/autosd/automotive-demo-bundle/automotive.qcow2
debugfs -R 'dump /automotive-demo-build/bundle/automotive.qcow2 build/autosd/automotive-demo-bundle/automotive.qcow2' \
  build/autosd/demo-builder-fullsystem/scratch.raw
sha256sum build/autosd/automotive-demo-bundle/automotive.qcow2
qemu-img check -f qcow2 build/autosd/automotive-demo-bundle/automotive.qcow2
# builder에서 기록한 SHA와 일치한 뒤 위 raw 변환 명령 수행
```

이 절차는 SSH/SCP 회수를 대체하며, 두 방법을 동시에 실행하지 않는다.

### 3.3. 이미지 부팅 [host 터미널 A]

**A: 새 AIB 이미지 — native UKI 경로, 신규 customization 이미지 부팅 검증 완료**

```sh
./run_qemu_linux.sh \
  --native-autosd-disk build/autosd/automotive-demo-bundle/automotive.raw \
  --ukiboot-dir build/tmp_baremetal/deploy/images/apollo-qvp \
  --headless --timeout 1800 \
  --out-dir build/autosd/automotive-demo-run \
  --netdev user,id=net0,hostfwd=tcp:127.0.0.1:2232-:22
```

**B: customization 설치 완료 regular 이미지 — 검증된 재현 경로**

터미널 A에서 다음을 실행하고 유지한다. launcher가 원본을 private copy하므로
원본 디스크를 직접 수정하지 않는다. `--reuse-disk` 같은 공유 사용 옵션을 추가하지 않는다.

```sh
./run_qemu_linux.sh \
  --autosd build/autosd/demo-minimal-qm-prepared/regular.json \
  --rootfs build/autosd/automotive-scenario-coldboot/rootfs.wic \
  --headless --timeout 1800 \
  --out-dir build/autosd/automotive-demo-run \
  --netdev user,id=net0,hostfwd=tcp:127.0.0.1:2232-:22
```

터미널 B에서 `tail -f build/autosd/automotive-demo-run/linux-uart.log`로 부팅 로그를
볼 수 있다. SSH와 QM 시작까지 기다린 뒤 아래 suite를 실행한다. 준비가 덜 되었으면
시험을 강제로 통과시키지 말고 systemd/journal을 확인한다.

### 3.4. 선택: 기존 minimal_qm에 customization 설치 [B-설치만]

customization이 없는 경우 3.3 B의 `--rootfs`를 기존 regular minimal_qm+
BlueChi+Podman이 구성된 **종료된** 디스크 경로로 바꿔 부팅한다. 단순 nightly
minimal 이미지는 대체할 수 없다. 새 AIB/OSTree 이미지에는 이 설치기를 쓰지 않는다.
3.2 ③에서 만든 bundle을 host 터미널 B에서 전달한다.

```sh
tar -C build/autosd/automotive-demo-bundle -czf build/autosd/automotive-demo-bundle.tar.gz .
python3 scripts/autosd_demo/guest_exec.py --port 2232 \
  --out build/autosd/automotive-demo-install-run \
  --upload build/autosd/automotive-demo-bundle.tar.gz:/root/automotive-demo-bundle.tar.gz \
  --command 'mkdir /root/automotive-demo-bundle && tar -C /root/automotive-demo-bundle -xzf /root/automotive-demo-bundle.tar.gz && python3 /root/automotive-demo-bundle/install-private-guest.py' \
  --timeout 600
```

확인: `LAYER_INSTALLED`. 이미 구성된 B 이미지와 A 이미지는 이 단계를 생략한다.

### 3.5. 부팅 준비 확인 [host 터미널 B]

SSH가 열린 시점에 QM의 BlueChi node는 아직 offline일 수 있다. 다음 read-only
준비 검사는 최대 180초 기다리며 서비스를 시작하거나 재시작하지 않는다.

**B: 기존 데모 계정**

```sh
python3 scripts/autosd_demo/guest_exec.py --port 2232 \
  --out build/autosd/automotive-demo-ready-run \
  --upload autosd/customization/wait-ready-guest.sh:/root/wait-ready-guest.sh \
  --command 'bash /root/wait-ready-guest.sh' --timeout 220 --connect-timeout 60
```

**A: 빌드 시 설정한 SSH key** — `AUTOSD_DEMO_KEY`는 host의 실제 개인키 경로로
설정한다. 아래는 3.2에서 생성한 시험 key 경로다. 새 copy 재부팅 시 host key 경고가
나면 fingerprint를 확인하고 처리한다.

```sh
AUTOSD_DEMO_KEY="$PWD/build/autosd/automotive-demo-key"
scp -i "$AUTOSD_DEMO_KEY" -P 2232 \
  autosd/customization/{wait-ready-guest.sh,check-guest.sh,fault-guest.sh,demo-guest.py} \
  root@127.0.0.1:/root/
ssh -i "$AUTOSD_DEMO_KEY" -p 2232 root@127.0.0.1 'bash /root/wait-ready-guest.sh'
ssh -i "$AUTOSD_DEMO_KEY" -p 2232 root@127.0.0.1 \
  'set -e; test -d /sys/firmware/efi; test -e /run/ostree-booted; uname -a; systemctl is-active ukiboot-set-success.service; ukibootctl dump; test "$(ukibootctl get-booted)" = "$(ukibootctl get-active)"'
```

현재 launcher는 console의 `root/password` 자동 로그인을 시도한다. A의 key-only
이미지는 이 로그인이 실패하므로, 정상 SSH 부팅/종료 후에도 launcher의
`login_observed=false`, `status=FAIL`이 나올 수 있다. 이를 부팅 성공 증거로 사용하거나
로그인 PASS로 바꾸지 않는다. A에서는 위 SSH EFI/OSTree/UKIBoot 검사, 3.6의 데모
결과, 실제 QEMU 종료와 UART `Power down`을 각각 확인한다. console 로그인 판정은
**key-only 인증 방식 미지원**으로 별도 기록한다.

### 3.6. S01–S06 실행과 증거 수집 [host 터미널 B]

**B: 기존 데모 계정**

```sh
python3 scripts/autosd_demo/guest_exec.py --port 2232 \
  --out build/autosd/automotive-demo-suite-run \
  --upload autosd/customization/demo-guest.py:/root/demo-guest.py \
  --upload autosd/customization/check-guest.sh:/root/check-guest.sh \
  --upload autosd/customization/fault-guest.sh:/root/fault-guest.sh \
  --command 'cd /root && python3 demo-guest.py --allow-disruptive-demo --out /root/automotive-demo-evidence' \
  --timeout 1500 \
  --download /root/automotive-demo-evidence/results.json:scenarios.json

python3 scripts/autosd_demo/guest_exec.py --port 2232 \
  --out build/autosd/automotive-demo-archive-run \
  --command 'set -e; journalctl -b -u apollo-safety-monitor -u apollo-adas -u qm --no-pager > /root/automotive-demo-evidence/journal.log; cd /root; python3 -m tarfile -c automotive-demo-evidence.tar.gz automotive-demo-evidence' \
  --download /root/automotive-demo-evidence.tar.gz:evidence.tar.gz
```

새 A 이미지에는 `tar` 실행 파일이 없으므로 guest archive는 이미 설치된 Python의
`tarfile` 모듈을 사용한다. host의 tar 명령과 구분한다.

`scenarios.json`의 여섯 항목이 모두 PASS여야 한다. host helper의 PASS 하나만으로
전체 성공을 판정하지 않는다. guest 디렉터리에는 시나리오별 `.log`, `results.json`,
해제 전 `fault-before-recovery.json`이 남는다. archive 명령은 실패 시에도 실행해서
원인을 보존한다. launcher 디렉터리의 `launch.json`, `linux-uart.log`, `result.json`도
유지한다. SSH timeout은 guest 명령을 완전히 정리한다는 보장이 없으므로 즉시
중복 실행하지 말고 프로세스와 service 상태를 먼저 확인한다.

**A: SSH key 경로** — 검사 내용은 B와 동일하다. 첫 명령이 끝난 뒤 archive를 수집한다.

```sh
ssh -i "$AUTOSD_DEMO_KEY" -p 2232 root@127.0.0.1 \
  'cd /root && python3 demo-guest.py --allow-disruptive-demo --out /root/automotive-demo-evidence'
ssh -i "$AUTOSD_DEMO_KEY" -p 2232 root@127.0.0.1 \
  'set -e; journalctl -b -u apollo-safety-monitor -u apollo-adas -u qm --no-pager > /root/automotive-demo-evidence/journal.log; cd /root; python3 -m tarfile -c automotive-demo-evidence.tar.gz automotive-demo-evidence'
mkdir build/autosd/automotive-demo-archive-run
scp -i "$AUTOSD_DEMO_KEY" -P 2232 \
  root@127.0.0.1:/root/automotive-demo-evidence.tar.gz \
  root@127.0.0.1:/root/automotive-demo-evidence/results.json \
  build/autosd/automotive-demo-archive-run/
```

### 3.7. S07: 전원 종료 → cold boot → 최종 종료

**B: 기존 데모 계정**, host 터미널 B:

```sh
python3 scripts/autosd_demo/guest_exec.py --port 2232 \
  --out build/autosd/automotive-demo-poweroff-run \
  --command 'systemctl poweroff'
```

SSH 연결 종료만으로 성공을 판단하지 않는다. 터미널 A가 끝나고 UART의 filesystem
unmount와 `Power down`, launcher 종료 결과를 확인한다. **QEMU 종료 후** 다음을
터미널 A에서 실행한다.

```sh
./run_qemu_linux.sh \
  --autosd build/autosd/demo-minimal-qm-prepared/regular.json \
  --rootfs build/autosd/automotive-demo-run/rootfs.wic \
  --headless --timeout 600 \
  --out-dir build/autosd/automotive-demo-reboot-run \
  --netdev user,id=net0,hostfwd=tcp:127.0.0.1:2232-:22
```

부팅 후 터미널 B:

```sh
python3 scripts/autosd_demo/guest_exec.py --port 2232 \
  --out build/autosd/automotive-demo-reboot-check-run \
  --command 'bash /root/wait-ready-guest.sh && bash /root/check-guest.sh' --timeout 300
python3 scripts/autosd_demo/guest_exec.py --port 2232 \
  --out build/autosd/automotive-demo-reboot-off-run \
  --command 'systemctl poweroff'
```

마지막 VM도 종료될 때까지 기다린다. fault 상태는 `/run`이므로 reboot를 넘어서
보존되지 않는다. 영속 fault latch가 필요한 제품은 별도 설계가 필요하다.

**A: native UKI 경로** — B 명령 대신 아래 명령을 사용한다. 첫 poweroff 후 반드시
터미널 A의 QEMU 종료를 확인한 뒤, 두 번째 launcher는 터미널 A에서 실행한다.

```sh
ssh -i "$AUTOSD_DEMO_KEY" -p 2232 root@127.0.0.1 'systemctl poweroff'
# QEMU 종료를 확인한 다음 터미널 A:
./run_qemu_linux.sh \
  --native-autosd-disk build/autosd/automotive-demo-run/rootfs.wic \
  --ukiboot-dir build/tmp_baremetal/deploy/images/apollo-qvp \
  --headless --timeout 600 --out-dir build/autosd/automotive-demo-reboot-run \
  --netdev user,id=net0,hostfwd=tcp:127.0.0.1:2232-:22
# 부팅 후 터미널 B:
ssh -i "$AUTOSD_DEMO_KEY" -p 2232 root@127.0.0.1 \
  'bash /root/wait-ready-guest.sh && bash /root/check-guest.sh'
ssh -i "$AUTOSD_DEMO_KEY" -p 2232 root@127.0.0.1 'systemctl poweroff'
```

두 경로 모두 UART `Power down`과 launcher 종료를 확인하고 로그/private disk를
보존한다. A의 boot-success/OTA health 정책 검증은 이 smoke demo와 별개다.
A의 launcher console-login FAIL은 3.5의 조건에 따라 분리하여 판정한다.
이번 A 실행에서는 종료 중 `/dev/loop0` busy/해제 실패 경고 후 Power down이
관찰됐다. 이를 완전한 loop teardown 성공으로 표시하지 않는다. 경고와 재부팅
결과는 재검증 리포트에 함께 보존했다.

### 3.8. 실패 시 진단·수동 복구 [target guest]

guest에서 `journalctl -b -u apollo-safety-monitor -u apollo-adas -u qm`,
`bluechictl status host`, `bluechictl status qm.host`, `podman ps -a`,
`podman exec qm systemctl --failed`로 earliest failure를 확인한다.
SELinux를 permissive로 바꾸거나 timeout을 무조건 늘려서 통과시키지 않는다.
TCG profile probe timeout은 10초이며 실제 차량 timing 요구사항 값이 아니다.

S04/S05 이후 중단되었다면 증거 수집 후 다음 복구를 **private guest에서만** 수행한다.
상태 파일 삭제는 latch를 명시적으로 해제하는 조작이다.

```sh
systemctl stop apollo-safety-monitor
cp /run/apollo-safety/state.json /root/fault-before-manual-recovery.json
python3 -c 'from pathlib import Path; Path("/run/apollo-safety/state.json").unlink()'
systemctl reset-failed apollo-adas apollo-safety-monitor
systemctl start apollo-adas
podman exec apollo-adas /workload health /run/heartbeat
systemctl start apollo-safety-monitor
# HEALTHY가 된 뒤:
bash /root/check-guest.sh
```

이 명령은 실제 actuator 안전성 확인을 대체하지 않는다. 시험 중 알 수 없는 실패라면
복구 전에 로그부터 수집하고 VM을 정상 종료하는 것이 우선이다.

### 3.9. QBox full-system 전원·SBSA watchdog 확장

QEMU 데모와 별도로 RSE·SI CL0·SI CL1·AP를 실행하는 경우에는
[full-system Quick Guide](autosd-fullsystem-dashboard-ko.md)를 따른다.
다른 full-system VM을 정상 종료하고 private 실행 디스크를 복사할 여유 공간을
확인한 뒤 `./run_qbox_autosd.sh --reset-trace`로 시작한다.
SI CL1 진입 주소는 launcher가 사용 중인 ELF/bin의 일치 여부와 CRC를 확인한 뒤
자동으로 설정한다. Zephyr를 재빌드한 뒤 옛 RVBAR 주소를 수동으로 재사용하지 않는다.
실제 선택 값은 실행 디렉터리의 `full-system/si-cl1-boot.json`에서 확인한다.

- 정상 종료: guest에서 `systemctl poweroff` 또는 `shutdown -h now`.
- 전체 재부팅: `systemctl reboot`; 새 boot ID와 모든 domain/모듈 준비를 확인한다.
- watchdog: [Guest Quick Guide](autosd-watchdog-guest-ko.md)의 준비 → 읽기 전용
  inspect → keepalive → 명시적 만료 시험 순서로 진행한다. 설치는
  `prepare.py --watchdog-tools` opt-in이며 기본 부팅에서 자동 만료시키지 않는다.

watchdog WS1은 SI CL0가 조정하는 **AP 단독 reset**이고, 정상 reboot의 전체 domain
reset과 다르다. systemd feeding과 만료 도구는 동시에 실행하지 않는다.
실제 결과와 남은 제한은 [전원·watchdog 검증 보고서](autosd-power-watchdog-validation-ko.md)에
기록한다. 이 시험을 물리 하드웨어 timing 또는 ASIL 인증으로 해석하지 않는다.

### 3.10. 웹 Mixed criticality / Watchdog 확장

[MC01–MC03 / WD01–WD04 Quick Guide](autosd-mixed-watchdog-demo-ko.md)에 따라
QBox full → Power on → 자동 상태 검사 → MC 묶음 → WD01–WD03 묶음 →
별도 동의한 WD04 순으로 실행한다. 각 단계는 Feature & Demo 하위 버튼으로도
실행할 수 있고, Host/Guest 로그와 완료 후 기능 결과 표를 제공한다.
WD04는 AP reset을 포함하므로 일반 watchdog 묶음에 포함하지 않는다.
