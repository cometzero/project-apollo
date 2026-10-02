# Apollo QVP runtime idle 개선

2026-10-03. [변경 전 측정](qbox-runtime-load.md)에 따른 구현 기록이다.
대상은 `apollo-qvp`이며 AP/SI CL1 PFDI 주기는 기존 3000 ms를 유지한다.
유휴 CPU 측정과 기능 검증 원본은 아래 증거 경로에 보관한다.

## 적용 내용

| 대상 | 변경 | 목적 |
|---|---|---|
| SI CL0 QEMU | 기본 TCG `SINGLE` → `MULTI` | WFE 반복에 따른 SystemC 동기화 비용 감소 |
| RSE M-profile | WFI/WFE 대기 이유 분리, event register 원자적 접근 | WFI가 남은 SEV event 때문에 계속 실행되는 문제 수정 |
| SI CL0 SCP | IRQ를 막고 최종 event queue를 확인한 뒤 `DSB; WFI` | 큐 처리와 대기 사이의 wakeup 누락 방지 및 실제 idle 대기 |
| AP Linux | `CONFIG_NO_HZ_IDLE=y`, `CONFIG_HZ_100=y` | idle scheduling tick 제거, 실행 중 주기 tick을 4 ms → 10 ms로 변경 |
| AP QVP DT | 미구현 CPU/cluster PSCI powerdown 상태 광고 제거 | architectural WFI idle에서 timer wake 유지 |
| SI CL1 Zephyr | 기존 100 Hz 유지, tickless 설정 명시 | 기존 10 ms tick 단위와 deadline 기반 timer 동작 유지 |
| SI CL0 SCMI | Performance Fast Channels 비활성화 | 40 ms polling 제거, 일반 SCMI mailbox 요청 및 MHU IRQ 응답 사용 |

Linux 설정 소유자는 `arch/arm64/configs/apollo_qvp_defconfig`다.
FVP 설정, 125 MHz architectural counter, MMIO 주소 및 IRQ 번호는 변경하지 않는다.
`HZ=100`은 scheduling tick의 단위이며 explicit high-resolution timer를
10 ms보다 짧게 예약하지 못하게 하는 제한은 아니다.

SCMI fast channel을 비활성화하면 Linux가 해당 capability를 발견하지 않으므로
`LEVEL_SET`/`LEVEL_GET` 메시지를 사용한다. 이 구성은 `fast_switch`를 제공하지
않는다. 일반 cpufreq governor와 SCMI DVFS 인터페이스는 유지하며 실제 왕복
통신으로 검증한다. QBox의 CPU 실행 속도와 DVFS 설정값의 물리적 연동은
기존과 같이 `UNSUPPORTED`다.
Linux MHU 드라이버의 전송 완료 확인은 별도 경로다. 현재 PBX의
`txdone_poll=true`, `txpoll_period=1`은 활성 전송 동안의 1 ms ACK 확인이며
유휴 상태의 SCMI fast-channel 40 ms 주기 polling과 구분한다. SCMI 응답은
MHU 수신 IRQ로 완료되며, 활성 전송 ACK 확인 주기는 유지한다.

## AP powerdown 상태의 검증 경계

첫 full-system 실행 `after`는 Linux MMIO broadcast timer 등록 후 정지했다.
QMP로 읽은 AP 4 CPU 모두 PC `0xf414`였으며, 실행 이미지와 일치하는 BL31 ELF에서
이는 `psci_pwrdown_cpu_end_wakeup()`의 WFI 다음 명령이다. GIC CPU interface를
끄고 진입하는 powerdown 경로다. NS timer frame `0x1a830000`은 deadline이 지난
상태에서 `CNTP_CTL=0x5`(enabled, unmasked, ISTATUS)였다. 이 읽기만으로 실제
IRQ callback 실행을 증명할 수는 없으며, GIC의 QMP physical debug read도
모두 0이어서 IRQ 전달 여부의 증거로 사용하지 않았다.

기존 QVP DT는 CPU/cluster powerdown 인자 `0x10000`/`0x1010000` 및
최소 residency 4.2/4.5 ms를 광고했다. NO_HZ/HZ100은 기존 4 ms 주기 tick에서
잘 선택되지 않던 해당 경로를 활성화할 수 있다. 현재 host PPU에는 GIC wake-request를
받아 powerdown에서 복귀하는 연결이 없다. 따라서 QVP 전용 DTSI에서 해당 상태 및
CPU 참조를 제거하고 지원하는 architectural WFI idle을 사용한다. FVP DT는 유지한다.

QVP에서 광고하는 idle 상태를 실제 지원 범위에 맞추는 변경이다.
DT 비교에서 차이는 idle-state 3개 노드와 16개 CPU의
`cpu-idle-states` 속성뿐이다. PSCI cpuidle driver가 등록되지 않으므로
`current_driver=none`, per-CPU `state*` 부재가 정상이며, scheduler의 기본 WFI
경로에서도 `NO_HZ_IDLE`은 동작한다. 깊은 powerdown과 그 residency/latency는
`UNSUPPORTED`이며 FVP 3-state 동등성 PASS로 보고하지 않는다.
기존 `cpuidle` validation profile은 실제 DT와 sysfs가 이 계약에 일치하는지
모든 명령에서 확인한 뒤, 기존 결과 형식의 `BLOCKED`와
`unsupported:psci_powerdown_wakeup_unmodeled` 사유를 기록한다. 드라이버 부재만으로
미지원 판정을 내리지 않으며, 기존 3-state 판정 및 잘못된 결과의 실패는 유지한다.

## SI CL0/CL1 timer 점검

| 항목 | 주기/조건 | 판단 |
|---|---|---|
| SI CL0 architectural timer | 다음 alarm deadline에 맞춘 one-shot | 고정 1 ms scheduler tick 없음 |
| SI CL0 SCMI Performance Fast Channels | 기존 40 ms | QVP에서 기능을 꺼 polling 제거 |
| SI CL0 debugger CLI UART | 100 ms polling | 유지 |
| SI CL0 DVFS retry | 요청 처리 실패/지연 시 1 ms | idle polling이 아니며 1200 us 전환 지연 계약과 관련되어 유지 |
| SI CL0 watchdog recovery | recovery 중 10 ms 재검사, 100 ms deadline | 정상 idle timer가 아니므로 유지 |
| SI CL0 RSE recovery | 10 s one-shot | 유지 |
| SI CL1 Zephyr | 100 Hz, tickless, timeslice 0 | 이미 10 ms 단위; idle에서 매 tick IRQ를 발생시키지 않음 |
| SI CL1 SCMI 응답 대기 | 활성 요청 중 10 us bounded busy wait | 평상시 idle 부하와 구분, 유지 |

SI CL1 UART 수신은 IRQ 기반이며, PFDI thread는 3000 ms message-queue timeout을
사용한다. 전역 quantum을 늘리거나 watchdog/PFDI 기능을 끄는 방법은 사용하지 않는다.

## 검증 및 증거

### 부하 및 timer 측정

| 항목 | 변경 전 | 변경 후 |
|---|---:|---:|
| 전체 QBox host CPU | 307.14% | 12.72% |
| SystemC main | 76.95% | 2.15% |
| RSE vCPU | 99.90% | 0.18% |
| SI CL0 vCPU | 97.73% | 1.39% |
| AP 4 vCPU 합 | 28.29% | 6.11% |
| SI CL1 4 vCPU 합 | 0.47% | 0.61% |
| 기타 helper | 3.82% | 2.23% |
| simulation second / host second | 1.00139 | 1.00152 |

변경 후 값은 `after-wfi`, `after-verified`의 **30초 × 3구간 × 2실행**을
시간 가중 평균한 것이다. 각 실행 평균은 12.30%, 13.14%이며 기준 대비
전체 비용 감소는 **95.86%**다. 모든 idle 변경의 결합 효과로,
40 ms polling 제거 한 항목의 절감량을 분리해 측정한 수치는 아니다.
기준은 직전 조사에서 같은 호스트·CPU 구성·PFDI 주기로 수집한 값이며
호스트를 독점 격리한 측정은 아니다.

guest snapshot 간 AP architectural timer IRQ는 4 CPU 합 약 **37.81회/s**로,
기준 약 1000회/s보다 줄었다. 별도 busy CPU0 검사는 **100.32회/s**였고,
실행 중 `/proc/config.gz`에서도 `NO_HZ_IDLE=y`, `HZ=100`, `PREEMPT_RT=y`를
확인했다. SI CL1 부팅 marker는 `ticks_per_sec=100 tickless=1`이다.

`functional-final`의 SCMI 검사에서는 performance→2500000 kHz,
powersave→1800000 kHz를 `cpuinfo_cur_freq`로 확인했다. `LEVEL_SET` 2건,
`LEVEL_GET` 4건 모두 `poll=0`, 응답 수신 및 성공을 기록했고 MHU INTID145는
6회 증가했다. Performance Fast Channel trace는 0건이다. 검사 후
`schedutil`, min/max 1800000/2500000 kHz를 복원했다.

제품 `nexios-image` 실행은 30초 × 3구간 평균 **97.09%**, sim/wall **1.0013**였다.
AP vCPU 합 87.71%, SI CL0 0.44%, RSE 0.16%를 기록했다. 제품 서비스가 포함된
별도 workload이며 위 BSP 기준과 직접 비교하지 않는다. PFDI 서비스는 active,
설정은 3000 ms였고 해당 검사에서 error/timeout은 없었다. 제품의 busy CPU0
timer도 **100.64회/s**, SCMI IRQ 전환 검사도 PASS였다. 다른 CPU의 IRQ는
활성 high-resolution timer 등의 영향으로 100회/s를 넘을 수 있다.

### 최종 검증 결과

| 검사 | 결과 | 증거 |
|---|---|---|
| QBox/libqemu/SCP/Zephyr/Linux 및 BSP·제품 이미지 통합 빌드 | PASS | `build-integrated.log` |
| WFI 전용 QVP DT 반영 이미지 재빌드 | PASS | `build-wfi-dt.log` |
| Native platform/core | 127/127 PASS | `final-log-do_check`, `final-qbox-core-unit-tests-log` |
| SCP framework | 26/26 PASS | `scp-framework-ctest.log` |
| Fast-channel CMake cache 전환 | 3/3 PASS | `scp-fast-channel-config/summary.json` |
| 최종 Python 설정/DT/validation 회귀 | 110/110 PASS | `tests-final.log` |
| BSP boot/post-login, timer snapshot, busy tick, SCMI IRQ | PASS | `functional-final/`, `functional-final-run.json` |
| AP PFDI 오류 주입·모니터링 | 7/7 PASS | `ap-probe-retry/result.json` |
| SI CL1 PFDI 통신·오류 주입·stress | 17/17 PASS | `si-probe/result.json` |
| 제품 boot/post-login/PFDI 서비스/tick/SCMI IRQ | PASS | `product/`, `product-run.json` |

PFDI는 현재 펌웨어의 stub implementation을 포함한 기능/API 검증이며
vendor 진단 라이브러리의 하드웨어 진단 coverage를 뜻하지 않는다.
SCMI IRQ 응답은 idle 상태의 SCP가 요청을 받아 처리하는 경로를 검증하지만,
모든 IRQ 도착 순서나 장시간 전원 관리 조합을 완전 탐색한 것은 아니다.

원본은 [runtime-idle](../build/qbox-apollo-qvp/runtime-idle/)에 보관한다.
CPU 부하는 호스트 논리 CPU 하나를 100%로 표시하며, 동일한 full-system 구성에서
post-login 완료 후 10초 안정화와 30초 × 3구간으로 비교한다. 측정 중 guest 명령,
perf 및 GDB는 실행하지 않는다. timer/SCMI 기능 probe는 측정 구간 밖에서 수행한다.
simulation/host 시간 비율을 함께 확인하여 시뮬레이션 정지를 부하 개선으로 오인하지 않는다.

빌드는 기존 `build/conf/`의 `MACHINE=apollo-qvp`,
`DISTRO=auto-ad-nexios`, `TMPDIR=build/tmp_baremetal`에서 수행한다.

```sh
APOLLO_BUILD_THREADS=3 APOLLO_PARALLEL_MAKE=-j4 \
  ./yocto_build.sh --keep-conf qbox-apollo-qvp-native scp-firmware \
  zephyr-demos-cl1 virtual/kernel nexios-bsp-initramfs nexios-image
python3 build/qbox-apollo-qvp/runtime-idle/run.py verify-new \
  --timer --tick-probe --cpufreq-probe
python3 build/qbox-apollo-qvp/runtime-idle/run.py ap-probe-new --probe pfdi
python3 build/qbox-apollo-qvp/runtime-idle/run.py si-probe-new --probe pfdi-si-cl1
python3 build/qbox-apollo-qvp/runtime-idle/run.py product-new \
  --product --tick-probe --cpufreq-probe
python3 build/qbox-apollo-qvp/runtime-idle/summarize.py
```

실행 label은 재사용하지 않는다. 각 실행은 배포 이미지를 별도 writable copy로
복사하고 SHA256, 실제 runner 명령, 도메인별 console, 원본 counter와 판정을 저장한다.
boot/login launcher의 기본 동작과 달리 이 harness는 canonical Python runner의
post-login 검증을 명시적으로 활성화한다.

첫 component 빌드의 기존 platform 64개 및 core 61개 테스트는 통과했으나,
새 M55 wait 테스트 두 개에서 IRQ stimulus 순서 문제가 드러났다. 실패 원본은
`build-components.log`에 보존한다. IRQ deassert handshake와 atomic 접근 보완 후
최종 native 검사 **64 platform + 63 core = 127개**가 모두 통과했다.
SCP framework idle queue/interrupt-mask 검사 26개, fast-channel CMake 전환 검사
3개, cpuidle capability/registry 검사 54개가 통과했다.

`after-wfi`는 부팅/post-login 및 30초 × 3구간 측정을 완료했으나 후속 tick probe가
BSP의 `taskset` 부재로 실패했다. 측정 데이터와 실패를 함께 보존한다. 재검증에는
Linux `sched_setaffinity` syscall을 사용하는 작은 AArch64 프로그램
`busy-cpu0.S`를 사용하며, CPU0에 고정하고 1초 안정화 후 3초 측정한 뒤 해당 PID를 종료한다.
`after-verified`의 초기 검사용 ELF도 PT_LOAD 정렬 오류로 실패했으며,
4 KiB 정렬로 재링크한 `functional-final`에서 tick/SCMI/boot/post-login이 모두
통과했다. 이 실행의 1초 진단용 부하 표본은 위 성능 비교에서 제외했다.

### 남은 초기 부팅 문제

`after-functional`은 SI CL0 PMIC 초기화 중 `RunOnSysc` 예외와 RSE의
`SCP is not ready`를 기록했다. SCP main loop/WFI 진입 전이며, 동일 종류의
실패가 변경 전 `runtime-load/baseline-perf`와 `pfdi-load-3000ms/product`에도 있다.
예외가 최초 원인인지 종료 과정의 결과인지는 미확정이다.
`after-functional-retry`, `ap-probe`는 RSE의 AP 전원 상태 readback에서 실패했다.
같은 오류가 변경 전 `dma-i2s-implementation-20261001/p3-full-pio-warm3/pio`에도 있다.
해당 기존 경로는 고정 NOP 대기 후 doorbell을 한 번 검사하므로 응답 지연에
취약하지만, 이번 실패의 세부 반환값이 없어 원인은 확정하지 않는다.
입력 SHA256은 성공 실행과 일치하며 실패 원본은 `boot-failure-analysis.json`에
연결했다. 성공한 재시도로 초기 부팅 신뢰성이 해결됐다고 판단하지 않는다.

이 검증은 functional boot, 통신, timer 및 idle CPU 비용을 대상으로 한다.
물리 저전력 소비량, RTL/FVP timing parity, 장시간 RT 지연 상한, 모든 reset/power
전환 또는 활성 audio/DMA workload 전체를 검증했다는 뜻은 아니다.
