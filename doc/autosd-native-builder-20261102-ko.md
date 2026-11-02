# AutoSD native 빌더 통합 검증

## 최종 결과

**rootful native 빌더로 ARM64 minimal_qm qcow2 생성과 오프라인 검증에 성공했다.**
rootless는 이 Ubuntu 호스트의 SELinux xattr 제한으로 실패하며, 조기 검사에서 거부한다.

- 이미지: `build/autosd/native-builder-20261102/rootful-cross-v2/fetch/minimal_qm.aarch64.qcow2`
- SHA256: `b1e199073127e00c65a93f955147516222949290eec167f595e49606f6a0c6c3`
- 가상 크기 8 GiB, 실제 할당 약 1.08 GiB, `qemu-img check` PASS.
- 읽기 전용 guestfish 검사 PASS: AutoSD 10, Root/QM `/usr/bin/bash` 모두 AArch64,
  `6.12.0-280.el10iv.aarch64` 모듈, AArch64 `BOOTAA64.EFI`, `ukibootaa64.efi` 존재.
- `SELINUX=enforcing`, `SELINUXTYPE=automotive`; `/usr/bin/bash`의 실제 xattr는
  `system_u:object_r:shell_exec_t:s0`. 설정과 라벨 검증이며 부팅 후 Enforcing 검증은 아니다.
- 관련 Python 테스트 70개 PASS, `git diff --check` PASS.
- 후속 QBox full-system 검증: **부팅·QM PASS, 종료 포함 전체 FAIL**.
  종료 중 TF-A assertion과 콘솔 수동 개입 내역은
  [부팅 검증 보고서](autosd-native-boot-20261102-ko.md)에 기록했다.
- **NOT_RUN:** Automotive/RT 후속 설치 및 데모 시나리오.
  이번 생성물은 공식 minimal_qm 이미지이며 최종 customization 완료 이미지가 아니다.

rootful loop-device 수정 후 재실행은 919.13초(약 15분 19초)였다. 기존 source/native
build 캐시를 사용했고 일부 rootless 실험과 겹쳤으므로 독립 cold-build 성능값이 아니다.
검증 로그는 `rootful-resume.log`, `guestfish-filesystems.log`, `guestfish-inspection.log`이다.

## 구성

Ubuntu x86_64에서 AIB/OSBuild/bwrap/Podman 및 빌드 도구 rootfs를 native로 실행하고,
AutoSD/QM 대상 rootfs만 ARM64로 구성한다. 대상 RPM scriptlet은 호스트 binfmt의
qemu-user로 실행된다. 기존 ARM64 빌더의 namespace clone EINVAL을 우회하는 대신,
namespace 생성 자체를 native bwrap에 맡긴다.

- `download_builder.py`: 호스트에 맞는 amd64/arm64 이미지 선택과 SHA 검증.
- `bootstrap.py`: `builder-amd64/` 또는 `builder-arm64/` 캐시 분리.
- `builder_podman.py`: native 이미지 확인, namespace 검사, mode별 권한 및 장치 설정.
- `native_build.py`: native/target AIB manifest compose, native build pipeline과 target
  pipeline 결합, OSBuild 실행과 qcow2 변환.
- `build_minimal_qm.py`: 이후 이미지 준비·Automotive/RT 설치·QBox 검증 흐름 유지.

`build` pipeline은 native compose 결과를 그대로 사용한다. 대상의
`qm_rootfs_base`, `rootfs` RPM 단계에만 `ignorearch`를 적용한다. GPG key와 SHA256
설정은 유지한다. 동일 noarch RPM의 arch별 URL 차이는 동일 SHA256일 때만 허용한다.
공식 AIB가 native/target 분리를 자동 지원한다고 주장하지 않으며 이 결합은
프로젝트의 통합 계층이다.

## 실험 입력과 로그

- AIB multiarch index: `sha256:37ce37564e1c76b6db707aa53800a77e112dfdc6167a2da77f93d4ce679f548f`
- native image config: `sha256:f0e8bce009e5915a1c2908b8113936c20fcce3fd6610662495a77eaac0059665`
- AIB 1.3.6, OSBuild 193, Podman 4.9.3, qemu-user 8.2.2
- 공식 `minimal_qm.aib.yml`, `autosd10-sig`, target `qemu`, target arch `aarch64`
- 로그와 생성물: `build/autosd/native-builder-20261102/`

| 실행 | 관찰 |
|---|---|
| `rootful.log` | native namespace PASS, ARM64 build root RPM의 architecture 검사에서 FAIL |
| `rootful-cross.log` | native/target compose PASS, noarch RPM URL 중복 처리에서 FAIL; 수정함 |
| `rootful-cross-v2.log` | native build root, ARM64 QM/Root 설치 및 이미지 조립 진행; 새 loop device가 컨테이너에 없어 FAIL (1061.21초) |
| `rootful-resume.log` | `/dev` 제공 후 동일 manifest와 기존 source/build 캐시로 재실행, 이미지 생성 및 qemu-img check PASS (919.13초) |
| `rootless-cross.log` | native namespace PASS, native build root SELinux 라벨 쓰기 EPERM으로 FAIL (154.26초) |
| `rootless-preflight.log` | rootless xattr 제한을 RPM 설치 전에 검사, 4.85초에 명확한 오류로 종료 |

rootful/rootless 기능 검증은 일부 시간대에 겹쳤고, 재실행은 캐시 조건도 다르다.
실행 시간은 성능 비교값이 아니다. 기존 QBox/Dashboard 디스크는 변경하지 않았다.

## rootless 제한

이 호스트에서는 rootless native 컨테이너가 build store에 `security.selinux` xattr를
기록할 수 없다. AIB VM의 `image` pipeline에 진입하기 전에 native `build` pipeline의
`org.osbuild.selinux`가 실패한다. `/dev/kvm` 접근은 가능하지만 이 실패를 해결하지 않는다.
SELinux labeling을 생략하거나 호스트 보안 정책을 완화하지 않았다.

따라서 현재 rootless 옵션은 이 호스트에서 빌드 완료가 가능한 경로가 아니다.
사전 검사에서 명확히 거부하며, rootless 완결에는 전체 빌드 VM 또는 SELinux
metadata를 안전하게 보존하는 별도 build-store 설계가 필요하다.

## 실행

```bash
# 기본 rootful native 경로. 전체 스크립트에 sudo를 붙이지 않는다.
./build_autosd_minimal_qm.sh \
  --output build/autosd/native-prepared \
  --work-dir build/autosd/native-build

# rootless capability 검사 포함. 현재 호스트는 xattr 제한으로 실패한다.
./build_autosd_minimal_qm.sh --rootless \
  --output build/autosd/native-rootless-prepared \
  --work-dir build/autosd/native-rootless-build
```

기존 경로는 덮어쓰지 않으므로 각 실행은 새 경로를 사용한다. rootful 컨테이너는
공식 wrapper와 같이 `/dev`를 제공받으며 host root 권한을 가진다. OSBuild는
생성한 image 파일을 loop device에 연결한다. host 디스크를 빌드 대상으로 지정하지 않는다.

build cache에는 `build`, `qm_rootfs_base`, `rootfs`, `image-tree` checkpoint를 남긴다.
통합 스크립트의 실행 간 자동 resume은 제공하지 않는다. 이번 loop-device 재시도는
작업자가 실패 manifest와 해당 실행의 캐시를 명시적으로 선택한 진단 실행이다.
