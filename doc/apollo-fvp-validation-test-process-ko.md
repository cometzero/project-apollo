# Apollo FVP Validation Test Process

이 문서는 `./run_test.sh` 기반 Apollo FVP validation의 준비, 실행,
판정, 의존성, 측정 시간을 정리한다.

## 측정 기준

| 항목 | 값 |
| --- | --- |
| 측정 명령 | `./run_test.sh --category functional --timeout-fvp 300 --timeout-oeqa 10800 --stamp bist-functional-real --out-dir build/tests/bist-functional-real` |
| 결과 디렉터리 | `build/tests/bist-functional-real` |
| 최종 결과 | `PASS`, exit code `0` |
| 전체 실행 시간 | 약 `1178.739s` |
| stage evidence | `build/tests/bist-functional-real/summary.json` |
| basic boot evidence | `build/tests/bist-functional-real/fvp/result.json` |
| OEQA evidence | `build/tests/bist-functional-real/oeqa/functional/results/testresults.json` |

`power`, `extended`, `stress` category는 opt-in category이며 이 측정 run에서는
실행하지 않았다. 아래 개별 시간 표는 실제 실행된 `basic` + `functional`
항목만 측정값을 기록한다.

## 공통 실행 흐름

| 순서 | 단계 | 적용 category | 의존성/입력 | 처리 | PASS 판정 | FAIL/BLOCK 판정 | 측정 시간 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `context` | all | `build/conf/local.conf`, `build/conf/bblayers.conf`, `build/conf/templateconf.cfg`, deploy/testdata | active Yocto/FVP 설정을 `manifest.json`으로 저장 | manifest status가 `ok` | manifest status가 `blocked` | `<0.001s` |
| 2 | `lock` | `basic`, `functional`, `power` runtime | `build/tests/.run_test.lock` | 동시 FVP/OEQA runtime 실행 방지 | lock 획득 | lock held이면 `BLOCKED` | `<0.001s` |
| 3 | `basic-preflight` | `basic`, `functional`, `power` | `runfvp`, `telnet`, FVP conf/testdata, FVP binary, `Crypto.so`, boot images, rootfs, runtime SSH port | runtime 실행 전 필수 artifact 검사 | 모든 check가 `ok` | 누락 artifact/tool/port 문제면 `BLOCKED` | `0.062s` |
| 4 | `basic-boot` | `basic`, `functional` | preflight PASS, `scripts/run/runfvp_log_boot.py`, FVP conf, writable flash copies | FVP를 headless로 실행하고 UART log marker scan | required domain marker와 error scan이 통과 | timeout, marker 누락, fatal/error log 감지 | `112.152s` |
| 5 | `host-python` | `functional`, `power` runtime | `python3` candidates, `pexpect`, `ptyprocess` | OEQA용 host Python 선택 | import check 성공 | usable Python이 없으면 `BLOCKED` | `0.056s` |
| 6 | `oeqa-functional` | `functional` | basic boot PASS, host Python PASS, generated `oeqa-functional.conf` | `bitbake -R <conf> nexios-image -c testimage` 실행 | OEQA JSON에 fail/error가 없고 bitbake exit `0` | OEQA fail/error 또는 bitbake non-zero이면 `FAIL`; timeout이면 `BLOCKED` | `1066.377s` |

최종 summary 판정은 `commands.jsonl`의 record status를 합산한다.

| 조건 | 최종 결과 | exit code |
| --- | --- | --- |
| 하나라도 `fail` | `FAIL` | `1` |
| `blocked`가 있거나 record가 없음 | `BLOCKED` | `2` |
| 나머지 모든 record가 `pass` 또는 `skipped` | `PASS` | `0` |

## Category별 실행 모델

| Category | 실행 방식 | 주요 의존성 | PASS/FAIL 판정 | 측정 여부 |
| --- | --- | --- | --- | --- |
| `basic` | `context` -> `lock` -> `basic-preflight` -> `basic-boot` | FVP artifact, UART marker, fatal log scan | basic boot marker 전체 PASS면 PASS | `functional` run 안에서 측정됨 |
| `functional` | `basic` 전체 PASS 후 `host-python` -> `oeqa-functional` | basic boot PASS, host Python, functional OEQA suite | OEQA 개별 test가 fail/error 없이 완료 | 측정됨 |
| `power` | `context` -> `lock` -> `basic-preflight` -> `host-python` -> `oeqa-power` | host Python, power/reboot OEQA suite | power/reboot OEQA JSON 기준 | 이번 run 미측정 |
| `extended` | suite metadata 및 opt-in long/conformance tests | 각 extended test별 firmware, Linux, storage, secure/conformance 기능 | 실행한 lane/test의 결과 기준 | 이번 run 미측정 |
| `stress` | suite metadata 및 반복/soak성 tests | reboot/poweroff/PFDI/HIPC/CPU 반복 조건 | 반복 loop의 fail/timeout 기준 | 이번 run 미측정 |

## Basic Boot Marker 측정

`basic-boot`는 각 subsystem UART에서 marker first-hit 시간을 기록한다.

| Marker ID | Subsystem/console | PASS marker | First hit |
| --- | --- | --- | --- |
| `rse_bl1_1` | RSE `terminal_uart` | `Starting TF-M BL1_1` | `7.174s` |
| `rse_jump_bl1_2` | RSE `terminal_uart` | `Jumping to BL1_2` | `10.250s` |
| `rse_bl1_2` | RSE `terminal_uart` | `Starting TF-M BL1_2` | `10.256s` |
| `rse_attempt_image_0` | RSE `terminal_uart` | `Attempting to boot image 0` | `10.261s` |
| `rse_bl2_decrypted` | RSE `terminal_uart` | `BL2 image decrypted successfully` | `10.274s` |
| `rse_bl2_validated` | RSE `terminal_uart` | `BL2 image validated successfully` | `11.802s` |
| `rse_jump_bl2` | RSE `terminal_uart` | `Jumping to BL2` | `11.802s` |
| `rse_image_4_loaded` | RSE `terminal_uart` | `Image 4 loaded from the primary slot` | `12.041s` |
| `rse_image_3_loaded` | RSE `terminal_uart` | `Image 3 loaded from the primary slot` | `12.368s` |
| `si_cl0_module_init` | Safety Island CL0 `terminal_uart_si_cluster0` | `Module initialization complete` | `12.480s` |
| `si_cl1_zephyr` | Safety Island CL1 `terminal_uart_si_cluster1` | `*** Booting Zephyr OS build` | `12.651s` |
| `rse_image_2_loaded` | RSE `terminal_uart` | `Image 2 loaded from the primary slot` | `12.850s` |
| `rse_image_0_loaded` | RSE `terminal_uart` | `Image 0 loaded from the primary slot` | `12.996s` |
| `rse_scp_power_on_ap` | RSE `terminal_uart` | `RSE to SCP SCMI power on AP succeeded` | `15.184s` |
| `rse_first_image_slot` | RSE `terminal_uart` | `Jumping to the first image slot` | `15.187s` |
| `measured_boot_bl33` | TF-A `terminal_sec_uart` | `BL_33` | `17.096s` |
| `primary_linux_cpu` | Linux `terminal_ns_uart0` | `Booting Linux on physical CPU` | `36.661s` |
| `primary_linux_version` | Linux `terminal_ns_uart0` | `Linux version` | `36.665s` |

Basic boot domain 판정:

| Domain | Console | PASS 조건 | 측정 결과 |
| --- | --- | --- | --- |
| RSE / TF-M | `terminal_uart` | RSE boot/handoff markers present, error pattern 없음 | PASS |
| Safety Island CL0 / SCP-firmware | `terminal_uart_si_cluster0` | SCP/module init markers present, error pattern 없음 | PASS |
| Safety Island CL1 / Zephyr | `terminal_uart_si_cluster1` | Zephyr boot marker present, error pattern 없음 | PASS |
| TF-A / BL31 | `terminal_sec_uart` | BL2/BL31/EL3 exit markers present, error pattern 없음 | PASS |
| U-Boot / Linux | `terminal_ns_uart0` | U-Boot, Linux boot, multi-user/login marker present, error pattern 없음 | PASS |

## Functional OEQA 개별 테스트

실행 순서는 `log.do_testimage`의 `NOTE:` 순서를 기준으로 정리했다.

| 순서 | Test | Dependency | 테스트 과정 | PASS 판정 | FAIL/SKIP 판정 | 측정 시간 | 결과 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `test_00_rse.RseTest.test_normal_boot` | 없음 | FVP를 `on`으로 전환하고 RSE console에서 first image slot handoff 확인 | `Jumping to the first image slot` 관측, 이전 RSE buffer에 `[ERR]` 없음 | marker timeout 또는 `[ERR]` 포함 | `15.719s` | PASSED |
| 2 | `test_00_secure_partition.OpteeTest.test_optee_normal` | 없음 | TF-A console에서 OP-TEE/SP load 및 normal-world handoff 확인 | `Loading SP: SE Proxy`, `Loading SP: SMM Gateway`, `Primary CPU switching to normal world boot` 관측, `E/TC` 없음 | marker timeout 또는 `E/TC` 포함 | `2.353s` | PASSED |
| 3 | `ping.PingTest.test_ping` | target IP | target IP가 localhost이면 skip-equivalent return, 아니면 ping 5회 연속 성공 확인 | localhost 또는 ping 5회 연속 성공 | target IP 없음, ping timeout, 5회 연속 실패 | `0.001s` | PASSED |
| 4 | `ssh.SSHTest.test_ssh` | `ping.PingTest.test_ping`, SSH server package | SSH로 `uname -a` 실행, connection-refused성 오류는 제한적으로 retry | `uname -a` exit code `0` | retry 후 SSH 실패 또는 command 실패 | `264.024s` | PASSED |
| 5 | `test_20_aspen_ap_dsu.APDSUClusterTest.test_dsu_cluster` | `ssh.SSHTest.test_ssh` | Linux login 후 DSU L3 cache size/shared CPU list와 DSU PMU event 확인 | cache size `4096K`, shared CPU list 일치, `perf stat` event 출력 match | SSH/login 실패, sysfs 값 불일치, PMU command 실패 | `46.182s` | PASSED |
| 6 | `test_30_configurable_pc_cores.ConfiguredPCCPUSTest.test_configured_pc_cpus_in_linux` | `ssh.SSHTest.test_ssh` | Linux login 후 DT CPU node count와 `nproc --all` 확인 | 둘 다 `PC_CPUS_COUNT`와 일치 | command 실패, 숫자 parse 실패, CPU count 불일치 | `289.735s` | PASSED |
| 7 | `test_30_configurable_pc_cores.ConfiguredPCCPUSTest.test_configured_pc_cpus_in_tf_a` | 없음 | boot console에서 Linux SMP bring-up CPU 수 marker 확인 | `smp: Brought up 1 node, 4 CPUs` 관측 | marker timeout | `35.308s` | PASSED |
| 8 | `test_01_auto_ad_nexios_uki_boot.AutoAdNexiosUkiBootTest.test_01_uboot_uki_boot_markers` | console/log availability | default console log 또는 live console에서 slot/UKI/Linux boot marker 확인 | slot A, selected UKI filename, Linux boot marker 모두 present | marker 누락 | `0.007s` | PASSED |
| 9 | `test_01_auto_ad_nexios_uki_boot.AutoAdNexiosUkiBootTest.test_02_dm_verity_root` | `ssh.SSHTest.test_ssh`, `test_01_uboot_uki_boot_markers` | Linux에서 cmdline, root mount source/options, dm name 확인 | `root=PARTLABEL=rootro_a`, `/dev/mapper/rootfs` 또는 `/dev/dm-*`, root `ro`, dm name `rootfs` | command 실패 또는 root/dm-verity 조건 불일치 | `254.049s` | PASSED |
| 10 | `test_01_auto_ad_nexios_uki_boot.AutoAdNexiosUkiBootTest.test_03_writable_mounts` | `test_02_dm_verity_root` | `/rootrw`, `/data`, `/run` mount type 확인 후 writable path 쓰기/삭제 | expected mount type와 write test 모두 성공 | mount 불일치, write/delete 실패 | `27.360s` | PASSED |
| 11 | `fvp_devices.FvpDevicesTest.test_cpu_hotplug` | `ssh.SSHTest.test_ssh`, `TEST_FVP_DEVICES` | CPU hotplug sysfs 테스트 | `TEST_FVP_DEVICES`에 `cpu_hotplug` 포함 시 online/offline 동작 검증 | 미포함이면 SKIPPED; command/count 실패 시 FAIL | `0.001s` | SKIPPED |
| 12 | `fvp_devices.FvpDevicesTest.test_networking` | `ssh.SSHTest.test_ssh`, `TEST_FVP_DEVICES=networking` | `/sys/class/net` device/driver 확인 및 outbound `wget` 실행 | net device count와 driver match, `wget` 성공 | device/driver 불일치, `wget` 실패 | `40.033s` | PASSED |
| 13 | `fvp_devices.FvpDevicesTest.test_rtc` | `ssh.SSHTest.test_ssh`, `TEST_FVP_DEVICES=rtc` | `/sys/class/rtc` device/driver 확인 및 `hwclock` 실행 | `rtc-pl031` driver와 `hwclock` 성공 | device/driver 불일치 또는 command 실패 | `12.023s` | PASSED |
| 14 | `fvp_devices.FvpDevicesTest.test_virtiorng` | `ssh.SSHTest.test_ssh`, `TEST_FVP_DEVICES=virtiorng` | rng_available/current와 `/dev/hwrng` 확인 | `virtio_rng.0` selected, `hexdump -n 32 /dev/hwrng` 성공 | rng 불일치 또는 command 실패 | `12.668s` | PASSED |
| 15 | `fvp_devices.FvpDevicesTest.test_watchdog` | `ssh.SSHTest.test_ssh`, `TEST_FVP_DEVICES=watchdog` | `/sys/class/watchdog` device/driver 확인 | `sp805-wdt` 또는 `sbsa-gwdt` driver present | device/driver 불일치 | `7.805s` | PASSED |
| 16 | `test_10_linuxboot.LinuxBootTest.test_linux_boot` | 없음 | target state를 `linux`로 전환 | transition 성공 | Linux transition timeout/failure | `0.001s` | PASSED |

## Opt-in Category 테스트 구성

아래 항목은 suite 구성과 dependency를 정리한 것이다. 이번 측정 run에서는 실행하지
않았으므로 시간은 `미측정`으로 둔다.

| Category | Test | Dependency/조건 | 테스트 과정/판정 | 시간 |
| --- | --- | --- | --- | --- |
| `power` | `test_00_rse.RseTest.test_measured_boot` | `test_normal_boot` | FVP off/on 후 RSE measured boot markers 확인 | 미측정 |
| `power` | `test_00_rse.RseTest.test_scmi_poweroff` | `test_measured_boot` | Linux login, `poweroff`, RSE SCMI shutdown notification, FVP EOF 확인 | 미측정 |
| `power` | `test_00_rse.RseTest.test_scmi_reboot` | `test_measured_boot` | Linux login, `reboot`, RSE reset, TF-A SCMI init, Linux login 복귀 확인 | 미측정 |
| `power` | `fvp_boot` | meta-arm FVP runtime | FVP target boot transition 검증 | 미측정 |
| `extended` | `test_02_safety_boot.TestSafetyBoot.test_lbist` | early RSE BL2 marker | `BL2: SI LBIST happens here` marker 확인 | 미측정 |
| `extended` | `test_02_safety_boot.TestSafetyBoot.test_mbist` | early RSE BL2 marker | `BL2: SI MBIST happens here` marker 확인 | 미측정 |
| `extended` | `test_10_pfdi` | PFDI support/image | PFDI 기능 검증 | 미측정 |
| `extended` | `test_10_ras_cpu` | RAS CPU support | CPU RAS 기능 검증 | 미측정 |
| `extended` | `test_10_sbistc_integration` | SBISTC support | SBISTC integration 검증 | 미측정 |
| `extended` | `test_40_rse_fw_encryption` | encrypted firmware image | RSE firmware encryption 검증 | 미측정 |
| `extended` | `test_50_trusted_services` | trusted services image/runtime | trusted services 검증 | 미측정 |
| `extended` | `test_50_cryptographic_extension` | crypto extension support | crypto extension 검증 | 미측정 |
| `extended` | `test_60_cpu_frequency` | cpufreq support | CPU frequency 기능 검증 | 미측정 |
| `extended` | `test_60_cpuidle_cstates` | cpuidle support | CPU idle state 기능 검증 | 미측정 |
| `extended` | `test_99_uefi_secure_boot` | UEFI secure boot image | UEFI secure boot 검증 | 미측정 |
| `extended` | `test_100_fwu` | FWU/capsule image | firmware update flow 검증 | 미측정 |
| `extended` | `tftf` | TFTF payload | Trusted Firmware tests 검증 | 미측정 |
| `extended` | `tbb` | TBB payload | Trusted Board Boot 검증 | 미측정 |
| `extended` | `qbox-parity` | QBox validation artifacts | FVP/QBox parity checks | 미측정 |
| `stress` | `scmi_reboot_loop` | `test_scmi_reboot` 기반 | reboot 반복 loop | 미측정 |
| `stress` | `scmi_poweroff_loop` | `test_scmi_poweroff` 기반 | poweroff 반복 loop | 미측정 |
| `stress` | `warm_reset_loop` | warm reset support | warm reset 반복 | 미측정 |
| `stress` | `pfdi_repeat` | PFDI support | PFDI 반복 | 미측정 |
| `stress` | `si_pfdi_stress_5x` | Safety Island PFDI | SI PFDI 5회 반복 | 미측정 |
| `stress` | `hipc_payload_loop` | HIPC support | HIPC payload 반복 | 미측정 |
| `stress` | `cpu_frequency_long` | cpufreq support | CPU frequency 장시간 반복 | 미측정 |
| `stress` | `cpu_idle_long` | cpuidle support | CPU idle 장시간 반복 | 미측정 |
| `stress` | `boot_soak` | Apollo validation | boot soak 반복 | 미측정 |

## Artifacts

| Artifact | 용도 |
| --- | --- |
| `summary.json` | 최종 PASS/FAIL/BLOCKED 및 stage별 결과 |
| `commands.jsonl` | stage별 command, status, duration, artifact path |
| `manifest.json` | active build/test configuration snapshot |
| `preflight.json` | runtime prerequisite check 결과 |
| `fvp/result.json` | basic boot domain/marker/result |
| `fvp/summary.txt` | 사람이 읽는 basic boot 요약 |
| `oeqa/<kind>/bitbake.stdout.log` | BitBake/OEQA stdout |
| `oeqa/<kind>/bitbake.stderr.log` | BitBake/OEQA stderr |
| `oeqa/<kind>/results/testresults.json` | OEQA 개별 test status/duration |
