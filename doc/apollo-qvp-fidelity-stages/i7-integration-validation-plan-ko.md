# I7 - Local 및 Yocto 통합 검증 계획

## 목적

I0~I6에서 실제로 구현된 slice를 동일한 4 CPU smoke 계약으로 local artifact와
Yocto artifact에서 각각 한 번 검증한다.

## 구현 범위

- `scripts/run/run_qbox_apollo_fidelity.py`를 추가해 기존 full-system runner를
  감싸고 provenance/CPU/fidelity marker를 표준 bundle로 만든다.
- local과 Yocto artifact selector를 분리하고 혼합을 거부한다.
- manifest에 source revision, artifact SHA-256, backend, CCI와 resolved topology를
  기록한다.
- FVP 비교 도구는 boot milestone과 구현된 대표 marker만 비교하고 차이를
  `equivalent`, `intentional-abstraction`, `partial-model`, `blocker`로 분류한다.

## 최소 검증 순서

```bash
./local_build.sh qbox
python3 scripts/run/run_qbox_apollo_fidelity.py \
  --artifacts local --cpus 4 --profile smoke
./yocto_build.sh
python3 scripts/run/run_qbox_apollo_fidelity.py \
  --artifacts yocto --cpus 4 --profile smoke
```

FVP 실행 환경이 유효할 때만 focused comparison을 한 번 수행하며, 환경 부재는
근거와 함께 `deferred`로 분류한다.

## 완료 조건과 보고서

- local과 Yocto 결과가 각각 자신의 artifact hash를 기록한다.
- RSE/SI/AP release, Linux boot와 online CPU 4가 통과한다.
- 구현된 fidelity marker는 실행 여부와 결과를 명시한다.
- 보고서: `i7-integration-validation-completion-2026-07-17-ko.md`
