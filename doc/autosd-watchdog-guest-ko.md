# AutoSD AP watchdog Guest Quick Guide

이 도구는 AP의 `/dev/watchdog0` (`SBSA Generic Watchdog`)만 대상으로 한다.
RSE/SI watchdog이나 실제 차량의 safety qualification을 대신하지 않는다.
기본 실행은 sysfs 읽기만 수행하며 watchdog 장치를 열거나 활성화하지 않는다.

## 준비 및 읽기 전용 확인

`apollo_qvp_defconfig`의 `CONFIG_WATCHDOG_SYSFS=y`를 반영한 커널로 부팅한다.
Host에서 customization bundle을 만들 때 명시적으로 추가한다.

```sh
python3 autosd/customization/prepare.py --watchdog-tools \
  --out build/autosd/automotive-watchdog
```

기존 AIB build 또는 disposable regular guest용 `install-private-guest.py` 흐름으로
설치하면 root에만 `/usr/libexec/apollo/watchdog-guest.py`가 배치된다. QM에는
배치하지 않으며 watchdog 서비스나 `RuntimeWatchdogSec`를 자동 활성화하지 않는다.
기존 customization/컨테이너를 갱신하는 private installer는 읽기 전용 도구가 아니므로
단순 진단만 필요하면 bundle의 `watchdog-guest.py`만 Guest에 복사해 실행해도 된다.
아래 예시는 설치된 경로를 사용한다.

```sh
python3 /usr/libexec/apollo/watchdog-guest.py inspect --output /var/tmp/watchdog-inspect
```

출력 디렉터리는 새 경로여야 한다. `events.jsonl`, `result.json`에 기록하며
stdout에도 실시간 JSON 이벤트를 출력한다. sysfs가 없으면 unavailable로
표시하며 active test는 진행하지 않는다. 로그의 시간은 guest monotonic seconds와
realtime nanoseconds다. QBox host wall time과 직접 동일시하면 안 된다.
inactive 상태의 `timeleft`는 읽지 않고 `valid: false`로 기록한다. 비활성 SBSA
타이머의 이전 WCV에서 현재 counter를 빼면 unsigned underflow로 큰 숫자가 나올 수
있기 때문이다. active keepalive에서는 실제 ioctl 값을 읽고 timeout 범위를 검증한다.

## 정상 feeding 검증

root 권한, `nowayout=0`, inactive 상태가 필요하다. systemd
`RuntimeWatchdogUSec`가 0이 아니거나 다른 프로세스가 장치를 소유하면 거부한다.
검사 이후의 경쟁은 커널 exclusive-open으로 차단한다.

```sh
python3 /usr/libexec/apollo/watchdog-guest.py keepalive --timeout 20 --duration 30 \
  --output /var/tmp/watchdog-keepalive
```

SETTIMEOUT/GETTIMEOUT ioctl 확인 후 timeout/4 간격으로 KEEPALIVE ioctl을
호출한다. 완료·오류·SIGINT/SIGTERM에는 DISABLECARD, 필요 시 magic-close `V`를
시도하고 inactive 상태를 확인한다. SIGKILL은 정리할 수 없으므로 사용하지 않는다.
PASS는 ioctl feeding 및 생존만 의미하며 reset 경로 PASS가 아니다.

## 만료 시험: 명시적 destructive opt-in

다른 작업을 종료하고 디스크·UART 로그를 보존한다. Host에서 UART와 watchdog
WS1/reset을 관찰할 준비가 된 뒤에만 실행한다. 자동 부팅 서비스로 등록하지 않는다.

```sh
python3 /usr/libexec/apollo/watchdog-guest.py expiry --timeout 20 --grace 5 \
  --acknowledge-reset --output /var/tmp/watchdog-expiry
```

`ready` 이벤트에 PID, timeout, fd 유지 여부가 출력된다. 최초 ping 이후 fd를
열어 둔 채 feeding을 중단한다. 프로세스 종료/강제 close로 만료를 유도하면
watchdog core가 대신 feeding할 수 있으므로 이 방식은 사용하지 않는다.
관찰 deadline까지 생존하면 disarm 후 `NOT_OBSERVED`를 기록한다. 실제 reset이면
마지막 이벤트만 남고 result.json이 없을 수 있으며, 이는 자체적으로 PASS가 아니다.
Host의 WCS/WS1 증거, UART reset, 새 boot ID를 함께 확인해야 한다.

현재 action=0에서는 Linux timeout이 **WS1까지의 전체 초 단위**다.
WOR는 `counter_frequency / 2 * timeout`; WS0 예상 시점은 timeout/2,
WS1 예상 시점은 timeout이다. `ws0-expected`는 계산값이며 실제 WCS 관측이 아니다.
action=1의 WS0 panic 모드는 이 도구에서 사용하지 않는다. 이 도구는 `/dev/mem`
MMIO에 접근하지 않는다. WCS 실제 값은 별도의 read-only platform monitor로 수집한다.

## systemd 통합은 별도 opt-in

시험 도구와 systemd를 동시에 owner로 사용하면 안 된다. 실험 종료 후 시스템의
reset 경로가 검증된 경우에만 administrator가 drop-in을 선택적으로 설치한다.

```ini
# /etc/systemd/system.conf.d/90-apollo-watchdog.conf
[Manager]
WatchdogDevice=/dev/watchdog0
RuntimeWatchdogSec=30s
```

자동 설치·자동 reexec는 제공하지 않는다. 잘못된 값은 반복 reset을 만들 수 있다.
적용/해제 시 systemd manager 상태와 `/sys/class/watchdog/watchdog0/state`를 확인한다.
이 가이드의 도구 단위 테스트는 mock 기반이며 실제 만료 검증 결과가 아니다.

### 일회성 `/run` manager 시험과 원복

아래는 운영자가 별도로 승인한 테스트용 절차이며 자동 실행하지 않는다.
WS1 이후 firmware 재부팅 경로에 실패가 남아 있다면 먼저 그 문제를 해결한다.
시험 중 expiry 도구를 병행하지 않으며 `/dev/watchdog0`을 여는 다른 프로세스를
실행하지 않는다. root shell에서 원래 설정이 watchdog 비활성인 경우만 진행한다.

아래 블록 전체를 한 번에 실행한다. subshell의 `set -eu`가 preflight 실패 시
즉시 중단한다. 정상 종료뿐 아니라 부분 적용 실패·INT/TERM/HUP에도 trap이
이번 실행에서 만든 drop-in만 제거하고 원래 비활성 상태로 복구한다.

```bash
(
set -eu
test "$(systemctl show --property=RuntimeWatchdogUSec --value)" = 0
test "$(cat /sys/class/watchdog/watchdog0/state)" = inactive
test "$(cat /sys/class/watchdog/watchdog0/nowayout)" = 0
test ! -e /run/systemd/system.conf.d/90-apollo-watchdog-test.conf
systemctl show --property=RuntimeWatchdogUSec --property=RuntimeWatchdogPreUSec \
  --property=WatchdogDevice
install -d -m 0755 /run/systemd/system.conf.d
watchdog_trial_file=$(mktemp /run/systemd/system.conf.d/.apollo-watchdog-test.XXXXXX)
cleanup_watchdog_trial() {
    watchdog_trial_status=$?
    trap - EXIT HUP INT TERM
    # Only unlink the exact inode this invocation linked, never an older file.
    if test /run/systemd/system.conf.d/90-apollo-watchdog-test.conf -ef "$watchdog_trial_file"; then
        rm /run/systemd/system.conf.d/90-apollo-watchdog-test.conf || watchdog_trial_status=1
        systemctl daemon-reexec || watchdog_trial_status=1
        test "$(systemctl show --property=RuntimeWatchdogUSec --value)" = 0 || watchdog_trial_status=1
        test "$(cat /sys/class/watchdog/watchdog0/state)" = inactive || watchdog_trial_status=1
    fi
    rm -- "$watchdog_trial_file" || watchdog_trial_status=1
    exit "$watchdog_trial_status"
}
trap cleanup_watchdog_trial EXIT
trap 'exit 129' HUP
trap 'exit 130' INT
trap 'exit 143' TERM
printf '%s\n' '[Manager]' 'WatchdogDevice=/dev/watchdog0' \
  'RuntimeWatchdogSec=30s' 'RuntimeWatchdogPreSec=0' \
  > "$watchdog_trial_file"
chmod 0644 "$watchdog_trial_file"
# Atomic, no overwrite: failure leaves another invocation's file untouched.
ln "$watchdog_trial_file" /run/systemd/system.conf.d/90-apollo-watchdog-test.conf
systemctl daemon-reexec
systemctl show --property=RuntimeWatchdogUSec --property=RuntimeWatchdogPreUSec \
  --property=WatchdogDevice
test "$(systemctl show --property=RuntimeWatchdogUSec --value)" = 30s
test "$(cat /sys/class/watchdog/watchdog0/state)" = active
sleep 30
systemctl --failed --no-pager
# EXIT trap restores RuntimeWatchdog=0 and verifies inactive.
)
```

manager가 feeding하는 상태에서 host가 정해진 시간만 관찰한다. 생존과 sysfs active는
reset 성공 증거가 아니다. 위 블록은 30초 관찰 후 자동 원복한다.
다른 `/etc` 또는 `/run` 설정은 건드리지 않는다. 이 절차는 원래 RuntimeWatchdog=0을
전제하므로 원래 값이 0이 아닌 시스템에는 적용하지 않는다.
원복 실패는 종료 코드에 반영한다. SIGKILL이나 guest reset에서는 trap 실행을
보장할 수 없다. 이 경우 파일이 이번 실행에서 생성됐는지 확인한 뒤 운영자가
동일한 unlink → daemon-reexec → RuntimeWatchdog=0/inactive 검증을 수행한다.

재부팅하면 `/run` drop-in은 사라지지만, 시험 중 장치 소유권을 정리하기 위해
정상 실행 상태에서 위 원복 검증을 우선 수행한다. 실패 시 journal과 manager 설정을
기록하고 반복 reexec/강제 종료로 문제를 덮지 않는다.

## 기록된 manager 시험: 2026-09-28 context 이미지

실제 실행 증거는 `build/autosd/watchdog-runtime-20260928/context-systemd/`의
`console.log`, `result.json`이다. 실행한 generated script는 같은 상위 디렉터리의
`systemd-watchdog-trial.sh`이며 장치를 직접 열지 않고 sysfs로 관찰했다.

| 항목 | 관측 결과 |
|---|---|
| manager 설정 | `/dev/watchdog0`, RuntimeWatchdog 30초, pretimeout 0 |
| 관찰 | guest uptime 215.41 → 247.48초, 약 32.07초, 7개 표본 |
| active timeleft | 26, 21, 27, 22, 28, 22, 29초; 모두 0–30 범위 |
| 원복 | RuntimeWatchdog=0, state=inactive, 임시 drop-in 제거 |
| 생존·서비스 | boot ID 유지, failed unit 0, 전체 명령 rc=0 |

SSH 준비·manager reexec 등을 포함한 Host 명령 시간은 약 92.27초로,
위 guest 관찰 시간과 다르다. 이 결과는 **manager feeding 및 원복 PASS**이며
최종 PFDI 수정 이미지의 반복 watchdog reset 복구 PASS를 뜻하지 않는다.
최종 reset/서비스 복구 결과는 [별도 검증 보고서](autosd-power-watchdog-validation-ko.md)의
이미지·실행별 증거를 확인한다.

## Reset 이후 HIPC 왕복 통신 확인

full-system의 provisioning 결과에서 `HIPC_ENDPOINT_READY`를 먼저 확인한다.
이는 `ethsi1`과 RPMsg endpoint 생성 확인일 뿐 통신 성공은 아니다.
아래 도구는 추가 패키지 없이 Guest의 Python 3, NetworkManager `nmcli`와
root의 raw socket 권한으로 AP→SI CL1 ICMP 요청 및 SI→AP 응답을 3회 확인한다.

Host 저장소 루트의 **Bash**에서 실행한다. SSH 포트는 현재 private VM 설정에 맞춘다.
기본 개발 이미지 계정은 `root`이며 SSH 인증 및 host key 확인을 정상 수행한다.
기존 Guest의 `ethsi1.200`이 있으면 도구가 중단하므로 기존 연결을 임의 삭제하지 않는다.

```bash
(
set -euo pipefail
hipc_port=2244
mkdir -p build/autosd
hipc_log=$(mktemp build/autosd/hipc-link.XXXXXX.log)
scp -P "$hipc_port" scripts/autosd_demo/hipc_ping.py \
  root@127.0.0.1:/var/tmp/apollo-hipc-ping.py
scp -P "$hipc_port" scripts/autosd_demo/check_hipc_link.sh \
  root@127.0.0.1:/var/tmp/apollo-check-hipc-link.sh
ssh -p "$hipc_port" -o ConnectTimeout=60 root@127.0.0.1 \
  'sh /var/tmp/apollo-check-hipc-link.sh' 2>&1 | tee "$hipc_log"
printf 'HIPC log: %s\n' "$hipc_log"
)
```

도구는 VLAN 200, AP `192.168.1.2/24`, SI CL1 `192.168.1.1` 계약을 사용한다.
`nmcli connection add save no`로 고유 UUID의 임시 연결을 만들고, 자동 연결과
default route를 비활성화한다. 기존 `eth0` 및 연결 프로파일은 변경하지 않는다.
완료·오류·일반 종료 신호에서 **이번 UUID만** 삭제하며 삭제 실패는 종료 코드에 반영한다.
SIGKILL/reset에서는 정리를 보장할 수 없다. 이때 `HIPC_TRIAL_START uuid=...`를
확인하고 `nmcli connection show uuid <해당-UUID>`로 소유 대상을 확인한 뒤
그 UUID만 삭제한다. `save no` 프로파일은 재부팅 후 유지되지 않는다.

ICMP 도구는 VLAN interface와 source IP에 bind하고, IP/ICMP checksum,
송수신 주소, identifier, sequence, 무작위 payload를 검증한다. 각 수신 deadline은
guest monotonic 기준 10초이며 세 패킷 모두 일치해야 JSON `status: PASS` 및
종료 코드 0이 나온다. `rtt_ms_guest_monotonic`은 **guest 시간**이며
Host wall time 또는 물리 하드웨어 latency 성능으로 해석하지 않는다.

2026-09-28 실제 reset 후 `rearm-hipc-traffic/{console.log,result.json}`에서
3/3 응답과 임시 프로파일 삭제를 확인했다. 증거 루트는
`build/autosd/watchdog-runtime-20260928/`이다. 이는 **AP 요청/SI 응답 왕복 PASS**이며
별도 SI-initiated ping, 지속 부하, UDP 무손실 전달 또는 최종 이미지의 모든 반복 reset
통신 성공을 뜻하지 않는다. 재접속/버퍼 부족 중 Veth TX는 무한 대기 대신
`-EAGAIN`/packet drop을 허용한다. TCP는 재전송할 수 있으나 UDP 전달을 보장하지 않는다.

위 최초 기록에는 RTT 키가 `rtt_ms_host_monotonic`으로 잘못 표기되어 있다.
실제 측정은 Guest Python의 monotonic clock이며, 보존된 원본 로그는 수정하지 않았다.
현재 저장소 도구는 올바른 `rtt_ms_guest_monotonic` 키를 출력한다.

최종 비-debug full-system 시험은 `autosd-watchdog-entry-fixed-20260928`에서
native reboot 2회와 WS1 reset 2회, 총 5개 부팅마다 앱 HEALTHY 및 HIPC 3/3을
확인하고 정상 shutdown까지 통과했다. 재현 순서와 boot ID/host trace는
[전원·watchdog 검증 보고서](autosd-power-watchdog-validation-ko.md)에 있다.
이는 유한한 기능 시험이며 장시간 stress 또는 UDP 전달 보장이 아니다.
