# Apollo AutoSD Automotive Customization Layer

기존 Apollo BSP kernel과 AutoSD AIB의 `content`/`qm.content` 구조에
automotive scenario를 추가하는 제품 구성 layer다. Yocto layer가 아니라
AutoSD manifest, Quadlet, systemd 및 애플리케이션 bundle이며 root 저장소가 관리한다.

| 실행 영역 | 구성 | 관리 경로 | 기본 자원 |
| --- | --- | --- | --- |
| root | safety monitor, Podman, BlueChi controller/agent | BlueChi `host`, systemd | monitor CPU 0 |
| asil-b | ADAS control 대체용 heartbeat 컨테이너 | `host`의 `apollo-adas.service`, `apollo-asil-b.slice` | CPU 1, slice 512 MiB, 컨테이너 384 MiB |
| qm | 일반 앱 + nested Podman 컨테이너 + BlueChi agent | `qm.host` | CPU 2–3, 1 GiB, CPUWeight 50 |

`partition`은 여기서 실행 격리 영역이다. `asil-b`는 root가 관리하는
전용 컨테이너/cgroup이며 별도 디스크 파티션, VM 또는 세 번째 BlueChi 노드가
아니다. QM은 AutoSD 기존 imageless container와 정책을 사용한다.
root 전체를 CPU 0에 묶지는 않으며, CPUWeight 50은 CPU 50% 제한이 아니다.
이 profile은 CPU 4개 이상을 전제로 한다.

AutoSD 공식 [정의](../sig-docs/docs/definitions.md)는 AutoSD가 ASIL 등급
워크로드에 적합하지 않다고 명시한다. `asil-b`는 개발용 영역명이며 ASIL-B
인증, freedom from interference, 실시간 deadline, 안전 제어를 보장하지 않는다.
기본 SELinux container/QM 격리를 사용하며 별도 인증된 ASIL SELinux domain은 없다.

## 애플리케이션 및 감시 계약

`apps/workload.c`는 실제 ADAS 제어 알고리즘을 대신하는 정적 ARM64 데모다.
100ms마다 monotonic timestamp를 atomic rename으로 기록한다. `health`는
timestamp가 1초 이내인지 확인하고, 없거나 손상되었거나 오래되면 실패한다.
ADAS 컨테이너는 network 없음, read-only root, capability 제거, writable tmpfs
`/run`을 사용한다. QM에는 같은 프로그램을 native systemd 앱과 컨테이너로 배치한다.

root monitor는 ADAS 컨테이너 안에서 health command를 실행한다.
연속 3회 실패하면 `/run/apollo-safety/state.json`에 `FAULT_LATCHED`를 기록하고
`apollo-adas.service`를 중지한다. 정상 응답은 연속 실패 수를 초기화한다.
fault는 monitor 서비스 재시작으로 해제되지 않으며 reboot 또는 운영자의 명시적
상태 파일 정리가 필요하다. 이 동작은 데모 프로세스 정지이고 차량 actuator의
safe state 전환은 구현하지 않는다. root 권한 관리자는 서비스를 다시 시작할 수
있으므로 이 monitor는 보안 경계 또는 독립적인 safety MCU가 아니다.

기본 probe timeout은 2초이며 Apollo TCG profile에서는 10초를 사용한다.
각 probe 완료 후 1초 대기하므로 고정 1Hz 감시나 실시간 반응시간을 의미하지 않는다.
실제 앱 적용 시 heartbeat 내용, 인증된 health protocol, FTTI, 정지/복구 정책과
CPU/메모리 예산을 제품 요구사항에 맞춰 교체해야 한다.

## Bundle 생성

workspace root에서 실행한다. Python yaml/jsonschema와 ARM64 정적 C toolchain이 필요하다.

```sh
python3 autosd/customization/prepare.py \
  --out build/autosd/automotive-customization
python3 -m pytest -q tests/test_autosd_customization.py
```

출력은 `automotive.aib.yml`, `runtime-files.json`, `payload/workload`,
scratch `Containerfile`, build/install script와 `provenance.json`이다.
manifest는 현재 checkout의 AIB schema로 검사한다. source file은 bundle 내 상대
경로 또는 inline content여서 host→builder 이동이 가능하다. 새로운 output directory만
사용하며 기존 산출물은 덮어쓰지 않는다.

## OS 이미지 빌드

기존 private AArch64 builder의 AIB container에 다음 경로를 준비한다.

- 이 workspace의 수정된 `autosd/automotive-image-builder`를 `/src`로 mount.
- `kernel-apollo-6.18.5-1.aarch64.rpm`과 repodata를 `/apollo-kernel-repo`로 mount.
- 위 bundle을 읽기/쓰기 `/manifest`로 mount.
- 기존 native AIB container storage/cache를 사용한다.

그 container 안에서:

```sh
bash /manifest/build-guest.sh /manifest/automotive.qcow2
```

build script는 네트워크 없이 scratch workload image를 구성한 뒤 동일 Podman
storage의 이미지를 root 및 QM에 embed하도록 AIB에 전달한다.
OS RPM 취득에는 기존 AIB repository 연결이 필요하다. `/src/bin/aib build`는
기존 OTA와 같은 bootc 경로이며 disk export에는 native builder helper가 필요하다.
전체 이미지 생성은 이 layer의 unit test나 기존 이미지 위 설치 검증과 구분한다.

기본 manifest에는 공개 root password/SSH 접근을 넣지 않는다. 제품에 필요한
`auth.root_ssh_keys`와 SSH package/service는 integrator가 별도 구성한다.
기존 데모의 항상 성공하는 boot health check도 상속하지 않는다.
앱 인증서, registry 인증, Secure Boot 서명 및 OTA health 정책은 제품 설정 항목이다.

생성된 디스크는 기존 launcher로 native UKI를 보존해 부팅한다.
qcow2라면 먼저 raw로 변환한다.

```sh
qemu-img convert -f qcow2 -O raw automotive.qcow2 automotive.raw
./run_qemu_linux.sh --native-autosd-disk automotive.raw \
  --ukiboot-dir build/tmp_baremetal/deploy/images/apollo-qvp \
  --headless --out-dir build/autosd/automotive-native
```

## 기존 private guest 위 검증

`install-private-guest.py`는 앞서 검증한 regular minimal_qm + BlueChi/Podman
게스트의 disposable copy에서만 실행한다. OSTree 배포 설치 절차가 아니다.
4 CPU, AArch64, Enforcing, 필수 RPM, QM rootfs 경로를 먼저 확인한다.
이 스크립트는 QM을 중지하고 layer를 설치한 뒤 root/QM 이미지를 적재한다.

```sh
python3 /root/automotive-layer/install-private-guest.py
bash /root/check-automotive.sh
# ADAS 데모를 의도적으로 정지하는 fault injection:
bash /root/fault-automotive.sh
```

check/fault script 원본은 이 디렉터리에 있으며 별도 업로드한다.
BlueChi로 native QM 앱을 제어하려면 다음을 사용한다.

```sh
bluechictl stop qm.host apollo-qm-app.service
bluechictl start qm.host apollo-qm-app.service
bluechictl status host apollo-adas.service
```

실제 앱으로 교체할 때 ADAS image/Exec/health 명령과 QM binary 또는 container
image를 변경한다. 배포용 컨테이너는 검증한 digest로 고정하고 서명 검증을 추가한다.
현재 `localhost/apollo-workload:1`은 해당 bundle에서 직접 빌드한 데모 이미지다.

검증 결과와 제한은 [한글 리포트](../../doc/autosd-customization-layer-ko.md)에 기록한다.

정상 기동, BlueChi 제어, QM container 자동 복구, ADAS fault/latch 및 운영자
복구를 순서대로 시연하려면 [전체 데모 실행 가이드](../../doc/autosd-automotive-demo-guide-ko.md)를
따른다. `demo-guest.py`는 disposable guest에서만 실행하며 시나리오별 로그와
JSON 결과를 보존하고 첫 실패에서 중단한다.
[데모 검증 리포트](../../doc/autosd-automotive-demo-validation-ko.md)에서 실제 결과와
준비 상태 검사 시 발생한 초기 실패를 확인할 수 있다.

신규 AIB 이미지의 BSP/RPM/OCI/QCOW2 빌드, native UKI 부팅, S01–S07 실제 재수행과
가이드 수정 내용은 [Quick Guide 재검증 리포트](../../doc/autosd-quick-guide-revalidation-ko.md)에 기록했다.

PREEMPT_RT 사용·도구 구성·QM 부하 비교·latency 초과 검출은
[RT 실험 Quick Guide](../../doc/autosd-preempt-rt-guide-ko.md)를 따른다.
`prepare.py --rt-tools`는 진단용 RPM과 측정 도구를 추가하지만 RT 서비스를 자동 실행하거나
QM의 RT 제한을 해제하지 않는다. 기본 profile은 그대로 유지된다.
## 웹 시뮬레이션 콘솔

[웹 실행·모니터링 Quick Guide](../../doc/autosd-dashboard-guide-ko.md)에서 로컬 데모 실행,
guest CPU·서비스 모니터링, 로그 및 결과 확인 방법을 설명한다.
