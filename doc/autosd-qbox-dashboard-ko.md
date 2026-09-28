# QBox AP domain AutoSD 대시보드

RSE/SI CL0/SI CL1까지 실행하는 `qbox-full`은
[full-system 가이드](autosd-fullsystem-dashboard-ko.md)를 참고한다.
상단 실행 대상 선택으로 `qemu`, `qbox`(AP only), `qbox-full`을 전환할 수 있다.
전환은 VM과 작업이 모두 종료된 상태에서만 허용된다.

## 범위

대시보드는 `--backend qbox`로 `run_qbox_linux.sh`를 호출해 Apollo QVP AP Linux를
직접 부팅한다. QEMU 기본 백엔드는 `--backend qemu`이며 기존 동작을 유지한다.
QBox에서는 AP CPU/디바이스를 실행하고 다른 도메인은 Linux-only 프로파일의 mock을 사용한다.
RSE/Safety Island 전체 firmware 부팅, 보안 인증 또는 물리 타이밍 동등성을 의미하지 않는다.

## Quick Guide

기존 대시보드에서 VM을 정상 종료한 다음 서버를 종료한다. 실행 중인 VM을 둔 채
서버만 종료하면 프로세스 소유권을 새 서버가 인계하지 않는다.
아래 `--rootfs`에는 보존할 최신 정상 종료 디스크를 지정한다.

```sh
python3 scripts/autosd_dashboard/server.py \
  --backend qbox \
  --listen 127.0.0.1 --listen 192.168.0.13 \
  --allow-unauthenticated-lan --allow-private-guest \
  --ssh-port 2244 \
  --manifest build/autosd/demo-minimal-qm-prepared/regular.json \
  --rootfs build/autosd/dashboard/20260927-161222-530e591a/10e53714acf34799b09e9b7ef4ad8033/vm/rootfs.wic
```

1. `http://192.168.0.13:8765/` 또는 localhost에 접속한다.
2. 상단의 `QBox AP direct` 표시를 확인하고 Power on을 누른다.
3. 1번 guest boot ID/SSH 확인 후 2번 Automotive health 자동 검사 완료를 기다린다.
4. Automotive S01–S06, PREEMPT_RT R01–R06, Timerlat, OS noise를 선택해 실행한다.
5. Host log에서 시나리오 명령/결과, Guest log에서 Boot UART 및 Root/ADAS/QM 서비스 출력을 확인한다.
6. 측정 종료 후 결과 표·그래프와 실제 실행 기준을 확인한다.
7. 종료는 Power off를 사용한다. 재시작은 정상 종료 후 Power on으로 진행한다.

개별 장애 시나리오는 정상 상태/latch 등의 선행 조건을 유지한다. 자동으로 장애를
해제하지 않으며 S06 등의 명시적 복구 시나리오를 사용한다.

## 지원 경계

| 기능 | QBox AP direct |
| --- | --- |
| Power on / Power off | 실행별 디스크 복사본, guest 정상 종료 확인 후 소유 프로세스 정리 |
| Reboot / Pause / Resume | 미지원; UI 비활성화 및 API 거부 |
| Feature 1 / 2 자동 연동 | 지원; QBox boot readiness 제한 600초 |
| CPU / subsystem 모니터링 | guest Linux CPU 및 서비스 cgroup 관찰 |
| Automotive / RT / Timerlat / OS noise | 동일한 guest 실행 adapter 사용, 실제 검증 결과는 아래 별도 기록 |
| OTA / native UKI / full-system firmware | 관리형 대시보드 범위 밖 |

QBox RT 결과에는 `platform=qbox`를 기록한다. 대시보드의 5000µs는 기능 관찰용
잠정 기준이며 QBox의 하드웨어 timing budget을 의미하지 않는다.

## 구현 계약

- `run_qbox_linux.py --ssh-port`는 `127.0.0.1:<port>`만 guest 22번에 포워딩한다.
- 커널 UART의 `reboot: Power down` 확인 후 자신의 QBox process group만 종료한다.
- runner 결과에 `poweroff_observed`와 `POWERED_OFF`를 기록해 timeout/수동 종료와 구분한다.
- 현재 Lua AP-only 프로파일은 전체 reset fanout을 구성하지 않아 native Reboot를 노출하지 않는다.
- dashboard job별 `vm/launch.json`, `vm/qbox.log`, `vm/linux-uart.log`, `console.log`, guest 결과를 보존한다.
- API는 임의 런처/명령을 받지 않으며 서버 시작 시 whitelist 백엔드를 선택한다.
- QBox의 guest 처리 시간을 고려해 health/trace는 360초, RT는 600초,
  개별 Automotive는 600초, 전체 Automotive는 1500초로 제한한다(host 시간).
- RTLA 내부 수집 제한은 QBox에서 측정 시간 + 120초(guest monotonic)다.
  tracefs 초기화/정리 여유만 분리하며 `-d 5s`와 5000µs 중지 기준은 유지한다.
  실패 후 남은 trace instance를 임의로 제거하지 않으며 정상 Power off/on으로 재검증한다.

### Device 준비 대기

최초 실행은 커널에서 `vda1..vda5`와 `ttyAMA0`가 확인되었지만 udev coldplug가
AutoSD의 기본 30초 device 제한을 넘겨 ESP 마운트가 실패했다. `local-fs.target`
실패 후 이미지의 Emergency Shell Override가 재부팅을 요청했다.
이는 디스크/커널 드라이버 미탑재와 구분한다.

AutoSD AP 직접 부팅에만 `systemd.default_device_timeout_sec=180s`를 추가했다.
명시적으로 전달된 값은 유지하며 UKI/비 AutoSD 부팅에는 적용하지 않는다.
180초는 로컬 AutoSD image builder의 debug 설정과 일치한다:
`autosd/automotive-image-builder/include/computed-vars.ipp.yml`의 `systemd_timeout`.
이 커널 인자는 [systemd 공식 문서](https://github.com/systemd/systemd/blob/main/man/kernel-command-line.xml)의
`DefaultDeviceTimeoutSec` override다. ESP 마운트와 서비스 검사를 생략하지 않는다.
수정 후 실제 로그에서 ESP/ttyAMA0 device 발견, 로그인, SSH 및 Automotive health PASS를 확인했다.

AP 직접 부팅에서 guest가 native restart를 요청하면 launcher는
`UNSUPPORTED_REBOOT`로 종료한다. 이전 로그인 성공을 재부팅 성공으로 오인하지 않는다.

## 검증 결과

2026-09-27, 현재 빌드의 `6.18.5-rt3-yocto-preempt-rt`, AP 4 CPU,
private regular customization disk로 실행했다.

| 검사 | 결과 | 근거 |
| --- | --- | --- |
| Device timeout 수정 후 부팅 | PASS | `00b95e359a2f45e58b96d13670efce0e`, 약 150초 host 시간 후 boot ID/SSH 확인 |
| 자동 Automotive health | PASS | `80f174bf2ce24f09901c2e67ea3d9de5` |
| Automotive S01–S06 | 모두 PASS | `ae38f239c0ee4e5fbc46ada5fe83459a`, S06 이후 HEALTHY |
| RT R01–R06 | 측정 PASS / RT 기준 이내 | `aed1a380a61c464c879ea8079db5b563`, platform=qbox |
| Power off | PASS | `f136b92b85d340e2922d0610ea493255`, 약 35초, runner POWERED_OFF / poweroff_observed=true |
| 보존 디스크 Power on / 자동 health | PASS | `05e83b4143bd423d9a916de76e10f4b7` / `f604fd948ed24e589a9d07255eb845b9`, 새 boot ID 및 Feature 초기화 확인 |
| Timerlat 재검증 | PASS | `9366771264ae42248760c2970f99391b`, 62.895초, trace 설정 복구 및 잔여 instance 없음 |
| OS noise 재검증 | PASS | `930c941356f9499188a6a83d03b67ec8`, 41.914초, 19925 samples, 최대 1718µs, trace 설정 복구 |
| CPU/subsystem 관찰 | PASS | CPU 0–3, Safety/ADAS/QM/BlueChi, ADAS 및 QM container cgroup |
| 현재 UART / LAN 접속 | PASS | 현재 boot epoch의 UART 61 KiB 이상, localhost 및 내부 IP HTTP 200 |
| 서비스별 Guest 로그 | PASS | Root, Safety, BlueChi, ADAS, QM system/app/container 7개 source 모두 API OK |
| Python / UI 회귀 | PASS | AutoSD 및 QBox launcher 321개, UI 23개 |

위 작업 증거는 `build/autosd/dashboard/20260927-215600-63498895/<job-id>/`에 있다.
첫 device timeout 실패는 별도로
`build/autosd/dashboard/20260927-215122-a23e0295/1419e0f0bb634779a49b8456373b9734/`에 보존했다.
스크린샷: `build/autosd/dashboard/qbox-ap-boot-automotive.png`.

RT R02/R03/R04/R06 최대는 각각 910.072 / 655.616 / 1025.080 / 791µs였다.
R01 일반 스케줄러는 5995.496µs로 EXCEEDED이며 baseline으로 보존한다.
R05 합성 주입은 11851.528µs로 DETECTION_PASS다. 둘 다 RT 성능 gate에서 제외한다.
실제 브라우저에서 이 작업으로 자동 선택되어 6행 표와 SVG 그래프가 표시됨을 확인했다.

최초 Timerlat `5e835c588a2c4ba9a3faf605da9cee83`은 기존 35초 수집 제한에서
TIMEOUT/무표본이었으며 trace 설정 복구에도 실패했다. 이어진 OS noise
`ee481b3879b243aeabb4df82444d6915`는 기존 instance 때문에 UNSUPPORTED로 거부했다.
이 결과는 성공으로 재분류하지 않는다.
정상 전원 재시작 및 QBox 수집 제한 125초 적용 후 Timerlat은 62.895초에 완료했다.
IRQ/Thread/User 각각 4952/4951/4951 samples, 최대 543/995/2136µs이며
trace 중지 기준 초과는 관찰되지 않았다. 실제 브라우저에서 3행 표와 SVG 자동 선택을 확인했다.
스크린샷: `build/autosd/dashboard/qbox-ap-timerlat-results.png`.
OS noise도 완료 후 실제 브라우저에서 1행 통계 표/SVG로 자동 전환됐으며,
`build/autosd/dashboard/qbox-ap-osnoise-results.png`에 보존했다.

최종 실행 중 세션은 `05e83b4143bd423d9a916de76e10f4b7`이며 CPU 4개 ONLINE,
Safety `HEALTHY`, failures=0을 확인했다. Guest 로그 7개 source는 이 세션 ID를
반환하고 실제 journal/컨테이너 출력과 명시적으로 구분한 heartbeat snapshot을 제공한다.
Host 로그는 선택한 작업의 SSH 명령 출력과 결과를 표시한다.
Reboot/Pause/Resume은 미지원 표시 및 API 거부를 유지하며, native reset 또는
full-system firmware 동작을 검증했다고 해석하지 않는다.
