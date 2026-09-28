# AutoSD Automotive Customization Layer 구성 및 검증

검증일: 2026-09-26. 소스: `autosd/customization/`.

## 요청 구성의 구현

| 요청 영역 | 구현 | 관찰된 실행 상태 |
| --- | --- | --- |
| root | Python safety monitor, Podman, BlueChi controller와 host agent | HEALTHY 및 fault latch 동작 확인 |
| asil-b | `apollo-adas` 컨테이너, `apollo-asil-b.slice`, heartbeat ADAS 대체 앱 | CPU 1, slice MemoryMax 512 MiB, `container_t` |
| qm | AutoSD QM 환경의 native 앱 및 nested container, QM BlueChi agent | CPU 2–3, MemoryMax 1 GiB, `qm_t`/`qm_container_t` |

기존 AutoSD 아키텍처의 root/QM 두 기본 영역을 사용하고, root 관리 하에
ADAS 전용 실행 영역을 추가했다. `asil-b`는 독립 VM/디스크 파티션이 아니라
namespace와 cgroup으로 분리한 개발용 컨테이너다. BlueChi 노드는 `host`와
`qm.host`이며 ADAS 서비스는 `host`에서 관리한다. 네트워크 없는 ADAS/QM 데모
컨테이너의 rootfs는 read-only, capability는 제거하고 writable `/run`만 제공한다.

사용자 ADAS 제어 코드와 QM 앱이 제공되지 않았으므로 정적 ARM64 heartbeat
프로그램을 대체 앱으로 사용했다. 실제 차량 제어 기능은 구현 범위에 포함되지 않는다.
AutoSD 공식 `autosd/sig-docs/docs/definitions.md`의 ASIL 정의에 따라 이 구성을
ASIL-B 인증 또는 안전 등급 워크로드 지원으로 표시하지 않는다.

## 산출물

- [구성 및 사용법](../autosd/customization/README.md)
- `prepare.py`: Apollo kernel 설정을 재사용하고 AIB manifest/binary bundle 생성.
- `build-guest.sh`: native AArch64 AIB 환경에서 OCI 및 disk image 생성 진입점.
- `root/`: BlueChi 연동, ADAS Quadlet/slice, safety monitor와 systemd unit.
- `qm/`: 일반 앱 systemd unit 및 nested container Quadlet.
- `install-private-guest.py`: 기존 regular private VM에서 layer 실행 검증용 설치.
- `check-guest.sh`, `fault-guest.sh`: 정상 상태 및 ADAS 정지 fault 검사.
- `tests/test_autosd_customization.py`: manifest, 실제 heartbeat, monitor fault 유지 시험.

생성 bundle: `build/autosd/automotive-customization-final/`.
공개 데모 password 및 항상 성공하는 boot check는 제품 manifest에서 제외했다.
root/QM 컨테이너는 bundle 내 scratch image를 양쪽에 embed한다.

## 검증 결과

1. 집중 pytest **4 PASS**: AIB schema, 이동 가능한 file reference, 실제 C
   heartbeat의 정상/정지/손상 감지, monitor 3회 연속 실패 및 재시작 거부,
   probe timeout 실패 처리.
2. 실제 AIB `ManifestLoader`의 manifest 변환 **PASS**.
   `extra-include.ipp.yml` 생성까지 확인했다. 초기 직접 호출의 `arch` 미지정
   오류는 AArch64 build context를 전달하여 해결했다.
3. QEMU guest 정상 상태 **PASS**: BlueChi host/QM online, root ADAS와 QM의
   native/nested 앱 실행, heartbeat 응답, CPU affinity, MemoryMax, SELinux
   Enforcing 확인. 증거: `build/autosd/automotive-monitor-timeout-fix/` 및
   `automotive-layer-fault-retry/`.
4. ADAS fault injection **PASS**: `podman kill --signal STOP apollo-adas` 후
   monitor의 DEGRADED → FAULT_LATCHED(3회), ADAS 컨테이너 종료, QM 앱과
   nested container 계속 실행. 증거: `automotive-layer-fault-retry/`.
5. fault 유지 및 BlueChi 실제 제어 **PASS**: monitor 재시작이 fault를 지우거나
   ADAS를 재시작하지 않음. `bluechictl stop/start qm.host apollo-qm-app.service`
   실행과 실제 systemd 상태를 확인. 증거: `automotive-layer-latch-bluechi/`.
6. 전원 종료 후 새 private copy의 cold boot **PASS**: 별도 설치/수동 start 없이
   모든 서비스, BlueChi 두 노드, heartbeat, CPU/메모리 및 SELinux domain을
   재확인했다. `/run`의 이전 fault는 부팅으로 초기화되고 monitor는 HEALTHY였다.
   증거: `automotive-scenario-coldboot/`, `automotive-layer-coldboot-check/`.
7. 최종 guest 설정과 소스의 SHA-256 일치 확인: monitor Python, monitor unit,
   ADAS Quadlet. 실제 container inspect에서도 network `none`, read-only root,
   CPU `1`, memory `402653184` byte를 확인했다.
   증거: `automotive-layer-final-evidence/`.

시험 VM 두 실행 모두 guest `systemctl poweroff`로 종료했고 마지막 UART에서
filesystem unmount와 `Power down`, launcher exit 0을 확인했다.
수정된 private disk와 로그는 `build/autosd/automotive-scenario-*`에 보존했다.

cold boot UART에는 cgroup2 mount의 SELinux security settings 불일치 경고가
있지만 위 서비스/앱 검사는 모두 통과했다. 이 경고를 SELinux 정책 완전성이나
격리 인증 PASS로 해석하지 않는다. 기존 이미지가 가진 정책과 런타임을 이용한 결과다.

fault로 SIGSTOP된 PID 1은 SIGTERM에 응답하지 않으므로 Podman은 10초 후
SIGKILL로 종료했다. 해당 ADAS unit은 `failed`, `Result=exit-code`, exit 137을
남겼다. fault 검사는 정상 종료로 위장하지 않고 실제 컨테이너 부재와 QM 실행을
확인한다. 초기 검사에서 `inactive`만 허용하여 실패한 로그는
`automotive-layer-fault/`에 보존했다.

초기 probe timeout 2초는 동시 검사가 실행되는 TCG에서 오탐을 발생시켰다.
`automotive-layer-check/`, `automotive-layer-monitor-diagnostic/`에 실패 증거가
있다. Apollo profile은 `APOLLO_PROBE_TIMEOUT=10`을 사용하도록 수정하고
정상/fault 시험을 다시 통과했다. 이 값은 차량용 실시간 deadline이 아니다.

## 검증 범위와 제품 적용 시 필요한 사항

이번 실행은 기존에 검증된 regular AutoSD private 이미지 위에 신규 layer를
설치한 QEMU 4 CPU / 4080 MiB 시험이다. 기존 원본의 별도 copy를 사용했다.
커널은 `6.18.5-rt3-yocto-preempt-rt`, Image SHA-256은
`9f953c06bbdee67187d4583566546b2272a687bf223196debed0b1855d10a8ab`이다.

신규 manifest의 전체 AIB image build 및 그 이미지의 OTA, QBox 실행은 아직
검증하지 않았다. 기존 AutoSD EFI/OTA 검증은 이 새 layer의 이미지 검증을 대신하지
않는다. 새 image 빌드에는 기존 native AIB helper와 kernel RPM repository가 필요하다.

실제 제품 적용에는 다음 입력이 필요하다.

- 실제 ADAS 제어 앱/health protocol과 차량 safe-state interface.
- QM native RPM 및 digest 고정 container image.
- ASIL 요구에 맞는 OS/하드웨어/FFI 및 safety case.
- 실측 WCET/FTTI에 근거한 감시 주기, timeout, CPU/메모리 할당.
- 제품용 registry 인증, 서명, Secure Boot, OTA health 및 복구 정책.

root monitor는 Podman을 제어하는 권한이 있고 기본 컨테이너/QM SELinux 정책을
사용한다. root 전체 CPU 고정이나 전용 ASIL SELinux domain, 독립 safety MCU,
hypervisor 기반 partition 및 시간 격리 증명은 구현하지 않았다.
