# I0 - 4 CPU 계약과 Fidelity Ledger 완료 보고서

- 완료일: 2026-07-16
- 판정: `complete`
- 대상: `apollo-qvp`, RD-Aspen CFG2, CPU0~CPU3

## 구현 결과

기존 Apollo topology exporter의 결과를 재사용하는
`scripts/test/validate_qbox_apollo_fidelity_contract.py`를 추가했다. 별도의 topology
정의를 만들지 않고 다음 항목을 한 JSON에서 판정한다.

- active machine과 variant: `apollo-qvp`, `cfg2`
- configured AP CPU 수와 허용 CPU ID: 4, CPU0~CPU3
- AP reset과 cross-domain default-deny 상태
- RSE 인증/ATU·APU 설정/SI 확인/AP release의 owner 순서
- workspace, QBox, QBox-platform, QEMU source revision
- active config와 machine contract source의 SHA-256
- 선택적 runtime 결과의 AP CPU count와 CPU4 이상 관찰 여부
- I0~I8 fidelity 단계 상태

runtime JSON을 입력하지 않은 검사는 `skip`으로 남긴다. CPU4를 포함한 fixture는
의도대로 실패하며, performance 수치는 계약에서 `not-required`로 기록한다.

## 변경 파일

- `scripts/test/validate_qbox_apollo_fidelity_contract.py`
- `tests/test_validate_qbox_apollo_fidelity_contract.py`
- `doc/apollo-qbox-full-model/coverage-ledger.md`
- `doc/apollo-qvp-fidelity-stages/i0-4cpu-contract-plan-ko.md`
- 이 완료 보고서

## 검증 결과

```text
/usr/bin/python3 -m py_compile \
  scripts/test/validate_qbox_apollo_fidelity_contract.py \
  tests/test_validate_qbox_apollo_fidelity_contract.py
결과: PASS

/usr/bin/python3 -m pytest -q \
  tests/test_validate_qbox_apollo_fidelity_contract.py
결과: 3 passed in 0.17s

/usr/bin/python3 scripts/test/validate_qbox_apollo_fidelity_contract.py \
  --cpus 4 --fail-on-enabled-cpu-above 3 \
  --runtime-result \
  build/qbox-apollo-fvp/architecture-debt-local-final-v1-20260716/result.json \
  --output build/qbox-apollo-qvp/fidelity-contract-4cpu.json
결과: PASS, 11개 check 모두 pass

/usr/bin/python3 scripts/test/validate_qbox_apollo_fvp_full_map.py
결과: PASS

/usr/bin/python3 scripts/test/audit_qbox_core_boundary.py
결과: QBox core boundary audit passed

git diff --check
git -C hsoc-stack/tools/qbox diff --check
git -C hsoc-stack/tools/qbox-platform diff --check
git -C hsoc-stack/tools/qemu diff --check
결과: PASS
```

기본 `python3`는 현재 browser-use 가상환경을 가리키며 `pytest`가 없었다. 프로젝트
시험은 pytest 8.3.4가 설치된 `/usr/bin/python3`로 재실행해 통과했다.

## Evidence

- `build/qbox-apollo-qvp/fidelity-contract-4cpu.json`
- `build/qbox-apollo-qvp/topology/validation.json`
- `build/qbox-apollo-qvp/full-map-validation.json`

runtime check는 이번 단계에서 새 full-system boot를 실행한 것이 아니라, 같은 날
생성된 기존 local baseline 결과의 4 CPU 관찰값을 계약 validator에 입력한 것이다.
새 local/Yocto boot는 I7에서 각각 수행한다.

## 잔여 범위

이 보고서 작성 시점에는 I1~I8을 machine-readable ledger에서 `planned`로
유지했다. 2026-07-17 현재 상태와 증거는 단계 README와 I7/I8 완료 보고서가
대체한다. I0 통과 자체는 후속 기능 구현을 의미하지 않는다.
