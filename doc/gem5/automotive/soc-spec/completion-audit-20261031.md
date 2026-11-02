# Completion audit — 2026-10-31 중간본

**전체 목표 미완료.** VERIFIED는 명시한 지원 범위의 증거이며 silicon 검증이나 전체
campaign 완료가 아니다. PARTIAL은 구현/일부 runtime을 확인했지만 전체 evidence가
남은 상태다. 조건부 항목은 trigger와 제외 근거를 최종 decision에 보존해야 한다.

경로 약어: C=`build/qbox-apollo-qvp/gem5/soc-spec-20261028T014936Z`,
V=`build/qbox-apollo-qvp/gem5/verification-20261031`, D=현재 문서 directory.
기존 중간 audit의 cache/G1/G2 상태는 최신 host/native/raw evidence로 갱신했다.
41개 row를 기계 집계하면 VERIFIED12, PARTIAL23, 조건부5, terminal acceptance 미완료1이다.
초기 review summary의14/22/4 집계 오류를 바로잡았으며 개별 row 판정은 변경하지 않았다.

| ID | 판정 | Evidence | 범위와 남은 작업 |
|---|---|---|---|
| REQ-DSE-001 | PARTIAL | `V/root-tests-final.log` | Target boundary semantics 확인; final scenario/resident/TBD decision 미완료 |
| REQ-DSE-002 | PARTIAL | `C/build/image-content.json` | Image/ROI correctness 확인; P5/heldout/P6 후속 coverage 미완료 |
| REQ-DSE-003 | PARTIAL | `V/validation-revision.json` | Input/model hashes 고정; 전체 후속 inventory 통합 미완료 |
| REQ-DSE-004 | VERIFIED | `V/native-config-tests.log` | 지원 cache geometry/resource/native config 검증 범위 |
| REQ-DSE-005 | PARTIAL | `V/memory-inventory-summary.json` | Workers scaling VALID; shortlist CPU uncertainty 미완료 |
| REQ-DSE-006 | VERIFIED | `C/reports-v4/native-framing-verification.json` | Clock/framing/실제 domain 검증; physical CDC parity 제외 |
| REQ-DSE-007 | PARTIAL | `V/p6-config-summary.json` | Channel/stripe 검증; Hynix guest 영향 및 resident budget 미완료 |
| REQ-DSE-008 | PARTIAL | `V/cache-completed-review.json` | Exact ROI/accounting, BG1/BG4 finish, pool1 terminal VALID; 전체 scenario acceptance 미완료 |
| REQ-DSE-009 | PARTIAL | `D/hypothesis-status-20261031.md` | 현재 가설 표 작성; P2/P5/P6 결과까지의 synthesis 미완료 |
| REQ-DSE-010 | PARTIAL | `V/p4-current-result-v2.json` | Baseline read 두 gate PASS; 다른 P2/P5/heldout/P6 안정성 미완료 |
| REQ-DSE-011 | PARTIAL | `V/root-tests-final.log` | BG finish guard host 및 BG1/BG4 runtime PASS; 전체 scenario acceptance 미완료 |
| REQ-DSE-012 | CONDITIONAL_NOT_TRIGGERED | `D/design.md` | 외부 IP requirement/traffic 근거 없음; CPU BG 대체 금지 |
| REQ-DSE-013 | CONDITIONAL_UNDECIDED | `D/requirement.md` | PPA/physical cost/resident 입력 없음; final report에 부재 연결 필요 |
| REQ-DSE-014 | PARTIAL | `V/p4-current-result-v2.json` | FAIL/NOT_RUN 보존; 전체 terminal coverage report 미완료 |
| REQ-DSE-015 | VERIFIED | `C/build/host-checkpoint-tests.log` | 지원 schema3 dependency-bound restore/immutable output; 새 endpoint는 matching snapshot 필요 |
| REQ-DSE-016 | PARTIAL | `V/screening-nomination.json` | Provisional A/B만 지명; final decision/re-entry 미완료 |
| IMP-DSE-01 | PARTIAL | `V/validation-revision.json` | Identity/canonicalization 구현; 최종 cases 통합 미완료 |
| IMP-DSE-02 | VERIFIED | `V/native-positive-summary.json` | Native oracle 및 config/DTB positive/mutation 검증; workload 성능 제외 |
| IMP-DSE-03 | PARTIAL | `V/p4-current-result-v2.json` | ROI/counter/comparison 구현; 남은 convergence와 최종 synthesis 미완료 |
| IMP-DSE-04 | VERIFIED | `C/build/image-content.json` | 실제 initramfs binary/guest correctness와 ROI; synthetic kernel 범위 |
| IMP-DSE-05 | PARTIAL | `V/root-tests-final.log` | Coordinator/finish guard 및 CPU1/CPU4 BG runtime 확인; 전체 scenario acceptance 미완료 |
| IMP-DSE-06 | CONDITIONAL_NOT_TRIGGERED | `D/implementation.md` | 현재 후보로 판단 불가할 때만 x32/rate/capacity/topology 확장 |
| IMP-DSE-07 | CONDITIONAL_NOT_TRIGGERED | `D/implementation.md` | 외부 IP envelope/연결 요구 없음; NPU snapshot 지원 주장 금지 |
| IMP-DSE-08 | PARTIAL | `V/screening-nomination.json` | Target/paired policy/nomination 구현; final decision artifact 미완료 |
| VER-DSE-001 | VERIFIED | `V/root-tests-final.log` | Equality/headroom/unit/sample/zero/coverage host 검증; 제품 target는 UNDECIDED |
| VER-DSE-002 | PARTIAL | `C/build/image-content.json` | Host oracle/guest output binding; 후속 case correctness 미완료 |
| VER-DSE-003 | VERIFIED | `C/build/host-checkpoint-tests.log` | Canonicalization/dependency 및 unsupported snapshot 거부 검증 |
| VER-DSE-004 | VERIFIED | `V/native-config-tests.log` | 지원 profile cache/native resource 검증;3 SKIP 별도 유지 |
| VER-DSE-005 | VERIFIED | `V/memory-inventory-summary.json` | Workers1/4/8/16 VALID 및 AP4 완료; fixed-total footprint 한계 유지 |
| VER-DSE-006 | VERIFIED | `C/reports-v4/native-framing-verification.json` | Framing6 및 실제 CPU/Ruby/mesh domain; physical parity 제외 |
| VER-DSE-007 | PARTIAL | `V/p6-config-summary.json` | 기존 channel/stripe 및 Hynix config; 제품 capacity/새 geometry guest 미완료 |
| VER-DSE-008 | VERIFIED | `C/reports-v4/native-backend-verification.json` | Direct/fanout/single4 및 FS fingerprint binding; FS/native 해석 분리 |
| VER-DSE-009 | PARTIAL | `V/p4-current-result-v2.json` | 기존 restore/O3/ROI 검증; 새 P5 acceptance 미완료, cold-start 미검증 |
| VER-DSE-010 | VERIFIED | `V/root-tests-final.log` | Counter corruption/NaN/missing/duplicate/negative/zero handling 검증 |
| VER-DSE-011 | PARTIAL | `V/p4-current-result-v2.json` | 기존 수렴 재계산 및 실패 보존; 새 regime 안정성 미완료 |
| VER-DSE-012 | PARTIAL | `D/hypothesis-status-20261031.md` | 두 interaction 및 현재 가설 표; P5 이후 전체 종합 미완료 |
| VER-DSE-013 | NOT_RUN_TERMINAL_ACCEPTANCE | `V/p5-nominees/check.json` | BG/cluster/pool1 완결된 raw/환경/slowdown acceptance 없음 |
| VER-DSE-014 | CONDITIONAL_NOT_TRIGGERED | `D/design.md` | 외부 IP 실행 조건 미trigger; REQ012/IMP07와 동일 경계 |
| VER-DSE-015 | PARTIAL | `V/p6-config-summary.json` | Config-only uncertainty5; selected control workload/ranking 미완료 |
| VER-DSE-016 | PARTIAL | `V/root-tests-final.log` | 누락 target/cost 처리 tests; final report replay 미완료 |
| VER-DSE-017 | PARTIAL | `V/p4-current-result-v2.json` | Mixed-status tests/부분 replay; 전체 required coverage final report 미완료 |

## 번호 밖 deliverable

- 최종 campaign/inventory/cases/comparison/decision 연결과 동일 evidence 재생성.
- A/B의 P5·heldout 결과에 따른 inclusion/exclusion/re-entry 및 최종 선정 또는 보류.
- Held-out pool1의 효과 이전 관측과 별도 scenario 수렴. Same-kernel footprint이며 calibration 아님.
- 선정이 성립하면6 solo uncertainty controls. Baseline-only unresolved outcome이면 policy에 따라 명시적 보류.
- 현재 [가설 표](hypothesis-status-20261031.md)에 후속 P2/P5/P6 evidence를 통합.
- P5 첫 run의 native verifier/capture protocol PASS를 확인. 초기 환경 누락 진단은 실제 argv 검토로 철회했으며 남은 scenario terminal 검증을 계속 수행.
- 최종 문서 anchor/command/source traceability 및 consistency 검사. 기존 local file92개 검사는 제한된 범위.
- 기존 build/image/snapshot 재사용의165 model-source 동일성 근거를 최종 report에 연결.

P2 warmup2→4 세 metric gate PASS(`V/p2-read-followup/completed-review.json`),
measured passes2→4/warmup2도 세 metric gate PASS(`V/p2-read-length/completed-review.json`)다.
P5 CPU1/CPU4 BG는 VALID 완료(`V/p5-bg1-completed-review.json`,
`V/p5-bg4-completed-review.json`)이며 pool1도 VALID 완료
(`V/p5-pool1-completed-review.json`)다. Image baseline solo의 warmup2→4와 frames4→8 네 metric gate는 모두 PASS다
(`V/p5-solo-convergence/warmup-completed-review.json`,
`V/recovery-20261101/frames8/length-completed-review.json`). Host 중단 후 별도 recovery
queue에서 후보 A/B의 BG/solo 검증을 계속하며, held-out pool1 후보도 실행 중이다.
전체 scenario 수렴과 환경 정책 판정이 남아 있으므로 위 PARTIAL 및 terminal acceptance
판정은 유지한다. 완료된 raw 하나로 전체 requirement를 VERIFIED로 승격하지 않는다.
제품 target/PPA/resident 입력 부재는 UNDECIDED 근거이며 수행 가능한 검증의 생략 근거가 아니다.
