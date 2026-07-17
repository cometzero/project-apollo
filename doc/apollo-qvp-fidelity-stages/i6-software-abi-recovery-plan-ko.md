# I6 - System Software ABI 오류와 Recovery 구현 계획

## 목적

잘못된 protocol request가 무한 poll, stale BUSY 또는 중복 completion을 만들지 않고
정상 요청으로 회복되는 platform-side 동작을 고정한다.

## 구현 범위

- 수정 범위는 QBox/QBox-platform/QEMU이며 firmware/Linux 등
  `hsoc-stack/components/**`는 변경하지 않는다.
- 현재 platform model이 소유한 SCMI/PFDI, PSCI, MHU, HIPC/RPMsg, FF-A 경로를
  inventory한다.
- 각 protocol은 대표 malformed 또는 denied 요청 하나와 cleanup/recovery만
  구현한다.
- firmware가 생성해야 하는 오류를 host model에서 합성하지 않는다. 이 경우
  검증 가능 범위와 blocker를 보고한다.
- 우선순위는 SCMI/PFDI, PSCI, MHU이며 나머지는 후속으로 분리할 수 있다.

## 최소 검증

- 대표 오류가 유한 시간 안에 정해진 error code로 종료됨
- channel/BUSY/doorbell 상태가 정리됨
- 바로 다음 정상 transaction이 성공함
- 관련 unit target 후 `./local_build.sh qbox`

## 구현 결정

- QBox platform이 직접 응답을 소유하는 SCMI/PFDI shared-memory transport는
  message length 하한과 channel capacity를 검사한다. 위반 시
  `SCMI_PROTOCOL_ERROR(-10)`를 기록하고 channel을 FREE로 반환한다.
- HIPC/RPMsg host name-service 계측은 잘못된 descriptor를 bounded poll로
  종료한 뒤 다음 doorbell에서 정상 descriptor를 다시 소비할 수 있어야 한다.
- PSCI invalid MPIDR/state와 FF-A descriptor 오류는 TF-A/OP-TEE가 소유한다.
  QBox host model에서 firmware 응답을 합성하지 않고 I6 범위 밖으로 둔다.
- peer-offline, reset 중 취소, 모든 protocol/message별 payload 길이 matrix는
  이번 최소 gate가 아니라 후속 extended validation으로 유지한다.

## 완료 조건과 보고서

model이 실제 소유한 protocol별로 오류, cleanup, 다음 정상 요청을 증명한다. 소유하지
않는 firmware semantics는 `deferred`로 남긴다.

- 보고서: `i6-software-abi-recovery-completion-2026-07-16-ko.md`
