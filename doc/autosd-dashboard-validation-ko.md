# AutoSD 웹 콘솔 검증 리포트

현재 로그 UI는 아래 과거의 탭 구현을 대체한 **Host log / Guest log 독립 패널**이다.
Guest는 별도 창과 서비스별 선택을 지원한다. [기본 부팅 검증](autosd-default-boot-guest-logs-ko.md).
세션 이력은 드롭다운으로 제공한다. 부팅 메시지 수정 및 세션별
검증은 [부팅 런타임 및 로그 세션 리포트](autosd-boot-runtime-and-logs-ko.md)를 따른다.

## 상단 System control 패널 (2026-09-27)

기존 산업용 콘솔의 색상·타이포그래피를 유지하는 frontend-design 기준으로
Power on/off, Reboot, Pause/Resume 패널을 상단에 추가했다.
진행 작업과 paused 상태에서 허용하지 않는 조작은 UI와 API 양쪽에서 차단한다.
호스트 전원이나 외부 VM 제어는 지원하지 않는다.

사용자 승인 후 기존 VM을 정상 종료하고 보존된 디스크의 복사본으로 재시작했다.
실제 제어 증거 session: `build/autosd/dashboard/20260927-130708-1dd19134/`.

| 제어 | 실제 확인 |
| --- | --- |
| Power on | 웹 버튼으로 boot `f0109cec2729430f9b3cc38993745546`, telemetry ONLINE |
| Pause | `1a6feaf963784cd29260538ef31b411c` PASS, HMP paused, Resume만 활성 |
| Resume | 웹 버튼으로 `84dd59abc70c462e84c4e5e278643921` PASS, HMP running |
| Reboot | `87de5ba889b8467a907cf2a07a567112` PASS, boot ID 변경 및 SSH 재연결 |
| Power off | `54c3e76a60ef4c30980aa5358f7eec58` PASS, VM exit 0 + UART Power down |

Reboot 전 boot ID `c44c8f09-44b6-43df-90d4-5ed0c05baef6`,
후 `39f65c6a-a48d-4318-b070-5ae98bea49cc`이며 재연결 후 safety HEALTHY를 관측했다.
OS 재부팅 확인과 전체 Automotive suite 검증은 구분한다.
모바일 390px에서 document width 390px, 5개 버튼 표시와 브라우저 오류 없음 확인.
화면 증거: `build/autosd/dashboard/system-controls-{live,paused,reboot,mobile}.png`.

종료 직후 Power on의 포트 사전 검사에서 TIME_WAIT 때문에 주소 사용 중 오류가
관측되어 검사 socket에 SO_REUSEADDR를 설정했다. 활성 listener 충돌 검사는 유지한다.
정상 종료 후 다음 Power on의 원본은 직전 guest 디스크로 갱신한다.
백엔드 58개, telemetry 3개, guest-exec/demo 28개, Node UI 7개 테스트 PASS.
최종 서버 재시작 후 직전 디스크를 원본으로 Power on을 다시 실행했다.
boot job `eb12147abeb64d5fa97cffb3617f29e3`에서 ONLINE, safety HEALTHY,
CPU 4개 계측을 확인하고 실행 상태로 남겼다. 최종 화면은
`build/autosd/dashboard/system-controls-final.png`다.

## Automotive guest 실시간 로그 수정 (2026-09-27)

원인은 `demo-guest.py`가 subprocess stdout/stderr를 guest 파일로만 전달하고
웹 SSH 경로에는 시작/완료 JSON만 출력했던 것이다. `run_case`를 streaming tee로
변경하여 guest 파일과 웹 console에 동시에 flush한다. 사전 검사와 본 실행의
BEGIN/END·종료 코드, nested bash의 명령 추적, stdout/stderr를 포함한다.
SSH helper에는 접속·업로드·명령 종료·다운로드 단계 표시를 추가했다.
서버 재시작 없이 다음 실행에서 새 runner를 업로드한다.

실제 읽기 전용 S01 job `44f83891ee744554838894b1e57493c4`의 웹 로그 API에서
guest 명령과 출력, 실패 지점 `systemctl is-active --quiet apollo-adas`, rc=3,
증거 회수 로그까지 확인했다. 기존 S04가 남긴 FAULT_LATCHED 때문에 예상된
health FAIL이며 임의로 복구하지 않았다. 기존 S02/S03/S04 작업은 모두 PASS였고
당시 상세 출력은 원본 evidence archive에 남아 있다.

회귀 테스트: demo/dashboard/customization 76 PASS, guest-exec/demo 28 PASS
(demo 테스트 중복 포함), Node UI 6 PASS. 실제 subprocess가 종료되기 전 개행 없는
stdout/stderr가 전달되는지, nested 명령 추적·실패 코드·timeout 124 보존을 검증했다.
Paramiko TripleDES deprecation 경고는 별도 의존성 경고이며 로그 누락 원인이 아니다.

## 작업별 로그 탭 및 개별 시나리오 검증 (2026-09-27)

대시보드는 한 페이지로 유지하고 **작업 & 실행 로그 내부만 실행 건별 탭**으로
구분했다. 이전 대시보드/로그 전역 탭 구현은 사용자 정정에 따라 제거했다.
작업별 상태·경과 시간·실제 단계 결과·로그 보기 및 키보드 탭 이동을 제공한다.
Automotive S01–S06, RT R01–R06의 12개 개별 실행과 기존 전체 실행을 함께 제공한다.
선행 상태가 맞지 않는 장애 시나리오는 자동 보정하지 않고 BLOCKED로 기록한다.

사용자 승인 후 이전 VM을 정상 종료했다. 종료 job
`f74fd5dfa0cc454c85971fd076dadcd1`은 PASS, VM exit 0,
UART `reboot: Power down`을 확인했다. 기존 작업 디스크
`20260927-114209-02d26f85/107750b50a3146fc8367d0a101330647/vm/rootfs.wic`를
보존하고 새 서버의 원본으로 지정하여 새 복사본을 부팅했다.
새 session은 `build/autosd/dashboard/20260927-120355-51b341a1/`,
boot job은 `aed18e8a4db54cb99613b3ee7dd43ad3`이다.

Python 관련 테스트 128개 PASS, Node 진행 표시 테스트 6개 PASS.
브라우저에서 두 시나리오 그룹과 작업별 로그 탭, 전역 탭 제거를 확인했다.
390px viewport에서 document width도 390px이었다.
화면 증거는 `build/autosd/dashboard/scenario-picker-mobile.png`다.

첫 S01 job `30ed3f7cbdd5434cb45c1c1ac086ea60`은 부팅 직후 QM BlueChi가
아직 offline인 시점에 실행하여 FAIL이었다. 증거를 보존했으며 이 결과를 부팅
완료로 취급하지 않았다. 이후 telemetry ONLINE 및 safety HEALTHY를 확인했다.

| 개별 실행 | 결과 | job / 증거 |
| --- | --- | --- |
| S01 현재 상태 검사 | PASS, S01 결과 1건만 생성 | `aa0ef95dfca24b8b8bd98110d809f552` |
| S05 선행 조건 검사 | HEALTHY 상태에서 BLOCKED, 시나리오 변경 없음 | `d00ca4f9200d44a192ab605564ab110e` |
| R06 cyclictest | PASS, 5,000 samples, max 694 µs | `ccaaddb9072347fbb8d2af413c3388b1` |

R06 결과의 `cases=[]`로 다른 RT probe를 실행하지 않았음을 확인했다.
사전/사후 Automotive 검사 exit 0, 측정 중 telemetry PAUSED, 종료 후 ONLINE을
확인했다. 웹 결과 선택 시 R06 한 행과 max latency 그래프가 표시됐다.
`scenario-r06-running.png`, `scenario-r06-result.png`를 같은 dashboard 경로에 저장했다.
로그 탭 ArrowRight 이동 시 focus·선택 탭·tabpanel의 `aria-labelledby`가 일치했고,
로그 영역 밖의 탭은 0개였다. 브라우저 page error는 관측되지 않았다.

검증 종료 시 VM은 running/owned, safety HEALTHY, 4개 CPU telemetry ONLINE이다.
두 주소 `127.0.0.1:8765`, `192.168.0.13:8765`는 로그인 없이 응답하며 preview
8766 서버는 종료했다. 다른 LAN PC에서의 접속 확인은 별도다.
이번 실제 개별 실행 검증은 S01/S05/R06 범위이며 나머지 개별 시나리오는 단위 테스트로
선택 분기·선행 조건·명령 구성을 검증했다. 전체 장애 주입 suite를 다시 실행한 것은 아니다.
TCG에서의 694 µs는 해당 5초 관측값이며 실제 하드웨어 RT 성능 보장이 아니다.

재현한 테스트:

```sh
python3 -m pytest -q tests/test_autosd_dashboard.py tests/test_autosd_dashboard_telemetry.py tests/test_autosd_demo_cases.py tests/test_autosd_rt_experiment.py
# 83 passed
python3 -m pytest -q tests/test_autosd_customization.py tests/test_autosd_latency_probe.py tests/test_autosd_rt_trace.py tests/test_autosd_builder_resume.py
# 45 passed
node --test tests/test_autosd_dashboard_ui.cjs
# 6 passed
```

## LAN 접속 변경 검증 (2026-09-27)

사용자 요청으로 로그인 없이 `127.0.0.1:8765`와 `192.168.0.13:8765` 두 주소에
명시적으로 bind하도록 재시작했다. 빌드 호스트에서 두 주소의 페이지 HTTP 200,
LAN API의 기존 job 8개 조회, 외부 Origin HTTP 403을 확인했다.
실제 다른 LAN PC에서의 접속은 아직 확인하지 않았다. VM은 종료 상태를 유지했다.
관련 테스트 31 PASS(5.21초). 사용자 인증은 없으며 Host/Origin·CSRF 검사는 유지된다.
이 모드에서는 접근 가능한 내부망 사용자에게 VM/데모 제어 권한이 제공된다.

실행일: 2026-09-27. [실행 Quick Guide](autosd-dashboard-guide-ko.md).

## 구현 및 실제 관측

`scripts/autosd_dashboard/`에 Python localhost server, read-only SSH collector,
외부 CDN 없는 HTML/CSS/JavaScript 웹 UI를 추가했다. 원본 이미지·기존 launcher·
기존 Automotive/RT 데모 동작은 변경하지 않았다.
frontend-design 스킬에 따라 계측 화면을 산업용 콘솔 형태로 구성하고,
실측 값·미관측 값·기능 검증 한계를 별도 표시했다.

관리 VM은 기존 RT regular 이미지의 새 copy, standalone Apollo QEMU TCG 4 CPU다.
실행 증거 session: `build/autosd/dashboard/20260927-112413-1341e716/`.

| 검증 | 결과 | 증거 |
| --- | --- | --- |
| API 부팅 | 실행 및 guest ONLINE | job `b7b352a4bb484b8d9e284d1dd4eb69e5` UART |
| 브라우저 health 실행 | PASS | job `03d8f04f55f7410c8240ffab79938307` |
| Automotive S01–S06 | 6/6 PASS | job `4b592b4adb5549bfafffbb61c9f6f989` |
| CPU instance 계측 | cpu0–cpu3 모두 유효 증분 관측 | session `telemetry.jsonl` |
| subsystem 계측 | root monitor/ADAS/QM/BlueChi, 실제 container cgroup | 같은 telemetry |
| 장애 상태 검출 | FAULT_LATCHED, ADAS deactivating/stopping, 이후 HEALTHY 복구 | `fault-monitor-evidence.json` |
| RT 중 계측 일시정지 | PAUSED_DURING_MEASUREMENT | `rt-running-evidence.json` |
| 데스크톱·모바일 화면 | 390px에서 document width 390px, 수평 페이지 넘침 없음 | `console-mobile.png` |
| 브라우저 오류 | 관측된 JS page error 없음 | agent-browser errors |

표의 job 경로는 위 session 상대경로이며, screenshot/API snapshot은
`build/autosd/dashboard/` 바로 아래에 있다. `console-online-final.png`는 실제
CPU 추이와 서비스 상태, `console-fault-latched.png`는 장애 상태,
`console-automotive-pass.png`는 6개 시나리오 결과 표를 보존한다.

부팅 중 SSH 미준비/timeout은 UNAVAILABLE로 표시했고 임의의 0%/HEALTHY로
대체하지 않았다. CPU 최초 sample도 미계산(null)이다. cgroup CPU는 cores,
메모리는 MiB로 표시하며 서비스와 container 계층 값을 합산하지 않는다.

## 웹 실행 RT 측정

job `5ed15b2f46ef44d6a708c6ac54b313a3`: 측정 유효성 PASS, 서비스 전후 검사 PASS,
latency 종합 EXCEEDED. 웹 표의 6개 행 및 SVG 6개 막대가 원본 JSON 값과 일치함을
브라우저 DOM에서 확인했다. `console-rt-result.png`에 화면을 보존했다.

| 시나리오 | 최대 지연 µs | 표본 | 판정 |
| --- | ---: | ---: | --- |
| R01 OTHER | 4,753.064 | 4,921 | EXCEEDED |
| R02 FIFO | 868.264 | 5,000 | 관측 구간 기준 이내 |
| R03 QM 부하 | 471.000 | 5,000 | 관측 구간 기준 이내 |
| R04 동일 CPU 경합 | 484.816 | 5,000 | 관측 구간 기준 이내 |
| R05 synthetic 주입 | 5,974.600 | 4,985 | DETECTION_PASS, 성능 비교 제외 |
| R06 cyclictest | 432.000 | 5,000 | 관측 구간 기준 이내 |

R07 timerlat job `79dda0fc78d1497aa87efd36b9a90572`: 수집 PASS / EXCEEDED,
IRQ/thread/user sample 538/539/539, histogram 최대 156/832/1,553 µs.
R08 osnoise job `6c758f53422f49d69f9d4ab4f74eec9c`: 수집 PASS / EXCEEDED,
1,476 samples, 평균 6.68 µs, 최대 1,680 µs.
두 실행 모두 threshold trace 저장 및 tracefs 설정 복원 확인. 웹의 수집 PASS를
latency budget PASS로 합치지 않으며 원본 `guest/rtla.log`와 archive를 보존한다.

## 종료·재시작·다운로드 검증

- 마지막 health job `5be971577ed34e90871404109743bdaf` PASS.
- 웹 종료 job `e216dcc88f1b420eac8dd69f0b1cb360` PASS: launcher exit 0,
  UART `reboot: Power down`, SSH 2244 listener 소멸 확인.
- VM 종료 후 최종 server 코드로 재시작: 기존 job 8개와 telemetry history 78개 복원.
  `vm.running=false`, `vm.owned=false`, monitor OFFLINE/historical=true;
  화면은 경과 시간에 따라 STALE 표시. 기존 VM을 임의로 재연결하지 않는다.
- 브라우저에 CPU 그래프 4개, 선택한 RT 결과 막대 6개, 새 부팅 버튼 활성 확인.
  [재시작 후 화면](../build/autosd/dashboard/console-restored-history.png).
- 브라우저의 원본 증거 다운로드 PASS. 다운로드와 원본 archive SHA-256 일치:
  `f1e958e1a9d316b361beec5ad434c6da8b0a97cc3f4cc3a9ba098eea34439e89`.
- 전체 관련 회귀 **213 PASS**, 14.62초. Paramiko의 기존 TripleDES deprecation
  warning 2개는 보존했다. JavaScript 문법, guide shell syntax, diff check PASS.
- 웹 서버는 `http://127.0.0.1:8765`에서 실행 상태로 남겼으며 VM은 종료했다.
  서버 중지/호스트 재시작 후에는 Quick Guide 명령으로 다시 시작한다.

## 명시적인 지원 한계

- root native RT probe 결과이며 ADAS application 자체의 RT화/안전성 검증이 아니다.
- RSE/Safety Island/물리 온도·전력 telemetry는 UNSUPPORTED다.
- QBox full-system, native OTA, IPC/iceoryx2, SELinux policy 설치·검증 workflow는
  웹 실행 adapter에 포함하지 않았다. 화면에 수동/미지원 범위로 명시한다.
- guest root/password 인증은 명시적으로 지정한 loopback regular private VM에만 사용한다.
  외부 multi-user 운영·인터넷 공개용 인증/권한 시스템은 아니다.
- 모니터링은 SSH 명령 시간 + 대기 5초 단위의 표본 수집이며 hard realtime 수집이 아니다.
- TCG latency/CPU 비율은 host scheduling과 계측 overhead 영향을 받는다.
  physical timing·ASIL·FFI·FTTI·WCET 보장을 주장하지 않는다.
