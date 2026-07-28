# QBox Apollo FVP Full-System 실행 가이드

> 2026-07-27: Apollo QVP는 이제 실제 CL0 SCP-firmware와 CL1 Zephyr를
> 항상 구성하는 단일 full-system 토폴로지만 지원한다. 아래에 남아 있는
> `--si-mode` 기반 절차와 `full-live-*` 경로는 전환 전 실험 기록이며 현재
> 실행 계약이 아니다. 현재 실행은
> `python3 scripts/run/run_qbox_apollo_fvp_full.py --timeout 600`을 사용한다.

생성일: 2026-06-03

상태: 구현 및 검증 완료

이 문서는 Apollo FVP local build 산출물을 사용해 QBox full-system
emulation을 실행하고, G0-G5 completion gate를 검증하는 절차를 설명한다.

## 빠른 요약

최종 완료를 다시 검증하려면 아래 순서로 실행한다.

```bash
./local_build.sh build
./local_build.sh qbox

python3 scripts/run/run_qbox_apollo_fvp_full.py \
  --si-mode live-cl0-cl1 \
  --skip-build \
  --timeout 2400 \
  --rootfs-bootargs-profile quiet-console \
  --post-login-probe \
  --out-dir build/qbox-apollo-fvp/full-live-cl0-cl1

python3 scripts/run/runfvp_log_boot.py \
  --machine apollo-fvp \
  --fvpconf build/local-apollo-fvp/deploy/apollo-fvp-local.fvpconf \
  --out-dir build/local-apollo-fvp/fvp-boot \
  --timeout 900 \
  --require all \
  --min-runtime 70 \
  --no-login

python3 scripts/analyze/compare_fvp_qbox_rse_logs.py \
  --fvp build/local-apollo-fvp/fvp-boot \
  --qbox build/qbox-apollo-fvp/full-live-cl0-cl1 \
  --output build/qbox-apollo-fvp/full-live-cl0-cl1/comparison.json

python3 scripts/test/validate_qbox_apollo_fvp_full_map.py \
  --check memory,irq,atu \
  --out build/qbox-apollo-fvp/full-live-cl0-cl1/map-comparison.json

python3 scripts/test/audit_qbox_apollo_fvp_full_coverage.py \
  --result-json build/qbox-apollo-fvp/full-live-cl0-cl1/result.json \
  --output build/qbox-apollo-fvp/full-live-cl0-cl1/coverage-audit.json

python3 scripts/test/verify_qbox_apollo_fvp_full_completion.py \
  --strict-final \
  --output build/qbox-apollo-fvp/full-live-cl0-cl1/final-verification.json
```

성공 조건은 마지막 command가 exit 0이고,
`final-verification.json`에 `completion_claim_allowed: true`가 기록되는
것이다.

`run_qbox_apollo_fvp_full.py`는 RSE-first firmware chain을 그대로 사용한다.
RSE 전체를 우회하는 full-system fast boot mode는 제공하지 않는다.
Apollo full-system boot는 AP flash와 host memory의 regular TLM 병목을
피하기 위해 range-limited flash DMI fast path를 기본으로 켠다. 이 경로는
스토리지 전체를 stub하지 않고 제한된 boot flash read 범위와 DMI 가능한
메모리 창만 빠르게 연결한다. CFI command-state, storage, UEFI variable,
FWU fidelity를 확인할 때만 `--no-range-limited-flash-dmi`로 끈다.

```bash
python3 scripts/run/run_qbox_apollo_fvp_full.py \
  --si-mode live-cl0-cl1 \
  --skip-build \
  --timeout 2400 \
  --post-login-probe \
  --out-dir build/qbox-apollo-fvp/full-live-cl0-cl1
```

RSE가 느린 구간은 실행 결과의 다음 필드에서 확인한다.

```text
build/qbox-apollo-fvp/<run>/result.json
  rse_boot_timing_profile.summary
  rse_boot_timing_profile.slowest_delta
  rse_boot_timing_profile.markers
```

`summary.txt`에도 같은 profile 요약이 기록된다.
느린 구간별 stub/fast-path 가능성은
`doc/qbox-rse-boot-slow-path-analysis-ko.md`에 정리되어 있으며, 저장된
run 결과는 다음처럼 재분석할 수 있다.

```bash
python3 scripts/analyze/analyze_qbox_rse_boot_timing.py --markdown \
  build/qbox-apollo-fvp/full-live-cl0-cl1/result.json
```

FVP 대비 상대 속도를 확인하려면 FVP도 같은 marker 방식으로 재실행한다.

```bash
python3 scripts/run/runfvp_log_boot.py \
  --machine apollo-fvp \
  --fvpconf build/local-apollo-fvp/deploy/apollo-fvp-local.fvpconf \
  --out-dir build/local-apollo-fvp/fvp-boot-timed-<run-id> \
  --timeout 120 \
  --min-runtime 0
```

2026-06-04 측정 기준으로 QBox full-system login은 FVP 대비 약 3.8배 느리고,
핵심 병목인 `rse_bl2_decrypted` -> `rse_bl2_validated` 구간은 약 100배
느리다. 상세 수치와 QEMU-side CC3XX backend 설계는
`doc/qbox-rse-boot-slow-path-analysis-ko.md`를 본다.

RSE BL1_2 validation 내부의 CC3XX HASH/PKA 비중을 같이 보려면 다음 옵션을
추가한다.

```bash
python3 scripts/run/run_qbox_apollo_fvp_full.py \
  --si-mode live-cl0-cl1 \
  --skip-build \
  --timeout 2400 \
  --rootfs-bootargs-profile quiet-console \
  --post-login-probe \
  --cc3xx-stats \
  --cc3xx-stats-interval 65536 \
  --out-dir build/qbox-apollo-fvp/full-live-cl0-cl1-cc3xx-stats
```

또는 tmux 화면 실행에서 `--cc3xx-stats --cc3xx-stats-interval 65536`을
붙인다. 결과의 `rse-cc3xx-stats.json`은
`scripts/analyze/analyze_qbox_rse_boot_timing.py`가 자동으로 읽는다.

RSE CC3XX polling read 비용만 분리해서 확인하려면 opt-in status-read fast
path를 추가한다. 이 옵션은 secure boot 검증을 skip하지 않고, side-effect 없는
ready/busy status read만 QEMU initiator에서 바로 반환한다.

```bash
python3 scripts/run/run_qbox_apollo_fvp_full.py \
  --si-mode live-cl0-cl1 \
  --skip-build \
  --timeout 2400 \
  --rootfs-bootargs-profile quiet-console \
  --post-login-probe \
  --cc3xx-stats \
  --cc3xx-stats-interval 65536 \
  --cc3xx-status-read-fastpath \
  --out-dir build/qbox-apollo-fvp/full-live-cl0-cl1-cc3xx-status-fastpath
```

`HOST_RGF_IRR`처럼 write/clear side effect와 연결된 register는 이 fast path
대상이 아니다. 실험 결과와 QEMU-side CC3XX backend 계획은
`doc/qbox-rse-boot-slow-path-analysis-ko.md`에 기록한다.

현재 더 효과적인 QBox-side 성능 옵션은 CC3XX local MMIO fast path이다. 이
옵션은 CC3XX register model과 DMA side effect는 유지하고, RSE CC3XX window
`0x50154000:0x2000`의 QEMU -> SystemC scheduler bridge만 우회한다.

```bash
python3 scripts/run/run_qbox_apollo_fvp_full.py \
  --si-mode live-cl0-cl1 \
  --skip-build \
  --timeout 2400 \
  --rootfs-bootargs-profile quiet-console \
  --post-login-probe \
  --cc3xx-stats \
  --cc3xx-stats-interval 65536 \
  --cc3xx-local-mmio-fastpath \
  --out-dir build/qbox-apollo-fvp/full-live-cl0-cl1-cc3xx-local-mmio
```

가장 빠른 debug iteration은 `--cc3xx-local-mmio-fastpath`와
`--cc3xx-status-read-fastpath`를 같이 켜는 것이다. 다만 status-read fast path는
CC3XX operation mix가 baseline과 달라질 수 있으므로, fidelity-oriented
comparison에는 local MMIO fast path만 사용한다.

RSE CC3XX를 QEMU-native backend로 실행하려면 `--cc3xx-qemu-native-backend`를
사용한다. 이 옵션은 기존 SystemC `cc3xx`와 동일한 `cc3xx_core`를 사용하지만,
RSE CPU의 CC3XX MMIO window를 QEMU `MemoryRegionOps` callback으로 처리한다.
default는 여전히 SystemC backend이며, qemu-native backend는 secure boot
검증을 skip하지 않는다. runner는 qemu-native 선택 시
`0x50154000:0x2000` direct MMIO fast path를 자동으로 켠다.

```bash
python3 scripts/run/run_qbox_apollo_fvp_full.py \
  --si-mode live-cl0-cl1 \
  --skip-build \
  --timeout 2400 \
  --rootfs-bootargs-profile quiet-console \
  --post-login-probe \
  --range-limited-flash-dmi \
  --cc3xx-stats \
  --cc3xx-stats-interval 65536 \
  --cc3xx-qemu-native-backend \
  --out-dir build/qbox-apollo-fvp/full-live-cl0-cl1-cc3xx-qemu-native
```

RSE 단독 timing 기준으로 qemu-native backend는 local-MMIO status fast path의
BL2 validation delta를 151.321초에서 133.339초로 줄였다. 같은 결과 bundle은
`build/qbox-apollo-fvp/cc3xx-qemu-native-20260605-001939/rse/`에 남아 있다.
full-system 검증 bundle은
`build/qbox-apollo-fvp/cc3xx-qemu-native-20260605-003557/full/`을 사용한다.
이 run은 `passed: true`, `blocker: none`, Linux login, post-login probe,
SI CL1 remoteproc/RPMsg, `ethsi1`, DSU PMU evidence를 남긴다. 역사적
direct-boot guardrail evidence는
`build/qbox-apollo-fvp/direct-guardrail-20260605-004025/`에서 pass로
확인했지만, 현재 G1/G2 contract에는 사용하지 않는다.

RSE boot time을 FVP에 가깝게 비교하는 기본 fast path는 file-backed SRAM
alias가 아니라 shared-memory SRAM DMI이다. 이 경로는 RSE runner에
`--rse-fast-boot-sram-dmi`를 전달하고
`QBOX_RDASPEN_HOST_SRAM_SHARED_MEMORY=true`를 설정해 SI CL0/CL1 SRAM,
AP shared SRAM, AP BL2 header SRAM을 transferable DMI backing으로 연결한다.
T10/T11 runtime 전까지 이 절의 명령은 선택된 기본 mode와 검증 절차를
문서화한다. 최종 runtime pass나 wall-time 개선은 아직 여기서 주장하지 않는다.

```bash
python3 scripts/run/run_qbox_apollo_fvp_full.py \
  --si-mode live-cl0-cl1 \
  --skip-build \
  --timeout 2400 \
  --rootfs-bootargs-profile quiet-console \
  --post-login-probe \
  --cc3xx-qemu-native-backend \
  --rse-lms-accel \
  --rse-fast-boot-sram-dmi \
  --out-dir build/qbox-apollo-fvp/full-live-cl0-cl1-fast-rse
```

이 기본 mode는 range-limited flash DMI, RSE storage direct fast path,
ATU/host-memory/SI-SRAM DMI, shared-memory SRAM backing을 켠다.
SRAM/AP-BL2 direct-file alias는 켜지 않는다. 성공한 check-only 또는 runtime
결과에서는 child `result.json`의 `rse_fast_boot_sram_dmi.enabled`,
`host_sram_shared_memory`, `range_limited_flash_dmi`가 `true`이고,
`rse_direct_file_aliases_summary.enabled`는 `false`여야 한다.
`host_sram_backing`의 네 SRAM entry는 `mode: "shared_memory"`,
`shared_memory: true`, `file_created: false`로 해석한다. DMI/profile counter는
해당 fast path가 선택됐는지 확인하는 용도이며, profile overhead가 들어간
run을 최종 wall-time 비교로 사용하지 않는다.

기본 mode에서 host SRAM `.bin` 파일이 생기면 regression이다.

```bash
find build/qbox-apollo-fvp/full-live-cl0-cl1-fast-rse -type f \( \
  -name 'host-si-cl*-sram.bin' -o \
  -name 'host-ap-*-sram.bin' \
\) -print -quit
```

위 command는 아무것도 출력하지 않아야 한다.

legacy file-backed SRAM alias는 명시적 debug/compatibility rollback 경로로만
사용한다. top-level wrapper를 쓸 때는 다음처럼 legacy mode를 요청한다.

```bash
./run_qbox_local.sh --legacy-file-backed-sram
```

private RSE runtime을 직접 디버그할 때만 legacy preset을 명시적으로 전달한다.

```bash
python3 scripts/run/run_qbox_apollo_fvp_full.py --runtime-child \
  --skip-build \
  --cc3xx-qemu-native-backend \
  --rse-lms-accel \
  --rse-fast-boot-aliases \
  --qbox-perf-profile \
  --timeout 90 \
  --ignore-fail-patterns \
  --out-dir build/qbox-apollo-fvp/rse-legacy-file-backed-sram
```

이 legacy preset은 compatibility/debug를 위해 SI SRAM, AP BL2, RSE boot
flash read-only window, AP FIP read-only window, RSE PS/ITS storage direct-MMIO
fast path를 direct-file alias로 켠다. RSE 전체 stub이나 secure boot success
stub은 아니다. FWU, PS/ITS persistence, negative secure-boot,
flash command-state fidelity 검증에는 legacy preset을 끄고 shared-memory SRAM
DMI 또는 기존 flash path를 사용한다.

RSE 부팅 시간 자체를 FVP와 비교하는 짧은 smoke에서는 full-system wrapper보다
private RSE runtime을 직접 쓰는 편이 빠르다. T8 기준 기본 QBox-side 성능 조합은
qemu-native CC3XX backend, LMS verifier accelerator, shared-memory SRAM DMI
fast path이다.

```bash
python3 scripts/run/run_qbox_apollo_fvp_full.py --runtime-child \
  --skip-build \
  --cc3xx-qemu-native-backend \
  --rse-lms-accel \
  --rse-fast-boot-sram-dmi \
  --qbox-perf-profile \
  --timeout 90 \
  --ignore-fail-patterns \
  --out-dir build/qbox-apollo-fvp/rse-fast-boot-perf
```

`build/qbox-apollo-fvp/rse-step1-storage-direct-fastpath-20260608-1/`은
shared-memory SRAM DMI 이전의 historical/pre-SRAM-DMI baseline이며, legacy
file-backed alias timing bundle로만 해석한다. 해당 run의 `rse_bl1_1` ->
`rse_first_image_slot`은 22.668초였고, 같은 기준의 FVP timed run은
`build/local-apollo-fvp/fvp-boot-timed-20260604/`의 4.818초였다. 이 값은 새
기본 mode의 성공 또는 최종 wall-time 개선 증거가 아니다. shared-memory SRAM
DMI 기본 조합의 최종 runtime pass와 wall-time evidence는 T10/T11에서 별도로
생성한다. 따라서 현재 historical baseline 기준 QBox RSE는 FVP 대비 약 4.7배
느렸고, 다음 개선 목표는 15초 이하, 최종 목표는 10초 이하로 잡는다.

성능 비교에서는 `--rse-bl2-load-profile`과 `--qbox-perf-profile`을 끈다.
두 옵션은 BL2 함수 hit/counter를 확인하는 분석용 hook이며, 최단 wall-time
비교에는 계측 overhead를 더한다. BL2 accelerator를 켠 positive smoke도
최종 timing 비교는 no-profile 형태로 실행한다.

`bootutil_verify_sig()` positive skip을 함께 켠 최신 profile smoke는
`build/qbox-apollo-fvp/rse-bl2-verify-sig-skip-remote-rebuild-smoke-20260608/`
에 저장되어 있다. 이 run은 `rse_bl1_1` -> `rse_first_image_slot = 24.773초`,
`verify_matches=1`, `skip_hits=1`, `last_fih_success=0x0`으로 image 4/3/2/0
load와 AP power-on, first image slot까지 진행했다. 다만 현재 최단 시간은
아니므로 `--rse-bl2-verify-sig-skip`은 PKA traffic 제거를 확인하는 positive
boot smoke 전용 옵션으로 사용하고, FWU/negative secure-boot fidelity 증거로
사용하지 않는다.

profile overhead를 뺀 같은 옵션의 smoke는
`build/qbox-apollo-fvp/rse-bl2-verify-sig-skip-noprofile-smoke-20260608/`이며,
`rse_bl1_1` -> `rse_first_image_slot = 24.179초`를 기록했다.

BL2 boot encryption/hash accelerator와 positive signature skip을 함께 켜되
profile hook을 끈 smoke는
`build/qbox-apollo-fvp/rse-bl2-accel-no-load-profile-smoke-20260608/`이다. 이
run은 `[ERR]` 없이 image 4/3/2/0 load, AP power-on, first image slot까지
진행했고 `rse_bl1_1` -> `rse_first_image_slot = 22.772초`를 기록했다. 현재
최단 run인 22.668초와 거의 같지만 넘어서지는 못했으므로, BL2 accelerator는
다음 image-level accelerator 개발을 위한 기능 검증 옵션으로 둔다.

BL2 hook 기반 profile/accelerator를 사용할 때 private RSE runtime은
`--rse-bl2-elf`
에서 `boot_load_image_to_sram`, `boot_enc_decrypt`, `bootutil_img_hash`,
`bootutil_verify_sig` 등의 symbol 주소를 자동으로 resolve한다. full-system
wrapper는 local-build TF-M BL2 ELF를 자동으로 전달하므로 일반적으로 별도
주소 override를 줄 필요가 없다. 실제로 사용된 주소는 child result JSON의
`rse_bl2_load_profile.symbol_source`에서 확인한다.

BL2 image-level accelerator 후보를 profiling하려면 다음 옵션을 추가한다.
성능 비교가 아니라 hook/counter 확인이 목적이다.

```bash
python3 scripts/run/run_qbox_apollo_fvp_full.py --runtime-child \
  --skip-build \
  --cc3xx-qemu-native-backend \
  --rse-lms-accel \
  --rse-fast-boot-sram-dmi \
  --rse-bl2-load-profile \
  --rse-bl2-boot-enc-accel \
  --rse-bl2-img-hash-accel \
  --rse-bl2-verify-sig-accel \
  --qbox-perf-profile \
  --timeout 90 \
  --ignore-fail-patterns \
  --out-dir build/qbox-apollo-fvp/rse-fast-boot-bl2-image-accel
```

`bootutil_img_hash` accelerator는 shared-memory SRAM DMI를 우선 사용하고,
legacy/debug direct-file alias mode에서만 분할된 alias window를 4KB chunk로
읽는 fallback을 사용한다. 해당 fallback 또는 DMI path가 동작하면
`qbox-perf-profile/rse-hotpath-profile.json`에서
`bl2_img_hash_accel.hits > 0`과 `dmi_failures = 0`을 확인할 수 있다. 이
accelerator는 hash/signature/security-counter flow를 보존하지만, 아직 최단
시간 조합은 아니므로 성능 비교 후보로만 사용한다.

`--rse-bl2-verify-sig-accel`은 기본 safe mode에서 host-native ECDSA 검증 결과를
기록하고 캐시하지만 guest firmware의 PKA 기반 `bootutil_verify_sig()` 실행은
유지한다. 따라서 `verify_matches`를 확인하는 profile 도구로는 유용하지만,
그 자체로 PKA traffic을 줄이지는 않는다. 실제 성능 개선은 이후
`boot_load_image_to_sram()` 단위 semantic accelerator에서 hash/ECDSA/AES-CTR
처리를 함께 검증하고 guest-visible 상태를 반영하는 방식으로 진행해야 한다.
PKA traffic 제거 실험에는 `--rse-bl2-verify-sig-skip`을 추가할 수 있다. 이
옵션은 host-native ECDSA 검증이 성공한 positive path에서만 guest
`bootutil_verify_sig()` body를 건너뛰며, BL2 ELF에서 resolve한 `FIH_SUCCESS`
변수 값을 guest memory에서 읽어 반환한다.

## tmux 화면으로 실행

사용자에게 subsystem별 UART 출력을 보여주려면 tmux wrapper를 사용한다.

```bash
scripts/run/run_qbox_apollo_fvp_full_tmux.sh
```

기본 실행은 `live-cl0-cl1`, `--skip-build`, `--post-login-probe`,
`--keep-running-after-pass`, `--rootfs-bootargs-profile quiet-console`, `--timeout 0`,
`--range-limited-flash-dmi`, `--rse-fast-boot-sram-dmi`를 사용한다. 이 기본
path는 `QBOX_RDASPEN_HOST_SRAM_SHARED_MEMORY=true`로 shared-memory SRAM DMI를
선택하며, legacy file-backed SRAM alias는 사용하지 않는다. 따라서 Linux
boot와 post-login probe가 끝나도 QBox target은 자동 종료되지 않는다.
종료하려면 tmux에서 `F12`를 눌러 session을 끝낸다. 실행하면 tmux session
안에 다음 pane이 생성된다.

qemu-native CC3XX backend를 화면 실행에 적용하려면 다음처럼 실행한다.

```bash
scripts/run/run_qbox_apollo_fvp_full_tmux.sh \
  --cc3xx-stats \
  --cc3xx-stats-interval 65536 \
  --cc3xx-qemu-native-backend
```

tmux 화면 실행에서 legacy file-backed SRAM alias rollback이 필요하면
top-level wrapper의 compatibility option을 사용한다.

```bash
./run_qbox_local.sh --legacy-file-backed-sram
```

| Pane | 로그 |
| --- | --- |
| `qbox-runner` | QBox runner stdout |
| `platform` | `qbox-platform.log` |
| `rse` | `qbox-rse.log` |
| `safety_island_cl0` | `qbox-safety-island-cl0.log` |
| `safety_island_cl1` | `qbox-safety-island-cl1.log` |
| `secure_console` | `qbox-secure-console.log` |
| `primary_console` | `qbox-primary-console.log` |

세션 이름과 출력 위치를 지정하려면 다음처럼 실행한다.

```bash
scripts/run/run_qbox_apollo_fvp_full_tmux.sh \
  --session apollo-qbox-demo \
  --out-dir build/qbox-apollo-fvp/full-demo
```

빌드까지 포함하려면 `--build`를 사용한다.

```bash
scripts/run/run_qbox_apollo_fvp_full_tmux.sh --build
```

검증용으로 pass 이후 자동 종료되는 bounded run이 필요하면
`--exit-after-pass` 또는 `--timeout SECONDS`를 사용한다.

```bash
scripts/run/run_qbox_apollo_fvp_full_tmux.sh \
  --exit-after-pass \
  --timeout 2400
```

실행하지 않고 command와 로그 layout만 확인하려면 `--dry-run`을 사용한다.

```bash
scripts/run/run_qbox_apollo_fvp_full_tmux.sh --dry-run
```

tmux 안에서 `F12`를 누르면 전체 session이 종료된다. `--no-attach`를
사용하면 session만 만들고 attach하지 않는다.

## 사전 조건

작업 디렉터리는 workspace top이어야 한다.

```bash
cd /build/arm/arm-auto-solutions
```

필요한 기본 산출물은 `build/local-apollo-fvp/` 아래에 있어야 한다.

| Artifact | 기본 경로 |
| --- | --- |
| RSE ROM | `build/local-apollo-fvp/deploy/firmware/rse-rom-image.img` |
| RSE flash | `build/local-apollo-fvp/deploy/firmware/rse-flash-image.img` |
| RSE OTP | `build/local-apollo-fvp/deploy/firmware/rse-otp-image.img` |
| AP flash | `build/local-apollo-fvp/deploy/firmware/ap-flash-image.img` |
| AP BL2 ELF | `build/local-apollo-fvp/work/trusted-firmware-a/apollo_fvp/debug/bl2/bl2.elf` |
| Root disk | `build/local-apollo-fvp/deploy/boot/apollo-fvp-local-disk.img` |
| EFI capsule disk | `build/local-apollo-fvp/deploy/boot/boot-fat.img` |
| Provisioning bundle | `build/local-apollo-fvp/deploy/firmware/combined_provisioning_message.bin` |
| AP DTB | `build/local-apollo-fvp/deploy/boot/apollo-fvp.dtb` |
| RSE symbols | `build/local-apollo-fvp/debug/symbols.json` |
| SI CL0 image | `build/local-apollo-fvp/deploy/firmware/si0_ramfw.bin` |
| SI CL1 image | `build/local-apollo-fvp/deploy/firmware/zephyr-demos-cl1.bin` |
| SI CL1 symbols | `build/local-apollo-fvp/deploy/firmware/zephyr-demos-cl1.elf` |

산출물이 없으면 먼저 local build를 실행한다.

```bash
./local_build.sh build
```

FVP 비교를 위해서는 FVP boot evidence도 필요하다.

```bash
python3 scripts/run/runfvp_log_boot.py \
  --machine apollo-fvp \
  --fvpconf build/local-apollo-fvp/deploy/apollo-fvp-local.fvpconf \
  --out-dir build/local-apollo-fvp/fvp-boot \
  --timeout 900 \
  --require all \
  --min-runtime 70 \
  --no-login
```

이 command는 FVP 로그를 `build/local-apollo-fvp/fvp-boot/`에 저장한다.

## QBox 빌드

full-system에 필요한 QBox target을 빌드한다.

```bash
./local_build.sh qbox
```

target 단위로 직접 빌드하려면 다음 command를 사용할 수 있다.

```bash
QBOX_PLATFORM_BUILD_DIR="${QBOX_PLATFORM_BUILD_DIR:-build/local-apollo-fvp/work/qbox-platform}"

cmake --build "${QBOX_PLATFORM_BUILD_DIR}" \
  --target cpu_arm_cortexR82 cpu_arm_cortexM55 addrtr platforms-vp apollo_fvp_full_system \
  --parallel 8
```

RSE CPU hook 또는 `tools/qbox/qemu-components/common/include/cpu.h`를 바꾼
뒤에는 `cpu_arm_cortexM55`, `platforms-vp`, 그리고 Apollo aggregate target인
`apollo_fvp_full_system`을 다시 빌드한다. 현재 Apollo RSE 경로는
`platforms-vp` 안에서 in-process `cpu_arm_cortexM55` 모듈을 사용하므로,
삭제된 Apollo remote helper target을 빌드 계약이나 실행 절차에
포함하지 않는다.

component 변경 이후에는 다음 검사를 권장한다.

```bash
QBOX_PLATFORM_BUILD_DIR="${QBOX_PLATFORM_BUILD_DIR:-build/local-apollo-fvp/work/qbox-platform}"

cmake --build "${QBOX_PLATFORM_BUILD_DIR}" \
  --target reset_fanout reset_fanout-tests mhu320ae mhu320ae-tests \
  platforms-vp \
  --parallel 8

ctest --test-dir "${QBOX_PLATFORM_BUILD_DIR}" \
  -R 'reset_fanout|mhu320ae' \
  --output-on-failure
```

## G0: 사전 검사

G0는 artifact와 source contract가 준비되었는지 확인한다.

```bash
python3 scripts/inspect/probe_qemu_cortex_r82.py --source-root .

python3 scripts/run/run_qbox_apollo_fvp_full.py \
  --check-only \
  --out-dir build/qbox-apollo-fvp/full-check-only

python3 scripts/test/validate_qbox_apollo_fvp_full_map.py \
  --check memory,irq,atu \
  --out build/qbox-apollo-fvp/full-check-only/map-validation.json

python3 scripts/test/audit_qbox_apollo_fvp_full_coverage.py \
  --check hardware-blocks \
  --output build/qbox-apollo-fvp/full-check-only/coverage-audit.json
```

확인할 파일은 다음과 같다.

```text
build/qbox-apollo-fvp/full-check-only/result.json
build/qbox-apollo-fvp/full-check-only/map-validation.json
build/qbox-apollo-fvp/full-check-only/coverage-audit.json
```

## G1/G2: Service-Model Full Boot 및 AP Probe

RSE-first AP firmware boot가 동작하는지 확인한다.

```bash
python3 scripts/run/run_qbox_apollo_fvp_full.py \
  --si-mode service-model \
  --skip-build \
  --timeout 1200 \
  --rootfs-bootargs-profile quiet-console \
  --post-login-probe \
  --out-dir build/qbox-apollo-fvp/full-service-model

python3 scripts/analyze/compare_fvp_qbox_rse_logs.py \
  --fvp build/local-apollo-fvp/fvp-boot \
  --qbox build/qbox-apollo-fvp/full-service-model \
  --output build/qbox-apollo-fvp/full-service-model/comparison.json
```

`service-model`은 Safety Island CPU fidelity debt를 명시적으로 남긴다.
G1은 같은 `full-service-model/result.json`에서 AP BL2, BL31, OP-TEE,
U-Boot, Linux, post-login probe, `qbox-secure-console.log`,
`qbox-primary-console.log`만 확인한다. G2는 같은 evidence directory에서
RSE-first service-model 전체 marker, subsystem logs, service-model debt,
comparison 결과까지 확인한다.

## G3: Live CL1 Integration

Safety Island CL1 Zephyr를 live Cortex-R82 domain으로 실행한다.

```bash
python3 scripts/run/run_qbox_apollo_fvp_full.py \
  --si-mode live-cl1 \
  --skip-build \
  --timeout 1200 \
  --rootfs-bootargs-profile quiet-console \
  --post-login-probe \
  --out-dir build/qbox-apollo-fvp/full-live-cl1

python3 scripts/test/audit_qbox_apollo_fvp_full_coverage.py \
  --result-json build/qbox-apollo-fvp/full-live-cl1/result.json \
  --output build/qbox-apollo-fvp/full-live-cl1/coverage-audit.json
```

확인할 marker는 CL1 Zephyr boot, PFDI agent/service, network configured,
Linux post-login의 `arm_si_rproc`, `rpmsg`, `hipc_ethsi1`이다.

## G4: Live CL0/CL1 Integration

Safety Island CL0 SCP-firmware와 CL1 Zephyr를 모두 live domain으로
실행한다. 최종 runtime completion candidate는 이 모드에서만 나온다.

```bash
python3 scripts/run/run_qbox_apollo_fvp_full.py \
  --si-mode live-cl0-cl1 \
  --skip-build \
  --timeout 2400 \
  --rootfs-bootargs-profile quiet-console \
  --post-login-probe \
  --out-dir build/qbox-apollo-fvp/full-live-cl0-cl1

python3 scripts/test/audit_qbox_apollo_fvp_full_coverage.py \
  --result-json build/qbox-apollo-fvp/full-live-cl0-cl1/result.json \
  --output build/qbox-apollo-fvp/full-live-cl0-cl1/coverage-audit.json
```

성공 시 `result.json`에서 다음 항목을 확인한다.

```bash
python3 - <<'PY'
import json
from pathlib import Path

path = Path("build/qbox-apollo-fvp/full-live-cl0-cl1/result.json")
data = json.loads(path.read_text())
print("verdict:", data.get("verdict"))
print("blocker:", data.get("blocker"))
print("completion_gates:", data.get("completion_gates"))
print("first_failing_marker:", data.get("first_failing_marker"))
PY
```

기대값은 `verdict: pass`, `blocker: None`, `G0/G4: pass`,
`first_failing_marker: None`이다.

## G5: FVP Equivalence Closure

FVP와 QBox full live run을 비교하고, map/coverage sidecar를 생성한다.

```bash
python3 scripts/run/runfvp_log_boot.py \
  --machine apollo-fvp \
  --fvpconf build/local-apollo-fvp/deploy/apollo-fvp-local.fvpconf \
  --out-dir build/local-apollo-fvp/fvp-boot \
  --timeout 900 \
  --require all \
  --min-runtime 70 \
  --no-login

python3 scripts/analyze/compare_fvp_qbox_rse_logs.py \
  --fvp build/local-apollo-fvp/fvp-boot \
  --qbox build/qbox-apollo-fvp/full-live-cl0-cl1 \
  --output build/qbox-apollo-fvp/full-live-cl0-cl1/comparison.json

python3 scripts/test/validate_qbox_apollo_fvp_full_map.py \
  --check memory,irq,atu \
  --out build/qbox-apollo-fvp/full-live-cl0-cl1/map-comparison.json

python3 scripts/test/audit_qbox_apollo_fvp_full_coverage.py \
  --result-json build/qbox-apollo-fvp/full-live-cl0-cl1/result.json \
  --output build/qbox-apollo-fvp/full-live-cl0-cl1/coverage-audit.json
```

## 최종 Strict Verification

최종 완료 판정은 strict verifier로만 한다.

```bash
python3 scripts/test/verify_qbox_apollo_fvp_full_completion.py \
  --strict-final \
  --output build/qbox-apollo-fvp/full-live-cl0-cl1/final-verification.json
```

결과 확인:

```bash
python3 - <<'PY'
import json
from pathlib import Path

path = Path("build/qbox-apollo-fvp/full-live-cl0-cl1/final-verification.json")
data = json.loads(path.read_text())
print("completion_ready:", data.get("completion_ready"))
print("completion_claim_allowed:", data.get("completion_claim_allowed"))
print("overall_gates:", data.get("overall_gates"))
print("first_blocker:", data.get("first_blocker"))
print("rejection:", data.get("completion_rejection_reason"))
PY
```

완료 조건:

```text
completion_ready: True
completion_claim_allowed: True
overall_gates.G0..G5: pass
first_blocker: None
completion_rejection_reason: None
```

## 결과 디렉터리 구조

runner는 `--out-dir` 아래에 evidence를 저장한다.

```text
build/qbox-apollo-fvp/full-live-cl0-cl1/
  result.json
  summary.txt
  rd-aspen-result.json
  qbox-platform.log
  qbox-rse.log
  qbox-safety-island-cl0.log
  qbox-safety-island-cl1.log
  qbox-secure-console.log
  qbox-primary-console.log
  post-login-probe-actions.log
  ap-si-mhuv3-trace.log
  si-cl1-mhuv3-trace.log
  si-cl0-pc-trace.log
  comparison.json
  map-comparison.json
  coverage-audit.json
  final-verification.json
```

중요 로그:

| 로그 | 확인 내용 |
| --- | --- |
| `qbox-rse.log` | TF-M BL1_1, BL1_2/BL2 handoff, image manifest, RSE-to-SI/AP handoff |
| `qbox-safety-island-cl0.log` | SCP start, module init, GIC multiview configured |
| `qbox-safety-island-cl1.log` | Zephyr boot, CPU OoR, PFDI agent/service, network configured |
| `qbox-secure-console.log` | AP BL2, BL31, OP-TEE |
| `qbox-primary-console.log` | U-Boot, Linux kernel, login, root shell |
| `ap-si-mhuv3-trace.log` | AP-SI MHU traffic |
| `si-cl1-mhuv3-trace.log` | CL1 MHU/PFDI traffic |
| `si-cl0-pc-trace.log` | CL0 SCP-firmware PC trace |

## Artifact Override

기본 artifact 대신 실험 이미지를 사용하려면 command-line option으로
경로를 지정한다.

```bash
python3 scripts/run/run_qbox_apollo_fvp_full.py \
  --si-mode live-cl0-cl1 \
  --skip-build \
  --timeout 2400 \
  --post-login-probe \
  --rse-rom /path/to/rse-rom-image.img \
  --rse-flash /path/to/rse-flash-image.img \
  --rse-otp /path/to/rse-otp-image.img \
  --ap-flash /path/to/ap-flash-image.img \
  --rootfs /path/to/apollo-fvp-local-disk.img \
  --si-cl0-image /path/to/si0_ramfw.bin \
  --si-cl1-image /path/to/zephyr-demos-cl1.bin \
  --si-cl1-symbols /path/to/zephyr-demos-cl1.elf \
  --out-dir build/qbox-apollo-fvp/full-live-cl0-cl1-experiment
```

모든 artifact override는 `result.json`의 `artifacts` 항목에 기록된다.

## 문제 분석 순서

복잡한 boot failure는 다음 순서로 본다.

1. `summary.txt`에서 `verdict`, `blocker`, `first_failing_marker`를 본다.
2. `result.json`의 `marker_groups`와 `completion_gates`를 본다.
3. 가장 이른 실패 domain의 UART log를 본다.
4. MHU나 PFDI 문제이면 `ap-si-mhuv3-trace.log`와
   `si-cl1-mhuv3-trace.log`를 확인한다.
5. CL0 hang이면 `si-cl0-pc-trace.log`를 확인한다.
6. map/interrupt/ATU 문제이면 `map-comparison.json`과
   `coverage-audit.json`을 본다.
7. 로그가 특정 firmware stage나 handoff를 가리킨 뒤 GDB/Iris 또는
   QBox/QEMU source-level debugging으로 넘어간다.

## 자주 보는 실패와 대응

### `missing_artifact:*`

원인: `build/local-apollo-fvp/deploy/` 산출물이 없거나 경로가 다르다.

대응:

```bash
./local_build.sh build
python3 scripts/run/run_qbox_apollo_fvp_full.py \
  --check-only \
  --out-dir build/qbox-apollo-fvp/full-check-only
```

### `live_cl0_cl1_marker_blocked:*`

원인: SI CL0 또는 SI CL1 live marker가 빠졌다.

대응:

```bash
sed -n '1,220p' build/qbox-apollo-fvp/full-live-cl0-cl1/qbox-safety-island-cl0.log
sed -n '1,220p' build/qbox-apollo-fvp/full-live-cl0-cl1/qbox-safety-island-cl1.log
sed -n '1,220p' build/qbox-apollo-fvp/full-live-cl0-cl1/si-cl0-pc-trace.log
```

### `live_cl0_cl1_hipc_rpmsg_blocked:*`

원인: Linux post-login에서 HIPC/RPMsg/PFDI 관련 device나 module marker가
빠졌다.

대응:

```bash
sed -n '1,260p' build/qbox-apollo-fvp/full-live-cl0-cl1/post-login-probe-actions.log
sed -n '1,260p' build/qbox-apollo-fvp/full-live-cl0-cl1/qbox-primary-console.log
sed -n '1,260p' build/qbox-apollo-fvp/full-live-cl0-cl1/ap-si-mhuv3-trace.log
sed -n '1,260p' build/qbox-apollo-fvp/full-live-cl0-cl1/si-cl1-mhuv3-trace.log
```

특히 `ethsi1`, `rpmsg`, `arm_si_rproc`, `hipc_ethsi1` marker를 확인한다.

### FVP comparison 실패

원인: FVP baseline log가 없거나 QBox run과 비교할 marker가 빠졌다.

대응:

```bash
python3 scripts/run/runfvp_log_boot.py \
  --machine apollo-fvp \
  --fvpconf build/local-apollo-fvp/deploy/apollo-fvp-local.fvpconf \
  --out-dir build/local-apollo-fvp/fvp-boot \
  --timeout 900 \
  --require all \
  --min-runtime 70 \
  --no-login
python3 scripts/analyze/compare_fvp_qbox_rse_logs.py \
  --fvp build/local-apollo-fvp/fvp-boot \
  --qbox build/qbox-apollo-fvp/full-live-cl0-cl1 \
  --output build/qbox-apollo-fvp/full-live-cl0-cl1/comparison.json
```

### Cortex-R82 probe 실패

원인: `tools/qemu` 또는 `tools/qbox`의 Cortex-R82 지원이 기대와 다르다.

대응:

```bash
python3 scripts/inspect/probe_qemu_cortex_r82.py --source-root .
git -C tools/qemu log -1 --oneline
git -C tools/qbox log -1 --oneline
```

### 오래된 로그가 섞이는 경우

runner는 `result.json`, `summary.txt`, UART log, trace log를 실행 전에
정리한다. 그래도 결과가 의심되면 새 output directory를 사용한다.

```bash
python3 scripts/run/run_qbox_apollo_fvp_full.py \
  --si-mode live-cl0-cl1 \
  --skip-build \
  --timeout 2400 \
  --post-login-probe \
  --out-dir build/qbox-apollo-fvp/full-live-cl0-cl1-$(date +%Y%m%d-%H%M%S)
```

## 완료 보고 시 포함할 정보

완료 또는 실패를 보고할 때는 다음 정보를 같이 남긴다.

- 실행 command 전체
- `result.json` 경로와 `verdict`
- `final-verification.json` 경로와 `completion_claim_allowed`
- 실패 시 `blocker`와 `first_failing_marker`
- 주요 UART log 경로
- FVP comparison, map comparison, coverage audit 결과
- 사용한 `tools/qbox`와 `tools/qemu` commit
