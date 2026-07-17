# I6 - System Software ABI 오류와 Recovery 완료 보고서

- 완료일: 2026-07-16
- 판정: `complete`
- 대상: Apollo CFG2, AP CPU0~CPU3
- acceptance slice: SCMI/PFDI malformed length와 HIPC/RPMsg invalid descriptor

## 소유권과 범위

`software_contract.lua`, Zena CSS PFDI/SCMI/HIPC 문서와 현재 runtime graph를
대조했다. QBox platform의 `mhu320ae`가 직접 소유하는 동작은 SCMI/PFDI
shared-memory response와 opt-in RPMsg name-service injection이다. PSCI invalid
MPIDR/state는 TF-A, FF-A descriptor 오류는 OP-TEE/Linux가 소유하므로 QBox에서
가짜 firmware 응답을 만들지 않았다.

PFDI의 per-core region은 Zena CSS Zephyr source와 동일한 40바이트 stride를
사용한다. 일반 SCMI mailbox 상한은 Apollo SCP 계열의 128바이트 mailbox
계약을 사용하고, stride가 있는 경우 실제 channel region보다 큰 message를
허용하지 않는다.

## 발견한 결함과 구현 결과

수정 전 `mhu320ae`는 SCMI `length`를 검증하지 않았다. 4바이트 message header보다
짧은 3바이트 PFDI 요청도 정상 `PROTOCOL_VERSION` 요청으로 처리해 success를
반환했다. 큰 값은 payload vector와 TLM read 범위를 제한하지 못했다.

수정 결과는 다음과 같다.

- 길이는 `4 <= length <= channel capacity`일 때만 decode한다.
- 일반 channel capacity는 128바이트, 40바이트 PFDI region은 header offset을
  제외한 16바이트다.
- 잘못된 길이는 `SCMI_PROTOCOL_ERROR(-10)`와 8바이트 error response로 끝난다.
- error response도 `SCMI_CHAN_STATUS=FREE`를 게시하고 polling requester가 다음
  요청을 보낼 수 있게 한다.
- malformed request에서는 power/reset 등 protocol side effect를 실행하지 않는다.
- RPMsg의 범위 밖 descriptor ID는 최대 4회 poll 뒤 종료하고, synthetic TX
  completion이 PBX 상태를 정리한다. descriptor를 고친 다음 doorbell은 정상
  name-service message와 MBX notification을 만든다.

Apollo software contract에도 SCMI/PFDI의 `protocol_error`와
`channel_free_next_request`, HIPC의 `bounded_poll_timeout`과
`next_doorbell_retry`를 기록했다.

## 변경 파일

QBox platform:

- `systemc-components/mhu320ae/include/mhu320ae.h`
- `tests/components/mhu320ae/mhu320ae-tests.cc`
- `platforms/apollo/hw-block/software_contract.lua`
- `platforms/apollo/README.md`

최상위 검증과 문서:

- `tests/test_apollo_qvp_software_abi_recovery.py`
- fidelity contract/ledger, architecture/roadmap 문서와 이 보고서

`hsoc-stack/components/**`, QBox core와 QEMU 소스는 I6에서 수정하지 않았다.

## Red/Green 및 단위 검증

동일 test를 구현 전에 실행해 3바이트 PFDI 요청이 success/12바이트 응답으로
잘못 끝나는 것을 재현했다.

```text
수정 전 mhu320ae-tests:
expected SCMI_LENGTH 8, observed 12
expected SCMI_PROTOCOL_ERROR 0xfffffff6, observed 0
결과: FAIL, 1/2 tests

cmake --build build/local-apollo-qvp/work/qbox-platform \
  --target mhu320ae-tests --parallel 8
ctest --test-dir build/local-apollo-qvp/work/qbox-platform \
  -R '^mhu320ae-tests$' --output-on-failure
수정 후 결과: PASS, 1/1 ctest target
```

SystemC test 하나에서 다음 순서를 확인했다.

1. malformed PFDI length → protocol error → channel FREE
2. 같은 channel의 정상 PFDI version request → success
3. invalid RPMsg descriptor → bounded timeout → PBX completion/IRQ clear 가능
4. descriptor 수정과 다음 doorbell → name-service payload와 MBX signal 성공

## Local QBox 및 정적 검증

```text
./local_build.sh qbox --qbox-unit-tests --no-package --jobs 8
결과: PASS, QBox configure/build 및 component suite 33/33

/usr/bin/python3 -m pytest -q \
  tests/test_apollo_qvp_software_abi_recovery.py \
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

I6은 protocol component의 오류와 즉시 recovery를 검증하는 단계다. 4 CPU
full-system local/Yocto image runtime은 I7에서 동일 source 상태로 수행한다.

## Deferred Fidelity 부채

- PSCI invalid MPIDR, already-on/off와 reset transition 오류는 TF-A 기반 runtime
  검증이 필요하다.
- FF-A invalid endpoint/memory descriptor는 OP-TEE/Linux 기반 runtime 검증이
  필요하다.
- SCMI protocol/message별 payload 최소 길이 전체 matrix, denied, peer-offline,
  reset 중 request와 duplicate notification은 extended validation이다.
- service-modeled RPMsg endpoint를 실제 SI CL1 Zephyr/OpenAMP peer로 대체하는
  작업은 별도 architecture 부채다.
