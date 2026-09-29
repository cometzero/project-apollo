# AutoSD minimal_qm 재생성 및 부팅 검증 (2026-09-29)

## 범위

공식 minimal_qm manifest로 AutoSD 이미지를 생성하고, 기존 Apollo QVP BSP의
UKI/커널/모듈로 QEMU 및 QBox full-system 부팅을 확인한다. 추가로 Automotive
Safety Monitor, ADAS, QM app/container, BlueChi의 정상 상태를 확인한다.
전체 실행 절차는 [Quick Guide](autosd-minimal-qm-build-ko.md)를 따른다.

이미지 생성, QEMU 및 QBox full-system 기본 부팅과 Automotive 정상 상태 검사가
완료됐다. 검증 VM은 정상 종료했고 디스크와 로그는 보존했다.

## 입력 및 생성 결과

- 공식 manifest: `autosd/sig-docs/demos/minimal_qm/minimal_qm.aib.yml`
- sig-docs HEAD: `75cb479c89c8ee01350d03ca031a9b780158a99d`
- Apollo kernel: `6.18.5-rt3-yocto-preempt-rt`
- BSP: `build/tmp_baremetal/deploy/images/apollo-qvp/`
- AIB registry ARM64 digest:
  `0d8262623269223234a970eb3dca99e3d48f117ce9aa70b33fe234046f7a2287`
- AIB OCI replay digest:
  `a22f49f998489bab74bb42e98652a39183cbd1223d9a6211ba7ab09c5b510442`
- AIB config ID (두 형식 동일):
  `4ad126bc3428a7423faa833367b2a7ff12bc86dc472b2a0a4f43abdff32ea5b5`
- OCI archive SHA256:
  `c4f0f2cf6eac787d958f19c0ee3b72061ffebf1ef294ba3a82fc5981b14505a1`
- 생성 qcow2 guest SHA256:
  `a011b395332a0f85c3324725a4ffe3c0280c2823e73b7c44a33a82fc68cb9ec8`

RPM 저장소 snapshot까지 고정한 것은 아니므로 과거 이미지와 byte-identical한
결과를 주장하지 않는다. 이번에는 기존 matching BSP를 재사용했고 BitBake 전체를
다시 실행하지 않았다.

## 발견 및 수정한 문제

1. 이전 빌더 launcher가 삭제된 demo 디렉터리에 의존했다. 현재 nightly manifest와
   canonical QEMU provider를 이용해 독립 VM을 구성하도록 수정했다.
2. 기존 AIB digest와 새 digest가 registry에서 `manifest unknown`을 반환했다.
   이미 확보한 고정 digest를 재사용하고, 별도 OCI archive를 보관했다. 빈 guest
   저장소의 load 및 OCI digest 조회는 PASS이다. archive 전송 SHA도 검증한다.
3. 이전 nightly builder의 SELinux Enforcing 정책이 새로운 QM file context를
   거부하여 osbuild가 실패했다. disposable builder에서만 일시 Permissive로
   빌드하고 EXIT 시 Enforcing을 복원한다. 수정 후 osbuild/AIB 전체가 PASS이고
   빌더의 Enforcing 복원도 확인했다. 결과 이미지 정책은 완화하지 않는다.
4. 공식 minimal_qm에는 openssh-server와 tar가 없어 첫 자동 실행이 중단됐다.
   최초 UART 자동 로그인 후 SSH 및 필수 도구를 설치하도록 파이프라인을 수정했다.
   실패한 디스크는 정상 종료 후 보존했으며, 새 작업 디렉터리의 재실행은 수동
   콘솔 보완 없이 끝까지 PASS했다.

## 증거 위치

모든 경로는 workspace 기준이다.

- 최초 registry 실패: `build/autosd/minimal-qm-rebuild-20260929-aib/`
- SELinux 실패: `build/autosd/minimal-qm-rebuild-20260929-aib-retry/`
- 성공한 빌드: `build/autosd/minimal-qm-rebuild-20260929-aib-cached-retry/`
- 원본 builder UART: `build/autosd/minimal-qm-rebuild-20260929-builder/uart.log`
- 재사용 OCI archive: `build/autosd/minimal-qm-rebuild-20260929-builder-replay/`
- OCI 복원 확인: `build/autosd/minimal-qm-rebuild-20260929-builder-replay-export/`
- qcow2 및 manifest 회수: `build/autosd/minimal-qm-rebuild-20260929-fetch/`
- 첫 부팅 자동화 실패: `build/autosd/minimal-qm-rebuild-20260929-pipeline/`
- 성공한 전체 부팅 자동화: `build/autosd/minimal-qm-rebuild-20260929-pipeline-v2/`
- QBox 네 도메인 UART 및 receipt:
  `build/qbox-apollo-qvp/autosd-minimal-qm-rebuild-20260929-pipeline-v2/`

실제로 수행한 성공 파이프라인 명령:

```bash
./build_autosd_minimal_qm.sh \
  --image build/autosd/minimal-qm-rebuild-20260929-fetch/minimal_qm.aarch64.qcow2 \
  --work-dir build/autosd/minimal-qm-rebuild-20260929-pipeline-v2 \
  --customize --crun-binary build/autosd/crun-cgroup-fix/crun
```

AIB 생성과 회수는 앞선 builder helper 실행으로 수행하고, 통합 스크립트는
`--image`부터 실제 검증했다. `--builder-archive`의 빈 저장소 복원은 별도 실행으로
확인했다. archive에서 이미지 재생성까지 포함한 통합 단일 명령을 다시 반복한
것은 아니다.

## 검증 상태

| 항목 | 결과 |
|---|---|
| AIB 이미지 생성 | PASS |
| OCI archive 빈 저장소 복원 및 digest 확인 | PASS |
| 관련 회귀 테스트 | PASS: 755 tests, 기존 Paramiko deprecation warning 2건 |
| qcow2 회수·무결성 | PASS: guest/host SHA256 일치, qemu-img check 오류 없음 |
| QEMU UKI 및 QM 부팅 | PASS: EFI, matching kernel, slot 0 성공, Enforcing, QM PID namespace |
| Automotive 정상 상태 | PASS: QEMU/QBox 모두 HEALTHY, failures=0 |
| QBox full-system 네 도메인 및 QM 부팅 | PASS: RSE, SI CL0, SI CL1, AP, HIPC/PFDI 모듈 |
| 정상 종료와 기본 launcher 재사용 | PASS: POWERED_OFF, passed=true, poweroff_observed=true; 기본 선택 dry-run 확인 |

## 결과 사용

`build/autosd/demo-minimal-qm-prepared/regular.json`이 복원됐다. 데모 설치를 마친
검증 디스크는 QBox 출력 디렉터리의 `rootfs.wic`이다. `./run_qbox_autosd.sh
--dry-run`은 이 디스크를 `latest matching full-system PASS and normal poweroff`
정책으로 선택한다. 변환 직후 `regular.raw`에는 후속 guest 설치가 들어 있지 않다.

```bash
./run_qbox_autosd.sh
```

이번 full-system 실행은 headless 검증이다. 기본 tmux 화면은 선택 계획만 확인했고
GUI나 dashboard 자체의 실행 검증을 새로 수행하지는 않았다.

## 남은 경고와 한계

최종 QBox journal에는 SMMUv3 SID 범위, 비활성화된 PSCI cpuidle, initrd journal
socket, out-of-tree 모듈 taint, BlueChi heartbeat 비활성 설정 경고가 남아 있다.
이를 warning-free 부팅으로 표현하지 않는다. 이들은 이번 QM/Automotive 정상 상태
검사를 막지 않았다. 최종 QBox 로그에서는 `bootctl partition is invalid`와
`SELinux: mount invalid`가 검출되지 않았다.

최초 provisioning 전 QEMU journal의 모듈 누락·QM 재시작·cgroup2 경고는 보존했다.
matching 모듈 및 customization의 crun/부팅 정책을 적용한 후 QBox 부팅 결과와
혼동하지 않는다.

물리 하드웨어 timing parity, ASIL 인증, 전체 RT/OTA/IPC/watchdog fault injection
suite는 이번 기본 부팅 검증의 범위가 아니다.

## 후속: build/autosd 삭제 후 입력 재생성

이후 변경으로 `build/autosd`는 보존 필수 디렉터리가 아니다. 소스 설정은
`autosd/config/minimal-qm.json`, runtime recipe/patch는
`autosd/customization/runtime/`에 둔다. 이전 절의 날짜별 디렉터리는 과거 실행의
증거이며, 새 빌드가 반드시 읽어야 하는 입력이 아니다.

기존 결과를 삭제하는 대신 비어 있던 별도 캐시로 검증했다.

```bash
./build_autosd_minimal_qm.sh --prepare-inputs-only --minimal \
  --cache-dir build/autosd/cold-bootstrap-20260929
./build_autosd_minimal_qm.sh --prepare-inputs-only \
  --cache-dir build/autosd/cold-bootstrap-20260929
```

- 공식 nightly `2891630236.466d2e78` 다운로드 및 checksum 검증 PASS
- 새 guestfish/커널 다운로드·추출과 실제 appliance 파일시스템 인식 PASS
- 새 builder-base raw/initrd/manifest 변환 PASS
- 공식 ARM64 AIB OCI archive 다운로드·모든 blob hash 확인 PASS
- AIB 선택 digest:
  `caf6971b15185272b36be9c699427179220da1e953b7d2f02d57c84edbf0a46e`
- 별도 빈 디렉터리의 crun 소스 재빌드와 ARM64 `--version`/`ldd` PASS
  (`build/autosd/crun-disposable-validation-20260929-v2/`)
- 통합 Automotive 입력 준비 PASS: cold cache의 `inputs.json`과
  `crun/provenance.json`에 기록했다. 새 CentOS 기반 crun SHA256은
  `c3eb4a725c22f4a312195f84aa3b1fe280dac55cb456f5532f17c333fd8c40a0`이다.
- 후속 관련 회귀 테스트: 788 PASS, 기존 Paramiko deprecation warning 2건.

추가로 이전 CentOS crun 빌더 digest가 Docker cache에만 남아 있음을 발견했다.
기본 `stream10`의 ARM64 digest를 registry에서 조회한 뒤 반드시 pull하도록 수정했다.
새 digest `5d752d7ae898d223954e748601bca4b434a59b5eb625cf1e9b1b7e908257fa0c`의
새 layer 다운로드를 확인했다. 이전 crun은 `crun-before-base-fix/`로 보존했다.

이번 후속 검증은 입력 재생성 경로에 집중했다. 새로 내려받은 nightly/AIB로
최종 OS 전체를 다시 빌드하고 QEMU/QBox를 재부팅한 것은 아니며, 앞 절의
기존 이미지 부팅 PASS와 구분한다. 기존 VM·결과를 삭제하거나 재시작하지 않았다.
