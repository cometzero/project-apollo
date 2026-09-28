# AutoSD / Apollo QVP QBox full-system 실행 가이드

## 실행 대상

대시보드 System control의 실행 대상에서 다음 세 가지를 선택한다.
VM 또는 작업이 실행 중이면 선택할 수 없다. 먼저 정상 Power off를 완료한다.

| 선택 | 실제 실행 범위 |
| --- | --- |
| QEMU TCG | standalone Apollo AP Linux |
| QBox AP only | AP 직접 Linux 부팅, 다른 도메인 mock |
| QBox full system | RSE TF-M, SI CL0 SCP, SI CL1 Zephyr, AP TF-A/OP-TEE/U-Boot/UKIBoot/AutoSD |

full-system은 네 도메인의 필수 로그, AP SSH/boot ID, full-system 모듈 배포를
확인한 뒤 Feature 1을 PASS 처리한다. Feature 2 Automotive health는 별도 자동 검사다.
SI CL1의 `RPMSG Endpoint: ATTACHED`까지 확인하며, AP 로그인만으로 full PASS라 하지 않는다.
이는 firmware 부팅 통합 검사다. 전체 하드웨어 qualification, 물리 타이밍, ASIL 인증,
Secure Boot 인증서 정책, OTA/rollback 검증을 의미하지 않는다.

## Quick Guide

1. `./yocto_build.sh --bsp`로 `apollo-qvp` BSP를 준비한다. 기존 정상 빌드가 있으면
   동일 deploy의 firmware/UKI/DTB/modules를 사용할 수 있다.
2. [Automotive Quick Guide](autosd-automotive-demo-guide-ko.md)에 따라 AutoSD regular
   customization 디스크와 manifest를 준비한다. 마지막 정상 종료 디스크를 보존한다.
3. 최초 full-system 전환 전에는 QEMU 또는 QBox AP-only로 준비 디스크를 부팅하고
   아래 payload 준비를 수행한다. SI CL0는 AP 전원 인가 후 PFDI 응답을 감시하므로
   full-system 로그인 뒤 처음 설치하면 감시 제한 시간보다 늦을 수 있다.

```sh
python3 scripts/run/autosd_fullsystem_modules.py \
  --port 2244 --build-dir build --prepare-only \
  --out build/autosd/fullsystem-payload-prepare
```

   이 단계는 설치/enable만 수행한다. PFDI 진단 성공으로 간주하지 않는다.
   출력 디렉터리는 새 경로여야 하며 SSH port는 실행 중인 private VM과 일치해야 한다.
   정상 Power off 후 같은 서버에서 `QBox full system`을 선택하면 보존된 디스크를 사용한다.
   서버를 재시작할 경우 `--rootfs`에 방금 준비하고 정상 종료한 디스크를 지정한다.

```sh
python3 scripts/autosd_dashboard/server.py \
  --backend qbox-full \
  --listen 127.0.0.1 --listen 192.168.0.13 \
  --allow-unauthenticated-lan --allow-private-guest \
  --manifest build/autosd/demo-minimal-qm-prepared/regular.json \
  --rootfs build/autosd/dashboard/20260927-232504-1f3664df/38bbd532590b449fa9c11b384ba626a4/vm/rootfs.wic
```

4. `http://192.168.0.13:8765/` 또는 localhost에서 `QBox full system`을 선택하고 Power on한다.
5. RSE/SI CL0/SI CL1/AP 카드와 Feature 1·2를 확인한다. readiness 제한은 900초다.
6. Automotive S01–S06, RT R01–R06, Timerlat, OS noise를 실행하고 표/차트를 확인한다.
7. Guest 로그 선택에서 RSE, SI CL0, SI CL1 또는 AP UART/AutoSD 서비스 로그를 확인한다.
8. 정상 Power off 뒤 다른 실행 대상을 선택하거나 Power on한다. QBox full의 native
   Reboot는 새 guest boot ID와 현재 firmware epoch/모듈 provisioning PASS를 확인한다
   (최대 900초). QBox AP-only의 Reboot와 모든 QBox의 Pause/Resume은 비활성화한다.
   full-system Power off는 강제 종료 없이 최대 180초 기다린다.

### 독립 CLI: tmux TUI

준비된 이 workspace에서는 인자 없이 실행할 수 있다.

```sh
./run_qbox_autosd.sh
./run_qbox_autosd.sh --dry-run  # 자동 선택값만 확인, 부팅/파일 변경 없음
```

기본값은 workspace 기준 `build/autosd/demo-minimal-qm-prepared/regular.json`,
`build/tmp_baremetal/deploy/images/apollo-qvp`의 BSP UKI/firmware,
SSH 2244, timeout 7200초, tmux TUI, timestamp 출력 경로/세션이다.
기본 manifest를 사용하는 경우 같은 manifest의 full-system 부팅·모듈 배포 PASS와
정상 Power off 증거가 모두 있는 실행 중 가장 최근 종료된 private disk를 선택한다.
검색 범위는 `build/autosd/dashboard/*/*/vm/`와 `build/qbox-apollo-qvp/*/`다.
실행 중이거나 실패한 기록은 선택하지 않는다. 적합한 종료 기록이 없으면 manifest의
rootfs를 사용하며, 최초 이미지에는 앞 절의 full-system payload 준비가 필요하다.
선택한 입력은 시작 시 출력하고 `launch.json`에 남긴다.
`--autosd`, `--rootfs`, `--build-dir`, `--deploy-dir`, `--uki`, `--out-dir`,
`--session`, `--ssh-port`, `--timeout`으로 명시한 값이 우선한다.
명시적 `--autosd`는 자동 이력 선택을 하지 않고 해당 manifest의 rootfs를 사용한다
(`--rootfs`를 함께 지정하면 그 디스크 사용). 기본 이미지가 없으면 다운로드나
임의 디스크 선택 대신 준비/옵션 지정 안내와 함께 중단한다.
비대화형 환경에서는 `--no-attach`를 사용한다. 터미널 없이 기본 실행하면
세션 생성은 가능하지만 attach는 실패하며, 생성된 세션은 출력된 접속 명령으로 연결한다.

먼저 대시보드의 full-system VM을 정상 Power off한다. 기본 CLI는
`run_qbox_yocto.sh`와 같은 tmux TUI를 연다. AutoSD는 AP domain에서 실행하고,
RSE는 TF-M, SI CL0는 SCP, SI CL1은 Zephyr firmware를 함께 실행한다.

```sh
./run_qbox_autosd.sh \
  --autosd build/autosd/demo-minimal-qm-prepared/regular.json \
  --rootfs PATH_TO_STOPPED_AUTOSD_DISK \
  --out-dir build/autosd/my-full-system \
  --session autosd-full --ssh-port 2244 --timeout 7200
```

AP 콘솔이 상단의 주요 영역을 차지하고, 오른쪽에 RSE/SI CL0/SI CL1/Secure
콘솔, 하단에 QBox platform 로그와 host 셸을 표시한다. 기존 UART 입력 경로도 유지한다.
`Ctrl-b d`는 detach이며 VM은 계속 실행된다. 다시 접속하려면
`tmux attach-session -t autosd-full`을 사용한다. `--no-attach`는 세션만 생성한다.
`--out-dir`을 생략하면 `build/qbox-apollo-qvp/autosd-full-<timestamp>-<pid>/`,
`--session`을 생략하면 고유한 `autosd-full-*` 세션을 생성한다.
AutoSD supervisor는 detach 뒤에도 모듈 배포·도메인 판정을 계속하며
`autosd-supervisor.log`, `supervisor.json`, `domains.json`에 증거를 남긴다.
정상 종료는 AP guest의 `systemctl poweroff`를 사용한다. F12는 기존 TUI와 같은
소유 QBox/세션 강제 정리이므로 guest 정상 종료와 구분한다.

Guest 전원 제어 명령은 다음과 같다. 종료 명령은 필요한 하나만 실행한다.

| Guest 명령 | 동작 |
|---|---|
| `systemctl reboot --no-block` | 같은 QBox 프로세스 안에서 firmware/OS 재부팅 |
| `systemctl poweroff --no-block` | guest 정상 종료 후 launcher가 소유 실행 정리 |
| `shutdown -h now` | systemd shutdown 명령 경로 |
| `shutdown -r now` | systemd의 native 재부팅 요청 경로 |

명령은 Host가 아닌 **AP AutoSD guest의 root shell**에서 실행한다.
재부팅 직후 SSH 단절은 예상되지만, 이것만으로 성공을 판정하지 않는다.
새 boot ID와 현재 firmware epoch의 RSE/SI CL0/SI CL1/AP 및 provisioning PASS를
확인한 뒤 시나리오를 실행한다. Power off는 UART `reboot: Power down`과 launcher의
소유 프로세스 정리까지 확인한다. `reboot -f`, `poweroff -f`, F12는 정상 종료 시험을
대체하지 않는다.

SBSA watchdog은 기본 비활성이며 데모를 자동 실행하지 않는다.
명시적 만료 시험은 `--reset-trace`로 부팅하고
[Watchdog Guest Quick Guide](autosd-watchdog-guest-ko.md)를 따른다.
지원 범위와 실제 PASS/FAIL 증거는
[전원·watchdog 검증 보고서](autosd-power-watchdog-validation-ko.md)에 구분한다.

watchdog 증거를 수집할 새 full-system 실행은 기존 VM을 정상 종료한 뒤 시작한다.

```sh
./run_qbox_autosd.sh --reset-trace
```

`--reset-trace`는 reset 경로 로그만 추가하며 watchdog을 자동 활성화하지 않는다.
Guest에서는 먼저 `/usr/libexec/apollo/watchdog-guest.py inspect`를 `python3`로
실행한다. helper를 bundle에 포함하려면 customization 준비 시 `--watchdog-tools`가
필요하다. systemd manager 소유 시험과 helper의 keepalive/expiry는 동시에 실행하지 않는다.

자동화/대시보드용 파일 로그 모드는 `--headless`를 추가한다. 이 경로에서는
tmux를 생성하지 않으며 기존 대시보드의 프로세스 소유권과 종료 처리를 유지한다.

출력 디렉터리는 비어 있어야 한다. `--dry-run`은 입력 artifact를 검사하고 계획만 출력한다.
이 래퍼는 원본을 수정하지 않고 rootfs/EFI capsule 디스크를 복사한다.
동일 호스트의 다른 full-system QBox와 동시 실행하는 것은 shared-memory 소유권 때문에
별도 검증 대상이며, 이 대시보드는 한 번에 하나의 VM만 관리한다.
실행기는 TUI/headless 모두 같은 UID의 기존 관리 full-system 프로세스가 있으면 새 실행을 거부한다.
기존 VM을 자동으로 종료하지 않으므로 먼저 해당 대시보드/guest에서 정상 종료한다.

## 부팅 및 모듈 계약

부팅 성능/경고 조사와 재현 명령은
[부팅 지연 조사](autosd-boot-performance-ko.md)를 참고한다.
기본 실행은 SLUB/강제 expedited RCU 진단 옵션을 제외한 RT 기본 정책을 사용한다.
기존 manifest의 진단 정책을 유지하려면 `--diagnostic-boot`를 지정한다.
private guest에 배포되는 ESP 권한/`ethsi1` 자동 DHCP 제외 정책은 다음 부팅부터
적용되며, 사용자 정의 NetworkManager 연결은 삭제하지 않는다.

- 기존 `run_qbox_yocto.sh`의 full-system firmware와 Lua를 재사용한다.
- AutoSD initrd/cmdline으로 Yocto BSP UKI를 구성해 private 디스크의 UKIBoot slot에 기록한다.
  GPT/rootfs/bootctl은 보존하며, slot 선택·부팅 결과 갱신은 실제 EFI loader/guest가 수행한다.
- RSE flash는 실행별 상태를 사용한다. AP-only loader나 domain mock으로 대체하지 않는다.
- `arm_si_rproc`와 `rpmsg_net`은 out-of-tree 모듈이다. 일반 kernel modules archive에는 없으므로
  현재 Yocto recipe의 install 산출물을 별도로 사용한다.
- 최초 AP 로그인 후 소유 guest의 loopback SSH로 module을 배포한다. SHA-256, AutoSD/root,
  실행 커널 release를 확인하고 `depmod`, `restorecon`, `modprobe`를 수행한다.
  `/etc/modules-load.d/apollo-fullsystem.conf`로 이후 부팅도 유지한다.
- 설치/로드 성공은 `modules.json`/`modules.log`, 실제 RPMsg 연결은 SI CL1 UART로 분리해 확인한다.
- 동일 빌드의 `pfdi_misc`, `libpfdi`, sample app과 4-CPU config를 배포한다.
  `apollo-pfdi.service`는 `apollo.fullsystem=1`에서만 실행하므로 다른 백엔드에서는
  PFDI SMC를 호출하지 않는다. startup은 CPU 0–3 실제 OnL 결과를 검사하고 이후
  주기적 진단을 실행한다. SI CL0의 `PFDI monitor timeout`은 계속 FAIL 판정 대상이다.
  현재 firmware는 `Stub firmware detected - No real diagnostics will be executed`를
  출력한다. OnL OK는 PFDI 호출/감시 연동 증거이며 실제 하드웨어 fault 진단 성공이 아니다.
- `--foreground-runtime`으로 AutoSD supervisor와 full runner의 lifetime을 연결한다.
  기존 full runner의 다른 호출 기본 동작은 유지한다.
- UART `reboot: Power down` 이후 소유 runtime과 QBox 정리가 끝나야 종료 PASS다.

## 증거

각 boot job의 `vm/`에 `launch.json`, `domains.json`, `modules.json`, `modules.log`,
`result.json`과 도메인별 UART를 저장한다. canonical full-system 로그·artifact는
`vm/full-system/`에 보존한다. 시나리오는 각 job의 `guest/`와 `console.log`에 저장한다.

## 2026-09-27 실행 검증

환경: `apollo-qvp`, Yocto BSP UKI `6.18.5-rt3-yocto-preempt-rt`, AP 4 CPU,
AutoSD regular customization 이미지, SSH 2244. 기존 deploy를 재사용했으며 이 변경에서
커널/firmware를 다시 빌드하지 않았다. 대시보드는 localhost와 `192.168.0.13:8765`에서 확인했다.

증거 루트: `build/autosd/dashboard/20260927-232504-1f3664df/`.

| 검사 | 결과 | 증거 |
| --- | --- | --- |
| 첫 full 부팅 | FAIL 보존 | `38bbd532590b449fa9c11b384ba626a4/vm/`: AP PFDI app 부재로 SI CL0 AP core monitor timeout |
| PFDI payload 사전 설치 | PASS (설치만) | `build/autosd/fullsystem-payload-prepare/modules.json`, ABI loader 검사 포함 |
| 정상 Power off / 소유 runtime 정리 | PASS | `8a485e2a6c05493181499ec3fe44af01`: UART Power down + launcher rc 0 |
| 준비 디스크 Power on | PASS | `6f37b79dbafb4c0d9933334b1364b07e/vm/`: RSE/SI0/SI1/AP + module/PFDI provision + SSH |
| 자동 Automotive health | PASS | `4779f6afed194c868f40b03586f18d13`: HEALTHY, SELinux Enforcing, Root/ADAS/QM/BlueChi |
| Automotive S01–S06 | 6/6 PASS | `693d1e609ad44fc1a7dcf476994e2919/guest/scenarios.json`: BlueChi, QM 교체, ADAS fault, latch, 명시적 복구 |
| PREEMPT_RT R01–R06 | 측정 PASS, R01 기준 초과 | `e161257725f04ffa8326825bed432f53/guest/results.json`; 아래 수치 참조 |
| Timerlat / histogram | PASS | `abe0365a5d6f482288e969573d99733c/guest/trace-result.json`; IRQ/Thr/Usr 3개 차트 확인 |
| OS noise / 시간대별 차트 | PASS | `842d8aad5de84423bbfa1d0c0de56428/guest/trace-result.json`; 실제 event timestamp 사용 |
| 백엔드 선택 / 실행 중 변경 차단 | PASS | 브라우저 3개 선택 확인; 실행 중 API 변경 거부 |
| Guest 로그 / AP CPU 관측 | PASS | RSE/SI0/SI1 UART 선택, AP CPU 4개 ONLINE |
| Python 회귀 / UI 단위 검사 | PASS | 444 / 30 tests; Paramiko 기존 deprecation warning 2개 |

화면 증거: `build/autosd/dashboard/fullsystem-ready.png`.
첫 실패를 성공으로 재분류하거나 PFDI timeout marker를 제거하지 않았다.
두 번째 부팅에서는 CPU 0–3 OnL OK와 주기적 PFDI service를 확인했다.
물리 진단은 firmware stub 제한 때문에 검증 대상 밖이다.

RT 관찰 기준은 기존 5,000µs를 유지했다. R01 SCHED_OTHER 최대 7,685.304µs
(초과 4건), R02 FIFO 3,824.328µs, R03 QM 부하 4,282.432µs,
R04 동일 CPU 경합 3,843.352µs였다. R05는 합성 지연 주입을 검출했고
(13,112.536µs, DETECTION_PASS), R06 cyclictest 실행도 PASS했다.
R01은 비교용 baseline이므로 suite의 RT 평가와 별개로 EXCEEDED를 그대로 표시한다.
이는 QBox/host 부하 아래 5초 관측이며 실보드 worst-case 보증이 아니다.

Timerlat은 IRQ/Thr/Usr 각각 4,114/4,115/4,115 samples, 최대 776/4,473/4,740µs,
overflow 0, `NO_THRESHOLD_STOP_OBSERVED`, `settings_restored=true`였다.
화면 증거: `build/autosd/dashboard/fullsystem-timerlat.png`.

OS noise는 11,975 events, 약 4.933초 구간, 최대 약 1,663µs였다.
event 손실/파싱 실패 0, raw trace truncation 없음, 555개 대표 peak로 보존했고
trace 설정 복구도 확인했다. UI의 X축은 실제 event 시간, Y축은 latency다.
화면 증거: `build/autosd/dashboard/fullsystem-osnoise.png`.

QBox Pause/Resume, QBox AP-only Reboot, OTA/rollback, OSTree full-system 실행,
RSE/SI firmware CPU 사용률 및 물리 타이밍은 이번 검증에 포함하지 않았다.
RSE/SI 카드는 부팅/오류 로그 관측이고 CPU 사용률 그래프는 AP Linux CPU만 의미한다.

최종 확인(`build/autosd/fullsystem-final-inspect/`): guest uptime 약 1,142초,
PFDI/Root monitor/ADAS/QM/BlueChi active, safety HEALTHY, PREEMPT_RT=1,
EFI runtime 존재, slot `_a`. 같은 부팅 세션의 SI CL0에 PFDI monitor timeout이
없고 dashboard domain PASS/monitoring ONLINE을 유지했다. VM은 실행 상태로 남겼다.

## 2026-09-28 tmux TUI 전환 검증

`run_qbox_autosd.sh` 기본 모드를 기존 `run_qbox_yocto.sh`의 `fvp-like` TUI로
연결했다. dashboard는 명시적 `--headless`를 계속 사용한다.
기존 dashboard VM은 사용자 승인 후 정상 종료했고
(`d108e11125e744e38e5ccf4eac9b0adc`, Power down 및 rc 0), 보존된 디스크로
`autosd-full` 세션을 생성했다. 증거 경로는
`build/qbox-apollo-qvp/autosd-tui-20260928/`이다.

- AP, RSE, SI CL0, SI CL1, Secure, platform, shell의 실제 canonical pane 7개 확인.
- 실제 터미널 attach 후 `Ctrl-b d`로 detach, 세션과 supervisor/runtime 생존 확인.
- 기존 full-system 실행 중 재실행 거부 및 출력 디렉터리 미생성 확인.
- 기존 TUI/AutoSD/dashboard/module 통합 회귀 테스트 222 PASS.
- 실제 RSE/SI CL0/SI CL1/AP 부팅 및 HIPC/PFDI provision 모두 PASS (`domains.json`).
- AP pane의 UART FIFO 입력으로 root 로그인, `AUTOSD_TUI_INPUT_OK`, 커널 버전 출력과
  PFDI/Root safety monitor/ADAS/QM 서비스 active 확인 (`linux-uart.log`).
- 같은 부팅 세션에서 SI CL0 PFDI monitor timeout 없음. detach 뒤에도 supervisor 유지.

독립 TUI의 VM은 대시보드가 소유하지 않는다. TUI 실행 중에는 대시보드의
Power on을 누르지 않는다. 정상 종료는 TUI AP 콘솔 또는 해당 SSH에서 수행한다.
검증 후 VM은 `autosd-full` 세션으로 실행 중이며 `tmux attach-session -t autosd-full`로
접속할 수 있다. F12 강제 종료 재시험은 수행하지 않았다(기존 canonical 동작 재사용).
