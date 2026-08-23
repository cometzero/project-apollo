# Apollo QBox CPU-idle 및 CPU-frequency deferred handoff

- 작성일: 2026-08-23
- 대상 machine: `apollo-qvp`
- 대상 image: `nexios-bsp-initramfs`
- 상태: Todo 18 `cpuidle`과 Todo 19 `cpufreq` 모두 `DEFERRED`

## 범위 및 현재 상태

이 문서는 Apollo QBox BSP의 `cpuidle`과 `cpufreq` validation profile을
재개할 때 필요한 구현 상태, 검증 결과, 현재 blocker를 통합한다. 두 profile은
standalone QBox에서 실제로 실행됐지만 아직 공개 PASS 조건을 만족하지 못했다.

| Profile | 공개 명령 | 최종 결과 | 현재 blocker |
|---|---|---|---|
| `cpuidle` | `./run_test.sh --machine apollo-qvp --bsp --test-profile cpuidle` | 0/8 PASS, 8 BLOCKED | CPU0 natural sleep 뒤 idle exit 미복귀와 RCU stall |
| `cpufreq` | `./run_test.sh --machine apollo-qvp --bsp --test-profile cpufreq` | 6/10 PASS, 4 FAIL | per-step capture 불일치와 누락된 negative record |

두 명령 모두 FVP reference 없이 실행하는 standalone 계약이다. 사용자가
`--fvp-reference`를 명시적으로 제공할 때만 기존 strict provenance 검사를
적용한다.

## 유지한 변경과 소유 repository

아래 파일은 현재 확인된 변경만 유지한다. 사용자 파일
`.vscode/settings.json`과 다른 Todo의 변경은 보존한다.

### Top-level repository

CPU-idle evaluator와 guest command transport:

- `scripts/run/qbox_cpuidle_guest.py`
- `scripts/run/qbox_cpuidle_commands.py`
- `scripts/run/qbox_cpuidle_probe.py`
- `scripts/run/qbox_validation/engine.py`
- `scripts/run/qbox_validation/reuse_cpuidle.py`
- `scripts/run/qbox_validation/types.py`
- `tests/test_qbox_validation_cpuidle.py`
- `tests/test_qbox_validation_registry.py`

CPU-frequency negative-write 증거 강화:

- `scripts/run/qbox_cpufreq_commands.py`
- `scripts/run/qbox_cpufreq_probe.py`
- `tests/test_qbox_validation_cpufreq.py`

`cpufreq` negative command는 invalid min/max write 실패와 상태 invariant를
분리한다. 실제 `before_min`, `before_max`, `after_min`, `after_max`를 비교하며
근거 없는 `unchanged=1`을 신뢰하지 않는다.

### `hsoc-stack/tools/qbox`

FIFO wake와 managed CPU timer/WFI component 검증:

- `systemc-components/backends/char_backend_file/include/char_backend_file.h`
- `tests/qbox/cpu/aarch64/CMakeLists.txt`
- `tests/qbox/cpu/aarch64/managed-uart-fifo-wfi-test.cc`
- `tests/qbox/cpu/aarch64/managed-timer-wfi-test.cc`

`char_backend_file`은 host thread에서 FIFO readiness를 감지하고 SystemC
`async_event`를 깨운다. 실제 read/enqueue는 기존 SystemC thread에서 한다.
EINTR와 cancellation-pipe teardown도 fail-safe로 처리한다.

### `hsoc-stack/tools/qbox-platform`

Apollo four-CPU timer 경로와 future-anchor timer 보정:

- `tests/platforms/CMakeLists.txt`
- `tests/platforms/apollo-fourcpu-timer-wake-test.cc`
- `systemc-components/host_gtimer/src/host_gtimer.cc`
- `tests/components/host_gtimer/host_gtimer-irq-tests.cc`

Four-CPU test는 Cortex-A720AE 네 개에서 local physical timer PPI30과 AP
REFCLK frame0 SPI49/INTID81 전달을 확인한다. `host_gtimer` 변경은 TLM
annotated delay로 counter anchor가 현재 SystemC timestamp보다 앞설 때 timer
thread가 조기 평가하지 않도록 한다. Socket 방향, address decode, IRQ wiring,
compare 계산은 바꾸지 않는다.

## Todo 18: QBox cpuidle

### 공개 실패 결과

#### Run `20260823-085342`

- Artifact: `build/tests/20260823-085342-qbox-bsp-cpuidle/`
- 결과: exit 2, standalone, 0 PASS / 8 BLOCKED
- Blocker: `command_timeout:71:primary`
- Console line 463: `disable 0 state0` command echo
- Console line 464: state0 disable stability 및 restore record 완료
- Console line 465: CPU RCU stall 시작

```text
summary.json      fd89cb765456be02daf45b71667c1592eeb38e56529b42e9ab98c082f69e772a
qbox/result.json  e9e64a35d419ccc0a07d71aa41768242fd786c0514920dbe8b7fd806e962230c
primary console   eeaa6759a3716fea09b81fbd1e858c8551d4ffdcb457160b05e2aba2777326f0
```

#### Run `20260823-110950`

- Artifact: `build/tests/20260823-110950-qbox-bsp-cpuidle/`
- 결과: exit 2, standalone, 0 PASS / 8 BLOCKED
- Blocker: `command_timeout:70:primary`
- Console line 463: `disable 0 state0` command echo
- Console line 464: CPU0 `rcu_preempt detected stalls`
- CPU2가 stall을 감지했으며 `CPUIDLE_DISABLE` completion record는 없음

```text
summary.json      286ab1efa8ac4cf5ac3431729cf040db9f602825ebab49e4c675e66df1683d07
qbox/result.json  be3233643b9e7d918a9a75c0bd581506bf60e65a02684565de3f2828253c2c9a
primary console   00f8d6378dac073f07ceccc9071d8a8efbfe00ee67254643444c1ac597b9bb58
```

### 확인된 component 경계

다음 경계는 독립 evidence로 확인했다.

- FIFO host readiness와 PL011/GIC wake
- Single-CPU MMIO timer SPI49 wake
- Four-A720AE local physical timer PPI30 wake
- Dynamic IROUTER81을 통한 SPI49/INTID81 전달
- Target CPU만 IRQ를 처리하고 peer CPU는 WFI 유지

Evidence:

```text
char functional
470e0b342b8b21c1adcf3a5bd94b9af5d78d6597d56587ca35d77b558ceae6f4
.omo/evidence/validation-profiles/task-18/char-backend-green-v2/functional-gate.md

char concurrency
f206118c978dcc6d65d20376063c8d1167db9e7d44995d04271fb345249e7e69
.omo/evidence/validation-profiles/task-18/char-backend-green-v2/concurrency-gate.md

managed timer/WFI
ea070a4da0f3a752aa3f894e4ef983c29f910bdf51d3efed2a1674d7902ad344
.omo/evidence/validation-profiles/task-18/qbox-core-wfi/observer-fix-gate.md

four-CPU timer/GIC
45ef9fa8b2dd9a3fa0e3c8bd8f164f46048e5d8df9e6f771c268bf15f90290f3
.omo/evidence/validation-profiles/task-18/four-cpu-timer-seam/AdversarialVerify.md
```

### 현재 blocker

가장 이른 blocker는 host FIFO delivery 이후 CPU0 natural sleep이 복귀하지
않는 경계다. 실제 Linux cpuidle state 선택, PSCI/local-timer-stop, broadcast
clockevent, CPU0 idle exit을 end-to-end로 확인하지 못했다.

CPU0 state0/state1 A/B discriminator의 첫 A boot도 Linux 전에 종료됐다.

- Artifact:
  `build/qbox-apollo-qvp/task18-cpu0-state-pair-state0-20260823-212651/`
- 결과: `child_failed:1`
- 첫 누락 marker: `rse:first_image_slot`
- `qbox-platform.log` line 38: RunOnSysc unknown job exception
- RSE: SCP protocol retry 뒤 `SCP is not ready. Abort`
- Primary console: 0 bytes

이 결과는 state0 또는 PPI30의 실패 증거가 아니다. B boot는 생성하지 않았다.

### 재개 절차

1. Todo 18 handoff와 `task-18/final-runtime/status.md`,
   `task-18/cpu0-state-pair/status.md`,
   `task-18/cpu0-state-pair/prereq-gate.md`를 먼저 읽는다.
2. Top-level, qbox, qbox-platform diff와 source/provider/image hash를 다시
   봉인한다. `.vscode/settings.json`은 보존한다.
3. Fresh CPU0-pinned A run을 만든다. State0만 enable하고 `sleep 0.5` 뒤
   PPI30, usage/time advance, exact restore를 요구한다.
4. A가 PASS한 뒤에만 fresh B run을 만든다. State1만 enable하고
   PSCI/local-timer-stop 및 `arch_mem_timer` SPI49/INTID81을 직접 증명한다.
5. Pre-Linux RunOnSysc/SCP prerequisite 실패는 idle 결과로 간주하지 않는다.
6. A/B가 owner를 확정한 뒤에만 failing-first test와 최소 fix를 추가한다.
   WAKER, direct UART fanout, idle pump, host followup, timeout 완화는 금지한다.
7. Provider를 exact source에서 rebuild/install하고 focused/component/static
   gate를 반복한다.
8. 공개 명령은 한 번 실행한다. 첫 8/8 PASS 후에만 동일 input hash로
   repeatability run을 수행한다.

## Todo 19: QBox cpufreq

### Run `20260823-133830`

- Artifact: `build/tests/20260823-133830-qbox-bsp-cpufreq/`
- 결과: exit 2, `RESULT: BLOCKED`, 0 PASS / 10 BLOCKED
- Blocker: `qbox_platform_failed:2`
- Primary console: 0 bytes
- SystemC time 18.097314124 s에서
  `platform.si_cl0_timer_cntbase.timer_thread`가
  `counter timestamp precedes the current anchor` 예외를 발생
- SI error marker: 없음

```text
summary.json       007970e77c8f723635e3e1e33ea6d0266d132beb1f8a3f4c7e29e86dcf1e8e5f
profile-result     e1fc7cb1b7adc38eab8d9e8a1d32e2edf132fd18bd699566c80aeaa903bacffb
qbox/result.json   cd065d860b8efd36caec6fba9fa9f4bdc7cb67bb354cb9fbe88a3f0986170a01
qbox-platform.log  1a57abb12148a58c0a37db3751ed2b37c0a7906089f791d160403e2ac661fd42
```

Future-anchor component test는 production fix 전에 같은 예외를
`host_gtimer_compare.timer_thread @ 80001 ps`에서 재현했다. 최소 timer-thread
defer fix 후 focused test가 PASS했다.

### Run `20260823-135035`

- Artifact: `build/tests/20260823-135035-qbox-bsp-cpufreq/`
- 결과: exit 2, stdout `RESULT: BLOCKED`
- Guest boot/login과 10개 command dispatch 완료
- Normalized 결과: 6 PASS / 4 FAIL / 0 BLOCKED / 0 SKIP
- Blocker: `validation_profile_failed:cpufreq`
- `si_error_hits`: 모두 false

FAIL assertion ID는 다음 네 개다.

1. `cpufreq-policy`
2. `cpufreq-scaling-min-frequencies`
3. `cpufreq-scaling-max-frequencies`
4. `cpufreq-min-max-negative`

Raw primary console에는 `policy0`, exact governor 집합, 1.8/2.0/2.5 GHz
OPP, `scmi` driver, affected CPU `0,1,2,3`, min/max
`1800000/2500000`가 기록됐다. Min/max 세 단계와 restore record도 보이지만
normalized evaluator는 FAIL이다. 마지막 negative step은
`CPUFREQ_NEGATIVE`와 해당 restore record를 남기지 않았다.

Console line 389의 `printf: write error: Invalid argument`는 invalid-governor
rejection의 예상 stderr다. 해당 assertion은 PASS다. Raw marker 일부가
존재해도 네 FAIL을 PASS로 승격하지 않는다.

```text
summary.json         bc94bc98cad5fd3bd624aa45898499d662f504268d04ef38b6f38157ffa6e432
profile-result       673d41e32e2ea3a2cd4ac221c1dea07b9901684da7f302a8d799961ca3ab577c
qbox/result.json     40f7755326890821740cf5bf1370570ed672cefa49462d253f4116332caaa102
primary console      3894e292c743df52ac47c2b246776b6d9574169de616ee46b1c561cb1253a327
```

### 재개 절차

1. Run `20260823-135035`의 per-step capture를 재현하는 behavioral test를
   먼저 추가한다.
2. Raw policy/min/max marker와 normalized FAIL의 불일치 원인을 확정한다.
3. 10번째 negative command가 record 없이 prompt로 끝나는 이유를 guest
   command framing, UART delivery, exit-trap 순서에서 조사한다.
4. Invalid min/max write failure, before/after exact equality, exact restore를
   동일 command output에서 증명한다. Fabricated output과 assertion 완화는
   금지한다.
5. Source/provider hash가 달라진 경우에만 exact provider를 rebuild/install한다.
6. Focused/component/static gate 뒤 공개 명령을 그대로 한 번 실행한다.
7. 10/10 PASS, exit 0, SI error 0, exact restore 이후에만 동일 input hash로
   repeatability run을 수행한다.
8. 별도 16-CPU runtime lane은 standalone 4-CPU 공개 PASS 이후 진행한다.

## Standalone 및 FVP reference 정책

두 profile의 필수 공개 경로는 standalone QBox다.

```sh
./run_test.sh --machine apollo-qvp --bsp --test-profile cpuidle
./run_test.sh --machine apollo-qvp --bsp --test-profile cpufreq
```

FVP reference는 필수가 아니다. Reference를 제공하지 않았다는 이유로
BLOCKED를 만들면 안 된다. 사용자가 `--fvp-reference`를 제공한 경우에는
revision, semantic profile, testdata provenance를 strict하게 검사한다.

## 이미 완료한 검증

### CPU-idle

- Focused Python: 128 PASS
- Character backend component: 4 PASS
- Managed timer/WFI와 four-A720AE timer/GIC independent gate: PASS
- Ruff, basedpyright, py_compile, no-excuse: PASS
- QBox full-map, core-boundary, top/nested diff check: PASS

### CPU-frequency

- 최종 focused Python: 97 PASS
- `host_gtimer-tests`, `host_gtimer-irq-tests`, `mhu320ae-tests`: 3/3 PASS
- `qbox-apollo-qvp-native` compile/install/populate_sysroot: exit 0
- Installed `host_gtimer.so` SHA-256:
  `5773e0e603d256cf31de1dd1b9157a432fea96580d441e46b52718b8de8b0f91`
- Installed Build ID: `743c65e6a132d3bb4b12f3e8739a1d70aabb1f29`
- Ruff, basedpyright, py_compile, no-excuse: PASS
- QBox full-map, core-boundary, top/nested diff check: PASS
- Four-CPU 및 16-CPU evaluator fixture: PASS
- MHU320AE four-domain OPP, limit, invalid request, isolation: PASS

## Cleanup 및 복구 가능성

Todo 18의 failed run copied media는 제거했으며 summary, result, JUnit,
console은 보존했다. 추가 snapshot에서는 다음 508,642,816 bytes를
`gio trash`로 이동했다.

- `input-images`: 307,250,688 bytes
- `writable-images`: 201,392,128 bytes
- `extra-blk2.raw`, `extra-blk3.raw`: 0 bytes

Todo 19의 두 run에서는 각 run의 `input-images`, `writable-images`, 0-byte
extra block만 `gio trash`로 이동했다. 총 workspace allocation은 약
586 MiB 감소했고 각 run은 약 1 MiB의 evidence만 유지한다.

Trash를 비우기 전에는 복구할 수 있다. Filesystem free-space 증가는 Trash를
비우기 전까지 주장하지 않는다. Task-owned QBox/QEMU process, managed tmux,
FIFO/socket, 관련 listener는 없다. 다른 run의 기존 `/dev/shm` 객체는
삭제하지 않았다.

## 명시적 non-claims

- `cpuidle`은 PASS가 아니다. 8개 assertion은 모두 BLOCKED다.
- `cpufreq`은 PASS가 아니다. 최종 결과는 6 PASS / 4 FAIL이다.
- Component PASS는 Linux guest end-to-end PASS가 아니다.
- CPU-idle A/B pre-Linux failure는 state0, state1 또는 PPI30 결과가 아니다.
- CPU0 idle exit, PSCI local-timer-stop, broadcast clockevent는 미확인이다.
- Guest-visible cpufreq 계약은 `identical`이지만 TCG execution-rate coupling은
  `unsupported`다.
- 16-CPU fixture PASS는 16-CPU full-system runtime qualification이 아니다.
- FVP reference 없이 실행한 standalone 결과를 FVP parity로 승격하지 않는다.
- Partial record, command echo, boot marker, timeout은 PASS 근거가 아니다.
- Cleanup은 recoverable Trash 이동이며 filesystem 용량 회수 완료 주장이 아니다.

두 Todo를 재개할 때는 fail-closed assertion과 exact restoration을 유지한다.
Timeout 연장, skip, fabricated guest output, direct UART/IRQ fanout으로 공개
결과를 우회하지 않는다.
