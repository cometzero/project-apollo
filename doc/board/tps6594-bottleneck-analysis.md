# TPS6594 부팅 병목: Linux와 QBox 구간별 실측

측정일: 2026-09-20. 대상: Apollo QVP BSP initramfs, I2C0의 TPS6594 4개.
Linux HEAD `ca13373f75ee8775a0055647b6a963c117887315`,
QBox HEAD `a009617f63eae6e0a935136158938f822b49db7a`.
Linux TPS6594 driver는 원본이며 ramp/ACK 최적화를 적용하지 않았다.

## 결론

Linux regulator IRQ 초기화가 PMIC당 1,118회의 작은 ACK write를 만든다.
각 전송에서 가장 오래 걸리는 구간은 TX_EMPTY 처리부터 STOP_DET 처리까지다.
Host 계측에서는 DW I2C controller의 byte별 `wait(10 us, reset_event)`가
가장 큰 누적 시간을 차지했다. 레지스터 처리 연산이나 DMA signal 갱신보다
SystemC timed event를 진행하고 QEMU CPU와 동기화하는 경로가 우선 조사 대상이다.
`Bringing ...uV`는 긴 ramp sleep 자체를 의미하지 않는다.

## 1. Linux 내부: 원본 드라이버 kprobe + I2C tracepoint

PMIC `0-0068`의 parent driver를 재bind하여 regulator probe를 계측했다.
Child regulator만 unbind하면 parent 소유 devm IRQ와 child rdev 수명이 어긋날 수
있으므로 이 방법은 사용하지 않았다. 테스트 consumer 9개가 disabled인 것을
확인했다. 재bind 시 voltage selector는 이미 설정돼 있으므로 cold boot의
전압 변경까지 동일하게 재현한 측정은 아니다.

| regulator probe 내부 | 횟수 | guest trace 시간 |
| --- | ---: | ---: |
| `tps6594_regulator_probe` | 1 | 7.447713 s |
| `regmap_irq_sync_unlock` | 38 | 7.242895 s (probe의 97.25%) |
| `i2c_dw_xfer` | 1,139 | 7.168974 s |
| transfer completion wait | 1,139 | 6.358429 s |
| DW ISR | 2,278 | 0.710639 s |

위 시간은 중첩된 inclusive 시간이다. 서로 합산할 수 없다.
전송 1,139회는 2-byte ACK write 1,118회와 register read 21회다.
IRQ 초기화는 rail 9개 × IRQ 4개 + VCCA IRQ 2개 = 38회다.
17개 status bank 중 masked bit가 남은 bank마다 ACK를 2회 기록한다.
완전히 unmask된 bank는 이후 순회에서 빠지므로 단순히 38×17×2가 아니다.
실측은 `34×7 + 32×8 + 30×4 + 28×8 + 26×8 + 24×3 = 1,118`이다.

전송 함수 안의 서로 겹치지 않는 구간:

| 구간 | guest 시간 |
| --- | ---: |
| 진입 → controller init | 0.119823 s |
| controller init | 0.414182 s |
| init → completion wait | 0.052610 s |
| completion wait | 6.358429 s |
| 복귀/정리 | 0.223930 s |

completion wait를 IRQ 처리 시점으로 나누면:

| 구간 | guest 시간 | 의미 |
| --- | ---: | --- |
| wait 진입 → TX_EMPTY 처리 | 0.387511 s | FIFO 공급을 시작하기까지 |
| TX_EMPTY → STOP_DET 처리 | **5.626932 s** | **wait의 88.50%, 전송당 평균 4.940 ms** |
| STOP_DET → wait 복귀 | 0.343986 s | 완료 ISR와 task 재개 |

이 시각은 Linux ISR 내부 관측점이다. 두 번째 구간에는 FIFO MMIO,
모델 전송, 완료 IRQ 전달 비용이 포함된다. 따라서 guest trace만으로 이를
전부 device 연산 또는 전부 IRQ 지연이라고 단정하지 않고 host 계측과 대조했다.

Parent bind 중 수집된 trace 이벤트 구간은 guest 7.984518 s이며 별도 host SSH 측정은
tracing off 8.403109 s, on 8.302997 s였다. 각 1회이며 SSH 비용 포함이다.
Trace 16,994/16,994 events, overwrite/drop/kretprobe miss/unmatched pair 모두 0.
Probe와 모든 전송은 정상 완료했다. 종료 시 consumer 수동 bind가 EBUSY였지만
9개 모두 자동 재bind되어 driver symlink와 disabled 상태를 확인했다.

소스 근거 (Linux):

- [regulator driver](../../hsoc-stack/components/primary_compute/linux/drivers/regulator/tps6594-regulator.c): IRQ 개수 596/598, 등록 순서 778/795/818.
- [MFD driver](../../hsoc-stack/components/primary_compute/linux/drivers/mfd/tps6594-core.c): bank 276, ACK 설정 534.
- [regmap IRQ](../../hsoc-stack/components/primary_compute/linux/drivers/base/regmap/regmap-irq.c): masked bank 검사 163, ACK write 168/173.

## 2. QBox 내부: host monotonic clock 계측

QBox에 환경변수로 활성화되는 임시 계측을 추가하고 실제 cold boot를 실행했다.
Linux trace와 별도 실행이다. 계측 patch는 재현용 evidence로 보관한다.
`host-profile-final`에서 첫 BUCK1 로그 → 네 번째 RTC 등록은 27.684 host s였다.

| 계측 경계 | 횟수/범위 | 누적 host 시간 |
| --- | --- | ---: |
| controller byte latency wait | PMIC 4개, 10,200 bytes | **21.224042 s** |
| I2C0 MMIO 왕복 | 139,856 accesses | 1.762275 s |
| ↳ SystemC job 진입 전 | 위 MMIO에 포함 | 0.864584 s |
| ↳ b_transport 실행 | 위 MMIO에 포함 | 0.076962 s |
| ↳ job 완료 → future 복귀 | 위 MMIO에 포함 | 0.768802 s |
| ↳ BQL 재획득 | 위 MMIO에 포함 | 0.051927 s |
| I2C bus/slave b_transport 실행 | PMIC bytes | 0.028679 s |
| slave가 annotation한 100 ns 대기 | PMIC bytes | 0.061962 s |
| controller update_irq 실행 | 159,956 calls | 0.009197 s |
| DMA output 갱신 실행 | 149,756 calls | 0.004190 s |
| controller IRQ drive 실행 | 20,330 edges | 0.055369 s |

`10 us` 설정에 대해 byte당 평균 host 경과 시간은 **2.081 ms**였다.
이는 2 ms sleep 설정이 있다는 뜻이 아니다. 이 wait가 풀리기까지 다른
SystemC/QEMU 작업, 시간 동기화, host scheduling이 함께 진행된다.
따라서 위 표는 host CPU 사용 시간도, 서로 배타적인 분해도 아니다.
MMIO 집계는 전체 부팅 범위이며 SI CL0의 동일 숫자 주소 접근 1회도 포함한다.
Model 집계도 전체 부팅이므로 27.684 s 로그 구간에 나누어 엄밀한 점유율로
표현하지 않는다. 그럼에도 byte wait와 실제 모델 연산의 규모 차이는 명확하다.

앞선 DMA event 제거 우선 제안은 실측으로 우선순위를 낮춘다.
직접 실행 비용 4 ms는 수십 초 지연의 주원인이 아니다. 이벤트 간접 영향까지
이 수치 하나로 완전히 배제할 수는 없다. MMIO queue도 부차적인 비용이다.

## 3. SystemC 시간 진행과 quantum keeper

- [freerunning QK](../../hsoc-stack/tools/qbox/systemc-components/common/include/qkmulti-freerunning.h)는 `need_sync=false`여도 공통 `timehandler()`를 사용한다.
- [QK timehandler](../../hsoc-stack/tools/qbox/systemc-components/common/src/libgssync/qkmultithread.cc):48–59는 RUNNING CPU의 current time이 SystemC 시간보다 앞서지 못하면 `sc_suspend_all()`을 호출한다.
- 실제 provider의 SystemC `sc_simcontext.cpp:1377`은 `!m_suspend || m_unsuspendable` 조건에서 미래 timed event를 선택한다.
- SystemC async suspend는 host semaphore를 기다리고 외부 asynchronous update가 이를 깨운다.
- [CPU bridge](../../hsoc-stack/tools/qbox/qemu-components/common/include/cpu.h)의 MMIO/time update, CPU loop, deadline callback, WFI/halt가 QK 진행에 관여한다.
- [fabric.lua](../../hsoc-stack/tools/qbox-platform/platforms/apollo/hw-block/fabric.lua)의 global quantum은 10 ms다. 이것을 매 byte마다 10 ms sleep한다고 해석하면 안 된다.

즉 `wait(10 us)`의 숫자를 줄이는 것만으로 host wait가 비례해서 줄어들지
않을 수 있다. SystemC의 다음 양의 시간 이벤트를 실행할 수 있는지가 중요하다.

### Quantum keeper 실측

Monitor `/qk_status`를 약 50 ms 간격으로 조회한 별도 기본 설정 부팅에서
786개 표본을 확보했다. `sc_waiting=true` 횟수는 CL1 CPU0 548,
CPU1 133, CPU2 43, CPU3 31이었다. AP 4개, RSE, CL0는 모두 0이었다.
표본은 비원자적 상태 조회이며 서로 겹칠 수 있다. 이를 정확한 suspend 시간
점유율이나 해당 CPU가 유일한 원인이라는 증명으로 사용하지 않는다.

CL1은 `si_cl1.lua:72`의 `managed_start_in_reset_release=true`를 사용한다.
`cpu.h:435–441`의 `wait_for_work()`는 managed reset이 release된 CPU에 대해
QK를 stop하지 않는다. 따라서 guest CPU가 idle이어도 QK가 RUNNING으로
남아 SystemC 진행 조건에 관여할 수 있다. 이 경로와 deadline time update가
우선적인 수정 검토 지점이다. 일반 halt pin callback과 guest idle 경로는 다르다.
CL1 로그에는 4개 core가 모두 올라왔으므로 단순한 secondary 미기동으로
설명하지 않는다. 정확한 idle/WFI 상태의 인과관계는 추가 계측이 필요하다.

Monitor 실행에서는 PMIC 로그 구간 40.172 s, byte wait 33.728 s였다.
Monitor 없는 27.684 s 실행과 차이가 크므로 측정 perturbation/실행 변동을
인정한다. 표본 횟수와 source 경로를 원인 후보를 좁히는 용도로 사용한다.

### Controller만 zero latency로 바꾼 진단

동일 monitor/profile 방식에서 controller `transfer_latency="0 ns"`만
설정하고 PMIC `access_latency=100 ns`는 유지했다. 10,200 bytes가 같았으며:

| 경계 | 기본 10 us / 100 ns | controller 0 / slave 100 ns |
| --- | ---: | ---: |
| PMIC 로그 구간 | 40.172 s | 38.459 s |
| controller byte wait | 33.728 s | **0.016982 s** |
| slave annotated delay wait | 0.070143 s | **32.065996 s** |

Controller를 zero-time delta wait로 바꾸면 대기 비용이 사라지는 대신
바로 다음 100 ns positive-time wait로 이동한다. 이것은 10 us 자체의 길이나
controller 연산이 아니라 **다음 simulated-time 진행 경계**에 큰 비용이 있음을
보여준다. Controller latency만 줄이는 변경을 해결책으로 삼을 근거는 없다.

### Controller와 slave 모두 zero latency로 둔 진단

동일 방식으로 controller와 TPS6594 4개의 latency를 모두 0으로 설정했다.

| 설정 | PMIC 로그 구간 (host) | controller wait | slave wait | PMIC bytes |
| --- | ---: | ---: | ---: | ---: |
| 10 us / 100 ns | 40.172 s | 33.728160 s | 0.070143 s | 10,200 |
| 0 / 100 ns | 38.459 s | 0.016982 s | 32.065996 s | 10,200 |
| 0 / 0 | **5.796 s** | 0.016813 s | 0.000254 s | 10,200 |

세 실행 모두 BSP ready/SSH에 도달했다. 양의 시간 대기 두 곳을 제거하면
PMIC 구간이 크게 단축됐다. 단, controller IRQ edge 수도 20,318에서
10,200으로 바뀌었다. Zero-time 진행에서 IRQ 발생·처리 순서 또는 level 변화 병합이
달라졌을 가능성이 있으므로 34.376 s 차이를 순수한 단일 wait의 효과로
정확히 분리할 수는 없다. 각 1회 측정이며 전체 I2C 회귀 검증도 아니다.
동일 byte count는 전송량 유지 근거이며 모든 device 동작 동등성의 증명은 아니다.

이 실험은 성능 패치를 적용하려는 것이 아니라 대기 경계를 구분하기 위한
진단이다. 실행별 CLI override만 사용했고 platform 기본값은 바꾸지 않았다.

## 4. 개선 검토의 우선순위

1. **공용 CPU/QK의 idle 계약 확인:** CL1 managed reset 해제와 실제 idle을
   분리하여, 일할 수 없는 CPU가 SystemC 미래 이벤트를 계속 막아야 하는지
   검토한다. `wait_for_work()`에서 무조건 QK를 stop하는 수정도 reset release,
   wakeup, deadline, Zephyr SMP 회귀를 만들 수 있으므로 바로 적용하지 않는다.
2. **QK current-time 갱신/통지:** RUNNING QK가 뒤처졌을 때 진짜 실행 중인
   CPU와 idle CPU를 구분하고 필요한 시간 갱신을 전달하는 경로를 검토한다.
   global quantum만 임의로 줄이는 것으로 정확성이나 성능을 보장하지 않는다.
3. **I2C 모델:** timed wait 수를 줄이는 구현은 protocol/reset/IRQ ordering과
   timing 계약을 보존해야 한다. zero latency는 경계 식별용 진단이며 최종
   모델 수정으로 제안하지 않는다.
4. **MMIO queue/DMA event:** 위 경계가 해결된 뒤 재계측해 판단한다.
   Linux ACK driver 최적화는 현재 요청에 따라 적용 대상에서 제외한다.

## 5. 재현 자료와 범위

Evidence root: `build/qbox-apollo-qvp/pmic-bottleneck-20260920/`.

- `clean-guest/guest-analysis.json`, `guest-trace.log`, `guest-trace-health.log`: 최종 guest 계측.
- `clean-guest/guest-measurement.json`, `restore-verified.log`: host bind 시간 및 consumer 상태.
- `host-profile-final/host-analysis.json`, `runtime/qbox-platform.log`: host 구간별 계측.
- `host-monitor-{default,zero,allzero}/`: CCI 비교, runtime command, QK samples와 host summary.
- `host-profile.patch`: 임시 계측 코드와 정확한 측정 경계.
- `analyze_guest_trace.py`, `analyze_host_profile.py`: 로그에서 수치를 재계산하는 도구.

초기 root guest trace는 native build와 겹쳐 시간 비교에서 제외했다.
`host-profile`/`host-profile-retry`는 종료 시 summary 회수가 안 되어 최종
집계로 사용하지 않았다. PMIC 이전에 실패한 preflight도 성능 비교에서 제외했다.

현재 결과는 이 host에서의 기능 시뮬레이션 병목 분석이다. 물리 I2C timing,
FVP 동등성, 반복 측정 기반 성능 보장은 검증하지 않았다.

## 6. 조사 후 복구 및 검증

임시 계측 patch를 역적용했고 Linux/QBox/platform 작업 트리는 clean이다.
원본 QBox provider의 `populate_sysroot` 재빌드는 905 tasks 모두 성공했다.
Apollo component 60개와 공용 QBox component 60개도 모두 통과했다.
기존 강제 do_check 이력에 대한 warning 1개가 있었다.
설치 산출물의 module shared library에서 `APOLLO_I2C_PROFILE` 문자열이
남지 않은 것을 확인했다. `restore-build.log`, `restore-verification.json` 참조.
복구 바이너리의 별도 재부팅은 수행하지 않았다. 조사용 boot 및 trace 결과와
component test 결과를 구분하며, 이번 작업에서 영구 성능 변경은 적용하지 않았다.
