# Apollo AutoSD 잔여 데모 후속 검증

검증 시작: 2026-09-22 KST. 이전 결과는 [기본 데모 리포트](autosd-demo-validation-ko.md)를 참고한다.

## 범위와 판정 원칙

QM 내부 컨테이너·CPU affinity·root↔QM IPC, SELinux 허용/거부,
BlueChi root↔QM, iceoryx2, 실제 bootc 업데이트·자동 rollback을 검증한다.
QEMU에서 먼저 수행하고 완료한 실행 경로를 QBox AP-only 프로파일에서 교차 확인한다.
이미지 빌드·로그인·프로세스 존재만으로 통신이나 rollback 성공을 선언하지 않는다.

## 입력 및 보존

- 커널: 이전 검증의 `6.18.5-rt3-yocto-preempt-rt` 및 matching modules.
- QM 기반: 공식 minimal_qm AIB 산출물을 적용한 private disk.
  `demo-minimal-qm-runtime`의 prepared disk를 재사용하며 원본 qcow2/nightly는 변경하지 않는다.
- QEMU 증거: `build/autosd/demo-qm-followup-session/` 및 시나리오별 디렉터리.
- ARM64 AIB builder: 기존 private root/scratch 재사용, SSH 2226.
- QM 시험 게스트 SSH 2224, QBox 2227, OTA 대상은 별도 포트를 사용한다.
- 호스트 패키지·binfmt·공유 Yocto 입력을 변경하지 않는다. 추가 source checkout은 `autosd/` 아래에 둔다.
- 시작 시 host 여유 공간 약 33 GiB. 이미지와 cache 증가량을 감시한다.

## 현재 진행 상태

- BlueChi root↔QM: **PASS**, 두 노드 online 및 QM 서비스 start/stop 확인.
- nested container·UDS IPC·affinity: **PASS**, root/QM 실제 왕복 및 CPU 0 확인.
- SELinux custom policy: 보정 1.0.1의 엄격한 4 DENY/30-message ALLOW **PASS**.
- iceoryx2: ARM64 빌드 및 실제 root↔QM 송수신 **PASS** (아래 SELinux 조건 구분).
- QBox regular/OSTree EFI 최초 부팅: **PASS**, 유효한 bootctl 및 slot A 성공 기록.
- OTA: base OCI 생성 완료. 변환용 builder 부재로 전체 명령은 FAIL;
  보존된 OCI를 이용해 helper 준비 및 디스크 변환을 계속 진행 중.

## 중요 구현 차이

minimal_qm rootfs에는 DNF·RPM 실행 파일이 없다. QM을 정지한 뒤 root 측
DNF의 `--installroot`로 BlueChi agent를 설치하고 Podman 의존성을 확인하며, `/etc/qm` 등 별도
bind 경로의 설정을 적용한다. 런타임 설치는 해당 패키지가 처음부터 포함된
AIB 이미지 빌드 검증과 구분한다.

## BlueChi root↔QM

공식 controller/agent 설정과 test.service를 적용했다. Enforcing에서 host와
qm.host가 모두 online이 됐고, `bluechictl start/stop qm.host test.service`에 따른
active→inactive 상태 전이를 QM 내부 systemd에서도 확인했다.
프로세스 도메인은 `bluechi_t`, `bluechi_agent_t`, `qm_bluechi_agent_t`였다.
증거: `build/autosd/demo-qm-bluechi-setup-retry/`.

최초 실행은 QM 재시작 직후 내부 systemd bus 준비 전에 접근해 실패했다.
재현 helper에 bounded readiness 대기를 추가한 후 재검사했다. 최초 실패 로그는
`demo-qm-bluechi-setup/`에 보존했다. RPM 설치 중 `/proc` 미마운트 경고가 있었으나
패키지 설치와 이후 systemd 기반 실제 실행은 완료했다.

## nested container·UDS·CPU affinity

공식 UDS server/client C 소스를 변경 없이 정적 ARM64 빌드한 payload를 작은
scratch OCI 이미지에 담았다. 공식 CentOS 기반 Containerfile 빌드와는 구분한다.
root Podman의 server와 QM 내부 Podman의 client 사이에 `/run/ipc`를 공유했다.

- 실제 server 수신 및 client 응답 로그 확인.
- 프로세스 domain: `ipc_t` 및 `qm_container_ipc_t`, SELinux Enforcing.
- client의 `/proc/PID/status`에서 `Cpus_allowed_list: 0` 확인.
- nested Podman은 cgroup v2, systemd manager, overlay, seccomp/SELinux enabled.
- 증거: `demo-qm-nested-ipc-retry/`, **PASS (113.66초, tar 설치 포함)**.
- 최초 실행은 tar 도구 누락으로 실패했다. private guest에 설치하고 재검사했다.

이는 CPU affinity 검사이며 부하 경쟁 시 CPU share 비율·지연·시간 격리 검증은 아니다.

추가로 `CPUWeight=50`을 runtime 설정하고 systemd 및 실제 cgroup v2의
`cpu.weight=50`, `cpu.idle=0`을 확인한 뒤 원래 값을 복구했다.
증거: `demo-qm-iceoryx-setup/`. 상대 스케줄링 가중치이며 전체 CPU의 50% quota를
설정하거나 실제 경합하 처리량 비율을 측정한 결과는 아니다.

## Custom SELinux 정책

공식 schema 2.0 설정과 selcraft 0.3.1의 원본 정책은 live-install 환경에서 FAIL했다.
기본 `/dev/shm/.* <<none>>`와 생성 context가 충돌했고, 일부 negative QM domain은
IPC 이전의 기본 파일 접근에서 실패했다. 원본 정책과 실패 로그를 보존했다.

별도 1.0.1 후보는 shm 경로를 `/dev/shm/qm(/.*)?`로 좁히고 두 negative domain에
기본 실행용 권한만 추가했다. IPC 접근 권한은 추가하지 않았다.
**엄격한 매트릭스 PASS (62.30초)**:

- `root_server_other_t`, `qm_qm_server_t`, `root_client_t`, `qm_qm_client_other_t`
  모두 `shared_uds_uds_t` 디렉터리 search에서 실제 Enforcing AVC로 거부됨.
- `root_server_t → qm_qm_client_t`는 요청·공유 메모리 내용 각각 30회, 정상 종료,
  허용 domain의 AVC 없음 확인.
- 증거: `demo-qm-policy-v101-matrix/`, `demo-qm-policy-v101-evidence/guest-evidence.tar.gz`.

네 negative 앱의 직접 shm 접근까지 각각 따로 검증한 것은 아니다.
공식 AIB fresh-boot 자체가 같은 원인으로 실패한다고 확대하지 않는다.
상세: [SELinux 부분 리포트](autosd-selinux-followup-ko.md).

iceoryx2는 공식 pinned source의 Cargo 예제를 cross-build했다. 공식 Bazel RPM
생성 전체를 재현한 것은 아니다. 세부 provenance는
[iceoryx2 부분 리포트](autosd-iceoryx-followup-ko.md)에 기록한다.

## iceoryx2 실제 송수신

| 조건 | 결과 | 증거 (`build/autosd/` 기준) |
|---|---|---|
| 기본 user_tmp_t, Enforcing | FAIL: qm_t subscriber의 open/write AVC | `demo-qm-iceoryx-enforcing/`, `demo-qm-iceoryx-diagnose/` |
| 공식 예제와 같은 permissive 비교 | PASS: 실제 송수신, 종료 후 Enforcing 복구 | `demo-qm-iceoryx-permissive/` |
| 공유 경로만 qm_file_t, Enforcing | PASS: 실제 송수신 및 fresh kernel journal AVC 없음 | `demo-qm-iceoryx-label-trial/` |

마지막 시험에서는 새 node/data/service 파일의 실제 qm_file_t 라벨을 확인했다.
`iceoryx_guest_setup.sh PAYLOAD --qm-shared-label`로 좁은 경로에만 opt-in 적용한다.
정책 allow rule을 추가하지 않았지만 QM 기본 도메인의 기존 파일 접근 권한을
이용하므로 앱별 최소권한 정책·보안 격리 인증과는 다르다. `/tmp`는 volatile이므로
재부팅 후 setup을 다시 실행해야 하며, 이번 시험만으로 자동 라벨 지속성을 주장하지 않는다.

## QBox 교차 검사

초기 cold boot에서 `/run/ipc`, `/tmp/iceoryx2`가 없어 QM bind mount가 실패했다.
QEMU의 live setup에서는 존재하던 휘발성 디렉터리들이었다.
`qm_shared_paths.conf` 및 helper의 `/etc/tmpfiles.d/apollo-qm-shared-paths.conf`
설치로 부팅 시 디렉터리를 재생성하도록 수정했다. 경로 생성과 iceoryx2의 opt-in
라벨 지정은 별개다. 최초 실패 증거는 `demo-qm-followup-qbox-bluechi-diagnose/`에 보존한다.
수정 후 `demo-qm-followup-qbox-recheck-2/`에서 전체 재검사가 통과했다.
BlueChi start/stop, nested UDS 및 CPU 0 affinity, CPUWeight readback,
SELinux 4 DENY/30-message ALLOW, Enforcing iceoryx2 실제 14회 수신을 확인했다.
이 디스크를 다시 cold boot한 `demo-qm-followup-qbox-coldboot/`에서도
수동 생성 없이 공유 디렉터리 생성, QM active 및 BlueChi 두 노드 online을
확인했다. `demo-qm-followup-qbox-coldboot-check-ready/`의 SSH 검사 결과는 PASS다.
단, SSH로 종료하여 launcher의 serial login 판정은 FAIL(`login_observed=false`)이며
이를 launcher PASS로 바꾸지 않았다. 초기 SSH 준비 전 접근 실패도 보존했다.
회수한 archive는 최초 생성 중 조기 종료되어 무결성 FAIL이므로 상세 증거로
사용하지 않는다. 정상 종료한 디스크에서 guestfish read-only로 원본 로그를
다시 회수했다. 정상 archive는
`build/autosd/demo-qm-followup-qbox-recovered-evidence.tar.gz`이며 gzip 및
전체 tar 목록 검사가 통과했다.
SHA-256: `51a44e007390384baf686ea021612ba86d8910c8074e7ce824411e0a6bf157f0`.
iceoryx2 공유 경로의 앱 실행용 opt-in 라벨은 여전히 부팅 후 setup 대상이다.

## 도구 검사

launcher·이미지 준비·native 보존·guest 증거 수집·OTA health 판정 focused pytest 154개 통과,
신규 guest helper의 bash 문법 및 root diff whitespace 검사 통과.
실행 로그와 원본 이미지는 보존했다. 이후 사용자 요청으로 삭제한 중간 산출물은
아래 정리 기록과 archive를 참고한다.
추가로 AIB kernel release/simple/reproducible/boot logging 집중 검사 148개가
통과했다. 신규 QBox EFI 경로 독립 소스 검토와 63개 관련 시험에서도
구체적 결함은 발견되지 않았다. 이 검토는 별도 runtime 시험을 대신하지 않는다.
OTA helper 검토에서 발견한 다중 unit `is-active`의 ANY-success 문제는
각 unit 개별 판정으로 수정하고 세 가지 조합을 실행 시험했다.
기존 full-map 정적 validator도 PASS했다
(`build/qbox-apollo-qvp/full-map-validation.json`). 정적 reset 항목 통과는
이 문서에서 미구현으로 분리한 QBox EFI 전체 플랫폼 재부팅의 runtime 증거가 아니다.

## QBox EFI 최초 부팅

`run_qbox_linux.sh --autosd MANIFEST --uki UKI`를 추가해 SystemC loader로
U-Boot에 진입하고 기존 UKI/disk 준비 helper를 공유한다. direct Linux 경로는 유지한다.
regular minimal_qm 이미지로 **102.05초 PASS**:
U-Boot → UKIBoot slot A → EFI Linux → root login → CPU 4개 및 disk probe.
bootctl CRC/valid 정상, A `successful_boot=1`, `tries_remaining=0` 확인.
증거: `build/autosd/qbox-efi-first/result.json` 및 UART 로그.

OSTree nightly도 별도 private disk에서 **112.56초 PASS**:
EFI/slot A 성공, `/run/ostree-booted`, 실제 deployment 및 root overlay,
CPU 4개·disk probe를 확인했다. 증거: `build/autosd/qbox-efi-ostree-first/`.
두 시험 모두 종료됐고 원본 이미지와 성공 증거는 보존했다.

SystemC 전체 플랫폼 native guest reset은 구현하지 않았고,
`efi_reboot_support=NOT_IMPLEMENTED`로 명시한다. 최초 부팅 성공을 QBox OTA·
자동 rollback 또는 Secure Boot 성공으로 확대하지 않는다.
상세: [QBox EFI 리포트](autosd-qbox-efi-followup-ko.md).

## OTA용 native UKI 보존 경로

QEMU에 `--native-autosd-disk RAW`를 추가했다. 외부 kernel/initrd/BLS를 요구하지
않고 private copy의 원래 A/B UKI와 bootctl 전체 partition SHA를 전후 비교한다.
기본값은 ESP도 보존하며 `--ukiboot-dir`를 명시한 경우에만 ESP loader/addon을
교체한다. `--native-autosd-mode regular|ostree`는 userspace 검사 계약을 선택한다.
기존 `--autosd --uki`의 Yocto UKI 적용 동작은 유지했다.

기존 검증된 regular 디스크를 native 보존 경로로 재부팅하여 **47.64초 PASS**:
EFI·slot A 성공·bootctl CRC·CPU/disk smoke를 확인했다.
증거: `build/autosd/qemu-native-uki-regular-smoke/`.
완료된 동일 private disk를 `--reuse-autosd-disk`로 다시 부팅한 실행도
**48.08초 PASS** (`qemu-native-uki-regular-reuse/`). 슬롯·ESP 재작성 없이
기존 bootctl을 사용했다. 새 경로의 독립 소스 검토에서도 확정 결함은 없었다.
이는 native 보존 launcher 검증이며 새 AIB 이미지의 OTA 성공을 대신하지 않는다.

## 사용자 요청에 따른 이전 산출물 정리 (2026-09-23)

추가 삭제 요청에 따라 중복 QEMU 실험, 실패한 첫 builder topology,
v5로 대체된 kernel RPM v2~v4, 임시 UKI probe 등 20개 디렉터리를 삭제했다.
삭제 대상의 실제 할당량 합계는 38.04 GiB였다.
실행 중인 프로세스의 열린 파일 및 mount 여부를 먼저 확인했다.
원본 nightly, 최종 검증 이미지, 현재 OTA/builder/cache, host tools는 보존했다.

이전 경로의 로그·설정·결과 JSON은
`build/autosd/cleanup-20260923-evidence.tar.gz`로 보존하고 전체 무결성을 검사했다.
SHA-256: `ae9e4c9333b3b5c49ce60cdc95050dd298f49f2cb531a177686e56e7c76089ef`.
정확한 삭제 목록·파일 inventory는 같은 경로의 `cleanup-20260923-*`에 있다.
삭제한 대용량 디스크/중간 산출물은 이 archive로 복구할 수 없으며 재생성이 필요하다.
정리 전후 호스트 가용 공간은 약 23 → 70 GiB였다(동시 OTA 작업의 변화 포함).
