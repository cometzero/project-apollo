# AutoSD crun cgroup mount 보정

AutoSD에서 사용 중인 crun 1.29.1의 새 mount API 경로는 공유 cgroup2
superblock에도 컨테이너별 SELinux mount label을 적용한 뒤 실패하면 label 없이
재시도한다. 따라서 컨테이너가 시작되어도 kernel에 `Same superblock, different
security settings`가 남는다. 본 패치는 `cgroup`/`cgroup2`만 기존
`do_mount_cgroup_v2()`와 동일하게 `LABEL_NONE` 처리한다. SELinux Enforcing,
process label, 다른 filesystem label, cgroup namespace 및 자원 제한은 유지한다.

원본: [crun 1.29.1 linux.c](https://github.com/containers/crun/blob/1.29.1/src/libcrun/linux.c).
패치 기준 commit: `f0d911de5587342cfeb16473bf32ecdfeaf25957`.

## 빌드

### 처음부터 다시 생성 (권장)

`build/autosd`는 입력 설정을 보관하는 곳이 아니라 삭제 가능한 출력 경로이다.
아래 진입점은 `autosd/crun`의 고정 Git 소스와 이 디렉터리의 패치만 사용한다.
이전 `crun-cgroup-fix`, 실행 중인 dependency container 또는 sysroot는 필요 없다.

```bash
bash autosd/customization/runtime/build-crun.sh \
  --output build/autosd/crun-cgroup-fix
```

Docker, AArch64 binfmt, host `aarch64-linux-gnu-gcc`, autotools, pkg-config,
Python 3, make, patch가 필요하다. 스크립트는 digest로 고정된 CentOS ARM64
이미지를 공식 `stream10` tag에서 ARM64 digest로 resolve하여 매번 registry pull로
가용성을 검증하고 별도 unprivileged container에 EL10 개발 RPM을
설치한다. 해당 sysroot를 복사하여 host에서 cross compile한 뒤 자신이 만든
container만 제거한다. 기존 출력 디렉터리는 덮어쓰지 않는다.
RPM 저장소와 base image 다운로드를 위한 네트워크가 필요하다.

`--dry-run`은 생성 없이 경로를 확인한다. `--base-image`로 다른 공식 CentOS
digest를 지정할 수 있지만 EL10/AArch64 ABI 호환성은 별도로 확인해야 한다.
명시한 digest를 가져오지 못하면 실패하며 다른 버전으로 자동 대체하지 않는다.
기본 tag는 변경될 수 있으므로 실제 사용 digest는 출력에 기록한다.
출력에는 `crun`, sysroot/source copy, source commit, 패치 checksum, RPM 목록,
compiler/version 및 빌드 로그가 포함된다. target guest에서 `crun --version`과
`ldd`를 확인해야 하며 compile 성공만으로 guest 기능 검증을 대체하지 않는다.
Base image는 출력의 `base-image.docker.tar`에도 보관하며 기존 Docker cache는
필수 입력이 아니다. `provenance.json`에는 소스 commit, 패치·binary·archive와
빌드 스크립트 SHA256을 기록하므로 cache 재사용 시 입력 일치 여부를 검사한다.

아래의 container/cross 진입점은 수동 작업용 저수준 인터페이스이다.

Docker와 기존 AArch64 binfmt가 필요하다. privileged 실행이나 Docker socket
mount는 사용하지 않는다. clone은 `autosd/` 아래에만 생성한다.

```bash
git clone --depth 1 --branch 1.29.1 --recurse-submodules --shallow-submodules \
  https://github.com/containers/crun.git autosd/crun
mkdir -p build/autosd/crun-cgroup-fix
CRUN_BASE_IMAGE=$(python3 autosd/customization/runtime/resolve-centos-image.py)
docker pull --platform linux/arm64 "$CRUN_BASE_IMAGE"
docker run --rm --platform linux/arm64 \
  -v "$PWD/autosd/crun:/src:ro" \
  -v "$PWD/autosd/customization/runtime:/fix:ro" \
  -v "$PWD/build/autosd/crun-cgroup-fix:/out" \
  "$CRUN_BASE_IMAGE" \
  bash /fix/build-crun-container.sh
```

입력 소스는 고정하고 base image는 실행 시 digest를 기록하지만 dnf repository는 움직이므로 bit-for-bit
재현 빌드는 아니다. 배포 시 실제 binary SHA256 및 build log를 보관한다.
빌드 산출물은 EL10 AArch64용이며 다른 distro/ABI에 사용하지 않는다.

### qemu-user의 autotools 실행이 느린 경우

`autogen.sh`는 아키텍처 독립적인 configure/Makefile 입력을 생성하므로
호스트에서 수행할 수 있다. 별도 source copy에 패치를 적용하고
`./autogen.sh`를 실행한다. 이미 build dependency 설치를 끝낸 컨테이너는
정지 후 `docker commit CONTAINER autosd-crun-builder:local`로 보존한다
(이 경우 최초 실행에서 `--rm`을 사용하지 않는다). 준비된 source copy를
`/work`에 mount하여 다음처럼 configure/compile만 AArch64에서 실행한다.

```bash
docker run --platform linux/arm64 \
  -v "$PRECONFIGURED_SOURCE:/work" \
  -v "$PWD/autosd/customization/runtime:/fix:ro" \
  -v "$PWD/build/autosd/crun-cgroup-fix:/out" \
  autosd-crun-builder:local bash /fix/build-crun-preconfigured.sh
```

`PRECONFIGURED_SOURCE`는 원본 clone이 아닌 별도 작업 복사본의 절대 경로이다.
패치 적용 여부와 원본 commit은 스크립트가 검사한다. 이 경로는
`builder-packages.txt`도 기록한다. 패키지 관리자는 반드시 직렬로 실행한다.

### 권장: EL10 sysroot를 이용한 호스트 cross build

QEMU-user의 C 컴파일도 느리면 dependency 설치를 마친 **실행 중인** builder의
header/library를 별도 디렉터리에 복사하여 호스트 cross compiler를 사용한다.
호스트에 `aarch64-linux-gnu-gcc`, autotools, pkg-config, Python 3가 필요하다.

```bash
bash autosd/customization/runtime/build-crun-cross.sh \
  apollo-crun-compile autosd/crun build/autosd/crun-cross-repro
```

마지막 인자는 새 디렉터리여야 한다. 이 스크립트는 빌드 컨테이너/원본 clone을
수정하지 않으며 source copy, sysroot, compiler version, RPM 목록 및 빌드 로그를
보관한다. 대상 guest에서 `--version`과 `ldd`를 확인한 뒤 설치한다. qemu-user의
직접 실행은 crun의 memfd 재실행 때문에 실패할 수 있으므로 native guest 검증을
대체하지 않는다.

이번 적용 artifact는 `build/autosd/crun-cgroup-fix/crun-cross`이며 SHA256은
`8a685e3d99443332d7003b2137c43b574ab4e01a3a4647711fda3e9e2f1ee170`이다.
root와 QM에서 모든 기존 feature flag 및 동적 library 연결을 확인했다.
해당 artifact를 사용할 때 아래 `--crun-binary` 경로를 `crun-cross`로 바꾼다.
동일 SHA256의 canonical `build/autosd/crun-cgroup-fix/crun`도 제공한다.

Cold boot 검증(`build/autosd/crun-coldboot-verify-20260927`)은 PASS이며
해당 boot의 `SELinux: mount invalid`는 0건이다. Enforcing과 root/QM/nested
process label, CPU 1/2–3 격리, CPUWeight 200/50, MemoryMax 512 MiB/1 GiB,
전체 health 및 bridge hook 3개 활성화를 확인했다. 이는 가상 플랫폼의 기능
검증이며 물리적 시간 격리 또는 ASIL 인증을 의미하지 않는다.

## 이미지 반영

```bash
python3 autosd/customization/prepare.py --rt-tools \
  --crun-binary build/autosd/crun-cgroup-fix/crun \
  --out build/autosd/customization-crun-fixed
```

root와 QM의 `/usr/bin/crun`을 동일 artifact로 overlay하고 `provenance.json`에
SHA256을 기록한다. 이는 vendor RPM 자체를 다시 만든 것이 아닌 임시 보정
overlay이다. 배포 제품은 동일 패치를 적용한 서명된 crun RPM으로 통합해야 한다.

기존 private regular VM에서는 binary와 `install-crun-private-guest.sh`를 업로드해
`bash install-crun-private-guest.sh BINARY SHA256`으로 설치한다. 이 스크립트는
원본을 `.apollo-vendor-backup`으로 보존하고 inode를 원자적으로 교체하며
SELinux label을 복구한다. 설치 후 별도로 정상 재부팅하고 kernel journal,
root/QM/nested 컨테이너 상태, cgroup 제한, `getenforce`를 확인한다.

## Bridge

`/etc/modules-load.d/apollo-container-network.conf`가 부팅 초기 `br_netfilter`를
로드하여 Podman bridge의 netfilter hook을 명시적으로 활성화한다. kernel의
bridge module 안내 문구는 `CONFIG_BRIDGE_NETFILTER=m`일 때 조건 없이 출력되므로
이 문구 자체가 없어지지는 않는다. `lsmod`와 `net.bridge.bridge-nf-call-*`로
적용 상태를 확인한다. veth의 blocking → forwarding 전이는 정상 동작이다.
