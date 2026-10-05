# 실행 구조와 API 설계

상태: **신규 설계, 미구현**. 기존 기반은 [현재 구성](current-state-ko.md)을 따른다.
구조 원본: [dashboard-architecture.drawio](assets/dashboard-architecture.drawio).

## 1. 실행 계약

`run_qbox_yocto.sh --dashboard`는 기존 이미지/provider 해석 결과를 typed launch
specification으로 저장하고 foreground 웹 서버로 `exec`한다. 웹 listener를 준비한
후 첫 board boot job을 자동 등록한다. 서버가 웹 요청을 받고, 공통 supervisor가
QBox/TC397/SIL Kit process를 소유한다. tmux 및 자동 브라우저 실행은 필요 없다.

| 옵션/조건 | 제안 동작 |
|---|---|
| `--dashboard` | headless + 지속 실행 + 자동 첫 부팅. 기본 `nexios-image` 선택 유지 |
| `--bsp --dashboard` | BSP 이미지; 기존 vMCU 준비를 headless에서도 수행 |
| `--bsp --dashboard --sil-kit` | registry/bridge/restbus 포함. 현재 executable 검사 재사용 |
| `--dashboard --stats` | 기존 통계 옵션 전달. 5초마다 현재 QBox 부하 수집·화면 표시; monitor/QMP 자동 활성화 |
| `--dashboard --stats-interval N` | 기존 유한 양수 seconds 검증 유지. `--stats`를 포함하며 지정 간격 사용 |
| `--no-vmcu` | Apollo-only 실행; MCU/CAN 제어는 DISABLED 사유 표시 |
| `--sil-kit-allow-actuation` | 기존 CAN op5..7 허용 opt-in 유지; 웹 인증과는 별개 |
| `--dashboard-listen IPV4` | 새 옵션. 반복 가능; 지정한 실제 local IPv4에 bind |
| `--dashboard-port 8765` | 새 옵션. 충돌 시 명확히 실패; 다른 서버로 attach하지 않음 |
| `--dashboard-password-file PATH` | 새 옵션. 기존 private credential 함수 재사용 |
| `--dashboard` + `--headless` | 중복 지정 허용 |
| `--dashboard` + `--no-attach` | 호환상 허용하되 headless에는 영향 없음 |
| `--dashboard` + tmux 전용/GDB UI 옵션 | 실행 전 충돌 오류; 조용히 무시하지 않음 |
| `--dashboard` + `--dry-run` | resolved launch spec과 URL/bind 계획만 출력; bind/boot/credential 생성 없음 |
| `--dashboard-boot-timeout N` | 새 옵션, 기본 900초의 host boot readiness deadline, 양수만 허용. RUN 총 수명과 별개 |
| 기존 `--timeout` | dashboard에서는 하위 runner에 0을 사용. 명시적 양수는 충돌 오류와 새 boot-timeout 옵션 안내 |
| `--multi-session` | 서로 다른 session/output/HTTP·monitor 포트 사용; process 소유권 격리 |

현재 product 이미지에 vMCU BSP boot adaptation을 적용하지 않는다. 일반
`--dashboard`에서도 AP/RSE/SI 관측과 지원 시나리오는 동작해야 한다. 초기 product
vMCU 제어는 `UNSUPPORTED_IMAGE`로 표시하고, 지원을 추가하려면 product의 AP peer
패키징·부팅 정책·이미지 검증을 별도 완료한다. BSP로 자동 치환하지 않는다.

`--monitor`의 의미는 계속 내부 QBox monitor다. Dashboard는 읽기 전용 monitor를
자동 구성하고, QMP diagnostics는 fixed query allowlist로 사용한다. Runtime injection은
기존 startup opt-in을 유지하며 dashboard를 켰다는 이유로 활성화하지 않는다.

## 2. 서버·backend·supervisor 분리

신규 모듈 이름은 구현 위치 제안이다. 공통 컴포넌트를 한꺼번에 이동하지 않는다.

| 계층 | 소유 파일/변경안 | 책임 |
|---|---|---|
| Launcher | `run_qbox_yocto.sh` | 기존 artifact resolution, 옵션 검증, launch spec 작성 |
| 웹 공통 | `scripts/autosd_dashboard/server.py` | 인증, read API, job 접수, artifact 제공 |
| Yocto adapter | 신규 `scripts/autosd_dashboard/yocto_board.py` | launch/readiness/log mapping/capability; AutoSD와 분리 |
| 보드 수명 | 신규 `scripts/run/qbox_board_session.py` | 공통 process ownership, FIFO 준비, TC397 wrapping, stop receipt |
| 동작 adapter | 신규 `scripts/autosd_dashboard/vmcu.py`, `board_scenarios.py` | typed CLI/CAN와 기존 profile evaluator 호출 |
| 관측 | 기존 simulator/topology + 신규 board/log adapter | 단일 수집기, bounded cache, run/epoch/source 보존 |
| 화면 | 기존 `web/*`, 신규 `board.js`/`board.css` | 동일 graph의 Board/Block view, UART·control·job 화면 |

Backend에는 `prepare`, `start`, `observe_readiness`, `stop`, `capabilities`,
`log_sources`, `run_action` 정도의 작은 계약만 둔다. BSP boot marker/serial과
product SSH/service health를 구분한다. AutoSD 전용 `manifest`가 없어도 Yocto backend는
동작하며 AutoSD의 기존 실행과 API를 회귀 검증한다.

## 3. 시작·종료 순서

1. `.qboxconf`와 artifact를 해석하고 session lock, 새 run directory를 만든다.
   selected Lua/provider/artifact hash와 필요한 환경·CCI override만 기록한다.
2. 웹 bind와 인증 파일을 준비한다. 브라우저는 PREPARING/BOOTING 상태부터 볼 수 있다.
3. 공통 supervisor가 UART input FIFO·log sink·monitor/QMP endpoint를 준비한다.
   FIFO 생성은 post-login probe 활성화 여부와 분리한다.
4. BSP vMCU 사용 시 private UKI preparation을 검증한다. TC397은 `-S`로 만들고
   console·Safety/AP UART·GPIO·SIL Kit 준비가 완료된 다음 QMP `cont`한다.
5. QBox를 `--foreground-runtime --keep-running-after-pass --timeout 0`의 소유 child로
   실행한다. 서버가 별도의 boot deadline를 집행한다. TC397과 QBox의 연결 readiness도 확인한다.
6. AP/RSE/SI/MCU별 진행을 독립 표시한다. 전체 boot gate 통과 후 RUNNING으로 전환한다.
   post-login qualification은 명시적 job으로 실행하며 boot PASS에 합치지 않는다.
   Boot deadline 만료는 FAILED로 기록하고 해당 run child를 정리하되 웹 서버와 증거는 남긴다.
7. 브라우저를 닫거나 접속이 끊겨도 실행을 유지한다. 웹의 **보드 실행 정지**는 자신이
   소유한 run만 종료하고 서버는 남긴다. **보드 재실행**은 새 run_id를 만든다.
8. launcher/server의 SIGINT/SIGTERM은 신규 owned 모드에서 자기 run의 bounded 정리까지
   완료하고 종료한다. AP-only off 상태면 이미 꺼진 AP에 재종료를 반복하지 않는다.

실행 상태는 `PREPARING → BOOTING → RUNNING → STOPPING → STOPPED`와
`FAILED/ORPHANED`를 구분한다. RUNNING은 host process 생존과 boot gate의 상태이며
현재 AP health와 동일하지 않다. AP_OFF 중에도 board run은 RUNNING일 수 있다.

`session_id`, `run_id`, UID, PID/start ticks 및 가능하면 pidfd로 소유권을 검증한다.
Dashboard 내부 restart/stop에 root launcher의 broad cleanup을 재호출하지 않는다.
다른 managed session, 외부 SIL Kit registry, 외부 UART backend는 종료하지 않는다.
시작 중 일부 child 실패는 해당 run을 FAILED로 기록하고 소유 child만 정리한다.
SIGKILL/host 장애는 graceful cleanup을 보장하지 못하므로 재시작 시 orphan을 발견해
mutation을 차단한다. 살아 있는 PID를 이름만 보고 adopt/kill하지 않는다.

## 4. 외부 접속

현재 서버는 exact IPv4 bind와 Basic auth/CSRF/Host·Origin 검사를 제공한다.
이를 유지하여 기본 `127.0.0.1`과 host default-route interface의 local IPv4에 bind한다.
명시적 `--dashboard-listen`은 자동 선택을 대체한다. LAN 주소가 없으면 loopback으로
실행하되 `외부 접속 주소 없음`을 표시한다. `0.0.0.0` wildcard를 새로 열 필요는 없다.

기본 credential은 run/session 전용 0600 파일로 생성한다. 기존 사용자명 `autosd`는
호환을 위해 우선 유지하며 URL·사용자명·credential 파일 위치만 terminal에 출력한다.
비밀번호를 URL, JSON manifest, 다운로드 evidence 또는 access log에 넣지 않는다.
공용 LAN 무인증은 기존 opt-in이 있을 때만 허용한다. 기본 실행은 별도 질문 없이
인증 구성을 만들고 시작한다.

HTTP 직접 접속은 신뢰하는 개발 LAN 범위다. 다른 네트워크에서는 SSH tunnel 또는
TLS reverse proxy를 사용한다. TLS proxy 지원 단계에서는 `public_origin` allowlist와
proxy 신뢰 범위를 명시하고 현재 `http://Host` 고정 Origin 검사를 수정한다. Firewall/NAT
rule은 자동 변경하지 않으며 출력된 주소의 도달성은 실제 외부 client로 검증한다.

QBox monitor는 loopback, QMP와 UART는 private socket/FIFO, SIL Kit 기본 registry는
기존 loopback이다. Browser가 임의 endpoint, Lua path, process PID, shell command,
MMIO 주소 또는 QMP 명령을 지정할 수 있는 proxy를 만들지 않는다.

## 5. 데이터와 API 계약

기존 `/api/state`, `/api/jobs`, `/api/topology`, `/api/topology/drawio`,
`/api/simulator/{snapshot,capabilities,objects,qmp,events}`는 호환 유지한다.
아래 board 경로와 body 확장은 **제안 API**다.

| API | 계약 |
|---|---|
| `GET /api/board` | 현재 run, image/profile, lifecycle, domain health, clock/age/source |
| `GET /api/board/capabilities` | available/qualified/ready/enabled/reason, 권한·reset 영향 |
| `GET /api/board/stats?after=<seq>&limit=120` | `--stats`의 최근 표본·bounded history·enabled/age/error. 미사용은 DISABLED |
| `GET /api/board/topology` | run manifest의 frozen graph + external attachments + runtime overlay |
| `GET /api/board/logs` | 허용 log ID, UART/host/CAN 구분, encoding·상태 |
| `GET /api/board/logs/{id}?cursor=...&limit=65536` | opaque cursor 기반 증분, generation·gap·next_cursor |
| `GET /api/board/scenarios` | registry의 실행 조건, 현재 가용성, evidence tier |
| `POST /api/jobs` 확장 | `action`, typed `args`, `run_id`, `request_id`, 필요 시 `confirm_disruptive` |
| `GET /api/board/jobs/{id}` | 단계별 receipt, 관측, 판정, 정리/복구 필요 여부, artifact ID |

예시 — AP off 요청. Shell text나 FIFO 경로를 전달하지 않는다.

```json
{"action":"vmcu.power.off","args":{},"run_id":"run-…",
 "request_id":"client-unique-id","confirm_disruptive":true}
```

서버는 current run 일치, capability, 필요 권한, AP/MCU epoch, action 인수 범위를
검사한다. 접수 성공은 기존 HTTP 202와 `{"job": {"id": "…", ...}}` wrapper를 보존하며
완료 PASS가 아니다. 기존 필드를 유지하고 board job에만 새 필드를 확장한다. stale run/동시 충돌은
409, 미지원 capability는 이유가 있는 422, 잘못된 인수는 400으로 반환한다.
동일 request_id·동일 payload는 같은 job을 반환하고 내용이 다르면 거절한다.
mutation timeout은 `UNKNOWN`이며 자동 재전송하지 않는다. runtime injection generation,
SI epoch, MCU cookie, AP boot ID는 서로 다른 식별자다.

실행당 mutation job은 하나다. AP/SI/MCU console writer와 CAN command queue에도
단일 소유권을 둔다. 상태 수집이 CLI를 사용하면 동일 queue를 통과하며 job 중에는 건너뛴다.
작업 취소와 주입 해제/원상 복구는 별개다. Cancel 지원 여부는 adapter별 명시하며,
partial 실행 후 중지 시 `recovery_required`와 실제 cleanup receipt를 남긴다.

## 6. 관측과 UART

| Log ID | Yocto run의 현재 파일 |
|---|---|
| `ap-primary` | `qbox-primary-console.log` |
| `ap-secure` | `qbox-secure-console.log` |
| `rse` | `qbox-rse.log` |
| `si-cl0` | `qbox-safety-island-cl0.log` |
| `si-cl1` | `qbox-safety-island-cl1.log` |
| `tc397` | `tc397-uart.log` |
| host 진단 | `qbox-platform.log`, `tc397-supervisor.log`, `tc397-qemu.log` |
| CAN/participant | `vehicle-can.jsonl`, `tc397-can.jsonl`, `silkit-*.log` |

Manifest에서 ID→실제 path를 매핑한다. AP management/Safety wire는 binary protocol이며
text console로 표시하지 않는다. supervisor의 단일 socket reader를 유지하고 로그를
tail한다. dashboard가 UART socket을 두 번째 reader로 열어 byte를 소비하면 안 된다.
RSE/Secure 콘솔은 우선 읽기 전용이다. 입력은 typed command만 제공하며 raw shell은
초기 범위 밖이다. SI CL0 명령은 SCP test console이고 Zephyr shell로 오표기하지 않는다.

첫 버전은 기존 HTTP polling을 사용한다. 활성 UART는 0.5~1초, board/monitor는 2초,
host CPU는 `--stats` 사용 시 기본 5초이며 `--stats-interval`을 따른다. 옵션이 없으면
부하 수집은 DISABLED로 표시한다. 브라우저 수와 무관하게 수집기는 run당 한 개다.
SIL Kit가 있으면 CAN 0x510을 수동적으로 읽고, 없으면 MCU `vmcu-cli status`를 5초마다
조회해 cache를 만든다. GPIO level은 같은 queue의 `vmcu-cli gpio status`로 별도 조회한다.
관측하지 못한 pin은 UNKNOWN으로 표시한다. 이는 기존 MCU 판단의 조회이며 SI 보고 주기를 바꾸지 않는다.
조회 출력은 필터로 숨길 수 있지만 원본 로그는 남긴다. PMIC 9+11개 조회는 초기 수동
snapshot으로 시작해 Safety RPC를 과도하게 점유하지 않게 한다.

Log cursor는 run_id/log_id/file-generation/byte-offset에 연결한다. Rotation/truncate,
재시작, UTF-8 split, 부분 line, 지연 client를 처리하고 gap을 표시한다. HTML은 escape하고
ANSI는 제한된 renderer로 처리한다. 사용자 path traversal, symlink escape, 임의 정규식
실행을 허용하지 않는다. ID allowlist와 fixed literal search로 시작한다.

초기 상한 제안: 요청 2초, JSON 1 MiB, log page 64 KiB, 화면 ring 5,000행, session 증거
1 GiB, active job 증거 별도 256 MiB. Producer 로그를 외부에서 copytruncate하지 않고
writer와 rotation 계약을 만든다. Disk 부족 시 증거 유실을 표시하고 새 mutation job을
차단한다. 이전 run과 active evidence를 자동 삭제하지 않는다.

모든 표본은 host monotonic 수집 시각/age와 제공된 simulation time, MCU uptime,
SI epoch를 별도 보존한다. SystemC와 독립 MCU·SIL Kit 사이에 공통 clock이 있다고
가정하지 않는다. IRQ 성공·PMIC 실측 전압·물리 FTTI를 UI animation에서 추론하지 않는다.

## 7. 결과 보존

제안 위치는 `build/qbox-apollo-qvp/dashboard/<session-id>/runs/<run-id>/`다.
`launch.json`, `topology.json`, `capabilities.json`, `events.jsonl`, UART 원본,
`jobs/<job-id>/{request,result,cleanup}.json`을 보관한다. Launch snapshot에는
provider/firmware/image hashes, dirty state, 명령 argv, 허용 환경, clock policy를 남긴다.
Credential은 다운로드 대상 밖이다. Browser 재접속 시 현재 run과 완료 job을 복구하지만,
서버 재시작 뒤 orphan mutation의 자동 재개는 하지 않는다.

## 8. `--stats` 현재 부하 모니터링

**P1 필수 범위**다. 기존 `qbox_load_stats.LoadStats`와 `qbox_stats_monitor.StatsMonitor`의
계산·process identity·read-only QMP 경로를 재사용한다. CLI만 사용하는 기존 실행의
간결한 text 형식은 유지한다. 아래는 형식 예시이며 현재 실행의 측정값은 아니다.

```text
[70s] CPU 16.0% (main 2.8% | vCPU 10.7% [AP 7.8 RSE 0.2 SI0 1.5 SI1 1.2] | other 2.6%) RSS 2276M threads=28
```

| 값 | 정의·표시 규칙 |
|---|---|
| CPU total | QBox 소유 process의 `(Δutime + Δstime) / CLK_TCK / Δhost_monotonic × 100` |
| main / vCPU / other | main TID, `/TCG` thread, 나머지 host thread 분류. 100%는 host 논리 CPU 하나 |
| AP / RSE / SI0 / SI1 | QMP `query-cpus-fast`로 얻은 domain vCPU TID의 CPU 합. SystemC/I/O 비용까지 domain에 배분한 값이 아님 |
| RSS | 해당 process resident pages × page size, UI는 MiB. 보드 가상 DRAM 용량/guest RAM 사용량과 구분 |
| threads | 현재 host thread 수. CPU 수와 동일하지 않음 |
| sample interval / age | 실제 두 표본 사이 host 시간과 마지막 성공 표본의 age. 순간값 대신 직전 구간 평균 |

CPU는 100%를 넘을 수 있으며 그래프를 100%로 자르지 않는다. AP/RSE/SI 값은 vCPU의
세부 분류이므로 total에 다시 더하지 않는다. Thread 생성/종료 때문에 breakdown이
partial이면 상태를 표시하며 억지로 total에 맞추지 않는다. 값은 guest CPU 사용률,
QK 상태, MCIPS, simulation/host 진행 비율과 별도 metric이다.

구현 시 공통 계산 결과를 structured record와 text formatter가 함께 사용하도록
작게 분리한다. Text log를 정규식으로 다시 계산하거나 browser마다 `/proc`/QMP를
조회하지 않는다. 기존 runtime의 실제 QBox PID를 사용하고 Python wrapper PID를
QBox 부하로 집계하지 않는다. Domain map은 기존 TID start-time 검증과 cache refresh를
유지하며 dashboard simulator collector와 read-only query 결과를 공유해 중복 수집을 줄인다.

제안 `stats.jsonl` record는 `schema_version`, `run_id`, `seq`, `pid`, `start_ticks`,
`sample_monotonic`, `interval_s`, `cpu_pct`, `main_pct`, `vcpu_pct`, `other_pct`,
`domain_vcpu_pct`, `rss_mib`, `threads`, `partial`, `status`, `error`를 포함한다.
Launcher는 이 파일을 manifest에 등록하고 웹은 API cache와 최근 120개 표본만 유지한다.
기본 5초 설정에서 최근 10분에 해당하며 주기를 바꾸면 실제 시간 축도 달라진다.
JSONL은 기존 session quota/rotation 정책을 따른다. 첫 두 표본이 모이기 전에는
WARMING_UP, 주기의 3배 이상 새 표본이 없으면 STALE로 표시한다.

QMP 불가/중복·소멸 TID는 해당 domain을 N/A로 표시하고 가능한 process CPU/RSS는
계속 제공한다. Monitor 준비 지연만으로 board boot를 실패 처리하지 않는다.
PID 재사용/새 run은 baseline과 history를 초기화한다. 의도된 AP off와 실행 정지를
분리하며, stale 값을 0%로 채우지 않는다. RT 측정 barrier에서 통계 수집을 중단한
구간은 `SUSPENDED_FOR_MEASUREMENT`와 gap으로 표시하고 그래프로 연결하지 않는다.

이 통계는 **Apollo QBox process 범위**다. 별도 TC397 QEMU, SIL Kit participant/registry,
웹 서버는 초기 값에 포함되지 않는다. 후속 process별 panel은 supervisor가 소유한 PID로
동일 계산기를 재사용하되 QBox total과 분리한다. Shared RSS를 단순 합해 실제 보드
메모리 사용량으로 표시하지 않는다. 외부 registry의 부하는 미관측으로 남긴다.
