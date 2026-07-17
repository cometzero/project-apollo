# I5 - Fault, Safety, Watchdog Event Plane 완료 보고서

- 완료일: 2026-07-16
- 판정: `complete`
- 대상: Apollo CFG2, AP CPU0~CPU3
- acceptance source: SMMUv3 event queue fault 1개

## 근거와 범위 결정

다음 로컬 Arm 문서를 기준으로 FMU record/interrupt와 SSU 상태 전이를 다시
확인했다.

- `doc/arm_zena_css_dev_guide/09-programmers-model-for-zena-css.md`
- `arm-zena-css/documentation/design/fmu.rst`
- `arm-zena-css/documentation/design/ssu.rst`
- `arm-zena-css/documentation/user_guide/reproduce.rst`

문서는 FMU의 `ERR<n>STATUS`, critical/non-critical interrupt와 SSU의
TEST/SAFE/ERRN/ERRC 상태를 근거로 제공한다. 반면 SMMU event queue가 특정
NI-710AE cluster FMU record에 물리적으로 직접 연결된다는 근거는 확인되지
않았다. 따라서 default hardware topology를 바꾸지 않고, opt-in QBox test
profile에 별도 FMU observer를 둔다. 이 observer는 검증 계측이며 FVP hardware
route parity 주장이 아니다.

사용자 요청에 맞춰 첫 source 하나만 완료 조건으로 삼았다. APU violation,
SI DCLS와 AP secure watchdog은 register/interrupt/reset ownership 근거를 각각
확정한 뒤 구현해야 하므로 이번 단계에서 추측 구현하지 않았다.

## 구현 결과

- `signal_fanout`이 실제 SMMUv3 `irq_eventq` level을 기존 GIC SPI 65와
  test-profile FMU observer에 동시에 전달한다.
- observer의 external fault input은 CCI로 enable/record/source/fault ID/sink를
  지정하며 default는 disabled다.
- fault 상승 시 FMU record가 valid가 되고 critical 또는 non-critical IRQ가
  assert된다.
- `ERR_STATUS` W1C clear가 record와 IRQ를 내리고 recovery를 완료한다.
- JSON은 `source`, `record`, `sink_assert`, `clear`, `sink_deassert`,
  `recovery`를 sequence 번호와 함께 기록한다.
- observer에는 가짜 programmer-model 주소를 만들지 않았다. `zena_fmu`의
  register target은 optional TLM target으로 바꾸되 기존 매핑된 FMU의 register
  접근은 그대로 유지했다.
- full-system과 direct AP entrypoint 모두
  `QBOX_APOLLO_FAULT_EVENT_TEST=true`일 때만 observer를 만든다.

## 변경 파일

QBox platform SystemC/TLM:

- `systemc-components/signal_fanout/CMakeLists.txt`
- `systemc-components/signal_fanout/include/signal_fanout.h`
- `systemc-components/signal_fanout/src/signal_fanout.cc`
- `systemc-components/zena_fmu/include/zena_fmu.h`
- `systemc-components/CMakeLists.txt`
- `tests/components/zena_fmu/CMakeLists.txt`
- `tests/components/zena_fmu/zena_fmu-tests.cc`
- `CMakeLists.txt`

Apollo wiring과 최상위 검증:

- `platforms/apollo/hw-block/config.lua`
- `platforms/apollo/hw-block/ap_compute.lua`
- `platforms/apollo/hw-block/primary_compute.lua`
- `platforms/apollo/hw-block/signal_routes.lua`
- `platforms/apollo/README.md`
- `tests/test_apollo_qvp_fault_event_plane.py`
- fidelity contract, coverage ledger, architecture 문서와 이 보고서

`hsoc-stack/components/**`, QBox core와 QEMU 소스는 I5에서 수정하지 않았다.

## 단위·정적 검증

실제 SystemC signal source를 FMU에 넣고 FMU critical output을 SSU에 연결했다.
동일 test process에서 disabled FMU에도 같은 source를 넣어 record와 IRQ가
변하지 않는 것을 확인했다.

```text
./local_build.sh qbox --qbox-unit-tests --no-package --jobs 8
최종 재검증: component suite PASS, 33/33

ctest --test-dir build/local-apollo-qvp/work/qbox-platform \
  -R '^(zena_fmu-tests|zena_ssu-tests)$' --output-on-failure
결과: PASS, 2/2

/usr/bin/python3 -m pytest -q \
  tests/test_apollo_qvp_fault_event_plane.py \
  tests/test_validate_qbox_apollo_topology.py \
  tests/test_validate_qbox_apollo_fidelity_contract.py
결과: PASS, 25 passed

/usr/bin/python3 scripts/test/validate_qbox_apollo_fvp_full_map.py
/usr/bin/python3 scripts/test/validate_qbox_apollo_topology.py
/usr/bin/python3 scripts/test/audit_qbox_core_boundary.py
git diff --check
git -C hsoc-stack/tools/qbox-platform diff --check
결과: PASS
```

JSON 증거:

- `build/qbox-apollo-qvp/i5-fault-event-observer.json`
- sequence 1~6:
  `source -> record -> sink_assert -> clear -> sink_deassert -> recovery`
- source: `ap_smmu_0.irq_eventq`
- fault ID: `translation-fault`
- sink: `critical_irq`

I3의 SMMUv3 test가 unmapped translation을 EVTQ에 기록하고 `irq_eventq`를
assert하는 것을 검증하고, I5 test가 동일 signal 계약을 FMU/SSU와 clear까지
검증한다. Apollo Lua source route는 두 계약을 opt-in fanout으로 연결한다.

## 4 CPU local runtime

```text
QBOX_APOLLO_NUM_CPUS=4 \
QBOX_APOLLO_FAULT_EVENT_TEST=true \
QBOX_APOLLO_FAULT_EVENT_LOG=... \
/usr/bin/python3 scripts/run/run_qbox_apollo_fvp_linux.py \
  --skip-build --timeout 60 \
  --local-build-dir build/local-apollo-qvp \
  --base-dtb build/local-apollo-qvp/deploy/boot/apollo-qvp.dtb \
  --bootargs '... maxcpus=4 ...' \
  --out-dir build/qbox-apollo-qvp/i5-fault-event-construction-r2-20260716
결과: PASS, 44.547초, Linux shell `~ #`
```

이 정상 부팅에서는 의도적인 SMMU fault가 없으므로 runtime JSON을 생성하지
않는 것이 정상이다. 이 실행은 fanout/observer Lua construction과 기존 GIC
경로의 비회귀를 검증한다. fault/clear acceptance는 위 component test와 JSON이
담당한다.

## 잔여 부채

- APU violation을 공식 FMU record에 연결하는 physical aggregation은 미구현이다.
- SI DCLS source와 SSU/ESM 정책은 미구현이다.
- AP secure watchdog의 WS0/WS1, RGM request/ack, CPU0~CPU3 reset 및 memory
  preserve/clear 정책은 별도 fidelity 부채다.
- full RSE-first local/Yocto image 통합은 I7에서 수행한다.
