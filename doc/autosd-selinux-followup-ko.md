# AutoSD custom SELinux policy 후속 검증

## 현재 결과

- **PASS — 정책 생성/컴파일/noarch RPM 패키징**: 공식 `custom_selinux_policy`
  demo의 schema 2.0.0 설정을 수정하지 않고 selcraft 0.3.1로 빌드했다.
- **준비 완료 — runtime payload 및 허용/거부 검사**: Apollo ARM64 실행 파일,
  공식 unit/drop-in, RPM, 설치/검증 helper를 묶었다.
- **FAIL — 공식 생성 정책 그대로의 live-install runtime**: shm 디렉터리가
  `user_tmp_t`로 남아 허용 대상 root server의 공유 메모리 생성이 실패했다.
- **부분 확인 — 좁은 label 보정 시험**: `/dev/shm/qm`만 `chcon`한 시험에서는
  실제 30회 전송이 성공했다. 다만 거부 대상 QM 프로그램은 IPC가 아닌 기본
  `/dev/null`/rootfs 탐색에서도 실패해 의도한 IPC 격리 증명은 아직 부족하다.
- **QEMU strict runtime PASS — 로컬 1.0.1 정책**: 4개 비허용 domain 모두 실제
  IPC 디렉터리 `shared_uds_uds_t` 접근이 Enforcing에서 거부됐고, 허용 domain
  조합은 30회 공유 메모리 전송에 성공했다. 공식 무수정 정책 PASS와 구분한다.
- **QBox strict runtime PASS — 로컬 1.0.1 정책**: 별도 QBox 실행에서도 4개
  IPC 접근 거부와 30회 허용 전송을 확인했다. QEMU 결과에서 추정한 것이 아니다.

## QEMU 최종 runtime 증거

2026-09-22, `custom-policy-selinux-1.0.1-1.el10.noarch` 설치 후 strict matrix를
실행했다. `demo-qm-policy-v101-matrix/result.json`의 returncode는 0, 소요 시간은
62.30초다. 종료 후 별도 확인에서도 SELinux가 Enforcing이었다.

- `root_server_other_t`, `qm_qm_server_t`, `root_client_t`,
  `qm_qm_client_other_t` 각각의 AVC가 `name="nshm_demo"`,
  `tcontext=system_u:object_r:shared_uds_uds_t:s0`, `tclass=dir`,
  `{ search }`, `permissive=0`를 기록했다. 일반 `qm_file_t` 접근 실패를
  IPC 거부로 대신 인정하지 않았다.
- 허용 프로세스의 실제 context는 `system_u:system_r:root_server_t:s0`,
  `system_u:system_r:qm_qm_client_t:s0`였다.
- 회수한 `root-transfer.log`에서 `Read command received` 30개와
  `Shared memory content:` 30개를 다시 집계했다. 허용 domain의 AVC는 없었다.
- 설치 로그에서 `/dev/shm/qm`은 `named_shm_shm_t`, `/run/nshm_demo`는
  `shared_uds_uds_t`로 확인했다.

증거 경로:

- 설치: `build/autosd/demo-qm-policy-v101-install/console.log`
- 검사: `build/autosd/demo-qm-policy-v101-matrix/{console.log,result.json}`
- 선별 AVC/Enforcing: `build/autosd/demo-qm-policy-v101-evidence/console.log`
- 전체 회수: `build/autosd/demo-qm-policy-v101-evidence/guest-evidence.tar.gz`
- 회수 tar SHA256: `36c0a1cb1b2dff9ff800675730961d43aa6c6cfd0fe24f3d0bd4b10b4869ed71`

이 검사는 해당 실행 파일/domain 및 UDS·공유 메모리 조합의 기능적 접근 제어를
검증한다. 시스템 전체 격리, 보안 인증, timing 보장, 원본 공식 이미지 전체
테스트 또는 QBox 결과로 확대하지 않는다. 네 비허용 앱은 UDS 디렉터리에서
차단되므로 각 앱의 공유 메모리 직접 접근까지 별도로 시도한 것은 아니다.

## QBox 최종 runtime 증거

`build/autosd/demo-qm-followup-qbox-recheck-2/result.json`의 전체 follow-up 명령은
returncode 0으로 완료했다. 331.53초는 여러 데모를 포함한 전체 명령 시간이며,
SELinux 매트릭스만의 소요 시간은 아니다. 같은 디렉터리의 `console.log`에는
4개 `DENY_PASS`, 실제 두 허용 domain, `CUSTOM_SELINUX_MATRIX_PASS`와 전후
Enforcing 상태가 남아 있다.

회수한 정책 로그를 별도로 확인한 결과:

- `root_server_other_t`, `qm_qm_server_t`, `root_client_t`,
  `qm_qm_client_other_t` 모두 `nshm_demo` 디렉터리에 대해
  `tcontext=system_u:object_r:shared_uds_uds_t:s0`, `{ search }`,
  `tclass=dir`, `permissive=0`인 AVC를 기록했다.
- 실제 허용 context는 `root_server_t`, `qm_qm_client_t`였으며 해당 domain의
  AVC는 없었다.
- `root-transfer.log`를 다시 집계해 요청 30개 및 공유 메모리 내용 30개를
  확인했다. 프로그램 실패만으로 DENY를 인정하거나 서비스 기동만으로 ALLOW를
  인정한 결과가 아니다.

첫 회수 파일 `demo-qm-followup-qbox-coldboot-check-ready/evidence.tar.gz`는
`gzip unexpected end of file`로 전체 무결성 검사에 실패했다. 실패 파일은
보존하고 최종 증거로 사용하지 않았다. 이후 QBox 정상 종료를 확인한 뒤
`demo-qm-followup-qbox-coldboot/rootfs.wic`을 guestfish의 `--ro`와
`/dev/sda5:/:ro`로 열어 아래 두 디렉터리를 직접 회수했다. VM 재실행이나
guest 파일 변경은 하지 않았다.

- 복구 디렉터리: `build/autosd/demo-qm-followup-qbox-recovered-evidence/`
- 정책: `apollo-followup-recheck.eIAZ4Q/policy/` 아래의 AVC/domain/전송 로그
- 함께 회수한 자료: `apollo-followup-recheck.eIAZ4Q/iceoryx/`,
  `apollo-qm-ipc.WE6fOi/`
- 정상 재포장: `build/autosd/demo-qm-followup-qbox-recovered-evidence.tar.gz`
- SHA256: `51a44e007390384baf686ea021612ba86d8910c8074e7ce824411e0a6bf157f0`
- 무결성: `gzip -t` 및 tar 전체 목록 검사가 모두 성공했다.

QBox의 이 판정도 해당 domain/resource 매트릭스의 기능적 접근 제어 PASS다.
시스템 전체 격리, 실시간성, 보안 인증 또는 원본 무수정 정책의 PASS는 아니다.

## 근거와 빌드

읽은 공식 자료:

- `autosd/sig-docs/docs/building/con_selinux-policies.md`
- `autosd/sig-docs/docs/building/proc_creating-custom-selinux-policies.md`
- `autosd/sig-docs/demos/custom_selinux_policy/{run-test.sh,custom_selinux_policy.aib.yml}`
- 같은 demo의 `selinux/conf.selcraft.yaml`, Containerfile, C 소스와 systemd unit

문서 본문에는 schema 1.0 예시도 있지만 실제 demo는 schema 2.0.0을 사용한다.
실제 demo 파일을 기준으로 했다. `server.c`, `client.c`, `common.h`는 기존
`shared_memory_qm_root` demo와 `cmp`로 동일함을 확인하여 이미 빌드한 정적
AArch64 `shm-server`, `shm-client`를 재사용했다.

호스트 x86_64 Docker의 기존 amd64 AIB image에 필요한 빌드 패키지를 컨테이너
내에서만 설치했다. 정책은 noarch이므로 ARM64 VM에서 빌드할 필요가 없었다.
호스트 전역 패키지/binfmt/daemon 설정, 기존 VM, upstream 소스를 변경하지 않았다.
컨테이너는 `--rm`으로 종료했고 writable mount는 작업 출력 디렉터리에 한정했다.

```sh
bash scripts/autosd_demo/selinux_build.sh
bash scripts/autosd_demo/selinux_payload.sh
```

- 빌드 로그: `build/autosd/demo-selinux-followup/policy-build.log`
- 생성 소스: `build/autosd/demo-selinux-followup/policy/`
- RPM: `policy/rpmbuild/RPMS/noarch/custom-policy-selinux-1.0.0-1.el10.noarch.rpm`
- RPM SHA256: `fad3922bf53771c1f0bab811afc1d6cbe2b7047bf3a9898633f59416795f502e`
- payload: `build/autosd/demo-selinux-followup/selinux-demo.tar.gz`
- payload SHA256: `09e6eb3437327b48c95c165b4b2ca5bac5fee8b648852b54d6ab6d90776b6822`
- RPM 요구 조건: `qm`, `policycoreutils`, SELinux policy/base/any >= 42.1.27

## runtime 적용과 판정

다른 QM 데모가 끝난 후 disposable regular 이미지의 `/root/selinux-demo-v1.0.1`에
**보정된 1.0.1 payload**를 풀고 다음 순서로 실행한다. 원본 1.0.0 payload는 실패
재현 자료로 보존한다. 설치 과정에서 QM이 재시작된다.

```sh
bash /root/selinux-demo-v1.0.1/selinux_guest_install.sh /root/selinux-demo-v1.0.1
bash /root/selinux-demo-v1.0.1/selinux_guest_check.sh /root/selinux-demo-v1.0.1/evidence
```

설치 helper는 실행 중 QM의 Rootfs 및 `/etc` bind source가 각각
`/usr/lib/qm/rootfs`, `/etc/qm`인지 확인한다. 서로 다른 기존 binary/unit을
덮어쓰지 않고 거부한다. `/etc/qm`의 다른 drop-in/BlueChi 설정은 변경하지 않는다.
SELinux를 permissive로 바꾸거나 전체 `/dev/shm`를 relabel하지 않는다.

| 실행 위치/프로그램 | 실제 요구 domain | 기대 결과 |
|---|---|---|
| root server-other | `root_server_other_t` | DENY, failed 및 새 AVC `permissive=0` |
| QM server | `qm_qm_server_t` | DENY, failed 및 새 AVC `permissive=0` |
| root client | `root_client_t` | DENY, failed 및 새 AVC `permissive=0` |
| QM client-other | `qm_qm_client_other_t` | DENY, failed 및 새 AVC `permissive=0` |
| root server → QM client | `root_server_t` → `qm_qm_client_t` | ALLOW, 30회 UDS 요청 및 공유 메모리 내용 수신 |

검증 helper는 새로운 journal cursor/audit 파일 offset 이후 기록만 판정한다.
허용 실행에서는 `/proc/PID/attr/current`로 실제 domain을 확인하고, 성공한
서비스 시작만으로 통과시키지 않는다. 30개 `Read command received`와
`Shared memory content:` 로그, 정상 종료, 허용 domain의 AVC 부재를 요구한다.
거부 실행은 단순 프로그램 실패가 아니라 해당 domain의 실제 Enforcing AVC를
요구한다. 증거는 위 명령의 guest `/root/selinux-demo-v1.0.1/evidence/`에 남는다.

## 주의 사항

원본 selcraft 0.3.1이 생성한 file-context는 입력 `/dev/shm/qm`보다 넓은
`/dev/shm(/.*)?`를 `named_shm_shm_t`로 매핑한다. 공식 생성물을 임의 수정하지
않았으며 helper는 `/dev/shm/qm`에만 `restorecon`을 적용한다. 이 정책을 설치한
VM에서 다른 서비스의 전체 shm relabel을 실행하면 영향을 줄 수 있다. 따라서
공유 QM 작업과 순차 실행하고, 검증 후 다른 시나리오로 넘어갈 때는 테스트
서비스를 중지하고 해당 RPM 제거 또는 깨끗한 private image 사용이 필요하다.

공식 `run-test.sh`의 AVC 부재 검사에는 실패를 뒤의 `|| true`가 상쇄할 수 있는
구문이 있어 그대로 재사용하지 않았다. helper는 허용 domain의 AVC가 하나라도
있으면 실패하도록 했다. 이것은 공식 정책의 내용을 바꾸는 것이 아니라 검증
조건을 엄격하게 적용한 것이다.

## 실제 실패 원인 및 로컬 1.0.1 보정

근거: `build/autosd/demo-qm-policy-diagnose/console.log`,
`build/autosd/demo-qm-policy-contexts/console.log`.

1. AutoSD 기본 context에는 `/dev/shm/.* <<none>>`가 있다. 생성된 정책의
   `/dev/shm(/.*)?`보다 이 규칙이 우선되어 `/dev/shm/qm`의 `matchpathcon`은
   `<<none>>`가 됐다. live `systemd-tmpfiles`로 생성된 디렉터리의 `user_tmp_t`
   label은 `restorecon`으로 바뀌지 않았다. 이는 본 live-install 환경에서 확인한
   실패다. 다른 domain으로 실행되는 공식 이미지의 초기 boot tmpfiles까지
   동일하게 실패한다고 확대 해석하지 않는다.
2. 원본 generated `.te`의 QM 기본 접근 허용 일부가 IPC READ 권한 생성 루프
   안에 있다. 따라서 의도적으로 IPC 권한이 없는 `qm_qm_server_t`,
   `qm_qm_client_other_t`에는 `/dev/null` read와 QM rootfs 탐색 등이 없다.
   실제 AVC의 `qm_file_t`는 정상 QM 파일 label이며, 부모의 `restorecon`이
   잘못된 label을 만들었다고 볼 근거는 없다.

별도 `policy-v1.0.1`은 다음만 바꾼다.

- file-context를 `/dev/shm/qm(/.*)?`로 좁혀 기본 `<<none>>`보다 구체적으로
  지정한다. `/dev/shm` 전체 relabel 또는 `user_tmp_t`에 대한 접근 허용은 없다.
- 두 거부 대상 QM domain에 `qm_file_t:dir search`,
  `qm_file_t:chr_file read`만 추가한다. QM 관리 domain의 해당 process proc-dir
  탐색을 위해 `qm_t → 해당 domain:dir search`도 추가한다.
- 두 domain에 `shared_uds_uds_t` 또는 `named_shm_shm_t` 접근 권한은 추가하지
  않는다. audit2allow 자동 생성이나 permissive 전환을 사용하지 않는다.

재현: `scripts/autosd_demo/selinux_adjusted_build.sh`,
`scripts/autosd_demo/selinux_adjusted_payload.sh`. 원본 `policy/`, 원본 RPM과
payload/evidence는 보존하고 버전별 디렉터리·tar를 사용한다.

- 로컬 RPM SHA256: `154bef48bcefc4b3058cce084ebefe2f6b32603751dbd6941aae2cc984da9ac2`
- 새 payload: `build/autosd/demo-selinux-followup/selinux-demo-v1.0.1.tar.gz`
- 새 payload SHA256: `64bb91c6ef6650c0e624e68905b3fd71dcbdc5564a63b88b3f11f03be18fb39f`
- 빌드 로그: `build/autosd/demo-selinux-followup/policy-v1.0.1-build.log`

새 payload는 `/root/selinux-demo-v1.0.1`처럼 다른 디렉터리에 풀어 원본 증거를
보존한다. QM이 실행 중인 상태에서 새 설치 helper에 해당 디렉터리를 인자로
주어 RPM을 upgrade한 뒤, 새 evidence 디렉터리를 지정하여 strict 검사를 실행한다.

검증 helper의 DENY 조건도 강화했다. 이제 domain 실패만 보지 않고 새 AVC의
`tcontext`가 `shared_uds_uds_t` 또는 `named_shm_shm_t`인 경우에만 IPC 거부로
판정한다. 실제 실패 로그를 fixture로 사용해 root `server-other`의 IPC 거부는
인정하고 QM server의 `qm_file_t` 거부는 인정하지 않는 것을 확인했다.
`/proc/PID/attr/current`의 NUL도 제거하여 실제 context 문자열을 증거에 남긴다.
