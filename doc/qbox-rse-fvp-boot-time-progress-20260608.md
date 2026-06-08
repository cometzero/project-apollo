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

사용자가 중지를 요청했으므로 당시 추가 runtime 실험은 진행하지 않았다. 이후
체크포인트를 커밋/푸시했다.

- `tools/qemu`: `8d387e0857b0 feat(libqemu): expose hotpath hooks`
- `tools/qbox`: `0accb9e6e60a perf(rse): accelerate boot hot paths`
- top-level `project-apollo`:
  `0b6e4b02b7c7 perf(qbox): wire RSE boot accelerators`

생성 디렉터리 `.omc/`는 작업 상태로 남아 있으나 커밋 대상이 아니다.

## 2026-06-08 재개 후 추가 검증

활성 목표의 1-5 검증 순서를 이어서 진행했다.

### 1. focused regression

명령:

```bash
ctest --test-dir tools/qbox/build \
  -R 'rse_p256_ecdsa|rse_mcuboot_image|rse_lms_accel|cc3xx_core' \
  --output-on-failure
```

결과:

- 4/4 통과
- `cc3xx_core-tests`, `rse_lms_accel-tests`,
  `rse_mcuboot_image-tests`, `rse_p256_ecdsa-tests` 모두 통과

### 2. split-DMI smoke 재실행

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
  --out-dir build/qbox-apollo-fvp/rse-bl2-load-accel-split-dmi-smoke2-20260608
```

결과:

- `passed: False`
- `blocker: qbox_platform_timeout`
- 이전 14초 조기 종료는 재현되지 않았다.
- RSE는 image 4/3/2/0 load, AP power-on SCMI, first image slot까지 도달했다.
- 주요 marker:
  - `rse_bl1_1`: 3.320s
  - `rse_bl2_validated`: 11.851s
  - `rse_image_4_loaded`: 13.355s
  - `rse_image_3_loaded`: 24.488s
  - `rse_image_2_loaded`: 26.193s
  - `rse_image_0_loaded`: 26.996s
  - `rse_first_image_slot`: 27.498s
- `rse_bl1_1 -> rse_first_image_slot`: 24.178s
- profile:
  - `bl2_load_accel.enabled: true`
  - `hits: 2`
  - `skip_hits: 579`
  - `bytes: 1019312`
  - `key_misses: 0`
  - `dmi_failures: 0`
  - `direct_file_alias_hits: 2`
  - `unsupported: 0`
  - snapshot `by_image`에는 image 4/3만 기록됨

해석:

- split-DMI fallback 자체는 image0 boundary DMI failure를 만들지 않았다.
- 그러나 이번 run에서는 BL2 load accelerator가 image 4/3에만 적용되고
  image 2/0에는 적용되지 않았다.
- runtime chain은 유지되었지만, 기대했던 `hits == 4` gate는 미충족이다.

### 3. no-profile timing

명령:

```bash
python3 scripts/run_qbox_fvp_rd_aspen_rse.py \
  --skip-build \
  --cc3xx-qemu-native-backend \
  --rse-lms-accel \
  --rse-fast-boot-aliases \
  --rse-bl2-load-accel \
  --timeout 60 \
  --ignore-fail-patterns \
  --out-dir build/qbox-apollo-fvp/rse-bl2-load-accel-noprofile-timing-20260608
```

결과:

- `passed: False`
- `blocker: qbox_platform_timeout`
- RSE first image slot까지 도달했다.
- `rse_bl1_1 -> rse_first_image_slot`: 23.983s
- slowest delta:
  `rse_image_4_loaded -> rse_image_3_loaded = 10.734s`

해석:

- BL2 load accelerator 단독 no-profile run은 기존 최단
  fast-alias/storage-direct baseline `22.668s`보다 빠르지 않다.
- FVP timed run `4.818s`와 비교하면 아직 약 5.0x 느리다.
- 병목은 계속 SI CL0 image 3 load/validate 구간에 남아 있다.

### 4. 기존 opt-in accelerator 조합 확인

처음에는 `/build` 아래에 all-accel timing out-dir를 만들었으나, flash image
padding 단계에서 `/build` filesystem이 100%라 `ENOSPC`가 발생했다. 실패한
partial output은 삭제했다.

이후 `/tmp`에 출력해서 같은 조합을 확인했다.

명령:

```bash
python3 scripts/run_qbox_fvp_rd_aspen_rse.py \
  --skip-build \
  --cc3xx-qemu-native-backend \
  --rse-lms-accel \
  --rse-fast-boot-aliases \
  --rse-bl2-load-accel \
  --rse-bl2-boot-enc-accel \
  --rse-bl2-img-hash-accel \
  --rse-bl2-verify-sig-skip \
  --timeout 60 \
  --ignore-fail-patterns \
  --out-dir /tmp/qbox-apollo-fvp/rse-bl2-all-accel-noprofile-timing-20260608
```

결과:

- RSE first image slot까지 도달했다.
- `rse_bl1_1 -> rse_first_image_slot`: 24.177s
- slowest delta:
  `rse_image_4_loaded -> rse_image_3_loaded = 11.135s`

해석:

- 기존 opt-in accelerator를 모두 조합해도 현재 최단 baseline을 넘지 못했다.
- `--rse-bl2-verify-sig-skip`은 positive smoke용 aggressive 옵션이므로,
  이 조합은 fidelity-oriented 기본 추천 대상도 아니다.

### 5. 최신 결론

- 이번 1-5 검증으로 split-DMI 보완 후 RSE runtime handoff가 유지되는 것은
  재확인했다.
- 단, `--rse-bl2-load-accel`은 현재 구현 그대로는 최단 timing bundle이 아니다.
- FVP `4.818s`에 접근하려면 `boot_enc_decrypt()`/hash/signature 단위보다 더
  큰 단위의 QBox 수정이 필요하다.
- 다음 유효한 구현 후보는 `boot_load_image_to_sram()` image-level semantic
  accelerator다. 다만 이 경우에도 전체 RSE stub이 아니라 MCUBoot
  header/protected TLV/hash/ECDSA/encryption TLV를 host에서 검증하고, guest-visible
  SRAM/state update만 동일하게 반영하는 positive boot 전용 opt-in 경로로
  제한해야 한다.
- `/build` filesystem이 100%라 추가 대형 runtime evidence는 `/tmp`를 쓰거나
  오래된 generated output을 정리한 뒤 수행해야 한다.

## 다음 재개 시 권장 순서

1. `/build` 용량을 먼저 확보한다. 최소 수 GB가 없으면 QBox runner가 flash
   image copy/padding 단계에서 실패한다.
2. `--rse-bl2-load-accel`이 image 2/0에서 hit하지 않는 이유를 profile한다.
   후보는 `boot_load_image_to_sram()` entry capture timing, `curr_img` state
   update timing, PC-entry callback 누락이다.
3. BL2 load accel을 계속 유지할 경우 success gate는 다음으로 둔다.
   - `bl2_load_accel.hits == 4`
   - `dmi_failures == 0`
   - `key_misses == 0`
   - `rse_bl1_1 -> rse_first_image_slot < 22.668s`
4. FVP에 더 가까워지는 주 구현은 image-level semantic accelerator로 진행한다.
   목표는 SI CL0 image 3 구간, 특히
   `rse_image_4_loaded -> rse_image_3_loaded` 10초대를 먼저 줄이는 것이다.
5. fidelity-oriented runbook에는 현재 최단인 fast-alias/storage-direct baseline을
   유지하고, BL2 accelerator 계열은 development-only opt-in으로 둔다.

## 2026-06-08 추가 진행: local BL1_2 LMS hook resolve

### 문제

full-system local artifact 실행에서 RSE BL1_2의 `BL2 image decrypted
successfully` 이후 `BL2 image validated successfully`까지 123초 이상 걸렸다.
RSE-only Yocto artifact에서는 LMS accelerator가 동작했지만, local full-system은
`build/local-apollo-fvp/work/trusted-firmware-m/bin/bl1_2.elf`를 사용한다.

확인 결과 `pq_crypto_verify` 주소가 artifact마다 달랐다.

- `fvp_rd_aspen` Yocto BL1_2: `0x11009bad`
- `apollo_fvp` Yocto/local BL1_2: `0x11009415`

기존 Lua 기본값은 `0x11009bad`였기 때문에 local full-system에서는
`--rse-lms-accel` PC-entry hook이 맞지 않았다.

### 변경

- RSE runner에 `--rse-bl1-2-elf`와 `--rse-lms-verify-addr`를 추가했다.
- `--rse-lms-verify-addr`가 없으면 선택된 `--rse-bl2-elf`와 같은 디렉터리의
  `bl1_2.elf`에서 `pq_crypto_verify`를 `llvm-nm`/`nm`으로 resolve한다.
- resolve 결과를 `QBOX_RDASPEN_RSE_LMS_VERIFY_ADDR`로 QBox에 전달한다.
- full-system wrapper가 local BL1_2 ELF를 child RSE runner에 전달한다.
- result summary에 BL1_2 symbol source와 resolved address를 기록한다.

### 검증

정적 검증:

```bash
python3 -m py_compile \
  scripts/run_qbox_fvp_rd_aspen_rse.py \
  scripts/run_qbox_apollo_fvp_full.py

git diff --check -- \
  scripts/run_qbox_fvp_rd_aspen_rse.py \
  scripts/run_qbox_apollo_fvp_full.py

git -C tools/qbox diff --check
git -C tools/qemu diff --check
```

full-system perf run:

```bash
python3 scripts/run_qbox_apollo_fvp_full.py \
  --skip-build \
  --si-mode service-model \
  --timeout 600 \
  --post-login-probe \
  --cc3xx-qemu-native-backend \
  --rse-lms-accel \
  --rse-fast-boot-aliases \
  --rse-bl2-libc-hotpath \
  --rse-bl2-delay-accel \
  --rse-bl2-load-accel \
  --rse-bl2-boot-enc-accel \
  --rse-bl2-img-hash-accel \
  --rse-bl2-verify-sig-accel \
  --qbox-perf-profile \
  --out-dir build/qbox-apollo-fvp/full-safe-accel-lms-resolve-20260608
```

결과:

- `blocker: qbox_post_login_probe_not_reached_timeout`
- `G0: pass`, `G2: blocked`
- RSE runtime handoff: `24.209s`
- `rse_bl2_decrypted -> rse_bl2_validated`: `0.100s`
- perf profile:
  - `lms_verify_addr: 0x11009415`
  - `lms_hits: 1`
  - `bl2_delay_accel.hits: 3`
  - `bl2_load_accel.hits: 4`
  - `bl2_img_hash_accel.hits: 4`
  - `bl2_verify_sig_accel.verify_matches: 9`
- `measured_boot_bl33` marker는 `72.021s`에 관측됐다.
- Linux marker와 login prompt는 timeout 전까지 관측되지 않았다.
- secure console은 OP-TEE `SE Proxy` secure partition 로드 중 멈췄고,
  primary console은 비어 있었다.

RSE-only no-profile local artifact run:

```bash
python3 scripts/run_qbox_fvp_rd_aspen_rse.py \
  --skip-build \
  --rse-rom build/local-apollo-fvp/deploy/firmware/rse-rom-image.img \
  --rse-flash build/local-apollo-fvp/deploy/firmware/rse-flash-image.img \
  --rse-otp build/local-apollo-fvp/deploy/firmware/rse-otp-image.img \
  --ap-flash build/local-apollo-fvp/deploy/firmware/ap-flash-image.img \
  --ap-bl2-elf build/local-apollo-fvp/work/trusted-firmware-a/apollo_fvp/debug/bl2/bl2.elf \
  --rse-bl1-2-elf build/local-apollo-fvp/work/trusted-firmware-m/bin/bl1_2.elf \
  --rse-bl2-elf build/local-apollo-fvp/work/trusted-firmware-m/bin/bl2.elf \
  --rootfs build/local-apollo-fvp/deploy/boot/apollo-fvp-local-disk.img \
  --provisioning-bundle build/local-apollo-fvp/deploy/firmware/combined_provisioning_message.bin \
  --cc3xx-qemu-native-backend \
  --rse-lms-accel \
  --rse-fast-boot-aliases \
  --rse-bl2-libc-hotpath \
  --rse-bl2-delay-accel \
  --rse-bl2-load-accel \
  --rse-bl2-boot-enc-accel \
  --rse-bl2-img-hash-accel \
  --rse-bl2-verify-sig-accel \
  --timeout 70 \
  --ignore-fail-patterns \
  --out-dir build/qbox-apollo-fvp/rse-local-safe-accel-lms-resolve-noprofile-20260608
```

결과:

- `blocker: qbox_platform_timeout`
- RSE runtime handoff: `24.792s`
- resolved LMS hook:
  - ELF:
    `build/local-apollo-fvp/work/trusted-firmware-m/bin/bl1_2.elf`
  - `pq_crypto_verify: 0x11009415`
- BL2 symbols were resolved from local
  `build/local-apollo-fvp/work/trusted-firmware-m/bin/bl2.elf`.
- `rse_bl2_decrypted -> rse_bl2_validated`: `0.100s`
- slowest RSE delta remains
  `rse_image_4_loaded -> rse_image_3_loaded = 11.340s`.

### 최신 결론

- local full-system의 123초 BL1_2 validation stall은 LMS hook 주소 mismatch가
  원인이었다.
- active BL1_2 ELF 기반 symbol resolve 후 해당 구간은 0.1초 수준으로 줄었다.
- RSE-only local artifact 기준 전체 RSE runtime handoff는 24.8초이며,
  남은 RSE 병목은 SI CL1 image load/validate 구간이다.
- full-system은 이제 RSE가 아니라 AP/secure-world 쪽이 다음 blocker다.
  OP-TEE secure partition 로드 중 AP memory regular path가 계속 증가하고,
  Linux primary console은 timeout 전까지 출력되지 않았다.
- 다음 최적화는 RSE가 아니라 AP/OP-TEE SP load 경로의 QEMU DMI/local fastpath
  또는 secure partition image load 경로 분석으로 분리해서 진행해야 한다.
