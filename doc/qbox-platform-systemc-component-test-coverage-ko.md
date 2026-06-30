# qbox-platform SystemC Components 테스트 검증 범위 분석

작성일: 2026-06-30

## 범위와 방법

이 문서는 현재 `tools/qbox-platform/systemc-components`에서 제공하는
SystemC 컴포넌트별로 `tools/qbox-platform/tests/components`에서 어떤
동작을 검증하는지 정리한다.

분석 기준은 다음 파일과 디렉터리이다.

| 항목 | 기준 |
| --- | --- |
| 컴포넌트 목록 | `tools/qbox-platform/systemc-components`의 1-depth 디렉터리 |
| 테스트 구현 | `tools/qbox-platform/tests/components/<component>` |
| 현재 top-level CTest 등록 | `tools/qbox-platform/CMakeLists.txt`의 `QBOX_PLATFORM_SYSTEMC_COMPONENT_TESTS` |
| tests/components 전체 목록 | `tools/qbox-platform/tests/components/CMakeLists.txt` |
| 재현 스크립트 | `scripts/analyze_qbox_platform_systemc_tests.py` |

## 핵심 요약

현재 qbox-platform SystemC 컴포넌트는 25개이다. 이 중 24개는 같은
이름의 테스트 디렉터리를 가지고 있고, `ras_ffh_stub`만 직접 대응되는
테스트 디렉터리가 없다.

주의할 점은 테스트 소스 존재 여부와 현재 top-level 빌드에서 CTest로
등록되는지가 항상 같은 의미는 아니라는 것이다. 현재
`tools/qbox-platform/CMakeLists.txt`는 `QBOX_PLATFORM_SYSTEMC_COMPONENT_TESTS`
목록을 통해 직접 테스트 디렉터리가 있는 24개 SystemC 컴포넌트를
top-level CTest에 등록한다. 직접 테스트 디렉터리가 없는 항목은
`ras_ffh_stub` 하나이다.

| 구분 | 컴포넌트 |
| --- | --- |
| top-level CTest 등록 | `cc3xx`, `dma350`, `gic720ae_messreg`, `gicx00_multiview`, `host_cmn_cyprus`, `host_gtimer`, `host_ni710ae_nci`, `host_ppu`, `host_scr`, `host_smcf_mgi`, `host_system_pll`, `mhu320ae`, `mmu720ae`, `reset_fanout`, `rse_atu`, `rse_integrity_checker`, `rse_kmu`, `rse_lcm`, `rse_protection_ctrl`, `rse_sam`, `rse_sysctrl`, `strata_flash_j3`, `zena_fmu`, `zena_ssu` |
| 테스트 소스는 있으나 top-level 미등록 | 없음 |
| 직접 테스트 디렉터리 없음 | `ras_ffh_stub` |

## 컴포넌트별 테스트 검증 범위

| 컴포넌트 | 테스트 타깃 | top-level CTest | tests에서 검증되는 부분 | 남은 gap |
| --- | --- | --- | --- | --- |
| `cc3xx` | `cc3xx-tests`, `cc3xx_core-tests`, `qemu_cc3xx-tests`, `rse_lms_accel-tests`, `rse_mcuboot_image-tests`, `rse_p256_ecdsa-tests` | 예 | TF-M 초기 read readiness에 필요한 reset/status 값, reset signal 복구, RNG 제어/entropy read, PKA SRAM cursor와 opcode 실행, SHA-256 empty/multipart/final block, AES CTR/ECB/CMAC DMA, DMA interrupt clear, trace filter, stats histogram, QEMU wrapper type export, LMS/MCUboot/P-256 helper 동작을 검증한다. | 실제 QEMU 통합 부팅 흐름보다는 register/model 단위 동작 중심이다. |
| `dma350` | `dma350-tests` | 예 | BL1 polling에 필요한 reset 값, channel command 즉시 완료, fill/copy command, xsize high bit 처리, trace copy filter와 address threshold, unsupported/out-of-range transaction reject를 검증한다. | 실제 DMA timing/ordering은 검증하지 않는다. |
| `gic720ae_messreg` | `gic720ae_messreg-tests` | 예 | message register reset-to-zero, value store/load, unsupported size, out-of-range access, unsupported command, debug transport read/write 보존을 검증한다. | GIC-720AE 전체 distributor/redistributor/ITS 동작이 아니라 messreg 보조 register block만 다룬다. |
| `gicx00_multiview` | `gicx00_multiview-tests` | 예 | view/power-on reset 상태, distributor view field, Apollo SPI range와 range 밖 RAZ/WI, AP/Safety Island view table, redistributor view/power/flush register, invalid access, debug transport를 검증한다. | interrupt delivery나 GIC CPU interface 동작은 별도 GIC 모델 영역이다. |
| `host_cmn_cyprus` | `host_cmn_cyprus-tests` | 예 | CFGM root/MXP discovery, 8개 HNS node와 RN-SAM 노출, RN-SAM range comparison mode, firmware programming write 보존, unseeded register zero, 1GiB window 밖 reject를 검증한다. | interconnect timing/ordering은 검증하지 않는다. |
| `host_gtimer` | `host_gtimer-tests` | 예 | counter low word 진행, frequency register, 일반 register write 보존을 검증한다. | timer interrupt, compare event, 다중 counter view는 검증 범위 밖이다. |
| `host_ni710ae_nci` | `host_ni710ae_nci-tests` | 예 | MHU MID topology, RSE MM ASNI, Apollo primary configured component 노출, APU region/control write 보존, configurable/read-only IIDR, primary component별 distinct APU block을 검증한다. | NCI topology discovery/register profile 중심이며 실제 bus protection enforcement는 별도 범위다. |
| `host_ppu` | `host_ppu-tests` | 예 | power policy write에 따른 power status, emulator register write, dynamic policy status bit, power-on transition에서 reset release 전 load signal 발생을 검증한다. | 실제 전력 도메인 latency 모델은 다루지 않는다. |
| `host_scr` | `host_scr-tests` | 예 | CL1 present reset value, CL0 reset config, writable control register 보존, PCID reset 값, AP SID parameterization, SID identity register read-only, out-of-window reject, system config read-only를 검증한다. | SCR이 제어하는 전체 platform side effect까지는 검증하지 않는다. |
| `host_smcf_mgi` | `host_smcf_mgi-tests` | 예 | Apollo 1-monitor MGI reset profile, configurable monitor count encoding, monitor/mode request 즉시 status 반영, sample enable busy 미보고, IRQ status write-one-to-clear, 전체 mapped region readable을 검증한다. | 성능 모니터링의 실제 sampling 데이터 생성은 검증하지 않는다. |
| `host_system_pll` | `host_system_pll-tests` | 예 | PLL write 후 locked status 즉시 보고, configurable lock mask를 검증한다. | clock tree propagation이나 주파수 산출은 검증하지 않는다. |
| `mhu320ae` | `mhu320ae-tests` | 예 | PBX/MBX doorbell/status/IRQ register 재사용 가능성, RSE BL2 power-domain transport 응답, reset/IRQ 연계, SCMI base/power/performance 응답, PSA measured boot/FWU/PS storage 서비스 흐름, AP/RSE bridge doorbell 전달을 검증한다. | MHU-320AE 전체 channel/window matrix를 포괄적으로 fuzzing하지는 않고 Apollo RSE BL2 부팅 handshake와 서비스 transport 중심이다. |
| `mmu720ae` | `mmu720ae-register-tests`, `mmu720ae-queue-tests`, `mmu720ae-tbu-tests` | 예 | implemented feature reset profile, CR0 write와 CR0ACK/generation invalidation, page1 queue alias, queue/MSI 64-bit write, unsupported access reject, command queue sync completion, IRQ/GERROR clear, disabled SMMU bypass, enabled SMMU fault event, ACE2 default SID와 ACE1 SID extension을 검증한다. | 정상 page table walk/translation 성공 경로보다는 probe/queue/fault 중심이다. |
| `ras_ffh_stub` | 없음 | 아니오 | 직접 대응되는 테스트 디렉터리가 없다. | 현재 SystemC component 목록 중 직접 테스트가 없는 유일한 항목이다. stub 특성상 필요한 최소 register/firmware-facing 동작을 별도 테스트로 명시할 필요가 있다. |
| `reset_fanout` | `reset_fanout-tests` | 예 | 입력 reset 값과 pulse를 모든 target sink로 broadcast하는 동작을 검증한다. | 복잡한 reset sequencing/timing은 검증하지 않는다. |
| `rse_atu` | `rse_atu-tests` | 예 | TF-M expectation에 맞는 build config reset, page size/region count preset, region programming register, interrupt clear, out-of-range reject, enabled region translation, high SI PIK region offset, unmapped/disabled/span/overflow/underflow/domain mismatch latch, translated DMI grant/reject, trace filter와 DMI trace를 검증한다. | 단위 테스트 범위는 비교적 넓지만 통합 부팅 경로의 ATU 정책 검증은 별도이다. |
| `rse_integrity_checker` | `rse_integrity_checker-tests` | 예 | TF-M driver expectation reset 값, programming register write, start-completion-clear flow, read-only register write ignore, out-of-range reject를 검증한다. | 실제 integrity algorithm 계산은 모델링하지 않는 register-facing 검증이다. |
| `rse_kmu` | `rse_kmu-tests` | 예 | TF-M reset 값, init seed/interrupt register write, reset signal 복구, key ready/export/invalidate completion, key slot word write, key trace filter, OTP image에서 KCE CM hardware slot load, out-of-range reject를 검증한다. | 실제 crypto key ladder 보안 속성은 모델 범위 밖이다. |
| `rse_lcm` | `rse_lcm-tests` | 예 | provisioned lifecycle reset, configured TCI/TP mode, secure provisioning magic self-complete, lifecycle identity read-only, OTP window write, OTP image load/writeback, provisioning 후 OTP lock, out-of-range reject를 검증한다. | 실제 one-time programmable 물리 제약은 파일/상태 모델 수준이다. |
| `rse_protection_ctrl` | `rse_protection_ctrl-tests` | 예 | MPC profile seeded reset 값 보존, lock 후 write 차단, non-secure write deny와 latch, compatibility allow mode를 검증한다. | downstream bus 차단 효과는 register-level policy 검증에 가깝다. |
| `rse_sam` | `rse_sam-tests` | 예 | TF-M driver expectation reset 값, programming register write, read-only register write ignore, event clear register write, out-of-range reject를 검증한다. | 주소 remap 또는 security attribution의 full path 검증은 없다. |
| `rse_sysctrl` | `rse_sysctrl-tests` | 예 | FVP RSE boot configuration reset 값, CCI parameter override, touched register read/write, secure debug set/clear status, software reset write가 simulation을 중단하지 않는 동작, unsupported/out-of-range reject를 검증한다. | platform-wide reset side effect는 제한적이다. |
| `strata_flash_j3` | `strata_flash_j3-tests` | 예 | image load/read array mode, RSE boot flash loader path, read-id/status command, NOR bit-clear program semantics, optional `0xff` program restore, sector erase compatibility, write buffer programming, read-only DMI와 array mode DMI grant, DMI range/invalidations, backing file write-through/deferred flush, noop/erased-sector write skip, stats counters, reject DMI를 검증한다. | flash command/DMI/backing-file coverage는 넓지만 timing model은 다루지 않는다. |
| `zena_fmu` | `zena_fmu-tests` | 예 | documented PCID reset 값, SYS_KEY가 필요한 register gating, status write-one-to-clear, critical/non-critical status에 따른 fault signal을 검증한다. | FMU integration 대상 장치별 fault propagation까지는 검증하지 않는다. |
| `zena_ssu` | `zena_ssu-tests` | 예 | documented reset register, SYS_KEY gated register, status detail low 16-bit 보존, sysctrl write가 visible state에 반영되는지, fault input이 status/safety output을 set하는지를 검증한다. | 다른 Zena safety block과의 통합 fault flow는 별도 검증이 필요하다. |

## 테스트 등록 상태 상세

| 상태 | 의미 | 컴포넌트 |
| --- | --- | --- |
| 직접 실행 경로 있음 | 현재 qbox-platform top-level CMake에서 `QBOX_PLATFORM_SYSTEMC_COMPONENT_TESTS`를 통해 등록된다. | `cc3xx`, `dma350`, `gic720ae_messreg`, `gicx00_multiview`, `host_cmn_cyprus`, `host_gtimer`, `host_ni710ae_nci`, `host_ppu`, `host_scr`, `host_smcf_mgi`, `host_system_pll`, `mhu320ae`, `mmu720ae`, `reset_fanout`, `rse_atu`, `rse_integrity_checker`, `rse_kmu`, `rse_lcm`, `rse_protection_ctrl`, `rse_sam`, `rse_sysctrl`, `strata_flash_j3`, `zena_fmu`, `zena_ssu` |
| 소스는 있으나 기본 실행 경로 없음 | 직접 테스트 디렉터리가 있는 SystemC 컴포넌트 중 현재 top-level CTest에서 빠진 항목이다. | 없음 |
| 테스트 없음 | 같은 이름의 테스트 디렉터리가 없다. | `ras_ffh_stub` |

## 실행과 검증 관점의 해석

현재 top-level 빌드에서 `ctest -L qbox-platform-systemc-components`로
자연스럽게 검증되는 범위는 직접 테스트 디렉터리가 있는 24개 SystemC
컴포넌트 전체이다. qbox-platform SystemC component test coverage를
"소스에 테스트가 있는가" 기준으로 보면 24/25가 대응 테스트를 갖고,
"현재 qbox-platform top-level에서 자동 실행되는가" 기준으로도 24/25가
등록되어 있다.

남은 구조적 gap은 `ras_ffh_stub`처럼 직접 테스트 디렉터리가 없는
컴포넌트와, 각 단위 테스트가 명시적으로 다루지 않는 timing, full-path
integration, 실제 보안 속성 검증 영역이다.

## 재현 명령

보고서와 현재 소스 트리의 일치 여부는 다음 명령으로 확인한다.

```bash
python3 scripts/analyze_qbox_platform_systemc_tests.py \
  --markdown doc/qbox-platform-systemc-component-test-coverage-ko.md \
  --check-coverage

python3 scripts/analyze_qbox_platform_systemc_tests.py --check-stale

python3 scripts/analyze_qbox_platform_systemc_tests.py \
  --markdown doc/qbox-platform-systemc-component-test-coverage-ko.md \
  --check-links
```

JSON 형태의 원자료가 필요하면 다음 명령을 사용한다.

```bash
python3 scripts/analyze_qbox_platform_systemc_tests.py --json
```
