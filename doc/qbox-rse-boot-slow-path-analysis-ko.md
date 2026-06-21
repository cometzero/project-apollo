# QBox RSE Boot Slow Path 분석

작성일: 2026-06-04
업데이트: 2026-06-08

## 결론

RSE 전체를 stub 처리하는 것은 현재 목표와 맞지 않다. 기존 QBox full-system
boot 결과를 marker 기준으로 다시 분석하면, 가장 오래 걸리는 구간은
TF-M BL1_2에서 BL2 image를 복호화한 뒤 서명 검증을 완료하기까지의
구간이다.

최신 QBox 성공 run 기준:

| 구간 | 시간 |
| --- | ---: |
| `rse_bl2_decrypted` -> `rse_bl2_validated` | 143.866초 |
| `rse_image_3_loaded` -> `rse_image_2_loaded` | 23.011초 |
| `rse_image_4_loaded` -> `rse_image_3_loaded` | 9.443초 |
| `rse_first_image_slot` -> `measured_boot_bl33` | 8.348초 |

따라서 stub/fast-path 후보는 RSE 전체가 아니라
`BL2 image decrypted successfully` 이후 `BL2 image validated successfully`
이전의 BL1_2 image validation 구간이었다.

2026-06-08 기준으로는 QEMU-native CC3XX backend, LMS verifier accelerator,
fast boot alias preset, storage direct fast path, BL2 boot encryption/hash
accelerator 조합을 시험해 RSE runtime handoff가 수십 초대로 줄었다. FVP의
`rse_bl1_1` -> `rse_first_image_slot` 4.818초와 비교하면 아직 느리지만,
초기 QBox full-system의 191.484초 대비 병목은 상당히 줄었다.

| Run | 핵심 옵션 | `rse_bl1_1` -> `rse_first_image_slot` | FVP 대비 |
| --- | --- | ---: | ---: |
| FVP timed run | FVP 기준 | 4.818초 | 1.0x |
| QBox 초기 full-system | 기존 SystemC CC3XX/flash path | 191.484초 | 39.7x |
| QBox qemu-native + fast aliases + storage direct | `--cc3xx-qemu-native-backend --rse-lms-accel --rse-fast-boot-aliases` | 22.668초 | 4.7x |
| QBox + BL2 accelerators(no profiling) | 위 옵션 + `--rse-bl2-boot-enc-accel --rse-bl2-img-hash-accel --rse-bl2-verify-sig-skip` | 22.772초 | 4.7x |
| QBox + BL2 boot_enc/img_hash profiled | 위 옵션 + `--rse-bl2-load-profile --qbox-perf-profile` | 25.073초 | 5.2x |
| QBox + positive `bootutil_verify_sig` skip | 위 옵션 + `--rse-bl2-verify-sig-skip` | 24.179초(no profile), 24.773초(profile) | 5.0x |

따라서 현재 남은 목표는 “RSE 전체 stub”이 아니라 QEMU-native CC3XX와
flash/storage direct path를 더 FVP 내부 fast-path에 가깝게 만드는 것이다.
`bootutil_verify_sig` skip은 PKA traffic 제거에는 효과가 있지만 현재 최단
시간은 아니므로, 기본 성능 기준선은 여전히 fast alias/storage direct run으로
둔다.
`--rse-bl2-load-profile`과 `--qbox-perf-profile`은 병목 분석용이다. 최단 시간
비교에서는 이 둘을 끄고 marker timing만 사용한다.

## FVP 대비 정량 비교

FVP와 QBox를 같은 marker 기준으로 비교하기 위해 FVP 로그 수집기에
`progress_marker_first_hits` 기록을 추가하고, 로컬 FVP를 다시 실행했다.

```bash
python3 scripts/run/runfvp_log_boot.py \
  --machine apollo-fvp \
  --fvpconf build/local-apollo-fvp/deploy/apollo-fvp-local.fvpconf \
  --out-dir build/local-apollo-fvp/fvp-boot-timed-20260604 \
  --timeout 120 \
  --min-runtime 0
```

비교에 사용한 QBox full-system 성공 run은 다음이다.

```text
build/qbox-apollo-fvp/full-20260604-062846/rd-aspen-result.json
```

| 구간 | FVP | QBox full-system | QBox/FVP |
| --- | ---: | ---: | ---: |
| `rse_bl2_decrypted` -> `rse_bl2_validated` | 1.437초 | 143.866초 | 100.1x |
| `rse_bl1_1` -> `rse_bl2_validated` | 1.446초 | 152.400초 | 105.4x |
| `rse_bl1_1` -> `rse_first_image_slot` | 4.818초 | 191.484초 | 39.7x |
| `measured_boot_bl33` -> `primary_linux_cpu` | 8.759초 | 7.355초 | 0.8x |
| `primary_linux_cpu` -> `primary_login_prompt` | 41.435초 | 9.823초 | 0.2x |
| `rse_bl1_1` -> `primary_login_prompt` | 56.886초 | 217.010초 | 3.8x |

전체 Linux login 기준으로는 QBox가 FVP보다 약 3.8배 느리다. 하지만
AP firmware/Linux 구간은 QBox가 더 빠르거나 비슷하다. 실제 큰 차이는
RSE secure boot의 BL1_2 BL2 validation에 집중되어 있고, 해당 구간만 보면
QBox가 FVP보다 약 100배 느리다.

RSE 단독 validation 실험은 full-system보다 더 느린 worst-case를 보여준다.

| Run | Validation delta | FVP 대비 |
| --- | ---: | ---: |
| QBox RSE baseline | 167.863초 | 116.8x |
| QBox RSE local MMIO fast path | 156.115초 | 108.7x |
| QBox RSE local MMIO + status-read | 151.321초 | 105.3x |

`--cc3xx-local-mmio-fastpath`는 동작을 유지한 상태에서 약 11.748초를 줄였지만,
FVP와의 100배 격차를 닫기에는 부족하다. 따라서 다음 성능 개선은 단순
SystemC scheduler 우회가 아니라 CC3XX register traffic 자체를 QEMU-local로
처리하거나, firmware hash 호출 구조를 줄이는 방향이어야 한다.

## 왜 SystemC 기반 FVP가 더 빠른가

FVP도 SystemC 기반이지만, 현재 QBox보다 빠른 이유는 SystemC 사용 여부 자체가
아니다. 현재 증거에서 병목은 다음 구조적 차이로 해석된다.

| 항목 | FVP | 현재 QBox |
| --- | --- | --- |
| CPU와 주변장치 결합 | Arm Fast Model 내부의 tightly-coupled path | QEMU TCG CPU -> libqemu callback -> QBox initiator -> SystemC/TLM target |
| Hot MMIO 처리 | commercial fast model 내부 최적화 가능 | CC3XX register access 1,638,400회가 co-simulation boundary를 통과 |
| CC3XX 처리 | FVP 내부 모델에서 local callback/optimized state 가능 | SystemC CC3XX target과 QEMU-originated payload 사이 왕복 |
| DMA path | 모델 내부 optimized memory path 가능 | CC3XX model이 DMA chunk마다 TLM memory access 수행 |
| Scheduling | 한 제품 안에서 통합된 event/scheduler 설계 | QEMU iothread, SystemC scheduler, QBox bridge의 ownership 전환 |

따라서 “SystemC라서 느리다”가 아니라 “QEMU와 SystemC 사이의 고빈도 register
왕복이 현재 RSE secure boot workload와 맞지 않는다”가 더 정확한 결론이다.

## 확인 방법

다음 스크립트로 저장된 QBox run 결과를 다시 분석한다. 이 스크립트는 QBox를
재실행하지 않고 `result.json` 및 `rd-aspen-result.json`만 읽는다.

```bash
python3 scripts/analyze/analyze_qbox_rse_boot_timing.py --markdown \
  build/qbox-apollo-fvp/full-20260604-062846/result.json \
  build/qbox-apollo-fvp/full-20260604-062124/result.json
```

성공 run의 주요 결과:

| Rank | From | To | Delta s | 판단 |
| --- | --- | --- | ---: | --- |
| 1 | `rse_bl2_decrypted` | `rse_bl2_validated` | 143.866 | opt-in validation accelerator 또는 좁은 debug stub 후보 |
| 2 | `rse_image_3_loaded` | `rse_image_2_loaded` | 23.011 | flash read/DMI/cache 최적화 후보 |
| 3 | `primary_linux_cpu` | `primary_login_prompt` | 9.823 | RSE boot 구간 아님 |
| 4 | `rse_image_4_loaded` | `rse_image_3_loaded` | 9.443 | flash read/DMI/cache 최적화 후보 |
| 5 | `rse_first_image_slot` | `measured_boot_bl33` | 8.348 | RSE 이후 AP firmware 구간 |

실패 run도 같은 병목을 보인다.

| From | To | Delta s |
| --- | --- | ---: |
| `rse_bl2_decrypted` | `rse_bl2_validated` | 142.799 |

## 소스 매핑

TF-M BL1_2의 RSE UART marker는 다음 코드에 대응한다.

- `hsoc-stack/components/system_mgmt/trusted-firmware-m/bl1/bl1_2/main.c:430`
  `BL2 image decrypted successfully`
- `hsoc-stack/components/system_mgmt/trusted-firmware-m/bl1/bl1_2/main.c:441`
  `bl1_2_validate_image_at_addr()`
- `hsoc-stack/components/system_mgmt/trusted-firmware-m/bl1/bl1_2/main.c:447`
  `BL2 image validated successfully`

검증 알고리즘은 BL1_2 설정에서 LMS가 선택된다.

- `hsoc-stack/components/system_mgmt/trusted-firmware-m/bl1/config/bl1_config_default.cmake:18`
  CM signing algorithm이 `LMS`
- `hsoc-stack/components/system_mgmt/trusted-firmware-m/bl1/config/bl1_config_default.cmake:26`
  DM signing algorithm이 `LMS`
- `hsoc-stack/components/system_mgmt/trusted-firmware-m/bl1/bl1_2/main.c:207`
  LMS key type에서 `pq_crypto_verify()` 호출

기존 GDB 증거도 같은 구간을 가리킨다.

- `doc/spec/rse-qbox/evidence.md:198`: TF-M/RSE가
  `cc3xx_lowlevel_hash_uninit()`에서 실행 중이며 call stack이
  `cc3xx_hash_update()` -> `hash_digit_array()` ->
  `mbedtls_lmots_calculate_public_key_candidate()` ->
  `mbedtls_lms_verify()` -> `bl1_2_validate_image()`로 이어짐
- `doc/spec/rse-qbox/evidence.md:3681`: fault loop가 아니라 BL1_2 flash
  copy, CC3XX hash state, LMS/LMOTS signature validation에 머무는
  performance/fidelity 문제로 정리됨

QBox의 CC3XX model은 SHA/AES/PKA register와 DMA path를 모델링한다.
`tools/qbox/systemc-components/cc3xx/include/cc3xx.h:58`,
`:75`, `:117`, `:140` 부근의 HASH, DMA, PKA model이 이 hot path의
QBox 측 대상이다.

## BL1_2 Validation 내부 분해

`rse_bl2_decrypted` -> `rse_bl2_validated` 사이의 실제 호출 흐름은 다음과
같다.

| 단계 | 코드 | 역할 | 병목 가능성 |
| --- | --- | --- | --- |
| BL2 decrypt 완료 marker | `bl1/bl1_2/main.c:430` | 복호화 완료 후 검증 시작점 | 관측 구간 시작 |
| image validation 진입 | `bl1/bl1_2/main.c:441` | `bl1_2_validate_image_at_addr()` 호출 | 검증 전체 wrapper |
| measured boot hash | `bl1/bl1_2/main.c:262` | protected values hash 계산 | 작음 |
| signer loop | `bl1/bl1_2/main.c:273` | 허용 signer/ROTPK별 signature 검증 | signer 수에 비례 |
| LMS 검증 진입 | `bl1/bl1_2/main.c:207` | `pq_crypto_verify()` 호출 | 주 병목 |
| Mbed TLS LMS verify | `pq_crypto_psa.c:33` | `mbedtls_lms_verify()` 호출 | 주 병목 |
| LMOTS candidate 생성 | `mbedtls/library/lms.c:368` | `mbedtls_lmots_calculate_public_key_candidate()` 호출 | 주 병목 |
| LMOTS hash chain | `mbedtls/library/lmots.c:225` | 34 digit 각각에 대해 `j_hash_idx` 반복 | 최상위 hot loop |
| Merkle path 검증 | `mbedtls/library/lms.c:393` | H10 path 10단계 internal hash | LMOTS보다 작음 |
| security counter | `bl1/bl1_2/main.c:317` | security counter 검증 | 작음 |
| BL2 validated marker | `bl1/bl1_2/main.c:447` | 검증 완료 marker | 관측 구간 끝 |

LMS 설정은 `lms_sha256_m32_h10` + `lmots_sha256_n32_w8`이다. 헤더 기준으로
LMOTS digit 수는 34개이고, 각 digit의 Winternitz hash chain은 최대
255회 반복된다. 따라서 public key candidate 계산만으로 수천 회의
SHA-256 operation이 발생할 수 있다. QBox 관측값도 이 모델과 일치한다.

## CC3XX 계측 결과

CC3XX aggregate stats를 추가해서 RSE validation 구간을 다시 실행했다.
이 계측은 동작을 바꾸지 않고 QBox CC3XX model의 access/operation counter만
파일로 기록한다.

```bash
python3 scripts/run/run_qbox_fvp_rd_aspen_rse.py \
  --skip-build \
  --cc3xx-stats \
  --cc3xx-stats-interval 65536 \
  --timeout 230 \
  --ignore-fail-patterns \
  --out-dir build/qbox-apollo-fvp/rse-cc3xx-validation-complete-20260604
```

관측 결과:

| 항목 | 값 |
| --- | ---: |
| `rse_bl2_decrypted` marker | 13.746초 |
| `rse_bl2_validated` marker | 181.609초 |
| validation delta | 167.863초 |
| CC3XX total accesses | 1,638,400 |
| CC3XX writes / reads | 1,107,380 / 531,020 |
| SHA-256 resets | 32,239 |
| SHA-256 updates | 14,827 |
| SHA-256 update bytes | 560,576 |
| SHA-256 transforms | 8,759 |
| SHA-256 finishes | 4,610 |
| HASH DMA triggers / chunks | 4,628 / 4,881 |
| HASH DMA bytes | 518,360 |
| PKA opcode writes | 10 |
| AES CTR ops / bytes | 291 / 269,237 |
| AES ECB ops / bytes | 12 / 192 |
| CMAC DMA triggers / bytes | 38 / 1,194 |

PKA opcode는 `0x4` 7회, `0x5` 3회뿐이다. 반면 HASH engine은
4,610회 finish되고 SHA-256 state reset은 32,239회 발생한다. 따라서 이
구간의 병목은 PKA/ECDSA가 아니라 LMS/LMOTS 검증이 만드는 작은 SHA-256
operation과 CC3XX hash state save/restore, MMIO polling/access traffic이다.

이 run은 전체 boot 완료 목적이 아니라 validation 관측 목적이므로
`qbox_platform_timeout`으로 끝난다. 하지만 `BL2 image validated successfully`
marker와 `Image 4 loaded from the primary slot` marker까지 확인되어
BL1_2 validation 구간 분석 증거로 충분하다.

저장된 결과는 다음처럼 다시 볼 수 있다.

```bash
python3 scripts/analyze/analyze_qbox_rse_boot_timing.py \
  build/qbox-apollo-fvp/rse-cc3xx-validation-complete-20260604/result.json
```

### CC3XX Register Histogram 추가 결과

`register_read_count`와 `register_write_count` histogram을 CC3XX stats에
추가한 뒤, 현재 권장 option 3A인 local MMIO fast path와 함께 다시 측정했다.

```bash
python3 scripts/run/run_qbox_fvp_rd_aspen_rse.py \
  --skip-build \
  --cc3xx-stats \
  --cc3xx-stats-interval 65536 \
  --cc3xx-local-mmio-fastpath \
  --timeout 230 \
  --ignore-fail-patterns \
  --out-dir build/qbox-apollo-fvp/rse-cc3xx-histogram-local-mmio-20260604

python3 scripts/analyze/analyze_qbox_rse_boot_timing.py --markdown \
  build/qbox-apollo-fvp/rse-cc3xx-histogram-local-mmio-20260604/result.json
```

관측값:

| 항목 | 값 |
| --- | ---: |
| `rse_bl2_decrypted` marker | 13.445초 |
| `rse_bl2_validated` marker | 166.329초 |
| validation delta | 152.884초 |
| CC3XX total accesses | 1,638,400 |
| CC3XX writes / reads | 1,107,380 / 531,020 |
| HASH DMA triggers / chunks | 4,628 / 4,881 |
| HASH DMA bytes | 518,360 |
| SHA-256 resets / finishes | 32,239 / 4,610 |
| SHA-256 transforms | 8,759 |
| PKA opcode writes | 10 |
| crypto engine writes | 69,839 |

상위 register read offset:

| Offset | Register | Count |
| --- | --- | ---: |
| `0x910` | `CRYPTO_BUSY` | 139,674 |
| `0x640` | `HASH_H[0]` | 32,239 |
| `0x644` | `HASH_H[1]` | 32,239 |
| `0x648` | `HASH_H[2]` | 32,239 |
| `0x64c` | `HASH_H[3]` | 32,239 |
| `0x650` | `HASH_H[4]` | 32,239 |
| `0x654` | `HASH_H[5]` | 32,239 |
| `0x658` | `HASH_H[6]` | 32,239 |
| `0x65c` | `HASH_H[7]` | 32,239 |
| `0x7c0` | `HASH_CONTROL` | 32,239 |
| `0x688` | `ENV_APBSC_PPROT_OVERRIDE` | 27,629 |
| `0x7cc` | `HASH_CUR_LEN0` | 27,629 |

상위 register write offset:

| Offset | Register | Count |
| --- | --- | ---: |
| `0x684` | `AUTO_HW_PADDING` | 73,698 |
| `0x900` | `CRYPTO_CTL` | 69,839 |
| `0x640` | `HASH_H[0]` | 69,088 |
| `0x644` | `HASH_H[1]` | 69,088 |
| `0x648` | `HASH_H[2]` | 69,088 |
| `0x64c` | `HASH_H[3]` | 69,088 |
| `0x650` | `HASH_H[4]` | 69,088 |
| `0x654` | `HASH_H[5]` | 69,088 |
| `0x658` | `HASH_H[6]` | 69,088 |
| `0x65c` | `HASH_H[7]` | 69,088 |
| `0x818` | `HASH_CLK_ENABLE` | 69,088 |
| `0x688` | `ENV_APBSC_PPROT_OVERRIDE` | 64,478 |

이 결과는 status polling만 줄이는 방식의 상한이 낮다는 것을 보여준다.
write traffic이 read보다 두 배 이상 많고, 상위 write가 모두 HASH state
save/restore와 engine control에 몰려 있다. 따라서 다음 대형 개선은
read-only status fast path가 아니라 QEMU-native CC3XX backend 또는
BL1_2 한정 CC3XX hash state 유지 방식이어야 한다.

## CC3XX Register Polling/Write 개선 검토

TF-M CC3XX driver의 busy-wait 지점은 세 곳이다.

| 파일 | 위치 | Register | 의미 |
| --- | --- | --- | --- |
| `low_level_driver/src/cc3xx_engine_state.c` | `cc3xx_lowlevel_set_engine()` | `cc_ctl.crypto_busy` | engine 전환 전후 busy wait |
| `low_level_driver/src/cc3xx_dma.c` | `wait_for_dma_complete()` | `host_rgf.host_rgf_irr` | DMA 완료 interrupt bit polling |
| `low_level_driver/src/cc3xx_hash.c` | `cc3xx_lowlevel_hash_finish()` | `cc_ctl.hash_busy` | hash finish 후 idle wait |

QBox CC3XX model은 이 register들을 이미 즉시 완료 상태로 만든다.
`CRYPTO_CTL` write 후 `CRYPTO_BUSY=0`, `HASH_BUSY=0`,
`HOST_CC_IS_IDLE=1`을 저장하고, DMA length write 후 `HOST_RGF_IRR`에
완료 interrupt를 세팅한다. 따라서 현재 병목은 QBox model이 실제 시간을
소모하며 기다리는 문제가 아니다. 게스트가 ready 값을 확인하기 위해 발생시키는
MMIO read/write가 모두 QEMU -> SystemC thread -> TLM target 경계를 통과하는
것이 비용이다.

이를 확인하기 위해 다음 trace를 수행했다. 이 run은 pattern 확인용이므로
70초 timeout으로 종료된다.

```bash
QBOX_RDASPEN_CC3XX_TRACE=true \
QBOX_RDASPEN_CC3XX_TRACE_FILTER=crypto \
QBOX_RDASPEN_CC3XX_TRACE_LIMIT=240 \
python3 scripts/run/run_qbox_fvp_rd_aspen_rse.py \
  --skip-build \
  --timeout 70 \
  --ignore-fail-patterns \
  --out-dir build/qbox-apollo-fvp/rse-cc3xx-trace-review-20260604
```

trace 초반에서도 다음 반복 패턴이 보인다.

- `CRYPTO_BUSY` read가 `CRYPTO_CTL` write 앞뒤에 반복된다.
- DMA 설정은 `HOST_RGF_IMR`, `HOST_RGF_ICR`, `DOUT_DST_LLI_WORD*`,
  `DIN_SRC_LLI_WORD*` write 후 `HOST_RGF_IRR` read와 `HOST_RGF_ICR` write로
  완료된다.
- PKA 초기화 경로는 `PKA_DONE`, `PKA_PIPE_RDY`, `PKA_SRAM_*` access가
  많지만 전체 validation stats에서 PKA opcode는 10회뿐이라 주 병목은 아니다.

QBox 내부 SHA padding micro-optimization도 시험했다. `sha256_finish()`에서
padding byte를 한 바이트씩 `sha256_update()`로 넣는 것을 내부 bulk update로
바꾸면 stats상 `sha256_update_calls`는 줄지만, guest-visible MMIO 수는 줄지
않는다.

| Run | `rse_bl2_decrypted` | `rse_bl2_validated` | Delta | CC3XX accesses | SHA update calls |
| --- | ---: | ---: | ---: | ---: | ---: |
| baseline | 13.746초 | 181.609초 | 167.863초 | 1,638,400 | 14,827 |
| padding bulk update | 14.448초 | 184.813초 | 170.365초 | 1,638,400 | 4,881 |

이 결과는 host SHA 구현의 padding overhead가 주 병목이 아님을 보여준다.
남는 큰 항목은 `crypto_engine_writes=69,839`,
`sha256_resets=32,239`, `write_accesses=1,107,380`,
`read_accesses=531,020`이다.

다음으로 QEMU/in-process RSE CPU bridge에서 side-effect 없는 ready/busy status read만
바로 반환하는 opt-in fast path를 시험했다.

```bash
python3 scripts/run/run_qbox_fvp_rd_aspen_rse.py \
  --skip-build \
  --cc3xx-stats \
  --cc3xx-stats-interval 65536 \
  --cc3xx-status-read-fastpath \
  --timeout 230 \
  --ignore-fail-patterns \
  --out-dir build/qbox-apollo-fvp/rse-cc3xx-status-fastpath-20260604
```

이 옵션은 `QBOX_MMIO_READ_FASTPATH`를 통해 RSE CC3XX의 정적 status register
read만 QEMU initiator에서 처리한다. 대상은 `PKA_PIPE_RDY`, `PKA_DONE`,
`AES_BUSY`, `AES_RBG_SEEDING_RDY`, `CLK_STATUS`, `CRYPTO_BUSY`, `HASH_BUSY`,
`HOST_CC_IS_IDLE`, `HOST_SF_READY`, `DIN/DOUT DMA busy`, `FIFO empty`류이다.
`HOST_RGF_IRR`은 DMA 완료 bit와 `HOST_RGF_ICR` clear write에 의해 상태가
변하므로 기본 fast path에서 제외했다.

| Run | `rse_bl2_decrypted` | `rse_bl2_validated` | Delta | CC3XX accesses | Reads | Writes |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| baseline | 13.746초 | 181.609초 | 167.863초 | 1,638,400 | 531,020 | 1,107,380 |
| status-read fast path | 14.248초 | 181.408초 | 167.160초 | 1,507,328 | 389,941 | 1,117,387 |

결론은 두 가지다.

- fast path는 실제로 적용되었다. CC3XX SystemC target까지 내려가는 read가
  약 141,079회 줄었다.
- BL2 validation delta는 약 0.7초만 줄었다. 병목의 대부분은 read polling이
  아니라 hash setup/update/finish 과정에서 발생하는 write traffic과 QEMU
  process 안의 MMIO callback 자체에 남아 있다.

따라서 안전한 option 2는 기본 off인 계측/iteration 보조 옵션으로 유지할 수
있지만, 큰 폭의 단축에는 QEMU-side CC3XX backend 또는 local fast MMIO path가
필요하다.

Option 3의 첫 구현으로 QEMU-local direct MMIO fast path를 추가했다. 이 방식은
`QBOX_MMIO_DIRECT_FASTPATH_RANGES=0x50154000:0x2000`으로 RSE CC3XX window를
지정하고, 해당 range의 read/write를 QEMU callback 안에서 직접 TLM target으로
호출한다. CC3XX register model, HASH/AES/CMAC/PKA side effect, DMA helper는
기존 SystemC CC3XX model을 그대로 사용하고 `run_on_sysc()` bridge만 우회한다.

```bash
python3 scripts/run/run_qbox_fvp_rd_aspen_rse.py \
  --skip-build \
  --cc3xx-stats \
  --cc3xx-stats-interval 65536 \
  --cc3xx-local-mmio-fastpath \
  --timeout 230 \
  --ignore-fail-patterns \
  --out-dir build/qbox-apollo-fvp/rse-cc3xx-local-mmio-fastpath-20260604
```

`--cc3xx-status-read-fastpath`와 같이 켠 상한도 측정했다.

```bash
python3 scripts/run/run_qbox_fvp_rd_aspen_rse.py \
  --skip-build \
  --cc3xx-stats \
  --cc3xx-stats-interval 65536 \
  --cc3xx-local-mmio-fastpath \
  --cc3xx-status-read-fastpath \
  --timeout 230 \
  --ignore-fail-patterns \
  --out-dir build/qbox-apollo-fvp/rse-cc3xx-local-mmio-status-fastpath-20260604
```

| Run | `rse_bl2_decrypted` | `rse_bl2_validated` | Delta | `rse_image_4_loaded` | CC3XX accesses | Reads | Writes |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| baseline | 13.746초 | 181.609초 | 167.863초 | 219.431초 | 1,638,400 | 531,020 | 1,107,380 |
| status-read fast path | 14.248초 | 181.408초 | 167.160초 | 219.435초 | 1,507,328 | 389,941 | 1,117,387 |
| local MMIO fast path | 14.046초 | 170.161초 | 156.115초 | 208.286초 | 1,638,400 | 531,020 | 1,107,380 |
| local MMIO + status-read | 13.546초 | 164.867초 | 151.321초 | 202.092초 | 1,507,328 | 389,941 | 1,117,387 |
| qemu-native + direct MMIO | 12.545초 | 145.884초 | 133.339초 | 147.389초 | 1,769,472 | 620,812 | 1,148,660 |

판단:

- `--cc3xx-local-mmio-fastpath`는 CC3XX access count와 주요 crypto counter를
  baseline과 같게 유지하면서 BL2 validation delta를 약 11.748초 줄인다.
  따라서 option 3의 현재 권장 구현이다.
- `--cc3xx-local-mmio-fastpath --cc3xx-status-read-fastpath` 조합은 약
  16.542초 줄어 가장 빠르다. 하지만 status-read path는 PKA/AES operation mix가
  baseline과 달라지므로 debug iteration 전용으로 둔다.
- 둘 다 `BL2 image validated successfully`, `Jumping to BL2`,
  `Image 4 loaded from the primary slot` marker를 유지했다. 이 run들은
  230초 timeout으로 끝나며 full-system completion 증거가 아니라 RSE validation
  performance evidence이다.
- `--cc3xx-qemu-native-backend`는 같은 marker를 유지하면서 local-MMIO
  status-read fast path 대비 validation delta를 151.321초에서 133.339초로
  줄였다. 이 옵션은 QEMU-native backend와 `0x50154000:0x2000` direct MMIO fast
  path를 같이 사용한다.

### QBox 측 후보

| 후보 | 기대 효과 | 적용 판단 |
| --- | --- | --- |
| QEMU-side CC3XX MMIO backend | SystemC 왕복 없이 QEMU memory region callback 안에서 CC3XX register access 처리 | 가장 효과적인 QBox 구조 개선 후보. 기존 SystemC CC3XX와 동일 register side effect를 공유하거나 이식해야 하므로 작업량은 큼 |
| QEMU/in-process RSE CPU bridge status-read fast path | 항상 ready인 `CRYPTO_BUSY`, `HASH_BUSY`, `HOST_CC_IS_IDLE`, DMA busy/interrupt read를 QEMU 측에서 바로 반환 | polling read 비용을 줄일 수 있음. 단, side-effect 없는 read-only ready register로 범위를 제한해야 함 |
| CC3XX register access histogram | offset별 read/write hot spot을 stats에 추가 | 구현 우선순위 결정을 위한 저위험 계측. 먼저 적용 가능 |
| CC3XX model 내부 micro-optimization | `load32/store32`, stats write, SHA padding 등 C++ 내부 비용 축소 | 안전하지만 이미 효과가 제한적임을 확인 |
| CC3XX DMI | QEMU가 register window를 직접 읽고 씀 | 일반 적용 금지. side-effect register를 우회해 fidelity가 깨진다. read-only status alias 실험 정도만 가능 |

### Firmware 측 후보

QBox만으로는 guest가 이미 발생시킨 write 수를 없앨 수 없다. 큰 폭의 감소는
TF-M/mbedTLS가 작은 SHA operation을 덜 만들게 해야 한다.

| 후보 | 기대 효과 | 적용 판단 |
| --- | --- | --- |
| LMOTS hash coalescing | 5회 `psa_hash_update()`를 1회 `psa_hash_compute()`/bulk input으로 축소 | 암호 결과는 유지하면서 CC3XX state save/restore traffic 감소. provisioning/OTP 재생성 경로가 정리되면 1순위 |
| BL1_2 한정 persistent hash | PSA hash operation 동안 CC3XX state를 유지 | traffic 감소 가능. driver semantics 변경 위험이 있어 BL1_2/QBox 전용 옵션으로만 검토 |
| known-good LMS fast verify | signature verify 자체를 known-good tuple로 shortcut | 가장 빠르지만 secure boot 검증을 우회하므로 debug iteration 옵션 전용 |

### 권장 순서

1. CC3XX stats에 register offset histogram을 추가해서 `CRYPTO_BUSY`,
   `HOST_RGF_IRR`, `HASH_H`, `PKA_DONE`, `DIN/DOUT_*`의 실제 비중을 분리한다.
2. QEMU/in-process RSE CPU 쪽에서 read-only ready status fast path를 opt-in으로
   구현할 수 있는지 확인한다. 이 방식은 register model의 write side effect를
   유지하면서 polling read의 SystemC 왕복만 줄이는 방향이다.
3. 장기적으로는 CC3XX를 QEMU-side MMIO backend로 옮기거나, QEMU callback에서
   SystemC CC3XX core를 직접 호출하는 local fast MMIO path를 만든다.
4. 큰 폭의 validation 시간 단축이 필요하면 TF-M LMOTS hash coalescing을
   별도 firmware option으로 다시 진행한다. 단, BL1_1/BL1_2/provisioned OTP가
   같은 build 결과로 맞춰지는 재생성 경로를 먼저 안정화해야 한다.

## 구간별 Stub 가능성

| 구간 | 가능성 | 권장 방향 |
| --- | --- | --- |
| BL1_2 BL2 validation | 가능하지만 opt-in debug 전용이어야 함 | QBox CC3XX/LMS fast-path를 우선 검토. 더 단순한 TF-M validation skip은 secure-boot 의미를 깨므로 completion 증거에는 사용하지 않음 |
| RSE BL2 image load | stub 대상 아님 | range-limited flash DMI, read-array cache, larger read batching 등 storage fast-path |
| RSE runtime handoff 이후 AP firmware/Linux | RSE stub 대상 아님 | TF-A/U-Boot/Linux 쪽에서 별도 분석 |

## Stats 기반 속도 개선 검토

CC3XX stats는 개선 대상을 명확히 좁힌다.

- PKA는 병목이 아니다. Validation 관측 run에서 PKA opcode write는 10회뿐이다.
- AES/CMAC도 주 병목이 아니다. AES CTR은 image decrypt/load 경로에 보이지만
  `rse_bl2_decrypted` 이후 validation 구간의 지배 비용은 아니다.
- 지배 비용은 작은 SHA-256 operation을 수천 회 수행하는 LMS/LMOTS 검증과,
  그때마다 발생하는 CC3XX register/state traffic이다.
- SHA-256 transform 자체는 8,759회로 host CPU 관점에서 큰 수가 아니다.
  167초의 핵심은 transform 연산량보다 1,638,400회의 MMIO/TLM access와
  `setup/update/finish/uninit` 반복이다.

따라서 개선 방향은 다음 순서가 적절하다.

| 우선순위 | 방법 | 기대 효과 | Fidelity 영향 | 판단 |
| --- | --- | --- | --- | --- |
| 1 | QEMU-local direct MMIO fast path | QEMU -> SystemC scheduler bridge를 줄임 | CC3XX register side effect는 유지. SystemC thread ownership 우회가 있으므로 opt-in 유지 | 구현 및 검증 완료 |
| 2 | QEMU-native CC3XX backend/core 분리 | register access에서 TLM/SystemC target dispatch까지 제거 | 구조 변경 큼. CC3XX side effect와 DMA semantics를 보존해야 함 | 구현 및 RSE marker/timing 검증 완료 |
| 3 | BL1_2 한정 CC3XX PSA hash persistent mode | 작은 hash compute마다 발생하는 HASH state save/restore traffic 감소 | CC3XX driver 동작 변경. BL1_2 단일-thread 조건에 한정해야 함 | QEMU-native backend와 병행 검토 |
| 4 | 남은 LMS/LMOTS hash 입력 coalescing | leaf/public/internal hash 같은 비-hot update 분할 감소 | 암호학적 결과는 동일. 효과는 제한적 | 현재 hot loop는 이미 `psa_hash_compute()` 사용 |
| 5 | known-good LMS fast verify | BL2 image hash, ROTPK, signature tuple이 일치할 때 검증 결과를 바로 반환 | secure-boot negative/FWU/provisioning 검증에는 부적합 | debug iteration 전용 |

### 1순위: QEMU-local Direct MMIO Fast Path

`--cc3xx-local-mmio-fastpath`는 이미 구현되어 있다. RSE CC3XX range
`0x50154000:0x2000`을 `QBOX_MMIO_DIRECT_FASTPATH_RANGES`에 넣고, QEMU
callback 안에서 기존 CC3XX TLM target을 직접 호출한다. secure boot 검증을
skip하지 않고, register side effect와 DMA 처리는 기존 CC3XX model을 그대로
사용한다.

검증 결과:

| Run | Validation delta | 판단 |
| --- | ---: | --- |
| baseline | 167.863초 | 기준 |
| local MMIO fast path | 156.115초 | access count 유지, 약 11.748초 단축 |
| histogram 재측정 local MMIO | 152.884초 | 같은 marker 유지, register hotspot 확인 |

따라서 현재 기본 fidelity를 유지하면서 바로 쓸 수 있는 권장 옵션은
`--cc3xx-local-mmio-fastpath`이다. `--cc3xx-status-read-fastpath`는 read
traffic 일부를 줄이지만 효과가 작고 operation mix 차이가 생기므로 debug
iteration 보조 옵션으로 둔다.

### 2순위: QEMU-native CC3XX Backend

register histogram은 다음 backend가 처리해야 할 hot register를 확정한다.
최소 구현 단위는 `CRYPTO_CTL`, `AUTO_HW_PADDING`, `HASH_CONTROL`,
`HASH_CUR_LEN*`, `HASH_H*`, `HOST_RGF_IRR/ICR`, DMA trigger register와
PKA SRAM access이다.

구현은 중복 모델을 새로 복사하지 않고 현재 SystemC CC3XX의
register/DMA/crypto state machine을 `cc3xx_core`로 분리했다. SystemC wrapper와
QEMU `MemoryRegionOps` wrapper가 같은 core를 호출하므로 reset value,
busy/idle bit, interrupt clear, DMA complete, PKA SRAM 동작이 갈라지지 않는다.

RSE 단독 검증 결과는 다음과 같다.

```text
build/qbox-apollo-fvp/cc3xx-qemu-native-20260605-001939/rse/result.json
```

| 기준 | 결과 |
| --- | --- |
| `rse_bl2_decrypted` | 12.545초 |
| `rse_bl2_validated` | 145.884초 |
| validation delta | 133.339초 |
| `rse_image_4_loaded` | 147.389초 |
| `rse_first_image_slot` | 185.447초 |
| backend label | `qemu-native` |
| direct MMIO range | `0x50154000:0x2000` |

full-system 검증에서는 같은 backend로 Linux login과 post-login probe까지
통과했다.

```text
build/qbox-apollo-fvp/cc3xx-qemu-native-20260605-003557/full/result.json
passed: true
blocker: null
runtime_elapsed_s: 207.416
```

full-system run의 BL2 validation delta는 127.195초였다. direct-boot guardrail은
`build/qbox-apollo-fvp/direct-guardrail-20260605-004025/result.json`에서
`passed: true`로 확인했다.

2026-06-08 재측정에서는 `--rse-lms-accel`과 fast alias preset을 함께 사용해
BL1_2 LMS validation 구간 자체는 약 0.1초 수준으로 줄었다. 이 상태에서
남는 시간은 BL2 이후 SI/AP image load, PS/ITS storage initialization, RSE-SCP
handoff 전후의 flash/storage/CC3XX DMA traffic이다. 가장 빠른 관측 run은
다음이다.

```bash
python3 scripts/run/run_qbox_fvp_rd_aspen_rse.py \
  --skip-build \
  --cc3xx-qemu-native-backend \
  --rse-lms-accel \
  --rse-fast-boot-aliases \
  --timeout 60 \
  --ignore-fail-patterns \
  --out-dir build/qbox-apollo-fvp/rse-step1-storage-direct-fastpath-20260608-1
```

| Marker | 시간 |
| --- | ---: |
| `rse_bl1_1` | 3.211초 |
| `rse_bl2_decrypted` | 11.537초 |
| `rse_bl2_validated` | 11.637초 |
| `rse_image_4_loaded` | 12.339초 |
| `rse_image_3_loaded` | 21.765초 |
| `rse_image_2_loaded` | 22.769초 |
| `rse_image_0_loaded` | 25.779초 |
| `rse_first_image_slot` | 25.879초 |

이 run은 `qbox_platform_timeout`으로 끝나는 RSE timing smoke이며 full-system
completion 증거는 아니다. 하지만 RSE boot time 비교에는 현재 가장 좋은
QBox-side 성능 기준이다.

### 2.5순위: BL2 Image-Level Semantic Accelerator

BL2 image load 구간에서는 `boot_enc_decrypt`와 `bootutil_img_hash` entry hook을
사용한 semantic accelerator를 시험했다. 이 방식은 guest가 수행하는
MCUBoot TLV traversal, `bootutil_verify_sig`, security counter check를 유지하고,
반복적인 AES-CTR decrypt/hash DMA만 QEMU host memory에서 처리한다.

초기 `bootutil_img_hash` accelerator는 hash 대상 이미지가 분할된 direct-file
alias 창에 걸쳐 있어 단일 DMI/direct alias 범위로 읽지 못했다. 증상은
`bl2_img_hash_accel.hits=0`, `dmi_failures=22159`였다.
`hotpath_read_bytes_or_alias()`에 4KB 단위 chunk fallback을 추가한 뒤 같은
image hash가 분할 alias를 따라 읽히도록 고쳤다.

검증 결과:

| Run | 결과 |
| --- | --- |
| `rse-bl2-symbol-img-hash-accel-smoke-20260608` | pre-fix, `hits=0`, `dmi_failures=22159` |
| `rse-bl2-img-hash-chunked-rebuilt-smoke5-20260608` | fixed, `hits=3`, `bytes=1116786`, `direct_file_alias_hits=3`, `dmi_failures=0`, `rse_first_image_slot=31.510초` |
| `rse-bl2-boot-enc-img-hash-combined-smoke-20260608` | combined, `rse_first_image_slot=28.585초`, `boot_enc decrypt_hits=1206`, `img_hash hits=3` |

`boot_enc`와 `img_hash` accelerator는 기능적으로 동작하지만 현재 최단 시간은
storage direct fast path 단독 조합보다 빠르지 않았다. 따라서 이 옵션은
“정확한 함수 entry hook 기반 semantic accelerator가 안전하게 동작하는지”를
검증하는 후보로 유지하고, 기본 추천 preset은 qemu-native CC3XX + LMS accel +
fast aliases + storage direct fast path로 둔다.

`bootutil_verify_sig()` safe accelerator도 같은 조합에서 재확인했다.

```bash
python3 scripts/run/run_qbox_fvp_rd_aspen_rse.py \
  --skip-build \
  --cc3xx-qemu-native-backend \
  --rse-lms-accel \
  --rse-fast-boot-aliases \
  --rse-bl2-load-profile \
  --rse-bl2-boot-enc-accel \
  --rse-bl2-img-hash-accel \
  --rse-bl2-verify-sig-accel \
  --qbox-perf-profile \
  --timeout 90 \
  --ignore-fail-patterns \
  --out-dir build/qbox-apollo-fvp/rse-bl2-image-all-safe-accel-smoke-20260608
```

결과는 `verify_matches=3`, `cache_hits=2`, `cache_misses=1`,
`verify_failures=0`으로 host-native ECDSA 검증은 성공했다. 하지만 기본
safe mode는 guest firmware의 `bootutil_verify_sig()` 실행을 유지하므로
`PKA_OPCODE=72899`, `PKA_PIPE_RDY=72899`, `PKA_DONE=28266`이 그대로 남았다.
`rse_bl1_1` -> `rse_first_image_slot`도 25.986초로 최단 run보다 느렸다.
따라서 `--rse-bl2-verify-sig-accel`은 현재는 “semantic accelerator 내부에
사용할 검증 primitive”로 유지하고, 독립 safe mode만으로는 성능 개선 후보로
보지 않는다.

### 3순위: BL1_2 한정 Persistent Hash Mode

1순위 후에도 충분하지 않으면 CC3XX PSA hash driver에 BL1_2/QBox 전용
compile-time option을 두고, 하나의 hash operation 동안 engine을 유지하는
방법을 검토한다.

주의할 점:

- 일반 TF-M runtime이나 multi-client crypto service에는 적용하면 안 된다.
- `psa_hash_clone()`, `psa_hash_abort()`, nested hash operation이 있으면
  깨질 수 있으므로 BL1_2 LMS 검증 경로에 한정해야 한다.
- 이 방법은 CC3XX driver의 state save/restore semantics를 바꾸므로,
  1순위보다 fidelity risk가 크다.

### 4순위: 남은 LMS/LMOTS Hash Coalescing

현재 Apollo TF-M에서 사용되는 fetched mbedTLS source를 확인한 결과,
가장 뜨거운 `mbedtls/library/lmots.c`의 `hash_digit_array()` 내부 반복은 이미
다음 형태로 contiguous input을 구성해 `psa_hash_compute()`를 호출한다.

```text
hash_input = I || q || i || j || tmp_hash
psa_hash_compute(PSA_ALG_SHA_256, hash_input, hash_input_len, ...)
```

따라서 이전에 가정했던 “hot loop의 5회 `psa_hash_update()`를 1회로
합치기”는 이 트리에서는 이미 적용되어 있다. 남은
`create_digit_array_with_checksum()`, `public_key_from_hashed_digit_array()`,
LMS Merkle leaf/internal hash는 coalescing할 수 있지만 호출 수가 훨씬 작다.
새 histogram의 69,839회 `CRYPTO_CTL` write와 69,088회 `HASH_H*` write를
줄이려면, firmware 함수 입력 병합보다 CC3XX driver/backend의 state
save/restore 구조를 줄이는 쪽이 우선이다.

### 5순위: Known-good LMS Fast Verify

가장 빠른 방법은 `pq_crypto_verify()` 또는 LMS verify 결과를 known-good
tuple 기준으로 바로 성공 처리하는 것이다. 하지만 이는 signature 검증 자체를
우회하므로 full-system completion 증거에는 사용하지 않는다.

## FVP 수준 접근을 위한 QBox 수정 중심 제안

남은 gap을 줄이기 위한 우선순위는 다음과 같다.

| 순서 | 제안 | 기대 효과 | 검증 방법 | 주의점 |
| --- | --- | --- | --- | --- |
| 1 | qemu-native CC3XX backend의 DMA/memory path 확대 | CC3XX register callback 안에서 DMI cache miss와 TLM fallback을 더 줄임 | `qemu-cc3xx-profile.json`의 `tlm_*`, `address_space_*`, callback ns 감소 확인 | CC3XX DMA side effect와 interrupt clear 순서를 유지해야 함 |
| 2 | RSE PS/ITS storage direct path 정식화 | runtime handoff 전 storage byte access의 `run_on_sysc()` 왕복 제거 | `--rse-fast-boot-aliases` smoke에서 `rse_image_*` delta와 PS/ITS marker 비교 | FWU, persistence, negative storage test에는 opt-in으로만 사용 |
| 3 | direct-file alias chunk reader를 image load/hash 공통 경로로 유지 | 분할 alias image를 host memory에서 직접 처리 | `bl2_img_hash_accel.dmi_failures=0`, direct alias hit 확인 | write side effect가 필요한 flash command 경로에는 사용 금지 |
| 4 | CC3XX PKA/P-256 path의 함수 단위 accelerator | BL2 image signature 검증이 만드는 72k PKA opcode/polling traffic 제거 | `pka_opcode_writes`, `PKA_PIPE_RDY`, `PKA_DONE` 감소와 `verify_matches` 확인 | 검증 실패를 성공으로 바꾸면 안 되며 skip은 positive smoke 전용 |
| 5 | BL2 image-load 함수 단위 semantic accelerator 확장 | AP/SI image decrypt/hash/copy/verify 반복을 QEMU host memory에서 batch 처리 | `bl2_load_profile.sites.*.hits`, image marker, hash/signature marker 유지 확인 | secure boot result를 강제 성공시키면 안 됨 |
| 6 | qbox RemotePass/DMI cache와 router lookup hot path 계측 | 아직 남은 TLM 경계 비용을 정량화 | `rse-hotpath-profile.json`, `qemu-cc3xx-profile.json`, router cache stats 추가 | 계측 overhead와 실제 개선을 분리해야 함 |
| 7 | negative secure-boot/FWU/persistence 전용 slow-fidelity profile 유지 | 빠른 preset으로 놓치는 fidelity debt 방지 | 빠른 preset off 상태의 기존 full-system/FWU 검증 | FVP 동등성 최종 증거는 fast preset만으로 주장하지 않음 |

현 시점에서 바로 권장하는 RSE 부팅 시간 비교 command는 다음이다.

```bash
python3 scripts/run/run_qbox_fvp_rd_aspen_rse.py \
  --skip-build \
  --cc3xx-qemu-native-backend \
  --rse-lms-accel \
  --rse-fast-boot-aliases \
  --qbox-perf-profile \
  --timeout 90 \
  --ignore-fail-patterns \
  --out-dir build/qbox-apollo-fvp/rse-fast-boot-perf-<run-id>
```

BL2 image-level accelerator까지 같이 시험할 때는 다음을 추가한다.

```text
--rse-bl2-load-profile
--rse-bl2-boot-enc-accel
--rse-bl2-img-hash-accel
--rse-bl2-verify-sig-accel
```

단, `--rse-bl2-verify-sig-accel`은 기본 safe mode에서 guest ECDSA/PKA 검증을
그대로 실행한다. 성능 개선을 내려면 다음 단계에서 `bootutil_verify_sig()`를
skip하는 것이 아니라, `boot_load_image_to_sram()` semantic accelerator 내부에서
header/TLV/hash/ECDSA/encryption TLV를 host에서 모두 검증한 뒤 guest-visible
상태를 반영하는 구조로 통합해야 한다.

목표 완료 기준은 FVP의 `rse_bl1_1` -> `rse_first_image_slot` 4.818초에 대해
QBox가 2배 이내, 즉 약 10초 이하로 들어오는 것이다. 그 전 단계의 실용적
milestone은 현재 22.668초를 15초 이하로 낮추는 것이다.

사용 가능한 조건:

- QBox iteration speed 전용 옵션으로 기본값 off
- BL2 image protected values hash, ROTPK, signature, LMS/LMOTS parameter가
  모두 예상값과 일치할 때만 enable
- 결과 JSON과 summary에 fidelity debt를 명시
- secure boot negative test, FWU, provisioning, storage/CFI fidelity test에서는
  자동 비활성화

## 권장 설계

1. 기본 full-system runner는 RSE-first firmware chain을 유지한다.
2. RSE boot timing marker는 항상 `result.json`에 기록한다.
3. BL1_2 validation 구간은 다음 순서로 좁혀 간다.
   - CC3XX stats로 HASH DMA, SHA-256 reset/update/finish, PKA opcode,
     AES/CMAC 호출 수를 확인한다.
   - 현재 결과처럼 HASH/SHA가 지배적이고 PKA가 미미하면, TF-M 전체 skip보다
     LMS/LMOTS 검증에 한정된 fast verify 또는 CC3XX hash operation cache를
     우선 검토한다.
   - fast-path는 BL2 image hash, ROTPK, signature, LMS/LMOTS parameter가
     예상값과 일치할 때만 허용한다.
   - fast-path가 켜진 결과에는 별도 fidelity debt를 기록하고, secure boot
     negative test, FWU, provisioning, storage/CFI fidelity 검증에서는
     자동으로 비활성화한다.
4. Image load 구간은 stub 대신 `--range-limited-flash-dmi`와 flash stats로
   효과를 비교한다.

## Option 3 구현 계획: QEMU-side CC3XX Backend

상세 구현 스펙, 디자인, 계획, task backlog는 다음 문서를 기준으로 한다.

- [QEMU-native CC3XX Backend Spec](qbox-cc3xx-qemu-native-spec-ko.md)
- [QEMU-native CC3XX Backend Design](qbox-cc3xx-qemu-native-design-ko.md)
- [QEMU-native CC3XX Backend Implementation Plan](qbox-cc3xx-qemu-native-plan-ko.md)
- [QEMU-native CC3XX Backend Tasks](qbox-cc3xx-qemu-native-tasks-ko.md)

목표는 RSE CC3XX register window를 QEMU/in-process RSE CPU 경로에서 처리해
SystemC thread 왕복을 제거하는 것이다. 첫 단계인
`--cc3xx-local-mmio-fastpath`와 두 번째 단계인
`--cc3xx-qemu-native-backend`가 구현되어 있다. Firmware-visible register
semantics와 DMA 결과는 현재 SystemC CC3XX model에서 분리한 공통 core를
공유하며, secure boot 검증 자체는 우회하지 않는다.

이 작업은 두 단계로 나눈다.

| 단계 | 형태 | 의미 |
| --- | --- | --- |
| 3A | QEMU-local direct MMIO fast path | 현재 구현. QEMU callback 안에서 기존 SystemC CC3XX target의 `b_transport()`를 직접 호출해 `run_on_sysc()` bridge를 줄인다. 모델 중복이 없고 안전하지만 여전히 TLM payload와 SystemC target 코드는 탄다. |
| 3B | QEMU-native CC3XX backend | 구현 완료. QEMU `MemoryRegionOps` callback 안에서 공통 `cc3xx_core` register/DMA state machine을 호출한다. |

### 설계 원칙

1. QEMU memory region callback 안에서 CC3XX register read/write를 처리한다.
2. 현재 `tools/qbox/systemc-components/cc3xx/include/cc3xx.h`에 들어 있는
   register state, AES/SHA/CMAC/PKA side effect, stats 로직을 dependency-free
   `cc3xx_core`로 분리하고 SystemC/QEMU wrapper가 이 core를 공유한다.
3. register access는 QEMU process local 함수 호출로 끝내고, DMA source/dest
   memory access만 QEMU address space 또는 필요한 TLM bridge를 사용한다.
4. `HOST_RGF_IRR`, `HOST_RGF_ICR`, HASH state register, PKA SRAM처럼 side
   effect가 있는 register는 read-only fast path가 아니라 backend core가
   처리한다.
5. 기본 full-system completion 경로에서는 secure boot negative test가 가능한
   fidelity를 유지한다. known-good signature skip과는 분리한다.

### QEMU-native Backend 설계

QBox에는 QEMU memory region callback을 감싸는 C++ API가 이미 있다.
`tools/qbox/qemu-components/common/src/libqemu-cxx/memory.cc`의
`MemoryRegion::init_io()`와 `MemoryRegionOps::set_read_callback()`,
`set_write_callback()`을 사용하면 QEMU-side MMIO region을 만들 수 있다.

권장 구조는 CC3XX 동작을 공통 core와 wrapper로 분리하는 것이다.

```text
cc3xx_core
  - register file
  - HASH/AES/CMAC/PKA state machine
  - HOST_RGF_IRR/ICR, busy/idle, DMA complete side effect
  - stats and optional register histogram
  - memory read/write callback interface

SystemC wrapper
  - tlm target_socket
  - sc_time/delay handling
  - current platform wiring compatibility

QEMU wrapper
  - qemu::MemoryRegionOps read/write callbacks
  - QEMU address-space backed DMA callback
  - optional bridge DMA callback for memory not local to QEMU
```

이 방식이면 SystemC와 QEMU backend가 register semantics를 공유한다. 단순히
현재 `cc3xx.h`를 복사해서 QEMU device를 만들면 빠르게 실험할 수는 있지만,
두 모델의 reset value, status clear, DMA complete, PKA SRAM 동작이 쉽게
갈라진다. 장기 유지보수와 negative secure-boot test를 생각하면 공통 core가
낫다.

QEMU wrapper의 high-level 흐름은 다음과 같다.

```text
read(offset, size, attrs)
  -> cc3xx_core.read(offset, size)
  -> return MemTxOK or MemTxError

write(offset, value, size, attrs)
  -> cc3xx_core.write(offset, value, size)
     -> if DMA length/start register triggers:
          memory_cb.read(src, bytes)
          crypto/hash/aes operation
          memory_cb.write(dst, bytes)
          set HOST_RGF_IRR / clear busy
  -> return MemTxOK or MemTxError
```

DMA callback는 성능에 결정적이다. RSE BL1_2 validation 구간의 register
access는 1,638,400회이지만 HASH DMA chunk는 4,881회, HASH DMA byte는
518,360바이트다. 따라서 register path를 QEMU-local로 옮기면 매우 많은
왕복을 제거하고, DMA만 coarse-grained memory access로 남길 수 있다. DMA
대상이 QEMU address space에 있으면 `address_space_read/write` 계열을 사용하고,
SystemC 쪽 host window에만 있는 경우에는 그 window에 한해 bridge callback을
쓴다.

### 기대 성능

현재 측정값만으로 정확한 상한을 단정할 수는 없지만, 수치는 우선순위를
분명히 보여준다.

- status-read fast path는 read 141,079회를 줄였지만 validation delta를
  0.703초만 줄였다.
- local MMIO fast path는 access count를 유지한 채 scheduler bridge를 줄여
  11.748초를 줄였다.
- QEMU-native backend는 local MMIO fast path보다 더 들어가서 SystemC target
  dispatch와 wrapper 비용을 줄였고, measured validation delta를 133.339초까지
  낮췄다.

따라서 QEMU-native backend는 RSE BL2 validation을 18초 수준 줄였지만,
FVP 수준의 1.4초에는 아직 멀다. LMS/LMOTS가 만드는 작은 SHA operation 구조
자체가 남아 있기 때문에, QEMU-native backend 이후에도 `sha256_resets`,
`crypto_engine_writes`, `total_accesses`가 충분히 줄지 않으면 LMOTS hash
coalescing 또는 BL1_2 한정 hash-state optimization을 병행해야 한다.

### 단계별 Task

| 단계 | 작업 | 완료 기준 |
| --- | --- | --- |
| 0 | QEMU-local direct MMIO fast path | 완료. RSE CC3XX range `0x50154000:0x2000`이 opt-in으로 direct TLM path를 사용하고 validation delta가 167.863초에서 156.115초로 감소 |
| 1 | CC3XX register offset histogram 추가 | RSE validation run에서 read/write hot offset 상위 목록이 `rse-cc3xx-stats.json`에 기록됨 |
| 2 | CC3XX core 분리 설계 | 완료. SystemC module에서 register/DMA side effect와 TLM wrapper 경계 분리 |
| 3 | QEMU-side backend skeleton | 완료. RSE CC3XX range `0x50154000` read/write가 `MemoryRegionOps` backend로 진입 |
| 4 | DMA memory access 연결 | 완료. HASH/AES/CMAC DMA가 QEMU address space first, TLM fallback 구조 사용 |
| 5 | Crypto/PKA parity | 완료. 기존 `cc3xx-tests`와 core-only tests 통과 |
| 6 | RSE boot 검증 | 완료. `BL2 image decrypted successfully`, `BL2 image validated successfully`, `Jumping to BL2`, SI/AP image load marker 유지 |
| 7 | Full-system 검증 | 완료. `run_qbox_apollo_fvp_full.py --post-login-probe --cc3xx-qemu-native-backend` 결과 `passed: true`, `blocker: null` |

### 위험 및 대응

| 위험 | 대응 |
| --- | --- |
| SystemC CC3XX와 QEMU-side CC3XX의 동작 중복 | 가능한 경우 register/crypto core를 공통 C++ class로 분리하고 SystemC/QEMU wrapper만 다르게 둔다 |
| QEMU iothread와 SystemC thread 소유권 혼재 | backend는 QEMU process local state로 제한하고, SystemC object를 직접 건드리는 방식은 후순위로 둔다 |
| DMA 대상 memory가 SystemC 쪽에만 존재 | RSE local crypto 경로에서 실제 DMA 대상이 QEMU address space에 있는지 histogram/trace로 먼저 확인하고, 필요한 window만 bridge한다 |
| interrupt/status clear semantics 손상 | `HOST_RGF_IRR/ICR`와 DMA complete bit를 단위 테스트와 RSE trace로 검증한다 |
| 성능 개선이 write traffic에 묶여 제한됨 | callback-local 처리 후에도 남는 비용을 stats로 비교해 LMOTS hash coalescing 필요성을 다시 판단한다 |

### 검증 명령

```bash
cmake --build build/local-apollo-fvp/work/qbox-platform \
  --target cc3xx-tests cpu_arm_cortexM55 platforms-vp apollo_fvp_full_system \
  --parallel 8

ctest --test-dir build/local-apollo-fvp/work/qbox-platform \
  -R 'cc3xx-tests' \
  --output-on-failure

python3 scripts/run/run_qbox_fvp_rd_aspen_rse.py \
  --skip-build \
  --cc3xx-stats \
  --cc3xx-stats-interval 65536 \
  --cc3xx-qemu-native-backend \
  --timeout 230 \
  --ignore-fail-patterns \
  --out-dir build/qbox-apollo-fvp/rse-cc3xx-qemu-native-backend-<run-id>
```

성공 판단은 baseline 대비 다음을 모두 만족하는 것이다.

- `rse_bl2_decrypted -> rse_bl2_validated` delta가 local-MMIO fastpath
  baseline보다 10% 이상 낮다.
- `rse_bl2_validated`, `rse_jump_bl2`, SI/AP image load marker가 유지된다.
- secure boot 검증을 skip하지 않았다는 fidelity label이 `result.json`에 남는다.
- `cc3xx-tests`와 RSE runtime stats가 기존 SystemC backend와 기능적으로
  동등하다.

## 2026-06-07 QBox-side Profile 재분석

FVP와 비슷한 RSE 부팅 시간을 목표로 QEMU-native CC3XX 이후의 남은 비용을
분리하기 위해 QBox 내부 profile을 추가했다. 이 계측은 기본 off이며,
`--qbox-perf-profile`을 켰을 때만 wall-clock counter를 기록한다.

```bash
python3 scripts/run/run_qbox_fvp_rd_aspen_rse.py \
  --skip-build \
  --cc3xx-qemu-native-backend \
  --qbox-perf-profile \
  --qbox-perf-profile-interval 65536 \
  --cc3xx-stats-interval 65536 \
  --timeout 230 \
  --ignore-fail-patterns \
  --out-dir build/qbox-apollo-fvp/perf-profile-validation-20260607-224345
```

이 run은 RSE-oriented timeout으로 종료되지만 BL1_2 validation marker까지
도달했다.

| 항목 | 값 |
| --- | ---: |
| `rse_bl2_decrypted` | 12.943초 |
| `rse_bl2_validated` | 155.639초 |
| validation delta | 142.696초 |
| `rse_image_4_loaded` | 189.448초 |
| CC3XX total accesses | 1,638,400 |
| CC3XX reads / writes | 531,020 / 1,107,380 |
| SHA-256 resets / finishes | 32,239 / 4,610 |
| SHA-256 transforms | 8,759 |

QEMU-native CC3XX profile은 register callback 비용과 실제 crypto/DMA 비용을
분리한다.

| 항목 | 값 |
| --- | ---: |
| QEMU CC3XX read / write callbacks | 531,020 / 1,107,380 |
| QEMU CC3XX read / write callback time | 0.197초 / 2.083초 |
| CC3XX address-space read / write hits | 0 / 0 |
| CC3XX TLM read / write hits | 5,345 / 425 |
| CC3XX TLM read / write time | 1.555초 / 0.023초 |
| `sha256_transform_ns` | 0.0036초 |
| `sha256_finish_ns` | 0.0040초 |
| `hash_dma_ns` | 1.545초 |

QEMU initiator와 RemotePass profile은 RSE CPU memory/peripheral path가 아직
큰 비중을 차지함을 보여준다.

| 항목 | 값 |
| --- | ---: |
| `remote_platform.cpu_0.cpu.mem` total accesses | 1,114,112 |
| regular initiator accesses | 1,114,111 |
| regular initiator time | 73.642초 |
| DMI-allowed transactions | 625,691 |
| RemotePass outbound b_transport | 667,497 |
| RemotePass outbound b_transport time | 40.723초 |
| RemotePass outbound DMI requests | 643,223 |
| RemotePass outbound DMI request time | 24.565초 |

판단:

- CC3XX의 SHA/PKA host crypto 자체는 FVP 대비 100배 차이를 만들지 않는다.
  SHA transform/finish는 합쳐도 10ms 미만이고, HASH DMA 처리도 약 1.5초다.
- QEMU-native backend가 register model을 QEMU callback으로 옮겼지만, guest
  firmware는 여전히 LMS/LMOTS 검증과 CC3XX driver state save/restore 코드를
  실제로 실행한다. 따라서 QEMU callback 수 160만 회와 RSE CPU instruction
  실행이 남는다.
- `address_space_*_hits=0`은 CC3XX DMA 대상이 현재 remote QEMU address
  space에 직접 등록되지 않고 TLM fallback으로 처리됨을 의미한다.
- RSE ITCM/DTCM/VM은 설정상 DMI를 허용하지만, profile상 QEMU initiator
  regular path와 RemotePass DMI request가 매우 많다. FVP에 근접하려면 단순
  CC3XX register 최적화보다 RSE CPU memory path의 QEMU-local화가 우선이다.

### QBox 수정 우선순위

1. **RSE TCM/VM QEMU-local shared RAM backend**

   RSE remote process 안에 ITCM, DTCM, VM0, VM1을 QEMU RAM region으로 직접
   등록하고, SystemC `gs_memory`와 같은 shared memory backing을 사용한다.
   `libqemu-cxx`에는 `MemoryRegion::init_ram_ptr(..., fd, fd_offset)`가 이미
   있어 fd-backed RAM region을 만들 수 있다. 목표는 RSE CPU instruction/data
   access와 CC3XX DMA source/destination access를 QEMU address space hit로
   바꾸는 것이다.

   완료 기준:

   - `qemu-cc3xx-profile.json`의 `address_space_*_hits`가 0이 아니고,
     TLM fallback hit가 크게 감소한다.
   - `qemu-initiator` profile의 `regular_ns`와 RemotePass
     `outbound_b_transport_ns`가 현재 73.642초 / 40.723초 대비 크게 줄어든다.
   - RSE BL1_2 validation marker와 SI/AP image load marker가 유지된다.

2. **RemotePass DMI request cache 또는 QEMU alias 안정화**

   현재 DMI request가 643,223회 발생한다. 같은 shared memory range에 대한
   반복 DMI query가 CPU fast path로 충분히 흡수되지 않으면, RemotePass에
   opt-in DMI cache를 추가하거나 QEMU alias 설치 조건을 추적해 반복 request를
   제거한다. 기존 `DMICACHE` 블록은 compile-time off 상태이므로, runtime
   option으로 다시 설계해야 한다.

   완료 기준:

   - RemotePass `outbound_dmi_request`와 `outbound_dmi_request_ns`가 한 자리
     수 수준의 초기 mapping 비용으로 수렴한다.
   - DMI invalidation, shared memory write coherency, read-only alias write
     fallback이 깨지지 않는다.

   Superseded/currently removed: 아래 RemotePass DMI cache option과
   command는 2026-06-21 Apollo RSE local-only 정리 이전의 historical
   comparison evidence다. 현재 Apollo QBox runner에서는 이 option을 제공하지
   않으며, 기본 run guidance로 사용하지 않는다. 1차 구현 당시에는
   `RemotePass`에 runtime opt-in `dmi_cache` CCI parameter와 RSE runner의
   `--remotepass-dmi-cache` option을 추가했다. 35초 smoke에서는 early boot
   marker가 유지되고 cache hit가 발생했다.

   ```bash
   python3 scripts/run/run_qbox_fvp_rd_aspen_rse.py \
     --skip-build \
     --cc3xx-qemu-native-backend \
     --remotepass-dmi-cache \
     --qbox-perf-profile \
     --qbox-perf-profile-interval 1024 \
     --cc3xx-stats-interval 65536 \
     --timeout 35 \
     --ignore-fail-patterns \
     --out-dir build/qbox-apollo-fvp/remotepass-dmi-cache-smoke-20260607-230225
   ```

   | 항목 | cache off | cache on | 변화 |
   | --- | ---: | ---: | ---: |
   | `rse_bl2_decrypted` | 14.045초 | 13.349초 | -0.696초 |
   | QEMU initiator regular time | 3.332초 | 3.072초 | -0.260초 |
   | RemotePass outbound b_transport time | 1.443초 | 1.285초 | -0.157초 |
   | RemotePass outbound b_transport | 11,243 | 10,742 | -501 |
   | RemotePass DMI cache b_transport hits | 0 | 501 | +501 |

   같은 option으로 230초 validation run도 수행했다.

   ```bash
   python3 scripts/run/run_qbox_fvp_rd_aspen_rse.py \
     --skip-build \
     --cc3xx-qemu-native-backend \
     --remotepass-dmi-cache \
     --qbox-perf-profile \
     --qbox-perf-profile-interval 65536 \
     --cc3xx-stats-interval 65536 \
     --timeout 230 \
     --ignore-fail-patterns \
     --out-dir build/qbox-apollo-fvp/remotepass-dmi-cache-validation-20260607-230416
   ```

   | 항목 | cache off | cache on | 변화 |
   | --- | ---: | ---: | ---: |
   | `rse_bl2_decrypted` -> `rse_bl2_validated` | 142.696초 | 142.440초 | -0.256초 |
   | `rse_image_4_loaded` | 189.448초 | 187.796초 | -1.652초 |
   | QEMU initiator regular time | 73.642초 | 75.582초 | +1.940초 |
   | RemotePass outbound b_transport time | 40.723초 | 39.783초 | -0.940초 |
   | RemotePass outbound DMI request time | 24.565초 | 24.195초 | -0.370초 |
   | RemotePass DMI cache b_transport hits | 0 | 800 | +800 |

   이 결과는 DMI cache가 올바른 경로의 보조 최적화임을 보여주지만, hit 수가
   전체 RSE validation workload에 비해 작고 장시간 validation delta 개선도
   1초 미만이다. 따라서 FVP 수준에 근접하는 핵심 작업은 여전히 1번의 RSE
   TCM/VM QEMU-local shared RAM backend이고, DMI cache는 그 작업과 병행 가능한
   보조 option으로 유지한다.

3. **RSE CPU hot-PC / translation-block profile**

   위 두 작업 후에도 validation delta가 10초대 이상이면, 남은 비용은
   QEMU Cortex-M55 TCG가 LMS/LMOTS C code를 실행하는 instruction 비용일
   가능성이 높다. 기존 RSE PC trace는 marker 중심 분석에는 충분하지만
   hot loop 비중을 보기에는 거칠다. QEMU plugin 또는 TB/PC histogram을
   추가해 `lmots.c`, `lms.c`, CC3XX low-level driver loop의 host 시간을
   분리한다.

   완료 기준:

   - `mbedtls_lmots_calculate_public_key_candidate()`,
     `hash_digit_array()`, `cc3xx_hash_*()` 주변 PC가 전체 runtime에서 차지하는
     비중을 JSON으로 기록한다.
   - QBox bridge 최적화 후 남은 비용이 CPU execution인지 다시 판단한다.

4. **QBox opt-in LMS/CC3XX semantic accelerator**

   QBox-only로 FVP의 1.4초 validation delta에 가까워지려면, hardware fidelity
   path와 분리된 debug/iteration 전용 accelerator가 필요할 수 있다. 후보는
   known-good BL2 hash/ROTPK/signature tuple을 기준으로 LMS verify 결과를
   빠르게 반환하거나, CC3XX HASH state save/restore 패턴을 QEMU-side에서
   semantic cache로 흡수하는 방식이다.

   이 옵션은 secure boot negative test, FWU, provisioning 검증에는 사용할 수
   없다. `result.json`에 fidelity debt를 명시하고, 기본 full-system completion
   경로에서는 비활성화해야 한다.

5. **RSE CPU execution backend 개선**

   QEMU Cortex-M55 TCG 실행 자체가 최종 병목으로 확인되면, RSE CPU를 더 빠른
   backend로 대체하거나 TCG translation/cache option을 조정한다. 단, 이는
   QBox 구조 변경이 크고 M-profile exception/NVIC/TrustZone 동작 fidelity에
   직접 영향을 주므로 1-3번 이후에 진행한다.

### 결론

FVP와 비슷한 시간까지 줄이는 가장 현실적인 QBox 수정 경로는
`CC3XX qemu-native` 다음에 `RSE TCM/VM QEMU-local shared RAM backend`를
추가하는 것이다. 이 작업으로 CC3XX DMA fallback과 RemotePass memory traffic을
줄인 뒤에도 BL1_2 validation이 여전히 10초대 이상이면, 그때는
QEMU Cortex-M55 TCG의 LMS/LMOTS instruction 실행을 줄이는 semantic
accelerator를 opt-in debug mode로 분리해 검토한다.

## 2026-06-07 추가 검증: Memory/Hotpath 단독 개선 한계

`CC3XX qemu-native` 이후 남은 병목을 줄이기 위해 DMI translation mask,
CC3XX DMA DMI cache, RSE BL1_1 `memcpy/memset` semantic hotpath를 차례로
검증했다.

```bash
python3 scripts/run/run_qbox_fvp_rd_aspen_rse.py \
  --skip-build \
  --cc3xx-qemu-native-backend \
  --qbox-perf-profile \
  --qbox-perf-profile-interval 65536 \
  --cc3xx-stats-interval 65536 \
  --timeout 190 \
  --ignore-fail-patterns \
  --out-dir build/qbox-apollo-fvp/rse-hotpath-validation-20260607-235536
```

| Run | `rse_bl2_decrypted` | `rse_bl2_validated` | Delta | `rse_image_4_loaded` | QEMU initiator regular | Regular time | RemotePass outbound time | CC3XX DMI cache hit R/W | Hotpath hit memcpy/memset |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Baseline | 12.943초 | 155.639초 | 142.696초 | 189.448초 | 1,114,111 | 73.642초 | 40.723초 | 0 / 0 | 0 / 0 |
| DMI mask fix | 13.450초 | 155.812초 | 142.363초 | 188.599초 | 851,967 | 47.411초 | 25.120초 | 0 / 0 | 0 / 0 |
| CC3XX DMA DMI cache | 13.351초 | 154.563초 | 141.212초 | 187.465초 | 851,967 | 47.285초 | 23.733초 | 5,207 / 149 | 0 / 0 |
| BL1_1 hotpath | 13.238초 | 153.489초 | 140.251초 | 187.485초 | 720,895 | 35.597초 | 17.165초 | 5,207 / 149 | 5,714 / 3,487 |

판단:

- DMI mask fix와 CC3XX DMA DMI cache는 QEMU/SystemC bridge 시간을 줄인다.
  하지만 validation delta 개선은 약 1.5초 수준이다.
- `memcpy/memset` hotpath는 실제로 hit되고 DMI/stack/state 실패가 0이다.
  그런데 validation delta는 baseline 대비 약 2.4초만 줄었다.
- 따라서 FVP의 약 1.4초 validation delta와 비슷하게 만들려면, QBox 외부
  `sync_with_kernel()` 경계에서 일부 loop를 건너뛰는 방식으로는 부족하다.
  남은 핵심은 BL1_2의 LMS/LMOTS 검증 C code 자체를 Cortex-M55 TCG로 장시간
  실행하는 비용이다.

## FVP 근접을 위한 권장 QBox 수정안

### 1순위: Host-side LMS verifier accelerator

FVP에 가장 가깝게 접근할 수 있는 QBox 중심 방법은 BL1_2의
`mbedtls_lms_verify()` 또는 `pq_crypto_verify()` 진입을 QBox/libqemu가
symbol 기반으로 감지하고, guest 메모리의 message/signature/public key를
DMI로 읽어 host-side LMS verifier를 실행한 뒤 AAPCS return value를 R0에
써서 guest PC를 LR로 진행시키는 방식이다.

이 방식은 단순 success stub이 아니라 실제 LMS 검증을 host native code로
수행하므로 positive secure boot 의미를 유지할 수 있다. 다만 QBox-only
accelerator이므로 기본 off, opt-in, 그리고 `result.json` fidelity label에
명시해야 한다.

완료 기준:

- 일반 path와 accelerator path가 같은 BL2 image/signature/key에 대해 같은
  verify 결과를 낸다.
- positive boot에서 `rse_bl2_decrypted -> rse_bl2_validated`가 FVP의
  1.4초에 근접한다.
- negative signature/FWU/provisioning 검증 run에서는 accelerator를 끄거나,
  mismatch가 발견되면 즉시 normal path로 fallback한다.
- symbol 주소는 고정값이 아니라 local build ELF 또는 debug manifest에서
  추출하고, 함수 prologue instruction fingerprint로 빌드 drift를 방어한다.

2026-06-08 구현/검증 상태:

- QBox에 opt-in `--rse-lms-accel` option과 host-side fixed-parameter
  LMS/LMOTS verifier helper를 추가했다. 현재 지원 범위는 TF-M BL1_2에서 쓰는
  `LMS_SHA256_M32_H10` + `LMOTS_SHA256_N32_W8` 조합이다.
- helper는 Mbed TLS `test_suite_lms.data`의 successful vector로 검증했다.
  따라서 host-side 검증 알고리즘 자체는 단순 success stub이 아니다.
- `QemuCpu::sync_with_kernel()` 기반 prototype은 함수 진입 PC를 안정적으로
  잡지 못했다. 45초 RSE smoke 결과:

```json
{
  "lms_accel_enabled": true,
  "lms_verify_addr": "0x11009414",
  "lms_hits": 0,
  "lms_pc_misses": 43008
}
```

- 결론적으로 host-side LMS verifier는 유효한 방향이지만, 현재 QBox 외부
  loop-end callback만으로는 FVP급 개선을 만들 수 없다. 다음 구현은
  libqemu/QEMU 쪽에서 `pq_crypto_verify()` 또는 `mbedtls_lms_verify()` 함수
  진입 시점에 직접 callback을 호출하는 PC-entry hook이어야 한다.
- 권장 hook 지점은 QEMU target/arm TCG translation 또는 TB 시작 경계이다.
  해당 hook은 Thumb PC, CPU object, guest register file 접근, DMI memory read,
  R0/PC update, TB invalidation/exit를 한 함수에서 처리해야 한다. 이 구조가
  들어가면 현재 추가한 host-side LMS verifier를 그대로 재사용할 수 있다.

### 2순위: QEMU TCG-side Thumb hot loop helper

현재 구현한 `QemuCpu` external hotpath는 QEMU loop가 SystemC로 빠져나온 뒤에만
동작한다. 다음 단계는 QEMU ARM M-profile TCG translation 단계에서 BL1_1/BL1_2
`memcpy`, `memset`, 필요 시 LMOTS inner hash loop PC를 감지하고 helper로
치환하는 것이다.

이 방식은 guest 함수 ABI를 덜 건드리지만 QEMU target/arm TCG 코드 수정이
필요하고, symbol-specific 최적화가 되기 쉽다. 따라서 host-side LMS verifier보다
일반성은 높지만 구현 비용과 검증 비용이 크다.

### 3순위: RSE QEMU-local memory backend 완성

ITCM/DTCM/VM을 remote QEMU address space에 shared RAM으로 더 직접 등록하면
RemotePass와 TLM memory traffic을 더 줄일 수 있다. 이미 DMI mask와 DMA DMI
cache로 bridge 비용이 줄어드는 것은 확인했다.

다만 최신 profile에서 memory/bridge 시간을 크게 줄여도 validation delta는
140초대에 남았다. 따라서 이 작업은 필요하지만 FVP 근접의 결정타가 아니라
semantic/TCG accelerator를 받쳐주는 기반 작업으로 분류한다.

### 4순위: CC3XX HASH sequence coalescing/cache

CC3XX backend에서 HASH register write sequence를 인식해 SHA operation을
더 큰 단위로 coalescing하거나 state save/restore 패턴을 cache할 수 있다.
하지만 현재 profile상 host SHA/AES 자체 시간은 작고, register callback도
FVP 대비 100배 차이를 설명하지 못한다. 효과는 제한적일 가능성이 높다.

### 최종 제안

FVP 수준의 RSE boot time이 목표라면 다음 순서가 가장 현실적이다.

1. 현재 적용한 DMI mask, CC3XX DMA DMI cache, hotpath profile은 유지하되
   기본 off인 opt-in 성능/계측 option으로 둔다.
2. 현재 추가한 host-side LMS verifier helper를 QEMU/libqemu PC-entry hook에
   연결한다. `sync_with_kernel()` 기반 prototype은 함수 진입을 놓치므로
   성능 개선 경로가 아니다.
3. PC-entry accelerator 결과가 여전히 부족하면 QEMU TCG-side Thumb helper로
   `memcpy/memset`과 LMOTS inner loop를 더 낮은 레벨에서 치환한다.
4. full-system completion 검증에는 accelerator 사용 여부를 `result.json`과
   summary에 반드시 기록하고, secure boot negative test는 accelerator off
   또는 strict fallback mode로 별도 수행한다.

## 2026-06-08 추가 구현: QEMU PC-entry LMS accelerator

위 제안의 1순위였던 QEMU/libqemu PC-entry hook을 구현해 RSE BL1_2
`pq_crypto_verify()` 진입 시점에 host-side LMS verifier를 직접 실행하도록
연결했다. 이 경로는 단순 success stub이 아니라 guest memory에서 public key,
message, signature를 읽고 QBox host-side `LMS_SHA256_M32_H10` +
`LMOTS_SHA256_N32_W8` verifier로 검증한 뒤 성공 시 R0를 `FIH_SUCCESS`로,
PC를 LR로 갱신한다.

핵심 구현:

- `tools/qemu/libqemu/*`: `libqemu_set_cpu_pc_entry_cb()` callback API 추가
- `tools/qemu/accel/tcg/cpu-exec.c`: TCG CPU loop의 TB lookup 전 PC-entry hook 호출
- `tools/qbox/qemu-components/common/*`: C++ `Cpu::set_pc_entry_callback()`와
  `QemuCpu` LMS accelerator 연결
- `tools/qbox-platform/platforms/fvp-rd-aspen-rse/conf.lua`: 현재 BL1_2 ELF의
  `pq_crypto_verify` entry인 `0x11009bad`를 기본 verify PC로 설정
- `scripts/run/run_qbox_fvp_rd_aspen_rse.py`,
  `scripts/run/run_qbox_apollo_fvp_full.py`: `--rse-lms-accel` 옵션의 기본
  data limit을 image verification payload에 맞춰 16MiB로 상향

검증 명령:

```bash
cmake --build build/local-apollo-fvp/work/qbox-platform \
  --target rse_lms_accel-tests cpu_arm_cortexM55 platforms-vp apollo_fvp_full_system \
  --parallel 8

python3 -m py_compile \
  scripts/run/run_qbox_fvp_rd_aspen_rse.py \
  scripts/run/run_qbox_apollo_fvp_full.py

QBOX_RSE_LMS_TEST_DATA="$(find build/tmp_baremetal/work \
  -path '*/zephyr-demos-cl1/*/git/modules/crypto/mbedtls/tests/suites/test_suite_lms.data' \
  -print -quit)" \
  build/local-apollo-fvp/work/qbox-platform/tests/components/cc3xx/rse_lms_accel-tests

ctest --test-dir build/local-apollo-fvp/work/qbox-platform \
  -R 'rse_lms_accel|cc3xx|qemu_cc3xx|cortex_m55_remote_dmi_byte_store' \
  --output-on-failure
```

RSE smoke:

```bash
python3 scripts/run/run_qbox_fvp_rd_aspen_rse.py \
  --skip-build \
  --cc3xx-qemu-native-backend \
  --rse-lms-accel \
  --qbox-perf-profile \
  --qbox-perf-profile-interval 1024 \
  --timeout 90 \
  --ignore-fail-patterns \
  --out-dir build/qbox-apollo-fvp/rse-lms-accel-smoke-20260608-004007
```

결과:

| 항목 | 결과 |
| --- | ---: |
| `lms_hits` | 1 |
| `lms_unsupported` | 0 |
| `lms_dmi_failures` | 0 |
| `lms_verify_failures` | 0 |
| `lms_state_failures` | 0 |
| `rse_bl2_decrypted` | 14.653초 |
| `rse_bl2_validated` | 14.753초 |
| decrypt-to-validate delta | 0.100초 |
| `rse_jump_bl2` | 14.853초 |
| `rse_image_4_loaded` | 46.955초 |

이전 `sync_with_kernel()` prototype은 `lms_hits=0`으로 효과가 없었지만,
PC-entry hook은 BL1_2 LMS 검증 구간을 사실상 제거한다. FVP의 약 1.4초
validation delta보다도 작은 delta가 나왔으므로, BL1_2 LMS verification
문제는 해결된 것으로 본다.

### 남은 병목

PC-entry LMS accelerator 이후에도 90초 RSE smoke는 full RSE runtime handoff까지
도달하지 못했다. slowest delta는 `rse_jump_bl2 -> rse_image_4_loaded`
32.102초이며, 이 구간은 RSE BL2가 SI image를 decrypt/load/verify하는 단계다.

동일 run의 profile 요약:

- QEMU initiator `regular`: 1,192,959회
- QEMU initiator `regular_ns`: 약 76.375초
- RemotePass `outbound_b_transport`: 704,653회
- RemotePass `outbound_b_transport_ns`: 약 40.143초
- RemotePass `outbound_dmi_request`: 686,963회
- RemotePass `outbound_dmi_request_ns`: 약 25.417초
- CC3XX PKA opcode writes: 18,657회
- CC3XX AES CTR bytes: 403,573 bytes
- CC3XX hash DMA bytes: 412,963 bytes

Superseded/currently removed: `--remotepass-dmi-cache` 비교 run
`build/qbox-apollo-fvp/rse-lms-remotepass-dmi-smoke-20260608-004222`는
`rse_image_4_loaded=47.741초`로 개선이 없었다. DMI cache hit가 6회뿐이라
이 경로의 per-access overhead를 줄이지 못했다.

RSE VM/host SRAM을 `QBOX_MMIO_DIRECT_FASTPATH_RANGES`로 직접 fastpath 처리하는
시험 run `build/qbox-apollo-fvp/rse-lms-direct-range-smoke-20260608-004437`은
16.163초에 조기 종료되어 기본 적용 후보에서 제외한다. 해당 접근은
SystemC thread hop을 우회하기 때문에 일부 memory/window side effect나
동기화 전제를 깨는 것으로 보인다.

### 최신 권장 순서

1. **적용 완료:** PC-entry LMS accelerator는 RSE BL1_2 LMS 검증 병목을 해결했다.
   `--rse-lms-accel`은 positive boot 성능 검증용 opt-in 옵션으로 유지한다.
2. **다음 1순위:** QEMU initiator DMI alias 재사용 문제를 수정한다. 현재 DMI가
   allowed로 보고되지만 실제 CPU access는 대부분 regular TLM/RPC로 남는다.
   목표는 RSE VM/host SRAM/flash read-write를 QEMU memory alias 또는 안전한
   shared-memory backed RAM으로 처리해 `regular`와 RemotePass access 수를
   자릿수 단위로 줄이는 것이다.
3. **다음 2순위:** RSE BL2 semantic accelerator를 별도 opt-in으로 추가한다.
   대상은 ECDSA P-256 verify, image hash, AES-CTR decrypt/copy sequence다.
   CC3XX register-level PKA model은 정확도 검증용으로 유지하고, FVP 근접
   성능 모드는 함수/sequence 단위 host helper로 우회한다.
4. **다음 3순위:** direct fastpath는 범위별 allowlist와 side-effect 검증을
   거친 뒤 제한적으로만 사용한다. 이번 broad range 시험처럼 VM/host SRAM을
   한 번에 우회하는 방식은 안전하지 않다.

## 2026-06-08 추가 검토: FVP 근접 RSE boot time 개선안

QBox RSE boot time을 Arm Zena CSS FVP에 더 가깝게 만들기 위해 QBox 수정
위주의 후보를 재검토했다. 결론은 CC3XX crypto 연산 자체보다 QEMU
initiator/RemotePass 경로의 반복 비용이 더 큰 병목이라는 것이다.

### 바로 적용 가능한 개선

1. **PC-entry hook 안정화**

   최초 PC-entry hook은 TB lookup 경로에서만 `pq_crypto_verify()` 진입을
   확인했기 때문에 QEMU TB chaining 상태에 따라 `lms_hits=0`이 되는 run이
   있었다. `libqemu_cpu_pc_entry_cb_enabled()`가 true인 동안 `CF_NO_GOTO_TB`
   와 `CF_NO_GOTO_PTR`를 설정해 entry PC를 안정적으로 관측하도록 했다.
   단, chaining을 계속 끄면 `rse_image_4_loaded`가 65.210초까지 느려졌으므로,
   LMS verify가 한 번 성공하면 `Cpu::clear_pc_entry_callback()`으로 callback을
   해제해 이후 BL2/SI image load 구간은 정상 TB chaining을 사용하도록 했다.

   검증 run:

   - `build/qbox-apollo-fvp/rse-pc-entry-clear-smoke-20260608-010111`
   - `lms_hits=1`
   - `rse_bl2_decrypted=13.239초`
   - `rse_bl2_validated=13.340초`
   - `rse_image_4_loaded=47.346초`

   이 결과는 PC-entry hook 안정성을 확보하면서 no-chain 전체 적용의 성능
   악화를 피한 상태다.

2. **host memory DMI 파라미터 수정**

   `gs_memory`의 실제 CCI parameter는 `dmi_allow`인데, RD-Aspen RSE platform의
   host memory window 일부는 `dmi = host_memory_dmi`를 사용하고 있었다. 이
   설정은 `p_dmi`에 연결되지 않아 기본값 `true`가 남고, QEMU initiator가
   DMI hint를 계속 받은 뒤 RemotePass DMI request/fallback을 반복한다.

   `dmi_allow = host_memory_dmi`로 수정한 뒤 기본값 false에서 측정한 결과:

   - `build/qbox-apollo-fvp/rse-host-dmi-param-smoke-20260608-010341`
   - `dmi_allowed`: 660,228회 -> 27회
   - RemotePass `outbound_dmi_request`: 660,851회 -> 1,117회
   - `rse_image_4_loaded`: 47.346초 -> 35.806초

   전체 host memory DMI를 `QBOX_RDASPEN_HOST_MEMORY_DMI=true`로 다시 켜면
   DMI 실패 반복이 되살아나고 `rse_image_4_loaded=47.247초`로 악화된다.
   따라서 현재 권장값은 전체 host memory DMI off이다.

### 추가 개발 후보

1. **negative DMI cache**

   host memory DMI 파라미터 수정 후에는 RSE boot smoke 기준 반복 DMI request가
   크게 줄어 우선순위가 낮아졌다. 그래도 다른 boot mode나 AP-enabled path에서
   DMI 실패 RPC가 다시 커질 수 있으므로, RemotePass에는 no-DMI 결과를 range
   단위로 cache하고 invalidation 때 지우는 negative cache를 추가할 수 있다.

2. **file-backed SI SRAM DMI**

   SI CL0/CL1 SRAM만 별도 DMI로 여는 옵션을 추가해 검토했지만,
   `QBOX_RDASPEN_HOST_SI_SRAM_DMI=true` run은 `lms_hits=0` 조기 종료가 나와
   유효 성능 결과로 쓰지 않았다. 이 경로는 DMI alias priority, file-backed
   MemoryRegion alias, TB invalidation/flush를 별도로 정리한 뒤 다시 검토한다.

3. **QEMU MemoryRegion alias priority/overlap**

   DMI alias가 valid한 경우에도 QEMU root가 전체 address space IO region으로
   잡혀 있어 priority 0 `add_subregion()` alias가 충분히 이기지 못할 수 있다.
   `add_subregion_overlap()` wrapper에 TLB flush를 보강하고, DMI alias를
   priority 1로 설치하는 실험을 적용했다.

   검증 run:

   - `build/qbox-apollo-fvp/rse-dmi-overlap-smoke-20260608-011808`
   - `lms_hits=1`
   - `rse_bl2_decrypted=13.148초`
   - `rse_bl2_validated=13.349초`
   - `rse_image_4_loaded=35.117초`
   - RemotePass `outbound_b_transport`: 1,053,603회 -> 1,024,931회

   `rse_image_4_loaded` 기준으로 35.806초에서 35.117초로 약 0.69초 개선됐다.
   큰 폭의 개선은 아니지만, QEMU memory topology 변경 시 overlap alias도
   add/del wrapper와 동일하게 TLB flush를 보장한다는 점에서 유지할 가치가 있다.

4. **RSE BL2 semantic accelerator**

   FVP 수준의 시간을 더 공격적으로 목표로 하면 BL2 image load/decrypt/verify
   sequence를 함수 또는 이미지 단위로 host helper에 연결하는 것이 가장 큰
   추가 개선 후보이다. CC3XX register-level model은 fidelity 검증용으로 유지하고,
   성능 모드는 opt-in semantic accelerator로 분리한다.

### 현재 권장 순서

1. PC-entry LMS accelerator 안정화와 host memory `dmi_allow` 수정은 기본 개선으로
   유지한다.
2. short boot smoke에서 `rse_image_4_loaded` 35.117초를 현재 기준선으로 삼는다.
3. `QBOX_RDASPEN_HOST_SI_SRAM_DMI=true`는 overlap/flush 보강 후에도
   `rse_image_4_loaded=45.948초`로 악화되므로 기본값으로 사용하지 않는다.
4. FVP 대비 격차가 여전히 크면 RSE BL2 semantic accelerator를 opt-in으로 추가한다.

## FVP 근접을 위한 QBox 중심 추가 제안

현재 기준선은 다음 run이다.

- `build/qbox-apollo-fvp/rse-dmi-overlap-smoke-20260608-011808`
- `rse_bl2_validated=13.349초`
- `rse_image_4_loaded=35.117초`
- slowest delta: `rse_jump_bl2 -> rse_image_4_loaded = 21.768초`
- QEMU initiator `regular=1,835,007`, `regular_ns=77.478초`
- RemotePass `outbound_b_transport=1,024,931`, `outbound_b_transport_ns=58.931초`
- CC3XX native backend crypto 처리 자체는 `aes_dma_ns=0.101초`,
  `hash_dma_ns=0.036초`, `pka_opcode_ns=0.014초` 수준이다.

즉, 지금 남은 차이는 CC3XX 알고리즘 실행 시간이 아니라 RSE BL2의
MCUboot image hash/decrypt/copy path가 만드는 QEMU CPU memory access와
SystemC/RemotePass 왕복 비용이다. BL2 map도 이 해석과 맞는다.
`bootutil_img_validate()`는 `0x3101eea4`, `bootutil_verify_sig()`는
`0x3101f450`에 있고, 현재 BL2는 `image_ecdsa.c` 경로를 사용한다.
따라서 BL1_2의 LMS accelerator를 BL2에 그대로 확장하는 것은 핵심 해법이
아니다.

### 1순위: SI SRAM QEMU-native direct file alias

가장 먼저 적용할 QBox 수정은 RSE CPU가 SI CL0/CL1 RAM-load image header와
payload를 접근하는 구간을 QEMU process 안의 `MemoryRegion` RAM alias로
직접 보이게 하는 것이다. 단순히 SystemC memory target에 DMI를 허용한
`QBOX_RDASPEN_HOST_SI_SRAM_DMI=true`는 `rse_image_4_loaded=45.948초`로
악화됐기 때문에 사용하지 않는다. 이번 구현은 DMI hint에 의존하지 않고
RSE CPU address space에 좁은 alias를 명시적으로 추가한다.

구현 형태:

1. `QemuInitiatorSocket`에 opt-in `direct_file_aliases` CCI parameter를
   추가한다.
2. `addr:size:file_offset:ro|rw:path` spec을 파싱해
   `MemoryRegion::init_ram_ptr()` 기반 alias를 QEMU root memory 아래
   overlap priority 20으로 설치한다.
3. unaligned MCUBoot header file offset은 4 KiB 아래로 align해 host file을
   mapping하고, guest alias start도 같은 delta만큼 보정한다.
4. `run_qbox_fvp_rd_aspen_rse.py --rse-direct-si-sram-alias`는 현재
   `rse-flash` MCUBoot header에서 CL0/CL1 payload size를 계산해 다음 alias를
   자동 생성한다.

검증 run:

```bash
python3 scripts/run/run_qbox_fvp_rd_aspen_rse.py \
  --skip-build \
  --cc3xx-qemu-native-backend \
  --rse-lms-accel \
  --rse-direct-si-sram-alias \
  --qbox-perf-profile \
  --timeout 90 \
  --ignore-fail-patterns \
  --out-dir build/qbox-apollo-fvp/rse-direct-si-sram-alias-smoke-20260608-015007
```

결과:

- `rse_jump_bl2 -> rse_image_4_loaded`가 `21.768초`에서 `2.909초`로 감소했다.
- `rse_image_4_loaded`는 `35.117초`에서 `16.353초`로 감소했다.
- 기존 기준선은 90초 안에 SI CL1/AP BL2/RSE runtime handoff까지 가지
  못했지만, direct alias run은 `rse_first_image_slot=54.582초`까지 도달했다.
- RemotePass `outbound_b_transport`는 `1,024,931회`에서 `426,764회`로,
  `outbound_b_transport_ns`는 `58.931초`에서 `24.637초`로 감소했다.
- QEMU initiator profile에는 `direct_file_aliases=4`,
  `direct_file_alias_bytes=1,026,048`로 alias 설치가 기록됐다.

따라서 현재 QBox 수정 중 FVP에 가장 가깝게 다가가는 실질적인 해법은
SI SRAM direct file alias를 opt-in 성능 모드로 유지하는 것이다. 다만 이
모드는 RSE ATU/SystemC routing을 해당 image header/payload range에서
우회하므로 fidelity label을 명확히 남긴다.

### 2순위: AP BL2 RAM-load alias

처음 시도한 AP BL2 단일 alias는 실패했다.

- run: `build/qbox-apollo-fvp/rse-direct-ramload-alias-smoke-20260608-015505`
- 실패 로그: `Image in the primary slot is not valid!`,
  `Image in the secondary slot is not valid!`, `Unable to find bootable image`

원인은 AP BL2가 SI SRAM과 달리 header와 payload가 다른 backing file/window에
놓이는 구조였기 때문이다. TF-M `host_atu_base_address.h` 기준으로 AP BL2는
다음 두 구간을 분리해야 한다.

- header: `0x70001c00:0x400` -> `host-ap-bl2-header-sram.bin` offset `0x1c00`
- payload: `0x70002000:<computed>` -> `host-ap-shared-sram.bin` offset `0x82000`

이를 `--rse-direct-ap-bl2-alias`로 구현하고 검증했다.

```bash
python3 scripts/run/run_qbox_fvp_rd_aspen_rse.py \
  --skip-build \
  --cc3xx-qemu-native-backend \
  --rse-lms-accel \
  --rse-direct-si-sram-alias \
  --rse-direct-ap-bl2-alias \
  --qbox-perf-profile \
  --timeout 90 \
  --ignore-fail-patterns \
  --out-dir build/qbox-apollo-fvp/rse-direct-si-ap-bl2-alias-smoke-20260608-continue1
```

결과:

- `rse_first_image_slot`이 `54.582초`에서 `47.542초`로 감소했다.
- AP BL2 구간인 `rse_image_3_loaded -> rse_image_2_loaded`가
  `17.661초`에서 `7.123초`로 감소했다.
- RemotePass `outbound_b_transport`는 `426,764회`에서 `330,399회`로 감소했다.
- RSE 로그는 image 4/3/2/0 load 성공과
  `RSE to SCP SCMI power on AP succeeded`를 모두 유지했다.

### 3순위: RSE boot flash/AP FIP read-only alias

남은 큰 비용은 flash image/FIP read path였다. 전 영역 flash stub은 fidelity
debt가 크므로, 다음 read-only alias만 opt-in으로 추가했다.

- `--rse-direct-rse-flash-alias`: RSE boot flash에서 valid MCUBoot image의
  실제 boot-read 범위만 alias한다. 현재 image 기준 range는
  `0x27000:0x31000`, `0x67000:0xb6000`, `0x167000:0x44000`이다.
- `--rse-direct-ap-fip-alias`: RSE AP-flash ATU window에서 active AP FIP slot
  `0x703ad000:0x240000`만 alias한다.
- `--rse-fast-boot-aliases`: SI SRAM, AP BL2, RSE boot flash, AP FIP alias를
  함께 켜는 검증된 preset이다.

분리 검증 결과:

| Run | `rse_first_image_slot` | Slowest delta | RemotePass outbound |
| --- | ---: | --- | ---: |
| SI + AP BL2 alias | 47.542초 | image 4 -> 3: 17.953초 | 330,399 |
| + RSE boot flash alias | 35.321초 | image 4 -> 3: 10.331초 | 330,399 |
| + AP FIP alias | 39.424초 | image 4 -> 3: 16.448초 | 235,167 |
| + RSE boot flash + AP FIP | 27.886초 | image 4 -> 3: 9.629초 | 235,167 |

검증 command:

```bash
python3 scripts/run/run_qbox_fvp_rd_aspen_rse.py \
  --skip-build \
  --cc3xx-qemu-native-backend \
  --rse-lms-accel \
  --rse-fast-boot-aliases \
  --qbox-perf-profile \
  --timeout 60 \
  --ignore-fail-patterns \
  --out-dir build/qbox-apollo-fvp/rse-fast-boot-aliases-preset-smoke-20260608-continue1
```

preset 검증 결과:

- `rse_first_image_slot=28.692초`
- `rse_bl1_1 -> rse_first_image_slot = 25.481초`
- QEMU initiator `direct_file_aliases=10`, `direct_file_alias_bytes=4,709,376`
- RSE 로그는 image 4/3/2/0 load 성공과 AP power-on 성공을 유지했다.

FVP timed run의 `rse_bl1_1 -> rse_first_image_slot`은 `4.818초`이므로,
현재 preset은 FVP 대비 약 5.3배 수준까지 줄었다. 기존 QBox full-system의
`191.484초` 대비로는 약 7.5배 빠르다.

### 4순위: RSE BL2 semantic image-load accelerator

FVP 수준에 더 가까워지려면 남은 `image 4 -> image 3` 약 9~10초 구간을
줄여야 한다. 현재 CC3XX QEMU-native profile에서 CC3XX callback 자체는
1초 미만이고, QEMU initiator/RemotePass 작은 access가 여전히 남아 있다.
따라서 다음 단계는 register polling stub이 아니라 BL2 image-load semantic
accelerator이다.

이를 확인하기 위해 기본 off인 `--rse-bl2-load-profile`을 추가했다. 이
옵션은 QEMU TCG PC-entry hook에서 RSE BL2 함수 진입 PC와 R0-R3/SP/LR/stack
word만 기록하며, guest firmware 실행은 건드리지 않는다. 현재 Apollo RSE는
`platforms-vp` 안의 in-process `cpu_arm_cortexM55` 경로에서 동작하므로 QBox
변경 검증 시에는 `cpu_arm_cortexM55`, `platforms-vp`, 그리고
`apollo_fvp_full_system` aggregate target을 함께 빌드한다.

검증 command:

```bash
cmake --build build/local-apollo-fvp/work/qbox-platform \
  --target cpu_arm_cortexM55 platforms-vp apollo_fvp_full_system \
  --parallel 8
python3 scripts/run/run_qbox_fvp_rd_aspen_rse.py \
  --skip-build \
  --cc3xx-qemu-native-backend \
  --rse-lms-accel \
  --rse-fast-boot-aliases \
  --rse-bl2-load-profile \
  --qbox-perf-profile \
  --timeout 60 \
  --ignore-fail-patterns \
  --out-dir build/qbox-apollo-fvp/rse-bl2-load-profile-smoke-20260608-remote-rebuild
```

결과:

- run은 60초 timeout 때문에 `qbox_platform_timeout`으로 종료됐지만,
  RSE image 4/3/2/0 load, runtime handoff,
  `RSE to SCP SCMI power on AP succeeded`, measured boot RT_0 marker는
  모두 유지됐다.
- `rse_bl1_1 -> rse_first_image_slot = 28.392초`로 fast alias preset과
  같은 등급이며, profile 계측 부하가 있는 run임을 감안해야 한다.
- `rse-hotpath-profile.json`에 BL2 site hit가 기록됐다.
  - `boot_go_for_image_id`: 3 hits
  - `boot_load_image_to_sram`: 3 hits
  - `boot_enc_load`: 3 hits
  - `boot_enc_decrypt`: 592 hits
  - `bootutil_img_validate`: 1 hit
  - `bootutil_verify_sig`: 1 hit
- 마지막 `boot_enc_decrypt` sample은
  `r0=0x310033d0`, `slot=0`, `off=0x40400`, `sz=0x400`,
  `blk_off=0`, `buf=0x700c4400`였다. 즉 남은 병목은 1KiB 단위
  AES-CTR decrypt chunk 반복이 지배한다.

대상:

- `boot_go_for_image_id()`
- `bootutil_img_validate()`
- `boot_enc_load()`
- `boot_enc_decrypt()`
- `bootutil_verify_sig()`

원칙:

- secure boot를 무조건 성공시키는 stub은 사용하지 않는다.
- host helper는 MCUBoot header/TLV/hash/signature/encryption TLV를 읽고
  실제 hash, AES-CTR decrypt, ECDSA verify를 수행한다.
- 결과가 현재 flash image와 정확히 맞을 때만 RAM-load destination에 bulk
  write하고 firmware return state를 진행시킨다.
- 기본 fidelity mode는 register-level CC3XX/QBox path를 유지하고,
  `--rse-bl2-load-accel` 같은 명시 옵션에서만 켠다.

구현 우선순위는 두 단계로 나누는 것이 좋다.

1. 먼저 `boot_enc_decrypt()` chunk accelerator를 opt-in으로 추가한다. 이
   방식은 `boot_load_image_to_sram()` 전체를 건너뛰지 않으므로 boot state,
   slot 선택, TLV scan, log 순서를 보존하기 쉽다. 단, `enc_state` 내부의 AES
   key/CTR state를 정확히 읽거나 QEMU-native CC3XX core에서 session state를
   조회할 수 있어야 한다.
2. 그 다음 `boot_load_image_to_sram()` semantic accelerator로 확장한다. 이
   방식은 MCUBoot header/TLV/hash/signature/encryption TLV를 host에서 검증한
   뒤 destination SRAM에 bulk write하고, 검증 실패 시 즉시 guest path로
   fallback해야 한다.

#### `boot_enc_decrypt()` chunk accelerator 적용 결과

1단계로 기본 off인 `--rse-bl2-boot-enc-accel`을 추가했다. 이 옵션은 RSE
BL2의 `boot_enc_set_key()` 진입에서 `boot_status.enckey[slot]`를 캡처하고,
`boot_enc_decrypt()` 진입에서 MCUBoot와 같은 AES-CTR counter 규칙으로
destination buffer를 직접 복호화한 뒤 guest PC를 LR로 복귀시킨다. 구현은
secure boot 성공을 강제하지 않고, key capture 실패, slot/key size 불일치,
buffer DMI/alias 조회 실패, unsupported argument는 guest path로 fallback한다.

검증 command:

```bash
cmake --build build/local-apollo-fvp/work/qbox-platform --target cc3xx_core-tests --parallel 8
ctest --test-dir build/local-apollo-fvp/work/qbox-platform -R '^cc3xx_core-tests$' --output-on-failure
cmake --build build/local-apollo-fvp/work/qbox-platform \
  --target cpu_arm_cortexM55 platforms-vp apollo_fvp_full_system \
  --parallel 8
python3 scripts/run/run_qbox_fvp_rd_aspen_rse.py \
  --skip-build \
  --cc3xx-qemu-native-backend \
  --rse-lms-accel \
  --rse-fast-boot-aliases \
  --rse-bl2-load-profile \
  --rse-bl2-boot-enc-accel \
  --qbox-perf-profile \
  --timeout 90 \
  --ignore-fail-patterns \
  --out-dir build/qbox-apollo-fvp/rse-bl2-boot-enc-accel-smoke-20260608-3
```

결과:

| Run | `rse_bl1_1 -> rse_first_image_slot` | `BL2 -> RSE runtime handoff` | Slowest delta | `boot_enc_decrypt` 처리 |
| --- | ---: | ---: | --- | ---: |
| BL2 load profile baseline | 28.392초 | 18.159초 | image 4 -> image 3: 11.234초 | profile hit 592 |
| `boot_enc_decrypt` accel | 25.473초 | 15.445초 | image 4 -> image 3: 10.830초 | accel hit 930 / 951,488 bytes |

세부 profile:

- `key_captures=3`, `key_capture_failures=0`
- `decrypt_hits=930`, `decrypt_bytes=951488`
- `decrypt_direct_file_alias_hits=930`
- `decrypt_dmi_failures=0`, `decrypt_key_misses=0`,
  `decrypt_state_failures=0`, `decrypt_unsupported=0`
- RSE log는 image 4/3/2/0 load, AP power-on SCMI, RSE runtime handoff,
  measured boot RT_0 marker를 유지했다.
- run은 90초 cap 때문에 `qbox_platform_timeout`으로 종료됐지만, 이 smoke의
  목적이었던 RSE chain 검증은 통과했다.

해석:

- chunk 단위 AES-CTR 복호화는 정확히 가속됐고 기능 회귀는 보이지 않는다.
- 개선폭은 `rse_bl1_1 -> rse_first_image_slot` 기준 약 2.9초다. 즉,
  `boot_enc_decrypt()`만으로는 FVP timed run의 4.818초에 근접하기 어렵다.
- 남은 최장 구간은 여전히 SI CL0/CL1 RAM-load image 처리이며,
  `image 4 -> image 3`가 10.830초다.
- 다음 성능 단계는 `boot_enc_decrypt()`보다 한 단계 높은 host-native
  검증/복사 경로가 맞다. 다만 `boot_load_image_to_sram()` 전체를 바로
  건너뛰는 방식은 `boot_enc_load()`/`boot_enc_set_key()`의 key unwrap과
  `boot_loader_state`/`boot_status` 상태 갱신까지 QBox가 복제해야 하므로
  위험하다.
- 더 안전한 다음 단계는 `bootutil_verify_sig()`를 host-native ECDSA-P256
  검증으로 대체하는 것이다. 이 함수는 `hash`, `sig`, `key_id`와
  `bootutil_keys[]`의 public key만 필요하므로 secure boot 성공을 강제하지
  않고 실제 검증이 성공할 때만 `FIH_SUCCESS`를 반환할 수 있다.
- `bootutil_verify_sig()` 가속 후에도 남은 병목이 RAM-load copy/decrypt라면,
  그 다음에 MCUBoot header/TLV/hash/signature/encryption TLV를 host에서 모두
  재현하는 `boot_load_image_to_sram()` image-level semantic accelerator로
  확장한다.

### FVP 수준에 근접하기 위한 QBox 수정 중심 권장안

현재 기준점은 다음과 같다.

| Run | `rse_bl1_1 -> rse_first_image_slot` | `BL2 -> RSE runtime handoff` | Slowest delta |
| --- | ---: | ---: | --- |
| FVP timed run | 4.818초 | - | - |
| QBox BL2 load profile baseline | 28.392초 | 18.159초 | image 4 -> image 3: 11.234초 |
| QBox `boot_enc_decrypt` accel | 25.473초 | 15.445초 | image 4 -> image 3: 10.830초 |

권장 순서는 다음과 같다.

1. `bootutil_verify_sig()` host-native ECDSA profile/helper를 먼저 추가한다.
   - 대상 심볼: `bootutil_verify_sig=0x3101f450`,
     `bootutil_keys=0x31000454`, `bootutil_key_cnt=0x3102b424`.
   - QEMU CPU hook에서 AAPCS 인자 `R0=hash`, `R1=hlen`, `R2=sig`,
     `R3=slen`, `SP[0]=key_id`를 읽는다.
   - `bootutil_keys[key_id]`의 `key`/`len` pointer를 guest memory에서 읽고,
     DER public key와 DER ECDSA signature를 host C++에서 검증한다.
   - 기본 모드는 profile/host-verify only이다. 즉, host 검증이 성공해도 guest
     firmware의 `bootutil_verify_sig()`는 그대로 실행한다.
   - 직접 skip은 `bl2_verify_sig_skip` CCI 옵션으로 분리하고 기본 off로 둔다.
     fast alias 및 `boot_enc_decrypt` accelerator와 결합했을 때 image validation을
     깨는 run이 확인되었기 때문이다.
   - host 검증 결과는 public key/hash/signature 바이트 기준으로 cache한다.
     cache 없이 매 entry에서 P-256 scalar multiply를 반복하면 profile 옵션
     자체가 부팅 시간을 크게 늘린다.
   - 이 단계의 주 목적은 image-level semantic accelerator에 넣을 ECDSA 검증
     primitive와 계측을 마련하는 것이다. guest 검증을 유지하는 safe mode만으로는
     FVP 수준의 성능 개선을 만들지 않는다.

2. `boot_load_image_to_sram()` semantic accelerator는 2단계로 진행한다.
   - 1단계에서는 guest의 `boot_enc_set_key()`까지는 그대로 실행해 key unwrap과
     상태 갱신을 보존하고, 이후 payload copy/decrypt loop를 image 단위 bulk
     operation으로 대체한다.
   - 2단계에서는 QBox가 MCUBoot header, protected TLV, key hash, image hash,
     signature, encryption TLV를 모두 검증한 뒤 전체 함수 skip을 허용한다.
   - 이 옵션은 positive boot smoke 전용으로 기본 off여야 하며,
     FWU/negative secure-boot test에서는 반드시 끈다.

3. RemotePass/DMI cache는 full-system profile에서 다시 병목으로 확인될 때
   적용한다.
   - shared SRAM, flash read-only range, frequently-polled MMIO에 positive/
     negative DMI cache를 적용한다.
   - `invalidate_direct_mem_ptr()` range invalidation을 구현하지 않은 cache는
     사용하지 않는다.
   - 이 개선은 RSE 단독보다 AP/full-system long run에서 효과가 커질 가능성이
     높다.

4. 장기적으로 CC3XX QEMU-native backend를 register polling bypass가 아니라
   cryptographic operation backend로 확장한다.
   - AES-CTR, ECDSA verify, SHA/HMAC, TRNG/status register 모델을
     SystemC register frontend와 QEMU-native crypto core로 분리한다.
   - guest-visible register/status/interrupt 순서는 유지하고, 내부 crypto
     연산만 host-native로 처리한다.
   - 이 경로가 FVP와 가장 유사한 성능/동작 균형점이다.

5. 전체 RSE stub은 사용하지 않는다.
   - RSE boot가 빠르더라도 TF-M BL1/BL2 secure boot, SI/AP image loading,
     measured boot, AP power-on SCMI handoff 증거가 사라진다.
   - 허용 가능한 stub은 문제가 되는 함수 또는 IP operation 단위의 opt-in
     accelerator로 제한한다.

### 2026-06-08 `bootutil_verify_sig()` 구현 및 검증 결과

QBox CPU hook에 P-256 ECDSA host verifier와 BL2 `bootutil_verify_sig()`
profile/helper를 추가했다. 구현은 `tools/qbox/qemu-components/common/include`
아래의 `rse_p256_ecdsa.h`와 `cpu.h`에 있다.

검증 결과는 다음과 같다.

| Run | 결과 | 주요 counter |
| --- | --- | --- |
| uncached safe profile | BL2에서 image 4 검증 중 90초 timeout | `verify_matches=3593`, `skip_hits=0` |
| cached safe profile | RSE runtime handoff 도달, Linux login 전 90초 timeout | `verify_matches=9`, `cache_hits=6`, `cache_misses=3`, `skip_hits=0`, failure counter 0 |
| positive skip after historical `remote_cpu` rebuild | RSE runtime handoff 도달, Linux login 전 90초 timeout | `verify_matches=1`, `skip_hits=1`, `last_fih_success=0x0`, failure counter 0 |

cached run의 evidence는
`build/qbox-apollo-fvp/rse-bl2-verify-sig-profile-cache-smoke-20260608-1/`에
있다. `summary.txt` 기준 RSE는 `25.771초`에 AP power-on/runtime handoff까지
도달했다. image 4/3/2/0 load, SCP power-on, first image slot, measured boot
marker도 모두 확인되었다. timeout은 해당 smoke가 Linux login까지 요구하는
runner 판정 때문에 남았고, RSE boot 자체는 정상 진행했다.

positive skip run의 profile evidence는
`build/qbox-apollo-fvp/rse-bl2-verify-sig-skip-remote-rebuild-smoke-20260608/`
에 있다. 이 run은 image 4/3/2/0 load, AP power-on, first image slot까지
진행했고 `[ERR]` fail pattern은 없었다. `last_fih_success=0x0`인 이유는
현재 BL2 MCUBoot FIH profile이 off라서 `FIH_SUCCESS` 변수의 실제 guest 값이
0이기 때문이다. 이 값을 상수로 가정하지 않고 BL2 ELF에서 resolve한
`FIH_SUCCESS` 주소를 guest memory에서 읽어 반환한다.

profile overhead를 뺀 evidence는
`build/qbox-apollo-fvp/rse-bl2-verify-sig-skip-noprofile-smoke-20260608/`에
있다. 이 run은 `[ERR]` 없이 `rse_first_image_slot=27.392초`,
`rse_bl1_1 -> rse_first_image_slot=24.179초`를 기록했다.

주의할 점은 현재 Apollo RSE가 `platforms-vp` 안에서 in-process
`cpu_arm_cortexM55` 모듈을 사용한다는 것이다. `cpu.h`의 hook/profile 코드를
바꾼 뒤 `cpu_arm_cortexM55`, `platforms-vp`, `apollo_fvp_full_system`을 다시
빌드하지 않으면 이전 동작으로 smoke가 실행될 수 있다.

```bash
cmake --build build/local-apollo-fvp/work/qbox-platform \
  --target cpu_arm_cortexM55 platforms-vp apollo_fvp_full_system \
  --parallel 8
```

따라서 ECDSA host verifier와 positive skip은 유지하되, skip은 positive
boot smoke 전용 opt-in으로 둔다. FVP 수준에 더 가까운 다음 작업은
`boot_load_image_to_sram()` 또는 `boot_enc_load()` 단위의 image-level
semantic accelerator이며, 그 내부에서 MCUBoot header/TLV/hash/ECDSA/AES-CTR
처리를 일괄 검증하고 guest-visible 결과만 반영해야 한다.

### 5순위: RemotePass/DMI cache 정리

direct alias 후에도 profile에는 RemotePass outbound가 약 235k회 남는다.
full-system/AP-enabled path에서는 이 비용이 다시 커질 수 있으므로 다음 cache를
보강하면 안정적이다.

- positive DMI cache: 공유 메모리 DMI range를 local b_transport path로 재사용
- negative DMI cache: DMI가 불가능한 range의 반복 request를 억제
- invalidation: `invalidate_direct_mem_ptr()` 때 range별 cache를 정리

다만 RSE boot time을 FVP 수준으로 더 줄이는 결정타는 4순위 semantic
accelerator이다.

### 권장 실행 순서

1. RSE boot smoke/perf 비교에는
   `--cc3xx-qemu-native-backend --rse-lms-accel --rse-fast-boot-aliases`를
   기본 성능 preset으로 사용한다.
2. fidelity 검증이나 flash write/FWU 검증에서는 `--rse-fast-boot-aliases`를
   끄고 기존 flash model path를 사용한다.
3. 빠른 positive-boot smoke에는 `--rse-bl2-boot-enc-accel`을 함께 켠다.
4. BL2 hook/counter를 확인할 때만 `--rse-bl2-load-profile`과
   `--qbox-perf-profile`을 켠다. 최단 시간 비교에서는 두 옵션을 끈다.
5. PKA traffic 제거 여부만 확인할 때는 `--rse-bl2-verify-sig-skip`을 추가한다.
   단, 이 옵션은 positive boot smoke 전용이며 FWU/negative secure-boot
   fidelity 증거로 사용하지 않는다.
6. FVP `4.818초`에 더 가까워지는 다음 구현은 `--rse-bl2-load-accel`
   image-level semantic accelerator로 진행한다.
7. ECDSA accelerator는 독립 기능보다 semantic accelerator 내부의 검증 단계로
   통합한다.
8. RemotePass/DMI cache는 full-system long run profile에서 병목으로 다시
   확인될 때 보강한다.

### 2026-06-08 재검토: FVP 근접화를 위한 다음 해법

최신 `build/local-apollo-fvp/work/trusted-firmware-m/bin/bl2.elf` 기준 BL2
심볼은 다음과 같이 바뀌어 있다.

| Symbol | Address |
| --- | ---: |
| `boot_go_for_image_id` | `0x3101e288` |
| `boot_load_image_to_sram` | `0x3101e758` |
| `boot_enc_load` | `0x3101eeb6` |
| `boot_enc_set_key` | `0x3101ef52` |
| `boot_enc_decrypt` | `0x3101ef8c` |
| `bootutil_img_validate` | `0x3101f010` |
| `bootutil_img_hash` | `0x3101f3aa` |
| `bootutil_verify_sig` | `0x3101f5bc` |

`bootutil_img_hash()`만 host-native SHA256으로 처리하는 opt-in accelerator를
실험적으로 추가했다. 이 방식은 `bootutil_img_validate()`의 TLV 순회,
`bootutil_verify_sig()`, `MCUBOOT_HW_ROLLBACK_PROT` security counter check를
guest에 남기므로 `bootutil_img_validate()` 전체 skip보다 안전하다.

하지만 현재 QEMU/libqemu PC-entry hook 기반으로는 BL2 함수 진입점이 안정적으로
잡히지 않는다. 다음 smoke에서 RSE runtime handoff는 유지됐지만 모든 BL2
profile/accelerator counter가 0이었다.

| Run | `rse_bl1_1 -> rse_first_image_slot` | `BL2 -> RSE runtime handoff` | 주요 counter |
| --- | ---: | ---: | --- |
| control | 28.392초 | 18.161초 | `bl2_load_profile.*.hits=0`, `verify_matches=0` |
| `bootutil_img_hash` accel | 30.292초 | 19.863초 | `bl2_img_hash_accel.hits=0` |
| PC trace diagnostic | 30.086초 | 19.759초 | BL2 symbol entry hit 없음 |

PC trace의 BL2 range 최다 sample은 `memset()`(`0x3101d160`)과
`get_zero_count_region()`(`0x31021aca`)였다. runtime profile도
`remote_platform.cpu_0.cpu.mem.regular`가 약 1.1M회,
`platform.rse_cpu_pass.inbound_b_transport_rpc`가 약 235k회로 남아 있다.
따라서 현재 남은 차이는 CC3XX 알고리즘 자체보다 QEMU memory/TLM crossing과
guest memory loop 비용이다.

#### 수정 중심 권장 순서

1. **RemotePass/DMI와 direct memory path를 먼저 줄인다.**
   - RSE VM/host SRAM, SI CL0/CL1 RAM-load destination, AP BL2/FIP
     read-only path에 대해 현재 direct alias보다 더 좁고 확실한
     QEMU-local backdoor를 만든다.
   - positive DMI cache와 negative DMI cache를 `RemotePass`에 넣고,
     `invalidate_direct_mem_ptr()` range invalidation을 같이 구현한다.
   - 목표 metric은 `remote_platform.cpu_0.cpu.mem.regular`와
     `inbound_b_transport_rpc`를 먼저 절반 이하로 낮추는 것이다.

2. **BL2 함수 entry hook을 신뢰 가능한 방식으로 바꾼다.**
   - 현재 TB lookup 전 `s.pc` 콜백은 BL2 callsite/entry를 놓친다.
   - QEMU TCG translation-time breakpoint, per-TB edge hook, 또는 특정
     callsite patchpoint 방식으로 `bootutil_img_hash()`,
     `boot_enc_decrypt()`, `boot_load_image_to_sram()` 진입을 검출해야 한다.
   - 이 단계가 끝나야 함수 단위 semantic accelerator의 hit counter가
     실제 성능과 연결된다.

3. **image-level semantic accelerator는 PC hook 안정화 후 적용한다.**
   - `bootutil_img_validate()` 전체 skip은 `MCUBOOT_HW_ROLLBACK_PROT`를
     건너뛰므로 바로 쓰지 않는다.
   - 안전한 1단계는 `bootutil_img_hash()` host SHA256이다.
   - 공격적인 2단계는 MCUBoot header/protected TLV/hash/ECDSA/encryption
     TLV를 QBox가 모두 검증하고 `boot_load_image_to_sram()`의 bulk
     copy/decrypt 결과만 guest-visible buffer와 state에 반영하는 방식이다.
   - 이 옵션은 positive boot smoke 전용, 기본 off로 유지한다.

4. **OTP/zero-count/LCM hotpath를 QEMU-native 또는 cached model로 옮긴다.**
   - PC trace의 `get_zero_count_region()` 반복은 RSE firmware가 OTP/LCM
     style state를 bit-level로 스캔하는 비용으로 보인다.
   - register-visible 상태는 유지하되 read-only zero-count 결과나 OTP region
     read path를 QEMU-local cache로 제공하면 FVP와 유사한 backdoor 효과를 낼
     수 있다.

5. **CC3XX는 register polling bypass에서 crypto operation backend로 확장한다.**
   - 지금의 QEMU-native CC3XX backend는 register polling/write 비용을 줄이는
     데 초점이 있다.
   - FVP 수준을 목표로 하면 AES-CTR, SHA, ECDSA verify를 SystemC register
     frontend 뒤의 QEMU-native crypto core로 처리하고, guest-visible
     status/IRQ ordering만 유지하는 구조가 더 적합하다.

6. **전체 RSE stub은 사용하지 않는다.**
   - 전체 stub은 BL1/BL2 secure boot, measured boot, SI/AP image loading,
     AP power-on SCMI evidence를 잃는다.
   - 허용 범위는 함수/IP operation 단위의 opt-in accelerator와
     read-only/cacheable hardware path로 제한한다.

현재 결론은 `bootutil_img_hash()` 자체는 좋은 가속 단위이지만, 그 전에
QEMU의 BL2 entry detection과 RemotePass/memory path를 고쳐야 FVP
`4.818초`에 의미 있게 접근할 수 있다는 것이다.

### 2026-06-08 최신 제안: FVP 근접을 위한 QBox 수정 우선순위

추가 address profile 결과에서 `--rse-fast-boot-aliases` 이후에도 두 종류의
QBox 비용이 남는 것을 확인했다.

1. RSE boot flash의 secure primary slot 앞쪽 scan window
   `0xb0007000..0xb0026fff`가 약 129k회의 regular access를 만든다.
2. TF-M PS/ITS storage window `0xb3000000:0x110000`이 byte program,
   status read, clear-status command를 반복하면서 Strata flash access를
   크게 만든다.

따라서 다음 제안은 전체 RSE stub이 아니라, FVP fast model 내부 backdoor와
유사한 QEMU-local read/write path를 좁은 range에만 추가하는 것이다.

#### 적용 완료 및 유지할 항목

1. **pre-primary scan read-only alias**
   - `--rse-direct-rse-flash-alias`에 `pre_primary_scan`
     `0xb0007000:0x20000` alias를 추가했다.
   - profiled run에서 `remote_platform.cpu_0.cpu.mem.total_accesses`가
     `1,117,184`에서 `988,160`으로 줄었다.
   - `rse_bl1_1 -> rse_first_image_slot`은 `25.479초`에서 `23.879초`로
     감소했다.
   - read-only alias라서 CFI command write나 PS/ITS state update는 우회하지
     않는다.

2. **RSE PS/ITS storage direct-MMIO fastpath**
   - TF-M flash layout 기준 image area 뒤의 PS/ITS window
     `0xb3000000:0x110000`을 `QBOX_MMIO_DIRECT_FASTPATH_RANGES`로 추가했다.
   - 이 방식은 full flash DMI가 아니다. Strata CFI model은 그대로 실행하고,
     QEMU -> SystemC scheduler thread 왕복만 제거한다.
   - manual env run 기준 `regular` access는 `988,159`에서 `347,539`로
     줄고, `640,621`회가 `local_fastpath`로 이동했다.
   - 같은 run에서 `rse_bl1_1 -> rse_first_image_slot`은 `22.668초`,
     `BL2 -> RSE runtime handoff`는 `14.142초`였다.
   - scripted preset run에서는 `rse_storage_direct_fastpath.enabled=true`와
     range `0xb3000000:0x110000`이 result JSON에 기록됐다. wall time은
     profile 부하와 host 상태에 따라 `24초`대까지 흔들렸으므로, 이 옵션의
     1차 성공 기준은 wall time 하나가 아니라 `regular -> local_fastpath`
     이동량으로 본다.

3. **`--rse-fast-boot-aliases` preset 확장**
   - 기존 SI SRAM, AP BL2, RSE boot flash image read, AP FIP alias에
     RSE PS/ITS storage direct-MMIO fastpath를 포함한다.
   - positive boot smoke/perf 비교에는 이 preset을 사용한다.
   - FWU, PS/ITS persistence, negative secure-boot, flash command-state 검증에는
     preset을 끄고 기존 flash path를 사용한다.

#### 새 profile에서 확인한 storage 병목

`--flash-stats` run의 Strata flash counter는 PS/ITS storage가 실제로 byte
program 중심 workload임을 보여준다.

| Counter | 값 |
| --- | ---: |
| `total_accesses` | 717,824 |
| `read_accesses` / `write_accesses` | 191,692 / 526,132 |
| `command_writes` | 438,443 |
| `read_status_cmds` | 175,377 |
| `clear_status_cmds` | 87,689 |
| `word_program_cmds` | 87,689 |
| `program_bytes` | 87,689 |
| `program_changed_bytes` | 4,489 |
| `program_noop_bytes` | 82,875 |
| `backing_write_ops` | 4,489 |

이 결과는 flash storage 전체를 stub 처리하면 빠르겠지만 fidelity debt가 너무
커진다는 것을 의미한다. 반대로 direct-MMIO fastpath는 같은 Strata command
state와 backing write 조건을 유지하면서 per-access scheduler crossing만
줄이므로, FVP 근접 성능 모드로 허용할 수 있다.

#### 다음 구현 우선순위

1. **QEMU-local memory/direct path 고도화**
   - `--rse-fast-boot-aliases`를 현재 성능 기준선으로 둔다.
   - RSE VM, host SRAM, PS/ITS처럼 side effect가 명확히 분리되는 range는
     read-only alias 또는 direct-MMIO fastpath로 처리한다.
   - 목표 metric은 `remote_platform.cpu_0.cpu.mem.regular`를 현재
     `347k`보다 더 낮추고, RemotePass `outbound_b_transport` 약 `235k`회를
     절반 이하로 줄이는 것이다.

2. **BL2 function-entry hook 재설계**
   - 현재 BL2 symbol PC hook은 run에 따라 hit가 0이 된다.
   - TCG translation-time hook, per-TB edge hook, 또는 callsite patchpoint로
     `boot_load_image_to_sram()`, `boot_enc_decrypt()`,
     `bootutil_img_hash()`, `bootutil_verify_sig()` entry를 안정적으로 잡는다.
   - 이 단계가 끝나야 함수 단위 accelerator가 재현 가능한 성능 옵션이 된다.

3. **image-level semantic accelerator**
   - FVP의 `rse_bl1_1 -> rse_first_image_slot = 4.818초`에 접근하려면
     현재 남은 14~15초대 BL2/runtime 구간을 함수 몇 개가 아니라 image load
     operation 단위로 줄여야 한다.
   - QBox가 MCUBoot header, protected TLV, image hash, ECDSA signature,
     encryption TLV를 모두 검증한 뒤 destination SRAM에 bulk copy/decrypt를
     반영하는 opt-in accelerator를 만든다.
   - 검증 실패, unsupported TLV, FWU/negative test에서는 즉시 guest path로
     fallback한다.

4. **OTP/LCM zero-count hotpath cache**
   - PC trace에서 `get_zero_count_region()`이 자주 보인다.
   - OTP/LCM register-visible state는 유지하되, read-only zero-count 결과와
     OTP region scan을 QEMU-local cache로 제공하면 FVP 내부 model과 비슷한
     효과를 낼 수 있다.

5. **CC3XX QEMU-native backend 확장**
   - 현재 CC3XX qemu-native는 register path 최적화 중심이다.
   - FVP 근접 목표에서는 AES-CTR, SHA, ECDSA verify, LMS helper를
     operation backend로 묶고, guest-visible register/status/IRQ 순서만
     유지하는 구조가 장기 해법이다.

#### 제안 결론

가장 현실적인 순서는 다음이다.

1. 기본 성능 비교 preset:
   `--cc3xx-qemu-native-backend --rse-lms-accel --rse-fast-boot-aliases`
2. 빠른 positive RSE boot smoke:
   위 preset에 `--rse-bl2-boot-enc-accel`을 추가한다.
3. FVP 수준 근접을 위한 다음 개발:
   BL2 entry hook 재설계 후 `--rse-bl2-load-accel` image-level semantic
   accelerator를 구현한다.
4. 전체 RSE stub은 사용하지 않는다. 허용 범위는 좁은 address range,
   IP operation, firmware function 단위의 opt-in accelerator로 제한한다.

### 2026-06-08 Step 2 진행: BL2 Hook Symbol 자동 Resolve

BL2 function-entry hook의 `hits=0` 문제는 QEMU callback 자체만의 문제가
아니라 BL2 artifact drift도 포함하고 있었다. standalone RSE runner의 기본
deploy artifact는 `build/tmp_baremetal`의 Yocto BL2를 사용하지만, 일부 hook
기본 주소는 `build/local-apollo-fvp` BL2 기준으로 남아 있었다. 특히
`bootutil_key_cnt`는 두 build 사이에서 다른 주소를 갖는다.

현재 runner는 `--rse-bl2-elf`를 받아 다음 symbol을 ELF에서 자동으로 resolve한다.
명시 주소 option이 주어지면 그 값을 우선하고, ELF가 없거나 symbol이 없으면
기존 fallback 상수를 사용한다.

| Symbol | Yocto BL2 | Local-build BL2 |
| --- | ---: | ---: |
| `boot_go_for_image_id` | `0x3101e218` | `0x3101e288` |
| `boot_load_image_to_sram` | `0x3101e66c` | `0x3101e758` |
| `boot_enc_load` | `0x3101ed4a` | `0x3101eeb6` |
| `boot_enc_set_key` | `0x3101ede6` | `0x3101ef52` |
| `boot_enc_decrypt` | `0x3101ee20` | `0x3101ef8c` |
| `bootutil_img_validate` | `0x3101eea4` | `0x3101f010` |
| `bootutil_img_hash` | `0x3101f23e` | `0x3101f3aa` |
| `bootutil_verify_sig` | `0x3101f450` | `0x3101f5bc` |
| `bootutil_key_cnt` | `0x3102b424` | `0x3102bbd0` |

full-system wrapper는 local-build의
`build/local-apollo-fvp/work/trusted-firmware-m/bin/bl2.elf`를 RSE runner로
전달한다. standalone RSE runner는 기본값으로 Yocto BL2 ELF
`build/tmp_baremetal/work/fvp_rd_aspen-poky-linux/trusted-firmware-m/2.2.2+git/build/bin/bl2.elf`
를 사용한다. Result JSON의 `rse_bl2_load_profile.symbol_source`에 실제 ELF,
resolved address, missing symbol 목록을 기록한다.

검증 command:

```bash
python3 scripts/run/run_qbox_fvp_rd_aspen_rse.py \
  --skip-build \
  --cc3xx-qemu-native-backend \
  --rse-lms-accel \
  --rse-fast-boot-aliases \
  --rse-bl2-load-profile \
  --qbox-perf-profile \
  --timeout 70 \
  --ignore-fail-patterns \
  --out-dir build/qbox-apollo-fvp/rse-bl2-symbol-profile-smoke-20260608
```

결과:

- `symbol_source.parsed=true`, `missing=[]`
- `boot_enc_decrypt=1571 hits`
- `boot_enc_load=6 hits`
- `boot_go_for_image_id=5 hits`
- `boot_load_image_to_sram=4 hits`
- `bootutil_img_hash=3 hits`
- `bootutil_img_validate=5 hits`
- `bootutil_verify_sig=4 hits`
- RSE marker는 image 4/3/2/0 load, AP power-on, first image slot까지 유지

`--rse-bl2-boot-enc-accel`도 같은 resolver로 재검증했다.

```bash
python3 scripts/run/run_qbox_fvp_rd_aspen_rse.py \
  --skip-build \
  --cc3xx-qemu-native-backend \
  --rse-lms-accel \
  --rse-fast-boot-aliases \
  --rse-bl2-load-profile \
  --rse-bl2-boot-enc-accel \
  --qbox-perf-profile \
  --timeout 70 \
  --ignore-fail-patterns \
  --out-dir build/qbox-apollo-fvp/rse-bl2-symbol-boot-enc-accel-smoke-20260608
```

결과:

- `decrypt_hits=1229`
- `decrypt_bytes=1,256,688`
- `key_captures=4`
- `decrypt_key_misses=0`
- `decrypt_dmi_failures=0`
- `decrypt_state_failures=0`
- `decrypt_unsupported=0`
- `key_capture_failures=0`
- `rse_first_image_slot=28.995초`

이로써 Step 2의 최소 gate인 BL2 function-entry 검출과 guest state capture는
재현 가능해졌다. 다음 단계는 이 안정화된 hook 위에서
`boot_load_image_to_sram()` image-level semantic accelerator를 구현하는 것이다.

### 2026-06-08 Step 3 진행: BL2 RAM-load image별 상태 관측

`boot_load_image_to_sram()` semantic accelerator를 바로 구현하기 전에,
QBox CPU hook이 BL2 `boot_loader_state`와 MCUBoot header를 image별로 안정적으로
읽을 수 있는지 확인했다. 이를 위해 `rse-hotpath-profile.json`의
`bl2_load_profile.ram_load_snapshot`에 `by_image` 항목을 추가했다.

검증 command:

```bash
python3 scripts/run/run_qbox_fvp_rd_aspen_rse.py \
  --skip-build \
  --cc3xx-qemu-native-backend \
  --rse-lms-accel \
  --rse-fast-boot-aliases \
  --rse-bl2-load-profile \
  --qbox-perf-profile \
  --timeout 45 \
  --ignore-fail-patterns \
  --out-dir build/qbox-apollo-fvp/rse-bl2-ram-load-by-image-smoke-20260608
```

결과:

- `ram_load_snapshot.hits=4`
- `dmi_failures=0`, `unsupported=0`
- image별 snapshot은 `0`, `2`, `3`, `4`가 각각 1회씩 기록됨
- RSE marker는 image 4/3/2/0 load, AP power-on, first image slot까지 유지
- 짧은 timeout run이므로 최종 판정은 `qbox_platform_timeout`이지만,
  RSE boot chain 관측 목적은 충족함

관측된 RAM-load 대상:

| Image | 역할 추정 | `load_addr` | `img_size` | `hash_region_size` | `flags` |
| --- | --- | ---: | ---: | ---: | ---: |
| 4 | SI CL1 | `0x70185c00` | 275,648 | 276,800 | `0x24` |
| 3 | SI CL0 | `0x70083c00` | 743,664 | 744,817 | `0x24` |
| 2 | AP BL2 | `0x70001c00` | 94,016 | 95,169 | `0x24` |
| 0 | RSE runtime | `0x3103f800` | 197,568 | 198,620 | `0x24` |

최신 smoke의 slowest delta는 여전히
`rse_image_4_loaded -> rse_image_3_loaded = 11.132초`다. 위 snapshot 기준으로
이 구간은 다음 image인 SI CL0 image 3의 744 KiB RAM-load/validate/decrypt
처리가 지배한다. 따라서 FVP 4.818초에 더 가까워지기 위한 다음 구현은
전체 RSE stub이 아니라 `boot_load_image_to_sram()`에 한정된 image-level
semantic accelerator가 맞다.

다음 구현 gate:

1. `by_image` snapshot을 입력으로 image 3과 image 4부터 positive boot 전용
   `--rse-bl2-load-accel`을 실험한다.
2. guest `bootutil_img_validate()`, `bootutil_verify_sig()`, security counter
   check는 유지하고, guest가 성공한 image에 대해서만 bulk copy/decrypt와
   `slot_usage` 상태 갱신을 QBox-native path로 대체한다.
3. `flags=0x24`인 RAM-load + AES-128 encrypted image만 지원하고,
   나머지 flag/TLV/slot layout은 즉시 guest path로 fallback한다.
4. FWU, negative secure-boot, flash command-state fidelity 검증에서는 기본 off로
   유지한다.
