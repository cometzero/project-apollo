# Apollo Lua SoC / VP / Board 구현과 검증

작업명: `lua-refactor`. 기준일: 2026-10-02.

요청한 구조 분리와 빌드·설치·부팅 검증을 완료했다. Full-system 기본 boot/post-login, Board I/O, AP-only audio 검사는 통과했다. 아래에 별도 기록한 DMA·BSP selftest·FVP fixture 실패가 있으므로 전체 platform qualification 완료를 뜻하지 않는다.

## 구현

Full-system entry는 `apollo-qvp-saturn-v.lua`이고 기존 `apollo-qvp.lua`는 forwarding한다. AP-only entry는 `apollo-qvp-linux.lua`를 유지한다. 두 entry 모두 조립이 성공한 뒤 최종 `platform`만 global로 공개한다.

- `soc/apollo.lua`: 도메인 metadata 준비, hardware define, AP view 연결, SI define/enable 순서.
- `soc/hw-block/`: AP Compute, RoS, RSE, SMD, SI CL0/CL1별 CPU·memory·syscore·mailbox·interrupt·interconnect leaf.
- `vp/`: 환경변수/options, QEMU instance, boot/console/backing, RSE acceleration, VirtIO, monitor/QMP, AP-only mocks, 시험 wiring.
- `board/hw-block/`: 외부 EEPROM/PCA9539/TPS6594, bus-local I2C 주소 검증. Board 필수 port와 주소 충돌은 오류 처리한다.
- SI PMIC host I2C/GPIO는 `vp/extensions/si-cl0-pmic-host.lua`에 두어 hardware map과 구분한다.

각 module은 local table/function을 반환한다. 옵션을 사용하는 module은 `.create(ctx)`에서 closure를 만들거나 `.define(ctx, platform, ...)`에 명시적으로 전달받는다. 큰 configuration 전역변수를 제거했으며 별도 include DSL이나 `_ENV` 교체를 도입하지 않았다. 정적 literal `dofile`과 source-relative 경로를 사용한다.

파일 계층에 맞춰 runtime container를 추가하지 않았다. `platform.ap_cpu_0`, `platform.si_cl0_gic`, `platform.rse_cpu_pass.cpu_0` 등의 CCI 경로와 `args`/socket/IRQ/reset target 순서를 보존한다. 기기 생성 직전에 중복 이름을 검사하며, intentional routing/backend 변경은 별도 함수에서 명시한다.

Native audio는 기존 address-view 적용 후 `vp/backends/audio.lua`가 최종 QEMU DMA350/I2S descriptor를 적용한다. 생성 순서까지 한 번에 바꾸는 대신 기존 routed target과 IRQ를 보존한 선택이다. AP-only firmware edge의 제거·재연결도 `vp/profiles/linux-direct.lua`에 격리했다. 이 두 compatibility adaptation은 남아 있으며 일반 deep-merge engine으로 확장하지 않았다.

## 함께 변경한 소비자

| 소유 repository | 변경 |
|---|---|
| `qbox-platform` | Lua 계층 분리, canonical entry, Board validation, README |
| `qbox` | Lua 오류에서 CCI export 중단, Lua state RAII 정리, argparser의 실패 검사 |
| `meta-hsoc-bsp` | provider 설치 검사 및 manifest의 canonical entry |
| `meta-hsoc-auto-solutions` | image `.qboxconf`의 canonical entry |
| Root | 런처 기본 경로, old/new process 식별, source graph·AP map·ownership·topology 검사기, 회귀 검사와 문서 |

기존 source indentation/문자열 위치에 의존하던 map 검사는 allowlist 안에서 Lua를 평가한 **최종 descriptor**를 사용하도록 바꿨다. source origin은 진단용이고 주소·IRQ·type·array 순서는 semantic 값으로 검사한다. topology도 동일한 평가 결과를 사용하므로 audio adapter 이후 실제 선택된 backend를 표시한다.

실제 부팅 검증 중 `--keep-running-after-pass --foreground-runtime` 조합에서 child가 `rd-aspen-result.json`을 기록하지만 outer runner가 `result.json`을 읽어 `child_failed:0`을 출력하는 기존 오류를 발견했다. Foreground 종료 시 올바른 child 결과를 읽도록 수정하고 성공·실패·stale 결과·build-only·일반 실행 조합의 회귀 검사를 추가했다. 수정 전 실패 기록은 `full-board-spi-pio/`에, 수정 후 재실행은 `full-final/`에 보존했다.

## 재현 기준과 증거 경로

모든 실행 증거는 root `build/qbox-apollo-qvp/soc-refactor/`에 둔다. [최종 검증 manifest](../../build/qbox-apollo-qvp/soc-refactor/final-validation.json)에 판정과 주요 증거의 SHA-256을 기록했다. `baseline/apollo/`는 수정 전에 보존한 17개 원본 Lua이며 `baseline/build-conf/`와 `baseline/repositories.json`에 구성과 repository 상태를 기록했다. 새 wrapper 두 개끼리의 비교를 기존 baseline 대용으로 사용하지 않았다. 초기 분석 문서의 Lua source link는 이 보존본을 가리킨다. 보존본이 없는 checkout에서는 qbox-platform의 `532d9e8a118a95349b7d75fdc6dfe5958ae5f80b` revision에서 `platforms/apollo/`를 추출해 재현할 수 있다.

`baseline-descriptors.json`은 22개 원본 profile의 `platform` tree와 type을 보존한다. 숫자 key/문자열 key, scalar type, 배열·reset target 순서를 보존한다. 경로 값에 한해 동등한 `..` lexical path를 정규화하고 source origin은 비교에서 제외했다. 그 외 필드 차이는 허용하지 않는다. Native loader가 읽는 `_G` 전체의 CCI preset 동등성 검사는 아니다. 기존 configuration global을 제거한 것은 의도적인 변경이며 global 누출 검사를 별도로 수행했다.

최종 리뷰에서 baseline 일부만 존재해도 비교가 PASS할 수 있는 경로를 수정했다. 요청 profile 누락과 중복 이름을 실행 전에 거부한다. Map 평가 실패 시 원래 Lua 오류 대신 `KeyError`를 출력하던 진단 경로도 수정했다. 실제 22개 baseline은 완전했고, 설치본 비교도 수정한 검사기로 다시 PASS했다.

검사 조합은 full-system AP 1/4/16 CPU, AP-only 1/4/16 CPU와 disk 유무, RSE local/remote crypto·flash·counter/TCM, monitor/QMP/runtime injection, PCIe IRQ/endpoint/EP/NVMe, fault observer다. **구성 비교 PASS와 각 조합의 native boot PASS는 별개다.**

```bash
python3 scripts/test/compare_apollo_lua_descriptors.py compare \
  --baseline build/qbox-apollo-qvp/soc-refactor/baseline-descriptors.json \
  --source-root hsoc-stack/tools/qbox-platform/platforms/apollo \
  --full-entrypoint apollo-qvp-saturn-v.lua \
  --output build/qbox-apollo-qvp/soc-refactor/descriptor-comparison.json
```

## 검증 결과

Machine은 `apollo-qvp`, TMPDIR은 `build/tmp_baremetal`이다. Native provider와 BSP 배포는 shared BitBake에서 순서대로 실행했다. Runtime은 provider 설치본의 106개 Lua와 matching BSP/firmware를 사용했다. 실제 native boot CPU 구성은 AP 4/RSE 1/CL0 1/CL1 4이며, AP 1/16 구성은 descriptor 비교 범위다.

| 항목 | 상태 | 근거 |
|---|---|---|
| 변경 전후 22개 descriptor | PASS | `descriptor-comparison.json`, `descriptor-comparison-lua54.json`; 차이 0 |
| AP/RoS 10개 세부 option 조합 | PASS | `ap-ros/parity.json` |
| RSE/SI 7개 조합 및 reset fanout | PASS | `rse-si/matrix.json` |
| 구조/Board negative tests | PASS | Lua 5.1과 5.4.2에서 27개, `ap-ros/layout-lua54-pytest.log` |
| 구조·소비자·런처/AutoSD/audio helper 회귀 | PASS | 통합 267개 pytest, `pytest.xml` |
| Runner 결과 전달·lifecycle·SI0 회귀 | PASS | 86개, `runner-pytest.xml` |
| Descriptor 비교·오류 처리 회귀 | PASS | 21개, `descriptor-pytest.xml`; 위 세 pytest 실행에서 중복 제거 시 총 301개 |
| Provider build / CTest | PASS | `provider-build.log`; platform 64 + core 61, 기존 slow/unstable 28개 제외 명시 |
| BSP image_complete / 배포 | PASS | 5339 tasks, `bsp-deploy-build.log`; 새 canonical entry |
| 설치 Lua tree / descriptor | PASS | `installed-tree.json`, 106개 hash 일치; 설치본 22개 descriptor 일치 |
| Native 실패 전달 | PASS | `native-errors/result.json`, `/tmp` cwd에서 6개 오류 모두 nonzero 종료 |
| Full/AP map 및 ownership | PASS | `full-map.json` 95/95, `ap-map.json`, `lua-ownership.json` 333개 객체 |
| 기본 full-system boot / BSP / post-login / timer | PASS | `full-final/result.json`; G0/G1/G2 pass, BSP READY, 8개 driver pattern, model timer snapshot |
| 최종 coverage 감사 | PASS | `final-runtime-coverage.json` 49개 항목; 지정된 gate 범위 |
| Full-system 기본 SPI DMA probe | FAIL — 원본 동일 | `full-system/`, `baseline-runtime/`, `spi-dma-baseline-comparison.json`; SPI 검사 중 `d350_irq` panic 재현 |
| Board PCA9539·EEPROM·PMIC | PASS | `final-qualification.json`, `pmic-qualification.json`; PCA GPIO/IRQ/reset, EEPROM 복원, PMIC identity. PMIC rail/GPIO는 SKIP |
| I2C EEPROM / SPI PIO | PASS | `final-qualification.json`; I2C 6개 bus, SPI 4개 controller의 8-byte loopback. SPI DMA 판정과 별개 |
| Full-system monitor/QMP | PASS | `final-qualification.json`; 4개 domain running·CPU 수·version, 안정적인 CCI object 경로 |
| UART DMA traffic | FAIL | `full-qualified-no-spi/`; channel 7 CH_CMD 접근 시 reentrancy guard 차단 |
| AP-only boot / audio DMA·PIO | PASS | `ap-only-audio/result.json`; mode별 PCM 4회, 양방향 WAV exact match, IRQ 진행, DMA memcpy/memset |
| AP-only BSP selftest | FAIL | DMA·PIO 모두 `pfdi_misc` 실패. Audio suite의 PASS와 별도 |
| PCIe FVP reference gate fixture | FAIL | `pcie-contract-pytest.xml`; 보존 FVP JSON 부재, 다른 Lua graph/hash 계약 8개 PASS |

Lua 5.4.2 CLI는 provider의 동일 dependency source와 `liblua.so`로 별도 빌드했다(`build-lua-tool.sh`). 시스템 기본 `lua` 5.1.5의 문법 검사와 구분한다. StyLua/Luacheck 설치 또는 실행은 주장하지 않는다.

커밋 준비 시 신규 Lua 8개 파일의 줄 끝 공백만 제거했다. 기존 설치본 106개 hash와 build/runtime 증거는 이 공백 정리 전 source에 해당한다. 정리 후 22개 descriptor 비교는 다시 PASS했으며 결과는 `commits/descriptor-comparison.json`, 전후 hash는 `commits/whitespace-cleanup.json`에 보존했다. 공백 정리를 이유로 native 재빌드·부팅을 반복하지 않았다.

주요 실행 명령:

```bash
./yocto_build.sh --keep-conf qbox-apollo-qvp-native
./yocto_build.sh --keep-conf nexios-bsp-initramfs -c image_complete
python3 build/qbox-apollo-qvp/soc-refactor/run-final.py
python3 scripts/test/audit_qbox_apollo_fvp_full_coverage.py \
  --result-json build/qbox-apollo-qvp/soc-refactor/full-final/result.json \
  --ap-map-audit build/qbox-apollo-qvp/soc-refactor/ap-map.json \
  --output build/qbox-apollo-qvp/soc-refactor/final-runtime-coverage.json
python3 scripts/test/verify_qbox_linux_audio.py \
  --conf build/tmp_baremetal/sysroots-components/x86_64/qbox-apollo-qvp-native/usr/share/qbox/platforms/apollo/apollo-qvp-linux.lua \
  --out-dir build/qbox-apollo-qvp/soc-refactor/ap-only-audio \
  --mode both --timeout 600
```

`run-final.py`는 이 실행의 evidence harness다. `final-command.json`에 canonical Python runner의 전체 인자와 환경을 기록하며, 입력 WIC/capsule disk는 원본 복사본을 사용한다. Monitor는 loopback 주소, QMP는 실행별 경로를 사용했다. Board 검사는 실제 UART FIFO로 guest script를 실행하고 반환값과 controller별 성공 marker를 모두 확인했다. 검사가 끝나면 해당 harness가 시작한 native process만 종료한다. CTest의 실행·제외 목록과 XML은 `ctest/`에 있다.

## 증거 해석 범위

Saturn-V schematic/BOM 일치는 `UNVERIFIED`다. Board population과 test loopback은 현재 QVP의 구성을 보존했다. PMIC 최소 identity probe PASS는 rail/GPIO 전체 qualification을 뜻하지 않는다. 구조·부팅·IO 검사로 physical timing, coherence, FVP/RTL parity, 전원/reset 전체 경로를 판정하지 않는다. 이전 full-system audio 제한은 이 refactor만으로 해소됐다고 간주하지 않는다.

Full-system post-login PASS는 요청된 기본 driver gate의 판정이다. Secure-service/FWU/RAS 전체 검증을 요청하지 않았으며, 해당 진단의 미지원·오류 관측을 숨기지 않았다. AP-only는 다른 domain을 mock으로 대체한다. 두 audio mode에서 `pfdi_misc` BSP selftest FAIL을 관측했고, 이를 AP-only audio PASS로 덮어쓰지 않았다.

## 실행 중 확인한 DMA 실패

기본 full-system DWC probe는 SPI DMA에서 `d350_irq()`의 channel 1 `CH_STATUS`
읽기(offset `0x1104`)가 거부되며 kernel panic한다. 변경 전 Lua snapshot을 같은
binary/image/옵션으로 실행해 같은 실패를 재현했다. Lua 분리로 발생한 새 SPI 회귀로
판정할 근거는 없다. 기본 probe의 FAIL을 삭제하거나 PIO 검사로 대체하지 않았다.

후속 UART 전송은 `d350_pause()` → UART RX DMA flush 경로에서 channel 7 `CH_CMD`
쓰기(offset `0x1700`)가 거부된다. `full-qualified/` 및 `full-qualified-no-spi/`에
별도 FAIL을 남겼다. UART의 변경 전 runtime 비교는 수행하지 않았으므로 SPI의 원본
재현 결과와 구분한다.

QEMU `hw/dma/arm-dma350.c`는 DMA 서비스 중 reentrancy guard를 유지하고,
`system/memory.c`는 그 상태의 접근을 `MEMTX_ACCESS_ERROR`로 거부한다. SystemC ACK
전달 중 iothread lock을 풀어 동기 실행하는 QBox wrapper와의 scheduling 충돌이
가능한 원인이다. 상세 interleaving은 추가 trace가 필요하며 이번 변경에서는
DMA/QEMU/driver 동작을 수정하지 않았다.

별도 PCIe reference-gate 계약 테스트는 보존된 FVP evidence
`.omo/evidence/apollo-gic-its/final/F2/cycle2/integration-current/fvp-reference-gate-current.json`
부재로 1건 FAIL이다. 검증 기준을 낮추거나 FVP evidence를 합성하지 않았다.
Lua graph/hash와 관련한 다른 PCIe 계약 8건은 PASS다.
