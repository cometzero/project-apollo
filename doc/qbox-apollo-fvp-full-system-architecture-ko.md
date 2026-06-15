# QBox Apollo FVP Full-System 구현 및 SW Architecture

생성일: 2026-06-03

상태: 구현 및 검증 완료

이 문서는 Apollo FVP full-system QBox 구현의 전체 소프트웨어 구조,
설계 의도, 구현 범위, 검증 모델을 한국어로 정리한다. 세부 acceptance
contract는
`doc/qbox-apollo-fvp-full-system-goal-verification.md`를 기준으로 한다.

## 목적

목표는 로컬 Apollo FVP 부팅 산출물을 QBox에서 FVP와 같은 subsystem
흐름으로 실행하는 것이다.

```text
RSE TF-M -> SI CL0 SCP-firmware -> SI CL1 Zephyr
         -> AP TF-A -> OP-TEE -> U-Boot -> Linux
```

단순히 Linux shell에 도달하는 것이 목표가 아니다. RSE, Safety Island
CL0, Safety Island CL1, Primary Compute가 같은 QBox 실행 안에서 모두
동작하고, cross-domain handoff와 boot-critical hardware block이 로그와
JSON evidence로 확인되어야 한다.

## 구현 범위

이번 구현은 세 repository 경계에 걸쳐 있다.

| Repository | 구현 내용 |
| --- | --- |
| Workspace root | full-system runner, map validator, coverage audit, strict verifier, 한국어/영어 설계 문서 |
| `tools/qbox` | Apollo full-system Lua platform, Safety Island CL1 단독 platform, SystemC/TLM host models, Cortex-R82 wrapper 조정, component tests |
| `tools/qemu` | Cortex-R82 architectural feature 보강 |

주요 커밋은 다음과 같다.

| 위치 | 커밋 | 요약 |
| --- | --- | --- |
| root | `366f9c544bdb` | `feat(qbox): verify Apollo full system` |
| `tools/qbox` | `5840f3eaef90` | `feat(apollo): add full-system platform` |
| `tools/qemu` | `9743cfc25f1e` | `feat(arm): complete Cortex-R82 features` |

## 기존 경로와 새 경로

기존 Apollo QBox 경로는 Primary Compute Linux를 직접 부팅한다.

```text
scripts/run/run_qbox_apollo_fvp_linux.py
./local-build.sh qbox
tools/qbox/platforms/apollo/apollo-pc.lua
```

이 경로는 Linux kernel, initramfs, AP device model 검증에는 빠르다.
하지만 RSE, TF-A, OP-TEE, U-Boot, Safety Island CL0/CL1을 우회하므로
full-system 완료 증거로 사용할 수 없다.

새 full-system 경로는 RSE-first firmware chain을 기준으로 한다.

```text
scripts/run/run_qbox_apollo_fvp_full.py
./local-build.sh qbox
scripts/run/run_qbox_apollo_fvp_si_cl1.py
scripts/test/validate_qbox_apollo_fvp_full_map.py
scripts/test/audit_qbox_apollo_fvp_full_coverage.py
scripts/test/verify_qbox_apollo_fvp_full_completion.py
tools/qbox/platforms/apollo/apollo-qvp.lua
tools/qbox/platforms/apollo/apollo-si-cl1.lua
```

## 전체 SW Architecture

```text
+---------------------------------------------------------------+
| User / CI                                                     |
|  - run_qbox_apollo_fvp_full.py                                |
|  - validate_qbox_apollo_fvp_full_map.py                       |
|  - audit_qbox_apollo_fvp_full_coverage.py                     |
|  - verify_qbox_apollo_fvp_full_completion.py                  |
+-------------------------------+-------------------------------+
                                |
                                v
+---------------------------------------------------------------+
| QBox Lua Platform                                              |
|  tools/qbox/platforms/apollo/apollo-qvp.lua                      |
|  - RD-Aspen RSE-first topology reuse                           |
|  - Apollo AP logical view router                               |
|  - live SI CL0 option                                          |
|  - live SI CL1 option                                          |
|  - service-model / live-cl1 / live-cl0-cl1 modes               |
+-------------------------------+-------------------------------+
                                |
                                v
+---------------------------------------------------------------+
| SystemC/TLM Host Models                                        |
|  - gicx00_multiview                                            |
|  - mhu320ae                                                    |
|  - host_cmn_cyprus                                             |
|  - host_gtimer                                                 |
|  - host_ni710ae_nci                                            |
|  - host_smcf_mgi                                               |
|  - host_system_pll                                             |
|  - host_ppu / host_scr                                         |
|  - reset_fanout                                                |
+-------------------------------+-------------------------------+
                                |
                                v
+---------------------------------------------------------------+
| QEMU/libqemu Domains                                           |
|  - Cortex-M55 RSE                                              |
|  - Cortex-R82 Safety Island CL0                                |
|  - Cortex-R82 Safety Island CL1 x4                             |
|  - Cortex-A720AE Primary Compute x4                            |
|  - QEMU GICv3 backends                                         |
+-------------------------------+-------------------------------+
                                |
                                v
+---------------------------------------------------------------+
| Local Apollo Artifacts                                         |
|  - TF-M RSE ROM/flash/OTP                                      |
|  - SCP-firmware SI CL0                                         |
|  - Zephyr SI CL1                                               |
|  - TF-A / OP-TEE / U-Boot / Linux / rootfs                     |
+---------------------------------------------------------------+
```

## Subsystem 책임

| Subsystem | CPU | Firmware / OS | QBox 책임 |
| --- | --- | --- | --- |
| RSE / System Management | Cortex-M55 | TF-M BL1_1, BL1_2, BL2, secure runtime | RSE boot, flash/OTP, provisioning, ATU, AP/SI release handoff, RSE UART log |
| Safety Island CL0 | Cortex-R82 | SCP-firmware | GIC multiview 설정, AP/SI 관리, SCMI/PFDI monitor, safety/control register 접근 |
| Safety Island CL1 | Cortex-R82 x4 | Zephyr/OpenAMP | SMP boot, PFDI agent, HIPC/RPMsg, AP-SI MHU path, CL1 UART log |
| Primary Compute | Cortex-A720AE x4 | TF-A, OP-TEE, U-Boot, Linux | AP firmware chain, secure console, primary UART, Linux login, post-login probes |

## Boot Flow

1. Runner가 `build/local-apollo-fvp/deploy/` 아래의 로컬 산출물을
   해석한다.
2. Runner가 QBox full-system platform을 빌드하거나 `--skip-build`일 때
   기존 빌드를 사용한다.
3. `apollo-qvp.lua`가 `hw-block/rse.lua`를 불러오며 Apollo-owned RSE-first
   topology를 직접 구성한 뒤 `ap_compute.lua`, `si_cl0.lua`, `si_cl1.lua`,
   `ros.lua`로 Apollo 전용 AP view router, Safety Island live domain, RoS
   routing을 추가한다.
4. RSE Cortex-M55가 TF-M ROM/flash/OTP로 부팅한다.
5. RSE가 provisioning bundle과 AP/SI image manifest를 처리한다.
6. Safety Island CL0 SCP-firmware가 live mode에서 Cortex-R82로 실행된다.
7. Safety Island CL1 Zephyr가 live mode에서 Cortex-R82 SMP로 실행된다.
8. AP CPU0가 TF-A BL2로 release되고 BL31, OP-TEE, U-Boot, Linux 순서로
   진행한다.
9. Linux login 이후 runner가 HIPC/RPMsg/PFDI 관련 post-login probe를
   수행한다.
10. Runner가 `result.json`, `summary.txt`, console logs, trace logs를
    저장한다.

## Safety Island 실행 모드

`scripts/run/run_qbox_apollo_fvp_full.py`는 세 가지 Safety Island 모드를
지원한다.

| Mode | 목적 | 완료 판정에서의 의미 |
| --- | --- | --- |
| `service-model` | RSE-first AP firmware boot를 빠르게 검증한다. Safety Island는 service model debt로 분류된다. | G2 milestone |
| `live-cl1` | SI CL1 Zephyr를 live Cortex-R82 domain으로 실행하고 AP Linux HIPC/RPMsg 경로를 검증한다. | G3 milestone |
| `live-cl0-cl1` | SI CL0 SCP-firmware와 SI CL1 Zephyr를 모두 live domain으로 실행한다. | G4/G5 final candidate |

최종 완료는 `live-cl0-cl1` 모드에서만 가능하다.

## QBox Platform 설계

### Apollo Full Platform

`tools/qbox/platforms/apollo/apollo-qvp.lua`는 full-system entrypoint이다.
`tools/qbox/platforms/apollo/hw-block/rse.lua`의 Apollo-owned RSE-first
구조를 기반으로 하며, 나머지 Apollo 전용 기능도
`tools/qbox/platforms/apollo/hw-block/` 아래 block module로 분리되어 있다.

핵심 설계는 다음과 같다.

- AP logical view router를 추가해 AP firmware와 Linux가 기대하는 view를
  `host_router`에 연결한다.
- `system_mgmt.lua`가 live CL0 통합 전 AP/RoS broad decode priority,
  AP logical view router, AP-RSE MHU alias 같은 cross-domain mutation을
  담당한다.
- `QBOX_APOLLO_FULL_SI_MODE` 환경 변수로 service/live mode를 선택한다.
- live CL0 모드에서 SI CL0 SRAM, GIC view, UART, timers, SCR/PPU, NCI,
  SMCF, system PLL, CL0 CPU, PC trace를 구성한다.
- live CL1 모드에서 SI CL1 SRAM, GIC view, UART, MHUv3, Zephyr image
  loader, Cortex-R82 SMP CPU를 구성한다.
- `reset_fanout`으로 MHU power-on-reset 신호를 여러 SI CL1 CPU reset
  입력으로 fan-out한다.
- AP/SI MHU trace와 SI CL0 PC trace를 파일로 남긴다.

### Safety Island CL1 단독 Platform

`tools/qbox/platforms/apollo/apollo-si-cl1.lua`는 CL1 Zephyr만 빠르게 실행해
SMP, UART, PFDI agent, PFDI service, shell marker를 확인하는 단독
milestone platform이다. 최종 완료 증거는 아니지만 Cortex-R82/Zephyr
bring-up 회귀 검사에 유용하다.

## SystemC/TLM 모델

이번 구현에서 추가되거나 확장된 주요 QBox SystemC/TLM 모델은 다음과
같다.

| Model | 역할 |
| --- | --- |
| `gicx00_multiview` | Safety Island GIC-720AE multiview control surface를 모델링한다. 실제 interrupt delivery는 QEMU GICv3 backend와 조합한다. |
| `host_cmn_cyprus` | SI CL0가 접근하는 CMN Cyprus register surface를 제공한다. |
| `host_gtimer` | SI CL0/CL1에서 사용하는 generic timer MMIO surface를 제공한다. |
| `host_ni710ae_nci` | NI-710AE NCI/FMUs 관련 firmware-visible register surface를 제공한다. |
| `host_smcf_mgi` | SMCF MGI register behavior를 제공한다. |
| `host_system_pll` | system PLL status/control surface를 제공한다. |
| `host_ppu` | policy, dynamic/off-lock, operating status bit를 모델링한다. |
| `host_scr` | CL0 config와 PCID reset value를 Apollo에 맞게 설정할 수 있게 한다. |
| `mhu320ae` | MHU-320AE/MHUv3-compatible SCMI channel range, PFDI monitor protocol, AP-SI/CL1 MHU trace를 지원한다. |
| `reset_fanout` | 하나의 reset 신호를 여러 CPU reset 입력으로 분배한다. |

각 모델에는 `tools/qbox/tests/components/` 아래에 component test가
추가되었다. 최소 검증 대상은 `reset_fanout`과 `mhu320ae`이며, 전체
component build는 `platforms-vp` target으로 확인한다.

## QEMU Cortex-R82 변경

Safety Island CL0/CL1 firmware 실행을 위해 `tools/qemu`의 Cortex-R82
지원이 보강되었다.

- Armv8-R EL2 SEL2 timer access를 허용한다.
- PMSA firmware가 사용하는 `ESR_EL1` access를 제공한다.
- Cortex-R82 `ID_AA64PFR0`에 FEAT_SEL2를 광고한다.
- Cortex-R82 `ID_AA64ISAR0`에 LSE를 광고한다.
- AArch32 ID register propagation을 보강한다.

이 변경은 `scripts/inspect/probe_qemu_cortex_r82.py --source-root .`로 source
level probe가 가능하다.

## Memory, Interrupt, ATU 설계

Arm Zena CSS는 하나의 flat map이 아니다. AP, RSE, SMD, Safety Island가
각자의 local view를 갖고 ATU/ATW를 통해 system-wide view에 접근한다.

full-system QBox 설계 원칙은 다음과 같다.

- AP, RSE, SMD, SI CL0, SI CL1 view를 분리해서 기록한다.
- AP GIC, RSE NVIC, SI CL0 GIC view, SI CL1 GIC view interrupt 번호를
  하나의 global SPI namespace로 합치지 않는다.
- ATU/ATW는 boot-critical block이다. 단순 alias로 숨기지 않는다.
- service-model mode에서는 필요한 window를 seed할 수 있지만,
  `result.json`과 coverage audit에서 debt로 분류한다.
- full live mode에서는 RSE/SI firmware가 보는 register와 translation
  결과를 로그와 sidecar JSON으로 확인한다.

정규화된 map/interrupt/ATU 근거는
`doc/qbox-apollo-fvp-map-analysis.md`에 정리되어 있고,
`scripts/test/validate_qbox_apollo_fvp_full_map.py`가 gate evidence를 만든다.

## GIC Multiview 설계

Safety Island GIC은 hybrid 구조를 사용한다.

```text
SI CL0 firmware-visible view0 MMIO
          |
          v
SystemC gicx00_multiview
          |
          +--> QEMU GICv3 backend for CL0 view
          |
          +--> QEMU GICv3 backend for CL1 view
```

이 방식은 firmware-visible multiview control register를 SystemC에서
모델링하고, 표준 distributor/redistributor/CPU interface 동작은 QEMU
GICv3 backend에 맡긴다. 첫 full-system boot milestone에서는 전체 GIC을
새로 구현하는 것보다 검증 가능성이 높고, QEMU patch debt를 줄인다.

## Cross-Domain 통신

full-system boot에서 중요한 통신 경로는 다음과 같다.

| 경로 | 사용 목적 | 검증 evidence |
| --- | --- | --- |
| RSE <-> AP MHU | AP firmware release, RSE communication | RSE log, secure console, marker groups |
| RSE <-> SI MHU | SI image handoff, system management | RSE/SI logs |
| AP <-> SI SCMI MHU | AP와 Safety Island system service | post-login probe, MHU trace |
| AP <-> SI HIPC/RPMsg MHU | Linux `ethsi1`, OpenAMP/RPMsg path | `hipc_ethsi1`, `rpmsg`, `arm_si_rproc` markers |
| CL1 <-> CL0 MHU | PFDI monitor/agent path | SI CL0/CL1 logs, `si-cl1-mhuv3-trace.log` |

`mhu320ae`는 단순 doorbell만 처리하지 않고, SCMI channel base index와
PFDI monitor protocol에 필요한 register/channel 동작을 포함한다.

## Evidence 및 검증 모델

모든 runtime claim은 파일 기반 evidence를 기준으로 한다. tmux 화면만
보고 완료를 선언하지 않는다.

full-system runner는 output directory에 다음 파일을 생성한다.

| 파일 | 의미 |
| --- | --- |
| `result.json` | command, artifact path, safety island mode, verdict, blocker, marker groups, gate status |
| `summary.txt` | 사람이 빠르게 읽는 요약 |
| `qbox-platform.log` | QBox platform stdout |
| `qbox-rse.log` | RSE TF-M console |
| `qbox-safety-island-cl0.log` | SI CL0 SCP-firmware console |
| `qbox-safety-island-cl1.log` | SI CL1 Zephyr console |
| `qbox-secure-console.log` | AP BL2/BL31/OP-TEE secure console |
| `qbox-primary-console.log` | U-Boot/Linux primary console |
| `ap-si-mhuv3-trace.log` | AP-SI MHU trace |
| `si-cl1-mhuv3-trace.log` | SI CL1 MHU trace |
| `si-cl0-pc-trace.log` | SI CL0 PC trace |

최종 evidence bundle은 다음 경로에 있어야 한다.

```text
build/qbox-apollo-fvp/full-live-cl0-cl1/
  result.json
  comparison.json
  map-comparison.json
  coverage-audit.json
  final-verification.json
```

## Completion Gate

완료 판정은 G0부터 G5까지 모두 통과해야 한다.

| Gate | 이름 | 의미 |
| --- | --- | --- |
| G0 | Contract readiness | artifact, Cortex-R82, map, coverage contract 준비 |
| G1 | Direct-boot guardrail | 기존 AP Linux direct boot 회귀 없음 |
| G2 | Service-model full boot | RSE-first AP boot와 service-model debt 확인 |
| G3 | Live CL1 integration | live CL1 Zephyr와 AP Linux HIPC/RPMsg path 확인 |
| G4 | Live CL0/CL1 integration | RSE, CL0, CL1, AP firmware, U-Boot, Linux가 한 run에서 통과 |
| G5 | FVP equivalence closure | FVP log comparison, map comparison, coverage audit 통과 |

최종 판정은 strict verifier만 허용한다.

```bash
python3 scripts/test/verify_qbox_apollo_fvp_full_completion.py \
  --strict-final \
  --output build/qbox-apollo-fvp/full-live-cl0-cl1/final-verification.json
```

JSON은 다음 조건을 만족해야 한다.

```json
{
  "completion_ready": true,
  "completion_claim_allowed": true,
  "overall_gates": {
    "G0": "pass",
    "G1": "pass",
    "G2": "pass",
    "G3": "pass",
    "G4": "pass",
    "G5": "pass"
  }
}
```

## 설계상 남겨둔 원칙

- Direct boot는 빠른 regression guardrail로 유지한다.
- Full-system 완료는 live CL0/CL1 integrated run만 인정한다.
- Register stub이나 service-model은 숨기지 않고 coverage audit에
  분류한다.
- Boot failure 분석은 로그 기반 triage를 먼저 수행한다.
- 로그가 earliest failing domain을 가리킨 뒤에 GDB/Iris 또는 QBox/QEMU
  source-level debugging으로 넘어간다.
- Arm Zena CSS hardware/software 구조 분석 시
  `doc/arm_zena_css_dev_guide/`와 `doc/qbox-apollo-fvp-map-analysis.md`를
  우선 참조한다.
