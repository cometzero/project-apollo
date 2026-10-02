# Apollo QVP QBox runtime 부하 조사

측정일: 2026-10-02. PFDI는 AP/SI CL1 모두 3000 ms로 고정했다.
대상은 현재 배포된 `apollo-qvp` 전체 시스템과 `nexios-bsp-initramfs`다.
AP 4 CPU, SI CL1 4 CPU, 실제 RSE TF-M과 SI CL0 SCP 펌웨어를 사용했다.
아래는 변경 전 조사 기록이다. 운영 기본값, QEMU 모델, 펌웨어, 커널 설정은
이 조사 단계에서 변경하지 않았다. 후속 적용 및 검증은
[runtime idle 개선 기록](qbox-runtime-idle.md)을 참조한다.

## 결론과 우선순위

1. **단기 후보: SI CL0의 TCG 모드를 MULTI로 변경.** 별도 실행의
   단일 CCI override만으로 전체 host CPU가 **307.14% → 236.44%**,
   약 **23.0%** 감소했다. SystemC 메인 스레드가 **76.95% → 4.33%**로
   줄었다. SI CL0 자체의 idle busy loop는 남는다.
2. **근본 개선: RSE의 WFI/WFE wake 조건 분리.** RSE가 약 100%를 사용하며,
   현재 QEMU에는 M-profile event register가 WFI까지 즉시 반환시키는 경로가
   있다. CPU 상태와 소스 분석은 아래에 기록한다. 수정 후 절감률은 미측정이다.
3. **SI CL0의 실제 idle 대기 구현.** A/R-profile WFE/SEV를 정확히 모델링하거나,
   firmware에서 event queue와 IRQ의 race를 처리하는 idle 진입을 구현한다.
   단순 WFE→WFI 치환은 큐에 남은 이벤트를 놓칠 수 있어 그대로 권고하지 않는다.
4. **AP의 tickless idle 실험.** 현재 idle에서도 AP 전체에 약 1000 timer IRQ/s가
   발생한다. `CONFIG_NO_HZ_IDLE=y`를 QVP 전용 defconfig에서 평가한다.
   커널 재빌드와 변경 후 CPU/IRQ/RT 지연 측정이 필요하다.

후보 2–4의 잠재 절감량을 후보 1의 측정값에 더해 총 절감률로 제시하지 않는다.
도메인 간 동기화 비용이 달라질 수 있고 현재 측정은 유휴 workload다.

## 측정 조건과 결과

100%는 호스트 논리 CPU 하나다. 도메인 수치는 QMP `query-cpus-fast`로 확인한
vCPU host TID의 합이며 해당 도메인의 모든 peripheral/helper 비용은 아니다.
메인 스레드와 나머지 helper 스레드는 별도로 집계했다.

기본 post-login 검증 후 10초 안정화하고 **30초 × 3구간**을 수집했다.
측정 구간 안에는 guest 명령, monitor polling, perf sampling, GDB 중단을
실행하지 않았다. 구간 밖의 guest `/proc/interrupts`와 `/proc/uptime`으로
IRQ 발생률을 별도로 계산했다. SystemC 시간과 `/proc` snapshot은 원자적이지 않다.

| 대상 | 기준: `baseline-perf-retry` | SI0 MULTI: `si0-multi` |
|---|---:|---:|
| 전체 QBox | 307.14% | 236.44% |
| SystemC 메인 | 76.95% | 4.33% |
| RSE vCPU | 99.90% | 99.76% |
| SI CL0 vCPU | 97.73% | 99.23% |
| AP vCPU 4개 합 | 28.29% | 28.51% |
| SI CL1 vCPU 4개 합 | 0.47% | 0.54% |
| 기타 helper | 3.82% | 4.12% |
| simulation seconds / host second | 1.00139 | 1.00136 |

전체 CPU 구간 범위는 기준 **304.56–309.70%**, 변경 **234.01–237.84%**였다.
시뮬레이션 진행률이 같으므로 simulation second당 비용도 약 23.0% 감소했다.
기준 메인 스레드의 76.95% 중 36.68%p는 host kernel CPU 시간이었다.
유저 함수 profiler만으로 이 비용 전체를 설명하거나 분모를 혼용하면 안 된다.

추가 기준 실행 `baseline`에서도 전체 302.30%, 메인 74.26%였다.
SI0 MULTI 반복 실행 `rse-inspect`에서는 전체 **237.18%**, 메인 **4.24%**,
sim/wall **1.00130**이었다. 이 두 실행은 host GDB 아래에서 실행했고,
중단·stack 수집은 90초 측정 뒤에만 수행했다. 각각의 CPU 측정 구간에
perf sampling은 없었다. 반복 결과는 `summary.json`에 보관한다.
호스트는 논리 CPU 16개이며 측정 중 load average 원본도 저장했다.
전용으로 격리한 호스트는 아니며 짧은 구간 평균을 성능 보장으로 해석하지 않는다.

## SI CL0: WFE에서 발생하는 반복 동기화

현재 SCP 배포 ELF에서 `fwk_arch_suspend`의 `0x12000439c`는 `wfe`다.
[framework main loop](../hsoc-stack/components/system_mgmt/scp-firmware/framework/src/fwk_core.c)
는 이벤트 큐와 로그 처리를 마치면 이 함수를 호출한다.

현재 QEMU의
[AArch64 translator](../hsoc-stack/tools/qemu/target/arm/tcg/translate-a64.c)
`trans_WFE()`는 SINGLE에서는 helper를 호출하고 MULTI에서는 이를 생략한다.
[WFE helper](../hsoc-stack/tools/qemu/target/arm/tcg/op_helper.c)는 non-M-profile에서
실제 halt 대신 `EXCP_YIELD`를 발생시킨다. 그 결과
[QBox CPU callback](../hsoc-stack/tools/qbox/qemu-components/common/include/cpu.h)의
`end_of_loop_cb()` → `sync_with_kernel()` → QK `start()/set()/sync()`가 반복된다.
[QK start/set](../hsoc-stack/tools/qbox/systemc-components/common/src/libgssync/qkmultithread.cc)
과 [freerunning sync](../hsoc-stack/tools/qbox/systemc-components/common/include/qkmulti-freerunning.h)
는 SystemC async event를 알린다.

30초 `perf`의 SI0 사용자 공간 표본에서는 mutex lock/unlock, TLS 접근,
조건변수 신호와 async update 경로가 관측됐다. 메인에서는
`sc_prim_channel_registry::perform_update()`, lock wait/wake,
`tlm_quantumkeeper_multithread::timehandler()`가 관측됐다.
이는 단일 설정 변경으로 메인 부하가 크게 줄어든 결과와 일치한다.

재현 override:

```sh
--platform-param platform.si_cl0_qemu_inst.tcg_mode=MULTI
```

이 설정은 SI0 WFE가 만드는 동기화 왕복을 줄이지만 SI0를 재우지는 않는다.
따라서 full-system 부팅/post-login PASS와 유휴 부하 감소를 확인했어도,
정식 기본값 변경 전에는 AP/SI PFDI 오류 주입, SCMI/MHU 연속 통신,
reset/power 전환, timer wake와 장시간 idle 복귀를 추가 검증해야 한다.
RSE는 별도 M-profile WFE 의미가 있으므로 함께 MULTI로 바꾸지 않는다.

QBox 중복 RUNNING 알림을 줄이는 방법도 후속 후보지만, QK의 SystemC
suspend/resume 및 종료 race를 보존해야 한다. 전역 sleep이나 무조건적인
알림 생략으로 대체해서는 안 된다.

## RSE: WFI와 event register

배포 TF-M ELF의 `tfm_idle_thread`는 `0x10001f0e`에서 실제 WFI를 실행한다.
[TF-M idle](../hsoc-stack/components/system_mgmt/trusted-firmware-m/secure_fw/partitions/idle_partition/idle_partition.c)
는 `psa_wait(..., PSA_POLL)`과 WFI를 반복한다.

현재 [arm_cpu_has_work()](../hsoc-stack/tools/qemu/target/arm/cpu.c)는
M-profile `event_register=true`를 무조건 work로 판단한다.
[helper_wfi()](../hsoc-stack/tools/qemu/target/arm/tcg/op_helper.c)는
`cpu_has_work()`가 true이면 halt 없이 반환한다.
[m_helper.c](../hsoc-stack/tools/qemu/target/arm/tcg/m_helper.c)의 exception
진입·복귀 경로는 event register를 설정하고, 이를 소비하는 명령은 WFE다.
WFI-only idle에서는 남은 event가 반복 실행을 유발할 수 있다.

RSE `perf`에는 `liveness_pass_1`, `tcg_gen_code`, `cpu_exec_loop`,
`pmsav8_mpu_lookup`, TB lookup 등이 나타났다. 현재 유휴 비용이 단순히
host의 sleep thread에 귀속된 수치가 아니라 실제 TCG 실행·변환 비용임을 보여준다.

실제 host GDB로 읽은 **20/20 표본**에서 `event_register=true`,
`interrupt_request=0`, `halted=0`이었다. guest PC는
`tfm_spm_partition_psa_wait`, SPM 진입/복귀, `tfm_arch_thread_fn_call`과
idle의 DSB(`0x10001f0a`, WFI 바로 앞)를 포함했다. `rse-state.json`과
`rse-pc-symbols.json`에 원본을 저장했다. 이 상태와 현재 `cpu_has_work()`
분기를 결합하면 event register가 WFI의 halt를 방해하는 조건이 실제로
존재함을 확인할 수 있다. 표본 수집 중 guest register/memory는 수정하지 않았다.
다만 모델 수정 전후 A/B를 수행한 것은 아니므로 RSE 100% 비용 전부가
해당 수정으로 사라진다고 확정하지 않는다.

정식 수정은 WFI와 WFE의 대기 이유를 구분하고 event register를 WFE wake에만
반영하는 방향이다. WFI에서 event register를 무조건 지우면 이후 WFE 동작이
달라진다. 기존 lifecycle 변경 전체를 복원하지 말고 해당 조건만 독립 검토한다.
검증에는 pending IRQ, WFI+event, WFE+SEV/SEVONPEND, exception-return,
reset과 SCMI 응답이 포함되어야 한다. CPU 비용 감소량은 모델 수정 후 별도 측정한다.

## AP: 주기적인 Linux tick

실제 배포 `Image`에서 `scripts/extract-ikconfig`로 추출한 설정은 다음과 같다.

```text
CONFIG_HZ_PERIODIC=y
CONFIG_HZ=250
# CONFIG_NO_HZ_IDLE is not set
CONFIG_HIGH_RES_TIMERS=y
CONFIG_PREEMPT_RT=y
CONFIG_CPU_IDLE=y
```

측정한 AP `arch_timer`는 유휴 상태에서 CPU마다 약 250–253 IRQ/guest-second다.
4 CPU 합계로 약 1000 IRQ/s이며 PFDI 3초 주기와 독립적인 비용이다.
IRQ 수가 AP CPU 비용 전체를 뜻하지는 않으므로 28% 전체가 사라진다고 예측하지 않는다.

`CONFIG_NO_HZ_IDLE=y`는 idle CPU의 scheduling tick을 생략하는 설정이다.
[Linux 공식 NO_HZ 문서](https://www.kernel.org/doc/html/latest/timers/no_hz.html).
QVP 전용 kernel defconfig에서 HZ=250과 PREEMPT_RT를 유지한 채 이 항목만
바꾸어 비교할 것을 제안한다. 주기 task의 지연과 idle 진입 비용도 측정한다.
현재 커널은 해당 기능 자체가 빠져 있으므로 `nohz=on` bootarg만으로는 적용되지 않는다.
FVP 설정과 모든 workload에 대한 기본 정책 변경은 별도로 판단한다.

## 후순위 후보와 적용하지 않은 변경

- Global quantum 10→50ms: 주기 QEMU deadline은 줄일 수 있지만 SI0 WFE마다
  발생하는 명시적 QK 알림은 줄이지 못한다. 이번에는 절감률을 측정하지 않았고,
  timer/IRQ 지연 검증이 필요하여 우선순위를 낮췄다.
- SI0 SCMI fast-channel polling은 소스상 40ms다. idle spin을 해결한 뒤
  실제 사용량을 측정하고 조정해야 하며, 주기 변경은 DVFS 응답에 영향을 준다.
- UART backend는 기본 100ms fallback과 FIFO readiness 대기를 사용한다.
  host timer도 event/deadline 대기 방식이다. 둘을 주범으로 지목할 근거는 없었다.
- 도메인 제거, CPU 개수 축소, `cpulimit`, PFDI 중지, CPU 가속 모드 일괄 변경은
  동일 full-system 기능의 개선 수치로 제시하지 않았다.

## 증거와 재현

원본: [build/qbox-apollo-qvp/runtime-load](../build/qbox-apollo-qvp/runtime-load/).

- `*-command.json`: 실제 runner 명령, 이미지 SHA256, 환경.
- `*-load.json`, `summary.json`: host raw counter, QMP TID, SystemC 시간,
  guest IRQ, 구간별 부하 및 스레드 분류.
- `baseline-perf-retry.perf.data`, `rse-inspect.perf.data`: 별도 30초 profiler 기록.
- `perf-baseline-*.txt`, `perf-clone-symbols.json`: 도메인별 사용자 공간 함수와
  삭제된 QEMU clone DSO 주소의 Build ID 일치 ELF 기반 symbolization.
- `host-stacks.json`: 90초 측정 후 얻은 GDB wall-time 표본. 이 표본은
  on-CPU 표본이 아니므로 CPU 함수 점유율로 사용하지 않았다.
- `rse-state.json`, `rse-pc-symbols.json`: QMP로 식별한 RSE thread의
  CPU 상태 20개와 TF-M ELF 기반 PC 해석. libqemu debug ELF는 실제 로드된
  바이너리와 Build ID `3b6a978dfd15de52520c2c51b63b5fd3e0a03f89`가 일치한다.
- `kernel.config`, `environment.json`: 배포 kernel 설정, host 정보, 저장소 HEAD/status.
- 각 run의 `result.json`, console: 부팅/post-login 및 관측된 실패 원본.

측정 프로그램은 [measure_qbox_pfdi_load.py](../scripts/test/measure_qbox_pfdi_load.py)를
재사용하고 host user/system ticks를 별도 저장하도록 확장했다. parser/accounting
검사 3개가 통과했다. 새 이미지/모델 빌드는 수행하지 않았다.
성공한 4개 실행은 full-system boot/post-login PASS이며 SI PFDI timeout
패턴이 없었다. `rse-inspect`의 model-side timer snapshot도 PASS다.
이는 정밀 timer IRQ latency나 reset/power 검증 결과를 뜻하지 않는다.

```sh
python3 build/qbox-apollo-qvp/runtime-load/run.py <new-baseline-label> --perf
python3 build/qbox-apollo-qvp/runtime-load/run.py <new-multi-label> --perf \
  --param platform.si_cl0_qemu_inst.tcg_mode=MULTI
python3 build/qbox-apollo-qvp/runtime-load/summarize.py
```

이 harness는 현재 배포물을 새 label의 writable input으로 복사한다. 이미 사용한
label로 원본을 덮어쓰지 않는다. perf는 `cpu-clock:u`, 99Hz, DWARF call graph,
30초이며 사용자 공간만 포함한다. 정확한 커널 함수 점유율은 수집하지 않았다.
기준 6928개, SI0 MULTI 6722개 표본을 수집했으며 lost sample은 0이었다.
현재 QEMU clone DSO는 로드 후 unlink되므로 일부 perf symbol은 익명 주소로
남는다. 해당 오프셋은 Build ID가 같은 unstripped ELF의 `addr2line`으로 보완했다.

기준 `baseline-perf`는 perf 연결 전 SI0 TPS6594 초기화에서 진행이 멈추고
RSE `SCP is not ready`로 실패했다. 동일 입력을 사용한
`baseline-perf-retry`는 통과했다. 이 기존 부팅 재현성 문제는 보존했으며
이번 설정 변경이 해결했다고 주장하지 않는다. 제품 이미지, 활성 audio/DMA,
물리 시간 정확도 및 FVP parity는 이번 비교의 검증 범위가 아니다.
