# RSE SysTick / TIMER0–3: FVP Iris 검증

검증일: 2026-09-14. 대상은 `apollo-fvp` BSP 이미지와 `FVP_Zena_CSS_Cfg2`이다.
이 문서는 timer register 동작 검증이며, 전체 boot/reset qualification은 아니다.

## 결론

SysTick과 TIMER0–3의 counter state는 분리해야 한다. 다만 TIMER0–3을 각각
독립된 free-running system counter로 구현해야 한다는 뜻은 아니다.

- Secure/Non-secure SysTick: 각각 독립된 24-bit down-counter 및 reload/control state.
- TIMER0–3: 공통 LSC의 `CNTVALUEB`를 받아 각각 compare/control/IRQ state를 유지.
- 같은 clock을 사용할 수 있다는 사실과 counter state를 공유한다는 것은 별개이다.
- 현재 QVP는 counter 구조와 별개로 **SysTick clock 선택에 FVP와 차이**가 있다.

## CLKSOURCE의 정확한 의미

[Arm Cortex-M55 Devices Generic User Guide, 101273_0101_03_en](https://documentation-service.arm.com/static/6622c155fabc8c11c7b534b4),
§5.4 및 Table 5-59, 5-62를 직접 확인했다. PDF p575–579.

| 레지스터/필드 | 의미 |
| --- | --- |
| `SYST_CSR[2].CLKSOURCE = 0` | External reference clock 선택 |
| `SYST_CSR[2].CLKSOURCE = 1` | Processor clock 선택 |
| `SYST_CALIB[31].NOREF = 1` | Reference clock 없음. CLKSOURCE는 read-as-one, 해당 bit write 무시 |
| `SYST_CALIB.TENMS = 0` | Calibration 값으로 주파수를 산출할 수 없음 |

External은 processor 관점의 reference input이라는 뜻이며, 외부 crystal,
processor clock의 특정 분주비, LSC counter 값 자체를 의미하지 않는다.
`CLKSOURCE`는 tick source를 바꾸고 `LOAD/VAL`은 SysTick 자체 counter state이다.

[Zena programmer's model](../arm_zena_css_dev_guide/09-programmers-model-for-zena-css.md)
§9.4.9는 LSC가 TIMER0–3의 CNTVALUEB를 공급한다고 명시한다.
이번에 확인한 Zena guide에서는 SysTick reference input의 구체적 배선/주파수를
확정하지 못했다. 아래 측정값은 **실행한 FVP 구성의 동작**이지 RTL clock-tree 보증이 아니다.

## 실험과 실제 관측

Iris target: `component.RD_ASD.css.smb.rseil.rse.cpu`, memory space `SP`.
모든 snapshot은 전체 simulation을 정지한 상태에서 읽었다.
RSE 실행 PC는 `0x10001f10`이었다. 이후 `set_execution_state(False)`로 RSE의
firmware 실행만 막고 simulation을 재개하여 register 변경 간섭을 제한했다.
이는 architectural debug halt나 hardware clock gating 검사가 아니다.
Arm 문서는 debug halt 시 SysTick이 감소하지 않는다고 설명하므로 혼동하면 안 된다.

| 검사 | 실제 관측 | 판정 |
| --- | --- | --- |
| TIMER0–3 공통 counter 관측 | 최초 네 CNTPCT 모두 `428411477`; 다음 모두 `468187340` | PASS: 공통 입력 구조와 일치 |
| TIMER별 compare state | TIMER3 CVAL만 `0x1212345678`로 변경; 다른 CVAL 및 모든 CNTPCT 불변 | PASS |
| SysTick S/NS 독립 state | LOAD 각각 `0xffffff`, `0x7fffff`, VAL 각각 0 설정; TIMER state 불변 | PASS |
| CLKSOURCE=0 | S/NS CTRL readback `1`, 두 VAL 모두 감소 | PASS |
| CLKSOURCE=1 | S/NS CTRL 하위 3bit readback `5`, 두 VAL 모두 감소 | PASS |
| LSC 직접 control/read access | `0x5015a000`, `0x5015b008`에서 Iris memory read 실패 | UNSUPPORTED: 직접 정지/재시작 미검증 |
| Reset별 counter 보존/초기화 | reset 미실행 | NOT TESTED |
| SysTick/TIMER ISR 진입 | TICKINT를 켜지 않음, handler 미추적 | NOT TESTED |

네 CNTPCT가 같다는 것만으로 binary 내부 구현이 단일 객체임을 증명하지는 않는다.
Hardware 계약과 합쳐 공통 counter 입력 구조를 뒷받침하는 관측이다.

### Clock 측정

시간은 host sleep 길이가 아니라 Iris `simulationTime_get`의 ticks/tickHz로 계산했다.
reload 직후 첫 sample은 버리고 연속 sample의 차이를 사용했다.

| 대상 | 측정 구간 및 변화 | 관측 rate |
| --- | --- | --- |
| SysTick external, S/NS | 0.1526014272 s 동안 각각 3816 감소 | 약 25.006 kHz, 즉 약 25 kHz |
| SysTick processor, S | 0.0729232512 s 동안 9115406 감소 | 약 125 MHz |
| SysTick processor, S/NS 짧은 재검사 | 0.0004666312 s 동안 각각 58329 감소 | 둘 다 약 125 MHz |
| TIMER CNTPCT | 같은 짧은 구간에서 각각 58329 증가 | 약 125 MHz |

external 구간의 1 tick 양자화는 약 6.55 Hz다. 정확한 물리 주파수나
25 kHz 생성 경로는 이 측정으로 확정하지 않는다. 모델 parameter listing의
`ros.ref_clk_frequency=125000000`도 SysTick external input 배선 증거는 아니다.

긴 processor 측정에서 NS는 reload period가 더 짧아 wrap했다. JSON의
`systick_modulo_hz` 약 9.97 MHz는 wrap을 복원하지 않은 값이며 **실제 NS clock으로
해석하면 안 된다**. S/NS 비교에는 위의 짧은 구간을 사용했다.
FVP의 `SYST_CALIB`은 S/NS 모두 0이므로 `NOREF=0`, `TENMS=0`이다.
TIMER의 CNTFRQ readback도 0이어서 이 값을 실제 counter rate로 해석하지 않았다.

## 현재 QVP와 차이

정적 소스 근거:

- [rse.lua](../../hsoc-stack/tools/qbox-platform/platforms/apollo/hw-block/rse.lua):
  `systick_cpuclk_hz = 100000000`.
- [armv7m-nvic.h](../../hsoc-stack/tools/qbox/qemu-components/irq-ctrl/armv7m_nvic/include/armv7m-nvic.h):
  S/NS `armv7m_systick`에 `cpuclk`만 연결하며 `refclk` 연결 없음.
- [armv7m_systick.c](../../hsoc-stack/tools/qemu/hw/timer/armv7m_systick.c):
  refclk가 없으면 CALIB.NOREF=1, reset/write 시 CLKSOURCE=1로 강제.

따라서 현재 QVP source 기준으로 external selection은 지원되지 않으며,
processor source도 이번 FVP의 관측 125 MHz와 QVP 설정 100 MHz가 다르다.
이는 QVP runtime을 이번에 실행해 얻은 결과가 아니라 checked-out source의 계약이다.
FVP parity를 원하면 reference clock 연결, source 선택/readback, calibration,
S/NS rate 및 reset 동작을 별도로 구현·검증해야 한다. 이번 요청에서는 모델을 수정하지 않았다.

## 재현 및 증거

[Probe script](../../scripts/test/probe_rse_counter_independence_iris.py)는 **폐기할 전용
인스턴스에서만** 실행한다. register와 CPU execution state는 복원하지 않으며,
외부 `timeout`으로 client도 제한한다. 실행 종료 시 모델을 반드시 폐기한다.

```sh
./run_fvp.sh --machine apollo-fvp --bsp --headless --timeout 900 \
  --out-dir build/agent-debug/fvp-rse-counter-20260914-b \
  -- --iris-server --iris-port 17214 --print-port-number
```

별도 client에서 `Model.NewNetworkModel(..., synchronous=False)`로 연결하고
`model.run(blocking=False, timeout=30)`으로 부팅을 진행한다. RSE runtime 도달 후
`model.stop(timeout=30)`하고 연결만 해제한다. 이번 run은 20초 host 대기 후 정지했으며,
환경마다 시간 대신 UART의 RSE runtime handoff를 확인하는 것이 적절하다.

```sh
timeout 480 python3 -u scripts/test/probe_rse_counter_independence_iris.py \
  --iris-python build/tmp_baremetal/sysroots-components/x86_64/fvp-rd-aspen-native/usr/lib/fvp/fvp-rd-aspen/Iris/Python \
  --port 17214 --disposable --sample-wall-seconds 1 \
  --output build/agent-debug/fvp-rse-counter-20260914-b/counter-probe-long.json
```

짧은 구간은 `--sample-wall-seconds 0.05`로 측정한다. host 대기시간은 simulation
구간 길이를 보장하지 않으므로 JSON의 실제 시간과 wrap 여부를 확인해야 한다.
종료는 해당 owned endpoint에 연결하여 `model.release(shutdown=True)`로 수행했다.
실제 FVP PID 24134 및 port 17214 listener의 종료를 확인했다.

`--debug` launcher 경로는 현재 apollo-qvp만 허용하여 apollo-fvp 요청이 거부됐다.
따라서 apollo-fvp BSP launcher에 Iris 옵션을 직접 전달했으며 machine/image를 바꾸지 않았다.
배포물 입력은 `build/tmp_baremetal/deploy/images/apollo-fvp/`이고 writeback은
runner가 만든 `writable-images/` 복사본에 한정했다.

증거 디렉터리:
[build/agent-debug/fvp-rse-counter-20260914-b](../../build/agent-debug/fvp-rse-counter-20260914-b/).

- `counter-probe.json`: 최초 state 독립성 검사, 5개 check 모두 true, client exit 0.
- `counter-probe-repeat.json`: 짧은 steady-state rate 추가, 5개 check 모두 true, exit 0.
- `counter-probe-long.json`: 긴 external rate 검사, 5개 check 모두 true, exit 0.
- `provenance.sha256`: 최종 probe script, FVP binary, fvpconf 및 두 rate JSON의 hash.
  앞의 두 probe는 최종 script에 steady sample/대기 옵션/CVAL toggle을 추가하는 과정에서 수집했다.
- `initial-state.json`: 사용한 firmware/image 경로와 SHA-256.
- `model-parameters.txt`, `fvp_stdout.log`, UART logs, `result.json`, `summary.txt`.

**전체 boot runner는 exit 1 / passed=false이다.** RSE, CL0, CL1, TF-A marker는
통과했고 Linux 시작도 관측했지만 전체 U-Boot/Linux 완료 조건은 미충족이다.
검사 후 전용 인스턴스를 의도적으로 종료했으므로 timer register PASS를 전체 boot PASS로
승격하지 않는다. 초기 탐색 인스턴스의 별도 로그도
`build/agent-debug/fvp-rse-counter-20260914/`에 보존했다.

검증 범위: Python syntax compile PASS, 실제 Iris probe 3회 exit 0.
QVP 수정/build/실행, hardware reset 검증, RTL 또는 cycle-accurate parity는 미수행.
