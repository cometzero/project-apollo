# QBox CC3XX QEMU-Native Backend Spec

작성일: 2026-06-04

상태: 구현 및 검증 완료

관련 문서:

- `doc/qbox-rse-boot-slow-path-analysis-ko.md`
- `doc/qbox-cc3xx-qemu-native-design-ko.md`
- `doc/qbox-cc3xx-qemu-native-plan-ko.md`
- `doc/qbox-cc3xx-qemu-native-tasks-ko.md`

## 목표

RSE TF-M BL1_2의 BL2 image validation slow path를 줄이기 위해 현재
SystemC-only `cc3xx` 모델에서 register/crypto 동작을 `cc3xx_core`로
분리하고, 같은 core를 사용하는 QEMU-native CC3XX backend를 추가한다.

최종 backend는 secure boot 검증을 우회하지 않는다. QEMU CPU가 접근하는
RSE CC3XX MMIO hot path를 QEMU `MemoryRegionOps` callback 안에서 처리해
QEMU TCG CPU -> QBox initiator -> SystemC/TLM target 왕복을 줄이는 것이
목표다.

## 문제 정의

현재 RSE boot 병목은 RSE 전체가 아니라 TF-M BL1_2가 BL2 image를 복호화한
뒤 서명 검증을 완료하는 구간이다.

| Run | `rse_bl2_decrypted` -> `rse_bl2_validated` |
| --- | ---: |
| QBox RSE SystemC baseline | 167.863초 |
| QBox RSE local MMIO fast path | 152.884초 |
| QBox RSE local MMIO + status-read fast path | 151.321초 |
| QBox RSE qemu-native + direct MMIO fast path | 133.339초 |
| FVP timed boot 기준 | 1.437초 |

`--cc3xx-local-mmio-fastpath`는 scheduler bridge 비용 일부를 줄였고,
qemu-native backend는 같은 `cc3xx_core` register model을 QEMU
`MemoryRegionOps` callback으로 노출해 local-MMIO 대비 BL2 validation delta를
151.321초에서 133.339초로 줄였다. 최신 histogram run 기준 CC3XX access는
1,638,400회이며, top traffic은
`CRYPTO_BUSY`, `HASH_H0..7`, `AUTO_HW_PADDING`, `CRYPTO_CTL` 같은 HASH/SHA
validation register에 집중되어 있다.

## 공식/로컬 문서 조사

- Arm public guide인
  [Arm CryptoCell-312 Guide to Generate and Verify Secure Boot and Secure
  Debug Certificate Chains](https://documentation-service.arm.com/static/62c415b831ea212bb6625a8d)는
  CryptoCell-312의 secure boot certificate chain verification이 hash,
  RSA-PSS SHA-256, image hash/encryption metadata를 사용한다는 boot-service
  관점을 확인해 준다. 이 문서는 integration/usage guide이며 register-level
  TRM은 아니다.
- `doc/arm_zena_css_dev_guide/09-programmers-model-for-zena-css.md`는 Zena CSS
  RSE memory map과 interrupt map의 로컬 기준 문서다. RSE peripheral expansion
  영역은 `0x5010_0000..0x57ff_ffff`이고, secure cryptographic device interrupt
  58이 정의되어 있다.
- 현재 checkout과 공개 Arm 문서 조사 범위 안에서는 CC312/CC3XX register-level
  TRM을 확인하지 못했다. 따라서 초기 구현은 현재 QBox `cc3xx` 모델, TF-M driver
  관찰 동작, Zena CSS memory/interrupt map, 기존 unit/runtime tests에 근거한다.
  라이선스된 TRM을 사용할 수 있게 되면 reset value, register side effect, DMA,
  error, IRQ semantics를 별도 fidelity review로 재검증해야 한다.

## 근거

- 현재 모델은 `tools/qbox/systemc-components/cc3xx/include/cc3xx.h`의
  단일 `sc_module` 안에 register file, PKA/HASH/AES/CMAC/RNG state,
  DMA access, trace, stats, CCI parameter, TLM socket이 함께 있다.
- `cc3xx.h`의 `mem_read()`와 `mem_write()`만 외부 memory access boundary다.
  나머지 register side effect와 crypto state machine은 QEMU wrapper와
  SystemC wrapper가 공유할 수 있다.
- RSE secure peripheral map에서 CC3XX는
  `tools/qbox/platforms/fvp-rd-aspen-rse/conf.lua`의
  `RSE_CC3XX_BASE_S = 0x50154000`이며 현재 window size는 `0x2000`이다.
- RSE KMU는 hardware slot export fallback address로 `0x50154400`을 쓰므로,
  QEMU-native backend도 KMU의 SystemC/TLM cold-path write를 받을 수 있어야
  한다.
- QBox libqemu wrapper는 `qemu::MemoryRegionOps::set_read_callback()`,
  `set_write_callback()`, `qemu::MemoryRegion::init_io()`,
  `qemu::AddressSpace::read/write()`를 제공한다.

## 범위

이 스펙의 구현 범위는 다음이다.

- `cc3xx_core` 공통 register/crypto/DMA side-effect class 추가.
- 기존 SystemC `cc3xx`를 core adapter로 전환.
- QEMU-native `qemu_cc3xx` backend 추가.
- RSE local crypto path에서 backend를 opt-in으로 선택하는 Lua/runner wiring.
- 단위 테스트, RSE boot timing 검증, full-system regression 검증.

## 비목표

- TF-M LMS/LMOTS secure boot 검증 자체를 skip하지 않는다.
- known-good image hash fast verify, signature bypass, BL2 validation stub은
  이 스펙의 대상이 아니다.
- AP Linux direct boot 성능 개선은 대상이 아니다.
- CC3XX full TRM coverage를 한 번에 완성하지 않는다. 현재 boot에 필요한
  SHA-256, AES-CTR/ECB/CMAC, observed PKA, RNG readiness, DMA/status
  semantics parity를 우선한다.

## 기능 요구사항

### FR1. 공통 Core

`cc3xx_core`는 다음 상태와 동작을 소유한다.

- register file과 reset values
- PKA SRAM, PKA opcode execution, status flags
- SHA-256 state restore/update/finalize
- AES-CTR, AES-ECB, AES-CMAC paths
- RNG readiness/status side effects
- DMA trigger side effects and `HOST_RGF_IRR`/`HOST_RGF_ICR` handling
- access counters and register histogram counters

`cc3xx_core`는 `sc_core`, TLM socket, CCI, QEMU object에 의존하지 않는다.
SystemC/QEMU wrapper만 외부 bus ownership과 scheduling을 처리한다.

### FR2. SystemC Wrapper Parity

기존 `moduletype = "cc3xx"` 동작은 기본값으로 유지한다. Core 분리 후에도
기존 `cc3xx-tests`가 동일하게 통과해야 하며, RSE SystemC backend runtime
marker와 `rse-cc3xx-stats.json` 구조가 유지되어야 한다.

### FR3. QEMU-Native Backend

새 backend는 `moduletype = "qemu_cc3xx"`로 제공한다. CPU MMIO read/write는
QEMU `MemoryRegionOps` callback에서 `cc3xx_core`로 직접 들어가야 한다.

QEMU-native backend도 SystemC/TLM target view를 제공해야 한다. 이유는 KMU
같은 SystemC peripheral이 CC3XX window에 key export write를 수행하기
때문이다.

### FR4. DMA Access

Core는 DMA memory access를 callback interface로 요청한다. QEMU wrapper는
가능하면 QEMU `AddressSpace::read/write()`를 사용하고, QEMU address space로
해결되지 않는 window에 대해서만 제한된 TLM fallback을 사용한다.

TLM fallback은 QEMU iothread와 SystemC thread ownership을 명시적으로
처리해야 하며 direct recursive call로 deadlock을 만들면 안 된다.

### FR5. Opt-In Runtime Selection

기본 backend는 기존 SystemC path다. QEMU-native backend는 명시 옵션으로만
활성화한다.

요구되는 사용자 인터페이스:

```bash
python3 scripts/run_qbox_fvp_rd_aspen_rse.py \
  --cc3xx-qemu-native-backend
```

Lua 환경 변수는 다음 이름을 사용한다.

```text
QBOX_RDASPEN_CC3XX_BACKEND=systemc|qemu-native
```

`--cc3xx-qemu-native-backend`는 같은 CC3XX window에 대해
`QBOX_MMIO_DIRECT_FASTPATH_RANGES=0x50154000:0x2000`도 자동 적용한다. 이것은
QEMU CPU MMIO가 새 QEMU memory region backend로 직접 들어가도록 하기 위한
성능 옵션이며, secure boot validation을 skip하지 않는다. `result.json`과
fidelity label에는 어떤 backend가 사용되었는지 기록한다.

## 비기능 요구사항

- **Fidelity:** secure boot success/negative behavior를 숨기지 않는다.
- **Performance:** RSE BL2 validation delta가 local-MMIO fastpath 대비 10%
  이상 감소해야 성능 pass로 본다.
- **Reproducibility:** 모든 runtime 검증은 file-backed output directory에
  `result.json`, UART logs, `rse-cc3xx-stats.json`을 남긴다.
- **Maintainability:** SystemC backend와 QEMU backend가 register semantics를
  복제하지 않는다.
- **Reviewability:** backend 선택, fidelity debt, remaining unsupported
  behavior가 machine-readable output에 남는다.

## 수락 기준

다음 조건을 구현 완료 기준으로 사용한다.

| ID | 기준 | 상태 |
| --- | --- | --- |
| AC1 | `cc3xx_core`가 SystemC/TLM/CCI/QEMU 의존성 없이 빌드된다. | 충족 |
| AC2 | 기존 `cc3xx-tests`가 core split 후에도 통과한다. | 충족 |
| AC3 | core-only tests가 reset, HASH, AES DMA, CMAC, PKA, interrupt clear, unsupported access를 검증한다. | 충족 |
| AC4 | `qemu_cc3xx` target이 빌드되고 Lua platform에서 opt-in으로 선택된다. | 충족 |
| AC5 | RSE narrow run에서 `rse_bl2_decrypted`, `rse_bl2_validated`, `rse_jump_bl2`, `rse_image_4_loaded` marker가 유지된다. | 충족 |
| AC6 | QEMU-native validation delta가 local-MMIO fastpath run보다 10% 이상 낮다. | 충족: 151.321초 -> 133.339초 |
| AC7 | full-system run에서 backend label이 secure boot skip이 아닌 QEMU-native model로 기록된다. | 충족: `build/qbox-apollo-fvp/cc3xx-qemu-native-20260605-003557/full/result.json` |
| AC8 | 기존 direct boot guardrail이 regression 없이 유지된다. | 충족: `build/qbox-apollo-fvp/direct-guardrail-20260605-004025/result.json` |

RSE 단독 runner의 최종 verdict는 기존 RSE-oriented 경로와 동일하게
`qbox_platform_timeout`일 수 있다. 이 스펙의 RSE acceptance는 timeout verdict가
아니라 RSE secure boot marker parity와 BL2 validation delta를 기준으로 한다.

## 리뷰 기준

리뷰어는 다음을 fail 조건으로 본다.

- `cc3xx_core`가 `sc_core`, TLM socket, CCI, QEMU object를 include한다.
- SystemC `cc3xx`와 QEMU `qemu_cc3xx`가 register side effect를 별도로
  구현한다.
- QEMU-native backend가 default로 켜진다.
- QEMU-native path가 BL2 validation을 skip하거나 known-good image만
  shortcut 처리한다.
- RSE CC3XX window를 `0x2000`보다 크게 잡아 `0x5015A000` 이후 syscounter,
  integrity checker, TRAM 영역과 겹친다.
- runtime pass가 tmux 화면 출력만으로 주장된다.
