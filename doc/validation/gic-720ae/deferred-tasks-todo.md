# Apollo GIC-720AE 최소 범위 이후 TODO 보고서

> 이 문서는 ledger seq 94 시점의 과거 분류 snapshot이다. 2026-08-03
> 실행 중 Task 13이 완료되고 Task 15 진단이 진행되었으므로, 다른 PC나
> Agent에서 작업을 재개할 때는
> [`continuation-handoff-20260803.md`](continuation-handoff-20260803.md)를
> 현재 기준으로 사용한다.

작성일: 2026-08-03 KST

이 문서는 현재 plan/ledger를 기준으로 아직 체크되지 않은 30개 항목을
`essential-now`, `deferred-nonessential`, `essential-blocked/deferred` 중
하나로 정확히 한 번씩 분류한다. 기존 완료 항목은 보존하며, Prometheus
plan이나 product source는 수정하지 않았다.

## 1. PIN

| 항목 | 값 |
| --- | --- |
| Plan | `.omo/plans/apollo-gic720ae-implementation.md` |
| Plan SHA-256 | `18a6763f64b7c91d80742d19f3a419a6210ce2471aa58a06a1f46bac9dcab4e0` |
| Plan line count | `4971` |
| Plan checkbox count | `50` |
| 완료 checkbox | `20` |
| 미완료 checkbox | `30` |
| Ledger | `.omo/start-work/ledger.jsonl` |
| Ledger SHA-256 | `20edbcd6c5c96ff612f870fc0c4ab4b42477a090e16888e4d33280dee69e373a` |
| Ledger latest seq/root | `94` / `cecb6424495754c1c2b587a6ae384722ba9c9f5e9dc42b455b578de6eaad41e8` |
| Latest ledger event | Task 27 `task-blocked`, verdict `confirmed-blocked` (parallel lanes: `host_tools`, `kernel`, `yocto_profile`) |

완료로 유지하는 항목은
`1,2,3,4,5,6,7,8,9,10,11,12,14,20,21,22,23,29,30,31`이다. 특히 Task 23은
ledger seq 92에서 `task_complete=true`, `task_pass=true`, verdict
`confirmed`로 확인되었으며, 이 보고서는 이를 다시 열거나 완료 의미를 바꾸지
않는다. 그 밖의 완료 항목도 다시 열거나 완료 의미를 바꾸지 않는다.

## 2. 분류 결과

Task 27의 세 구현 lane(`host_tools`, `kernel`, `yocto_profile`)은 각각
PASS했지만 통합 lane은 BLOCKED다. `linux-yocto-rt -c deploy`가
`key-store:do_unpack`에서 `/proc/self/uid_map` 쓰기 `EPERM`으로 중단되었고,
현재 host AppArmor/userns 정책 때문에 유효한 opt-in kernel/DTB/WIC/qboxconf/
module tuple이 생성되지 않았다. 따라서 Task 27은 `essential-now`가 아니라
`essential-blocked/deferred`이며, 통합 runtime PASS를 주장하지 않는다. Task
23은 완료로 확인되었고, 현재 unchecked 집합에서 제거했다. Plan의 `Blocked by` 행을 적용하면 Task
17/18은 Task 13/15/16, Task 25는 Task 24, Task 26은 Task 19/25, Task 38은
Task 17/18/26/33-37, Task 39-46과 F1-F4는 그 뒤의
freeze/review/publication chain을 요구한다.

따라서 실제 최소 실행 분류는 다음과 같이 조정한다.

| 분류 | 항목 | 수 |
| --- | --- | --- |
| `essential-now` | `—` | 0 |
| `essential-blocked/deferred` | `17,18,25,26,27,38,39,40,41,42,43,44,F1,F2,F3,F4,45,46` | 18 |
| `deferred-nonessential` | `13,15,16,19,24,28,32,33,34,35,36,37` | 12 |

`essential-now`는 현재 없다. `essential-blocked/deferred`는 최종 제품
완료에는 필요하지만, 이번 2시간 목표에서는 환경 또는 선행 항목 때문에
실행 가능한 완료 항목으로 주장하지 않는다. 2시간은 보장 시간이 아니라
bounded execution target이다.

## 3. 현재 즉시 실행 경로

| 순서 | Task | 목적 | 선행 조건 | 재개 명령 | 증거 경로 |
| --- | --- | --- | --- | --- | --- |
| 1 | 27 | Primary Compute Linux controlled SGI/PPI/SPI/affinity/hotplug probe를 opt-in profile로 증명 | 세 구현 lane은 PASS했지만 통합은 `key-store:do_unpack` → `/proc/self/uid_map` EPERM으로 BLOCKED | `python3 scripts/test/run_gic720ae_linux_probe.py --commands tests/commands/gic720ae-linux-probe.yaml --out-dir <attemptDir>/task-27-apollo-gic720ae-implementation` (유효 tuple 생성 후에만) | `.omo/evidence/task-27-apollo-gic720ae-implementation/` |

Task 27은 bounded two-hour 환경 BLOCKED이며, 최종 제품 완료가 아니다.
통합 manifest SHA는
`38192afaba5ba99b8d2c930f11bf3ad9318c7bc0eaefb63fc62c0f4d16915d95`, 독립
검증 manifest SHA는
`36099f4f97cfa1127641887ee16beea303c2c9685381c48a9c6013c2e6d66514`다.
독립 검증은 `unshare -Ur true`와 BitBake의 동일 `uid_map` EPERM을 재현했다.
현재 host AppArmor/userns 정책을 약화하거나 BitBake network isolation을
우회하는 안전한 code/config bypass는 없다. 다음 안전한 조치는 필요한 user
namespace를 허용하는 host/environment에서 동일 builder command를 재실행하거나,
host policy 변경을 명시적으로 승인받는 것이다.

| Lane | 담당 | exact evidence root |
| --- | --- | --- |
| `host_tools` | `/root/task27_host_tools` PASS | `.omo/evidence/task-27-apollo-gic720ae-implementation/host-tools/` |
| `kernel` | `/root/task27_linux_driver` PASS | `.omo/evidence/task-27-apollo-gic720ae-implementation/kernel/` |
| `yocto_profile` | `/root/task27_yocto_profile` PASS | `.omo/evidence/task-27-apollo-gic720ae-implementation/yocto-profile/` |
| 통합 runtime | BLOCKED, no valid tuple/no runtime PASS | `.omo/evidence/task-27-apollo-gic720ae-implementation/integration/` |
| 독립 검증 | `confirmed` blocker boundary | `.omo/evidence/task-27-apollo-gic720ae-implementation/independent-blocker-verification/` |

세 구현 lane의 PASS는 통합 runtime PASS가 아니다. 유효한 isolated tuple이
생성되기 전 QBox를 실행하면 default/incomplete image를 사용하게 되므로
금지한다.

## 4. 보류 backlog

아래 표의 `재개 명령`은 원 plan의 acceptance surface를 재개할 때 사용할
대표 명령이다. 아직 해당 task가 구현하지 않은 script/path는 실행 가능한
현재 명령으로 주장하지 않고, 해당 task 구현 후 검증할 계획상 명령으로만
기록한다.

| 우선순위 | Task | 분류 | 원 acceptance 요약 | 보류 이유 | 필수 선행 조건 | 위험 | 재개 명령 | 증거 경로 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 13 | `deferred-nonessential` | SI SGI/PPI/SPI route validator와 `apollo_si_gic_irq-tests`가 owner/target counter를 검증 | BQL teardown RC134가 3회 반복되어 인간 승인 전 autonomous retry/source edit 금지 | 11,12 완료. 추가로 bounded BQL caller 진단 승인 필요 | semantic tuple만 보고 PASS 처리할 위험 | `timeout --signal=TERM --kill-after=5 45 build/gic720ae-qbox-platform-tests/tests/components/apollo_si_gic_irq/apollo_si_gic_irq-tests --integration-sgi-directed` | `.omo/evidence/task-13-apollo-gic720ae-implementation/` |
| 2 | 15 | `deferred-nonessential` | GICR_PWRR/WAKER bridge, SCP opt-in `test gic_power`, 3-cycle reset/power runtime | power/reset fidelity는 P0 전환 전 필요하지만 2시간 핵심 QEMU CPUif fix 범위를 넘음 | 3,11,14 | marker-only reset/power PASS 오판 | `python3 scripts/test/run_gic720ae_p0_power_reset.py --self-test-negative tests/fixtures/gic720ae/p0-power-marker-only.json --out-dir <attemptDir>/task-15-negative` | `.omo/evidence/task-15-apollo-gic720ae-implementation/` |
| 3 | 16 | `deferred-nonessential` | 단일 SI GDB endpoint 12341에서 CL0/CL1 selector와 5 thread attach 검증 | SI runtime validation의 지원 기능이지만 current QEMU extended interrupt proof와 분리 | 8-12 | TCP connect만으로 GDB PASS 오판 | `python3 scripts/debug/run_gic720ae_si_gdb_smoke.py --launcher ./run_qbox_local_debug.sh --symbols-json build/local-apollo-qvp/debug/symbols.json --endpoint 127.0.0.1:12341 --timeout 120 --out-dir <attemptDir>/task-16-apollo-gic720ae-implementation` | `.omo/evidence/task-16-apollo-gic720ae-implementation/` |
| 4 | 17 | `essential-blocked/deferred` | SCP CL0 controlled IRQ/FMU command injection, negative self-test, FVP profile producer | 13/15/16이 deferred라 plan closure상 지금 PASS 불가 | 3,5,13-16 | generic NI FMU 또는 marker-only evidence로 대체할 위험 | `python3 scripts/test/run_gic720ae_scp_validation.py --self-test-negative tests/fixtures/gic720ae/scp-marker-only.json --out-dir <attemptDir>/task-17-negative` | `.omo/evidence/task-17-apollo-gic720ae-implementation/` |
| 5 | 18 | `essential-blocked/deferred` | Zephyr CL1 directed/broadcast IPI, timer PPI, cross-view negative Test Driver | 13/15/16이 deferred라 QVP/FVP CL1 runtime proof가 닫히지 않음 | 3,5,13-16 | build-only를 runtime PASS로 오판 | `python3 scripts/test/run_gic720ae_zephyr_validation.py --self-test-negative tests/fixtures/gic720ae/zephyr-wrong-affinity.json --out-dir <attemptDir>/task-18-negative` | `.omo/evidence/task-18-apollo-gic720ae-implementation/` |
| 6 | 19 | `deferred-nonessential` | P0 gate 뒤 single-SI default 전환과 split rollback 동일 SHA 검증 | 15/17/18 없이는 default 전환 금지 | 12,15-18 | split rollback 없이 default를 바꿀 위험 | `python3 scripts/test/validate_gic720ae_default_switch.py --matrix doc/validation/gic-720ae/feature-matrix.yaml --evidence-root <attemptDir> --status-output-dir <attemptDir>/task-19-apollo-gic720ae-implementation` | `.omo/evidence/task-19-apollo-gic720ae-implementation/` |
| 7 | 24 | `deferred-nonessential` | QEMU-owned GIC-720AE IIDR property와 AP/SI identity readback | Task 25의 plan dependency이며 현재 Task 27 bounded lane보다 후순위 | 4,10 | generic QEMU IIDR을 GIC-720AE로 과장할 위험 | `scripts/build/run_qemu_gic720ae_qtests.sh --test arm-gicv3-gic720ae-iidr` | `.omo/evidence/task-24-apollo-gic720ae-implementation/` |
| 8 | 25 | `essential-blocked/deferred` | QBox `spi/espi/ppi/eppi` socket ABI와 property 전달 CTest | Task 24가 deferred이므로 plan closure상 실행 가능 완료 아님 | 20-24 | flat socket index로 ESPI/EPPI를 흉내 낼 위험 | `python3 scripts/build/run_gic720ae_qbox_platform_tests.py --target arm_gicv3_extended_sockets-tests --ctest-regex '^arm_gicv3_extended_sockets-tests$' --output <attemptDir>/task-25-ctest.json` | `.omo/evidence/task-25-apollo-gic720ae-implementation/` |
| 9 | 26 | `essential-blocked/deferred` | Apollo SI capacity와 extended-range Zephyr/runtime Test Driver | Task 19/25 미완료 | 3,5,19,25 | extended register qtest만으로 SI runtime을 주장할 위험 | `python3 scripts/test/run_gic720ae_si_extended_irq.py --self-test-negative tests/fixtures/gic720ae/si-extirq-wrong-family.json --out-dir <attemptDir>/task-26-negative` | `.omo/evidence/task-26-apollo-gic720ae-implementation/` |
| 10 | 28 | `deferred-nonessential` | AP PCI MSI-X to ITS physical LPI와 INTx 비교 | PC Linux 기본 probe 뒤의 확장 검증으로 보류 | 3,5,27 | normal DT에 consumer가 없는데 LPI delivery를 주장할 위험 | `python3 scripts/test/run_gic720ae_pcie_irq_validation.py --self-test-negative tests/fixtures/gic720ae/pcie-no-irq-delta.json --out-dir <attemptDir>/task-28-negative` | `.omo/evidence/task-28-apollo-gic720ae-implementation/` |
| 11 | 32 | `deferred-nonessential` | opt-in KVM software-vLPI probe와 hardware-forwarding gap 분류 | hardware vLPI/VFIO route는 P2 gap으로 분리 가능 | 3,5,30,31 | VFIO 부재를 runtime FAIL로 과장하거나 반대로 구현 완료로 과장할 위험 | `python3 scripts/test/run_gic720ae_vlpi_software_probe.py --out-dir <attemptDir>/task-32-apollo-gic720ae-implementation` | `.omo/evidence/task-32-apollo-gic720ae-implementation/` |
| 12 | 33 | `deferred-nonessential` | SPI collator preflight가 active일 때만 message path 구현 | Task 13/17 없이는 controlled preflight 불가 | 11,13,17 | unverifiable/P2를 active PASS로 넣을 위험 | `python3 scripts/test/run_gic720ae_collator_preflight.py --self-test-negative tests/fixtures/gic720ae/collator-unavailable.json --out-dir <attemptDir>/task-33-negative` | `.omo/evidence/task-33-apollo-gic720ae-implementation/` |
| 13 | 34 | `deferred-nonessential` | GIC FMU SystemC model과 `zena_fmu` 연결 CTest | collator/SCP path 뒤 safety product layer로 보류 | 3,33 | generic FMU를 GIC internal FMU로 오판 | `python3 scripts/build/run_gic720ae_qbox_platform_tests.py --target gic720ae_fmu-tests --ctest-regex '^gic720ae_fmu-tests$' --output <attemptDir>/task-34-ctest.json` | `.omo/evidence/task-34-apollo-gic720ae-implementation/` |
| 14 | 35 | `deferred-nonessential` | SCP production FMU driver/test command end-to-end fault 검증 | Task 17/34 없이는 end-to-end fault path 없음 | 3,17,34 | NI-only PASS를 GIC fault PASS로 오판 | `python3 scripts/test/run_gic720ae_scp_validation.py --self-test-negative tests/fixtures/gic720ae/scp-generic-ni-only.json --out-dir <attemptDir>/task-35-negative` | `.omo/evidence/task-35-apollo-gic720ae-implementation/` |
| 15 | 36 | `deferred-nonessential` | 공개 RAS/GSPV error record, correction, flush 경로 | SI/extended/FMU 선행 항목 다수 미완료 | 3,17,18,26,35 | confidential safety coverage를 공개 evidence로 과장할 위험 | `python3 scripts/build/run_gic720ae_qbox_platform_tests.py --target gic720ae_ras_gspv-tests --ctest-regex '^gic720ae_ras_gspv-tests$' --output <attemptDir>/task-36-ctest.json` | `.omo/evidence/task-36-apollo-gic720ae-implementation/` |
| 16 | 37 | `deferred-nonessential` | full low-power, CPU hotplug, system reset qualification | Task 15/19 미완료 | 14,15,19 | reboot liveness만으로 reset/power fidelity를 주장할 위험 | `python3 scripts/test/run_gic720ae_final_qualification.py --scenario low-power-reset --out-dir <attemptDir>/task-37-apollo-gic720ae-implementation` | `.omo/evidence/task-37-apollo-gic720ae-implementation/` |
| 17 | 38 | `essential-blocked/deferred` | SI FVP/QBox 동일 stimulus differential | 17/18/26/33-37 미완료 | 2,17,18,26,33-37 | FVP comparison 없이 SI parity를 완료로 주장할 위험 | `python3 scripts/test/build_gic720ae_fvp_profiles.py --dry-run --verify-explicit-overrides --profiles standard,extirq,power --output-root <attemptDir>/task-38-fvp-builder-contract` | `.omo/evidence/task-38-apollo-gic720ae-implementation/` |
| 18 | 39 | `essential-blocked/deferred` | scope audit, repository commit, implementation input freeze | Task 1-38 closure 미완료 | 1-38 | stale freeze로 final gates를 실행할 위험 | `python3 scripts/test/capture_gic720ae_source_state.py --plan .omo/plans/apollo-gic720ae-implementation.md --output <attemptDir>/task-39-apollo-gic720ae-implementation/implementation-source-manifest.json` | `.omo/evidence/task-39-apollo-gic720ae-implementation/` |
| 19 | 40 | `essential-blocked/deferred` | fresh Primary Compute Linux 최종 qualification | 19/26/32/38/39 미완료 | 5,19,26,27,29,32,38,39 | Task 27 부분 결과를 final Linux gate로 오판 | `python3 scripts/test/run_gic720ae_final_qualification.py --domain linux --out-dir <attemptDir>/task-40-apollo-gic720ae-implementation` | `.omo/evidence/task-40-apollo-gic720ae-implementation/` |
| 20 | 41 | `essential-blocked/deferred` | fresh SI CL0/CL1 최종 qualification | 19/26/32/38-40 미완료 | 5,19,26,32,38-40 | SCP/Zephyr liveness를 controlled stimulus로 오판 | `python3 scripts/test/run_gic720ae_final_qualification.py --domain safety-island --out-dir <attemptDir>/task-41-apollo-gic720ae-implementation` | `.omo/evidence/task-41-apollo-gic720ae-implementation/` |
| 21 | 42 | `essential-blocked/deferred` | fresh FVP differential과 full coverage audit | 33/40/41 미완료 | 33,40,41 | historical FVP log를 fresh final evidence로 오판 | `python3 scripts/test/run_gic720ae_final_qualification.py --domain fvp-differential --out-dir <attemptDir>/task-42-apollo-gic720ae-implementation` | `.omo/evidence/task-42-apollo-gic720ae-implementation/` |
| 22 | 43 | `essential-blocked/deferred` | 한글 구현 계획/분석/테스트 완료 문서 동기화 | freeze와 final qualification 미완료 | 39-42 | deferred 구현을 완료 구현처럼 문서화할 위험 | `python3 scripts/test/audit_gic720ae_docs.py --plan .omo/plans/apollo-gic720ae-implementation.md --output <attemptDir>/task-43-apollo-gic720ae-implementation/docs-audit.json` | `.omo/evidence/task-43-apollo-gic720ae-implementation/` |
| 23 | 44 | `essential-blocked/deferred` | read-only repository/pointer/rollback release exit gate | 1-43 전체 closure 미완료 | 1-43 | dirty/stale source를 release candidate로 승인할 위험 | `python3 scripts/test/build_gic720ae_final_review_envelope.py --plan .omo/plans/apollo-gic720ae-implementation.md --output <releaseEvidenceDir>/final-review-envelope.json` | `.omo/evidence/task-44-apollo-gic720ae-implementation/` |
| 24 | F1 | `essential-blocked/deferred` | isolated plan compliance audit | Task 44 envelope 미완료 | 44 | plan hash/ledger hash를 재측정하지 않는 reviewer receipt | `python3 scripts/test/audit_gic720ae_plan_compliance.py --plan .omo/plans/apollo-gic720ae-implementation.md --output <releaseEvidenceDir>/f1-plan-compliance-input.json` | `<releaseEvidenceDir>/f1-*` |
| 25 | F2 | `essential-blocked/deferred` | isolated code quality review | Task 44 envelope 미완료 | 44 | collector-only diff review로 승인할 위험 | `python3 scripts/test/collect_gic720ae_review_diff.py --repos hsoc-stack/tools/qemu --plan .omo/plans/apollo-gic720ae-implementation.md --output <releaseEvidenceDir>/f2-review-input.json` | `<releaseEvidenceDir>/f2-*` |
| 26 | F3 | `essential-blocked/deferred` | real manual QA, Yocto/QBox/SCP/Zephyr/FVP 실행 | Task 44 envelope와 Task 40-42 미완료 | 44 | dry-run/marker-only/TCP-connect-only manual QA | `python3 scripts/test/run_gic720ae_manual_qa_postprocess.py --plan .omo/plans/apollo-gic720ae-implementation.md --output <releaseEvidenceDir>/f3-manual-qa.json` | `<releaseEvidenceDir>/f3-*` |
| 27 | F4 | `essential-blocked/deferred` | scope fidelity gate | Task 44 envelope와 F1-F3 receipt 미완료 | 44,F1-F3 | mirrored GIC state나 permanent test ABI를 놓칠 위험 | `python3 scripts/test/audit_gic720ae_scope_fidelity.py --plan .omo/plans/apollo-gic720ae-implementation.md --reference doc/validation/gic-720ae/reference-contract.yaml --matrix doc/validation/gic-720ae/feature-matrix.yaml --output <releaseEvidenceDir>/f4-scope-fidelity-input.json` | `<releaseEvidenceDir>/f4-*` |
| 28 | 45 | `essential-blocked/deferred` | `$commit-atomic` final atomic-commit closure | 44와 F1-F4 승인 전 commit closure 금지 | 44,F1-F4 | stale review 뒤 몰래 commit할 위험 | `python3 scripts/test/audit_gic720ae_release_commits.py --plan .omo/plans/apollo-gic720ae-implementation.md --output <releaseEvidenceDir>/publication/commit-audit.json` | `<releaseEvidenceDir>/publication/commit-*` |
| 29 | 46 | `essential-blocked/deferred` | `$github-push` changed nested-first/top-last publish | Task 45 전 push 금지 | 45 | unowned remote 또는 stale SHA push | `python3 scripts/test/run_gic720ae_github_push.py --mode audit --owner cometzero --manifest <releaseEvidenceDir>/publication/publish-manifest.json --output <releaseEvidenceDir>/publication/github-push-audit.json` | `<releaseEvidenceDir>/publication/github-push-*` |

## 5. Gate 정의

### 5.1 Bounded two-hour gate

이번 최소 실행 목표의 PASS는 다음을 모두 만족할 때만 가능하다.

1. Task 27이 필요한 user namespace를 허용하는 host/environment에서 유효한
   opt-in tuple을 만든 뒤에만 PC Linux probe를 실행한다.
2. 이 문서의 classification validator가 30/30 exactly-once를 유지한다.
3. Task 27의 current integration BLOCKED와 no-runtime-PASS 경계를 보존한다.
4. deferred task를 구현 완료로 표현하지 않는다.

이 gate는 전체 GIC-720AE FVP parity completion이 아니다.

### 5.2 Final product completion gate

최종 완료를 주장하려면 아래 gate가 모두 current source freeze에 묶여야 한다.

| Gate marker | 필요 조건 |
| --- | --- |
| Linux gate | Task 27과 Task 40이 fresh PC Linux controlled probe, default exclusion, final qualification을 PASS |
| SCP gate | Task 17과 Task 41이 CL0 controlled IRQ/FMU command와 final SI qualification을 PASS |
| Zephyr gate | Task 18과 Task 41이 CL1 SMP/IPI/timer/cross-view Test Driver runtime을 PASS |
| FVP gate | Task 38과 Task 42가 동일 stimulus FVP/QBox differential과 full coverage audit을 PASS |
| Commit gate | Task 39/43 freeze와 Task 44/F1-F4 review receipt 이후 Task 45가 signed atomic commit closure를 PASS |
| Push gate | Task 46이 `cometzero` owned remotes에 changed nested-first/top-last publish 후 remote SHA 일치를 PASS |
| Poweroff gate | Task 27 integration BLOCKED인 현재는 push와 `sudo poweroff`가 모두 비인가·부적격이다. 모든 essential gate, signed commit, verified push, cleanup과 사용자 확인 이후에만 최종 post-push/post-cleanup action으로 검토할 수 있다. `sudo poweroff`는 validation step이 아니다. |

## 6. RED 조건

다음 중 하나라도 발생하면 이 보고서 자체가 RED다.

- 30개 미완료 task 중 누락 또는 중복 분류가 있다.
- `essential-now`에 항목을 넣거나 Task 27 host-policy blocker를 숨긴다.
- `essential-blocked/deferred`를 구현 완료처럼 표현한다.
- Task 23 confirmed 완료나 Task 27 integration BLOCKED/no-runtime-PASS 상태를 왜곡한다.
- BitBake network isolation을 약화하는 code/config bypass를 안전한 해결책으로 주장한다.
- Linux/SCP/Zephyr/FVP/commit/push/poweroff gate가 current source freeze와
  분리된다.

## 7. 검증 artifact

보고서 final refresh의 inventory와 dependency closure는
`.omo/evidence/apollo-gic720ae-essential-scope/report-final-refresh/`에 저장했다.

| 파일 | 의미 |
| --- | --- |
| `inventory-validation.log` | plan/ledger SHA, checkbox count, 최신 seq, 미완료 inventory |
| `dependency-closure.json` | 30개 분류, 누락/중복, Task 27 blocked dependency 사유 |
| `automated-verify.log` | 문서/분류/path/link/diff 검증 |
| `manual-report-check.log` | tmux send-keys manual QA channel 결과 |
| `cleanup-receipt.txt` | owned tmux/process/temp cleanup 확인 |
| `SHA256SUMS` | evidence root hash manifest |

Task 27 blocker source evidence는 기존 task root의
`integration/{doneclaim.json,report.md,profile-kernel-deploy.log,SHA256SUMS}`와
`independent-blocker-verification/{AdversarialVerify.md,verdict.json,SHA256SUMS}`
를 사용한다. 통합 manifest SHA는
`38192afaba5ba99b8d2c930f11bf3ad9318c7bc0eaefb63fc62c0f4d16915d95`, 독립
검증 manifest SHA는
`36099f4f97cfa1127641887ee16beea303c2c9685381c48a9c6013c2e6d66514`다.
