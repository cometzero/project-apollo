# TPS6594 부팅 지연: QBox/SystemC 개선 검토

> 후속 실측: [구간별 병목 분석](tps6594-bottleneck-analysis.md).
> 아래 개선 순위는 계측 전 가설이다. 실제로는 byte timed wait가
> 지배적이며 DMA 갱신의 직접 실행 비용은 4 ms 수준이었다.
> 우선 조사 대상은 CL1 quantum keeper와 SystemC 시간 진행 경계로 바뀌었다.


2026-09-20. 사용자 요청에 따라 Linux TPS6594 IRQ ACK 수정은 제거했다.
Linux 작업 트리는 clean이며 `ack_invert = 1`, `clear_ack = 1` 상태다.
Ramp override도 없다. 원복 상태로 `nexios-bsp-initramfs`를 재빌드했다
(5793 tasks PASS, 기존 forced-task 이력 warning 5개).
이번 작업은 조사이며 QBox/QEMU/platform 소스의 성능 변경은 적용하지 않았다.

## 확인한 비용 경로

1. Linux는 regulator마다 IRQ 4개를 등록한다. Regmap IRQ mask sync가
   17개 bank에 최대 2번씩 ACK를 쓰므로 인접 rail 사이 최대 136개의
   작은 I2C write가 발생한다. Linux를 유지하면 이 전송 자체는 유지해야 한다.
2. 각 write는 register offset과 value의 2 data bytes다. DW controller는
   byte마다 10 µs를 기다린 후 slave에 접근하며, TPS6594가 추가하는
   100 ns에도 별도 `wait()`를 호출한다. 따라서 정상 2-byte write는
   이 경로에서 timed wait 4번을 거친다.
3. 제어·상태·FIFO MMIO 각각은 QEMU/SystemC bridge를 통과한다.
   `do_regular_access()`는 BQL 해제 → `run_on_sysc()` → BQL 재획득을 한다.
   외부 vCPU thread의 요청에는 job 할당, promise/future, queue mutex,
   asynchronous notification, 완료 대기가 필요하다.
4. I2C 완료 IRQ는 GIC를 거쳐 vCPU kick/wakeup으로 이어진다. Linux는
   STOP_DET 또는 abort 처리 후 transfer completion을 깨운다.
5. `read_register()`와 `write_register()`는 항상 `update_irq()`를 호출한다.
   이 함수는 IRQ level이 같으면 IRQ 통지를 생략하지만 DMA event는 항상
   예약한다. Apollo I2C0의 PMIC 전송은 DMA를 사용하지 않는다.

주요 코드:

- [DW I2C model](../../hsoc-stack/tools/qbox/systemc-components/i2c/src/dw-apb-i2c.cc):
  latency 30–31, read/update 241, DMA event 308–330, byte wait 393–469.
- [TPS6594 model](../../hsoc-stack/tools/qbox/systemc-components/i2c/tps6594/src/tps6594.cc):
  latency 39/165, IRQ level dedup 354–360.
- [MMIO bridge](../../hsoc-stack/tools/qbox/qemu-components/common/include/ports/initiator.h):
  `do_regular_access()` 660–669, I/O lock 735.
- [SystemC work queue](../../hsoc-stack/tools/qbox/systemc-components/common/include/runonsysc.h):
  handler 104, `run_on_sysc()` 216–242.
- [GIC signal bridge](../../hsoc-stack/tools/qbox/qemu-components/common/include/ports/qemu-target-signal-socket.h):
  GPIO/BQL 34–40.
- [Board wiring](../../hsoc-stack/tools/qbox-platform/platforms/apollo/hw-block/ros.lua):
  controller/IRQ binding 221–234.

`10 µs`는 simulated time이며 host wall time 10 µs라는 의미가 아니다.
또한 freerunning quantum keeper의 `need_sync()`는 false이므로 global
quantum 10 ms를 전송마다 강제로 기다린다고 설명할 근거는 없다.
기존 27.5 s → 14.6 s 결과는 Linux ACK 횟수를 줄인 과거 실험이며,
SystemC 최적화의 성능 수치로 재사용해서는 안 된다.

## 소스 변경 없는 CCI 비교 실행

동일하게 원복된 Linux/BSP로 fresh copied disk, 비영속 RSE state,
기본 AP CPU 정책을 사용했다. 시간은 host wall time이며 console sampling은
50 ms다. 각 설정 1회 실행이므로 통계적으로 검증한 개선율이 아니다.

| 설정 | PMIC 첫 BUCK1 → 네 번째 RTC 등록 | Launcher → ready + SSH |
| --- | ---: | ---: |
| 기본 controller 10 µs / slave 100 ns | 33.036 s | 86.130 s |
| controller만 1 µs | 30.564 s | 84.424 s |
| controller 10 µs / PMIC 4개의 slave latency 0 ns | 29.815 s | 83.089 s |

Byte latency를 10배 줄여도 초기화가 비례해 빨라지지 않았다.
별도 slave wait 제거도 이번 표에서는 약 3.2 s 차이지만, 이전 실행의
기본 설정 PMIC 구간이 27.5 s였으므로 host 실행 편차를 제외한 개선이라고
단정할 수 없다. 이 결과만으로 latency 기본값을 바꾸는 것은 권장하지 않는다.

세 실행 모두 boot marker와 SSH 응답을 확인했다. 마지막 실행은
`platform.si_cl0_cpu_0.timehandler`에서 `cci_get_global_broker` hierarchy
오류를 기록했다. 부팅은 계속됐지만 깨끗한 전체 시스템 PASS로 취급하지
않으며 해당 수치는 진단 참고다. 이 비교에서 regulator/GPIO/RTC/EEPROM
기능 시험은 다시 실행하지 않았다.

Artifact 디렉터리는 각각 `systemc-default/`, `systemc-1us-retry/`,
`systemc-no-slave-wait/`이며 `systemc-comparison.json`에 수치를 모았다.
최초 `systemc-1us/`는 CCI JSON string quoting 오류로 시작 전 실패했으며
비교에서 제외했다. 재현 시 시간 문자열의 JSON 따옴표를 유지해야 한다:

```bash
./run_qbox_yocto.sh --bsp --headless --multi-session --copy-disks \
  --no-persistent-rse-state --out-dir build/qbox-apollo-qvp/pmic-1us \
  -- --platform-param 'platform.ap_dw_i2c_0.transfer_latency="1 us"'
```

Slave 대기 제거는 `platform.board_tps6594.access_latency="0 ns"` 및
`board_tps6594_1`, `_2`, `_3`에 같은 값을 전달한다. 모든 override는
해당 프로세스에만 적용했으며 소스·Lua·영구 설정에는 남기지 않았다.
원복 kernel source/Image/DTB hash는 `restore-driver-artifacts.json`에 있다.

## 개선 후보

### 1. I2C controller의 불필요한 event 예약 제거

부작용 없는 status/config read에는 IRQ/DMA 재평가를 생략한다.
FIFO, interrupt mask, clear register, enable/reset 등 실제 상태가 바뀌는
경로에서만 갱신한다. 특히 DMA 비활성 및 request idle 상태에서는
`m_dma_event` 예약을 생략할 수 있다.

범위가 I2C 모델로 한정되고 전송 시간과 Linux 인터페이스를 유지할 수
있어 첫 구현 후보로 적합하다. 단 DMA disable/reset 때 기존 request를
낮추는 event와 pending ACK 처리까지 생략하면 안 된다. 상태 변화표에
기반한 조건이 필요하다. 개선 크기는 아직 측정하지 않았다.
공용 `jobs_handler()` 자체도 매 job 후 zero-time wait를 수행하므로,
DMA event를 생략해도 MMIO 왕복이나 모든 delta cycle이 없어지는 것은 아니다.

### 2. Byte 처리의 두 번 wait를 줄이는 timing 구조

현재의 controller wait와 slave annotated-delay wait를 단일 완료 event로
통합하는 방안을 검토할 수 있다. 단순히 slave를 먼저 호출하고 합산 시간만
기다리면 PMIC GPIO/IRQ/register side effect가 일찍 발생한다.
따라서 byte 완료 시점의 state commit, STOP/RESTART, RX FIFO visibility,
reset/cancel을 보존하는 명시적 계약이 필요하다.

CCI `access_latency=0 ns`는 별도 작은 wait의 비용을 알아보는 진단이다.
아날로그/물리 timing 개선이나 같은 timing을 보존하는 최적화로 간주하지 않는다.
Controller latency를 0으로 만들어 FIFO 전체를 즉시 처리하는 방법도
CPU 접근 및 reset 사이의 interleave를 바꾸므로 그대로 기본값으로 채택하지 않는다.

### 3. 공용 RunOnSysc의 요청 처리 비용 감소

프로파일에서 allocator/futex/queue 비용이 크면 job 및 completion 객체 재사용,
queue가 이미 pending일 때 중복 notification 억제를 검토한다.
동기 MMIO는 한 번에 하나씩 기다릴 수 있어 queue notification 합치기의
효과가 작을 수도 있다. Pool/reuse 역시 cancellation, shutdown, exception,
reentrant access와 lost-wakeup 방지를 보존해야 한다.

영향이 AP 전체 장치로 확장되므로 I2C 모델의 국소 개선 이후 순위다.
QEMU thread에서 SystemC model을 직접 호출하거나 side-effect MMIO에 DMI를
허용하는 shortcut은 올바른 대안이 아니다.

### 우선순위가 낮은 후보

- Bus route는 시작 시 주소별로 만들어 이미 O(1) lookup이다.
  매 byte마다 모든 slave를 검색하는 병목은 없다.
- START/RESTART/STOP/CANCEL broadcast는 여러 slave에 전달되지만,
  기존 transaction 정리와 EEPROM page-write commit에 쓰인다.
  selected slave만 남기는 변경은 protocol 계약부터 검토해야 한다.
- Controller와 PMIC는 이미 IRQ level 변화만 통지한다.
  동일 level IRQ write dedup만 추가하는 효과는 제한적이다.
- CPU sync policy/quantum 변경은 전역 영향이 있으며 이번 권장 변경에
  포함하지 않는다. 필요하면 별도의 진단 실험으로 분리한다.
- MMIO `access_latency=10 ns`는 annotated delay다. 이를 줄여도
  각 MMIO의 host queue/future 왕복은 없어지지 않는다.
- PMIC reset voltage를 DT 목표 전압과 맞추면 `Bringing` 로그와 소수의
  voltage write는 줄지만 rail IRQ 등록의 반복 ACK는 그대로다.
  로그 제거를 주요 병목 해결로 해석해서는 안 된다.

## 구현 전후에 필요한 검증

측정은 PMIC 첫 BUCK1 → 마지막 PMIC RTC 등록 구간으로 제한하고,
MMIO 수, DMA event 예약/실행 수, byte wait 수, IRQ edge 수,
RunOnSysc queue/실행/완료 host 시간을 각각 수집한다. Hot path의 printf
대신 누적 counter와 종료 시 summary를 사용한다. Host profile은
`perf stat`의 context-switches와 allocator/futex 관련 stack을 확인한다.

후보를 하나씩 적용한 뒤 기존 I2C component tests에서 repeated-start,
read ACK/NACK, NACK abort, reset during transfer, FIFO/IRQ/DMA 경계를 검증한다.
Guest에서는 PMIC 4개/36개 regulator/GPIO/RTC 반복 알람과 EEPROM 3개
동시 client를 검증한다. 공용 bridge 변경은 I2S DMA와 AP 다른 MMIO 장치의
회귀까지 필요하다. 빌드·부팅만으로 이 검증을 대체하지 않는다.

증거 디렉터리: `build/qbox-apollo-qvp/pmic-performance-20260920/`.
