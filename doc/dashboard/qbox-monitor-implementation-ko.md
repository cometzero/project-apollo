# QBox Monitor Dashboard 구현 및 검증

## 구현 범위

기존 Guest telemetry/Host·Guest 로그와 분리된 simulator worker를 추가했다.
Monitor는 loopback에서만 열며 launcher가 기록한 PID/start ticks 및 실제
LISTEN socket 소유권을 확인한다. 이전 VM의 표본은 새 VM에 적용하지 않는다.

| 기능 | 구현 계약 |
|---|---|
| Simulation panel | SystemC 시간, simulation/host 진행 비율, 표본 age, 도메인별 QK 상태 |
| MCIPS | 실제 plugin 응답만 표시; 모델 설정·진행 상태이며 물리 처리량 아님 |
| Timeline | firmware/Guest boot 관측, injection JSON 및 watchdog 로그의 simulation timestamp |
| Inspector | metadata-only 객체 조회; CCI callback·MMIO 자동 읽기 없음 |
| QMP | 도메인별 query-status/query-cpus-fast/query-version만 허용; request ID·deadline·byte quota |
| MHU01 | channel 0 lost doorbell → Guest timeout → 전체 reset → health/HIPC 복구 |
| Pause qualification | 10회 × 최소 2초 정지 → 동일 boot ID → health/HIPC → WD04 복구 |

QK 상태는 Guest CPU 사용률과 다르다. `sc_suspended`는 일반 QK 동기화 중에도
true가 될 수 있으므로 사용자 Pause 판정에는 별도 `monitor_paused`를 사용한다.
Pause/Resume은 해당 **현재 VM 실행**의 qualification이 통과해야 활성화된다.
Power cycle 후 재검증이 필요하다. 제어 응답이 불명확하면 UNKNOWN으로 남기며
자동 재전송하지 않는다. 이 경우 예외적으로 현재 소유한 VM의 명시적 Resume을
허용한다. Resume 성공만으로 qualification을 되살리지는 않는다.

## Quick Guide

### 1. Native provider 빌드 및 테스트

```bash
./yocto_build.sh qbox-apollo-qvp-native -c compile
./yocto_build.sh qbox-apollo-qvp-native -c populate_sysroot
```

두 번째 명령은 recipe의 `do_check`, install 및 sysroot 갱신을 포함한다.
실행 중인 VM이 사용하는 provider는 교체하지 말고 먼저 정상 종료한다.

### 2. Dashboard 시작

아래 이미지 경로는 사용자가 준비한 regular manifest와 Automotive customization
디스크로 지정한다. launcher는 원본 디스크를 직접 실행하지 않고 실행별로 복사한다.

```bash
python3 scripts/autosd_dashboard/server.py \
  --listen 127.0.0.1 --listen 192.168.0.13 --port 8765 \
  --allow-unauthenticated-lan --allow-private-guest \
  --backend qbox-full --ssh-port 2244 \
  --manifest build/autosd/demo-minimal-qm-prepared/regular.json \
  --rootfs /absolute/path/to/prepared/rootfs.wic \
  --qbox-diagnostics --runtime-injection
```

`--qbox-diagnostics`와 `--runtime-injection`은 기본 꺼짐이다. 전자는 읽기 전용
QMP를, 후자는 파괴적 MHU 데모를 위한 모델 mutation capability를 켠다.
관측만 필요하면 둘 다 생략한다. `--base-dir /absolute/path`는 private disk와
로그 위치를 변경한다. 로그인 없는 LAN 제어는 신뢰할 수 있는 내부망에서만 사용한다.
QMP에는 Python `websocket-client`가 필요하다. 없으면 미지원 원인을 표시한다.

### 3. 관측 및 데모

1. Power on → firmware 도메인 진행 및 simulator ONLINE을 확인한다.
2. Feature 1·2 PASS를 기다린다. Monitor ONLINE만으로 Guest 부팅 성공은 아니다.
3. QBox panel에서 객체 경로 `platform`을 조회한다. QMP는 AP/RSE/SI CL0/SI CL1을
   선택해 조회한다. RT/제어 작업 중에는 진단 요청을 즉시 거부한다.
4. 필요하면 Pause qualification을 실행한다. 실제 watchdog reset을 포함하므로
   Guest 휘발성 상태가 바뀐다. 통과한 실행에서만 Pause/Resume을 사용한다.
5. MHU 데모는 RSE·SI·AP **전체 reset**을 포함한다. 주입 접수와 Guest 관측 및
   복구 판정을 따로 확인한다. DELETE/cancel만으로 PBX pending이 복구되지 않는다.

### 4. 재현 가능한 검증 명령

```bash
python3 scripts/test/validate_autosd_monitor_dashboard.py \
  --out build/qbox-apollo-qvp/dashboard-monitor-20260928 --action boot
python3 scripts/test/validate_autosd_monitor_dashboard.py \
  --out build/qbox-apollo-qvp/dashboard-monitor-20260928
python3 scripts/test/validate_autosd_monitor_dashboard.py \
  --out build/qbox-apollo-qvp/dashboard-monitor-20260928 \
  --action monitor-qualify --confirm-disruptive
python3 scripts/test/validate_autosd_monitor_dashboard.py \
  --out build/qbox-apollo-qvp/dashboard-monitor-20260928 \
  --action monitor-mhu --confirm-disruptive
python3 scripts/test/validate_autosd_monitor_dashboard.py \
  --out build/qbox-apollo-qvp/dashboard-monitor-20260928 \
  --action mixed-criticality --confirm-disruptive
python3 scripts/test/validate_autosd_monitor_dashboard.py \
  --out build/qbox-apollo-qvp/dashboard-monitor-20260928 --action rt-r02
```

이미 부팅되어 있다면 첫 명령을 생략한다. 검증 실패를 PASS로 치환하지 않으며
호스트 timeout은 제출된 모델 동작이 취소됐음을 의미하지 않는다.
`--action` 없는 관측 검증은 QMP까지 검사하므로 서버의 `--qbox-diagnostics`가 필요하다.

Backend 회귀는 먼저 `--action shutdown --confirm-disruptive`로 정상 종료한 뒤
`--action boot --backend qbox` 또는 `--action boot --backend qemu`로 실행한다.
실행 중 backend 변경은 거부한다. AP-only에서는 관측 검증 명령으로 AP QMP를
확인할 수 있다. QEMU에서는 QBox 진단 대신 `/api/simulator/snapshot`이
UNSUPPORTED인지와 기존 Guest health를 확인한다.

## 증거와 제한

실행별 dashboard 디렉토리에는 `simulator.jsonl`, `simulator-events.jsonl`,
`simulator-capabilities.json`, 작업별 `simulator-result.json` 및 시나리오 결과가 남는다.
Domain epoch는 firmware 로그 기반 관측이며 injection generation과 별개이다.
모델 로그 유실·회전·quota 초과는 gap/drop으로 기록한다. Timestamp 없는
부팅 로그에 정확한 simulation 발생 시각을 만들어 붙이지 않는다.

- 기본 simulator 주기 2초, 요청 timeout 2초, 응답 1 MiB, backoff 최대 30초.
- 표본 저장 64 MiB, 이벤트 저장 8 MiB, 메모리 history 120개/event 500개 상한.
- RT·watchdog·mixed-criticality·제어 작업 동안 simulator/Guest 주기 수집을 중단한다.
- 범용 HMP/QMP, 임의 CCI 쓰기, 임의 MMIO는 웹 API로 제공하지 않는다.
- Debug-read 주소/SystemC 문맥 수정은 native component 테스트 대상이며 웹에
  read-safe register 목록이 검증되지 않은 주소를 노출하지 않는다.
- QEMU는 기존 Guest 관측을 유지하고 simulator panel은 UNSUPPORTED이다.
- 물리 WCET/FTTI, ASIL 인증, 소비전력/온도, FVP/RTL timing parity의 증거가 아니다.

### 최초 계획과의 차이

안전하게 검증되지 않은 기능을 임의로 활성화하지 않는다.

| 계획 항목 | 현재 경계 |
|---|---|
| P1 scenario와 simulator 연계 | 같은 실행의 결과·epoch·이벤트 연결. 측정 barrier 중 값은 last-known이며 동시 측정값이 아님 |
| QM/ADAS/cgroup/simulation 속도 동시 비교 | 기존 Guest 결과는 유지. Barrier 중 simulator polling을 중단하므로 정밀 시간 정렬 비교는 미구현 |
| Structured model event stream | 기존 timestamped injection/watchdog 로그를 bounded 수집. 모든 모델 전이를 제공하는 범용 native event API는 미구현 |
| P2 debug-read | Native 주소·정렬·SystemC 경계 테스트만 수행. 검증된 read-safe register 목록이 없어 웹 MMIO는 비활성 |
| 추가 GIC/GPIO/I2C/SSU fault | 이 dashboard에서는 미노출. MHU channel 0 시나리오만 고정 허용 |
| 수집 부하 | 3개 브라우저에서 단일 주기 유지 확인. Collector off/on 정량 성능 차이 및 허용 기준은 아직 미검증 |

## 검증 결과

검증일: 2026-09-28. 증거 디렉토리:
`build/qbox-apollo-qvp/dashboard-monitor-20260928/`.
계획 문서 또는 빌드 성공만으로 미실행 항목을 PASS 처리하지 않는다.

### 회귀 검사

```bash
pytest -q tests/test_autosd*.py tests/test_qbox_monitor_manifest.py \
  tests/test_run_qbox_autosd.py tests/test_run_qbox_linux.py
node --test tests/test_autosd_dashboard_ui.cjs
```

Python **633 PASS**, UI **36 PASS**. Host Paramiko의 TripleDES deprecation
warning 2건은 기존 의존성 경고이며 테스트 실패가 아니다.

### 초기 full-system 실험 및 발견한 결함

| 실험 | 관측 및 판정 |
|---|---|
| Monitor-only 부팅 | `54dd316672254ed0abbe0e32aed58233`: full boot/Automotive health PASS |
| SSH 이전 관측 | Guest UNAVAILABLE 상태에서도 simulator ONLINE, RSE 1/SI CL0 1/SI CL1 4/AP 4 QK 관측 |
| 브라우저 | localhost/LAN 접속, 3개 탭에서 약 2초 단일 sampler 유지; 390px 폭 가로 넘침 없음 |
| Inspector | `platform` 직계 객체 327개 metadata 조회, MMIO 자동 읽기 없음 |
| 첫 Pause 검증 | `376d16cf078e469fbace24a3e5a5f829`: FAIL. SystemC 시간은 정지했으나 CPU local time이 약 2.08초 진행; Resume 복구 PASS |
| MHU 장애·복구 | `4a3e3ff67e55435b8b3ddd5a10f6bc49`: PASS. 주입 소비, Guest timeout, 전체 reset, 새 boot ID 및 health/HIPC 3/3 복구 |
| 정상 종료 | `b486e14f6a9c4bb48d7c47bd48daddca`: PASS, QBox 프로세스 종료 확인 |

MHU 실행에서 네 도메인 firmware epoch는 모두 1→2로 증가했고 injection
generation은 0→1로 바뀌었다. Guest boot ID는
`bec0a599-be43-4ae5-9778-d73b6a638e91`에서
`ee15920a-8696-4ecd-be66-e52610bb625f`로 변경되었다.
증거는 `monitor-only/monitor-mhu.json`, `after-mhu-state.json`에 보존했다.

실제 부팅 검증 중 다음 결함을 수정했다.

- Native provider의 필수 module 목록에 `qmp`가 없어 로드 실패: required target에 추가.
- RSE QMP가 QemuInstance 초기화 후 등록되어 socket이 생성되지 않음:
  `rse_cpu_pass` 내부에 QMP를 배치하고 instance/device 생성 순서를 명시.
- 선택적 QMP 연결 실패가 reader thread의 uncaught report로 VM을 종료:
  bounded 연결 대기, warning 및 예외 격리로 변경.
- SystemC-only Pause가 full-system 정지를 보장하지 않음: 기존 global debugger
  coordinator를 재사용해 모든 QemuInstance 정지 후 SystemC를 suspend하도록 변경.
  검증 gate에는 모든 CPU local time의 2초 정지도 추가했다.

최종 provider의 재검증 결과는 다음 절에 기록한다. 위 첫 Pause 실패를
빌드 성공으로 대체하거나 qualification PASS로 간주하지 않는다.

### 최종 native 및 Pause/Watchdog qualification

`populate_sysroot` 성공. Platform **64 PASS**, 선택된 core **61 PASS**;
recipe의 기존 slow/unstable 제외 목록은 그대로이며 해당 제외 항목의 PASS를
의미하지 않는다. 로그: `native-do-check-coordinated-pause.log`.
입력 provider/DTB hash는 `final-provider-sha256.txt`에 기록했다.

- 실행: `141236adc40845ecb47f52642e16892f`, QBox full + QMP + injection.
- Qualification: `542b2f863d654632b9575a9236116f45`, **PASS**.
- 10회 각 2초 이상 정지에서 SystemC 및 모든 10개 CPU local time 불변.
- Pause 반복 전후 boot ID `af00a73b-77f8-49cd-b89e-08e9858f4c59` 유지,
  이후 Automotive health와 HIPC 3/3 PASS.
- 이어 WD04 WS0→WS1 reset/clear, SI IRQ 재무장, host 프로세스 연속성 PASS.
  RSE/SI epoch 유지, AP epoch 1→2 및 새 boot ID
  `d23d380d-088e-4e42-b19a-40e919800d98`, health/HIPC 복구 PASS.
- 근거: `final/qualification.json`, `final/monitor-qualify.json`.

QMP 실제 발견 결과는 `qmp_socket`이 아닌 내부
`qmp_socket.qmp_socket_router`가 monitor biflow 이름이었다. 새 manifest를
수정하고 기존 manifest에는 정확한 이름 또는 해당 고정 suffix만 허용하는
discovery를 추가했다. 네 도메인의 `query-status`에서 running 응답을 확인했다.

### 최종 웹 API 확인

최종 서버 재시작 후 실행 `2cb97aba2b0a4acd93dbe96cd54df183`에서 SSH 이전
simulator ONLINE 및 네 도메인 QMP의 3개 읽기 전용 명령을 모두 검증했다.
실제 CPU 목록 수는 RSE 1 / SI CL0 1 / SI CL1 4 / AP 4이다.
LAN 브라우저에서도 RSE QMP 응답을 확인했다.
증거: `api/observation.json`, `api/pre-ssh-state.json`, `api/rse-qmp.png`.

QMP `stop`, 잘못된 객체 경로 및 외부 Origin은 거부되었다. 새 run의 Pause는
다시 비활성화되며 이전 run의 qualification을 재사용하지 않는다.
이전 run의 일반 Pause/Resume은 각각 `final/pause.json`, `final/resume.json`에서 PASS,
정상 Power off는 `final/shutdown.json`에서 PASS이다.

### 기존 시나리오 회귀

| 실행 | 결과 | 증거 |
|---|---|---|
| MC01 자원 분리 | PASS | `api/mixed-scenarios.json` |
| MC02 QM 부하 격리 | PASS; 측정 QM CPU time 24.191077초, ADAS heartbeat 지속 | 동일 |
| MC03 QM 장애·복구 | PASS; 컨테이너 재생성 및 ADAS 유지 | 동일 |
| RT R02 FIFO 측정 | 측정 PASS / WITHIN_OBSERVED_THRESHOLD | `api/rt-results.json` |

Mixed-criticality 작업 `3402681701ae4dcbad69ee8d45e89625` 및 RT 작업
`095963efc0f843d19c2763593238d68b` 동안 simulator는 DEFERRED이며 sample sequence
114가 유지되었다. 진단 QMP 요청은 busy로 즉시 거부되었다. 결과 화면은
`api/mixed-result.png`, `api/rt-result.png`에 저장했다. 이 결과는 실제 보드의
시간 격리나 WCET를 보증하지 않는다.

최종 MHU 작업 `0afd762cecbf461ba7b3df41e3cd018e`도 **PASS**이다.
`consumed_and_guest_timeout=true`, `all_domain_epochs_advanced=true`,
`recovered=true`를 확인했다. 즉 접수 응답만으로 PASS한 것이 아니라 실제
소비·Guest 실패·네 도메인 재부팅·health/HIPC 복구가 모두 관측되었다.
증거: `api/monitor-mhu.json`, `api/mhu-scenarios.json`, `api/mhu-result.png`.

정상 Reboot `a154bc9341d04acb8d18c089733aa933` 및 후속 자동 health도 PASS.
새 boot ID `193a0d77-1573-477c-8a5b-1415596dc227`과 네 도메인 epoch 3을
관측했다 (`api/reboot.json`, `api/after-reboot-state.json`).

반복 QMP 조회 후 replay buffer가 byte 단위로 잘려 첫 JSON 줄이 불완전해지는
문제도 재현했다. 첫 줄이 현재 request ID를 포함하지 않을 때만 bounded skip하고,
이후 malformed JSON은 계속 거부한다. RSE 175/AP 174바이트의 prefix를 건너뛴 뒤
네 도메인 응답을 확인했다. 이는 수정한 helper의 직접 조회 검증이며 당시 서버에
hot reload한 결과가 아니다 (`api/replay-recovery.json`). 이후 서버 재시작으로 반영했다.

### AP-only / QEMU 회귀

- 첫 AP-only 실행은 공유 AP 생성 코드가 요구하는 `ctx.modules` 초기화 누락으로
  FAIL했다 (`ap-only/boot.json`). AP-only profile에서 SI interrupt/window metadata만
  로드하도록 수정했다. SI 도메인은 생성하지 않는다. C++/hw-block 변경은 없다.
- 수정 후 AP-only 실행 `e1a3c333a1c5412b9638bc24581e5830`에서 boot/자동 health,
  AP QK 관측 및 QMP 3종 조회 **PASS** (`ap-only/fixed/boot.json`, `observation.json`).
  Full-only MHU와 Pause qualification은 비활성이다.
- QMP 웹 API 8회 반복(24개 명령) 모두 PASS. 최종 status 응답에서는 실제
  replay prefix 146바이트가 skip되어 parser 복구를 웹 API에서도 확인했다
  (`ap-only/fixed/replay-8/observation.json`).
- QEMU 실행 `98276d56a5524973b23af97870b5601d`: boot/자동 health/정상 poweroff
  **PASS**. Simulator는 UNSUPPORTED이며 가짜 도메인·CPU 수치를 제공하지 않는다
  (`qemu/boot.json`, `qemu/shutdown.json`, `qemu/simulator.json`).

AP-only 실부팅은 launcher 기본값인 source-tree Lua profile과 최종 native provider를
사용했다. 공유 모듈 metadata 수정은 다음 native populate_sysroot 때 설치 profile에도
반영된다. Full-system native qualification 결과와 AP-only source profile 검증은 구분한다.

## 인계 상태

최종 실행 `4750038b99bf443bb1e016fb9b037b76`을 **QBox full-system**으로 부팅해
네 도메인·모듈 초기화 및 자동 Automotive health PASS, Guest/Simulator ONLINE을
확인하고 실행 상태로 남겼다. `handoff/boot.json`, `handoff/state.json`,
`handoff/observation.json`, `handoff/launch.json`에 현재 실행 근거가 있다.

- 접속: `http://127.0.0.1:8765/`, `http://192.168.0.13:8765/`.
- 현재 서버는 `--qbox-diagnostics --runtime-injection`을 명시적으로 사용한다.
- Pause는 run별 qualification이므로 새 인계 실행에서는 다시 검증해야 활성화된다.
- 검증 중 private disk는 `/tmp/apollo-dashboard-monitor-*`에 보존했고 이미지 원본을
  덮어쓰지 않았다. 작은 qualification/MHU 원본 로그는 증거 디렉토리에도 복사했다.
- 기존 무관한 staged/untracked 변경은 보존했다. 커밋·푸시는 수행하지 않았다.
