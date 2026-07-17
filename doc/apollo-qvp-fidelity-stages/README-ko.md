# Apollo QVP 잔여 Fidelity 단계별 실행 문서

- 기준일: 2026-07-16
- 대상: `apollo-qvp`, RD-Aspen CFG2, AP CPU0~CPU3
- 구현 경계: `hsoc-stack/tools/qbox`, `hsoc-stack/tools/qemu`,
  `hsoc-stack/tools/qbox-platform`와 최상위 검증 도구
- 제외 경계: `hsoc-stack/components/**`

이 디렉터리는 잔여 fidelity 부채를 I0~I8의 독립된 단계로 구현하기 위한 실행
계획과 완료 증거를 보관한다. 각 단계는 계획 문서를 먼저 고정하고, 가장 작은
정적·단위 검증을 통과한 뒤에만 완료 보고서를 작성한다. 빌드만 성공한 결과를
runtime 통과로 간주하지 않는다.

| 단계 | 계획 | 완료 보고서 |
| --- | --- | --- |
| I0 | [4 CPU 계약과 ledger](i0-4cpu-contract-plan-ko.md) | [완료](i0-4cpu-contract-completion-2026-07-16-ko.md) |
| I1 | [공통 request context](i1-request-context-plan-ko.md) | [완료](i1-request-context-completion-2026-07-16-ko.md) |
| I2 | [NI-710AE APU](i2-ni710ae-apu-plan-ko.md) | [완료](i2-ni710ae-apu-completion-2026-07-16-ko.md) |
| I3 | [MMU-720AE/SMMUv3](i3-mmu720ae-smmuv3-plan-ko.md) | [완료](i3-mmu720ae-smmuv3-completion-2026-07-16-ko.md) |
| I4 | [GPEX MSI/ITS/LPI](i4-gpex-msi-lpi-plan-ko.md) | [완료](i4-gpex-msi-lpi-completion-2026-07-16-ko.md) |
| I5 | [fault/safety/watchdog](i5-fault-safety-plan-ko.md) | [완료](i5-fault-safety-completion-2026-07-16-ko.md) |
| I6 | [software ABI recovery](i6-software-abi-recovery-plan-ko.md) | [완료](i6-software-abi-recovery-completion-2026-07-16-ko.md) |
| I7 | [local/Yocto 통합 검증](i7-integration-validation-plan-ko.md) | [완료](i7-integration-validation-completion-2026-07-17-ko.md) |
| I8 | [종결과 ledger 갱신](i8-closeout-plan-ko.md) | [완료](i8-closeout-completion-2026-07-17-ko.md) |

공통 판정 원칙은 다음과 같다.

1. AP CPU 성능 수치는 acceptance에 포함하지 않는다.
2. 정상 경로 하나와 대표 오류 경로 하나를 핵심 검증으로 사용한다.
3. 공식 programming model로 확인되지 않은 register 의미는 구현하지 않는다.
4. 미지원 범위는 `pass`가 아니라 `blocked`, `deferred` 또는 `partial`로 기록한다.
5. local QBox 검증을 통과한 변경만 Yocto 검증으로 확대한다.
