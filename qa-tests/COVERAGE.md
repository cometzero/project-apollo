# Apollo runtime pytest coverage

이 문서는 **구현된 검사와 기존 assertion ID의 대응** 및 최초 실행의 발견 사항을
기록합니다. 대응표 자체는 실제 QBox 실행 성공을 보장하지 않으며,
host unit test/collection 성공을 runtime PASS로 간주하지 않습니다.

`tests/`는 실제 플랫폼을 사용하는 runtime suite입니다. `unittests/`는 manager,
parser, 실행 제어와 증거 계약을 host fixture로 검사합니다. Runtime test는 upstream
형태의 `platform_base_obj.mgr` API로 명령과 로그를 처리합니다. 기존
`scripts.run.qbox_validation.registry.canonical_matrix_path()`가 반환하는 matrix의
14개 profile / 99개 assertion 중 11개 profile / 79개 assertion을 이관했습니다.
나머지 20개 assertion은 3개 명시적 SKIP case입니다.

프로필의 연속 명령은 하나의 pytest case에서 실행하고 기존 evaluator로 판정합니다.
PSA suite totals, CPU별 반복 및 복원 결과는 그대로 검사합니다. 한 번 측정한 시간을
여러 가상 testcase에 나누어 기록하지 않습니다. 프로필 case의 JUnit properties에는
`validation_profile`과 실제 평가된 `assertions` JSON을 기록합니다.

## 프로필 대응

아래 경로는 `qa-tests/tests/` 기준입니다. `image` marker는 실제 이미지 의존성으로
`bsp-only`, `product-only`, `any`를 구분합니다. legacy profile의 BSP/product 목록은
이 pytest suite에 적용하지 않습니다. 기본 부팅·topology·DSU·장치 검사와 실제 SSH 검사는
프로필 실행과 별도로 명확한 이름의 pytest case를 제공합니다.

| 기존 profile | Runtime 파일 | 기존 assertion 수 | 구현 상태 |
|---|---|---:|---|
| `bsp-core` | `아래 BSP 분해 표` | 10 | 구현; runtime 결과 별도 |
| `platform-devices` | `ap/devices/test_platform_devices.py` | 7 | 구현; runtime 결과 별도 |
| `trusted-services` | `ap/security/test_trusted_services.py` | 4 | 구현; runtime 결과 별도 |
| `pfdi` | `ap/safety/test_primary_pfdi.py` | 7 | 구현; runtime 결과 별도 |
| `pfdi-si-cl1` | `si_cl1/safety/test_cluster_pfdi.py` | 17 | 구현; runtime 결과 별도 |
| `safety-diagnostics-tests` | `si_cl0/safety/test_safety_diagnostics.py` | 2 | 구현; runtime 결과 별도 |
| `ras_cpu` | `ap/safety/test_cpu_ras.py` | 9 | 구현; runtime 결과 별도 |
| `si-cl1` | `si_cl1/devices/test_kernel_shell.py` | 1 | 구현; runtime 결과 별도 |
| `crypto-extension` | `ap/security/test_crypto_extensions.py` | 1 | SKIP; QBox probe 미구현 |
| `cpuidle` | `ap/power/test_cpu_idle.py` | 8 | 구현; runtime 결과 별도 |
| `cpufreq` | `ap/power/test_cpu_frequency.py` | 10 | 구현; runtime 결과 별도 |
| `mbpp` | `ap/power/test_cpu_parking.py` | 9 | SKIP; QBox probe 미구현 |
| `hipc` | `si_cl1/network/test_hipc_network.py` | 10 | SKIP; QBox probe 미구현 |
| `smcf` | `si_cl0/safety/test_sensor_monitoring.py` | 4 | 구현; runtime 결과 별도 |

## BSP core의 도메인별 분해

기존 `bsp-core`의 세 명령과 부팅 로그 판정은 다음 독립 검사로 나눴습니다.
`bsp-uboot-boot`와 `pc-cpus-linux`는 여러 조건을 합친 기존 assertion이므로
해당하는 모든 새 검사가 성공해야 기존과 같은 범위를 충족합니다.

| 기존 assertion ID | 새 runtime 검사 |
|---|---|
| `bsp-scp` | `si_cl0/boot/test_scp_boot.py::test_scp_boot_and_cmn_discovery` |
| `bsp-uboot-boot` | `ap/boot/test_uboot_boot.py::test_uboot_boot_and_efi_handoff` + `ap/devices/test_bsp_devices.py::test_rtc_watchdog_and_rng_interfaces` |
| `bsp-safety-island-cl1` | `si_cl1/boot/test_zephyr_boot.py::test_zephyr_boot_and_secondary_cpus` |
| `rse-normal-boot` | `rse/boot/test_rse_boot.py::test_rse_normal_boot_and_ap_power_on` |
| `rse-measured-boot` | `rse/boot/test_rse_boot.py::test_rse_measured_boot` |
| `primary-fvp-boot` | `ap/boot/test_linux_boot.py::test_linux_boot_and_userspace_handoff` + `ap/devices/test_linux_shell.py::test_linux_uart_executes_guest_command` |
| `ap-dsu-cluster` | `ap/devices/test_dsu_pmu.py::test_dsu_pmu_events_under_memory_traffic` |
| `pc-cpus-tfa` | `ap/boot/test_optee_boot.py::test_optee_primary_and_secondary_cpu_boot` (실제 관측은 OP-TEE secondary CPU handoff) |
| `pc-cpus-linux` | `ap/devices/test_cpu_topology.py::test_four_cpu_topology_and_shared_cache` + `test_secondary_cpu_hotplug_and_restore` |
| `secure-partition-optee` | `ap/security/test_secure_partition.py::test_optee_and_secure_partitions` |

별도 `ap/boot/test_tfa_boot.py`가 TF-A BL2→BL31→EL3 exit를 검사합니다.
SI CL1의 `devices/test_kernel_shell.py`는 Zephyr version 명령과 secondary CPU 로그를
검사하여 `si-cl1` profile의 `safety-island-cluster1`도 충족합니다. AP secure console은 AP 도메인이며
RSE console과 구분합니다.

## 이미지 적용 범위

현재 28개 case 중 `bsp-only` 0개, `product-only` 3개, `any` 25개입니다.

| 분류 | Case / 이유 |
|---|---|
| `product-only` | `ap/devices/test_platform_devices.py`: OVS bridge와 systemd boot 로그 |
| `product-only` | `ap/security/test_trusted_services.py`: PSA crypto/PS/ITS/IAT 테스트 바이너리 |
| `product-only` | `ap/safety/test_cpu_ras.py`: ts-ras-inject 및 rasdaemon/systemd journal |
| `any` | 나머지 25개; 공통 boot/kernel/firmware/UART/SSH 기능과 미구현 placeholder |

기존 BSP 전용 6개(cpufreq, cpuidle, AP/CL1 PFDI, FMU/SSU, SMCF)를 `any`로 바꿨습니다.
CPU idle의 BSP 전용 CPU 설정 파일 의존성은 kernel sysfs로 교체하고,
AP PFDI는 Product의 systemd 서비스/journal과 BSP의 process/log 파일 경로를 처리합니다.
`any`는 실행 대상 분류이며 양쪽 이미지에서의 검증 완료를 의미하지 않습니다.
미구현 MBPP/crypto/HIPC 및 실제 모델 제약에 의한 SKIP은 유지합니다.

이미지 범위 확대 중 드러난 두 판정 오류도 수정했습니다.

- CPU frequency의 범위 밖 숫자 요청은 Linux QoS가 허용하고 실제 policy를 한계 안으로
  보정합니다. `cpufreq-min-max-negative`는 2.6 GHz 최소 요청 → 2.5/2.5 GHz,
  1.7 GHz 최대 요청 → 1.8/1.8 GHz와 원래 설정 복원을 확인합니다. 무시된 요청이나
  범위 밖 실제 값은 FAIL이며, 비동기 policy 반영은 제한 시간 안에서 기다립니다.
- SI CL1은 Zephyr `arch/arm64/core/reset.S`의 primary 선출 및 `smp.c`의 DT CPU 순서를
  따릅니다. 논리 secondary CPU 1–3은 primary를 제외한 세 MPID여야 하며, physical
  CPU 0만 primary라고 가정하지 않습니다. 누락·중복·잘못된 MPID/순서는 계속 FAIL입니다.

### 2026-10-23 이미지 분류·부팅 검사 재검증

증거 디렉터리는 `build/qbox-apollo-qvp/image-scope-boot/`입니다.
각 실행의 report.html/results.json/JUnit과 UART 원본을 유지하며, 재검사로 이전 결과를 덮어쓰지 않았습니다.

| 실행 | 실제 결과 | 보고서 |
|---|---|---|
| Host framework·공통 probe 회귀 | 498 PASS, 2 dependency deprecation warnings | [host](../build/qbox-apollo-qvp/pytest-20261023T063855Z-vmfw0aww/report.md) |
| 최초 Product 전체 28개 | 15 PASS / 1 FAIL / 3 SKIP / 9 ERROR; boot 8개는 PASS | [전체 원본](../build/qbox-apollo-qvp/image-scope-boot/runtime-product-all/report.html) |
| Product 공통 기능 재실행 | 4 PASS / 1 FAIL / 1 SKIP | [공통 기능](../build/qbox-apollo-qvp/image-scope-boot/runtime-product-common/report.html) |
| Product CPU frequency 수정 후 | 1 PASS; 실제 clamp와 원상 복원 확인 | [CPU frequency](../build/qbox-apollo-qvp/image-scope-boot/runtime-product-cpufreq-final/report.html) |
| 최초 BSP boot | 7 PASS / 1 FAIL; SI CL1 고정 MPID 기대 오류 | [BSP 원본](../build/qbox-apollo-qvp/image-scope-boot/runtime-bsp-boot/report.html) |
| BSP boot 수정 후 + Zephyr shell | 9 PASS (boot 8개, shell 1개) | [BSP 재검증](../build/qbox-apollo-qvp/image-scope-boot/runtime-bsp-boot-final/report.html) |

Product 공통 기능의 PASS는 AP PFDI, FMU/SSU, Zephyr kernel shell, SI CL1 PFDI입니다.
CPU idle은 실제 DT/sysfs의 `psci_powerdown_wakeup_unmodeled` 제약을 확인한 SKIP입니다.
SMCF는 `test smcf`의 integration PASS/End를 받았지만 120초 안에 센서 샘플/시작 로그가
없어 command rc=124로 FAIL입니다. 이 실패를 이미지 미지원 SKIP으로 바꾸지 않았습니다.

최초 Product의 CPU frequency FAIL은 위 경계값 판정 수정 후 해소했습니다.
그 뒤 run-0004에서 RSE의 `SCP is not ready. Abort`로 재부팅이 실패하여 9개가 ERROR로
기록됐습니다. 새 실행에서 해당 공통 기능을 검사했지만 간헐 RSE–SCP 초기화 문제 자체는
이번 변경으로 해결했다고 주장하지 않습니다. 중단된 첫 boot 실행도 별도 interruption 기록으로 보존했습니다.

[검증 집계](../build/qbox-apollo-qvp/image-scope-boot/verification.json)는 모든 실행 소유 PID가
정리됐음을 확인합니다. 실패한 초기 실행의 상태는 유지했습니다. 기존 prebuilt 이미지를
사용했으며 이미지 재빌드, 전체 BSP 기능, FVP/물리 보드 검증은 수행하지 않았습니다.

## 보존한 assertion ID

아래 ID는 기존 matrix와 대조하는 식별자입니다. 새 테스트의 도메인/category는
실제 명령 대상과 기능을 기준으로 정했습니다. cross-domain 관찰도 유지합니다.


### platform-devices

`platform-device-networking`, `platform-device-rtc`, `platform-device-cpu-hotplug`, `platform-device-virtiorng`, `platform-device-watchdog`, `primary-ssh`, `systemd-boot-message`.


### trusted-services

`ts-psa-crypto-api-test`, `ts-psa-ps-api-test`, `ts-psa-its-api-test`, `ts-psa-iat-api-test`.


### pfdi

`pfdi-systemd-service`, `pfdi-app`, `pfdi-cli`, `pfdi-cli-force-error`, `pfdi-app-monitoring`, `pfdi-app-monitoring-error`, `pfdi-sbistc`.


### pfdi-si-cl1

`si-pfdi-cluster-status`, `si-pfdi-run-all-tests`, `si-pfdi-run-block`, `si-pfdi-run-invalid-params`, `si-pfdi-run-block-valid`, `si-pfdi-run-range-valid`, `si-pfdi-invalid-cpu-value`, `si-pfdi-cpu-out-of-range`, `si-pfdi-count-blocks`, `si-pfdi-count-block-parts`, `si-pfdi-result`, `si-pfdi-set-state-toggle`, `si-pfdi-force-error-effect`, `si-pfdi-multiple-runs-consistency`, `si-pfdi-stress`, `si-pfdi-info`, `si-pfdi-monitoring`.


### safety-diagnostics-tests

`safety-island-fmu`, `safety-island-ssu`.


### ras_cpu

`ras-inject-list`, `ras-inject-invalid-cpu-error`, `ras-inject-usage`, `ras-inject-correctable-cpu-error`, `ras-inject-deferred-cpu-error`, `ras-inject-correctable-cpu-error-10x`, `ras-inject-uncorrectable-cpu-error`, `ras-inject-correctable-deferred-cpu-error`, `ras-journalctl-service`.


### si-cl1

`safety-island-cluster1`.


### crypto-extension

`cryptographic-extension-performance`.


### cpuidle

`cpuidle-ensure`, `cpuidle-c-states`, `cpuidle-default-status`, `cpuidle-disable-state`, `cpuidle-residency-latency`, `cpuidle-governors`, `cpuidle-governor-switching`, `cpuidle-invalid-governor`.


### cpufreq

`cpufreq-policy`, `cpufreq-default-governors`, `cpufreq-set-governors`, `cpufreq-scaling-driver`, `cpufreq-current-frequency-per-governor`, `cpufreq-affected-cpus-per-policy`, `cpufreq-invalid-governor`, `cpufreq-scaling-min-frequencies`, `cpufreq-scaling-max-frequencies`, `cpufreq-min-max-negative`.


### mbpp

`mbpp-script-exists`, `mbpp-help-and-list`, `mbpp-set-parking`, `mbpp-idempotent-profiles`, `mbpp-case-insensitive-profiles`, `mbpp-invalid-profile`, `mbpp-toggle-all-modes`, `mbpp-all-cores-online`, `mbpp-restore-default-governor`.


### hipc

`hipc-dt-and-shared-memory`, `hipc-linux-stack`, `hipc-memory-layout`, `hipc-icmp-bidirectional`, `hipc-udp-pc-to-cl1`, `hipc-tcp-pc-to-cl1`, `hipc-udp-cl1-to-pc`, `hipc-tcp-cl1-to-pc`, `hipc-boundary-payload-sizes`, `hipc-boundary-multistream`.


### smcf

`smcf-client-start`, `smcf-execute-test`, `smcf-run-3x`, `smcf-sensor-monitor`.


## Transport와 상태 변경의 경계

- `get_port("ap"/"secure"/"rse"/"si_cl0"/"si_cl1"/"ssh")`로 port를 얻습니다.
  명령은 `execute_command_with_prompt_capture(port, command, timeout)`에 전달하고,
  로그는 `read_log`, 부팅/비동기 완료는 `wait_for_prompt_in_log`로 확인합니다.
- 기존 `ProbeStep.command`는 raw command입니다. SI CL0의 Ctrl-E/Ctrl-D 및 newline,
  AP shell return-code framing은 manager가 소유합니다. helper에서 중복하지 않습니다.
- SI CL0 SMCF는 CLI exit 뒤에 나오는 sample까지 기다립니다. QBox manager의
  `command_completion_patterns[(port, command)]` 확장에 기존 step의 완료 regex를
  전달하고 종료 후 원래 설정을 복원합니다. manager가 보유한 로그 cursor에서
  새 구간을 캡처하므로 CR/ANSI 정규화에 의한 offset 차이나 이전 결과 재사용을
  피합니다. 실제 실행은 upstream 형태의 execute API를 그대로 사용합니다.
- SI CL1의 invalid CPU/인자 검사는 의도적인 firmware error가 정상 결과입니다.
  firmware rc 0/1은 기존 evaluator가 판정하고, transport timeout/exit rc 124/125는
  즉시 실패합니다. AP/SSH는 실제 shell rc 0이 필요합니다.
- PFDI force-error, CPU RAS, SI CL1 PFDI, FMU/SSU, SMCF, CPU frequency/idle,
  hotplug 포함 device case에는
  `destructive` marker가 있습니다. fixture는 다음 검사 전에 새 generation을 부팅해야
  합니다. CPU frequency/idle 명령은 원래 governor/limit/enable 상태를 복원하고 그
  복원 기록을 evaluator가 검증합니다. 중간 timeout으로 복원이 완료되지 못한 경우도
  다음 검사에 영향을 주지 않도록 동일한 재시작 경계를 적용합니다.
- 정상 completion 없는 명령, 누락/실패 assertion 및 cleanup 실패는 PASS가 아닙니다.
  cpuidle의 `unsupported:psci_powerdown_wakeup_unmodeled`는 명시적 SKIP입니다.

## 기존 이름과 실제 의미

`platform-devices`의 기존 `primary-ssh` assertion은 **AP UART command/topology/DSU**
검사입니다. 기존 evaluator·비교 결과와 호환하려고 ID는 보존하지만 SSH 성공으로
해석하지 않습니다. 실제 SSH guest 명령 검사는 새 파일
`ap/network/test_ssh.py::test_primary_ssh_executes_guest_command`에서 `ssh` port로
별도 수행하며 Linux/aarch64/root 응답과 실제 명령 return code를 검사합니다.
BSP와 product 모두 이 검사를 실행합니다. BSP의
`NEXIOS_BSP_SSH daemon=dropbear result=PASS` 부팅 기록은 daemon 기동 증거이며,
SSH 연결·인증·명령 성공은 별도 SSH case의 결과로 판단합니다.

RSE normal/measured boot는 로그 관찰입니다. watchdog은 driver/device 존재 확인이며
watchdog 만료·reset 검사는 아닙니다. CPU idle residency는 모델/driver 기능 증거이고
실리콘 전력·시간 보증이 아닙니다. PSA tests는 crypto 60/57/3, PS 17/11/6,
ITS 10/10/0, IAT 1/1/0의 total/pass/skip 기대값을 유지합니다.

`crypto-extension`, `hipc`, `mbpp`는 실행 구현이 없어 명시적으로 SKIP합니다.
Crypto FVP plugin 시간 측정은 QBox 검증을 대신하지 않으며, MBPP는 별도 16-CPU
lane이 필요합니다. HIPC driver 탐지는 양방향 TCP/UDP/ICMP 시험을 대신하지 않습니다.

## 최초 BSP 실행의 발견 사항

`build/qbox-apollo-qvp/qa-redesign/runtime-bsp/results.json`의 최초 실행은
25개 case 중 12 PASS, 5 FAIL, 8 SKIP였습니다. CPU topology 실패는 실제 CPU/DT/cache
값을 추가 출력하도록 했고, cpufreq의 여러 policy 이름을 비교할 때 발생한 shell
quoting 오류는 수정했습니다. SI CL0 FMU/SSU는 CLI 종료 이후 비동기 응답 처리 경계를
추가 확인해야 합니다. SMCF는 integration 결과가 성공이어도 요구한 sensor sample이
없어 timeout FAIL이며, SI CL1은 Zephyr 부팅/SMP 로그가 있어도 `kernel version`
명령에 `kernel: command not found`가 반환되어 기능 검사 FAIL입니다. 이 실패를
SKIP이나 PASS로 바꾸지 않습니다. 최초 실행에서는 SSH가 product 전용 marker 때문에
SKIP되었으므로 BSP의 실제 SSH 기능도 재실행 결과가 필요합니다. 수정 후 runtime 결과와
product 이미지의 결과는 각각의 실행 증거로 별도 확인해야 합니다.

## 기존 runner에 남은 별도 범위

`--post-login-probe`, `--secure-service-probe`, `--fwu-probe`,
`--dwc-peripheral-probe`, `--primary-operation-manifest`, vMCU/CAN과 GIC/PCIe 전용
validation workflow는 위 79개 assertion의 일부로 간주하지 않습니다. 기존 launcher와
해당 명시적 경로를 유지하며, runtime pytest 이전에는 별도 범위·fixture가 필요합니다.

## 재설계 시점 검증 기록 (2026-10-23 KST)

전체 host pytest는 2592 PASS / 9 SKIP이다. Product 전체 runtime은
11 PASS / 4 FAIL / 9 SKIP / 1 ERROR이며, 실제 SSH와 PSA suite는 PASS했다.
HTTP fixture 보완 후 장치 profile은 내부 6 PASS / 1 FAIL이며 networking은 PASS,
남은 legacy `primary-ssh` assertion은 CPU topology 계약 불일치다.

수정 후 BSP 단독 실행은 테스트 명령 이전 RSE BL2의
`SCP is not ready. Abort`로 19 setup ERROR / 6 SKIP을 기록했다.
따라서 SI CL0 adapter와 cpufreq 수정의 host 회귀는 통과했지만 최신 BSP live 재검증은
완료하지 못했다. 최초 BSP 결과를 대체하거나 전체 runtime PASS로 주장하지 않는다.

세부 결과·원본 로그·입력 검증은 workspace의
`build/qbox-apollo-qvp/qa-redesign/review.md` 및 각 run의 자동 report를 참조한다.

## Product 실패 수정 후 검증 (2026-10-23 KST)

CPU 수에 맞는 DT 선택, Linux CPER/RAS consumer, Zephyr kernel shell,
SCP CPU_OFF 완료 순서와 PD 중복 알림 처리를 수정했다.
전체 host pytest는 2,635 PASS / 9 SKIP이며, 실제 hotplug 8회 및 watchdog 만료 후
AP 재부팅·IRQ 재활성화도 PASS했다. 최종 Product runtime은 **16 PASS / 9 SKIP**,
FAIL/ERROR 0건이며 704.87초가 걸렸다. 4개 세션의 cleanup도 모두 PASS했다.
자동 report는 `build/qbox-apollo-qvp/product-runtime-fix/runtime-product-validated/`에
보존했다. Runtime의 9 SKIP은 BSP 전용 6개와 QBox probe 미구현 3개이며,
이 결과로 BSP/FVP 또는 16-CPU 실행을 검증했다고 간주하지 않는다.

원인, 변경 범위, 수정 전 실패와 수정 후 검증은
[Product runtime 실패 수정](../doc/qa-product-runtime-fixes.md)에 기록한다.
