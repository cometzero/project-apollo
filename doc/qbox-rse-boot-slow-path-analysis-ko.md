# QBox RSE Boot Slow Path 분석

작성일: 2026-06-04

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
이전의 BL1_2 image validation 구간이다.

## FVP 대비 정량 비교

FVP와 QBox를 같은 marker 기준으로 비교하기 위해 FVP 로그 수집기에
`progress_marker_first_hits` 기록을 추가하고, 로컬 FVP를 다시 실행했다.

```bash
python3 scripts/runfvp_log_boot.py \
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
python3 scripts/analyze_qbox_rse_boot_timing.py --markdown \
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
python3 scripts/run_qbox_fvp_rd_aspen_rse.py \
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
python3 scripts/analyze_qbox_rse_boot_timing.py \
  build/qbox-apollo-fvp/rse-cc3xx-validation-complete-20260604/result.json
```

### CC3XX Register Histogram 추가 결과

`register_read_count`와 `register_write_count` histogram을 CC3XX stats에
추가한 뒤, 현재 권장 option 3A인 local MMIO fast path와 함께 다시 측정했다.

```bash
python3 scripts/run_qbox_fvp_rd_aspen_rse.py \
  --skip-build \
  --cc3xx-stats \
  --cc3xx-stats-interval 65536 \
  --cc3xx-local-mmio-fastpath \
  --timeout 230 \
  --ignore-fail-patterns \
  --out-dir build/qbox-apollo-fvp/rse-cc3xx-histogram-local-mmio-20260604

python3 scripts/analyze_qbox_rse_boot_timing.py --markdown \
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
python3 scripts/run_qbox_fvp_rd_aspen_rse.py \
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

다음으로 QEMU/RemoteCPU bridge에서 side-effect 없는 ready/busy status read만
바로 반환하는 opt-in fast path를 시험했다.

```bash
python3 scripts/run_qbox_fvp_rd_aspen_rse.py \
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
python3 scripts/run_qbox_fvp_rd_aspen_rse.py \
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
python3 scripts/run_qbox_fvp_rd_aspen_rse.py \
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
| RemoteCPU/QEMU bridge status-read fast path | 항상 ready인 `CRYPTO_BUSY`, `HASH_BUSY`, `HOST_CC_IS_IDLE`, DMA busy/interrupt read를 QEMU 측에서 바로 반환 | polling read 비용을 줄일 수 있음. 단, side-effect 없는 read-only ready register로 범위를 제한해야 함 |
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
2. QEMU/RemoteCPU 쪽에서 read-only ready status fast path를 opt-in으로
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

목표는 RSE CC3XX register window를 QEMU/RemoteCPU process 안에서 처리해
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
cmake --build tools/qbox/build \
  --target cc3xx-tests platforms-vp remote_cpu \
  --parallel 8

ctest --test-dir tools/qbox/build \
  -R 'cc3xx-tests' \
  --output-on-failure

python3 scripts/run_qbox_fvp_rd_aspen_rse.py \
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
