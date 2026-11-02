# AutoSD ARM64 Podman 빌드 비교 — 2026-11-02

## 결과

sudo 권한은 정상 적용됐다. 그러나 두 경로 모두 이미지 생성에 실패했으므로
완료 시간이나 성능 배율은 산정할 수 없다. 이전에 제시한 1.5~4배 예상은
이 실험으로 검증되지 않았으며 성능 근거로 사용하지 않는다.

| 실행 | AIB 옵션 | 결과 | 실패까지 wall time |
|---|---|---|---:|
| rootful Podman + qemu-user | `--no-vm` | FAIL: bwrap namespace clone | 220.03초 |
| rootless Podman + AIB VM | `--vm --no-sudo` | FAIL: VM 진입 전 bwrap namespace clone | 199.39초 |

두 실행은 호환성 확인을 위해 일부 시간대에 겹쳐 실행했다. rootful/rootless의
컨테이너 저장소 캐시 조건도 다르다. 위 수치는 pull·RPM 다운로드를 포함한 실패까지의
시간이며 속도 비교용 벤치마크가 아니다. 두 실험 컨테이너는 종료·정리됐고 기존
QBox/Dashboard 디스크는 수정하지 않았다. QBox 부팅 검증은 NOT_RUN이다.

## 동일 입력

- 호스트: Ubuntu x86_64, Podman 4.9.3, qemu-user 8.2.2
- manifest: `autosd/sig-docs/demos/minimal_qm/minimal_qm.aib.yml`
- AIB: `quay.io/centos-sig-automotive/automotive-image-builder@sha256:37ce37564e1c76b6db707aa53800a77e112dfdc6167a2da77f93d4ce679f548f`
- distro/target/arch: `autosd10-sig` / `qemu` / `aarch64`
- 별도 작업 디렉터리, 기본 manifest, 기존 이미지 덮어쓰기 없음

## 원인과 최소 재현

두 빌드 모두 manifest 생성과 RPM 다운로드를 수행한 후 OSBuild build pipeline에서
다음 오류로 종료됐다.

```text
bwrap: Creating new namespace failed: Invalid argument
```

같은 ARM64 컨테이너의 최소 명령 결과:

```text
unshare --mount --pid --fork /bin/true  -> exit 0
bwrap --unshare-pid --ro-bind / / /bin/true -> exit 1
```

`QEMU_STRACE=1`로 확인한 실패 syscall:

```text
clone(CLONE_NEWNS|CLONE_NEWPID|0x11, ...) = -1 errno=22 (Invalid argument)
```

즉 단순 unshare 성공은 OSBuild 호환성을 보장하지 않는다. rootful privileged에서도
같은 실패가 재현되므로 sudo를 더 부여할 문제가 아니다. ARM64 bwrap을 실행하는
qemu-user의 namespace clone 경로가 현재 환경의 차단점이다.

추가로 내부 Podman은 `crun --version`의 memfd 재실행 실패를 출력했다.
이 오류 이후에도 AIB는 진행했으므로 최종 종료 원인인 bwrap 실패와 구분한다.

소스의 `aib/main_dev.py`는 VM 대상에 `image` pipeline을 추가하고,
`aib/osbuild.py`는 이를 `--in-vm image`로 전달한다. 모든 AIB 실행을 VM으로
감싸는 것이 아니므로 container-side build pipeline 실패를 우회하지 못한다.

## 반영한 변경 및 다음 경로

- 기존 진입점에 `--rootless` 추가; 빌더의 sudo/chown 호출 없이 `--vm --no-sudo` 전달.
- rootful/rootless 모두 빌드 전 bwrap 검사 추가; 지원되지 않는 환경에서는 조기에 실패.
- 기존 QBox full-system 최종 검증 흐름 유지.
- 관련 Python 테스트 57개 PASS. 전체 이미지 생성 PASS를 의미하지 않는다.

이 호스트에서 빌드를 완결하려면 AIB/OSBuild/bwrap을 ARM64 전체 VM 안에서 실행하거나,
호스트 native orchestration과 ARM64 target 실행을 분리해야 한다. 후자는 별도 통합과
cross-architecture 검증이 필요하다. bwrap 격리를 제거하거나 호스트 보안 정책을
완화하는 방식은 적용하지 않았다.

## 증거

생성 로그: `build/autosd/podman-comparison-20261102/`

- `rootful.log`, `rootless.log`: 빌드 출력과 `/usr/bin/time -p` 결과
- `namespace-probe.log`: unshare/bwrap 최소 재현
- `bwrap-strace.log`: qemu-user syscall trace
- `rootful/fetch/minimal_qm.osbuild.json`, `rootless/fetch/minimal_qm.osbuild.json`: 생성 manifest

이 디렉터리는 삭제 가능한 생성물이다. 완성 qcow2는 생성되지 않았다.

## 후속 조사: namespace 실패 원인과 해결책

### 원인 확정

호스트에서 사용한 QEMU 8.2.2의 upstream `linux-user/syscall.c`는
`CLONE_NEWNS`, `CLONE_NEWPID` 등을 지원하지 않는 플래그로 분류한다.
`do_fork()`는 `CLONE_INVALID_FORK_FLAGS` 검사에서 `-TARGET_EINVAL`을 반환한다.
이 경로는 요청된 namespace clone을 호스트 커널에 전달하기 전에 거부한다.
로컬 QEMU checkout에도 같은 제한이 있지만, 현재 binfmt 실행 파일은 Ubuntu의
qemu-user 8.2.2이며 로컬 checkout 빌드가 아니다.

따라서 다음을 구분해야 한다.

- `unshare()` 후 일반 fork: 이번 최소 재현에서 성공.
- `clone(CLONE_NEWNS | CLONE_NEWPID | SIGCHLD)`: qemu-user에서 실패.
- native x86_64 bwrap의 namespace clone: 같은 ARM64 컨테이너 안에서 성공.

추가 sudo, host sysctl 또는 AppArmor 정책 완화는 이 QEMU 분기 자체를 바꾸지
않는다. 최신 QEMU 공식 문서에도 namespace 관련 clone 제한이 명시되어 있어
단순 버전 업데이트로 해결된다고 가정할 수 없다. QEMU에서 플래그 검사만 제거하면
현재의 `fork()`가 요청된 namespace를 만들지 않으므로 올바른 수정이 아니다.

근거:

- [QEMU 8.2.2 syscall.c](https://github.com/qemu/qemu/blob/v8.2.2/linux-user/syscall.c)
- [QEMU user-mode threading 제한](https://www.qemu.org/docs/master/user/main.html)
- [bubblewrap namespace 구성](https://github.com/containers/bubblewrap/blob/main/README.md)

### 실제 검증한 해결 방법: native bwrap + ARM64 payload

namespace 생성은 x86_64 bwrap이 수행하고, 생성된 namespace 안의 ARM64
프로그램만 기존 binfmt/qemu-user로 실행했다. bwrap 격리를 제거하지 않았다.

| 컨테이너 모드 | bwrap 실행 방식 | 결과 |
|---|---|---|
| rootful | ARM64 bwrap → qemu-user | FAIL: clone EINVAL |
| rootless | ARM64 bwrap → qemu-user | FAIL: clone EINVAL |
| rootful | native x86_64 bwrap → ARM64 shell | PASS: `aarch64`, `pid=1` |
| rootless | native x86_64 bwrap → ARM64 shell | PASS: `aarch64`, `pid=1` |

rootless 재현 명령(Ubuntu x86_64 전용 진단):

```bash
podman run --rm --privileged --platform linux/arm64 \
  -v /usr/bin/bwrap:/native/bwrap:ro \
  -v /lib/x86_64-linux-gnu:/native/lib:ro \
  --entrypoint /native/lib/ld-linux-x86-64.so.2 \
  quay.io/centos-sig-automotive/automotive-image-builder@sha256:37ce37564e1c76b6db707aa53800a77e112dfdc6167a2da77f93d4ce679f548f \
  --library-path /native/lib /native/bwrap \
  --unshare-pid --as-pid-1 --ro-bind / / \
  /bin/sh -c 'uname -m; echo pid=$$'
```

`--privileged`는 rootless 사용자 namespace 내 권한이며 이 명령은 sudo를 사용하지
않는다. rootful 대조 실험은 같은 명령의 Podman만 `sudo -n podman`으로 실행했다.
호스트 라이브러리 디렉터리는 컨테이너의 `/native/lib`에 읽기 전용으로 제공했고,
호스트 rootfs 전체를 마운트하거나 호스트 정책을 변경하지 않았다.

로그는 `build/autosd/namespace-diagnosis-20261102/native-bwrap-{rootful,rootless}.log`이다.

### 적용 범위와 권장 방향

이번 결과는 namespace 차단점의 해결을 입증한다. 전체 AIB 이미지 생성까지
검증한 것은 아니다. bwrap 파일만 x86_64 바이너리로 덮어쓰면 ARM64 이미지에
native loader/library가 없으므로 위처럼 실행 환경까지 함께 제공해야 한다.

전체 빌드의 권장 구조는 호스트 native AIB/OSBuild/bwrap/Podman이 namespace와
이미지 조립을 담당하고 ARM64 RPM scriptlet·target 도구만 qemu-user로 실행하는
것이다. ARM64 이미지 안에 native bwrap wrapper를 넣는 방식도 시험할 수 있지만,
nested Podman/crun의 memfd 재실행, seccomp filter의 아키텍처, VM 실행기의
아키텍처까지 추가로 확인해야 한다. native bwrap 하나로 모든 문제가 해결됐다고
간주하지 않는다. 실험용 호스트 라이브러리 bind는 재현 가능한 제품 빌드 설정을
대신하지 않는다.

rootless 모드에서 namespace 생성 성공은 privileged filesystem/loop-device 작업의
권한까지 제공하지 않는다. 디스크 조립에는 AIB VM 경로를 유지해야 한다.
native orchestration을 통합하기 어렵다면 AIB 전체를 ARM64 system VM 안에서
실행하는 기존 방식이 대안이다. 이번 조사에서는 빌드 기본 경로를 자동 변경하지 않았다.
