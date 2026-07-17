# I3 - MMU-720AE/SMMUv3 통합 완료 보고서

- 완료일: 2026-07-16
- 판정: `complete`
- 대상: AP GPEX LTI00, Stream ID `0x40`, stage-1 4 KiB translation

## 설계 결정과 구현 범위

QBox 공용 `smmuv3` 모델은 linear STE/CD, 4 KiB page walk, CMDQ/TLBI,
EVTQ와 level IRQ를 이미 동일한 translation state owner 안에서 구현한다. Apollo
전용 walker를 복제하지 않고 `systemc-mmu720ae` backend의 Lua integration shell이
다음 결선을 소유하도록 변경했다.

- `smmuv3`: MMU register와 translation/queue state owner
- `smmuv3_tbu`: GPEX LTI00 DMA ingress, topology/Stream ID `0x40`
- `target_socket`: AP SMMU programmer-model window `0x1c0000000..0x1c7ffffff`
- `dma`: STE/CD/page-table/CMDQ/EVTQ 접근을 AP canonical memory에 연결
- `downstream_socket`: 번역된 GPEX DMA를 AP router에 연결
- `irq_eventq`: AP GIC SPI 65에 연결
- reset: AP cold-reset fanout에 연결

Apollo profile은 PAMAX 48, SIDSIZE 8, ATO off, TBU 1개와 IIDR
`0x720ae000`을 설정한다. 기존 qbox-platform `mmu720ae` register-only 모델은
active machine 경로에서 제거했지만 회귀 비교용 target과 unit test는 보존했다.

## 변경 파일

QBox core qualification:

- `tests/components/smmuv3/smmuv3-tests.cc`

QBox platform:

- `CMakeLists.txt`
- `platforms/apollo/hw-block/config.lua`
- `platforms/apollo/hw-block/ap_compute.lua`
- `platforms/apollo/hw-block/transaction_routes.lua`
- `platforms/apollo/hw-block/signal_routes.lua`

최상위 검증과 문서:

- `scripts/test/audit_qbox_apollo_ap_memory_map.py`
- `scripts/test/validate_qbox_apollo_fvp_full_map.py`
- `scripts/test/validate_qbox_apollo_fidelity_contract.py`
- `tests/test_apollo_qvp_smmuv3_wiring.py`
- `tests/test_validate_qbox_apollo_topology.py`
- `tests/test_validate_qbox_apollo_fidelity_contract.py`
- `doc/apollo-qbox-full-model/coverage-ledger.md`
- I3 계획, 단계 README와 이 완료 보고서

`hsoc-stack/components/**`는 수정하지 않았다.

## 핵심 기능 검증

공용 `smmuv3-tests`는 다음 I3 acceptance를 실제 TLM transaction으로 검증한다.

1. linear STE/CD와 4 KiB page mapping을 통한 DMA write 및 read
2. unmapped IOVA가 EVTQ record와 event IRQ를 만들고 downstream backing 값을
   변경하지 않음
3. leaf mapping 변경 뒤 CMDQ TLBI가 IOTLB를 비우고 새 PA를 사용함

```text
cmake --build build/qbox-core-tests --target smmuv3-tests --parallel $(nproc)
ctest --test-dir build/qbox-core-tests \
  -R '^smmuv3-tests$' --output-on-failure
결과: PASS, 1/1 CTest, 3.56초

/usr/bin/python3 -m pytest -q \
  tests/test_apollo_qvp_smmuv3_wiring.py \
  tests/test_validate_qbox_apollo_topology.py \
  tests/test_validate_qbox_apollo_fidelity_contract.py
결과: PASS, 25 passed

/usr/bin/python3 scripts/test/validate_qbox_apollo_fvp_full_map.py \
  --out build/qbox-apollo-qvp/i3-full-map.json
/usr/bin/python3 scripts/test/audit_qbox_apollo_ap_memory_map.py \
  --check coverage \
  --output build/qbox-apollo-qvp/i3-ap-map-audit.json
결과: PASS

./local_build.sh qbox
결과: PASS
  qbox-configure: 4초
  qbox-build: 33초
  최종 target: smmuv3, platforms-vp, apollo_fvp_full_system
```

## 동적 구성 확인

30초 제한의 full-system smoke를 실행해 Lua module factory가 `smmuv3` 코어와
LTI00 TBU를 생성하고 모든 SystemC/TLM 포트를 바인딩한 뒤 `SC_START`에 진입하는
것을 확인했다. RSE는 SI CL0/CL1 image load까지 진행했으며 SystemC unbound
socket, module, Lua 또는 SMMU 구성 오류는 없었다.

- `build/qbox-apollo-fvp/fidelity-i3-smmuv3-construction-20260716/qbox-platform.log`
- `build/qbox-apollo-fvp/fidelity-i3-smmuv3-construction-20260716/result.json`
- smoke 판정: 30초 제한에 따른 `qbox_platform_timeout`; full boot pass로 보지 않음

전체 local boot와 Yocto image boot 판정은 I7에서 수행한다.

## 잔여 범위

- 공용 코어가 구현하는 stage-2, two-level STE, 16/64 KiB granule과 translated
  DMI는 이번 I3 qualification 범위 밖이다.
- 공용 코어의 전체 IDR feature advertisement를 FVP MMU-720AE 값으로 제한하는
  capability profile은 잔여 fidelity 부채다.
- GERROR, secure event, PRI와 RAS aggregation은 I5 event-plane 범위다.
- ACE1/ACE2/LTI01/LTI02 ingress는 현재 active GPEX 경로에 연결하지 않았다.
