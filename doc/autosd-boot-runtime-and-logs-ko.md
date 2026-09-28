# AutoSD 부팅 런타임 및 로그 세션 변경

## 증상과 원인

- `podman0`/`veth`의 blocking, disabled, promiscuous, forwarding 출력은 컨테이너
  bridge 포트를 연결하는 정상 상태 전이이며 자체적으로 오류가 아니다.
- bridge filtering 안내는 Linux `net/bridge/br.c`에서
  `CONFIG_BRIDGE_NETFILTER=m`인 경우 출력한다. 이 커널은 이미 해당 모듈을
  빌드하며, 실제 guest에도 맞는 vermagic의 모듈이 있다. 부팅 시 명시적인
  `br_netfilter` 로딩으로 호환 필터링 경로를 준비한다. 의존성인 bridge가 먼저
  초기화되므로 안내문 자체는 여전히 출력될 수 있다. 메시지 억제를 위한 커널
  변경이나 printk 전체 수준 변경은 하지 않는다.
- `SELinux: mount invalid ... cgroup2`는 현재 crun 1.29.1의 cgroup2 신규 mount
  경로가 SELinux mount label을 붙여 시도한 후, 실패하면 label 없이 재시도하는
  동작과 관련된다. 기존 cgroup2 superblock의 보안 설정과 충돌한다.
  SELinux Enforcing을 끄거나 cgroup 격리를 제거하는 방식으로 처리하지 않는다.

## 로그 UI

기존 콘솔 스타일을 유지하며 탭을 **Host log / Guest log** 두 개로 고정했다.

- Host log: 작업 드롭다운에서 선택한 시나리오의 명령, guest SSH stdout/stderr,
  사전 검사, 실행 결과, 업로드/다운로드 로그.
- Guest log: 현재 관리 VM의 `linux-uart.log`를 고정 표시하며 Host 선택과 독립적이다.
- 새 Power on에는 새 세션 ID를 부여한다. Reboot는 명령을 발행하기 직전에
  새 세션 ID와 UART 파일 시작 offset을 기록한다. 해당 reboot의 종료·부팅
  메시지부터 새 Guest log에 표시한다.
- 이전 작업은 드롭다운의 `이전 세션 · 실행 이력`에서만 선택한다. 원본 파일은
  삭제하지 않는다. 서버 재시작 시 예전 VM 소유권을 자동 승계하지 않는다.
- 네트워크 응답의 세션 ID를 검사하여 늦게 도착한 이전 Guest 로그가 새 화면을
  덮어쓰지 않도록 한다. 각 응답은 최신 256 KiB로 제한하며 잘림 여부를 표시한다.

## 초기 검증

- backend/telemetry 테스트 65 PASS, UI 테스트 13 PASS.
- 실제 UART 46,036 bytes를 조회했고, 과거 Host 작업 선택 후 Guest 출력이
  유지되는 것을 확인했다.
- 390px 모바일 가로 넘침 없음, JavaScript 오류 없음.
- 화면: `build/autosd/dashboard/fixed-log-tabs-mobile.png`.
- boot 시작 직후 이전 VM의 UART를 새 세션으로 반환할 수 있는 경합을 수정했다.
  Host 상태 조회와 Guest 응답 사이의 세션 변경 및 동일 세션의 지연 응답도
  회귀 테스트로 확인했다.

## 런타임 보정 산출물

- crun 1.29.1 소스: `autosd/crun/` (기존 외부 소스는 수정하지 않고 별도 patch 적용).
- 패치·빌드·설치 가이드: [runtime/README](../autosd/customization/runtime/README.md).
- 실제 바이너리: `build/autosd/crun-cgroup-fix/crun-cross`.
- SHA256: `8a685e3d99443332d7003b2137c43b574ab4e01a3a4647711fda3e9e2f1ee170`.
- 실제 EL10 guest에서 root/QM 모두 `--version` 및 라이브러리 로딩 검증 PASS.
  SYSTEMD/SELINUX/APPARMOR/CAP/SECCOMP/EBPF/CRIU/JSON_C 기능을 유지한다.
- root의 `container_runtime_exec_t`, QM rootfs의 `qm_file_t` 라벨을 유지했다.
  원본은 각 `/usr/bin/crun.apollo-vendor-backup`으로 보존했다.
- 설치 증거: `build/autosd/crun-fixed-install-20260927/`.
- ARM64 에뮬레이션 빌드는 느려서 호스트 교차 컴파일러와 동일 EL10 sysroot를
  사용한 별도 산출물로 전환했다. 초기 패키지 캐시 충돌을 포함한 실패 로그도
  보존했다. upstream 전체 테스트 통과를 주장하지 않으며 실제 guest 검증과
  프로젝트 회귀 테스트를 구분한다.
- 전체 AutoSD Python 테스트 237 PASS, UI 테스트 13 PASS.

개발용 overlay이며 vendor 서명 RPM 자체를 재생성한 것은 아니다. 재생성 이미지에는
`prepare.py --crun-binary`로 같은 artifact를 root/QM에 반영해야 한다.

## 실제 cold boot 검증

정상 종료 후 수정 디스크의 복사본으로 새 부팅:
`build/autosd/dashboard/20260927-135515-37b96135/2ca1c75d340c4b8eaa1e4e4127e7d76d/`.
포괄 검사 증거: `build/autosd/crun-coldboot-verify-20260927/` (exit 0).

| 항목 | 관측 결과 |
| --- | --- |
| SELinux cgroup mount 오류 | 0건 |
| SELinux | Enforcing, qm_t/container_t/qm_container_t 도메인 유지 |
| 런타임 | root/QM 모두 지정 SHA256, 기존 기능·파일 라벨 유지 |
| bridge | br_netfilter 자동 로드, 3개 hook=1, podman0 up |
| 컨테이너 | QM/ADAS/QM nested 모두 running |
| CPU·자원 제한 | ADAS CPU 1, QM CPU 2-3, weight 200/50, memory 512 MiB/1 GiB |
| health | HEALTHY, failures=0, 정상 상태 검사 PASS |
| 로그 | 현재 세션 1건 / 이전 38건 분리, Guest UART에 mount 오류 0건 |

boot ID: `9807c8c8-e112-429e-9a73-08f000b370c4`.
화면: `build/autosd/dashboard/fixed-log-coldboot.png`.

## Reboot 및 최종 상태

Reboot job `48c8152c1b6446a78ce6139d1ba307f1` PASS.
새 boot ID `7b852100-4fff-49e8-a512-a9795833db60`로 SSH 재연결을 확인했다.
`build/autosd/crun-reboot-verify-20260927/`의 실제 guest 검사도 exit 0:

- kernel 로그 `SELINUX_MOUNT_ERRORS=0`, Enforcing 유지.
- br_netfilter 자동 로드, 세 bridge hook=1.
- BlueChi host/qm.host online, CPU·메모리 제한 및 SELinux 도메인 유지.
- `AUTOMOTIVE_SCENARIO_HEALTHY_PASS`, safety HEALTHY, failures=0.
- Guest 탭 선택은 유지되고 새 UART 세션으로 전환됨. 현재 작업 1건,
  이전 이력 39건으로 분리되어 두 고정 탭만 표시됨.
- 새 Guest UART 57,862 bytes에서 mount invalid 0건.
- 화면: `build/autosd/dashboard/fixed-log-reboot.png`, 브라우저 오류 없음.

최종 VM은 실행 중이며 ONLINE·HEALTHY 상태로 남겼다. bridge의 모듈 안내문과
정상 veth 상태 전이는 의도적으로 보존한다. 이것은 물리 하드웨어 안전성/격리 인증
또는 upstream crun 전체 회귀 테스트 통과를 의미하지 않는다.
