# I0 - 4 CPU 계약과 Fidelity Ledger 구현 계획

## 목적

후속 구현의 공통 기준을 machine-readable 계약으로 고정한다. active machine은
`apollo-qvp`, variant는 `cfg2`, AP CPU는 CPU0~CPU3의 네 개만 허용한다.

## 구현 범위

- `scripts/test/validate_qbox_apollo_fidelity_contract.py`를 추가한다.
- 기존 topology validator가 생성한 JSON을 단일 source of truth로 재사용한다.
- topology, reset/boot route, artifact provenance와 선택적 runtime CPU 결과를
  검증한다.
- I1~I6 항목을 상태와 증거 경로를 가진 fidelity ledger로 출력한다.
- 기존 coverage ledger에 잔여 fidelity 단계와 상태 정의를 연결한다.

## 최소 검증

```bash
python3 -m py_compile scripts/test/validate_qbox_apollo_fidelity_contract.py
python3 -m pytest -q tests/test_validate_qbox_apollo_fidelity_contract.py
python3 scripts/test/validate_qbox_apollo_fidelity_contract.py \
  --cpus 4 --fail-on-enabled-cpu-above 3 \
  --output build/qbox-apollo-qvp/fidelity-contract-4cpu.json
```

정상 fixture의 통과와 CPU 수 불일치 fixture의 실패를 각각 한 번 확인한다.

## 완료 조건과 보고서

- machine/variant/CPU/reset/boot/provenance 검사가 모두 명시적 결과를 가진다.
- CPU4 이상의 online/release evidence가 있으면 실패한다.
- 보고서: `i0-4cpu-contract-completion-2026-07-16-ko.md`
