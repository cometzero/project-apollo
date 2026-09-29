# 빌드 이미지의 Dashboard 데모 검증 — 2026-09-29

결론: **QBox full에서 Automotive·Mixed criticality·Watchdog·MHU reset·Pause/Resume은
PASS이며, RT 측정 데모는 사용자 공간 도구/파일 누락으로 실행 준비가 미완료다.**
검증 후 VM은 정상 Power off했고 Dashboard 서버는 결과 조회용으로 유지했다.

## 대상과 방법

- 대상: `demo-minimal-qm-prepared`의 Automotive customization 적용 디스크.
- 원본: `build/qbox-apollo-qvp/autosd-minimal-qm-rebuild-20260929-pipeline-v2/rootfs.wic`
- 원본 SHA256: `3437e00c865c2d0f09861dc374389fe4e92c1f9e112d99695511cc368f1769af`
- Manifest: `build/autosd/demo-minimal-qm-prepared/regular.json`
- Backend: **QBox full system** (RSE, SI CL0, SI CL1, AP).
- 커널: `6.18.5-rt3-yocto-preempt-rt`, guest `/sys/kernel/realtime=1`.
- 원본 디스크는 수정하지 않고 Dashboard 소유 복사본을 사용했다.
- 웹 화면의 Power on 및 각 시나리오 실행 버튼으로 시작했다.
  장애 주입 확인을 승인하고 직렬 실행했다. 과거 결과를 이번 PASS로 사용하지 않았다.
- 이번 검증은 이미지 수정이나 패키지 추가 설치를 포함하지 않는다.

서버 실행 명령:

```sh
python3 scripts/autosd_dashboard/server.py \
  --listen 127.0.0.1 --listen 192.168.0.13 \
  --allow-unauthenticated-lan --allow-private-guest \
  --backend qbox-full --runtime-injection --qbox-diagnostics \
  --manifest build/autosd/demo-minimal-qm-prepared/regular.json \
  --rootfs build/qbox-apollo-qvp/autosd-minimal-qm-rebuild-20260929-pipeline-v2/rootfs.wic
```

로그인 없는 LAN 공개는 기존 요청에 따른 개발용 설정이다. 신뢰하는 내부망에서만 사용한다.

## 확인된 결과

| 시나리오 | 결과 | 근거 |
| --- | --- | --- |
| Power on / 상태 검사 | PASS | 4개 domain boot marker, 현 AP epoch 모듈 provision, Automotive health |
| Automotive S01–S06 | PASS | BlueChi 제어, QM 컨테이너 재생성, ADAS 장애, latch 유지, 명시적 복구 |
| PREEMPT_RT R01–R06 묶음 | FAIL | `latency-probe` 파일 누락으로 측정 시작 전 중단; R01–R05 측정 미실행 |
| Cyclictest R06 개별 실행 | FAIL | RT용 `check-automotive.sh` 누락으로 사전 검사 중단; cyclictest도 미설치 |
| Timerlat | UNSUPPORTED | RTLA 미설치; trace 미수집, 지연 판정 NOT_EVALUATED |
| OS noise | UNSUPPORTED | RTLA 미설치; trace 미수집, 지연 판정 NOT_EVALUATED |
| Mixed criticality MC01–MC03 | PASS | CPU/cgroup/namespace 검사, QM 부하 및 장애 중 ADAS heartbeat 진행·복구 |
| Watchdog WD01–WD03 | PASS | SBSA 구성, 20초 timeout/30초 keepalive와 정상 disarm, 서비스 watchdog 검출·정리 |
| Watchdog WD04 | PASS | WS0→WS1→reset-clear, SI0 IRQ 재무장, 새 AP boot ID, 현 epoch provision, 앱 health·HIPC 3/3 |
| MHU 장애 / 전체 reset 복구 | PASS | 정상 HIPC → doorbell 누락 후 ICMP 3회 timeout → 전체 reset 및 앱·HIPC 복구 |
| QBox Pause/Resume 실증 검증 | PASS | 10회 시간 정지/재개, boot ID 유지, 앱·HIPC 검사 및 후속 WD04 reset 복구 |
| Power off | PASS | Guest 정상 종료, Dashboard VM running=false 및 shutdown PASS |

MC02에서 ADAS heartbeat 진행 248회, 최대 관측 age 약 0.107초를 기록했다.
MC03에서도 heartbeat가 281회 진행했고 최대 관측 age는 약 0.109초였다.
이는 QBox 기능 관측값이며 ASIL 인증, FFI 증명, 물리적 WCET/FTTI 보장이 아니다.

WD04에서 AP boot epoch는 1→2로 증가했고 RSE/SI CL0/SI CL1 epoch는 1로
유지됐다. QBox 프로세스 연속성도 검사했다. 이는 AP watchdog reset 복구이며
전체 시스템 reset과 구분한다.

MHU 실험에서는 RSE/SI CL0/SI CL1 epoch가 1→2, AP epoch가 2→3으로 증가했다.
통신 손실을 실제 ICMP timeout으로 관측한 뒤 전체 reset 복구를 검증했다.

Pause/Resume의 10개 표본 모두 정지 전후 SystemC 시간 및 CPU local time이
동일했다. 재개 이후 health/HIPC exit 0, 추가 watchdog 시험 PASS를 확인했다.
추가 AP reset 이후에도 도메인별 simulator observation과 읽기 전용 QMP 검사를
다시 실행해 PASS를 확인했다.

## RT 데모 실패 원인과 필요한 후속 작업

R06의 `guest/results.json`에 실제 package/tool inventory가 보존되어 있다.

- 커널 PREEMPT_RT 활성화 및 `timerlat osnoise` tracer 제공은 확인됨.
- 미설치 패키지: `realtime-tests`, `rtla`, `trace-cmd`, `stress-ng`.
- 미설치 파일: `/usr/libexec/apollo/latency-probe`,
  `/usr/libexec/apollo/check-automotive.sh`.
- 현재 `scripts/autosd_demo/build_minimal_qm.py`의 `customize()`는 기본
  Automotive 구성만 설치하고 RT 준비 절차를 수행하지 않는다.

따라서 **커널이 RT여도 현재 빌드 이미지는 모든 Dashboard RT 데모를 실행할 준비가
완료된 이미지가 아니다.** R06의 일반적인 "Automotive scenario is not healthy"
문구는 이번에는 앱 장애가 아니라 health-check 파일 부재(returncode 127)를 의미한다.

후속 작업은 [RT 가이드](autosd-preempt-rt-guide-ko.md)의 패키지·probe·health-check
설치를 재현 가능한 이미지 빌드 단계에 포함하고, QM 내부 probe까지 준비한 뒤
R01–R06/Timerlat/OS noise를 재검증하는 것이다. 이번 검증에서 임계값을 변경하거나
실패를 PASS로 바꾸지 않았다.

## 웹 화면과 로그

- `127.0.0.1:8765`, `192.168.0.13:8765` 접근 확인.
- Host log: 실제 SSH upload, guest 명령, stdout/stderr, 단계 완료 이벤트 표시 확인.
- Guest log: AP UART 부팅 및 서비스 출력 표시 확인.
- Guest log를 Root services로 전환해 API status OK와 실제 journal/HEALTHY
  출력 갱신을 확인했다. 모든 개별 서비스 로그 선택지를 전수 검사한 것은 아니다.
- CPU 0–3 그래프 4개와 서비스/cgroup telemetry 갱신 확인.
- 도메인별 QMP `query-status`, `query-cpus-fast`, `query-version` 및 simulator
  observation 검증 PASS.
- MC 결과 표의 실제 sample 수·heartbeat age·QM CPU 사용량 표시 확인.
- Timerlat은 UNSUPPORTED/NOT_EVALUATED와 빈 histogram 안내 표시 확인.
  실제 측정이 없으므로 정상 histogram/time-series 그래프 렌더링 PASS로 보지 않는다.
- 초기 브라우저 JavaScript error 조회에서 오류 없음.
- Automotive 실행 중 `/etc/bashrc: BASHRCSOURCED: unbound variable` 경고가
  관측됐지만 S01–S06 명령은 모두 exit 0이었다. 경고 없는 실행으로 주장하지 않는다.
- PFDI의 stub firmware 안내 및 `expirations coalesced into one run` 경고가
  관측됐다. PFDI 앱 실행/provision PASS를 실제 하드웨어 진단·주기 보장으로 해석하지 않는다.

## 증거 위치

이번 Dashboard 세션:
`build/autosd/dashboard/20260929-223602-c36fd207/`

각 job 디렉터리의 `job.json`, `console.log`, `guest/`의 JSON과 archive를 보존했다.

| 실행 | Job ID |
| --- | --- |
| Boot | `f8c9c4cbd8604e7f94491243b38ef344` |
| 자동 health | `b142e97340f14ff19c60fd53a404161a` |
| Automotive | `7c4ea0700aeb46efb91938f31f1f7333` |
| RT 묶음 | `37ca6a053e1d422592cf226347104793` |
| Timerlat | `02aa064c19dd4b9d820e7302293e36f6` |
| OS noise | `74a24711984e473bb1b41692c4545158` |
| Mixed criticality | `b1a6233d8a48418b8331d66074797008` |
| Watchdog WD01–03 | `1c93ca763868416cb35ddae7caedad67` |
| R06 개별 실행 | `01d3e532ff16407b8ca942b1c8acf592` |
| WD04 | `a9ff9f59dace43aab20569ce06d639ac` |
| MHU 장애 / 전체 reset | `56c18451e2904c7f971ad56881ae514c` |
| Pause/Resume 실증 검증 | `10792f7a56e74d659a2695256428f106` |
| 최종 자동 health | `189924527af54a7ab26cc24c5d017672` |
| Power off | `9fab088cc4ab4a56b51a9632a3c9cb10` |

보조 관측 증거:
`build/autosd/dashboard-validation-20260929/boot.json`, `observation.json`,
`dashboard-running.png`.
최종 관측은 같은 경로의 `final-observation/observation.json`,
결과 표 화면은 `final-results.png`에 보존했다.

QEMU/AP-only backend, OTA/rollback, SELinux 정책·iceoryx2 별도 데모는 이번
QBox full Dashboard 검증 범위에 포함하지 않는다.
