# Apollo GIC-720AE FVP 대비 QBox 테스트 완료 보고서

작성일: 2026-07-29

계획: [`test-plan.md`](test-plan.md)

분석: [`analysis.md`](analysis.md)

## 1. 완료 판정

테스트 실행과 증거 분류는 완료했다. 최종 결과는 **FVP 대비 전체 기능
동등성 FAIL**이다.

이 FAIL은 QBox가 부팅하지 못한다는 뜻이 아니다. 현재 QBox는 AP Linux의
GICv3/ITS 초기화, 4 CPU, timer PPI, FVP와 동일한 주요 discovery marker,
SCP/Zephyr production image의 기본 SI liveness를 제공한다. 반면
SI shared multiview routing, FuSa/RAS, power/reset, real-time/collator,
현재 MSI/LPI delivery와 directed SI interrupt test는 완료되지 않았다.

| 도메인 | 결과 | 검증 수준 |
| --- | --- | --- |
| Primary Compute / Linux | 부분 PASS | GIC/ITS discovery, 4 CPU, per-CPU timer PPI |
| Safety Island CL0 / SCP-firmware | 부분 PASS | multiview 설정/liveness, generic host unit test |
| Safety Island CL1 / Zephyr | build PASS, runtime BLOCKED | SMP/IPI test image compile/link, 주입 실행 timeout |
| SI shared multiview | FAIL | 구현 자체가 독립 GIC/static route 구조 |
| FuSa/RAS/power/realtime | FAIL/미검증 | 동작 모델과 targeted runtime 부족 |

## 2. 증거 디렉터리

이번 검증의 root-owned 증거:

[`build/qbox-apollo-qvp/gic-720ae-validation-20260729-195140/`](../../../build/qbox-apollo-qvp/gic-720ae-validation-20260729-195140/)

주요 파일:

| 파일 | 의미 |
| --- | --- |
| `static-and-root-tests.log` | Python, map, boundary, topology, root pytest |
| `component-rebuild-and-test.log` | GIC component 두 개 재빌드와 15 tests |
| `component-reconfigure-off.log` | generated cache를 원래 OFF로 복원 |
| `ap-linux-gic-parity.json` | FVP/QBox Linux discovery 비교 |
| `full-coverage-audit.json` | 보존 full-system artifact coverage 분류 |
| `fvp-gic-introspection.txt` | 설치된 FVP instance/parameter 원본 |
| `fvp-gic-params-concise.txt` | AP/SI GIC 핵심 FVP parameter |
| `fvp-binary-sha256.txt` | FVP executable provenance |
| `scp-host-tests.log` | SCP generic FMU, timer, MHU host tests |
| `scp-gic-fmu-target-missing.log` | GIC/MHU FMU target 미생성 재현 |

추가 runtime/build 증거:

- AP Linux:
  [`linux-gic-probe-20260729/`](../../../build/qbox-apollo-qvp/linux-gic-probe-20260729/)
- 중단된 AP custom probe:
  [`linux-gic-custom-probe-20260729/`](../../../build/qbox-apollo-qvp/linux-gic-custom-probe-20260729/)
- Zephyr SMP runtime 시도:
  [`si-cl1-smp-test-wave2-20260729/`](../../../build/qbox-apollo-qvp/si-cl1-smp-test-wave2-20260729/)
- Zephyr SMP build:
  [`zephyr-si-cl1-tests-20260729-wave2-smp-production-modules/`](../../../build/zephyr-si-cl1-tests-20260729-wave2-smp-production-modules/)
- Zephyr directed/broadcast IPI build:
  [`zephyr-si-cl1-tests-20260729-wave2-ipi-production-modules/`](../../../build/zephyr-si-cl1-tests-20260729-wave2-ipi-production-modules/)

## 3. 테스트 결과

### TP-01 활성 구성 및 source baseline: PASS

확인값:

```text
MACHINE                  apollo-qvp
RD_ASPEN_VARIANT         cfg2
PC_CPUS_COUNT_DEFAULT    4
TMPDIR                    build/tmp_baremetal
```

정확한 repository SHA는 분석 문서 2.2절에 기록했다.

### TP-02 map/topology/static validator: PASS

실행:

```bash
python3 -m py_compile \
  scripts/test/compare_qbox_fvp_gic_logs.py \
  scripts/test/validate_qbox_apollo_pcie_irq_runtime.py
python3 scripts/test/validate_qbox_apollo_fvp_full_map.py
python3 scripts/test/audit_qbox_core_boundary.py
python3 scripts/test/validate_qbox_apollo_topology.py
pytest -q tests
```

결과:

```text
full-map validator       PASS, 80 checks
QBox core boundary       PASS
Apollo topology          PASS
root pytest              79 passed in 9.20s
```

artifact:

- [`full-map-validation.json`](../../../build/qbox-apollo-qvp/full-map-validation.json)
- [`topology/validation.json`](../../../build/qbox-apollo-qvp/topology/validation.json)

이 결과는 주소, component 존재, Lua wiring과 tooling 회귀만 검증한다.

### TP-03 GIC component build/test: PASS, 제한적 의미

generated build tree를 임시로 `BUILD_TESTING=ON`으로 재구성한 뒤 두 test
executable을 현재 source에서 다시 빌드하고 실행했다. 종료 후 cache는
원래 `BUILD_TESTING=OFF`로 복원했다.

결과:

```text
gicx00_multiview-tests    11/11 PASS
gic720ae_messreg-tests     4/4 PASS
CTest                      2/2 PASS
```

build 중 SDK Meson shim이 `meson.real`을 찾지 못해 `Makefile.mtest`
재생성 warning을 출력했으나 QEMU install, component build, test link와
CTest는 종료 코드 0이었다.

통과한 내용은 register reset/storage, RAZ/WI, address translation,
inactive redistributor discovery와 backend forwarding이다. 실제 IRQ
delivery, view ownership, power/reset, message interrupt는 시험하지 않는다.

### TP-04 FVP/QBox AP Linux discovery parity: PASS

입력:

- FVP:
  `build/qbox-apollo-qvp/timer-refcnt-fvp-20260724/run/uarts/u_boot_linux.log`
- QBox:
  `build/qbox-apollo-qvp/yocto-apollo-qvp-20260729-193302/qbox-primary-console.log`

결과:

```text
960 SPI                             PASS
GICv3 DirectLPI                     PASS
GICv4 DirectLPI/RVPEID/Valid+Dirty  PASS
GICv4.1 mode                        PASS
32768 interrupt collections         PASS
DirectLPI VPE invalidation setup    PASS
```

FVP와 QBox log 생성일이 다르고 parser는 Linux 문자열을 비교한다. 이
PASS는 raw register bit equality 또는 interrupt delivery parity가 아니다.

### TP-05 Primary Compute Linux runtime: 부분 PASS / overall BLOCKED

실행 결과:

[`linux-gic-probe-20260729/result.json`](../../../build/qbox-apollo-qvp/linux-gic-probe-20260729/result.json)

```text
passed                    false
verdict                   blocked
blocker                   qbox_post_login_probe_failed
G0                        pass
G1                        blocked
G2                        blocked
```

GIC 관련 positive evidence:

- GICv3, 960 SPI, 16 PPI, DirectLPI
- GICv4.1 ITS, 8192 device, 32768 collection, 8192 virtual CPU table
- CPU0-3 redistributor와 LPI pending table 초기화
- `possible=0-3`, `online=0-3`
- `/proc/interrupts`의 `arch_timer`:
  `4815 4780 4815 4827`, 네 CPU 모두 timer IRQ 처리
- UART, virtio-mmio, MHU 등 여러 SPI의 non-zero counter
- SMMU, RTC, MMIO timer, DSU IRQ descriptor

overall blocker는 GIC failure가 아니라 현재 BSP image에 `pfdi-cli`가 없어
고정 post-login probe의 PFDI 항목이 실패한 것이다.

미완료:

- before/after controlled IRQ delta
- IRQ affinity 변경
- CPU offline/online과 redistributor 재초기화
- MSI/MSI-X 및 physical LPI delivery
- virtual LPI injection

normal DT에는 PCI/MSI consumer가 없고 kernel은 virtualization/KVM을
비활성화한다. opt-in PCI profile을 재생성하지 않았으므로 과거 성공
문서를 현재 qualification으로 사용하지 않았다.

`linux-gic-custom-probe-20260729`는 임의 명령 주입을 위해 keep-alive로
실행했으나 `--no-post-login-probe` 경로가 input FIFO를 만들지 않았다.
명령을 주입하지 않고 runner process group을 종료했으며 `result.json`이
없다. 따라서 완료된 test로 인용하지 않는다.

### TP-06 Safety Island CL0 SCP-firmware: 부분 PASS

host test:

```text
fmu_ni710ae_unit_test      4/4 PASS
mod_gtimer_unit_test       2/2 PASS
mod_mhu3_unit_test        27/27 PASS
```

이 시험은 generic NI-710AE FMU, timer, MHU module logic을 검증한다.
Apollo GIC multiview와 GIC internal FMU 동작은 검증하지 않는다.

GIC/MHU FMU unit source에는 네 test가 있으나 CMake target selector가
뒤의 `fmu_ni710ae_unit_test` 값으로 덮어써진다.

```text
cmake --build build/scp-firmware-product-tests \
  --target fmu_gic_mhu_unit_test
ninja: error: unknown target 'fmu_gic_mhu_unit_test'
exit_code=1
```

runtime positive marker:

```text
SI GIC-multiview configured successfully
AP GIC-multiview configured successfully
Subscribed to FMU fault notifications
```

미완료:

- CL0-owned IRQ의 controlled handler delta
- `test fmu` 20-case suite
- `test_inject_gic_fmu`
- view assignment 변경에 따른 delivery 변화

canonical headless runner는 SI0 debugger CLI를 자동 입력하지 않는다.
또한 일부 QBox log에는 CL1 core 대상 PFDI monitor timeout이 반복된다.

### TP-07 Safety Island CL1 Zephyr: build PASS / runtime BLOCKED

Apollo CL1 board를 대상으로 upstream test를 source edit 없이 build-only로
컴파일했다.

| test | build | BIN SHA-256 |
| --- | --- | --- |
| `kernel.multiprocessing.smp` | PASS | `3c399caab5ba6d498e74be891c7a2e364eee9ee3bd93dae9f8432bcfd1779e9b` |
| `kernel.ipi_optimize.smp` | PASS | `58d7dffbdbdfc5f605f78f33a6d19630bbcecd9a829954aa0e837eea84f57836` |

Twister는 `--build-only`였으므로 `twister.json`의 scenario status는
`not run`이며, build error는 0이다. ELF에는 `arm_gic_init`,
`arm_gic_secondary_init`, `arch_smp_init`, directed/broadcast IPI와 Ztest
symbol이 포함된다.

SMP test image를 QBox의 `--si-cl1-image/--si-cl1-symbols`로 주입한
runtime:

```text
passed                    false
blocker                   qbox_platform_timeout
G0                        pass
G1                        not_run
G2                        blocked
SI1 UART                  0 bytes
```

RSE는 Image 4를 load했고 CL0은 네 CL1 core power-on을 관측했으나 SI1
test entry의 UART 실행은 관측되지 않았다. 이는 test image의 direct-loader
override와 RSE/FWU Image 4 layout/release 경계를 먼저 검증해야 함을
의미한다. GIC/IPI 자체 실패로 단정하지 않는다.

production Zephyr runtime의 4 CPU/PFDI/RPMsg marker는 liveness evidence로
유지하지만 directed IPI와 timer-to-IPI 기능 완료 근거는 아니다.

### TP-08 SI cross-view negative test: FAIL / 구현 부재 확인

동적 시험을 실행할 수 있는 shared multiview signal plane이 없다.
QBox source inspection 결과:

- SI0과 SI1은 독립 QEMU GIC
- `IVIEWR`/`VIEWR`은 register storage
- SPI ownership은 Lua static wiring
- shared distributor pending/active state 없음
- cross-view SGI 정책 없음

즉 negative test가 단순히 빠진 것이 아니라 현재 구조에서 FVP의 의미론이
구현되지 않았다. component 11 tests가 PASS해도 이 판정은 변하지 않는다.

### TP-09 FuSa/RAS/realtime/power: FAIL 또는 현재 검증 불가

| 기능 | 결과 |
| --- | --- |
| generic System FMU/SSU/APU denial | 부분 구현, GIC 전용 아님 |
| GIC internal FMU fault/RAS/GSPV | 미구현 |
| parity/CRC/lock-step containment | 미구현 |
| `GICR_PWRR` 실제 power effect | 미구현 |
| view/messreg runtime reset | 미구현 |
| Q/P channel | 미구현 |
| SPI Collator/message interrupt | 미구현 |
| real-time SPI priority/timing | 미구현 |
| confidential safety detail | 공개 정보로 검증 불가 |

FVP는 `fmu-blktype-num=6`과 redistributor PWRR 관리 기능을 노출하지만
QBox의 view model은 power/reset/fault signal을 갖지 않는다.

### TP-10 coverage와 문서 회귀: 제한적 PASS

coverage audit:

[`full-coverage-audit.json`](../../../build/qbox-apollo-qvp/gic-720ae-validation-20260729-195140/full-coverage-audit.json)

입력은 보존된 pass artifact
`yocto-apollo-qvp-20260729-193302/result.json`이다. audit은 PASS지만 G1은
non-gating `not_run`이고 GIC stimulus를 검증하지 않는다. 최신 AP probe가
overall blocked이므로 이 audit을 최신 full qualification으로 사용하지
않는다.

최종 검증:

```text
git diff --check                                      PASS
untracked 문서별 git diff --no-index --check          3/3 PASS
로컬 Markdown link/path 검사                          3 files, missing 0
```

증거:
[`doc-validation.log`](../../../build/qbox-apollo-qvp/gic-720ae-validation-20260729-195140/doc-validation.log)

## 4. 실행하지 못한 테스트와 정확한 이유

| 테스트 | 이유 |
| --- | --- |
| AP MSI-X→ITS→LPI/INTx | normal DT에 consumer 없음, opt-in 두-image profile 미실행 |
| AP vLPI | active kernel에 KVM/VFIO 없음 |
| AP affinity/hotplug delta | canonical runner에 arbitrary post-login command hook 없음 |
| SCP `test fmu` | headless SI0 CLI driver 없음 |
| SCP GIC/MHU FMU host test | CMake target 변수 덮어쓰기 |
| CL1 SMP/IPI runtime | test image의 RSE Image 4/FWU 주입·release 경계에서 timeout |
| cross-view negative routing | shared multiview signal/state 모델 자체 없음 |
| FuSa/power/realtime | target model과 stimulus 없음 |

## 5. 최종 해석

이번 결과로 다음 주장은 가능하다.

> 현재 QBox는 Apollo cfg2 4-CPU AP에서 Linux-visible GICv3/ITS 초기화,
> 네 CPU timer interrupt, FVP와 일치하는 주요 GICv4.1 discovery
> marker를 제공한다. SI production firmware도 기본 부팅과 multiview
> configuration facade를 사용한다.

다음 주장은 불가능하다.

> QBox가 FVP의 GIC-720AE 기능을 모두 구현하고 동작 검증했다.

불가능한 이유는 단순 test 누락뿐 아니라 shared multiview, GIC safety,
power/reset, real-time/collator 기능의 소스-level 구현 부재가 확인됐기
때문이다.
