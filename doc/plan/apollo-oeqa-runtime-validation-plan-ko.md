# Apollo OEQA 런타임 검증 이관 및 실행 계획

## 1. 목적과 완료 기준

이 문서는 `arm-zena-css/documentation/design/validation.rst`에 정의된
RD-Aspen 런타임 통합 검증을 Apollo 제품 레이어로 이관하기 위한 사전
분석과 구현 계획이다. 대상 제품은 `apollo-fvp`와 `apollo-qvp`이며, 두
machine 모두 이번 단계에서는 Arm FVP를 OEQA controller로 실행한다.
`apollo-qvp`의 실제 QBox controller는 후속 확장 지점만 남기고 이번 범위에
포함하지 않는다.

완료 기준은 다음과 같다.

1. 가이드의 비가상화 런타임 동작 100개가
   `hsoc-stack/yocto/meta-hsoc-auto-solutions/lib/oeqa/runtime/cases/`
   아래 Apollo 소유 테스트로 존재한다.
2. 모든 boot 테스트 모듈은 `test_00_`으로 시작하고, RSE/SI CL0/SI
   CL1/TF-A/U-Boot/Linux/power/기타 기능은 각각 `10/20/30/40/50/60/70/80`
   대역을 따른다.
3. 각 기능 테스트는 boot 또는 앞선 기능 테스트를 명시적인
   `OETestDepends`로 참조한다.
4. `apollo-fvp`와 `apollo-qvp` 모두 `HSOCOEFVPTarget`를 사용하며,
   machine별 최종 `TEST_SUITES`가 Apollo 레이어의 suite로 해석된다.
5. `scripts/validation/`의 선언형 설정으로 suite와 case 별칭을 관리한다.
6. `run_validation.sh`가 선택된 OEQA 테스트를 실행하고 진행 상황, 통합
   로그, JSON/텍스트 요약 및 Markdown 상세 보고서를 남긴다.
7. 정적 검사, BitBake parse 검사와 소수의 실제 FVP OEQA smoke test로
   구현을 검증한다.

## 2. 범위

### 2.1 포함

- `validation.rst`의 비가상화 런타임 테스트 100개
- 현재 Apollo 제품 고유 UKI/dm-verity/writable mount boot 검증
- 현재 Apollo suite에 이미 포함된 RSE safety boot marker
- `apollo-fvp`, `apollo-qvp`의 FVP OEQA controller와 suite 정책
- suite/case 선택, 임시 BitBake `-R` 설정, 진행 표시 및 결과 보고
- 후속 QBox controller가 같은 machine/profile 표면을 사용할 수 있는
  명시적 controller 필드

### 2.2 제외

- Xen Dom0/DomU, Xen guest reboot/shutdown 등 가이드의 virtualization
  절 전체
- 실제 `HSOCOEQBoxTarget` 구현과 QBox에서의 OEQA 실행
- pinned 외부 레이어인 Poky, meta-arm, arm-zena-css 및
  sw-ref-stack 원본 수정
- 가이드와 직접 관계없는 펌웨어 업데이트, UEFI secure boot, warm reset
  테스트의 재분류

## 3. 현재 구조 사전 분석

### 3.1 활성 Yocto 설정

분석 기준은 다음 활성 파일이다.

- `build/conf/local.conf`
  - `MACHINE ??= "apollo-qvp"`
  - `RD_ASPEN_VARIANT = "cfg2"`
  - `PC_CPUS_COUNT_DEFAULT = "4"`
  - `TMPDIR = "${TOPDIR}/tmp_baremetal"`
  - `IMAGE_CLASSES += "testimage"`
  - `DISTRO_FEATURES:append = " demos"`
- `build/conf/bblayers.conf`
  - arm-zena-css, meta-hsoc, meta-arm, Poky, sw-ref-stack가 모두 포함됨
- `build/conf/templateconf.cfg`
  - Apollo QVP template를 선택함
- `yocto_build.sh`
  - 기본 빌드는 `nexios-bsp-initramfs`와 `nexios-image`를 만들지만
    `-c testimage`를 자동 호출하지 않음

실측 parse 결과는 다음과 같다.

| 항목 | `apollo-fvp` | `apollo-qvp` |
|---|---|---|
| `TEST_TARGET` | `HSOCOEFVPTarget` | `OEFVPTarget` |
| `FVP_EXE` | `FVP_Zena_CSS_Cfg2` | `FVP_Zena_CSS_Cfg2` |
| `TESTIMAGE_AUTO` | `0` | `0` |
| suite 정책 | Nexios 전용 11개 모듈 | demos 전용 25개 모듈 |
| `TEST_FVP_DEVICES` | rtc/watchdog/networking/virtiorng | 앞 항목 + cpu_hotplug |

원인은 `auto-ad-nexios.conf`의 제품 override가
`apollo-fvp:auto-ad-nexios`에만 있고 `apollo-qvp`에는 없기 때문이다.
`apollo-qvp.conf`도 RD-Aspen FVP machine 설정을 상속하므로 FVP 실행 자체는
가능하지만, 제품 controller와 suite 정책은 적용되지 않는다.

### 3.2 OEQA controller 경로

현재 동작 흐름은 다음과 같다.

```text
MACHINE/DISTRO metadata
  -> nexios-image.testdata.json 및 deploy .fvpconf
  -> bitbake nexios-image -c testimage
  -> TEST_SUITES module/class/method 선별
  -> TEST_TARGET 동적 controller 로드
  -> HSOCOEFVPTarget
  -> FVP writable flash 초기화
  -> lazy OFF -> ON -> LINUX 전이
  -> console pexpect 및 SSH/target.run 검증
  -> OEQA JSON, console log, target artifact 기록
```

`HSOCOEFVPTarget`는 Nexios A/B flash와 RSE NVM을 매 실행 전 writable
사본으로 재설정하고, terminal status query 응답 및 login prompt 보정을
제공한다. 이 동작은 두 Apollo machine에 공통으로 필요하다.

### 3.3 현재 테스트 소유권 문제

가이드 테스트는 네 곳에 흩어져 있다.

| 원본 | 역할 |
|---|---|
| `arm-zena-css/.../meta-zena-css-bsp/lib/oeqa/runtime/cases` | Aspen boot, RSE, secure partition, systemd-boot, SI diagnostics, DSU, CPU topology |
| `layers/meta-arm/meta-arm/lib/oeqa/runtime/cases` | FVP boot/device와 Trusted Services 공통 구현 |
| `layers/poky/meta/lib/oeqa/runtime/cases` | Ping/SSH 공통 구현 |
| `sw-ref-stack/.../meta-arm-auto-solutions/lib/oeqa/runtime/cases` | PFDI, RAS, SI, HIPC, crypto, power, MBPP, SMCF |

현재 hSOC 제품 레이어에는
`test_01_auto_ad_nexios_uki_boot.py` 하나만 있다. 이 상태에서는 원본
레이어의 파일명과 dependency에 Apollo suite가 결합되고, upstream의
선택 정책 변경이 Apollo 검증 범위를 암묵적으로 바꿀 수 있다. 따라서
테스트 구현은 hSOC 레이어로 복사하고, 공통 OEQA API와 필요한 utility만
원본 레이어에서 import한다.

### 3.4 확인된 원본 결함과 이관 원칙

단순 복사로는 가이드 계약을 충족하지 못하는 항목이 있다.

1. TF-A CPU 수 테스트가 실제로는 Linux의 `smp:` 로그를 default console에서
   검사한다. Apollo 이관본은 TF-A console의 CPU bring-up marker를 사용한다.
2. PFDI/SBISTC 문서는 non-critical FMU fault를 요구하지만 원본은 critical
   fault를 기대한다. 가이드 표현과 실제 Apollo 로그를 함께 수용하되,
   어떤 marker가 검출됐는지 보고한다.
3. RAS journal 테스트는 가이드가 요구한
   `rasdaemon: ras:arm_event event enabled`의 양성 검사를 하지 않는다.
   Apollo 이관본은 이를 명시적으로 검사한다.
4. SI PFDI와 SI monitor는 4개 CL1 CPU를 하드코딩한다. Apollo cfg2의 현재
   4 CPU 기본값은 유지하되 metadata 값으로 구성한다.
5. HIPC의 TCP PC→CL1 테스트는 Linux boot dependency가 빠져 있다. 이관 시
   보강한다.
6. CPU frequency의 invalid governor 테스트는 잘못된 쓰기가 성공해도
   실패하지 않을 수 있다. 성공 경로를 명시적으로 실패 처리한다.
7. MBPP는 16 CPU에서만 실행 가능하다. 테스트는 이관하되 현재 4 CPU
   machine에서는 명시적으로 skip되도록 유지한다.
8. crypto 성능 테스트는 writable 작업 경로와 FVP crypto plugin을 필요로
   한다. `/tmp` 작업 디렉터리를 사용하고 QBox profile에서는 후속
   capability gate 대상으로 기록한다.

## 4. 테스트 번호와 100개 동작 이관표

번호는 파일명 prefix다. 같은 성격의 테스트는 같은 번호의 모듈 안에서
method 이름으로 구분하고, 성격이 바뀔 때 해당 대역 안에서 1씩 증가시킨다.
Boot는 처리 도메인과 무관하게 모두 `00`을 사용한다.

### 4.1 Boot root tests

| 대상 모듈 | 원본과 포함 동작 | 개수 | dependency |
|---|---|---:|---|
| `test_00_fvp_boot.py` | meta-arm `fvp_boot`: Linux boot 및 전체 console 공통 error scan | 1 | 없음 |
| `test_00_rse_boot.py` | `test_00_rse`: normal boot, measured boot | 2 | normal -> measured |
| `test_00_si_cl0_boot.py` | `test_00_aspen_boot.test_scp` | 1 | 없음 |
| `test_00_si_cl1_boot.py` | Aspen SI CL1 marker, sw-ref SI CL1 secondary cores | 2 | SI CL0 boot |
| `test_00_tfa_secure_partition_boot.py` | OP-TEE/SP load와 Normal world handoff | 1 | RSE boot |
| `test_00_uboot_boot.py` | U-Boot banner와 autoboot | 1 | RSE boot |
| `test_00_systemd_boot.py` | systemd-boot `Boot in` marker | 1 | U-Boot boot |
| `test_00_linux_boot.py` | Linux transition/login 기반 | boot root | systemd/FVP boot |
| `test_00_safety_boot.py` | RSE LBIST/MBIST marker | Apollo 추가 | RSE boot |
| `test_00_apollo_uki_boot.py` | UKI A/B, dm-verity, writable mount | Apollo 추가 | Linux boot |

가이드의 boot 동작은 후반부 SI CL1 secondary-core boot를 포함해 9개다.
Linux boot root는 Ping/SSH 및 모든 Linux
기능의 공통 dependency로 유지한다.

### 4.2 RSE, Safety Island, TF-A, U-Boot

| 대역/대상 모듈 | 포함 동작 | 가이드 개수 | boot/선행 dependency |
|---|---|---:|---|
| `test_10_rse_platform.py` | 현재 가이드에는 boot/power 외 독립 RSE 기능 없음; 후속 예약 | 0 | RSE boot |
| `test_20_si_cl0_diagnostics.py` | SSU, FMU | 2 | SI CL0 boot, SSU -> FMU |
| `test_21_si_cl0_pfdi.py` | AP monitor start/error, PFDI-SBISTC propagation, SI PFDI monitor | 4 | SI CL0 + Linux boot |
| `test_22_si_cl0_smcf.py` | client start, execute, 3회 반복, sensor monitor | 4 | SI CL0 boot, 순차 |
| `test_30_si_cl1_pfdi.py` | cluster status, all, block/parameter/range/CPU/count/result/monitor/error/repeat/stress/info | 16 | SI CL1 boot, cluster status |
| `test_31_si_cl1_hipc.py` | DT, stack, shared memory, ICMP, 4방향 UDP/TCP, boundary, multistream | 10 | SI CL1 + Linux boot, 순차 |
| `test_40_tfa_cpu_topology.py` | TF-A CPU 수 | 1 | secure-partition boot |
| `test_41_tfa_ras.py` | list, invalid, usage, correctable/deferred/repeat/fatal/mixed, rasdaemon | 9 | TF-A + Linux boot, CLI prerequisite |
| `test_50_uboot_platform.py` | 현재 가이드에는 boot 외 독립 U-Boot 기능 없음; 후속 예약 | 0 | U-Boot boot |

### 4.3 Primary Compute Linux

| 대상 모듈 | 포함 동작 | 개수 | boot/선행 dependency |
|---|---|---:|---|
| `test_60_linux_connectivity.py` | Ping, SSH | 2 | Linux boot, Ping -> SSH |
| `test_61_linux_dsu.py` | DSU cache/PMU | 1 | SSH |
| `test_62_linux_cpu_topology.py` | DT와 `nproc` CPU 수 | 1 | SSH |
| `test_63_linux_fvp_devices.py` | networking, RTC, hotplug, RNG, watchdog | 5 | SSH |
| `test_64_linux_pfdi.py` | service, app, CLI, forced error | 4 | Linux boot, service |
| `test_65_linux_crypto.py` | Arm crypto extension 성능 | 1 | Linux boot |

Linux 영역 합계는 14개다.

### 4.4 Power

| 대상 모듈 | 포함 동작 | 개수 | boot/선행 dependency |
|---|---|---:|---|
| `test_70_power_scmi.py` | RSE SCMI poweroff, reboot | Apollo 추가 | RSE + Linux boot |
| `test_71_power_cpuidle.py` | prerequisite, name, default, disable, timing, governors, switch, invalid | 8 | Linux boot, 순차 |
| `test_72_power_cpufreq.py` | topology, default, set, SCMI, current, affected, invalid, min/max 갱신/오류 | 10 | Linux boot, prerequisite |
| `test_73_power_mbpp.py` | script, help/list, initial, idempotent, case, invalid, cycle, offline, restore | 9 | Linux boot, 16 CPU gate |

가이드 power 영역 합계는 27개다.

### 4.5 기타

| 대상 모듈 | 포함 동작 | 개수 | boot/선행 dependency |
|---|---|---:|---|
| `test_80_trusted_services.py` | PSA Crypto, Protected Storage, Internal Trusted Storage, Initial Attestation | 4 | SSH, package gate |

위 표의 가이드 동작 수는 boot 9, SI CL0 10, SI CL1 26, TF-A 10,
Linux 14, power 27, 기타 4로 최종 100개다. Linux 14개에는 FVP device
5개가 포함된다. Apollo 고유 boot와 RSE power는 이 100개 외 기존 제품
회귀 검증으로 유지한다.

## 5. controller 및 Yocto suite 설계

### 5.1 공통 FVP controller 정책

`auto-ad-nexios.conf`에 공통 suite 문자열을 한 번 정의하고 두 machine에
명시적으로 할당한다.

```bitbake
HSOC_APOLLO_FVP_TEST_SUITES = "..."

TEST_SUITES:apollo-fvp:auto-ad-nexios = "${HSOC_APOLLO_FVP_TEST_SUITES}"
TEST_SUITES:apollo-qvp:auto-ad-nexios = "${HSOC_APOLLO_FVP_TEST_SUITES}"
TEST_TARGET:apollo-fvp:auto-ad-nexios = "HSOCOEFVPTarget"
TEST_TARGET:apollo-qvp:auto-ad-nexios = "HSOCOEFVPTarget"
```

`TEST_FVP_DEVICES`와 `TESTIMAGE_UPDATE_VARS`도 두 machine에 동일하게
설정한다. `apollo-qvp` override를 별도로 유지하는 이유는 후속 QBox
확장 때 이 한 줄만 `HSOCOEQBoxTarget`로 교체할 수 있게 하기 위해서다.

### 5.2 suite 선택

Yocto의 기본 suite에는 이관된 모든 모듈을 포함한다. package, variant,
CPU 수가 맞지 않는 테스트는 OEQA skip으로 표현한다. `demos` feature의
직접 할당보다 machine+distro override가 더 구체적이므로 최종 suite가
안정적으로 Apollo 목록을 선택한다.

개별 실행은 환경 변수로 `TEST_SUITES`를 덮어쓰지 않는다. 매 실행마다
다음 내용을 가진 임시 `-R` conf를 생성한다.

```bitbake
MACHINE = "apollo-qvp"
TEST_SUITES = "<ordered selectors>"
TEST_SUITES:apollo-qvp:auto-ad-nexios = "<ordered selectors>"
TEST_TARGET = "HSOCOEFVPTarget"
TEST_TARGET:apollo-qvp:auto-ad-nexios = "HSOCOEFVPTarget"
```

`build/conf/`는 수정하지 않는다. 생성 위치는
`build/tests/validation-<machine>-<UTC>/conf/`로 제한한다.

## 6. `scripts/validation/` 설정과 CLI

### 6.1 파일 구성

```text
run_validation.sh
scripts/validation/
  run_validation.py
  profiles.json
  suites.json
tests/
  test_run_validation.py
```

- `profiles.json`: machine별 controller, image, distro, 기본 suite
- `suites.json`: 사용자 suite/case 별칭, OEQA selector 및 dependency
- `run_validation.py`: 설정 검증, dependency 확장, 임시 conf, subprocess
  streaming, 결과 수집과 보고서 생성
- root shell: 저장소 root를 결정한 뒤 Python entrypoint 실행

### 6.2 사용자 표면

```bash
./run_validation.sh \
  --machine apollo-qvp \
  --test-suite boot \
  --test-case rse-boot

./run_validation.sh --test-suite boot
./run_validation.sh --list
./run_validation.sh --dry-run --test-suite linux --test-case ssh
```

기본 machine은 활성 개발 대상인 `apollo-qvp`다. `--test-case`는
`--test-suite` 안에 등록된 별칭만 허용하고, 선택된 case의 dependency를
앞에 추가한다. raw OEQA selector가 필요한 경우 별도 `--oeqa-selector`
옵션으로 `module[.Class[.method]]` 문법만 허용한다.

### 6.3 미리 정의할 suite

| suite | case 예 | 선택 정책 |
|---|---|---|
| `boot` | `rse-boot`, `si-cl0-boot`, `si-cl1-boot`, `tfa-boot`, `uboot-boot`, `linux-boot`, `apollo-uki` | 해당 boot root와 앞선 boot |
| `rse` | 후속 RSE 기능 | RSE boot 선행 |
| `safety-island-cl0` | `diagnostics`, `pfdi`, `smcf` | SI CL0 및 필요 시 Linux boot |
| `safety-island-cl1` | `pfdi`, `hipc` | SI CL1 및 필요 시 Linux boot |
| `tf-a` | `cpu-topology`, `ras` | TF-A/secure partition boot |
| `u-boot` | 후속 U-Boot 기능 | U-Boot boot 선행 |
| `linux` | `connectivity`, `dsu`, `cpu-topology`, `fvp-devices`, `pfdi`, `crypto` | Linux boot와 SSH |
| `power` | `scmi`, `cpuidle`, `cpufreq`, `mbpp` | RSE/Linux boot |
| `trusted-services` | `psa-api` | Linux boot와 SSH |
| `all` | 없음 | virtualization 제외 전체 |

## 7. 진행 표시와 evidence 계약

실행 디렉터리는 다음과 같다.

```text
build/tests/validation-<machine>-<UTC>/
  runner.log
  commands.jsonl
  manifest.json
  conf/oeqa-selected.conf
  logs/parse.stdout.log
  logs/testimage.stdout.log
  oeqa/logs/
  oeqa/results/
  oeqa/artifacts/
  summary.json
  summary.txt
  report.md
```

표준 출력과 `runner.log`에는 timestamp가 포함된 `START`, `PROGRESS`,
`DONE` 이벤트를 실시간으로 출력한다. 종료 시 다음 네 줄을 반드시
표시한다.

```text
RESULT: PASS|FAIL|BLOCKED
SUMMARY: <summary.json>
REPORT: <report.md>
LOG: <runner.log>
```

`report.md`는 선택 machine/suite/case, 최종 selector, 정확한 명령,
단계별 exit code와 소요 시간, OEQA pass/fail/skip, 로그 및 artifact,
실패 원인과 알려진 portability gap을 기록한다.

## 8. 구현 순서

1. 이 계획 문서를 먼저 저장하고 참조 경로와 현재 parse 값을 재검증한다.
2. 원본 테스트를 hSOC 레이어로 기계적으로 복사하고 대역별 파일명으로
   분할한다.
3. module/class/method dependency를 hSOC 이름으로 바꾸고 모든 기능
   테스트에 boot 또는 선행 dependency를 추가한다.
4. 3.4절의 가이드 불일치와 Apollo portability 항목을 수정한다.
5. 기존 Nexios boot 테스트를 `test_00_apollo_uki_boot.py`로 바꾸고
   dependency를 갱신한다.
6. `auto-ad-nexios.conf`에 두 machine 공통 suite/controller 정책을
   적용한다.
7. `scripts/validation/` 설정, Python runner, root shell wrapper와
   단위 테스트를 구현한다.
8. 좁은 검사부터 parse와 runtime으로 확장한다.

## 9. 검증 계획

### 9.1 정적 및 단위 검사

```bash
python3 -m py_compile \
  hsoc-stack/yocto/meta-hsoc-auto-solutions/lib/oeqa/runtime/cases/*.py \
  scripts/validation/*.py
shellcheck run_validation.sh
pytest -q tests/test_run_validation.py
git -C hsoc-stack/yocto/meta-hsoc-auto-solutions diff --check
git diff --check
```

추가로 모든 runtime Python 파일을 AST로 읽어 다음을 검사한다.

- 파일명 prefix가 허용 대역과 일치
- virtualization selector가 없음
- 기능 테스트 method마다 `OETestDepends`가 있음
- dependency selector가 실제 이관 모듈에 존재
- 가이드 동작 inventory가 정확히 100개

### 9.2 BitBake parse

```bash
source layers/poky/oe-init-build-env build
MACHINE=apollo-fvp bitbake-getvar -r nexios-image TEST_TARGET TEST_SUITES
MACHINE=apollo-qvp bitbake-getvar -r nexios-image TEST_TARGET TEST_SUITES
./run_validation.sh --machine apollo-qvp \
  --test-suite boot --test-case rse-boot --parse-only
```

임시 `-R` conf 사용 후 최종 `TEST_SUITES`가 dependency를 포함한 요청
selector와 정확히 같아야 한다.

### 9.3 실제 smoke

빌드 artifact와 FVP license가 준비된 경우 소요 시간이 짧고 상태 변경이
적은 항목부터 수행한다.

```bash
./run_validation.sh --machine apollo-qvp \
  --test-suite boot --test-case rse-boot
./run_validation.sh --machine apollo-qvp \
  --test-suite boot --test-case secure-partition-boot
./run_validation.sh --machine apollo-fvp \
  --test-suite linux --test-case connectivity
```

전체 100개 검증은 smoke 완료 후 별도 장시간 qualification으로 남긴다.
Smoke가 artifact/license/host resource로 막히면 결과를 `BLOCKED`로
분류하고 정적/parse 성공을 runtime 성공으로 표현하지 않는다.

## 10. 커밋과 배포 경계

변경은 owning repository 기준으로 커밋한다.

1. `hsoc-stack/yocto/meta-hsoc-auto-solutions`
   - Apollo 테스트 이관
   - controller/suite metadata
2. top-level repository
   - submodule pointer
   - `run_validation.sh`, `scripts/validation/`, 단위 테스트
   - 이 계획과 분석 문서

각 commit은 Conventional Commits, `git commit -s`, 50자 이내 제목과
72자 이내 본문을 사용한다. push 전에 소유 remote audit 및 dry-run을
수행하고, push 뒤 각 remote ref가 local commit과 같은지 확인한다.
