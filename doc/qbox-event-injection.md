# Apollo QVP runtime event injection

`/build/arm/qbox_event_injection.md`의 Implementation Plan v1.1을 현재
Apollo QVP에 적용한다. 기존 Monitor와 `apollo_runtime_injection`을 확장하며,
SystemC/QEMU state의 소유권은 기존 hardware model에 유지한다.

## 구현 경로

| 역할 | 현재 source |
| --- | --- |
| HTTP validation / API | `hsoc-stack/tools/qbox/systemc-components/monitor/` |
| Host → SystemC 전달 | Monitor의 기존 `gs::runonsysc::run_on_sysc()` |
| 예약, 상태, 취소, generation | `hsoc-stack/tools/qbox-platform/systemc-components/apollo_runtime_injection/` |
| IRQ proxy | `hsoc-stack/tools/qbox/systemc-components/signal-fault-injector/` |
| HIPC MHU doorbell fault | `hsoc-stack/tools/qbox-platform/systemc-components/mhu320ae/` |
| 구성과 reset 배선 | `hsoc-stack/tools/qbox-platform/platforms/apollo/apollo-qvp.lua`, `hw-block/config.lua` |
| CLI | `scripts/run/qbox_inject.py` |
| Linux fault/recovery 검증 | `scripts/test/verify_qbox_event_injection.py` |

문서의 신규 queue/manager 예제 대신 이미 검증된 `run_on_sysc` 경계를 재사용한다.
HTTP handler는 SystemC context에서 admission/즉시 action을 수행한 뒤 반환하며,
예약과 pulse 종료는 manager의 simulation-time scheduler가 처리한다.
HTTP 응답은 future fault의 완료를 기다리지 않는다. 기존 read-only Monitor와
`/api/v1/injection/capabilities` 경로를 유지한다.

## Fault와 복구 계약

| Target | Action | 관측 / 복구 |
| --- | --- | --- |
| `platform.host_ap_si_cl1_mhu_pbx` | `drop-next-doorbell`, channel 0 | Linux AP→SI1 HIPC doorbell 한 번을 전달하지 않음. PBX pending 유지, Linux ping timeout 후 system reset으로 복구 |
| `apollo.irq.i2c5` | `pass`, `drop-next-assert`, `force-high`, `force-low`, `pulse` | `ap_dw_i2c_5.irq`와 기존 AP GIC 입력 사이 proxy. force-low 상태에서 EEPROM read timeout, DELETE 후 read 복구 |
| `apollo.control.system-reset` | `pulse`, `duration_ns` | 기존 `apollo_system_reset_fanout.reset_in`으로 AP/SI/RSE reset 및 재부팅 |

MHU lost request에는 synthetic completion 또는 shared-memory FREE 값을
만들어 넣지 않는다. Linux의 MHUv3 sender는 pending bit가 남으면 다음
송신을 거부하므로 reset까지 필요한 fault다. I2C IRQ force는 입력/source와
출력을 분리하며 clear하면 현재 source level로 복구한다.

현재 Linux cpufreq는 SCMI fast channel을 사용한다. ftrace의 `scmi_fc_call`
관측으로 런타임 주파수 제어가 doorbell을 우회하는 것을 확인했다. 따라서
원문의 MHU/IPC 시나리오는 실제 MHU를 사용하는 HIPC 네트워크로 검증한다.
Linux `ethsi1.200`의 `192.168.1.2`와 SI1 `192.168.1.1` 사이 ICMP를 사용하며,
주소와 VLAN 200은 현재 Zephyr HIPC 설정을 따른다.

Generation은 현재 manager의 **전체 system reset epoch**다. `reset_domain`은
target에 맞는 요청인지 검사하는 metadata이며, domain별 독립 generation을
제공한다는 뜻이 아니다. 선택적 AP/SI/RSE reset fault는 후속 범위다.
기존 전체 reset 신호가 pending/active request를 취소한다. Reset을 발생시키는
pulse 자체는 별도 SystemC release 경로를 사용하여 자기 reset으로 해제 예약이
사라지지 않게 한다.

## 실행

BSP 빌드:

```bash
./yocto_build.sh --keep-conf --bsp
```

개발용 guest 시작(사용할 profile의 검증 결과는 아래 참조):

```bash
QBOX_APOLLO_MONITOR=true QBOX_APOLLO_RUNTIME_INJECTION=true \
./run_qbox_yocto.sh --bsp --headless --multi-session \
  --monitor --monitor-port 18080 --keep-running-after-pass \
  --copy-disks --no-persistent-rse-state --record-initial-state \
  --out-dir build/qbox-apollo-qvp/event-injection
```

```bash
python3 scripts/run/qbox_inject.py capabilities
python3 scripts/run/qbox_inject.py inject --file qa-tests/qbox-runtime-injection/i2c5-force-low.json
python3 scripts/run/qbox_inject.py status 1
python3 scripts/run/qbox_inject.py cancel 1
python3 scripts/test/verify_qbox_event_injection.py \
  --runtime-dir build/qbox-apollo-qvp/event-injection \
  --out-dir build/qbox-apollo-qvp/event-injection/verification
```

검증은 전용 guest에서 수행한다. I2C5 통신을 잠시 차단하고 HIPC 요청을
유실시키며 전체 guest를 재부팅한다. JSON에 HTTP 요청/응답, SSH 명령과
출력, 오류 및 복구 결과를 기록한다. 실제 request ID는 submit 응답을 사용한다.

지원 endpoint는 `GET /api/v1/injection-capabilities`,
`GET/POST /api/v1/injections`, `GET/DELETE /api/v1/injections/<id>`다.
Mutation은 기본 비활성이고 loopback에서만 허용한다.
예약 trigger는 `immediate`, `relative-simulation-time`의 `delay_ns`,
`absolute-simulation-time`의 `time_ns`이며 모두 정수 ns다.
`expected_generation`을 보내면 reset 이후의 오래된 요청을 거부한다.
지원하지 않는 persistent와 top-level duration 정책은 거부한다.
Pulse 폭은 해당 action의 `parameters.duration_ns`를 사용한다.

## 검증 범위와 후속 작업

실행 profile은 현재 Apollo 기본값인 `multithread-freerunning` +
`quantum_keeper`를 사용한다(AP MULTI, RSE/SI0 SINGLE, SI1 MULTI,
global quantum 10ms). 원문의 all-instance `multithread-quantum`, 100us,
SI1 SINGLE 조합은 injection 없는 기존 BSP에서도 600초 내 부팅하지 못했다.
`quantum-baseline/result.json`과 UART 로그에 보존했다. RSE BL2는
`SI CL0 is released out of reset` 이후 정지하고 AP/SI1 console은 비어 있다.
따라서 해당 조합은 이번 기능의 검증 profile로 채택하지 않는다. 정확한
cross-instance 동기화 원인은 별도 scheduler 검증이 필요하며, 이번 결과를
일반적인 모든 quantum 설정의 실패로 확장하지 않는다.

검증 artifact는 `build/qbox-apollo-qvp/event-injection-20260908/`에 보관한다.
source pin은 `source-pins.txt`, 실제 launch 입력은 각 run의
`initial-state.json`과 `result.json`을 기준으로 한다.

Deterministic replay, MCIPS, generic QEMU fault ABI, DMI memory corruption,
multi-domain atomic update는 원문에서 제외한 후속 항목이다. 이번 구현은
추가 QEMU/libqemu ABI나 TLM proxy 없이 기존 MHU hook과 IRQ signal 경로를
사용한다. 기능적 fault/recovery 증거이며 ASIL/WCET 또는 bit/cycle 정확도의
근거로 사용하지 않는다.

### 2026-09-08 검증 기록

| 검사 | 결과 | 증거 (위 artifact directory 기준) |
| --- | --- | --- |
| 최종 기본 설정 BSP + provider | PASS | `bsp-build-final-config.log` |
| Provider CTest | 51/51 PASS | `provider-tests-final.log` |
| 최종 injection 비활성 / 활성 boot | PASS | `baseline-final/result.json`, `runtime-final/result.json` |
| Monitor 활성 boot / absolute submit/status/cancel | PASS | `runtime-observer/result.json`, `absolute-accepted.json`, `absolute-cancelled.json` |
| I2C5 IRQ 차단, Linux timeout, DELETE 후 EEPROM read | PASS | `verification-final/result.json` |
| HIPC one-shot drop, ping timeout, reset 후 ping 2/2 | PASS | `verification-final/result.json` |
| 단독 system reset, 예약 취소, stale generation 거부 | PASS | `reset-verification/result.json` |
| Monitor 관측기와 PCA9539 reset/IRQ 동시 구성 | PASS | `pca9539-regression.log` |
| Python 기존 회귀 | 16 PASS | `python-tests.log` |
| Strict quantum 100us baseline | timeout | `quantum-baseline/result.json` |
| 전체 platform coverage | FAIL: AP map 증거 없음, G1 미실행 | `full-coverage-audit.json` |

HIPC 선택 검증 run은 `runtime-hipc/`이며, 당시 설치된 Lua의 SCMI target을
`--platform-param platform.apollo_runtime_injection.mhu_target=platform.host_ap_si_cl1_mhu_pbx`
로 지정했다. 이 선택을 최종 source Lua의 기본 target에도 반영했다.
최종 `runtime-final/`과 `verification-final/`은 해당 override 없이
배포된 기본 설정으로 같은 두 fault/recovery 시나리오를 다시 통과했다.
단독 reset 및 HIPC reset 시험은 새 AP boot ID, RSE/SI0 부팅 marker,
새 Zephyr boot marker, SCMI 2000000 kHz readback, EEPROM read 및 실제
HIPC ping을 확인한다. 재부팅 시 PFDI 서비스 메시지는 항상 재출력되지
않았으므로 해당 로그를 readiness 조건으로 사용하지 않는다. PFDI 서비스의
fault/recovery qualification을 수행했다는 의미도 아니다.

초기 실패 artifact는 보존했다. Monitor API test는 BitBake의 기본 network
격리에서 loopback 연결이 불가능해 `do_check[network]`를 설정했다. 기존
PL061 관측기의 무조건적인 추가 bind는 PCA9539 reset 배선과 충돌했으므로,
elaboration 시 미연결 output에만 fallback observer를 붙이고 기존 sink를
직접 읽도록 수정했다. Source pin은 기존 submodule 체계를 유지하며,
SystemC `febde7a3e007ce3030cf574a4cb6fcc13d0ed820`, CCI
`aff681775057a9a332983b240f27bb4e6aae3887`로 빌드했다.
