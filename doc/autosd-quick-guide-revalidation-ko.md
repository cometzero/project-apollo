# AutoSD Quick Guide 전체 재검증

실행일: 2026-09-26. 대상: [Quick Guide](autosd-automotive-demo-guide-ko.md).
새 AIB 이미지 경로 A를 실제로 재수행했다. BSP → kernel RPM → AIB OCI/QCOW2 →
native UKI 부팅 → S01–S07까지 통과했다. 기존 가이드는 그대로는 완전하지 않았고,
실행 중 확인한 저장소·접근·증거 수집 절차를 아래와 같이 수정했다.

## 완료된 단계

- Apollo QVP BSP 재빌드: **PASS**. 5,817 tasks 중 5,803 재사용, 나머지 성공.
  기존 forced-task taint warning 5개는 로그에 보존했다.
  `build/autosd/automotive-guide-bsp-build.log`.
- kernel RPM 신규 생성: **PASS**. 동일 입력으로 두 번 빌드한 SHA-256 일치.
  `build/autosd/automotive-demo-kernel-rpm/result.json`.
  RPM SHA-256: `429d8f902ce55d9cde79676f9118b293f840acdeae7bf77ac6d0431323d10884`.
- customization bundle 신규 생성 및 SSH 공개키 설정: schema **PASS**.
  `build/autosd/automotive-demo-bundle/`. 시험용 개인키는 이미지/소스에 포함하지 않는다.
- 관련 pytest: **18 PASS** (customization, guest_exec, builder resume).
- QEMU/UKI/디스크/OTA/prepare 도구 회귀 pytest: **123 PASS**. 실행 검증과는 별도다.
- 관련 전체 회귀 테스트 최종 재실행: **141 PASS**, 6.49초.
- 최종 가이드 shell 블록 25개 구문 검사, 로컬 Markdown 링크, `git diff --check`:
  **PASS**.
- native builder 재시작 및 기존 scratch 확인·mount: **PASS**.
  `build/autosd/automotive-guide-builder*`에 증거 보존.
- distro-matched AIB helper 재생성 및 storage 등록: **PASS**.
  helper OCI digest: `579715f3a8fc2ccd0a17ce1d08330a0c475c10e0f2ae983f0ea47d064ffcb79f`.
  이후 workload build가 시작돼 helper 명령 성공을 확인했다.
- scratch workload container build: **PASS**, image ID
  `703f6c26d1e65e840740e3b7679f31901f1b4bf5b4018fe05b0f830f088b1a38`.
- customization OS osbuild/OCI export: **PASS**.
  OCI digest: `b95076bc12810205f0338f69d4ab887e4e90ede09e4b479b572631d480514a43`.
  OSTree commit: `eb55214b0e1adec157160b43b4565cc8d8249e458dcc916dc17bed6837abb71c`.
  root/QM filesystem 및 embedded workload 구성, Apollo kernel RPM 설치,
  key-only SSH 설정 적용을 실제 osbuild 로그에서 확인했다.
- OCI 기반 QCOW2 변환 재시도: **PASS**, 명령 exit 0.
  `build/autosd/automotive-guide-convert/`.
  QCOW2 SHA-256: `81b33a1caddb05013d21f44d74af46256f76fe2cf31e85d7d38b323d9d5a8546`.
  `ukibootctl_init.bin` 기록, OSTree 설치 완료와 root/ESP unmount를 확인했다.
- 로컬 회수·QCOW2 검사·raw 변환: **PASS**. builder 정상 종료 후 scratch를
  읽기 전용 `debugfs dump`로 추출했고 builder/host SHA-256이 일치했다.
  `qemu-img check`는 오류 없음. SSH 전송은 느려 중단했으며 부분 파일/오류 결과는
  `automotive-guide-image-retrieval/`에 그대로 보존했다 (완성본으로 사용하지 않음).
- 신규 이미지 native UKI 부팅: **PASS**.
  `automotive-demo-run/linux-uart.log`, `automotive-guide-native-boot-check.log`.
  Yocto U-Boot/UKIBoot → native slot A → kernel `6.18.5-rt3-yocto-preempt-rt`,
  EFI 및 OSTree 표식, booted=active, slot A successful_boot=1을 확인했다.
  kernel cmdline에 ttyAMA0/PL011 earlycon 포함, UART 부팅 로그 출력.
  최초 `Uninitialized uki_bootctl partition, reseting to default`는 초기화 동작이며
  invalid partition 오류는 없었다. 시작 후 failed systemd unit은 0개다.
  첫 SSH 시도는 sshd 준비 전 banner timeout, 준비 후 key-only 접속 및 readiness 성공.
- 신규 이미지 S01–S06: **6/6 PASS**.
  `build/autosd/automotive-demo-archive-run/results.json` 및
  `automotive-demo-evidence.tar.gz`에 개별 로그·journal·해제 전 latch 상태 보존.
  관찰 시간: S01 20.174초, S02 30.053초, S03 38.499초,
  S04 32.730초, S05 13.035초, S06 34.681초 (TCG 관찰값, deadline 보장 아님).
- 신규 이미지 S07 cold boot: **PASS**.
  `build/autosd/automotive-guide-native-reboot-check.log`,
  `build/autosd/automotive-demo-reboot-run/`.
  첫 VM 종료 후 그 private disk의 새 copy로 native UKI 부팅했다. 추가 설치나
  수동 서비스 시작 없이 readiness/healthy 검사, EFI/OSTree, booted=active,
  slot A successful_boot=1, failed unit 0개를 확인했다.
- builder와 두 target 실행 모두 `systemctl poweroff` 후 UART `Power down` 및
  QEMU 종료를 확인했다. 최종 QEMU 프로세스 없음, SSH 2226/2232 listener 없음.
  target launcher의 exit 1은 아래 key-only console 판정 제한으로 별도 보존했다.

## 실행 중 확인한 가이드 보완

1. builder 재시작 도구가 기존 UART 파일 때문에 실패하므로 `--out`을 추가했다.
   기존 로그 보존 회귀 테스트를 추가했다.
2. 기존 native builder는 scratch를 자동 mount하지 않는다. LABEL/UUID 확인 후
   기존 filesystem mount 절차를 추가했다. 포맷이나 기존 산출물 삭제는 하지 않았다.
3. helper/container storage/osbuild cache 재사용 경로와 디스크 조건을 명시했다.
4. nightly 입력이 바뀌면 `build-builder --if-needed`도 재빌드함을 명시했다.
5. `yocto_build.sh`가 build/conf를 template에서 재생성한다는 주의를 추가했다.
6. key-only 이미지에서 launcher의 고정 password console-login 판정은 사용할 수
   없으므로 SSH 기반 EFI/OSTree/UKIBoot 검사를 분리해 안내했다.
7. 24 GiB scratch는 OCI export까지 성공했으나 disk 변환 중 99%/273 MiB 여유가
   되어 변환을 의도적으로 중단했다 (`INTERRUPTED_FOR_CAPACITY`, 원래 명령 exit 137).
   Podman stop은 SIGKILL 전환 후 timeout 오류를 냈으나 이후 실행 컨테이너 부재와
   builder의 filesystem detach/Power down/QEMU exit 0을 확인했다. 기존 OCI/cache는
   삭제하지 않았다. scratch raw를 오프라인으로 40 GiB까지 확장하고, 재부팅 후
   UUID 확인·기존 ext4 온라인 확장에 성공했다 (여유 16 GiB).
   `automotive-guide-capacity-stop/`, `automotive-guide-before-expand/`,
   `automotive-guide-resize/`에 증거를 보존했다.
   OCI archive SHA-256: `4384166462b41bb1901eca0af66adb337525fa26fed6306cb6e88d0ae5b67a67`.
   가이드에 디스크 확장 및 OCI 기반 변환만 재시도하는 절차를 추가했다.
8. 새 OS에 `tar` 실행 파일이 없어 기존 archive 명령이 exit 127로 실패했다.
   guest archive 명령을 이미 설치된 Python 표준 `tarfile`로 변경했다.
   수정 명령으로 archive 생성·회수·host 목록 검사에 성공했다. OS package 추가나
   이미지 재빌드 없이 가이드 명령만 수정했다.

## 판정 경계와 남은 제한

- **PASS**: 신규 이미지의 위 빌드·부팅·데모·cold boot 기능. 이전 regular 이미지의
  PASS를 대신 인용하지 않았다. 이번에는 A 경로를 재실행했으며 B/B-설치의 기존
  검증 기록은 유지했다. builder 입력 전송에는 private SSH helper를 사용했고,
  최종 회수에는 가이드에 추가한 로컬 offline 절차를 사용했다.
- **UNSUPPORTED**: key-only 이미지에 대한 launcher 자동 console-login 판정.
  `automotive-demo-run/result.json`의 `status=FAIL`, `login_observed=false`,
  `efi_boot_observed=false`, `ukiboot_service=NOT_OBSERVED`는 그대로 보존했다.
  이 판정을 PASS로 고치지 않았으며 SSH의 실제 EFI/OSTree/bootctl 증거로
  부팅 기능을 별도 판정했다. launcher 종료 코드 1을 무조건 무시하면 안 된다.
- **관찰 경고**: UART에 cgroup2 SELinux mount 경고와 EFI handle 메시지가 있다.
  서비스 검사 시 Enforcing과 모든 workload 정상 실행은 확인했으나 전체 AVC
  무결점 보장을 의미하지 않는다. 종료 중 `/dev/loop0` busy/해제 실패 경고가
  있었으므로 완전한 loop teardown PASS는 아니다. Power down과 cold boot 결과는
  이 경고와 구분한다.
- **미검증**: QBox, OTA rollback/update, Secure Boot 신뢰 체인, 실제 ADAS 알고리즘,
  ASIL-B 인증/FFI/WCET/FTTI. boot-success 표시는 제품 안전 정책 검증을 대체하지 않는다.
- kernel/BSP metadata는 이번 가이드 검증에서 변경하지 않았다. 코드 변경은 builder
  `--out` 및 기존 로그 보존 테스트이며, 나머지는 문서/생성된 시험 산출물이다.

## 최종 산출물과 재실행

- 새 QCOW2: `build/autosd/automotive-demo-bundle/automotive.qcow2`.
- 부팅 원본 raw: `build/autosd/automotive-demo-bundle/automotive.raw`.
- 시험 후 디스크: `build/autosd/automotive-demo-run/rootfs.wic`,
  `build/autosd/automotive-demo-reboot-run/rootfs.wic` (현재 모두 종료 상태).
- 시험 private key: `build/autosd/automotive-demo-key` (host 전용, mode 0600).
  이미지에는 공개키만 포함했다. key 및 VM 디스크를 공개 배포하지 않는다.
- 재실행은 Quick Guide A의 3.3 이후를 따르되 `--out-dir`과 guest evidence 경로에
  새 이름을 사용한다. 원본 raw에서 시작하면 첫 부팅 초기화부터 다시 수행한다.
- OCI/cache/부분 전송 파일/실패 로그를 삭제하지 않았다. 최종 host 여유 공간은
  약 30 GiB이며 다음 전체 재빌드 전에는 공간을 다시 확인해야 한다.
- 커밋·push 및 관련 없는 worktree 변경은 수행하지 않았다.
