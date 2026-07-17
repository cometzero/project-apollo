# I8 - Architecture와 Fidelity Ledger 종결 계획

## 목적

구현 및 검증 결과를 아키텍처 문서, roadmap과 ledger에 반영해 완료·부분·차단
범위를 추적 가능하게 만든다.

## 구현 범위

- `doc/apollo-qvp-machine-architecture-ko.md`의 실제 구조와 제한을 갱신한다.
- `doc/qbox-fvp-emulation-project.md`의 roadmap/status를 갱신한다.
- `doc/apollo-qbox-full-model/coverage-ledger.md`에 각 I 단계의 source, test,
  local/Yocto/FVP evidence를 연결한다.
- `hsoc-stack/tools/qbox-platform/platforms/apollo/README.md`에 새 runtime/validation
  interface를 반영한다.
- `components/**`가 변경되지 않았는지 최종 확인한다.

## 최소 검증

- 모든 Markdown link와 Mermaid 문법 검사
- top-level/QBox/QBox-platform/QEMU `git diff --check`
- fidelity contract와 기존 map/topology/core-boundary validator 재실행
- 완료 보고서에 정확한 명령, 결과, blocker와 후속 부채 기록

## 완료 조건과 보고서

각 단계가 `complete`, `partial`, `blocked`, `deferred` 중 하나와 증거 경로를
가지며, 실행하지 않은 항목을 pass로 표시하지 않는다.

- 보고서: `i8-closeout-completion-2026-07-17-ko.md`
