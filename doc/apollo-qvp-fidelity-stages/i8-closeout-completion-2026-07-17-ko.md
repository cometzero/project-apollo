# I8 - Architecture와 Fidelity Ledger 종결 완료 보고서

- 완료일: 2026-07-17
- 판정: `complete`
- 대상: `apollo-qvp`, RD-Aspen CFG2, AP CPU0~CPU3
- 전체 FVP equivalence 판정: 하지 않음

## 종결 결과

I0~I8 단계와 실제 구현·검증 결과를 다음 문서에 반영했다.

- `doc/apollo-qvp-machine-architecture-ko.md`
- `doc/apollo-qvp-fidelity-debt-architecture-design-ko.md`
- `doc/apollo-qvp-fidelity-debt-implementation-plan-ko.md`
- `doc/apollo-qvp-fidelity-debt-validation-plan-ko.md`
- `doc/apollo-qbox-full-model/coverage-ledger.md`
- `doc/qbox-fvp-emulation-project.md`
- `hsoc-stack/tools/qbox-platform/platforms/apollo/README.md`
- `doc/apollo-qvp-fidelity-stages/README-ko.md`

machine-readable fidelity ledger도 I0~I8의 단계 증거를 연결하도록 갱신했다.

```text
build/qbox-apollo-qvp/fidelity-contract-4cpu.json
  status: pass
  I0~I8: complete

build/qbox-apollo-qvp/fidelity-4cpu-local-20260717/fidelity-contract.json
  status: pass
  I0~I8: complete

build/qbox-apollo-qvp/fidelity-4cpu-yocto-20260717/fidelity-contract.json
  status: pass
  I0~I8: complete
```

I7/I8의 `complete`는 정의된 4 CPU MVP 단계가 완료되었다는 뜻이다. 아래 deferred
및 partial 항목을 FVP-equivalent 또는 전체 safety/software parity로 승격하지
않는다.

## 최종 구현 상태

| 단계 | 상태 | 범위 |
| --- | --- | --- |
| I0 | `complete` | CFG2 4 CPU와 provenance contract |
| I1 | `complete` | 공통 request context와 경로 보존 |
| I2 | `complete` | SI CL0 primary NI-710AE APU와 policy-aware DMI |
| I3 | `complete` | LTI00 MMU-720AE/SMMUv3 대표 translation/fault/TLBI |
| I4 | `complete` | 동일 endpoint MSI-X→ITS/LPI 및 legacy INTx |
| I5 | `complete` | 선택한 SMMU event→FMU→SSU와 clear/recovery slice |
| I6 | `complete` | SCMI/PFDI/HIPC 대표 malformed/recovery slice |
| I7 | `complete` | local/Yocto 4 CPU build, boot, provenance와 coverage |
| I8 | `complete` | architecture, roadmap, ledger와 report 종결 |

## Build와 Runtime 증거

Local:

```text
./local_build.sh qbox
  -> PASS

./local_build.sh qbox --qbox-unit-tests --no-package --jobs 8
  -> PASS, QBox-platform component CTest 33/33

ctest --test-dir build/qbox-core-tests \
  -R '^request-context-tests$' --output-on-failure
  -> PASS, 1/1

scripts/run/run_qbox_apollo_fidelity.py --artifacts local --cpus 4
  -> fidelity-4cpu-local-20260717
  -> runtime/coverage/contract PASS
  -> Linux CPU IDs [0,1,2,3]
  -> artifact_family_errors []
```

Yocto:

```text
./yocto_build.sh
  -> PASS, 7,293/7,293 tasks succeeded
  -> qbox-libqemu-native compile/install/sysroot PASS
  -> qbox-apollo-qvp-native configure/compile/check/install/sysroot PASS
  -> nexios-image do_build PASS

scripts/run/run_qbox_apollo_fidelity.py --artifacts yocto --cpus 4
  -> fidelity-4cpu-yocto-20260717
  -> runtime/coverage/contract PASS
  -> Linux CPU IDs [0,1,2,3]
  -> artifact_family_errors []
```

## 문서와 Diagram 검증

`markdown-diagram-validator` 절차로 변경된 architecture/plan Markdown 4개를
검사했다.

```text
build/qbox-apollo-qvp/i8-markdown-diagrams-20260717/report.json
  diagrams: 2
  syntax/render: 2/2 pass
  hard failures: 0

build/qbox-apollo-qvp/i8-markdown-diagrams-20260717/viewer-evidence.json
  mermaid-001: 17 nodes, 20 edges, viewer pass
  mermaid-002: 9 nodes, 10 edges, viewer pass
  browser console errors: 0
```

checker의 기본 full-page PNG는 SVG DOM이 존재함에도 빈 container만 캡처했다.
따라서 이를 viewer pass로 사용하지 않고, Playwright/Chrome element screenshot을
별도로 생성해 실제 graph가 표시되는 것을 확인했다.

- `previews/mermaid/mermaid-001-element.png`
- `previews/mermaid/mermaid-002-element.png`

설치된 `agent-browser`는 스킬 문서가 요구한 `skills get core` 명령을 지원하지
않아 viewer fallback에 사용하지 못했다. 이는 diagram syntax/render 문제가
아니며 Chrome element viewer로 대체했다.

## Source 경계 확인

재귀 submodule 상태를 확인한 결과 다음 source 경계에는 변경이 없다.

- `hsoc-stack/components/primary_compute/**`
- `hsoc-stack/components/system_mgmt/**`
- 특히 `hsoc-stack/components/primary_compute/optee_os`

구현 변경은 요청된 최상위 도구/문서, `hsoc-stack/tools/qbox`,
`hsoc-stack/tools/qbox-platform`에 한정된다. `hsoc-stack/tools/qemu`는 이번
fidelity 단계에서 추가 변경 없이 기존 local source를 사용했다.

## Deferred 및 Partial 부채

다음 항목은 이번 완료 범위에 포함하지 않는다.

1. CPU4~CPU15 enablement, 16 CPU lifecycle, KVM과 성능 기준
2. 새 focused FVP differential
   - comparison script 부재
   - 실행 가능한 `FVP_Zena_CSS_Cfg2`와 local FVP bundle 부재
3. NI-710AE의 다른 ASNI/AMNI ingress와 exhaustive permission/DMI matrix
4. SMMUv3 stage-2, two-level STE, queue overflow와 translated DMI 전체 조합
5. PCIe affinity, invalid DeviceID/EventID와 ITS invalidation matrix
6. watchdog, DCLS, APU violation source의 전체 FMU/SSU/reset 수직 경로
7. PSCI/FF-A, peer-offline와 reset-time software ABI negative matrix
8. CHI/NoC timing·contention, analog/PHY와 silicon safety coverage 수치

각 항목은 architecture/validation 문서에서 owner, 영향과 후속 완료 조건을
유지한다. 이번 결과는 대표 정상/오류 경로와 4 CPU local/Yocto integration을
빠르게 닫는 최소 검증 계약에 대한 완료다.

## 최종 판정

- 4 CPU fidelity MVP: `complete`
- local QBox build/runtime: `pass`
- Yocto `nexios-image` build/runtime: `pass`
- source/artifact provenance 분리: `pass`
- `components/**` 무변경: `pass`
- focused FVP differential: `deferred`
- blocker: 없음
