# QBox unit test 반복 검증 및 불안정 항목 격리

## 1. 조치 요약

최근 실패를 바탕으로 timeout을 늘려 반복 검사하고, 수정 가능한 원인과
미해결 불안정 항목을 분리했다. 이후 성공한 실행으로 이전 실패를 지우지 않았다.

| 테스트 | 확인한 문제 | 조치 |
| --- | --- | --- |
| `qemu-pl061-test` | 비동기 reset 완료 전에 GPIO 출력을 검사 | 고정 1µs 대기를 실제 상태 변화 대기로 수정, 기본 실행 유지 |
| `aarch64-managed-uart-fifo-closed-writer` | `sc_stop()` 이후 프로세스 종료 지연, 120초에도 timeout | 원인 미확정, 불안정 항목으로 제외 |
| `aarch64-managed-timer-wfi-timer-wake` | `sc_stop()` 이후 간헐적 30초 timeout | 원인 미확정, 불안정 항목으로 제외 |

기본 정책은 기존 장시간 항목 26개와 신규 불안정 항목 2개를 별도로 관리한다.
등록된 core 88개 중 60개를 실행하며, AArch64 CPU 사례는 11개가 유지된다.
qbox-platform은 55개를 유지한다. 제외된 28개도 구성·컴파일 대상에는 남는다.

## 2. 재현 근거

원본 로그는 증거 디렉터리의 `historical/`에 복사했다.
네 로그는 같은 `do_check` 함수와 테스트 선택 설정을 사용했다.

| 기존 로그 | platform | core | 실패 |
| --- | --- | --- | --- |
| `log.do_check.248431` | 55/55 PASS | 61/62 PASS | UART closed-writer, 30.01초 timeout |
| `log.do_check.250556` | 55/55 PASS | 62/62 PASS | 없음; trace 출력 중복은 별도 실행으로 집계하지 않음 |
| `log.do_check.251855` | 55/55 PASS | 62/62 PASS | 없음 |
| `log.do_check.253674` | 55/55 PASS | 61/62 PASS | PL061 reset 후 pin 1 assertion, 0.11초 |

추가 반복 검사 결과는 다음과 같다. `until-fail`은 실패가 나오면 해당 항목의
반복을 중단한다. 실패 후 재시도하여 PASS로 바꾸는 `until-pass`는 사용하지 않았다.

| 대상 / 실행 방식 | 반복 결과 | 판단 |
| --- | --- | --- |
| platform 55개, 각각 `until-fail:5` | 275/275 실행 PASS | 해당 반복 범위에서 실패 없음 |
| core 중 기존 문제 2개를 뺀 60개, 각각 `until-fail:5` | 실제 298회 실행: 297 PASS, 1 timeout | timer-wake가 3번째 반복에서 실패 |
| PL061 수정 전, `until-fail:30`, 120초 상한 | 첫 실행에서 assertion 실패 | 기존 실패 재현 |
| PL061 수정 후 private native 바이너리 직접 반복, 매회 `timeout 120` | 50/50 PASS | 수정 효과 확인; CTest 반복과 구분 |
| timer-wake, `until-fail:30`, 120초 상한 | 30/30 PASS | 앞선 간헐 실패가 해결됐다는 뜻은 아님 |
| UART closed-writer, 첫 번째 `until-fail:100`, 120초 상한 | 100/100 PASS | 이 묶음에서는 실패 미재현 |
| UART closed-writer, 독립된 두 번째 `until-fail:100`, 120초 상한 | 32 PASS 후 33번째 실행에서 120.01초 timeout | 제한을 늘려도 hang 재현, 불안정 확정 |

두 번째 UART 묶음의 완료 전 전달된 100회 PASS 집계는 폐기했다.
위 표는 실제 완료 로그를 기준으로 정정한 결과다.
짧은 상한의 탐색용 부하 probe는 장시간 안정성 검증 결과에 합산하지 않았다.

## 3. PL061 수정 원인과 범위

기존 테스트는 instance reset을 요청한 후 1µs를 기다리고 reset을 해제했다.
그러나 이 요청은 QEMU main loop가 나중에 처리하는 비동기 요청이다.

호출 경로:

1. `QemuInstance::reset_cb()` → `LibQemu::system_reset()`
2. `qemu/libqemu/wrappers/cpu.c`의 `libqemu_system_reset()` → `qemu_system_reset_request()`
3. `qemu/system/runstate.c`에서 `reset_requested`를 설정하고 event 통지
4. main loop가 요청을 소비한 후 실제 `qemu_system_reset()` 실행

호스트 스케줄링에 따라 실제 reset이 완료되기 전에 SystemC의 1µs가 지날 수 있다.
따라서 일정 시간만 기다리는 방식으로는 reset 완료를 보장하지 못했다.

수정 파일:
[qemu-pl061-test.cc](../../hsoc-stack/tools/qbox/tests/qbox/gpio/qemu-pl061-test.cc)

- reset 전에 pin 1은 LOW이고 pull-up 설정은 활성 상태다.
- reset으로 pin 1이 HIGH가 되는 `value_changed_event()`를 기다린다.
- 그 후 wrapper reset을 해제하고 입력 재적용을 위해 delta cycle을 진행한다.
- 기존 GPIO 값과 입력 보존 assertion은 그대로 유지한다.

PL061 모델, QEMU reset 구현, 공통 종료 코드는 변경하지 않았다.
실제 reset이 완료되지 않으면 외부 CTest timeout으로 실패하므로 오류를 숨기지 않는다.

## 4. 미해결 종료 hang

UART의 120초 실패 로그에는 아래 상태가 기록되어 있다.

```text
mode=closed-writer entered=1 cpu_nonrunnable=1
pl011_rx=0 uart_irq=0 resumed=0 unexpected=0 watchdog=0
Simulation stopped by user.   # simulated time: 3 ms
Timeout 120.01 sec
```

closed-writer 분기의 assertion 이후 `sc_stop()`까지 도달했지만 프로세스가 종료되지 않았다.
timer-wake도 시뮬레이션 종료 메시지 후 timeout이 발생했다.

공통 QEMU/CPU 정리·종료 경로의 동기화 문제가 의심되지만,
정확한 대기 함수와 lock cycle은 확보하지 못했다. ptrace 제한으로 stack 수집에도
제약이 있었다. 특정 mutex나 backend 코드가 원인이라고 확정하지 않는다.

추측에 따른 공통 lifecycle 변경이나 `_Exit`로 소멸자를 우회하는 처리는 하지 않았다.
두 테스트는 **미수정·격리** 상태이며, timeout 증가 또는 이후 PASS만으로 해제하지 않는다.

## 5. 제외 정책

[Yocto recipe](../../hsoc-stack/yocto/meta-hsoc-bsp/recipes-devtools/qbox/qbox-apollo-qvp-native.bb)에서 관리한다.

| 변수 | 의미 |
| --- | --- |
| `QBOX_CORE_TEST_SLOW_REGEX` | 기존 5초 이상 측정 항목 26개 |
| `QBOX_CORE_TEST_UNSTABLE_REGEX` | 이번에 확인한 미해결 불안정 항목 2개 |
| `QBOX_CORE_TEST_EXCLUDE_REGEX` | 기본값은 두 패턴의 합집합; 전체 정책을 직접 override 가능 |

진단 목적으로 모든 core 제외를 해제하려면 별도 BitBake 설정에서 다음을 사용한다.
일상 빌드의 `local.conf`는 이번 작업에서 변경하지 않았다.

```bitbake
QBOX_CORE_TEST_EXCLUDE_REGEX:pn-qbox-apollo-qvp-native = ""
```

이 설정만으로 개별 테스트의 `TIMEOUT`이 해제되지는 않는다.
`QBOX_APOLLO_UNIT_TEST_TIMEOUT` 또는 CTest `--timeout`은 기본값이며,
테스트에 명시된 `TIMEOUT 30`보다 우선하지 않는다.

## 6. 120초 반복 검사의 재현 방법

Yocto provider를 빌드한 뒤 별도의 진단 디렉터리에 아래 `CTestTestfile.cmake`를 둔다.
현재 workspace의 경로를 사용하는 예시다. 원래 생성된 CTest 파일은 수정하지 않는다.

```cmake
subdirs("/build/arm/arm-auto-solutions/build/tmp_baremetal/work/x86_64-linux/qbox-apollo-qvp-native/1.0/build/tests/core")
set_tests_properties(
    qemu-pl061-test
    aarch64-managed-uart-fifo-closed-writer
    aarch64-managed-timer-wfi-timer-wake
    PROPERTIES TIMEOUT 120)
```

```bash
ctest --test-dir build/qbox-unit-tests/stability-20260909/diagnostic \
  --show-only=json-v1 \
  -R '^(qemu-pl061-test|aarch64-managed-uart-fifo-closed-writer|aarch64-managed-timer-wfi-timer-wake)$'

ctest --test-dir build/qbox-unit-tests/stability-20260909/diagnostic \
  -R '^aarch64-managed-uart-fifo-closed-writer$' \
  --repeat until-fail:100 --no-tests=error --output-on-failure
```

JSON의 `TIMEOUT`이 실제로 120인지 먼저 확인했다.
이 진단 실행은 recipe의 `-E` 필터를 사용하지 않으므로 격리된 테스트도 검사한다.
무제한 대기로 고아 프로세스를 남기지 않도록 유한한 상한을 유지한다.

## 7. 증거 파일

기준 디렉터리: `build/qbox-unit-tests/stability-20260909/`

- [기존 실패 4회](../../build/qbox-unit-tests/stability-20260909/historical/)
- [원래 native 바이너리 SHA-256](../../build/qbox-unit-tests/stability-20260909/baseline-binaries.sha256)
- [플랫폼 5회 반복](../../build/qbox-unit-tests/stability-20260909/platform-baseline.log)
- [core 5회 반복과 timer 실패](../../build/qbox-unit-tests/stability-20260909/core-baseline.log)
- [PL061 수정 전 재현](../../build/qbox-unit-tests/stability-20260909/pl061/baseline-repeat-30.log)
- [PL061 private 바이너리 수정 후 50회](../../build/qbox-unit-tests/stability-20260909/pl061/after-repeat-50.log)
- [timer 120초 상한 30회](../../build/qbox-unit-tests/stability-20260909/timer-baseline-120s.log)
- [UART 첫 번째 100회](../../build/qbox-unit-tests/stability-20260909/uart-baseline-120s.log)
- [UART 33번째 120초 실패](../../build/qbox-unit-tests/stability-20260909/uart/baseline-repeat-100.log)

과거 [1회 시간 측정](unit-test-timing-2026-09-09.md)은 당시의 성공 기록이다.
이번 반복 실패를 대체하거나 현재 안정성을 보증하는 자료로 사용하지 않는다.

## 8. 수정 후 정식 Yocto 산출물 검증

소스와 metadata를 고정한 후 다음 명령을 실행했다.

```bash
./yocto_build.sh --keep-conf qbox-apollo-qvp-native
```

configure, compile, `do_check`, install, sysroot 반영이 모두 성공했다.
단일 `do_check` 결과는 platform **55/55 PASS**, core **60/60 PASS**다.
제외 목록에는 기존 장시간 26개와 불안정 2개, 총 28개가 들어 있고 PL061은 없다.
기존 강제 실행에 따른 taint 경고 외 빌드 오류는 없었다.

이어 정식 native 바이너리를 대상으로 아래 반복 검사를 수행했다.
`final-diagnostic/CTestTestfile.cmake`에서 등록된 테스트의 실제 `TIMEOUT`을
120초로 덮어썼고, 실행 전 JSON 조회로 이를 확인했다.

| 최종 검사 | 반복 방식 | 실제 실행 결과 | 전체 반복 구간 시간 |
| --- | --- | --- | ---: |
| PL061 집중 검사 | `until-fail:100` | **100/100 PASS** | 2.85초 |
| platform 전체 | 55개 각각 `until-fail:5` | **275/275 PASS** | 26.81초 |
| 유지한 core 선택 항목 | 60개 각각 `until-fail:5` | **300/300 PASS** | 93.44초 |

이 표의 시간은 개별 테스트가 아니라 각 반복 묶음의 전체 시간이다.
JUnit의 테스트 수만으로 반복 횟수를 계산하지 않고, CTest 로그의 실제 실행 행을 집계했다.
각 반복 명령의 종료 코드는 모두 0이었다.

- [정식 provider 빌드 로그](../../build/qbox-unit-tests/stability-20260909/native-build.log)
- [정식 do_check 및 JUnit 결과](../../build/qbox-unit-tests/stability-20260909/native-final/)
- [실제 제외된 28개 목록](../../build/qbox-unit-tests/stability-20260909/native-final/qbox-core-unit-tests.excluded.list)
- [120초 override CTest 파일](../../build/qbox-unit-tests/stability-20260909/final-diagnostic/CTestTestfile.cmake)
- [PL061 최종 100회](../../build/qbox-unit-tests/stability-20260909/pl061-final-repeat.log)
- [platform 최종 275회](../../build/qbox-unit-tests/stability-20260909/platform-final-repeat.log)
- [core 최종 300회](../../build/qbox-unit-tests/stability-20260909/core-final-repeat.log)
- [최종 native 바이너리 SHA-256](../../build/qbox-unit-tests/stability-20260909/final-binaries.sha256)

`git diff --check`와 core 소유 경계 검사도 통과했다.
이번 작업은 unit test 안정성 검증이며 게스트 부팅·Linux driver·FVP 비교 검증은 수행하지 않았다.
격리한 두 종료 hang의 정확한 원인은 여전히 미확정이다.
