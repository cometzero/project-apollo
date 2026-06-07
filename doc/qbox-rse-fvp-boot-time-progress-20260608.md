# QBox RSE FVP Boot-Time Gap 진행 기록

기록 시각: 2026-06-08 10:40 KST

## 목표

Arm Zena CSS FVP 대비 QBox의 RSE 부팅 시간이 크게 느린 문제를 줄이기 위해,
QBox 수정 중심의 opt-in 성능 개선 경로를 검토하고 구현한다. 기본 방향은
RSE 전체 stub이 아니라, FVP 대비 병목이 큰 BL2 image load/decrypt/hash/verify
구간을 좁은 semantic accelerator로 줄이는 것이다.

## 현재 판단

- 기존 최단 QBox 기준은 `--cc3xx-qemu-native-backend --rse-lms-accel
  --rse-fast-boot-aliases` 조합의 RSE timing smoke다.
- 기존 문서 기준 FVP timed run은 `rse_bl1_1`부터 `rse_first_image_slot`까지
  약 4.818초이고, QBox fast-alias/storage-direct 기준은 약 22.668초다.
- 남은 큰 gap은 전체 RSE 실행이 아니라 BL2 이후 SI/AP/RSE runtime image의
  RAM-load, decrypt, hash, signature/storage 경로에 집중되어 있다.
- MCUBoot `ram_load.c` 확인 결과 이 빌드는 image 전체를 먼저 SRAM에 복사한
  뒤 payload만 1 KiB chunk로 `boot_enc_decrypt()`한다. 따라서 첫 decrypt
  entry에서 같은 image payload 전체를 host-native AES-CTR로 한 번에 처리하고,
  같은 image의 나머지 decrypt call만 skip하는 방식은 이후 flash read가
  payload를 다시 덮어쓰지 않아 구조적으로 타당하다.

## 이번 작업에서 구현한 내용

### QEMU/libqemu hook support

파일: `tools/qemu/`

- QBox가 QEMU TCG PC-entry callback, memory DMI/direct access, Arm CPU state를
  더 좁게 사용할 수 있도록 libqemu wrapper surface를 확장했다.
- Cortex-M/RSE hot path에서 guest firmware 함수 entry를 관측하고, 필요한
  register/state/memory를 host side에서 검사하는 기반을 추가했다.

### QBox CPU hook

파일: `tools/qbox/qemu-components/common/include/cpu.h`

- `bl2_load_accel` CCI parameter를 추가했다.
- `boot_load_image_to_sram()` entry에서 수집한 image별 RAM-load snapshot을
  `boot_enc_decrypt()` hook에서 참조하도록 했다.
- `boot_enc_set_key()`에서 캡처한 AES key를 `bl2_load_accel`에서도 사용하도록
  기존 key capture 경로를 확장했다.
- 지원 대상은 `IMAGE_F_RAM_LOAD | IMAGE_F_ENCRYPTED_AES128`, 즉 현재 관측된
  `flags=0x24` image로 제한했다.
- 첫 chunk인 `off == 0 && blk_off == 0`일 때만 image payload 전체를
  host-native AES-CTR로 복호화한다.
- 같은 image의 이후 `boot_enc_decrypt()` entry는 이미 복호화된 image일 때만
  LR로 return시켜 skip한다.
- unsupported layout, key miss, DMI/direct-alias 실패, state update 실패는
  guest firmware path로 fallback하도록 했다.
- `rse-hotpath-profile.json`에 `bl2_load_accel` 카운터를 추가했다.
- 후속 보완으로 image payload가 RSE VM0/VM1 경계를 넘는 경우를 위해
  split-DMI read/write fallback을 추가했다.

### Lua platform wiring

파일: `tools/qbox/platforms/fvp-rd-aspen-rse/conf.lua`

- `QBOX_RDASPEN_RSE_BL2_LOAD_ACCEL`
- `QBOX_RDASPEN_RSE_BL2_LOAD_ACCEL_MAX_BYTES`

위 환경변수를 RSE `RemoteCPU`의 `bl2_load_accel`,
`bl2_load_accel_max_bytes` CCI parameter로 연결했다.

### Runner wiring

파일:

- `scripts/run_qbox_fvp_rd_aspen_rse.py`
- `scripts/run_qbox_apollo_fvp_full.py`

추가된 옵션:

```bash
--rse-bl2-load-accel
--rse-bl2-load-accel-max-bytes <bytes>
```

standalone RSE runner는 이 옵션을 받으면 BL2 hook address, state layout,
encryption key layout, profile output 환경변수를 함께 설정한다. Apollo full
wrapper도 동일 옵션을 child RSE runner로 전달하도록 했다.

## 검증 결과

완료된 정적/빌드 검증:

```bash
python3 -m py_compile \
  scripts/run_qbox_fvp_rd_aspen_rse.py \
  scripts/run_qbox_apollo_fvp_full.py
```

결과: 통과

```bash
git -C tools/qbox diff --check -- \
  qemu-components/common/include/cpu.h \
  qemu-components/common/include/rse_mcuboot_image.h \
  platforms/fvp-rd-aspen-rse/conf.lua \
  platforms/fvp-rd-aspen/README.md

git diff --check -- \
  scripts/run_qbox_fvp_rd_aspen_rse.py \
  scripts/run_qbox_apollo_fvp_full.py \
  doc/qbox-rse-boot-slow-path-analysis-ko.md
```

결과: 통과

```bash
cmake --build tools/qbox/build \
  --target remote_cpu cpu_arm_cortexM55 platforms-vp \
  --parallel 8
```

결과: 통과. `fmt` enum formatting deprecation warning은 기존
`ports/initiator.h` 경로에서 발생했으며 빌드 실패는 아니다.

```bash
ctest --test-dir tools/qbox/build \
  -R 'rse_p256_ecdsa|rse_mcuboot_image|rse_lms_accel|cc3xx_core' \
  --output-on-failure
```

결과: 통과. split-DMI 보완 전과 후 모두 4/4 test가 통과했다.

## Runtime smoke 결과

### BL2 load accelerator 1차 smoke

명령:

```bash
python3 scripts/run_qbox_fvp_rd_aspen_rse.py \
  --skip-build \
  --cc3xx-qemu-native-backend \
  --rse-lms-accel \
  --rse-fast-boot-aliases \
  --rse-bl2-load-accel \
  --qbox-perf-profile \
  --timeout 60 \
  --ignore-fail-patterns \
  --out-dir build/qbox-apollo-fvp/rse-bl2-load-accel-smoke-20260608
```

결과:

- `passed: False`
- `blocker: qbox_platform_timeout`
- RSE는 `rse_first_image_slot`까지 도달했다.
- 주요 marker:
  - `rse_bl1_1`: 3.412s
  - `rse_bl2_decrypted`: 12.340s
  - `rse_bl2_validated`: 12.440s
  - `rse_image_4_loaded`: 13.945s
  - `rse_image_3_loaded`: 24.578s
  - `rse_image_2_loaded`: 26.384s
  - `rse_image_0_loaded`: 29.795s
  - `rse_scp_power_on_ap`: 30.297s
  - `rse_first_image_slot`: 30.398s
- profile:
  - `bl2_load_accel.enabled: true`
  - `hits: 3`
  - `skip_hits: 1086`
  - `bytes: 1113328`
  - `key_misses: 0`
  - `direct_file_alias_hits: 3`
  - `dmi_failures: 2`
  - `unsupported: 233`
  - `last_flags: 0x24`
  - `last_unsupported_mask: 64`

분석:

- image 4/3/2는 accelerator가 적용되었다.
- image 0은 `load_addr=0x3103f800`, payload start `0x3103fc00`에서
  RSE VM0/VM1 경계를 넘어가며, 기존 full-region DMI lookup이 실패했다.
- 이 결과를 바탕으로 split-DMI fallback을 추가했다.

### split-DMI 보완 후 smoke

명령:

```bash
python3 scripts/run_qbox_fvp_rd_aspen_rse.py \
  --skip-build \
  --cc3xx-qemu-native-backend \
  --rse-lms-accel \
  --rse-fast-boot-aliases \
  --rse-bl2-load-accel \
  --qbox-perf-profile \
  --timeout 60 \
  --ignore-fail-patterns \
  --out-dir build/qbox-apollo-fvp/rse-bl2-load-accel-split-dmi-smoke-20260608
```

결과:

- `passed: False`
- `blocker: none`
- `platform_returncode: 0`
- `runtime_elapsed_s: 14.555`
- platform log는 `Simulation stopped by user`로 끝났다.
- RSE log는 BL1_2가 BL2 image를 decrypt한 직후까지만 출력했다.
- 주요 marker:
  - `rse_bl1_1`: 3.412s
  - `rse_bl1_2`: 6.422s
  - `rse_attempt_image_0`: 6.824s
  - `rse_bl2_decrypted`: 13.246s
- profile:
  - `bl2_load_accel.enabled: true`
  - `hits: 0`
  - `skip_hits: 0`
  - `bytes: 0`
  - `key_misses: 0`
  - `dmi_failures: 0`
  - `unsupported: 0`

분석:

- split-DMI 보완 코드는 컴파일과 focused ctest는 통과했다.
- 다만 보완 후 smoke는 BL2로 jump하기 전 조기 종료되었기 때문에, image0
  split-DMI 개선의 runtime 효과는 아직 검증되지 않았다.
- 현재 증거만으로는 code regression인지, runner/platform stop 조건인지,
  일회성 실행 문제인지 확정할 수 없다.

## 중단 시점의 상태

사용자가 중지를 요청했으므로 추가 runtime 실험은 진행하지 않았다. 현재 커밋은
완료 전이며, 변경은 아래 세 저장소에 나뉘어 있다.

- `tools/qemu`: libqemu callback/memory/state wrapper 확장
- `tools/qbox`: QBox CC3XX/RSE hot path 및 BL2 load accelerator 구현
- top-level `project-apollo`: runner wiring, runbook, 분석 문서, submodule pointer

생성 디렉터리 `.omc/`는 작업 상태로 남아 있으나 커밋 대상이 아니다.

## 다음 재개 시 권장 순서

1. split-DMI smoke를 같은 옵션으로 한 번 재실행해 조기 종료가 재현되는지
   확인한다.
2. 재현되면 `--rse-bl2-load-accel`을 끈 baseline smoke를 같은 빌드로 실행해
   split-DMI 보완 자체의 영향인지 runner/platform lifecycle 문제인지 분리한다.
3. baseline이 정상이라면 BL1_2의 BL2 validation/jump 직전 PC-entry callback과
   runner stop 조건을 우선 추적한다.
4. split-DMI smoke가 정상화되면 다음 profile 조건을 확인한다.
   - `bl2_load_accel.enabled == true`
   - `bl2_load_accel.hits == 4`
   - `bl2_load_accel.dmi_failures == 0`
   - `bl2_load_accel.key_misses == 0`
   - RSE가 최소 `rse_first_image_slot`까지 도달
5. 이후 profiling을 끈 no-profile timing run으로 FVP 4.818s 기준과 다시
   비교한다.
