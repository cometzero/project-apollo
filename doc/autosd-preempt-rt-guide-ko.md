# AutoSD Automotive PREEMPT_RT 실험 Quick Guide

대상: Apollo QVP 4 CPU, AutoSD Automotive customization. 작성일: 2026-09-27.
이미지 기본 절차는 [전체 Quick Guide](autosd-automotive-demo-guide-ko.md)를 따른다.
이 문서는 RT 도구를 선택 구성하고 latency를 측정·검출하는 추가 절차다.
실행 결과는 [RT 검증 리포트](autosd-preempt-rt-validation-ko.md)에 별도로 기록한다.

## 1. AutoSD 문서와 적용 원칙

검토한 `autosd/sig-docs` revision:
`75cb479c89c8ee01350d03ca031a9b780158a99d`.

- [Real-Time Linux](../autosd/sig-docs/docs/about/con_real-time-linux-kernel.md):
  PREEMPT_RT, 우선순위 상속, POSIX clock, mlock 사용을 설명한다. 공식 Automotive
  예시는 ECU 오류 IRQ → check-engine 표시다. 아래 timer 기반 실험은 이 경로의
  **스케줄링 부분을 단순화한 데모**이며 실제 ECU IRQ/센서/화면 응답 측정이 아니다.
- [QM scheduling](../autosd/sig-docs/docs/features-and-concepts/con_scheduler.md):
  QM은 seccomp 정책으로 RT 스케줄링을 제한한다. QM에 SYS_NICE/privileged를 주거나
  seccomp를 해제해서 FIFO를 강제하지 않는다.
- [CPU tuning](../autosd/sig-docs/docs/features-and-concepts/con_cpu-tuning.md),
  [공식 QM 데모](../autosd/sig-docs/demos/container_qm_scheduling/container_qm_scheduling.aib.yml):
  CPUWeight는 같은 cgroup 계층의 상대 가중치이며 50% CPU 제한이나 RT 우선순위가
  아니다. affinity도 shared cache/memory/IRQ/host 간섭까지 제거하지 않는다.
- [PCP 성능 실험](../autosd/sig-docs/docs/performance/performance_monitoring_with_pcp.md):
  stress-ng/fio와 PCP time-series를 연계한다. PCP는 부하 상관관계 관측이며
  microsecond wakeup latency 측정이나 deadline 검증을 대신하지 않는다.
- [Watchdogs](../autosd/sig-docs/docs/features-and-concepts/watchdogs.md):
  기존 Python safety monitor는 외부 watchdog 또는 인증된 safety MCU가 아니다.

이 workspace는 AutoSD 기본 `kernel-automotive` 대신 Apollo Yocto의
`kernel-apollo` RPM을 사용한다. PREEMPT_RT 이름만 같다고 설정·성능이 같지는 않다.
실행 커널의 `/sys/kernel/realtime`, `/proc/config.gz`, cmdline과 산출물 SHA를 기록한다.

| 영역 | 유지할 구성 | 이번 실험의 역할 |
| --- | --- | --- |
| root | safety monitor/Podman/BlueChi, monitor CPU 0 | 신뢰된 진단 프로세스 실행·증거 수집 |
| ADAS | 기존 container CPU 1, slice 512 MiB | root native RT probe를 CPU 1에서 실행해 주기 wakeup 지연 관찰 |
| QM | CPU 2–3, CPUWeight 50, 1 GiB, 기존 seccomp | SCHED_OTHER CPU/메모리/I/O 부하 발생 |

**기존 ADAS heartbeat container를 FIFO로 자동 변경하지 않는다.** root probe는
ADAS container 내부 측정과 동일하지 않다. 실제 ADAS를 RT화할 때는 앱의 blocking/
lock/priority-inheritance/메모리 선할당, IRQ thread 우선순위, RT 권한·seccomp·SELinux를
별도 설계한다. blanket privileged container로 대체하지 않는다.

`sched_rt_runtime_us`/`sched_rt_period_us`는 기록만 하고 변경하지 않는다. 예를 들어
950000/1000000은 RT CPU budget이며 모든 작업이 매초 반드시 50ms 지연된다는 뜻이
아니다. `-1`로 throttling을 해제하거나 `isolcpus`/`nohz_full`을 기본 적용하지 않는다.

## 2. 커널과 유틸리티 구성

QVP의 활성 원본은
`hsoc-stack/components/primary_compute/linux/arch/arm64/configs/apollo_qvp_defconfig`다.
기존 PREEMPT_RT/HIGH_RES_TIMERS/FTRACE에 TIMERLAT/OSNOISE/HWLAT/HIST_TRIGGERS를
추가한다. tracer는 선택 실행할 때만 동작하며 부팅 시 자동으로 켜지지 않는다.
FVP defconfig는 이번 변경 범위가 아니다.

| 도구/패키지 | 용도 | 실행 정책 |
| --- | --- | --- |
| `latency-probe` (동봉 static AArch64) | 절대시간 주기, FIFO/mlock, percentile/threshold/page fault | root에서 명시 실행 |
| `realtime-tests` | cyclictest, oslat 등 upstream rt-tests 계열 | root, 짧은 테스트부터 |
| `rtla` | timerlat IRQ/thread 지연, osnoise | root, 별도 trace 실험 |
| `trace-cmd` | sched/IRQ 등 ftrace 수집·해석 | 다른 tracer와 동시 실행 금지 |
| `util-linux`, `procps-ng` | chrt/taskset/ps/환경 확인 | 설정 readback |
| `stress-ng` | CPU/메모리 부하 | root/QM 설치, QM은 일반 스케줄링 |
| PCP, fio, tuna, perf | 선택적 시스템 상관관계/튜닝 | 기본 RT profile에는 미포함 |

AutoSD RPM 이름은 `rt-tests`가 아니라 **`realtime-tests`**다. 실제 nightly aarch64
repository에서 패키지 존재를 확인했지만 nightly 버전은 변한다. RPM NEVRA와 도구의
`--help`를 저장한다. 특히 rtla/kernel/perf 버전이 다르면 지원 옵션/tracepoint를
확인해야 하며, 도구 미설치는 UNSUPPORTED이지 latency PASS가 아니다.

## 3. 이미지 빌드 Quick Guide [host]

공유 BitBake는 직렬 실행한다. 기존 [이미지 빌드 3.2](autosd-automotive-demo-guide-ko.md#32-bsp--kernel-rpm--bundle--os-이미지-빌드-경로-a)의
bundle 생성 단계만 `--rt-tools`로 바꾸고 **새 kernel RPM도 다시 만든다**.

```sh
./yocto_build.sh --machine apollo-qvp --bsp
grep -E 'CONFIG_(PREEMPT_RT|OSNOISE_TRACER|TIMERLAT_TRACER|HWLAT_TRACER|HIST_TRIGGERS)=y' \
  build/tmp_baremetal/work-shared/apollo-qvp/kernel-build-artifacts/.config
bash scripts/autosd_demo/kernel_rpm_build.sh \
  build/tmp_baremetal/deploy/images/apollo-qvp \
  build/tmp_baremetal/work-shared/apollo-qvp/kernel-build-artifacts \
  build/autosd/automotive-rt-kernel-rpm
python3 autosd/customization/prepare.py --rt-tools --out build/autosd/automotive-rt-bundle
python3 -m pytest -q tests/test_autosd_customization.py \
  tests/test_autosd_latency_probe.py tests/test_autosd_rt_experiment.py tests/test_autosd_rt_trace.py
```

출력 manifest는 root에 도구와 `/usr/libexec/apollo/{latency-probe,rt-experiment.py,
rt-trace.py,check-automotive.sh}`, QM에 probe와 stress-ng를 추가한다. RT 서비스 자동
활성화나 공개 password는 추가하지 않는다. 나머지 SSH key 설정·native builder 전송·
AIB build·QCOW2/raw 회수는 기존 Quick Guide와 같고, 경로는 새 `automotive-rt-*`로
일관되게 바꾼다. native UKI에는 디스크에 내장된 커널이 사용되므로 host Image만
재빌드해 놓고 기존 native 디스크를 부팅하면 새 tracer 커널 검증이 아니다.

전체 AIB 재빌드 전 빠른 진단은 **종료된 regular customization disk의 private copy**에
새 Apollo Image를 직접 부팅하고 RPM/도구를 설치해 수행할 수 있다. 이는 아래 실행
구성을 검증하는 개발 경로이며 새 immutable 이미지 전체 빌드 PASS와 구분한다.

```sh
./run_qemu_linux.sh \
  --autosd build/autosd/demo-minimal-qm-prepared/regular.json \
  --rootfs build/autosd/automotive-scenario-coldboot/rootfs.wic \
  --headless --timeout 2400 --out-dir build/autosd/automotive-rt-run \
  --netdev user,id=net0,hostfwd=tcp:127.0.0.1:2234-:22
```

이 regular 개발 경로의 root/password 계정은 localhost 전용이다. OSTree/native
이미지의 `/usr`에 `dnf install`을 강행하거나 unlock을 자동 수행하지 않는다.

regular 개발 경로에서는 SSH 준비 후 다음을 host의 다른 터미널에서 수행한다.
원본 디스크가 아니라 launcher가 만든 copy에만 설치된다. 새 profile 전체 OS 빌드와
구분해서 기록한다. timeout 초기 실패 시 부팅 로그를 확인하고 새 `--out`으로 재시도한다.

```sh
python3 scripts/autosd_demo/guest_exec.py --port 2234 --timeout 1200 \
  --out build/autosd/automotive-rt-stage \
  --upload build/autosd/automotive-rt-bundle/payload/latency-probe:/root/latency-probe \
  --upload autosd/customization/rt/experiment.py:/root/rt-experiment.py \
  --upload autosd/customization/rt/trace-guest.py:/root/rt-trace.py \
  --upload autosd/customization/check-guest.sh:/root/check-automotive.sh \
  --upload build/autosd/automotive-rt-kernel-rpm/repo/kernel-apollo-6.18.5-1.aarch64.rpm:/root/kernel-apollo-rt.rpm \
  --command 'set -e; test ! -e /run/ostree-booted; dnf -y install realtime-tests rtla trace-cmd stress-ng util-linux procps-ng; rpm -Uvh --replacepkgs /root/kernel-apollo-rt.rpm; install -m 0755 /root/latency-probe /usr/libexec/apollo/latency-probe; install -m 0644 /root/rt-experiment.py /usr/libexec/apollo/rt-experiment.py; install -m 0644 /root/rt-trace.py /usr/libexec/apollo/rt-trace.py; install -m 0644 /root/check-automotive.sh /usr/libexec/apollo/check-automotive.sh; test "$(podman inspect --format "{{.Rootfs}}" qm)" = /usr/lib/qm/rootfs; install -m 0755 /root/latency-probe /usr/lib/qm/rootfs/usr/libexec/apollo/latency-probe; restorecon -RF /usr/libexec/apollo /usr/lib/qm/rootfs/usr/libexec/apollo; rpm -V kernel-apollo; sha256sum /usr/lib/modules/6.18.5-rt3-yocto-preempt-rt/vmlinuz'
python3 scripts/autosd_demo/guest_exec.py --port 2234 \
  --out build/autosd/automotive-rt-stage-off --command 'systemctl poweroff'
# UART Power down 및 QEMU 종료 확인 후, 설치된 copy로 재부팅:
./run_qemu_linux.sh \
  --autosd build/autosd/demo-minimal-qm-prepared/regular.json \
  --rootfs build/autosd/automotive-rt-run/rootfs.wic \
  --headless --timeout 2400 --out-dir build/autosd/automotive-rt-measure \
  --netdev user,id=net0,hostfwd=tcp:127.0.0.1:2234-:22
```

설치된 vmlinuz SHA가 packager의 `result.json`에 기록된 Image SHA와 같아야 한다.
같은 NEVRA/uname의 이전 모듈이 남지 않도록 로컬 검증 RPM을 `--replacepkgs`로
재설치한 뒤 재부팅한다. 이 RPM은 서명된 배포용 vendor RPM이 아니다.

## 4. 실행 전 확인 [target guest root]

```sh
uname -a
cat /sys/kernel/realtime
zcat /proc/config.gz | grep -E 'CONFIG_(PREEMPT_RT|TIMERLAT_TRACER|OSNOISE_TRACER|HWLAT_TRACER|HIST_TRIGGERS)='
cat /proc/cmdline
cat /proc/sys/kernel/sched_rt_{runtime,period}_us
getenforce
systemctl show apollo-asil-b.slice qm.service -p AllowedCPUs -p CPUWeight -p MemoryMax
rpm -q realtime-tests rtla trace-cmd stress-ng
cyclictest --help
rtla timerlat hist --help
bash /usr/libexec/apollo/check-automotive.sh
```

QM/BlueChi 시작이 늦으면 기존 `wait-ready-guest.sh`로 준비 상태를 기다린다.
실험 중 build/fault injection/다른 benchmark를 병행하지 않는다. kernel boot log의
`loglevel=7`, slub_debug, fsck/cpuidle/RCU 설정도 현재 실험 조건이며 production 최적화
기준이 아니다. host CPU governor/부하/QEMU command도 launch.json과 함께 보존한다.

## 5. Automotive latency 데모 시나리오

| ID | 실험 | 판정 |
| --- | --- | --- |
| R01 | CPU 1, SCHED_OTHER periodic wakeup | 유효 sample/actual policy/affinity 기록 |
| R02 | CPU 1, FIFO 50 + mlock | 요청 정책과 잠금 성공, 실패 시 normal로 강등하지 않음 |
| R03 | R02 + QM CPU 2–3 부하 | QM 일반 스케줄링 유지, 실제 부하 active/CPU 사용량 확인 |
| R04 | R02 + 동일 CPU 1의 root SCHED_OTHER 부하 | 별도 경합 비교; QM affinity 변경 없음 |
| R05 | 최초 sample에 명시적 지연 주입 | synthetic 표시 + threshold 검출 확인; 성능 값과 합산 금지 |
| R06 | cyclictest 독립 측정 | histogram/JSON 원본 보존, custom probe와 정의 비교 |
| R07 | rtla timerlat | IRQ/thread latency 분리, 임계 초과 trace 수집 |
| R08 | rtla osnoise | 제한된 sampling window로 OS 간섭 관찰 |

기존 S01–S07 서비스/장애/latch 데모는 유지한다. 아래 runner는 실험 전후 정상 상태를
검사하나 **fault를 자동 해제하지 않는다**. 안전 monitor가 latch되면 로그를 보존하고
기존 가이드의 명시적 운영자 복구 절차를 따른다.

```sh
python3 /usr/libexec/apollo/rt-experiment.py --allow-private-guest \
  --platform tcg --duration 10 --cpu 1 --qm-cpus 2 3 \
  --priority 50 --period-us 1000 --threshold-us 5000 --external-tools \
  --out /var/tmp/apollo-rt-run-001
```

TCG 기본 관찰 기준은 `5000us`이며 차량 요구사항에서 도출한 budget이 아니다.
기존 `1000us`는 검출 예시였고, 실제 대시보드 R01 최대 4817us 및 R03 최대 1456us
관찰을 고려해 TCG 데모 기준을 잠정 5ms로 분리했다. 반복 측정/다른 호스트에서의
통계적 보장이나 WCET를 의미하지 않는다. `--threshold-us`로 명시 재설정할 수 있으며
QBox/hardware의 미지정 기본값은 1000us로 유지한다(이 값 역시 요구사항 budget은 아님).
R01은 SCHED_OTHER 비교용 baseline이며 초과 수치는 남기되 RT 합격 여부의 gate에서는
제외한다. R05는 합성 지연 검출이고 성능 판정과 구분한다.
runner exit 0 = 유효한 RT 관찰 또는 baseline/검출 완료, exit 2 = 유효한 RT 단계의 **초과
관찰**, exit 1 = 측정/부하/정책/서비스 검사 실패다. 임계 초과 때문에 다음 실험을
자동 생략하지는 않으므로 전체 results.json을 확인한다.

R06은 `cyclictest --json=파일`을 사용한다. 설치된 2.10은 잘못된 옵션에도 exit 0을
반환할 수 있으므로 종료 코드만으로 PASS를 판정하지 않는다. JSON의 thread별
`cycles > 0` 및 min/max를 검사하며, `--external-tools`를 요청했는데 도구가 없거나
유효 sample이 없으면 전체 측정은 FAIL이다. cyclictest 최대 지연도 임계값 판정에 포함한다.

sample 통계: min/mean/max/p50/p95/p99/p999, threshold_exceedances, missed_periods,
minor/major fault 변화량, actual scheduler/affinity, CLOCK_MONOTONIC 해상도,
first/max 초과 시각을 저장한다. missed_periods는 지연 때문에 건너뛴 주기 수다.
각 주기를 따라잡는 busy catch-up은 하지 않는다. 따라서 sample 수뿐 아니라 missed
period와 최대값도 같이 봐야 한다. percentile은 유한 관찰 구간의 통계이며 WCET가 아니다.
R01/R02는 같은 PREEMPT_RT 커널의 정책 비교다. non-RT 커널 대조군이 없으므로
이 결과만으로 PREEMPT_RT 패치 자체의 개선 폭을 주장하지 않는다.

R03/R04의 부하는 고유 이름의 transient unit이고 종료 시 해당 unit만 정리한다.
RuntimeMaxSec는 보조 제한이다. root RT 측정에는 RLIMIT_RTTIME 보호를 사용하고
IRQ thread보다 무조건 높은 priority 99를 적용하지 않는다.

## 6. 임계값 초과 원인 추적 [target guest root]

trace 수집은 측정에 overhead를 더하므로 baseline과 별도로 실행한다. 다른 tracing
session이나 instance가 있으면 소유자가 종료할 때까지 새 수집을 시작하지 않는다.

```sh
mountpoint -q /sys/kernel/tracing || mount -t tracefs tracefs /sys/kernel/tracing
cat /sys/kernel/tracing/available_tracers
python3 /usr/libexec/apollo/rt-trace.py --allow-private-guest \
  --mode timerlat --cpu 1 --priority 50 --duration 10 --threshold-us 5000 \
  --out /var/tmp/apollo-timerlat-001
python3 /usr/libexec/apollo/rt-trace.py --allow-private-guest \
  --mode osnoise --cpu 1 --priority 50 --duration 5 --threshold-us 5000 \
  --out /var/tmp/apollo-osnoise-001
```

도구가 없거나 실행 커널에 tracer가 없으면 UNSUPPORTED(exit 77)로 기록한다.
수집 성공은 latency budget PASS가 아니다. threshold trace는 실제 임계 초과 때
생성되므로 파일이 없다고 곧바로 장애로 판단하지 말고 histogram과 종료 원인을 본다.
RTLA의 threshold-stop exit 2는 stop marker·유효 sample·저장된 trace·설정 복원이
모두 확인될 때 수집 PASS / latency EXCEEDED로 분류한다. BTF 없는 현재 커널에서
libbpf 경고 후 tracefs fallback이 사용될 수 있다. 유효 histogram 없이 경고만
남은 실행을 성공으로 판단하지 않는다.

분석 순서:

1. timer IRQ 자체가 늦었는지, IRQ 이후 thread dispatch가 늦었는지 구분한다.
2. 보존된 trace의 IRQ/softirq/scheduler activity와 first/max monotonic 시각을 비교한다.
   도구별 trace clock/time domain이 다르면 직접 timestamp를 빼지 않는다.
3. `/proc/interrupts`, `/proc/softirqs`, CPU pressure, RT bandwidth, page fault와
   해당 CPU의 runnable/RT thread를 확인한다. `chrt -p PID`, `taskset -pc PID`로 실제
   정책을 읽는다. 고정원인 없이 priority/timeout부터 올리지 않는다.
4. TCG에서는 guest 밖 host scheduling/VM exit/에뮬레이션 지연도 포함되며 guest
   trace만으로 전부 설명할 수 없다. 동일 kernel·rootfs·부하를 물리 보드에서 반복한다.

기준: [kernel timerlat](https://docs.kernel.org/trace/timerlat-tracer.html),
[RTLA histogram](https://docs.kernel.org/tools/rtla/rtla-timerlat-hist.html),
[osnoise](https://docs.kernel.org/trace/osnoise-tracer.html).
실행 바이너리의 help가 최신 웹 문서와 다르면 설치 버전의 지원 옵션을 우선한다.

`oslat`은 CPU를 점유하는 진단이므로 물리 보드의 별도 CPU에서 짧은 bounded 테스트로
시작한다. `hwlat`은 IRQ를 끄는 busy loop를 사용하므로 운용 중 Automotive workload와
같이 실행하지 않는다. 이번 자동 suite에는 포함하지 않는다.

## 7. 추가 부하·PCP 및 장시간 실험

QM의 선택적 memory 부하는 private guest에서 `stress-ng --vm 1 --vm-bytes 128M
--timeout 10s --metrics-brief`처럼 1 GiB 한도보다 작게 시작한다. I/O 실험은 별도
disposable data disk에만 fio 파일을 만들고 OS/bootctl partition을 직접 쓰지 않는다.
PCP를 사용할 때는 manifest root RPM에 `pcp`, `pcp-system-tools`,
`pcp-export-pcp2json`을 선택 추가하고 공식 PCP 문서의 bounded pmlogger 절차를 따른다.
PCP/trace 없는 baseline과 도구를 켠 run을 나눠 관측 overhead를 비교한다.
QM의 stress-ng는 전체 `--rt-tools` 이미지에 포함된다. regular 빠른 staging은 root에만
RPM을 설치하므로 QM 내부 `podman exec qm sh -c 'command -v stress-ng'`부터 확인한다.
없으면 선택적 memory 실험은 UNSUPPORTED로 남긴다. R03의 동봉 CPU load probe는
QM에도 staging하므로 이 선택 패키지에 의존하지 않는다.

물리 보드 qualification에서는 cold/warm boot, idle/CPU/memory/I/O/network 부하,
IRQ affinity, 온도·전력·governor·DVFS, 여러 반복과 충분한 장시간 관찰을 포함한다.
CPU/IRQ 격리나 RT throttling 변경은 baseline 이후 별도 실험으로 수행하고 원래 값을
보존·복구한다. 최대 관찰값, 초과 건수, sample/missed count, 부하 유효성, 측정 시간을
모두 보고한다. 실험 결과만으로 ASIL-B/FFI/FTTI/WCET 또는 실제 제어 안전성을 주장하지 않는다.

## 8. 증거 회수와 종료

```sh
# guest: tar RPM에 의존하지 않는다. 생성한 실험 디렉터리를 모두 명시한다.
cd /var/tmp
python3 -m tarfile -c apollo-rt-evidence.tar.gz \
  apollo-rt-run-001 apollo-timerlat-001 apollo-osnoise-001
# host에서 해당 SSH 인증 방식으로 SCP 회수 후, guest:
systemctl poweroff
```

host에는 results/원본 tool 로그/trace/launch.json/UART/커널 SHA/manifest/provenance를
보존한다. VM 종료를 확인한 후 재부팅한다. 이전 evidence 디렉터리나 JSON을 덮어쓰지 않는다.
