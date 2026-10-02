# SoC · VP · Board 분리 계획 리뷰

[설계안](README.md) · [전환 계획](migration.md) · [Lua 작성 지침](lua-style.md)

리뷰일: 2026-10-02. 대상은 구현 전 설계 문서와 당시 QBox Lua/loader/검사기다. 판단은 **분리 방향을 유지하되 아래 사항을 보완한 계획으로 구현 진행 가능**이다. 아래에는 당시 지적과 완료 조건을 보존한다. 이후 적용한 Lua·loader·검사기 수정과 검증 결과는 [구현·검증 기록](implementation.md)에 기록했다.

## 1. P1 — backend 선택이 hardware 생성보다 늦게 읽힐 수 있음

이전 설명은 `soc.define()` 다음 `vp.attach()`에서 backend를 추가한다고 했고, 다른 절에서는 hardware 생성 시 최종 backend를 선택한다고 했다. 실제 [AP SMMU factory](../../build/qbox-apollo-qvp/soc-refactor/baseline/apollo/hw-block/ap_compute.lua#L194)는 backend에 따라 MMIO/IRQ socket과 constructor `args`가 다르다. [RSE flash](../../build/qbox-apollo-qvp/soc-refactor/baseline/apollo/hw-block/rse.lua#L1084)도 객체 구성이 달라진다.

**반영:** `options.resolve → vp.prepare → soc.define → vp.attach` 순서를 명시했다. `vp.prepare()`가 backend/capability/instance 참조를 확정하고 SoC가 그에 맞는 최종 descriptor를 생성한다. `attach()`는 instance·loader·확장 등을 추가하며 backend를 다시 선택하지 않는다. 초기 compatibility 단계의 기존 audio 교체는 그대로 보존하고 별도 단계에서 제거한다.

**완료 조건:** 각 지원 backend에 대해 socket/args와 final descriptor가 baseline과 같아야 한다. backend 선택 이후 다른 module이 값을 바꾸는 경로가 없어야 한다.

## 2. P1 — 최종 table만으로 중복 생성을 검출할 수 없음

Lua에서 `platform.cpu = first` 다음 `platform.cpu = second`가 실행되면 최종 table에는 `second`만 남는다. 최종 `vp.validate()`가 중복 생성 이력을 검출한다는 약속은 성립하지 않는다.

**반영:** 각 owner의 생성 직전에 `assert(platform[name] == nil, ...)`를 둔다. 의도된 교체는 별도 함수에서 기존 `moduletype` 등 기대값을 검사한다. table literal의 중복 field는 lint/code review로 확인한다. `__newindex` 기반 magic이나 전체 객체 registry는 기본 설계에 추가하지 않는다.

**완료 조건:** 같은 owner를 두 번 호출하거나 다른 owner가 동일 이름으로 정의할 때 두 번째 assignment 전에 오류가 발생해야 한다. 원래 존재하는 객체의 명시적인 wiring 수정은 이 생성 guard와 구분한다.

## 3. P1 — Lua assertion과 native 실패 전달은 다른 계약

[Lua loader](../../hsoc-stack/tools/qbox/systemc-components/common/src/luautils.cc#L144)는 chunk 오류를 로그로 남긴 뒤 `_G`를 CCI로 순회한다. [argparser](../../hsoc-stack/tools/qbox/systemc-components/common/include/argparser.h#L113)는 `lua.config()`의 반환값을 검사하지 않는다. 따라서 `assert`를 추가했다는 사실만으로 잘못된 구성이 native 실행을 즉시 중단한다고 말할 수 없다.

**반영:** `platform = p`를 최종 검증 뒤 한 번만 수행하는 원칙과 native 오류 전달 검증을 분리했다. negative test에서 native nonzero 또는 runner의 명시적 FAIL이 필요하다. timeout이나 빈 platform만 관찰한 결과는 PASS가 아니다. legacy global에 대한 rollback도 자동 제공되지 않는다.

**완료 조건:** 필수 board port 누락·지원하지 않는 backend를 실제 native 입력에 넣어 실패 판정을 확인한다. 필요하면 후속 구현의 독립적인 loader/runner 수정으로 해결하며, 문서상 보완을 구현 완료로 표시하지 않는다.

## 4. P1 — 서식 변경으로 source 검사 범위가 사라질 수 있음

실제 Python parser에 작은 메모리 fixture를 넣어 확인한 결과다. 아래는 Lua 언어의 제약이 아니라 **현재 검사기 구현의 제약**이다.

| 입력 | 실제 검사기 결과 |
|---|---|
| `dofile(dir.."cpu.lua")` | `soc/cpu.lua` include 인식 |
| `dofile (dir.."cpu.lua")` | `malformed_dofile` |
| `dofile(dir..'cpu.lua')` | `malformed_dofile` |
| constant table의 `uart = 0x1A400000;` | `AP_ADDRESS.uart = 440401920` 수집 |
| 같은 field 끝을 `,`로 변경 | constant 수집 결과 `{}` |
| 객체 선언 앞 공백 4개 | 시험 socket 1개 수집 |
| 같은 선언 앞 공백 2개 또는 tab | 시험 socket 0개 수집 |
| `platform["ap_virtioblk_"..i]`를 사용하는 기존 RoS 패턴 | VirtIO binding 4개 수집 |
| 같은 문자열 결합을 `platform["ap_virtioblk_" .. i]`로 변경 | binding 0개 수집 |

근거: [include parser](../../scripts/test/apollo_ap_map_lua.py#L9), [constant/socket parser](../../scripts/test/audit_qbox_apollo_ap_memory_map.py#L422), [RoS binding parser](../../scripts/test/audit_qbox_apollo_ap_memory_map.py#L505), [ownership parser](../../scripts/test/audit_qbox_apollo_lua_ownership.py#L115).

**반영:** 현재는 4-space·큰따옴표·`dofile(`·semicolon field 관례를 유지한다. formatter 도입과 동적 factory 추출 전에 해당 consumer를 수정한다. 연산자 공백이나 명시적 `if`를 추가하는 수동 수정도 검사 범위에 포함한다. 가능한 구성 값은 실행 평가한 descriptor를 읽고, source 위치나 규칙 검사는 별도 유지한다. inspector가 지원하지 않는 문법을 조용히 무시하거나 빈 수집을 PASS로 처리하지 않게 한다.

**완료 조건:** 경로·서식 변경 전후 include graph, 수집한 object/address 집합, final descriptor가 같아야 한다. StyLua의 syntax/AST 확인만으로 이 호환성이 증명되지는 않는다.

## 5. P2 — 파일 수와 context 의존을 제한해야 함

목표 트리를 모든 IP당 한 파일로 해석하면 파일을 오가며 읽어야 하는 비용이 커진다. `ctx`를 새 전역처럼 사용해 다른 domain의 설정을 자유롭게 수정하면 기존 결합도 그대로 남는다.

**반영:** 트리는 추출 가능한 책임 목록으로 정의했다. 첫 이행은 domain별 작은 수의 응집된 파일로 시작한다. `ctx.options/profile/board/backends`는 준비 후 읽기 전용 규칙, `ctx.ports`는 owner만 쓰는 규칙으로 구분한다. private helper는 필요한 설정만 인자로 받는다. 과도한 wrapper·registry·deep merge는 추가하지 않는다.

## 6. P2 — host Lua 검증 버전 명시

리뷰 환경의 기본 `lua`/`luac`는 **5.1.5**다. QBox [CMake dependency](../../hsoc-stack/tools/qbox/CMakeLists.txt#L279)는 **5.4.2**를 지정한다. 기존 host 문법 PASS는 해당 host interpreter에서의 결과다.

**반영:** 후속 검증 명령은 Lua 5.4 도구를 명시하고 native embedded interpreter도 확인하도록 바꿨다. `luac5.4`가 없으면 버전 일치 검증을 수행하지 않았다고 기록한다. 문서 예제는 현 host에서도 읽을 수 있는 기본 문법을 사용한다.

## 7. 유지한 결정

- filesystem의 domain 계층과 기존 QBox runtime hierarchy를 분리한다.
- 새 canonical entry와 기존 forwarding entry를 함께 유지한다.
- QVP 확장, 실제 SoC hardware, 외부 board 장치, 시험 연결을 구분한다.
- 최종 descriptor 비교와 native/guest 검증을 분리한다.
- Saturn-V 실물 schematic/BOM 확인은 `UNVERIFIED`로 유지한다.

이번 리뷰는 문서·현재 소스 검사와 작은 구성 실험에 한정한다. 새로운 QBox build/boot나 실물 board 검증을 수행하지 않았다. [Lua 작성 지침](lua-style.md)의 formatter/linter 설정도 후속 도입 제안이다.

## 8. 문서 예제 검증

- 문서의 Lua code block 8개를 host `luac`로 문법 검사하고 TOML 설정 1개를 구문 분석했다.
- EEPROM 예제를 실행해 세 장치의 주소/속성/연결, descriptor와 socket table의 독립성, 중복 생성/연결 오류, bus 누락 오류, 반복 구성 및 global 미생성을 확인했다.
- optional reset 목록과 false 기본값 처리 예제를 각각 true/false/누락 입력으로 확인했다.
- 문서의 로컬 링크와 공백 오류를 검사했다.

결과와 실행한 예제는 [review/document-validation.json](../../build/qbox-apollo-qvp/soc-plan-20261002/review/document-validation.json)에 기록했다. 실행 interpreter는 Lua 5.1.5이며 embedded Lua 5.4/native QBox 검증은 NOT RUN이다. StyLua/Luacheck는 이 환경에 설치되어 있지 않아 해당 설정의 실제 도구 적용은 검증하지 않았다.
