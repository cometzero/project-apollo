# AutoSD Simulation Console — 웹 실행 및 모니터링

## 목적과 지원 범위

로컬 브라우저에서 AutoSD private regular VM을 부팅하고 Automotive/RT 데모,
로그, 결과 표·latency 그래프, guest CPU·subsystem 상태를 확인한다.
기존 [Automotive Quick Guide](autosd-automotive-demo-guide-ko.md)와
[RT Quick Guide](autosd-preempt-rt-guide-ko.md)의 실행 도구를 연결한다.
Mixed criticality MC01–MC03와 Watchdog WD01–WD04의 실행 순서·판정·안전 제한은
[Mixed criticality / Watchdog Quick Guide](autosd-mixed-watchdog-demo-ko.md)를 따른다.
임의 shell 명령을 받는 웹 terminal이 아니며 허용된 작업만 실행한다.

| 기능 | 데이터/실행 경로 | 제한 |
| --- | --- | --- |
| 부팅·종료 | `run_qemu_linux.sh`, `run_qbox_linux.sh`, `run_qbox_autosd.sh`, private disk copy | 서버가 소유한 VM만 제어 |
| 정상 상태 | 기존 `check-guest.sh` | BlueChi/root/ADAS/QM/monitor 검사 |
| Automotive 데모 | `demo-guest.py` S01–S06 | 장애 주입·서비스 재시작·복구 포함, 확인 필요 |
| RT 측정 | R01–R06 runner | SCHED_OTHER/FIFO/QM 부하/경합/주입/cyclictest |
| latency trace | timerlat/osnoise | 수집 PASS와 임계값 EXCEEDED 분리 |
| Mixed criticality | MC01 배치 / MC02 QM 부하 / MC03 QM 장애·복구 | 공유 커널 기능 관측; ASIL/FFI 인증 아님 |
| Watchdog | WD01 검사 / WD02 keepalive / WD03 서비스 검출 / WD04 WS1 복구 | WD04는 QBox full 전용, 별도 동의; 그룹 실행에서 제외 |
| CPU instance | guest `/proc/stat` 증분 | 첫 sample은 미계산; host CPU 수치가 아님 |
| subsystem | systemd 서비스, 실제 container PID cgroup, safety JSON | CPU cores·memory·cpuset; 인증 안전 모니터 아님 |
| 과거 결과 | 기존 검증 JSON과 새 job evidence | 측정일·출처를 확인; 현재 실행과 혼동 금지 |

Linux 전용 QEMU/QBox AP direct에는 RSE/Safety Island firmware telemetry가 없으므로 해당 항목은
UNSUPPORTED다. QBox full-system의 firmware 부팅과 로그는
[full-system Quick Guide](autosd-fullsystem-dashboard-ko.md)를 따른다.
native OTA/rollback·IPC/iceoryx2·SELinux 정책 데모는
이미지/프로비저닝 조건이 다르므로 이 regular VM 실행 adapter와 구분한다.
그 항목이 표시되더라도 실행 지원으로 해석하지 않는다.

## Quick Guide

04(PREEMPT_RT)·05(Timerlat)·06(OS noise)는 완료 시 결과 표와 최대 지연 그래프를
자동으로 선택한다. Feature의 `결과 보기`로도 이동할 수 있다. 측정 PASS와 지연 기준
판정은 별도이며, 과거 결과에는 당시 기준을 표시한다.
TCG용 새 관찰 기준과 해석은 [RT 결과 가이드](autosd-rt-dashboard-results-ko.md)를 참고한다.

상단 **System control**은 이 대시보드가 소유한 AutoSD VM만 제어한다.
빌드 호스트 전원 제어가 아니다. QBox full-system에서는 정상 guest 종료 후
소유한 전체 도메인 프로세스를 정리한다. QBox full은 native Reboot를 지원하지만,
Pause/Resume은 지원하지 않는다.
기본 백엔드는 `--backend qemu`다. `--backend qbox`로 AP domain 직접 부팅과
동일한 Automotive/RT 시나리오를 사용할 수 있다. 시작 명령과 검증 범위는
[QBox AP domain Quick Guide](autosd-qbox-dashboard-ko.md)를 참고한다.
Reboot는 QEMU와 QBox full에서 지원하며, QBox AP-only에서는 비활성화된다.
Pause/Resume은 QEMU 전용이다. QBox full Reboot는 새 boot ID뿐 아니라 최신
firmware boot epoch와 해당 epoch의 provisioning PASS까지 최대 900초 확인한다.
QBox full Power off는 최대 180초 기다리며 timeout에도 강제 종료하지 않는다.

| 버튼 | 동작 / 완료 확인 |
| --- | --- |
| Power on | 새 Feature 주기 시작 → 1번 guest 부팅 확인 → 2번 Automotive health 자동 검사 |
| Power off | Feature 상태 즉시 초기화; guest `systemctl poweroff`, VM exit와 UART Power down 확인 |
| Reboot | Feature 상태 즉시 초기화 → 1번 새 boot ID/SSH 확인 → 2번 health 자동 검사 |
| Pause | QEMU `stop` 후 `info status`로 paused 확인 |
| Resume | QEMU `cont` 후 running 확인; 다음 telemetry 표본 대기 |

데모/제어 작업 실행 중에는 중복 제어를 차단한다. Pause 중에는 guest SSH 작업과
모니터링도 중단되며 마지막 표본은 현재 측정값이 아니다. Power off/Reboot를 하려면
먼저 Resume한다. 정상 Power off 후 다음 Power on은 직전 디스크의 복사본을 사용해
변경 사항을 보존한다. 서버를 재시작할 경우 보존할 최신 디스크를 `--rootfs`로 지정한다.
Reboot PASS는 OS 재부팅 확인이지 Automotive health PASS가 아니다.
Feature 1번 PASS는 guest 연결과 boot ID 확인이며, Feature 2번 PASS가 실제
Automotive 정상 상태 검사 결과다. 부팅 중 2번은 QUEUED로 표시되고 이후 자동 실행된다.
서비스 초기화가 늦으면 제한 시간 안에서 read-only health 검사를 재시도한다.
장애 주입/복구 및 RT 시나리오는 자동 실행하지 않는다. 자동 초기 검사가 끝나면
개별 시나리오를 실행할 수 있다. 전원 제어 요청이 거부되면 상태를 초기화하지 않는다.
이전 Feature 결과는 현재 카드에서 제거되지만 Host log의 이전 실행 목록에는 남는다.
각 제어 작업도 Host log에 기록된다. Pause는 launcher의 7200초 wall-clock
실행 제한을 연장하지 않는다.

workspace root에서 실행한다. Python 3와 기존 guest helper의 `paramiko`가 필요하다.
별도 npm build나 외부 CDN은 사용하지 않는다.

```sh
# 과거 결과 열람만: VM 제어 비활성
python3 scripts/autosd_dashboard/server.py
```

브라우저에서 `http://127.0.0.1:8765`를 연다.
빌드 호스트가 원격이면 로컬 PC에서 `ssh -N -L 8765:127.0.0.1:8765 user@build-host`로
같은 포트를 전달한 뒤 접속한다. HTTP Host 검사 때문에 전달 포트 번호도 동일하게 쓴다.
실제 실행은 RT Quick Guide로 준비하고 정상 종료한 regular customization disk를 지정한다.
아래 경로는 이 workspace에서 검증에 사용한 산출물이다. 원본 디스크가 사용 중이면
먼저 해당 VM을 정상 종료한다. 서버는 launcher가 만든 새 복사본을 사용한다.

```sh
python3 scripts/autosd_dashboard/server.py \
  --allow-private-guest \
  --manifest build/autosd/demo-minimal-qm-prepared/regular.json \
  --rootfs build/autosd/automotive-rt-measure/rootfs.wic
```

1. 부팅 작업을 실행하고 UART 로그와 guest telemetry가 ONLINE이 되는지 확인한다.
2. 정상 상태 검사로 준비 여부를 확인한다. TCP listener만으로 부팅 PASS라 하지 않는다.
3. Automotive 또는 RT/trace 데모를 선택한다. 장애 주입 확인창을 읽고 실행한다.
4. job 로그와 결과 표를 확인한다. RT 그래프에서 synthetic 주입은 성능 비교에서 제외한다.
5. 종료 작업으로 guest를 정상 poweroff한 뒤 부팅 job 종료를 확인한다.

대시보드는 CPU·subsystem·결과·로그를 한 페이지에 표시한다. **작업 & 실행 로그**
영역에는 **Host log와 Guest log를 서로 독립된 패널**로 표시한다.
Host log는 시나리오별 명령·SSH 출력이며 작업 드롭다운에서 선택한다.
Guest log는 기본 UART 외에 Root/Safety/BlueChi/ADAS/QM/QM app/QM container를
선택할 수 있으며 Host 작업 선택과 무관하게 갱신된다. **새 창에서 보기**를 누르면
`/?view=guest`에서 Guest 로그만 독립적으로 표시한다. 서비스별 로그는 SSH 준비 후
15초 캐시로 수집하며, stdout이 조용한 앱은 명시적으로 heartbeat snapshot을 표시한다.
Reboot 또는 Power off 후 Power on을 하면 새 세션으로 전환되고 이전 실행은
드롭다운의 이전 세션 이력에서만 조회한다. 원본 로그 파일은 삭제하지 않는다.
Feature & Demo에서 실행하면 Host log의 해당 작업을 선택하며 대시보드를 숨기지 않는다.
각 번호 아래에는 최근
작업 상태, 경과 시간, 진행 설명, 별도의 **로그 보기** 버튼이 표시된다.
다른 작업 실행으로 시작 버튼이 비활성화돼도 로그는 볼 수 있다.
**로그 보기**를 누르면 로그 영역으로 스크롤하면서 Host log의 해당 작업을 선택한다.
기본 부팅 포함 여부와 상세 검증은 [기본 부팅 및 Guest 로그](autosd-default-boot-guest-logs-ko.md)를 참조한다.
새 Automotive 실행 로그에는 `[host:ssh]` 접속·종료, upload/download,
`[guest:Sxx-precheck]` 사전 검사, `[guest:Sxx-...]` 실행 시작·종료 코드와
guest stdout/stderr가 실시간으로 기록된다. `+` 접두사는 실제 실행한 shell
명령/검사이며, S04의 대기 루프 및 journal 출력도 포함한다.
상세 출력은 guest 개별 `.log`와 웹 작업 로그에 동시에 저장된다.
수정 전 작업의 웹 로그는 소급해서 바뀌지 않는다. 해당 작업의 원본 evidence
archive에는 당시 guest 상세 로그가 있으므로 이를 내려받아 확인한다.
상태는 약 3초마다 갱신되며 완료된 작업의 경과 시간은 고정된다.
Automotive S01–S06은 로그에서 실제 수신한 단계 결과 수를 표시한다.
RT 도구처럼 중간 결과를 제공하지 않는 작업은 실행 구간 설명을 표시하며,
추정 진행률(%)을 만들지 않는다. 부팅 작업은 VM이 살아 있는 동안 실행 중으로 남는다.

Automotive와 PREEMPT_RT 항목의 **시나리오별 실행**을 펼치면 각각 S01–S06,
R01–R06을 독립적으로 실행할 수 있다. 상위 버튼은 기존 전체 실행이다.
S01은 현재 guest 상태를 검사하며 VM을 새로 부팅하는 작업이 아니다.
S02/S03/S04는 정상 상태에서, S05/S06은 FAULT_LATCHED 상태에서 실행한다.
선행 상태가 맞지 않으면 BLOCKED로 남기며 필요한 시나리오를 자동 실행하지 않는다.
S04 단독 실행은 장애 latch를 남긴다. 검사 후 필요하면 S05를 실행하고,
S06으로 명시적으로 복구한다. S02–S06은 실행 확인이 필요하다.
RT 개별 실행은 해당 항목만 측정하지만 공통 사전/사후 health 검사는 수행한다.
R03/R04의 부하는 해당 실행에서만 생성·정리하며, R06은 cyclictest만 측정한다.

RT/trace 실행 중 주기적 SSH 모니터링을 일시 중단한다. 화면의 마지막 값은
실시간 값이 아니며 PAUSED 표시와 sample 시각을 확인한다. 모니터링 자체도 VM에
부하를 더하므로 모니터링 활성 실험과 비활성 실험을 같은 조건으로 비교하지 않는다.
VM 재부팅·counter reset 후 첫 CPU 값은 0이 아니라 미계산이다.
서비스 cgroup과 container cgroup은 계층이 겹칠 수 있어 CPU/memory를 합산하지 않는다.
`cpu_cores=1.0`은 관측 구간에 CPU 한 개 분량을 사용했다는 뜻이며 전체 VM 100%가 아니다.

## 안전 및 운영

- 기본은 loopback 전용 개발 도구다. 아래 명시적 LAN 설정 외에는 개방하지 않으며,
  인터넷에 공개하지 않는다.
- private guest의 root/password는 기존 regular 개발 경로 전용이다. 키 기반 native
  이미지에 비밀번호를 추가하거나 OSTree를 unlock하지 않는다.
- HTTP 요청은 Host/Origin 및 CSRF token을 검사한다. OS 계정 접근 제어를 대신하지 않는다.
- 실행을 직렬화한다. 외부 BitBake/다른 VM/benchmark 동시 실행은 운영자가 피해야 한다.
- 안전 monitor fault를 일반 health 버튼이 자동 해제하지 않는다. Automotive suite의
  명시적인 장애/복구 시나리오만 복구를 수행한다.
- 브라우저를 닫아도 서버 작업은 계속된다. 서버 종료 전에 웹에서 VM을 종료한다.
- generated 증거는 `build/autosd/` 아래에 보존한다. 초기 실패도 지우지 않는다.

실행별 증거는 `build/autosd/dashboard/<session>/<job-id>/`에 저장한다.
`job.json`, `console.log`, `guest/`의 JSON·원본 archive를 보존하며 웹에서도
선택한 결과의 원본 증거를 다운로드할 수 있다. `telemetry.jsonl`은 session 단위로
최대 10,000 samples를 저장하고 웹에는 최근 120개 중 CPU 차트 60개를 표시한다.
서버 재시작 후 이전 job 로그·결과는 읽을 수 있지만 이전 프로세스 제어권은
승계하지 않는다. 미완료 job은 `ORPHANED_NOT_MANAGED`로 표시하므로 서버를 종료하기
전에 반드시 VM을 정상 종료한다. 종료 후 부팅 job의 `BOOT_PROCESS_COMPLETED`는
프로세스 종료 상태이지 Automotive health PASS가 아니다.
마지막 유효 CPU/subsystem 표본과 최근 history도 복원하며 OFFLINE/STALE 및 원래
수집 시각을 표시한다. 이는 이전 실행 기록이고 새 실행의 실시간 측정이 아니다.

TCG의 관찰 latency는 실제 하드웨어 timing, ASIL-B, FFI, FTTI 또는 WCET 보장이 아니다.

## 선택: localhost와 내부망 직접 접속

실행 디스크가 누적될 때는 [실행 이미지 정리 가이드](autosd-disk-cleanup-20260927-ko.md)의
`scripts/cleanup_run_images.py`를 사용한다. 기본은 dry-run이며 로그는 삭제하지 않는다.

현재 요청된 구성은 **로그인 없음**이다. 다음과 같이 실행한다.

```sh
python3 scripts/autosd_dashboard/server.py \
  --listen 127.0.0.1 --listen 192.168.0.13 \
  --allow-unauthenticated-lan --allow-private-guest \
  --manifest build/autosd/demo-minimal-qm-prepared/regular.json \
  --rootfs build/autosd/automotive-rt-measure/rootfs.wic
```

`http://127.0.0.1:8765`와 `http://192.168.0.13:8765`에서 로그인 없이 접속한다.
이 모드에서는 해당 내부망에 접근 가능한 사용자가 VM 제어·장애 주입도 수행할 수 있다.
Host/Origin 및 CSRF 검사는 유지하지만 사용자 인증을 대신하지 않는다.

로그인이 필요한 환경에서는 아래의 선택적 인증 구성을 사용한다.

```sh
python3 scripts/autosd_dashboard/server.py \
  --listen 127.0.0.1 --listen 192.168.0.13 \
  --password-file build/autosd/dashboard-access.password \
  --allow-private-guest \
  --manifest build/autosd/demo-minimal-qm-prepared/regular.json \
  --rootfs build/autosd/automotive-rt-measure/rootfs.wic
```

두 주소 모두 포트 8765에서 접속할 수 있다. 로그인 사용자 이름은 `autosd`,
비밀번호는 `build/autosd/dashboard-access.password`의 내용이다. 파일이 없으면
서버가 무작위 비밀번호를 한 번 생성하며 현재 OS 사용자 전용 0600 권한을 요구한다.
재시작 때 기존 비밀번호를 유지한다. 비밀번호 파일을 Git에 추가하거나 공유하지 않는다.

LAN listen에는 비밀번호 파일 또는 명시적인 `--allow-unauthenticated-lan` 선택이 필요하다.
비밀번호 파일을 선택한 경우 인증은 HTML/API/로그/다운로드 모두에 적용되며
기존 Host/Origin 및 CSRF 검사는 유지된다. `0.0.0.0` 대신 정확한 interface IP를
명시하므로 Docker bridge 등 다른 주소에는 서버를 노출하지 않는다.
이 HTTP Basic 로그인은 **전송 암호화를 제공하지 않는다**. 신뢰하는 내부망에서만
사용하고, 그렇지 않으면 HTTPS reverse proxy 또는 SSH tunnel을 사용한다.
`127.0.0.1`은 접속하는 PC 자신을 뜻하므로 원격 PC에서는 `192.168.0.13`을 사용한다.
