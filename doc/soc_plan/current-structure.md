# 현재 Apollo QVP Lua 분석

> 이 문서는 변경 전 17개 Lua의 분석이다. 현재 구현 경로와 검증은 [구현·검증 기록](implementation.md)을 참고한다. 원본은 `build/qbox-apollo-qvp/soc-refactor/baseline/apollo/`에 보존했다.

[설계안](README.md) · [전환 및 검증](migration.md) · [후속 리뷰](review.md) · [Lua 작성 지침](lua-style.md)

2026-10-02 checkout 기준이다. Root HEAD는 `ef7a5e8127fb`, Lua 소유 저장소 `hsoc-stack/tools/qbox-platform` HEAD는 `532d9e8a118a95349b7d75fdc6dfe5958ae5f80b`이다. 분석 시작 시 해당 nested repository는 clean이었다. 아래 설명은 과거 문서의 수치가 아니라 현재 소스를 읽고 Lua를 평가한 결과다.

## 1. 파일 구성

경로는 `hsoc-stack/tools/qbox-platform/platforms/apollo/` 기준이다. 전체 Lua는 **17개, 6,854행**이다. full-system entry에서 도달하는 include graph는 **15개 파일**이며 Linux entry와 `linux-boot/domains.lua`는 별도 profile에 속한다.

| 파일 | 행 수 | 현재 역할 |
|---|---:|---|
| `apollo-qvp.lua` | 115 | full-system 조합, injection, QMP, monitor, timer snapshot |
| `apollo-qvp-common.lua` | 59 | 공용 config/AP/RoS/pinctrl/board 구성, DMA·I2S backend 교체 |
| `apollo-qvp-linux.lua` | 124 | AP-only 조합, firmware/reset 경로 제거, Linux loader와 domain mock |
| `apollo-qvp-qmp.lua` | 37 | domain별 QMP와 QemuInstance 연결 |
| `hw-block/config.lua` | 528 | 환경변수, globals, artifact/log 경로, CPU/reset helper, request context |
| `hw-block/fabric.lua` | 46 | root Container, quantum, keep-alive, system/SMD router/addrtr |
| `hw-block/ap_compute.lua` | 1,236 | AP CPU/GIC/SMMU/PCIe, memory, timer/watchdog, boot loader, RAS, AP view |
| `hw-block/rse.lua` | 1,266 | RSE CPU/Container, memory/security/peripheral/MHU, loader/가속 |
| `hw-block/system_mgmt.lua` | 587 | SMD ATU/MHU/SRAM, reset/counter/PIK/SCR |
| `hw-block/si_cl0.lua` | 1,628 | SI IRQ 계약, CL0 CPU/GIC/메모리, PPU/MHU/SSU/FMU, PMIC host 확장 |
| `hw-block/si_cl1.lua` | 480 | CL1 CPU/GIC/SRAM/HIPC/PFDI/UART, loader, reset 최종 순서 |
| `hw-block/ros.lua` | 502 | DMA350/DW peripheral, VirtIO, EEPROM, UART/I2S loopback |
| `hw-block/pinctrl.lua` | 58 | PERI0/PERI1 pinctrl/GPIO와 peripheral-enable 연결 |
| `board/pca9539.lua` | 45 | AP I2C0 bus, EEPROM 추가, expander reset/IRQ와 GPIO loopback |
| `board/tps6594.lua` | 36 | SI CL0 I2C bus, PMIC 하나와 GPIO loopback |
| `board/peri0-loopback.lua` | 20 | PERI0/PERI1 GPIO 시험 배선 |
| `linux-boot/domains.lua` | 87 | AP-only SCMI/SI/RSE/SMCCC 대체 모델 |

## 2. full-system의 실제 실행 순서

기준: [apollo-qvp.lua](../../build/qbox-apollo-qvp/soc-refactor/baseline/apollo/apollo-qvp.lua#L18), [apollo-qvp-common.lua](../../build/qbox-apollo-qvp/soc-refactor/baseline/apollo/apollo-qvp-common.lua#L4).

1. `common.load()`가 `config.lua`를 실행해 globals를 설정하고 `ctx`를 생성한다. 이어 AP/RoS module을 로드한다.
2. entry가 fabric/SMD/RSE/CL0/CL1/PMIC module을 로드하고 `ctx.modules`에 연결한다.
3. `fabric.create()`가 root `platform`과 router를 생성한다.
4. `rse.define()` → `common.define_ap()` → `system_mgmt.define()`를 호출한다. AP 공용 구성은 AP → RoS → pinctrl 순서다.
5. `common.connect_board()`가 PCA9539/EEPROM bus와 PERI GPIO loopback을 연결한다.
6. `ap_compute.enable_ap_router()`가 기존 객체를 AP 주소 view에 다시 연결한다.
7. `common.use_qemu_audio()`가 DMA350/I2S descriptor를 QEMU 기반 descriptor로 교체하고 일부 pinctrl 연결을 제거한다.
8. `si_cl0.define()` → `si_cl1.define()` → `si_cl0.enable()` → `pmic.connect()` → `si_cl1.enable()`를 호출한다.
9. 선택된 runtime injection, QMP, monitor, timer snapshot을 추가한다.

현재 `define()`과 `enable()`의 이름만으로 객체 생성/연결 단계를 구분할 수 없다. SI `enable()`은 CPU/장치 생성과 cross-domain 수정까지 수행한다. 파일을 옮기면서 이 순서까지 동시에 재배열하면 원인 추적이 어려워진다.

## 3. 주요 결합 관계

| 현재 결합 | 소스 근거 | 설계 영향 |
|---|---|---|
| module 로드 전에 globals 필요 | [AP:140](../../build/qbox-apollo-qvp/soc-refactor/baseline/apollo/hw-block/ap_compute.lua#L140), [RSE:79](../../build/qbox-apollo-qvp/soc-refactor/baseline/apollo/hw-block/rse.lua#L79) | 옵션 값 의존 계산을 함수 내부로 옮긴 뒤 globals 제거 |
| CL1이 CL0의 interrupt helper 사용 | [CL0:366](../../build/qbox-apollo-qvp/soc-refactor/baseline/apollo/hw-block/si_cl0.lua#L366), [CL1:99](../../build/qbox-apollo-qvp/soc-refactor/baseline/apollo/hw-block/si_cl1.lua#L99) | `si_common/interrupts.lua`를 공유; CL0 전체 include 불필요 |
| AP 주소 view가 CL1 HIPC window를 참조 | [AP:1032](../../build/qbox-apollo-qvp/soc-refactor/baseline/apollo/hw-block/ap_compute.lua#L1032), [CL1:51](../../build/qbox-apollo-qvp/soc-refactor/baseline/apollo/hw-block/si_cl1.lua#L51) | 공유 window의 단일 정의 유지 |
| CL0 소스가 CL1 CPU PPU도 생성 | [CL0:1455](../../build/qbox-apollo-qvp/soc-refactor/baseline/apollo/hw-block/si_cl0.lua#L1455) | reset 제어 소유권과 대상 CPU domain을 구분 |
| CL0가 SMD ATU를 후속 수정 | [CL0:955](../../build/qbox-apollo-qvp/soc-refactor/baseline/apollo/hw-block/si_cl0.lua#L955) | SoC interconnect 연결 단계로 명시화 |
| CL1이 system-reset fanout 순서를 최종 변경 | [CL1:171](../../build/qbox-apollo-qvp/soc-refactor/baseline/apollo/hw-block/si_cl1.lua#L171) | PPU hold, UART IRQ, GIC/QEMU reset 순서 보존; unordered merge 금지 |
| AP CPU RAS가 SI CL0로 전달 | [AP:993](../../build/qbox-apollo-qvp/soc-refactor/baseline/apollo/hw-block/ap_compute.lua#L993) | AP-only profile에서 제거하는 경로도 명시적 선택 필요 |
| AP/RSE/SI timer가 CSS counter를 공유 | [SMD:471](../../build/qbox-apollo-qvp/soc-refactor/baseline/apollo/hw-block/system_mgmt.lua#L471), [AP:1015](../../build/qbox-apollo-qvp/soc-refactor/baseline/apollo/hw-block/ap_compute.lua#L1015) | domain별 clock을 새로 만들어 분리하지 않음 |
| AP router 재구성이 RoS callback 사용 | [AP:1124](../../build/qbox-apollo-qvp/soc-refactor/baseline/apollo/hw-block/ap_compute.lua#L1124), [RoS:434](../../build/qbox-apollo-qvp/soc-refactor/baseline/apollo/hw-block/ros.lua#L434) | VirtIO를 VP로 옮겨도 기존 MMIO 재연결 범위 유지 |
| MHU pair와 shared-memory 이름으로 연결 | [SMD:164](../../build/qbox-apollo-qvp/soc-refactor/baseline/apollo/hw-block/system_mgmt.lua#L164), [CL0:864](../../build/qbox-apollo-qvp/soc-refactor/baseline/apollo/hw-block/si_cl0.lua#L864) | source 파일 분리와 endpoint pair identity 변경을 분리 |

`system_mgmt.ownership`은 [SMD:76](../../build/qbox-apollo-qvp/soc-refactor/baseline/apollo/hw-block/system_mgmt.lua#L76)에 있지만 나열된 모든 객체를 이 파일이 직접 생성하는 것은 아니다. 이 table만으로 새 파일 소유권을 자동 생성하면 안 된다.

## 4. 세 계층이 섞여 있는 구체적인 위치

- [fabric.lua:5](../../build/qbox-apollo-qvp/soc-refactor/baseline/apollo/hw-block/fabric.lua#L5): system/SMD 주소 domain과 VP quantum/keep-alive가 같은 factory에 있다.
- [config.lua:89](../../build/qbox-apollo-qvp/soc-refactor/baseline/apollo/hw-block/config.lua#L89): AP reset target에 CPU/peripheral과 VP loader/주입 장치가 함께 있다. [229행](../../build/qbox-apollo-qvp/soc-refactor/baseline/apollo/hw-block/config.lua#L229)의 workspace/deploy fallback은 파일 깊이에 의존한다.
- [ap_compute.lua:118](../../build/qbox-apollo-qvp/soc-refactor/baseline/apollo/hw-block/ap_compute.lua#L118): hardware 상수 table에 BL2 layout 값도 있다. [470행](../../build/qbox-apollo-qvp/soc-refactor/baseline/apollo/hw-block/ap_compute.lua#L470)의 reset loader와 [232행](../../build/qbox-apollo-qvp/soc-refactor/baseline/apollo/hw-block/ap_compute.lua#L232)의 PCIe 시험 장치/observer는 VP 분리 대상이다.
- [rse.lua:117](../../build/qbox-apollo-qvp/soc-refactor/baseline/apollo/hw-block/rse.lua#L117): firmware symbol/hotpath 주소는 firmware/VP 정책이다. [926행](../../build/qbox-apollo-qvp/soc-refactor/baseline/apollo/hw-block/rse.lua#L926)의 `rse_cpu_pass`는 실제 nested Container이므로 유지한다.
- [ros.lua:107](../../build/qbox-apollo-qvp/soc-refactor/baseline/apollo/hw-block/ros.lua#L107): VirtIO가 hardware peripheral과 함께 정의된다. [234행](../../build/qbox-apollo-qvp/soc-refactor/baseline/apollo/hw-block/ros.lua#L234)의 EEPROM은 board 장치, [279행](../../build/qbox-apollo-qvp/soc-refactor/baseline/apollo/hw-block/ros.lua#L279)의 UART peer와 [305행](../../build/qbox-apollo-qvp/soc-refactor/baseline/apollo/hw-block/ros.lua#L305)의 I2S peer는 시험 배선이다.
- [si_cl0.lua:96](../../build/qbox-apollo-qvp/soc-refactor/baseline/apollo/hw-block/si_cl0.lua#L96): PMIC I2C/GPIO는 실제 RD-Aspen peripheral 배정이 아닌 QVP 확장임을 명시한다. `0x2A800000`/`0x2A810000`의 device와 reset 연결은 VP 확장으로 이동해야 한다.
- [board/pca9539.lua:28](../../build/qbox-apollo-qvp/soc-refactor/baseline/apollo/board/pca9539.lua#L28), [board/tps6594.lua:22](../../build/qbox-apollo-qvp/soc-refactor/baseline/apollo/board/tps6594.lua#L22): 외부 device/IRQ와 자체 GPIO loopback이 한 descriptor에 있다.

RoS에 있는 각 I2C EEPROM과 PCIe endpoint도 개별 확인이 필요하다. 기존 guest probe가 요구하는 장치라면 단순히 시험용이라는 이유로 삭제하지 않는다. endpoint hardware/population, host backing, traffic/fault generator를 분리한다.

## 5. QBox loader가 강제하는 계약

| 계약 | 현재 구현 |
|---|---|
| Lua 실행 후 `_G` 전체를 CCI로 변환 | [luautils.cc:149](../../hsoc-stack/tools/qbox/systemc-components/common/src/luautils.cc#L149) |
| table 계층을 dotted key로 순회 | [luautils.cc:288](../../hsoc-stack/tools/qbox/systemc-components/common/src/luautils.cc#L288) |
| 숫자 table key는 CCI에서 zero-based로 변환 | [luautils.cc:207](../../hsoc-stack/tools/qbox/systemc-components/common/src/luautils.cc#L207) |
| Container는 direct child의 `moduletype`로 객체 탐색 | [module_factory_container.h:729](../../hsoc-stack/tools/qbox/systemc-components/common/include/module_factory_container.h#L729), [cciutils.cc:63](../../hsoc-stack/tools/qbox/systemc-components/common/src/cciutils.cc#L63) |
| bind/constructor args 경로의 parent 정규화 | [module_factory_container.h:185](../../hsoc-stack/tools/qbox/systemc-components/common/include/module_factory_container.h#L185), [259행](../../hsoc-stack/tools/qbox/systemc-components/common/include/module_factory_container.h#L259) |
| `construction_priority`로 실제 생성 순서 결정 | [module_factory_container.h:713](../../hsoc-stack/tools/qbox/systemc-components/common/include/module_factory_container.h#L713) |
| CMake Lua dependency는 5.4.2 | [qbox/CMakeLists.txt:275](../../hsoc-stack/tools/qbox/CMakeLists.txt#L275) |

따라서 `platform.soc.ap_compute.cpu0` 같은 grouping table만 추가하면 객체가 생성되지 않을 수 있다. 각 grouping을 Container로 바꾸면 실제 runtime path가 변한다. 반면 `soc/hw-block/ap_compute/cpu.lua`에서 기존 `platform.ap_cpu_0`에 descriptor를 쓰면 파일만 분리할 수 있다.

Lua load 오류를 로그로 남긴 뒤 CCI 변환으로 진행하는 [loader 경로](../../hsoc-stack/tools/qbox/systemc-components/common/src/luautils.cc#L136)도 있다. Lua validation뿐 아니라 native 실행 로그의 오류와 elaboration 실패를 runner가 실패로 처리하는지 확인해야 한다. 이 설계 작성에서는 loader의 오류 처리 방식을 변경하지 않았다.

## 6. include 분석기와 profile 소비자

[apollo_ap_map_lua.py](../../scripts/test/apollo_ap_map_lua.py#L9)는 `dofile(..."literal.lua")`만 추출하고, literal을 **호출 파일의 parent** 기준으로 해석한다. include cycle, 없는 파일, entry 디렉터리 외부 경로를 거부한다. Lua 실행과 같은 path 규칙을 유지해야 한다.

[AutoSD topology evaluator](../../scripts/autosd_dashboard/topology.py#L45)는 수집된 source만 허용하는 `dofile()`과 제한된 Lua environment에서 entry를 실행한다. 현재 entry 이름과 `hw-block/`/`board/`의 domain 분류 규칙도 고정되어 있다. 신규 폴더로 이동한 후에는 graph를 읽는 것뿐 아니라 도메인 색인과 source attribution도 수정해야 한다.

[Linux entry](../../build/qbox-apollo-qvp/soc-refactor/baseline/apollo/apollo-qvp-linux.lua#L8)는 SI metadata를 읽지만 SI firmware를 실행하지 않는다. AP 구성 이후 reset/firmware 객체를 삭제하고 router bind를 AP local로 바꾸며 [domain substitutes](../../build/qbox-apollo-qvp/soc-refactor/baseline/apollo/linux-boot/domains.lua#L5)를 만든다. 이 profile을 full-system entry의 단순 하위 옵션으로 합쳐 실제 firmware 실행 여부가 불명확해지지 않도록 한다.

## 7. 이번 분석의 검증 결과

| 확인 | 결과 | 증명 범위 |
|---|---|---|
| `luac -p`, Apollo 전체 17개 Lua | PASS | Lua 문법 |
| 실행 topology 평가 | 333 nodes, 1,175 edges, 15 source files, warnings 0 | AP CPU 활성화 환경의 정적 descriptor/binding graph |
| 기존 full-map validator | 95/95 PASS | 현재 checkout의 source/문서 패턴 계약 |
| Linux composition, board, modular include, topology pytest | 25 passed | 기존 evaluator와 Lua 구성 계약 |
| native QBox build/boot/guest traffic | NOT RUN | 문서 작업이므로 새 runtime 검증을 수행하지 않음 |

평가 환경은 `QBOX_RDASPEN_ENABLE_AP_CPUS=true`이고 나머지 환경변수는 topology evaluator의 기본값이다. 333/1,175는 모든 profile에 대한 고정 목표 수치가 아니다. full-map validator 역시 source 패턴 검사이므로 실제 ATU transaction/IRQ 동작의 증거가 아니다. 후속 리뷰에서 기본 `lua`/`luac`가 5.1.5임을 확인했으므로 위 host 문법 검사 결과를 QBox embedded Lua 5.4 실행 증거로 확대하지 않는다.

로컬 산출물:

- [topology.json](../../build/qbox-apollo-qvp/soc-plan-20261002/topology.json)
- [full-map-validation.json](../../build/qbox-apollo-qvp/soc-plan-20261002/full-map-validation.json)

재실행한 pytest:

```bash
python3 -m pytest -q \
  tests/test_apollo_linux_lua.py \
  tests/test_qbox_pca9539_board.py \
  tests/test_apollo_ap_map_modular_lua.py \
  tests/test_autosd_topology.py
```

codebase-memory의 `apollo-qbox-platform` index는 2026-09-30 generation이며 조회한 범위에서 일부 C++/assembly parse gap을 보고했다. include와 실행 순서에 대한 결론은 index 완전성을 가정하지 않고 현재 Lua/C++ 직접 읽기와 위 평가 결과에 근거한다.
