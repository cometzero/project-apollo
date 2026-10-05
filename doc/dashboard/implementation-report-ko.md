# Saturn-V dashboard 구현 및 검증

2026-10-05. Root repository의 launcher·Python adapter·웹 UI를 변경했다.
QEMU/SystemC/firmware 모델은 이 dashboard 작업에서 변경하지 않았으며, 현재 설치된
Apollo QVP provider와 빌드된 firmware/image로 실제 실행을 검증한다.

## 구현

| 기능 | 구현과 범위 |
|---|---|
| 실행 | `run_qbox_yocto.sh --dashboard` → 웹 서버 → 소유 supervisor → canonical full-system runner. 자동 headless, foreground 지속 실행 |
| 이미지 | 기본 `nexios-image` 유지. `--bsp`는 BSP initramfs + TC397 Zephyr, `--no-vmcu` 지원 |
| 접속 | 기본 loopback + route로 선택한 LAN IPv4, 포트 8765. 기본 계정 없이 접속, `--dashboard-password-file` 지정 시에만 Basic 인증. Host/Origin/CSRF 검사. 내부 monitor/QMP는 loopback/private socket |
| 보드도 | 실제 provider Lua·환경·CCI 인자를 launch 시점에 평가·동결. Board/Block 보기가 같은 그래프 사용. 장치/주소/출처/연결 검색, draw.io export |
| 외부 부품 | 실제 launcher endpoint가 일치하는 TC397 UART/Safety/GPIO 및 SIL Kit CAN attachment. Registry는 control plane으로 표시 |
| UART | AP primary/secure, RSE, SI CL0/CL1, TC397. 추가 host/CAN 로그. run/inode/byte cursor, UTF-8 경계·회전·gap 처리 |
| 부하 | `--stats` 기본 5초, `--stats-interval N`. 기존 text와 같은 표본으로 JSONL 생성. CPU/main/vCPU/other, AP/RSE/SI별 vCPU, RSS, threads 및 최근 120개 추이 |
| 제어 | 보드 start/stop/restart, AP/SI ping, SI PFDI/GPIO 상태, PMIC rail 9개·STAT 11개, AP off/wake/recover, TC397 reset |
| 시나리오 | Safety LINK_TIMEOUT/보고 재개, AP PFDI agent 정지/복구, CAN classic/FD64 왕복, controller restart, 차량 CAN 0x600/0x601 명령 |
| QVP 검증 | canonical registry의 11개 profile을 fresh run job으로 연결. profile assertions + canonical verdict + process 종료/cleanup을 함께 확인 |
| 결과 | 요청 ID 중복 실행 방지, stale run 차단, 상태 QUEUED/RUNNING/PASS/FAIL/UNKNOWN. 응답 timeout 시 mutation 자동 재시도 없음. 현재 run의 성공한 작업에만 qualified 표시 |
| 수명·상한 | PID/start ticks 및 소유 child 추적. 활성 run의 log/JSON 증거 1 GiB soft budget(10초 검사) 도달 시 writer 정지·원본 보존. 세션 1,000 jobs 상한. 웹 로그 응답 64 KiB, 브라우저 소스별 200k 문자, artifact 다운로드 16 MiB |

PFDI가 AP health의 유일한 기준이다. 도메인의 READY 표시는 부팅 marker 관측이며
현재 생존 판정과 구분한다. vMCU의 SI 보고 주기는 기존 **5초**다. PMIC 조회값은
프로그램된 설정/모델 STAT이며 측정 전압이나 실제 rail 전원 차단을 뜻하지 않는다.

`--stats`의 CPU 100%는 host 논리 CPU 한 개다. AP/RSE/SI 값은 QBox vCPU 합의
부분 집합으로 중복 합산하면 안 된다. TC397/SIL Kit의 프로세스 부하, guest workload
처리량, target CPU 사용률 또는 실제 보드 소비전력으로 해석하지 않는다. 오래되거나
다른 run의 표본은 현재값으로 표시하지 않는다.

## 주요 소스

- [launcher](../../run_qbox_yocto.sh), [supervisor](../../scripts/run/qbox_board_session.py), [stats producer](../../scripts/run/qbox_load_stats.py)
- [HTTP server](../../scripts/autosd_dashboard/board_server.py), [lifecycle/jobs](../../scripts/autosd_dashboard/yocto_board.py)
- [console/log transport](../../scripts/autosd_dashboard/board_io.py), [vMCU adapter](../../scripts/autosd_dashboard/vmcu.py)
- [launch topology](../../scripts/autosd_dashboard/board_topology.py), [UI](../../scripts/autosd_dashboard/web/board.html)
- [HTTP 통합 검증기](../../scripts/test/validate_qbox_board_dashboard.py)

기존 AutoSD server/진단/monitor/topology 코드를 재사용하고 Yocto 실행 adapter를
분리했다. 기존 AutoSD HTTP endpoint의 의미를 바꾸지 않았다. 보드 외형 때문에 live
CCI 이름, 주소, IRQ나 Lua 배선을 변경하지 않는다.

## 재현

검증 당시 `build/conf/local.conf`는 `MACHINE=apollo-qvp`, `DISTRO=auto-ad-nexios`이며
`bblayers.conf`에는 소유 `meta-hsoc-bsp`/`meta-hsoc-auto-solutions`가 포함된다.
실제 provider는 `build/tmp_baremetal/sysroots-components/x86_64/qbox-apollo-qvp-native/`
아래 `platforms-vp` 및 `apollo-qvp-saturn-v.lua`다. 각 run의 `board-launch.json`과
`board-topology.json`에 실제 argv/env, provider 및 source hash를 보관한다.

```bash
./run_qbox_yocto.sh --bsp --dashboard --stats-interval 2 \
  --sil-kit --sil-kit-allow-actuation --sil-kit-echo-fixture \
  --dashboard-port 18765 --monitor-port 18780 \
  --copy-disks --no-persistent-rse-state --multi-session \
  --out-dir build/qbox-apollo-qvp/dashboard-validation/runtime-final

python3 scripts/test/validate_qbox_board_dashboard.py \
  --url http://127.0.0.1:18765 \
  --out-dir build/qbox-apollo-qvp/dashboard-validation/http-check \
  --action vmcu.status --action vmcu.pmic.snapshot --action vmcu.can.roundtrip
```

통합 검증기는 명시한 `--action`만 실행한다. `vmcu.power.off/on`, fault-recover,
`qvp.bsp-core` 등의 파괴적 시험은 현재 보드 동작을 변경한다. 실패한 명령을
자동 재시도하지 않으며, 동일 request_id의 중복 제출이 같은 job을 돌려주는지 확인한다.

## 실제 시험 기록

모든 증거는 [dashboard-validation](../../build/qbox-apollo-qvp/dashboard-validation/)
아래 보관한다. 실패 run도 삭제하지 않는다.

기본 로그인 제거 전 동일 source tree 회귀 검사는 **Python 521개 + Node UI 58개 = 579개 PASS**다.
실패/error/skip은 없고 기존 Paramiko deprecation 경고 두 건이 있다.
`py_compile`, `bash -n`, 변경 범위 `git diff --check`도 통과했다.
[검사 요약](../../build/qbox-apollo-qvp/dashboard-validation/final-regression-summary.json),
[정적 검사](../../build/qbox-apollo-qvp/dashboard-validation/final-static-checks.json),
[입력 artifact SHA256](../../build/qbox-apollo-qvp/dashboard-validation/input-artifact-sha256.json)을 보관한다.
[구현 source SHA256](../../build/qbox-apollo-qvp/dashboard-validation/implementation-sha256.json)도 함께 기록했다.

| 영역 | 결과·증거 |
|---|---|
| BSP + TC397 + SIL Kit | RSE boot/handoff/measured boot, SI CL0/CL1, Linux BSP, TC397 app marker 모두 PASS |
| 기본 product | `nexios-image`의 Linux login 및 SI/RSE marker PASS. vMCU 미활성. [격리 검증](../../build/qbox-apollo-qvp/dashboard-validation/launcher-review/product-isolation.json) |
| 두 세션 | BSP와 product 동시 RUNNING, product stop/SIGTERM 후 primary run/PID/start ticks 유지, cleanup PASS·잔류 PID 없음 |
| 인증/HTTP | 초기 인증 활성 설정에서 LAN IP 경유 HTTP, 미인증 401, 잘못된 Host/Origin/CSRF 403, stale run 409, 실제 포트 충돌 시 VM 생성 전 실패 |
| topology | BSP+TC397+SIL Kit 실제 실행 설정 350 nodes/1,203 bindings, draw.io export. 구성/endpoint 출처를 보존 |
| PMIC/통신 | 9 rail + 11 STAT, AP/SI ping, CAN classic 8B + FD64 왕복 PASS. [조회 시험](../../build/qbox-apollo-qvp/dashboard-validation/http-read-pmic-v2/result.json) |
| 실제 제어 | AP off/wake 2회, TC397 reset 및 CAN cookie 재협상, CAN restart/왕복, 차량 CAN 상태·ping·PMIC·off/wake, Safety 보고 단절/복구, 실제 AP PFDI fault/복구 **18 jobs PASS**. [결과](../../build/qbox-apollo-qvp/dashboard-validation/http-controls-v2/result.json) |
| Companion 장애 | 소유 TC397 프로세스 종료 → dashboard FAILED, cleanup PASS·잔류 PID 없음. [결과](../../build/qbox-apollo-qvp/dashboard-validation/companion-crash.json) |
| 부팅 후 수명 | boot deadline 120초인 서버가 정상 boot 후 130초 이상 계속 RUNNING. [결과](../../build/qbox-apollo-qvp/dashboard-validation/post-boot-lifetime.json) |
| 동시 로그 접근 | 독립 HTTP reader 3개가 2분 동안 각각 464–472 요청 수행, cursor/read 오류 없음. 장애 상태 조회도 포함하며 장시간 runtime 부하 시험과 구분. [결과](../../build/qbox-apollo-qvp/dashboard-validation/http-three-clients.json) |
| SI CL1 PFDI profile | 실제 fresh run에서 **17/17 assertion PASS**, canonical runner pass, supervisor 종료 0, cleanup PASS. [결과](../../build/qbox-apollo-qvp/dashboard-validation/qvp-profiles/qvp.pfdi-si-cl1-second.json) |
| BSP core profile | 3회 모두 AP power-state readback 단계에서 BLOCKED. 최신 adapter도 BLOCKED를 표시. [결과](../../build/qbox-apollo-qvp/dashboard-validation/qvp-profiles/qvp.bsp-core-third.json) |
| SMCF profile | 검증 순서와 하위 runner 조기 종료 수정 후 실제 부팅·명령 전송·runner 유지는 정상. sensor 출력 미관측으로 `command_timeout:0:si0`, 120초 후 BLOCKED, FIFO/완료 gate/프로세스 cleanup PASS. [결과](../../build/qbox-apollo-qvp/dashboard-validation/qvp-profiles/qvp.smcf-coordinated.json) |
| 브라우저 | 1440/1024/390px, overflow 없음, Board/Block, 주소 검색/Inspector, 6 UART 실제 byte 증가, 통계 추이, 키보드·취소·재접속·STALE PASS. [결과](../../build/qbox-apollo-qvp/dashboard-validation/browser-validation.json) |

초기 구현의 최종 일반 실행은 `runtime-demo/runs/20261005-133000-9dfc2693`에서 RUNNING이며,
LAN URL `http://192.168.0.13:18765`의 화면과 최신 source의 상태/PMIC/CAN 왕복을 다시 확인했다.
이 실행은 당시 계정 인증을 사용했다. 후속 변경부터 기본 실행은 계정 없이 접속한다.
[최종 API 시험](../../build/qbox-apollo-qvp/dashboard-validation/http-final/result.json),
[최종 브라우저 시험](../../build/qbox-apollo-qvp/dashboard-validation/final-browser.json),
[화면](../../build/qbox-apollo-qvp/dashboard-validation/board-final.png)을 남겼다. 실행 상태와 주소는 검증 시점 기준이다.

검증 중 launch spec 작성의 `Path.open(opener=...)` 오류를 수정하고 실제 dispatch
회귀 시험을 추가했다. 별도 BSP run에서 RSE BL2의 `Read back AP state failed`
오류가 발생했으며 해당 run은 FAIL과 cleanup PASS를 그대로 보존했다
(`runtime-final/runs/20261005-130021-32953505`). 이후 명시적으로 새 run을 시작해
정상 부팅했다. 이 결과로 platform의 간헐적 BL2 부팅 실패가 해결됐다고 주장하지 않는다.
`bsp-core`의 세 시도도 같은 RSE readback 단계에서 BLOCKED였으며 각 원본
job/runner 결과를 보존한다. 해당 종류의 실패는 기존 [idle runtime 보고서](../qbox-runtime-idle.md)에도 기록되어 있다.

PFDI fault 복구 scenario PASS와 일반 boot runner 결과는 별도다. fault를 의도적으로
발생시킨 run의 canonical 결과는 `passed=false`, `blocker=si_error:pfdi_monitor_timeout`으로
남아 있다. Dashboard는 이를 일반 보드 검증 PASS로 덮어쓰지 않는다.

SMCF profile 시험에서는 client 시작 전에 네 명령이 모두 실행되어 sensor 출력을
관측하지 못하는 기존 검증 순서 문제가 드러났다. `reuse_si.py`에서 최초 client 준비,
출력이 켜진 각 단계의 새로운 sensor 값을 기다리게 수정했다. 네 번의 integration test와
기존 assertion은 유지하며 firmware/model은 변경하지 않았다. 처음 실패한 SMCF 결과도 보존한다.
또한 outer SI0 profile이 완료되기 전에 AP boot 성공만으로 하위 runner가 종료되는
경합을 수정했다. 기존 필수 marker gate를 사용하여 outer profile PASS까지 기다리고,
실패·timeout에서는 소유 프로세스와 FIFO/gate를 정리한다. 두 조기 종료 경로와 실제
child/FIFO로 지연 응답·실패를 시험했다. 현재 실제 SMCF sensor 출력이 없는 원인은
이 dashboard 작업에서 확정하지 않았고 모델 PASS로 대체하지 않았다.

## 후속 변경: 기본 로그인 제거

사용자 요청에 따라 `--dashboard`는 계정·암호 없이 접속한다. 기본 암호 파일은
생성하거나 읽지 않으며 `--dashboard-password-file` 지정 시에만 인증을 활성화한다.
Host/Origin/CSRF 및 stale run 검사는 유지한다.

HTTP·launcher 회귀 시험 **22개 PASS**. Loopback/LAN의 화면·JS·상태 API는
Authorization 없이 HTTP 200이며 로그인 challenge가 없다. 실제 launcher로
`runtime-no-login/runs/20261005-134410-db0a98ce`를 시작하여 모든 부팅 도메인 READY,
6 UART·통계·topology 조회 및 `vmcu.status` 작업 PASS를 확인했다.
현재 접속 주소는 `http://192.168.0.13:18765`다(검증 시점 기준).
[직접 접속 증거](../../build/qbox-apollo-qvp/dashboard-validation/http-no-login/anonymous-http.json),
[부팅·API·vMCU 검증](../../build/qbox-apollo-qvp/dashboard-validation/http-no-login/result.json).

## 남은 제한

- 보드 그림은 Lua에서 얻은 **논리적 배치**다. 실물 PCB 배치·회로도·배선 길이가 아니다.
- Product 이미지의 vMCU packaging과 AutoSD SSH/customization 시나리오는 이 Yocto
  adapter에서 비활성으로 이유를 표시한다. 기존 AutoSD dashboard에서 계속 제공한다.
- AP graceful off/wake는 AP core 상태·RSE reload·새 Linux/PFDI 관측 범위다.
  실제 PMIC rail gating/cold power cycle, 외부 MCU와 coherent pause, 물리 CAN 오류
  confinement/FVP/RTL timing parity는 제공하지 않는다.
- QVP profile 목록의 노출은 해당 profile의 runtime 통과를 뜻하지 않는다. 실제 실행한
  profile과 verdict는 job 증거에 남는다. AutoSD RT 측정은 이 adapter에서 실행하지 않는다.
- 전체 보드 초기 부팅의 RSE readback 실패와 SMCF sensor 출력 미관측은 남아 있다.
  추가 SystemC 진단은 boot 완료 뒤 시작하지만 `--stats` 자체의 수집은 유지하므로,
  이 조정이 기존 부팅 문제를 해결했다고 주장하지 않는다.
- LAN bind와 같은 host에서 LAN IP를 경유한 접속은 검증했다. 별도 물리 PC에서의
  방화벽·라우팅 경유 접속은 이 환경에서 검증하지 않았다.
- 증거 budget은 활성 run에 적용되며 writable image와 종료된 run은 자동 삭제하지
  않는다. 계획의 producer별 rotation·별도 job 256 MiB quota·30분 UART burst 부하
  시험은 별도 운영성 확장/시험 항목이다. 로그를 외부에서 copytruncate하지 않는다.
