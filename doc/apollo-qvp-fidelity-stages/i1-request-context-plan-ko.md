# I1 - 공통 Request Context 구현 계획

## 목적

QEMU ingress에서 생성된 요청 식별자와 보안 속성을 router, translator와 target까지
손실 없이 전달할 수 있는 공통 TLM extension을 만든다.

## 구현 범위

- 소유 저장소는 `hsoc-stack/tools/qbox`다.
- opaque origin/domain ID, requester/substream ID, security, privilege,
  instruction/ATS, access path와 capability를 C++14 POD 형태로 정의한다.
- TLM extension의 `clone()`/`copy_from()`과 payload lifetime을 구현한다.
- `QemuInitiatorSocket::qemu_io_access()`에서 기존
  `QemuMemTxAttrsTlmExtension`을 유지하면서 공통 context를 부착한다.
- regular/debug/direct/reentrant 분기는 관찰 정보만 바꾸고 permission을 바꾸지
  않는다.

## 최소 검증

- clone/copy가 모든 필드를 보존하는 단위 시험 하나
- QEMU access path별 context 설정 시험 하나
- 기존 qemu-components 관련 target 빌드와 `git diff --check`
- 통과 후 `./local_build.sh qbox`

## 완료 조건과 보고서

- 요청 동안 context가 유효하고 nested 요청 뒤 stale extension이 남지 않는다.
- 기존 `MemTxAttrs` 변환과 결과 mapping이 회귀하지 않는다.
- 보고서: `i1-request-context-completion-2026-07-16-ko.md`
