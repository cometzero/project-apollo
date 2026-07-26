# Apollo OEQA runtime validation 구현 및 검증 보고서

## 1. 요약

`arm-zena-css/documentation/design/validation.rst`의 runtime validation을
기준으로 virtualization 항목을 제외한 100개 동작을
`meta-hsoc-auto-solutions` 소유의 OEQA runtime test로 이관했다.

Apollo 제품에 이미 존재하던 Linux login, Safety LBIST/MBIST, UKI 및
SCMI 전원 테스트 8개도 동일한 번호 체계로 정리했다. 최종 구성은
28개 모듈과 108개 test method이다.

`apollo-fvp`와 `apollo-qvp`는 현재 모두
`HSOCOEFVPTarget`을 통해 `FVP_Zena_CSS_Cfg2`에서 실행한다.
`apollo-qvp`의 QBox controller 전환은 별도 controller를 추가하고
machine별 `TEST_TARGET`만 교체할 수 있도록 override를 분리했다.

## 2. 구현 범위

### 2.1 가이드 테스트 수

| 영역 | 모듈 번호 | 가이드 테스트 수 |
|---|---:|---:|
| Boot | `test_00_*` | 9 |
| Safety Island CL0 | `test_20_*`~`test_22_*` | 10 |
| Safety Island CL1 | `test_30_*`~`test_31_*` | 26 |
| Primary Compute TF-A | `test_40_*`~`test_41_*` | 10 |
| Primary Compute Linux | `test_60_*`~`test_65_*` | 14 |
| Power | `test_71_*`~`test_73_*` | 27 |
| Trusted Services와 기타 | `test_80_*` | 4 |
| 합계 |  | 100 |

가이드의 RSE normal/measured boot는 boot이므로 `test_00_rse_boot`에
배치했다. RSE SCMI poweroff/reboot는 power 기능이므로 Apollo 기존
테스트인 `test_70_power_scmi`에 배치했다. 가이드에 U-Boot 기능
테스트가 별도로 없으므로 `test_50_*` 빈 모듈은 만들지 않았다.

### 2.2 Apollo 추가 테스트

| 모듈 | 테스트 수 | 내용 |
|---|---:|---|
| `test_00_linux_boot` | 1 | Linux login과 OEQA SSH 준비 |
| `test_00_safety_boot` | 2 | RSE LBIST와 MBIST |
| `test_00_apollo_uki_boot` | 3 | UKI boot, dm-verity, writable mount |
| `test_70_power_scmi` | 2 | SCMI poweroff와 reboot |
| 합계 | 8 |  |

### 2.3 이관한 모듈

Boot:

- `test_00_fvp_boot`
- `test_00_rse_boot`
- `test_00_si_cl0_boot`
- `test_00_si_cl1_boot`
- `test_00_tfa_secure_partition_boot`
- `test_00_uboot_boot`
- `test_00_systemd_boot`
- `test_00_linux_boot`
- `test_00_safety_boot`
- `test_00_apollo_uki_boot`

기능:

- `test_20_si_cl0_diagnostics`
- `test_21_si_cl0_pfdi`
- `test_22_si_cl0_smcf`
- `test_30_si_cl1_pfdi`
- `test_31_si_cl1_hipc`
- `test_40_tfa_cpu_topology`
- `test_41_tfa_ras`
- `test_60_linux_connectivity`
- `test_61_linux_dsu`
- `test_62_linux_cpu_topology`
- `test_63_linux_fvp_devices`
- `test_64_linux_pfdi`
- `test_65_linux_crypto`
- `test_70_power_scmi`
- `test_71_power_cpuidle`
- `test_72_power_cpufreq`
- `test_73_power_mbpp`
- `test_80_trusted_services`

각 기능 test method는 boot 또는 선행 기능을 가리키는
`OETestDepends`를 명시한다. `scripts/validation/suites.json`의 suite와
case 선택도 dependency가 속한 모듈을 함께 선택한다.

## 3. 원본 대비 보정

단순 복사로 유지되던 false positive와 Apollo 이식성 문제를 다음과
같이 보정했다.

- TF-A CPU topology는 Linux console이 아니라 TF-A console의
  secondary CPU handoff를 검사한다.
- RAS journal은
  `rasdaemon: ras:arm_event event enabled`를 긍정적으로 확인한다.
- PFDI SBISTC는 문서와 기존 구현 사이 severity 차이를 기록하고
  Critical 및 Non-critical 표기를 모두 수용한다.
- Safety Island CL1 CPU 수는 `SI_CL1_CPUS_COUNT`에서 읽으며 기본값은
  4이다.
- HIPC의 PC-to-CL1 TCP 테스트에도 Linux boot dependency를 추가했다.
- crypto 테스트 작업 경로는 dm-verity root가 아닌
  `/tmp/apollo-oeqa-crypto`를 사용한다.
- 잘못된 cpufreq governor write가 성공하면 테스트를 실패시킨다.
- 잘못된 cpufreq min/max write는 command 실패와 상태 검증을 분리한다.
  write가 성공한 경우에도 `min <= max` invariant를 확인하며 원래 값을
  `finally`에서 복구한다.

## 4. Yocto controller와 suite 구성

`conf/distro/auto-ad-nexios.conf`에
`HSOC_APOLLO_FVP_TEST_SUITES`를 정의하고 다음 값을 machine별로
명시했다.

| 변수 | `apollo-fvp` | `apollo-qvp` |
|---|---|---|
| `TEST_TARGET` | `HSOCOEFVPTarget` | `HSOCOEFVPTarget` |
| `TEST_SUITES` | 공통 28개 모듈 | 공통 28개 모듈 |
| `TEST_FVP_DEVICES` | RTC, watchdog, network, RNG, CPU hotplug | 동일 |
| `SI_CL1_CPUS_COUNT` | 4 | 4 |

두 machine override를 합치지 않았기 때문에 추후 QBox controller가
준비되면 `apollo-qvp`의 target만 별도로 변경할 수 있다. 현재
`apollo-qvp`라는 machine 이름은 OEQA backend가 QBox라는 뜻이 아니며,
이번 단계에서는 명시적으로 FVP를 사용한다.

## 5. 실행 도구

루트의 `run_validation.sh`가
`scripts/validation/run_validation.py`를 실행한다. 선택 정책은
`profiles.json`과 `suites.json`에 선언했다.

예:

```bash
./run_validation.sh \
  --machine apollo-qvp \
  --test-suite boot \
  --test-case rse-boot

./run_validation.sh --test-suite boot

./run_validation.sh \
  --machine apollo-fvp \
  --oeqa-selector test_00_rse_boot.RseBootTest.test_normal_boot
```

지원 기능:

- machine, suite, case 또는 OEQA raw selector 선택
- `--list`, `--dry-run`, `--parse-only`
- 실행별 임시 `-R` BitBake 설정 생성
- 최종 `TEST_SUITES`와 `TEST_TARGET` parse 검증
- `START`, `PROGRESS`, `DONE` 실시간 출력
- OEQA JSON 결과의 pass/fail/skip 집계
- 쉘용 `summary.txt`와 `summary.json`
- 상세 `report.md`
- command별 로그, FVP/UART 로그와 OEQA artifact 보존

`build/conf`는 수정하지 않는다. 모든 결과는
`build/tests/validation-<machine>-<timestamp>/` 또는 사용자가 지정한
`build/tests` 하위 디렉터리에 저장한다.

## 6. 검증 결과

### 6.1 BitBake parse

다음 두 결과에서 선택된 suite와 controller가 정확히 일치했다.

- `build/tests/validation-apollo-fvp-parse-fixed/`
  - `TEST_SUITES=test_00_rse_boot`
  - `TEST_TARGET=HSOCOEFVPTarget`
- `build/tests/validation-apollo-qvp-parse-final/`
  - `TEST_SUITES=test_00_rse_boot`
  - `TEST_TARGET=HSOCOEFVPTarget`

`MACHINE=<machine>`을 BitBake 환경에 명시하지 않고 `-R` 파일에서만
설정하면 이미 선택된 machine configuration을 바꾸지 못한다는 점을
실제 실패로 확인했다. runner는 이를 수정하여 모든 parse 및
`testimage` 명령에 `MACHINE=<machine>`을 명시한다.

### 6.2 실제 FVP OEQA smoke

`apollo-qvp` image를 `HSOCOEFVPTarget`으로 FVP에서 실행했다.

| 선택 | 결과 | OEQA 결과 |
|---|---|---:|
| `boot/rse-boot` | PASS | 2 pass, 0 fail, 0 skip |
| `boot/si-cl0-boot` | PASS | 1 pass, 0 fail, 0 skip |
| 합계 | PASS | 3 pass, 0 fail, 0 skip |

상세 증거:

- `build/tests/validation-apollo-qvp-rse-smoke/report.md`
- `build/tests/validation-apollo-qvp-rse-smoke/summary.json`
- `build/tests/validation-apollo-qvp-rse-smoke/runner.log`
- `build/tests/validation-apollo-qvp-si-cl0-smoke/report.md`
- `build/tests/validation-apollo-qvp-si-cl0-smoke/summary.json`
- `build/tests/validation-apollo-qvp-si-cl0-smoke/runner.log`

각 실행 디렉터리에는 `testresults.json`, FVP log, default/RSE/SCP/TF-A/
Safety Island CL1 UART log가 함께 저장됐다.

### 6.3 정적 및 회귀 검증

```bash
python3 -m py_compile \
  scripts/validation/*.py \
  hsoc-stack/yocto/meta-hsoc-auto-solutions/lib/oeqa/runtime/cases/*.py

shellcheck run_validation.sh

python3 -m pytest -q \
  tests/test_apollo_oeqa_inventory.py \
  tests/test_run_validation.py \
  tests/test_auto_ad_nexios_oeqa_boot.py \
  tests/test_run_test_suite_plan.py \
  tests/test_run_test_qbox_lanes.py \
  tests/test_run_test_conf.py \
  tests/test_run_test_manifest.py
```

결과:

- 28개 Apollo OEQA 모듈 import 성공
- pytest 45개 통과
- shellcheck 통과
- top-level, `meta-hsoc-auto-solutions`, `hsoc-stack/tests`의
  `git diff --check` 통과

## 7. 제한과 후속 검증

- 100개 가이드 테스트를 모두 소스와 dependency 관점에서 검증했지만
  이번 smoke에서는 3개만 실제 실행했다.
- 4 CPU 기본 구성에서는 16 CPU 전용 MBPP 테스트 9개가 skip된다.
- HIPC, PFDI, RAS injection, crypto performance와 power 상태 변경은
  각각 필요한 firmware 옵션, target package 및 FVP plugin이 갖춰진
  전체 suite 실행으로 추가 검증해야 한다.
- `apollo-fvp`는 parse를 검증했고 실제 smoke는 동일 controller를
  사용하는 `apollo-qvp` image에서 수행했다.
- QBox runtime controller와 lifecycle 구현은 이번 범위가 아니다.
  QBox 확장 시 `HSOCOEQBoxTarget`과 같은 별도 controller를 추가하고
  `apollo-qvp` override만 전환해야 한다.
