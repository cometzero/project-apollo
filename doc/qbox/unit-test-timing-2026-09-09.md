# QBox / qbox-platform unit test 실행 시간 측정

이 문서는 당시 1회 측정 기록이다. 이후 반복 검사에서 발견한 간헐 실패와
수정·제외 정책은 [안정성 검증 기록](unit-test-stability-2026-09-09.md)을 참조한다.

## 1. 결과 요약

2026년 9월 9일, 현재 Yocto 설정으로 unit test를 새로 실행했다.
**qbox core 62개와 qbox-platform 55개가 모두 PASS**했다.
기존 정책에 따라 5초 이상으로 분류된 core 테스트 26개는 실행하지 않았다.

| 대상 | 실행 / PASS | 실패 | 정책상 제외 | CTest 실행 구간 시간(초) | 개별 테스트 시간 합계(초) |
| --- | ---: | ---: | ---: | ---: | ---: |
| qbox core | 62 / 62 | 0 | 26 | 19.61 | 19.546866 |
| qbox-platform | 55 / 55 | 0 | 0 | 5.26 | 5.233622 |
| 합계 | 117 / 117 | 0 | 26 | **24.87** | **24.780488** |

- BitBake 명령 전체 경과 시간: **42.13초**, 종료 코드 **0**.
- qbox core 최장 개별 테스트: `smmuv3-tests`, **3.601880초**.
- qbox-platform 최장 개별 테스트: `strata_flash_j3-tests`, **1.098530초**.
- 이번에 실행한 모든 개별 테스트는 **5초 미만**이었다.
- 실제 실행 순서는 qbox-platform → qbox core이며, CTest는 순차 실행했다.
- 반복 측정 평균이 아니라 **이번 1회 실행 결과**다.

## 2. 시간 측정 기준

서로 다른 시간 지표를 구분했다.

1. **개별 테스트 시간**: 이번 JUnit XML의 각 `testcase@time` 값이다.
   GTest 내부 assertion이나 하위 테스트 단위가 아니라 CTest 등록 사례 단위다.
2. **CTest 실행 구간 시간**: 각 로그의 `Total Test time (real)` 값이다.
   테스트 프로세스 실행과 CTest 관리 비용을 포함하며, 컴파일 시간은 제외한다.
3. **CTest 구간 합계**: 두 CTest 실행 구간을 더한 24.87초다.
   두 구간 사이의 빌드 타깃 확인 등은 포함하지 않는다.
4. **명령 전체 경과 시간**: `/usr/bin/time`으로 측정한 42.13초다.
   BitBake 초기화·캐시 확인·타깃 빌드 확인·테스트 실행을 포함한다.
   따라서 순수 테스트 시간과 동일하지 않다.

JUnit의 개별 시간은 원래 정밀도로 합산한 뒤 소수점 6자리로 표시했다.
CTest 구간 시간은 로그가 제공하는 소수점 2자리를 사용했다.
반올림과 실행 관리 비용 때문에 개별 시간 합계와 CTest 구간 시간은 다르다.
SystemC의 시뮬레이션 시간이 아니라 **호스트에서 측정한 실제 경과 시간**이다.

## 3. 실행 환경과 범위

| 항목 | 설정 |
| --- | --- |
| 실행 날짜 | 2026-09-09 |
| 플랫폼 테스트 시작 | 2026-09-09T11:46:36 UTC / 20:46:36 KST |
| core 테스트 시작 | 2026-09-09T11:46:41 UTC / 20:46:41 KST |
| 호스트 CPU | AMD Ryzen 7 PRO 4750G, 8 core / 16 logical CPU |
| 호스트 OS | Linux 6.8.0-139-generic, x86_64 |
| Yocto machine / variant | `apollo-qvp` / `cfg2` |
| recipe | `qbox-apollo-qvp-native` |
| core suite | `components sync utils qbox` |
| CPU 테스트 아키텍처 | `aarch64`만 구성 |
| CPU 반복 조합 | `multithread-freerunning`, CPU 1/2/4개, TCG MULTI |
| 시간 동기화 | `quantum_keeper`, `QBOX_ENABLE_MCIPS_TESTS=OFF` |
| core 등록 / 실행 / 제외 | 88 / 62 / 26 |
| AArch64 CPU 등록 / 실행 / 제외 | 38 / 13 / 25 |
| 플랫폼 등록 / 실행 | 55 / 55 |

개별적으로 등록된 shutdown, managed timer, UART 등의 회귀 테스트는
각 테스트에 지정된 CPU 수와 동기화 설정을 그대로 사용한다.
반복 조합 설정을 모든 테스트에 일괄 적용한 것은 아니다.

플랫폼 55개에는 모델 테스트 46개, UART 테스트 5개, four-CPU timer 테스트 3개,
CMake 선택 설정 검사 1개가 포함된다.
UART 테스트 중 4개는 core와 동일한 소스를 `apollo-*` 이름으로 별도 실행한다.
따라서 117이라는 수치는 중복 없는 기능 개수가 아니라 실제 실행한 CTest 사례 수다.

기존 호스트·기능 조건도 유지했다.
Python binder는 비활성이며, macOS 전용 DMI-reset 및 display 테스트는 실행하지 않았다.
동기화 `checker` 실행 파일은 CTest로 등록되어 있지 않다.
이번 결과는 게스트 Linux 부팅이나 FVP 비교 결과가 아니다.

### 소스 상태

측정 당시 다음 HEAD에 미커밋 테스트 관련 변경 사항이 적용되어 있었다.
HEAD만으로 이번 측정 상태를 재현할 수 있는 것은 아니다.

| 저장소 | HEAD | 상태 |
| --- | --- | --- |
| qbox | `4827bcaafc92f6b27600d963604d14526b413e44` | 미커밋 변경 포함 |
| qbox-platform | `b5509f4e9b929ed8a83ab611729eb2b576e8691f` | 미커밋 변경 포함 |
| meta-hsoc-bsp | `f486bf33d9f1fb0dd147de995ab73b4adb8ec8d1` | 미커밋 recipe 변경 포함 |

측정 디렉터리에 저장소별 diff와
[테스트 설정 입력 SHA-256](../../build/qbox-unit-tests/timing-20260909-114606/source-inputs.sha256)을 함께 보관했다.
이번 요청에서는 모델·CMake·recipe 설정을 변경하지 않고 테스트와 문서 작성만 수행했다.

## 4. qbox core 개별 실행 시간

아래 표의 `(CPU=N)`은 다음 CTest 이름 접미사를 축약한 것이다.
원래 전체 이름은 연결된 JUnit XML과 실행 목록에서 확인할 수 있다.

```text
:sync-pol=multithread-freerunning:num-cpu=N:icount=false:threading=MULTI:accel=tcg:time_sync_strategy=quantum_keeper
```

| 번호 | 테스트 이름 | 시간(초) | 결과 |
| ---: | --- | ---: | --- |
| 1 | `test_exclusive_monitor` | 0.008740 | PASS |
| 2 | `memory-tests` | 0.506319 | PASS |
| 3 | `router-tests` | 0.006555 | PASS |
| 4 | `router-tests-extended` | 0.007687 | PASS |
| 5 | `router-addressmap-tests` | 0.003089 | PASS |
| 6 | `router-advanced-overlap-tests` | 0.007293 | PASS |
| 7 | `router-shadowing-warning-test` | 0.006918 | PASS |
| 8 | `router-tests-new` | 0.006225 | PASS |
| 9 | `router-thread-safety-test` | 0.509266 | PASS |
| 10 | `router-coverage-tests` | 0.006032 | PASS |
| 11 | `router-memory-tests` | 0.506503 | PASS |
| 12 | `addrtr-tests` | 0.005623 | PASS |
| 13 | `request-context-tests` | 0.003567 | PASS |
| 14 | `aliases-mapping-test` | 0.507431 | PASS |
| 15 | `loader-test` | 0.508375 | PASS |
| 16 | `memory-blocs` | 0.509155 | PASS |
| 17 | `dmi-converter-tests` | 0.006827 | PASS |
| 18 | `remote-tests` | 0.020430 | PASS |
| 19 | `gs_register-tests` | 0.507903 | PASS |
| 20 | `generic_lua_model-tests` | 0.510791 | PASS |
| 21 | `container_builder-tests` | 0.513324 | PASS |
| 22 | `dw-apb-i2c-tests` | 0.008405 | PASS |
| 23 | `pca9539-tests` | 0.008695 | PASS |
| 24 | `tps6594-tests` | 0.007571 | PASS |
| 25 | `dw-apb-ssi-tests` | 0.008695 | PASS |
| 26 | `monitor-runtime-config-tests` | 0.006419 | PASS |
| 27 | `monitor-runtime-api-disabled` | 0.008430 | PASS |
| 28 | `monitor-runtime-api-missing` | 0.007991 | PASS |
| 29 | `monitor-runtime-api-full` | 0.009158 | PASS |
| 30 | `fss-tests` | 0.007069 | PASS |
| 31 | `file-backend-test` | 0.005826 | PASS |
| 32 | `uart-biflow-stdio-test` | 0.507104 | PASS |
| 33 | `uart-biflow-backend-socket-test` | 0.309120 | PASS |
| 34 | `uart-ibex-biflow-stdio-test` | 0.508774 | PASS |
| 35 | `dw-apb-uart-test` | 0.007589 | PASS |
| 36 | `smmuv3-tests` | 3.601880 | PASS |
| 37 | `signal_fault_injector-tests` | 0.005828 | PASS |
| 38 | `qk_extendedif_test` | 0.004905 | PASS |
| 39 | `qkmultithread_test` | 0.506886 | PASS |
| 40 | `qkmulti-quantum_test` | 0.507710 | PASS |
| 41 | `scp_report_thread` | 0.007818 | PASS |
| 42 | `factory_platform` | 0.509977 | PASS |
| 43 | `cci_test` | 0.008271 | PASS |
| 44 | `cci_alias_test` | 0.006748 | PASS |
| 45 | `scp_logging_test` | 0.006055 | PASS |
| 46 | `lua_test` | 0.006545 | PASS |
| 47 | `logger_test_gslog` | 0.005445 | PASS |
| 48 | `logger_test` | 0.004969 | PASS |
| 49 | `aarch64-single-tcg-five-cpu-shutdown-test` | 0.512920 | PASS |
| 50 | `halt-tests (CPU=1)` | 0.525825 | PASS |
| 51 | `halt-tests (CPU=2)` | 0.524979 | PASS |
| 52 | `halt-tests (CPU=4)` | 0.525728 | PASS |
| 53 | `aarch64-managed-timer-wfi-baseline` | 2.515690 | PASS |
| 54 | `aarch64-managed-timer-wfi-timer-wake` | 0.515032 | PASS |
| 55 | `aarch64-managed-uart-fifo-active` | 0.515251 | PASS |
| 56 | `aarch64-managed-uart-fifo-quiescent` | 0.515366 | PASS |
| 57 | `aarch64-managed-uart-fifo-closed-writer` | 0.515256 | PASS |
| 58 | `aarch64-managed-uart-fifo-cancel-eintr` | 0.009658 | PASS |
| 59 | `aarch64-smmu-router-stress-test-v2 (CPU=1)` | 0.526118 | PASS |
| 60 | `aarch64-smmu-router-stress-test-v2 (CPU=2)` | 0.526236 | PASS |
| 61 | `aarch64-smmu-router-stress-test-v2 (CPU=4)` | 0.527135 | PASS |
| 62 | `qemu-pl061-test` | 0.029736 | PASS |

core 개별 시간 합계는 **19.546866초**, CTest 구간 시간은 **19.61초**다.

## 5. qbox-platform 개별 실행 시간

| 번호 | 테스트 이름 | 시간(초) | 결과 |
| ---: | --- | ---: | --- |
| 1 | `qbox-core-selection-smoke` | 0.104388 | PASS |
| 2 | `arm_system_counter-tests` | 0.003785 | PASS |
| 3 | `apollo_runtime_injection-tests` | 0.078118 | PASS |
| 4 | `apollo_cpu_ras-tests` | 0.003685 | PASS |
| 5 | `cc3xx-tests` | 0.007305 | PASS |
| 6 | `cc3xx_core-tests` | 0.003511 | PASS |
| 7 | `qemu_cc3xx-tests` | 0.004032 | PASS |
| 8 | `rse_lms_accel-tests` | 0.003500 | PASS |
| 9 | `rse_mcuboot_image-tests` | 0.002252 | PASS |
| 10 | `rse_p256_ecdsa-tests` | 0.036242 | PASS |
| 11 | `dma350-tests` | 0.004307 | PASS |
| 12 | `gic720ae_messreg-tests` | 0.003671 | PASS |
| 13 | `apollo_sbist-tests` | 0.004189 | PASS |
| 14 | `gicx00_multiview-tests` | 0.801602 | PASS |
| 15 | `host_cmn_cyprus-tests` | 0.005763 | PASS |
| 16 | `host_gtimer-tests` | 0.006346 | PASS |
| 17 | `host_gtimer-irq-tests` | 0.004927 | PASS |
| 18 | `host_ni710ae_nci-tests` | 0.003864 | PASS |
| 19 | `host_ppu-tests` | 0.003856 | PASS |
| 20 | `host_ppu-signal-tests` | 0.003554 | PASS |
| 21 | `host_scr-tests` | 0.004067 | PASS |
| 22 | `host_smcf_mgi-tests` | 0.003719 | PASS |
| 23 | `host_system_pll-tests` | 0.003284 | PASS |
| 24 | `hsoc_gpio-tests` | 0.007879 | PASS |
| 25 | `mhu320ae-tests` | 0.074195 | PASS |
| 26 | `mmu720ae-register-tests` | 0.004659 | PASS |
| 27 | `mmu720ae-queue-tests` | 0.003861 | PASS |
| 28 | `mmu720ae-tbu-tests` | 0.004054 | PASS |
| 29 | `ras_ffh_stub-tests` | 0.003263 | PASS |
| 30 | `reset_fanout-tests` | 0.003835 | PASS |
| 31 | `signal_or-tests` | 0.003963 | PASS |
| 32 | `rse_atu-tests` | 0.004563 | PASS |
| 33 | `rse_integrity_checker-tests` | 0.003294 | PASS |
| 34 | `rse_kmu-tests` | 0.003849 | PASS |
| 35 | `rse_lcm-tests` | 0.003900 | PASS |
| 36 | `rse_ppc_filter-tests` | 0.004972 | PASS |
| 37 | `rse_protection_ctrl-tests` | 0.003960 | PASS |
| 38 | `rse_sam-tests` | 0.003867 | PASS |
| 39 | `rse_sysctrl-tests` | 0.003830 | PASS |
| 40 | `rse_sysctrl-reset-tests` | 0.003707 | PASS |
| 41 | `strata_flash_j3-tests` | 1.098530 | PASS |
| 42 | `zena_fmu-tests` | 0.005369 | PASS |
| 43 | `zena_leaf_fmu-tests` | 0.003555 | PASS |
| 44 | `zena_ssu-tests` | 0.003606 | PASS |
| 45 | `zena_watchdog-tests` | 0.003487 | PASS |
| 46 | `zena_reset_ctrl-tests` | 0.003500 | PASS |
| 47 | `zena_safety_vertical-tests` | 0.004255 | PASS |
| 48 | `apollo-file-backend-test` | 0.004986 | PASS |
| 49 | `apollo-pl011-aperture-tests` | 0.004700 | PASS |
| 50 | `apollo-uart-biflow-stdio-test` | 0.505757 | PASS |
| 51 | `apollo-uart-biflow-backend-socket-test` | 0.307003 | PASS |
| 52 | `apollo-uart-ibex-biflow-stdio-test` | 0.507113 | PASS |
| 53 | `apollo-fourcpu-local-ppi-wake` | 0.514753 | PASS |
| 54 | `apollo-fourcpu-mmio-broadcast-wake` | 0.515407 | PASS |
| 55 | `apollo-fourcpu-invalid-target` | 0.509981 | PASS |

플랫폼 개별 시간 합계는 **5.233622초**, CTest 구간 시간은 **5.26초**다.
`apollo-fourcpu-invalid-target`은 예상 오류를 확인하는 `WILL_FAIL` 테스트다.
해당 항목의 PASS는 잘못된 입력이 예상대로 거부되었다는 뜻이다.

## 6. 이번 실행에서 제외한 테스트

아래 26개는 이전 5초 제한 측정에 근거한 recipe 제외 정책과 일치한다.
**이번 실행에서는 다시 실행하지 않았으므로 현재 소요 시간은 미측정**이다.
이 항목들의 시간을 0초로 간주하거나 PASS로 집계하지 않았다.
CPU 시뮬레이션 종료 후 프로세스 종료가 지연된 사례도 포함되며, 해당 문제는 미해결이다.

| 번호 | 제외한 CTest 이름 | 이번 실행 시간 |
| ---: | --- | --- |
| 1 | `router-cache-bench-enhanced` | 미측정 — 제외 |
| 2 | `aarch64-simple-write-test (CPU=1)` | 미측정 — 제외 |
| 3 | `aarch64-simple-write-test (CPU=2)` | 미측정 — 제외 |
| 4 | `aarch64-simple-write-test (CPU=4)` | 미측정 — 제외 |
| 5 | `aarch64-dmi-test (CPU=1)` | 미측정 — 제외 |
| 6 | `aarch64-dmi-test (CPU=2)` | 미측정 — 제외 |
| 7 | `aarch64-dmi-test (CPU=4)` | 미측정 — 제외 |
| 8 | `aarch64-dmi-test-concurrent-inval (CPU=1)` | 미측정 — 제외 |
| 9 | `aarch64-dmi-test-concurrent-inval (CPU=2)` | 미측정 — 제외 |
| 10 | `aarch64-dmi-test-concurrent-inval (CPU=4)` | 미측정 — 제외 |
| 11 | `aarch64-ld-st-excl-fail-test (CPU=1)` | 미측정 — 제외 |
| 12 | `aarch64-ld-st-excl-fail-test (CPU=2)` | 미측정 — 제외 |
| 13 | `aarch64-ld-st-excl-fail-test (CPU=4)` | 미측정 — 제외 |
| 14 | `aarch64-write_read (CPU=1)` | 미측정 — 제외 |
| 15 | `aarch64-write_read (CPU=2)` | 미측정 — 제외 |
| 16 | `aarch64-write_read (CPU=4)` | 미측정 — 제외 |
| 17 | `aarch64-dmi-test-async-inval (CPU=1)` | 미측정 — 제외 |
| 18 | `aarch64-dmi-test-async-inval (CPU=2)` | 미측정 — 제외 |
| 19 | `aarch64-dmi-test-async-inval (CPU=4)` | 미측정 — 제외 |
| 20 | `reset-test-system (CPU=1)` | 미측정 — 제외 |
| 21 | `reset-test-system (CPU=2)` | 미측정 — 제외 |
| 22 | `reset-test-system (CPU=4)` | 미측정 — 제외 |
| 23 | `reset-test-cpu (CPU=1)` | 미측정 — 제외 |
| 24 | `reset-test-cpu (CPU=2)` | 미측정 — 제외 |
| 25 | `reset-test-cpu (CPU=4)` | 미측정 — 제외 |
| 26 | `aarch64-start-in-reset-release-test` | 미측정 — 제외 |

제외 목록은 `QBOX_CORE_TEST_EXCLUDE_REGEX`로 관리한다.
호스트 부하나 CPU 조합을 바꾸면 실행 시간이 달라질 수 있으므로 재측정이 필요하다.
이번 측정에서는 제외 정책을 해제하거나 timeout을 늘리지 않았다.

## 7. 재현 명령

프로젝트 루트에서 다음 명령을 실행했다.
`-f`는 이전 task stamp를 재사용하지 않고 `do_check`를 실제로 재실행하기 위한 옵션이다.

```bash
mkdir -p build/qbox-unit-tests/timing-20260909-114606
source layers/poky/oe-init-build-env build

/usr/bin/time \
  -f 'elapsed_seconds=%e\nuser_seconds=%U\nsystem_seconds=%S\nexit_status=%x' \
  -o ../build/qbox-unit-tests/timing-20260909-114606/bitbake-wall-time.txt \
  env MACHINE=apollo-qvp bitbake \
  -R conf/apollo-bitbake-resources.conf \
  qbox-apollo-qvp-native -c check -f \
  > ../build/qbox-unit-tests/timing-20260909-114606/bitbake.log 2>&1
```

재현 시에는 기존 증거를 덮어쓰지 않도록 다른 측정 디렉터리 이름을 사용한다.
resource 설정은 이번 실행에서 `BB_NUMBER_THREADS=6`, `PARALLEL_MAKE=-j6`이었다.
이는 빌드 병렬도이며 CTest를 병렬 실행했다는 뜻은 아니다.

실제 task 실행은 903개 중 902개를 재사용하고 `do_check`를 새로 실행했다.
종료 코드는 0이며, 강제 실행에 따른 `tainted from a forced run` 경고 1건만 있었다.
이 경고는 테스트 실패가 아니다.

## 8. 원본 증거

이번 실행 직후 recipe의 `temp/` 결과를 아래 디렉터리로 복사했다.

- [BitBake 실행 로그](../../build/qbox-unit-tests/timing-20260909-114606/bitbake.log)
- [명령 전체 경과 시간](../../build/qbox-unit-tests/timing-20260909-114606/bitbake-wall-time.txt)
- [do_check 전체 로그](../../build/qbox-unit-tests/timing-20260909-114606/log.do_check)
- [qbox core JUnit XML](../../build/qbox-unit-tests/timing-20260909-114606/qbox-core-unit-tests.xml)
- [qbox core CTest 로그](../../build/qbox-unit-tests/timing-20260909-114606/qbox-core-unit-tests.log)
- [qbox core 실행 목록](../../build/qbox-unit-tests/timing-20260909-114606/qbox-core-unit-tests.list)
- [qbox core 제외 목록](../../build/qbox-unit-tests/timing-20260909-114606/qbox-core-unit-tests.excluded.list)
- [qbox-platform JUnit XML](../../build/qbox-unit-tests/timing-20260909-114606/qbox-platform-unit-tests.xml)
- [qbox-platform CTest 로그](../../build/qbox-unit-tests/timing-20260909-114606/qbox-platform-unit-tests.log)
- [qbox-platform 실행 목록](../../build/qbox-unit-tests/timing-20260909-114606/qbox-platform-unit-tests.list)
- [CMake 설정 스냅샷](../../build/qbox-unit-tests/timing-20260909-114606/CMakeCache.txt)

`build/`의 원본 증거는 로컬 생성 산출물이다.
위 개별 시간표와 요약 수치는 이 Markdown 문서에 함께 보존한다.
