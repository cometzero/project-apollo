# AutoSD Mixed criticality / Watchdog 데모 Quick Guide

QBox full-system(RSE, SI CL0, SI CL1, AP)을 우선 대상으로 하는 기능 데모다.
AutoSD root의 safety monitor·BlueChi·Podman, CPU 1의 ADAS 컨테이너,
CPU 2–3의 QM partition·앱·nested container를 실제 실행 상태로 관측한다.
여기서 `ASIL-B`는 개발용 slice 이름이다. **동일 Linux 커널을 공유하는
컨테이너 구성으로, ASIL 인증·FFI 증명·물리적 latency/FTTI 보장이 아니다.**

## 1. 시나리오와 판정

| ID / 화면 이름 | 실행·관측 | PASS에 필요한 증거 | 영향 |
| --- | --- | --- | --- |
| MC01 Partition 자원 분리 | root monitor, ADAS, QM 서비스 및 실제 프로세스/cgroup 검사 | monitor CPU 0, ADAS CPU 1, QM CPU 2–3; effective cpuset; ADAS memory limit; 서로 다른 PID namespace; SELinux Enforcing/프로세스 label; ADAS heartbeat 진행 | 읽기 전용 |
| MC02 QM 부하 격리 | QM 내부 UUID transient unit에 제한된 CPU busy loop | 실제 load cpuset 2–3, CPU 사용량 증가, ADAS PID·CPU 배치 유지, 관측 중 heartbeat 진행과 monitor HEALTHY, load 정리 성공 | QM CPU 부하 |
| MC03 QM 장애 격리 | nested `apollo-qm-container`를 KILL하고 systemd 재생성 대기 | 이전/새 container ID 상이, 새 컨테이너 health, 동시에 ADAS heartbeat 진행·PID 불변, 서비스 복구 | QM 컨테이너 재시작 |
| WD01 SBSA 구성 검사 | sysfs와 systemd watchdog 정책 조회 | 조회 결과·identity·state·nowayout·정책을 수집 | 장치를 열지 않음; reset 검증 아님 |
| WD02 SBSA keepalive | timeout 20초, 30초 동안 ioctl feeding | SET/GETTIMEOUT, KEEPALIVE/GETTIMELEFT, 정상 disarm 및 inactive 확인 | AP watchdog 일시 활성화 |
| WD03 서비스 watchdog | 전용 transient notify 서비스가 급식 후 알림 중단 | systemd `Result=watchdog`, 해당 서비스 journal, 소유 unit 정리 | 해당 시험 서비스만 종료; HW reset 아님 |
| WD04 SBSA WS1 reset 및 복구 | fd를 유지하고 feeding 중단; host에서 독립 검증 | WS0 → WS1 → reset-clear, SI0 IRQ 재무장, 새 AP boot ID/epoch와 현 epoch module provision PASS, 앱 health·HIPC 3/3, QBox 프로세스 연속성과 RSE/SI epoch 보존 | **AP 강제 reset, QBox full 전용** |

MC03은 기존 Automotive S03의 단순 컨테이너 재생성 검사에 더해, 장애 주입·복구
명령 실행 중에도 ADAS timestamp와 monitor 상태를 별도 thread로 계속 표본 수집한다.
MC 샘플 주기는 250 ms이고 stale 기준은 기존 `/workload health`와 같은 1초다.
장애 주입 전에 ADAS health와 monitor HEALTHY를 동기 확인한다. monitor timestamp는
기존 최대 probe 10초 + 주기 1초 + 여유 1초인 12초 freshness를 적용하고 실제
timestamp 진행도 요구한다. 오래된 HEALTHY 문자열만으로 통과시키지 않는다.
최대 관측 age는 표본값이며 최악 지연의 상한이나 deadline 보장은 아니다.

MC02는 `CPUQuota=100%`, `MemoryMax=32M`, `TasksMax=4`, `RuntimeMaxSec=30`인
고유 시험 unit을 사용한다. 8초 관측과 실제 CPU accounting을 함께 확인한다.
`CPUWeight`는 동일 계층의 경쟁 sibling cgroup 사이 상대 가중치다.
`CPUWeight=50`을 시스템 전체 CPU의 고정 50%나 예약 대역폭으로 해석하면 안 된다.
특히 이 구성처럼 ADAS/QM의 cpuset이 분리되어 있으면 weight만으로 두 domain의
CPU 시간 비율을 주장할 수 없다. 결과에는 실제 cgroup 경로와 ancestor의
`cpu.max`, `cpu.weight`, `memory.max`, `memory.high`도 남긴다.

WD04는 전체 QBox 프로세스를 종료하고 새로 실행하는 재시작이 아니다.
현재 AP watchdog recovery 정책은 RSE/SI domain을 유지하면서 AP를 복구한다.
따라서 일반 native full-system reboot와 reset 범위가 다르다.

## 2. 준비

1. [전체 실행 가이드](autosd-automotive-demo-guide-ko.md)에 따라 Automotive
   customization과 현재 Apollo BSP 커널/firmware가 포함된 prepared image를 준비한다.
   이 데모 추가만을 위해 기존 prepared image를 다시 설치할 필요는 없다.
   웹서버는 최신 guest helper를 실행별 고유 경로로 업로드한다.
2. SSH 가능한 disposable/private guest만 사용한다. 다른 full-system QBox를 동시에
   실행하지 않는다. 빌드·이미지 설치·다른 장애 시험과도 병행하지 않는다.
3. image 복사본과 로그를 보관할 디스크 여유를 확인한다. 원본 이미지나 이전
   증거를 자동 삭제하는 절차는 없다.
4. 웹서버를 최신 코드로 실행한다. 이미 실행 중이면 VM을 정상 종료한 뒤
   서버를 재시작하고 Power on 한다. 현재 실행 중인 old-code VM에 WD04 trace
   설정만 소급 적용할 수는 없다.

prepared manifest와 정상 종료된 private image 경로를 지정하는 서버 시작 예시
(`PRIVATE_IMAGE.wic`는 실제 사용할 이미지 경로로 바꾼다):

```sh
python3 scripts/autosd_dashboard/server.py \
  --listen 127.0.0.1 --listen 192.168.0.13 --port 8765 \
  --backend qbox-full --allow-private-guest --allow-unauthenticated-lan \
  --manifest build/autosd/demo-minimal-qm-prepared/regular.json \
  --rootfs PRIVATE_IMAGE.wic
```

위 예시는 로그인 없이 내부 네트워크에서 VM 제어를 허용한다. 신뢰할 수 있는
LAN에서만 사용한다. 서버가 이미 포트를 사용 중이면 두 번째 서버를 실행하지 않는다.
웹서버는 launcher와 달리 이미지를 자동 선택하지 않으므로 `--manifest`와
`--rootfs` 두 옵션이 필요하다. 비밀번호·SSH 자격 증명은 로그에 기록하지 않는다.

## 3. 브라우저 권장 실행 순서

1. `http://127.0.0.1:8765/` 또는 `http://192.168.0.13:8765/` 접속.
2. VM이 꺼진 상태에서 backend를 **QBox full**로 선택하고 **Power on**.
   이 경로는 watchdog host 증거용 `--reset-trace`도 설정한다.
3. Feature & Demo의 **1 부팅**, **2 Automotive 상태 검사**가 자동으로
   완료될 때까지 기다린다. RSE/SI CL0/SI CL1/AP 및 현 AP epoch provision이
   PASS여야 한다. SSH 접속이나 login prompt만으로 전체 준비 완료를 판정하지 않는다.
4. **Mixed criticality MC01–MC03** 상위 실행 버튼으로 세 케이스를 순차 실행한다.
   필요한 경우 펼쳐진 **MC01**, **MC02**, **MC03** 하위 버튼으로 독립 실행한다.
5. **Watchdog WD01–WD03** 상위 실행 버튼을 누른다. 이 묶음은 하드웨어
   reset을 포함하지 않지만 WD02의 HW watchdog 활성화와 WD03 시험 서비스 종료는 포함한다.
6. 앞의 결과와 정상 health를 확인한 뒤에만 **WD04 SBSA WS1 reset 및 복구**를
   별도로 선택하고 destructive 확인을 진행한다. WD04는 상위 묶음에 자동 포함되지 않는다.
   QEMU/QBox AP-only backend에서는 WD04를 지원하지 않는다.
7. AP reset 이후 새 부팅 상태와 Automotive health의 자동 갱신을 기다린다.
   Host log의 WS1/복구 결과와 Guest log의 새 boot를 함께 확인한다.

S04/S05 등으로 `FAULT_LATCHED` 상태를 만든 직후 MC를 실행하면 정상 상태
전제 조건이 실패한다. MC가 latch를 임의로 지우지는 않는다. 기존 명시적
S06 운영자 복구를 먼저 수행하고 health를 확인한다.

## 4. 로그·결과 확인

- **Host log**: 선택한 작업의 실제 명령 stdout/stderr, case 이벤트, reset 대기·검증.
- **Guest log**: 고정 UART 및 제공된 서비스별 출력. reset 때는 새 부팅 세션을 확인한다.
- **결과 선택**: 완료된 Mixed criticality 또는 Watchdog 작업을 선택한다.
  기능 결과 표에서 case 상태, heartbeat 표본 수/진행 수/관측 age, CPU 사용량,
  복구 관측값을 확인한다. WD04의 WS0/WS1/reset-clear는 SystemC clock 기반
  timeline으로 제공된다. guest monotonic, host wall time, SystemC 시간은 서로
  같은 clock이라고 가정하지 않는다.

Host 증거 기본 경로는 `build/autosd/dashboard/<session>/<job>/`이다.
UI 작업의 `evidence_path`가 해당 실행의 정확한 경로다.

| 실행 | 주요 원본 |
| --- | --- |
| 공통 | `job.json`, `console.log`; boot job의 `vm/domains.json`, `vm/linux-uart.log`, domain UART 로그 |
| MC | `guest/scenarios.json`, `guest/evidence.tar.gz`; archive 안 `results.json`, `MC01.json` 등, `commands.log`와 `heartbeat_samples` |
| WD01–03 | `scenarios.json`, 각 `WD01/` 등의 `scenario.json` 및 guest 실행 로그; WD03 guest 출력 디렉터리의 `journal.log` |
| WD04 | `scenarios.json`, `watchdog-trace.log`, `si0-reset.log`, `before-boot/`, `baseline/`, `expiry/`, `recovery-boot-*/`, `recovery/` |

reset에 따른 SSH disconnect/timeout 124는 단독으로 PASS가 아니다.
WD04는 reset 전 offset 이후의 host trace, boot ID, 프로세스 starttime, 현 epoch
provision, 앱 및 HIPC를 결합해서 판정한다. 증거가 없거나 정리가 실패하면 FAIL로 남긴다.
watchdog 만료 직전 guest의 `result.json`이 없을 수 있으며 이를 성공으로 대체하지 않는다.

## 5. Guest 직접 실행과 안전한 정리

웹 실행 외에 helper만 복사해 root guest에서 MC를 재현할 수 있다. 매번 새로운
출력 경로를 지정하며 기존 결과를 덮어쓰지 않는다.

```sh
python3 /var/tmp/mixed-criticality-guest.py --case MC01 \
  --allow-disruptive-demo --out /var/tmp/mixed-mc01-run1
python3 /var/tmp/mixed-criticality-guest.py --case MC02 \
  --allow-disruptive-demo --out /var/tmp/mixed-mc02-run1
python3 /var/tmp/mixed-criticality-guest.py --case MC03 \
  --allow-disruptive-demo --out /var/tmp/mixed-mc03-run1
```

MC02는 자신이 이름을 생성한 UUID transient unit만 stop하며 bounded runtime이
최후 방어다. MC03은 시험 전 정상인 QM 컨테이너 서비스만 다시 start/health 확인한다.
다른 서비스나 임의 PID를 kill하지 않는다. 결과가 FAIL이면 cleanup 필드와 현재
서비스 상태를 확인하고 원인을 해결한 뒤 새 출력 경로로 다시 실행한다.

WD02/WD04는 `nowayout=0`, inactive 상태, systemd `RuntimeWatchdogUSec=0`,
다른 owner 부재 및 SBSA action=0을 요구한다. PID 1과 helper를 동시에
watchdog owner로 만들지 않는다. SIGKILL은 disarm/finally를 실행할 수 없으므로
정상 중단 수단으로 사용하지 않는다. WD03은 UUID 시험 서비스만 정리하며
PID 1의 `RuntimeWatchdogSec` 정책을 변경하지 않는다.

직접 watchdog 도구 사용법과 만료 시 보존할 증거는
[Watchdog Guest Quick Guide](autosd-watchdog-guest-ko.md)를 따른다.
WD04 전체 판정은 host 관측이 필요하므로 guest expiry 명령만 실행한 결과를
웹의 WD04 PASS와 동일하게 취급하지 않는다.

## 6. 검증 결과

검증 backend는 `qbox-full`, guest kernel은 `6.18.5-rt3-yocto-preempt-rt`,
AP online CPU는 `0-3`이다. 부팅 job은 `43cb28f41c28444599eb5ec51fa4adb2`이며,
session `build/autosd/dashboard/20260928-082132-67c1d83f/` 아래에 모든 증거를 보관한다.
검증 이미지 복사본은 해당 boot job의 `vm/rootfs.wic`, 실제 firmware/UKI/launch
설정과 module 해시는 `vm/launch.json`, `vm/domains.json`, `vm/modules.json`을 따른다.
최종 도구 source 해시는 `build/autosd/mixed-watchdog-source-20260928.sha256`이다.

| 범위 | 상태 | 증거 |
| --- | --- | --- |
| MC helper host 회귀 | PASS | `pytest -q tests/test_autosd_mixed_criticality.py` — 17 tests |
| Dashboard / MC / WD Python 회귀 | PASS | `build/autosd/mixed-watchdog-unit-tests-20260928.log` — 193 tests |
| UI 회귀 | PASS | `build/autosd/mixed-watchdog-ui-tests-20260928.log` — 33 tests |
| QBox full MC01–MC03 실제 실행 | PASS | session `20260928-082132-67c1d83f`, job `340c4de6039a487793fa0b49dd4741e7` |
| QBox full WD01–WD03 실제 실행 | PASS | 같은 session, job `1abde481589a4e7ab8cf43abad9c3726` |
| QBox full WD04 실제 WS1 복구 | PASS | 같은 session, job `5713780ef6fc4a22b26fdb4602b11ced` |
| 장시간 stress / 물리 timing / ASIL·FFI 인증 | 미검증·범위 밖 | 기능 데모 PASS로 승격하지 않음 |

기존 reset 구현 검증 이력은 [전원·Watchdog 검증 리포트](autosd-power-watchdog-validation-ko.md)에
있다. 기존 이력은 이번 새 웹 시나리오의 실제 실행 결과를 대신하지 않는다.

### 2026-09-28 실제 Mixed criticality 관측

| 시나리오 | ADAS 표본 / 진행 | 최대 heartbeat age | monitor timestamp 진행 | 추가 증거 |
| --- | --- | --- | --- | --- |
| MC01 | 94 / 93 | 0.107946 s | 4 | monitor CPU0, ADAS CPU1, QM CPU2–3 |
| MC02 | 253 / 252 | 0.113609 s | 11 | QM load CPU time 24.70143 s, cpuset2–3, 소유 load 정리 PASS |
| MC03 | 258 / 257 | 0.104756 s | 10 | nested container 새 ID, ADAS PID 유지, QM 복구 PASS |

MC 결과는 `guest/scenarios.json`과 `guest/evidence.tar.gz`에 보존했다.
브라우저에서 완료 결과의 자동 선택과 22개 기능 결과 행, 실제 Host 명령 출력 및
별도 Guest UART 출력을 확인했다. 화면 증거:
`build/autosd/mixed-watchdog-ui-mc-pass-20260928.png`.

WD02는 keepalive 표본 6개 모두 feeding 후 `timeleft=19s`를 관측했고 정상
disarm했다. WD03은 4회 알림 후 feeding을 중단하여 systemd가 5초 watchdog
timeout과 `Result=watchdog`를 보고했으며, 소유 transient unit 정리도 PASS했다.
의도적으로 만든 서비스 timeout warning은 이 시나리오의 기대 검출 증거다.
reset 후 읽기 전용 WD01을 job `be83ee87d821455e9877ad0a8d03a761`로 재실행해
`state=inactive`, `nowayout=0`, `RuntimeWatchdogUSec=0`,
`RebootWatchdogUSec=10min`을 확인했다. RuntimeWatchdog 비활성화와 reboot 단계의
watchdog 정책은 서로 다른 설정이며, 이 데모는 이를 임의로 변경하지 않는다.

### 2026-09-28 실제 WS1 복구 관측

- AP boot ID: `98d391b2-45fd-48aa-949b-e601e843708f` →
  `86e4c996-453e-44d8-83f5-3b3d30e22f8d`.
- AP epoch 1 → 2, RSE/SI CL0/SI CL1 epoch 1 유지.
- QBox PID 910596/910650 및 starttime 유지, 별도 QBox 재실행 없음.
- 새 epoch module provision PASS, Automotive health PASS, HIPC ICMP 3/3 PASS,
  시험용 VLAN profile 정리 PASS. 후속 자동 health job
  `72da475041a246a9a5ded43847b31f63`도 PASS.
- SI0 IRQ 321: enabled=1 / pending=0 / recovery=0, rearm attempt=1 PASS.
- 만료 SSH의 종료 코드 124는 부수적인 연결 끊김 기록이며 판정 근거가 아니다.

| 실제 이벤트 | SystemC 원본 시각 | 단위 |
| --- | ---: | --- |
| WS0 | 699504626280 | ns |
| WS1 | 709504626280 | ns |
| reset-clear | 713034182172001 | ps |

대시보드의 기능 결과 표와 위 이벤트 표를 실제 브라우저에서 확인했다.
`build/autosd/mixed-watchdog-ui-wd04-pass-20260928.png`에 화면을 보존했다.
이 실행에서는 QEMU/AP-only 경로를 새로 검증하지 않았다. WD04는 의도적으로
QBox full 외 backend에서 차단한다. PFDI는 stub firmware 기반 기능 데모이며
실제 하드웨어 진단 성능을 검증한 것은 아니다.

최종 Power off job `5b120d69b08249d6b815e653d719b3d3`은 PASS
(`vm_returncode=0`, UART `Power down` 확인)였다. 이후 웹서버를 위 검증 이미지
복사본을 사용하는 QBox full 설정으로 재시작했다. VM은 종료 상태이며 다음
Power on에서 보존된 이미지로 새 실행 복사본을 만든다. `127.0.0.1:8765`와
`192.168.0.13:8765` 모두 HTTP 200, 로그인 없음, 기존 MC/WD 결과 조회와
WD04 이벤트 표 표시를 재확인했다. 서버 로그는
`build/autosd/mixed-watchdog-dashboard-server-20260928.log`다.
브라우저 polling 이후 펼친 관측값이 유지되는 것도 검증했으며 page error는 없었다.

검증 공간 확보를 위해 이전 시험의 미사용
`build/qbox-apollo-qvp/autosd-watchdog-async-20260928/rootfs.wic`를
`/tmp/apollo-autosd-watchdog-archive.Y23fKU/async-rootfs.wic`로 옮기고 원래 경로에
symlink를 유지했다. 이동 전후 SHA256은
`6c99163a463019729a5cc4a1f5195f4bf548eafd8cde1ac01d649c2018e7f4f9`로 동일하다.
삭제는 하지 않았지만 `/tmp`는 장기 보관 경로가 아니므로 필요 시 별도 보관한다.

## 7. 구현 및 AutoSD 문서 근거

- [MC guest helper](../autosd/customization/mixed-criticality-guest.py)
- [웹 시나리오/제어](../scripts/autosd_dashboard/server.py),
  [WD host 검증](../scripts/autosd_dashboard/watchdog_scenarios.py)
- [SBSA guest helper](../scripts/autosd_demo/watchdog_guest.py),
  [서비스 watchdog 데모](../scripts/autosd_demo/watchdog_process_demo.py)
- AutoSD [Mixed criticality concepts and design](../autosd/sig-docs/docs/features-and-concepts/con_mixed-criticality.md):
  단일 OS 컨테이너 기반 isolation, QM의 독립 systemd/Podman 및 SELinux 구성.
- AutoSD [Configuring Linux schedulers](../autosd/sig-docs/docs/building/configuring_scheduler_priority_qm.md):
  cgroup 계층의 상대 CPUWeight 및 QM scheduling.
- AutoSD [Watchdogs](../autosd/sig-docs/docs/features-and-concepts/watchdogs.md):
  서비스·시스템 watchdog 개념. 문서의 i6300esb 예제를 Apollo SBSA MMIO/WOR
  규칙과 동일하다고 가정하지 않는다.
- AutoSD [FuSa disclaimer](../autosd/sig-docs/docs/fusa_disclaimer.md):
  개발용 배포판/문서와 safety-qualified 제품 요건의 경계.
