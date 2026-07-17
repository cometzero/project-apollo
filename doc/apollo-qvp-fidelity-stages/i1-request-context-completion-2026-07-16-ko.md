# I1 - 공통 Request Context 완료 보고서

- 완료일: 2026-07-16
- 판정: `complete`
- 대상: QBox QEMU ingress, loader, AP/RSE/SI/GPEX initiator

## 구현 결과

공통 `RequestContextTlmExtension`을 QBox core에 추가하고 QEMU ingress부터
router/translator/target까지 전달할 수 있게 했다. context는 다음 정보를 명시적
validity bit와 함께 보존한다.

- origin/domain, requester/substream ID
- secure, privileged, instruction, ATS 속성
- regular/debug/direct/reentrant/DMI access path
- boot loader, authenticated image, debugger capability

QEMU `MemTxAttrs`가 실제로 제공하는 secure/debug 정보만 공통 context로
정규화한다. 현재 libqemu ABI가 제공하지 않는 privilege, instruction, ATS 값은
추정하지 않고 validity를 false로 유지한다. 기존
`QemuMemTxAttrsTlmExtension`은 호환성을 위해 그대로 함께 전달한다.

CPU, GPEX bus master, global peripheral initiator와 loader에 CCI 기반 base context를
추가했다. Apollo Lua는 AP CPU0~CPU3, RSE, SI0, SI1, GPEX와 loader에 서로 다른
origin/domain/requester ID를 지정한다. SMMUv3는 기존 전용 extension이 없을 때
공통 context의 substream/security를 사용한다.

stack payload의 extension은 요청 종료 전에 제거하고, clone/copy는 모든 필드와
validity를 보존한다. DMI 경로도 별도 access path로 표시하되 권한을 새로
추론하지 않는다.

## 변경 파일

QBox core:

- `systemc-components/common/include/tlm-extensions/request-context.h`
- `qemu-components/common/include/ports/initiator.h`
- `qemu-components/common/include/cpu.h`
- `qemu-components/global_peripheral_initiator/include/global_peripheral_initiator.h`
- `qemu-components/pci/qemu_gpex/include/qemu_gpex.h`
- `systemc-components/common/include/loader.h`
- `systemc-components/smmuv3/include/smmuv3.h`
- `tests/components/request-context/`
- `tests/components/CMakeLists.txt`

QBox platform:

- `platforms/apollo/hw-block/config.lua`
- `platforms/apollo/hw-block/ap_compute.lua`
- `platforms/apollo/hw-block/rse.lua`
- `platforms/apollo/hw-block/si_cl0.lua`
- `platforms/apollo/hw-block/si_cl1.lua`
- `platforms/apollo/hw-block/transaction_routes.lua`

최상위 문서와 검증 도구:

- `scripts/test/validate_qbox_apollo_fidelity_contract.py`
- `tests/test_validate_qbox_apollo_fidelity_contract.py`
- `doc/apollo-qbox-full-model/coverage-ledger.md`
- 이 완료 보고서

## 검증 결과

```text
cmake --build build/qbox-core-tests --target request-context-tests
ctest --test-dir build/qbox-core-tests -R request-context-tests \
  --output-on-failure
결과: PASS, 1/1 CTest 및 내부 GoogleTest 3개 통과

cmake --build build/qbox-core-tests --target \
  loader smmuv3 global_peripheral_initiator qemu_gpex \
  cpu_arm_cortexM55 cpu_arm_cortexR52
결과: PASS

find hsoc-stack/tools/qbox-platform/platforms/apollo/hw-block \
  -name '*.lua' -print0 | xargs -0 -n1 luac -p
결과: PASS

./local_build.sh qbox
결과: PASS
  qbox-configure: 5초
  qbox-build: 56초
  최종 target: platforms-vp, apollo_fvp_full_system

/usr/bin/python3 -m pytest -q \
  tests/test_validate_qbox_apollo_fidelity_contract.py
결과: 3 passed in 0.16s

/usr/bin/python3 scripts/test/validate_qbox_apollo_fvp_full_map.py
결과: PASS

/usr/bin/python3 scripts/test/audit_qbox_core_boundary.py
결과: QBox core boundary audit passed

git -C hsoc-stack/tools/qbox diff --check
git -C hsoc-stack/tools/qbox-platform diff --check
결과: PASS
```

## Evidence

- `build/local-apollo-qvp/logs/qbox-configure.log`
- `build/local-apollo-qvp/logs/qbox-build.log`
- `build/local-apollo-qvp/logs/local-build-timings.tsv`
- `build/qbox-apollo-qvp/fidelity-contract-4cpu.json`
- `build/qbox-apollo-qvp/full-map-validation.json`

## 잔여 범위

I1에서는 context 전달 계약만 구현했다. context를 실제 allow/deny 정책으로
판정하는 NI-710AE APU data path는 I2 범위다. full-system runtime boot와 Yocto
검증은 I7에서 수행하므로, 이번 단계의 local build 성공을 runtime 통과로
간주하지 않는다.
