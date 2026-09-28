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

Docker와 기존 AArch64 binfmt가 필요하다. privileged 실행이나 Docker socket
mount는 사용하지 않는다. clone은 `autosd/` 아래에만 생성한다.

```bash
git clone --depth 1 --branch 1.29.1 --recurse-submodules --shallow-submodules \
  https://github.com/containers/crun.git autosd/crun
mkdir -p build/autosd/crun-cgroup-fix
docker run --rm --platform linux/arm64 \
  -v "$PWD/autosd/crun:/src:ro" \
  -v "$PWD/autosd/customization/runtime:/fix:ro" \
  -v "$PWD/build/autosd/crun-cgroup-fix:/out" \
  quay.io/centos/centos@sha256:fd6b1e14d330489aac4624aeb6269428163b6fd557cfb572fd1098c73109e84b \
  bash /fix/build-crun-container.sh
```

입력 소스와 base image는 고정했지만 dnf repository는 움직이므로 bit-for-bit
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
