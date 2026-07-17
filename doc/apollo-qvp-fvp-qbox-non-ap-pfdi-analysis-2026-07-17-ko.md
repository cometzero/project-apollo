# Apollo QVP FVP/QBox 비-AP 로그 비교 및 PFDI 수정 보고서

- 작성일: 2026-07-17
- 대상: `apollo-qvp`, CFG2, Safety Island CL1 4 CPU
- 상태: 구현 및 local/Yocto 검증 완료
- 범위: RSE, Safety Island CL0, Safety Island CL1
- 제외: AP 부팅 오류와 AP 기능 차이

## 1. 비교 기준

기준 FVP 로그는 다음 실행 결과다.

- RSE: [`rse.log`](../build/fvp-tmux/apollo-qvp-20260717-091507/uarts/rse.log)
- SI0: [`safety_island_cl0.log`](../build/fvp-tmux/apollo-qvp-20260717-091507/uarts/safety_island_cl0.log)
- SI1: [`safety_island_cl1.log`](../build/fvp-tmux/apollo-qvp-20260717-091507/uarts/safety_island_cl1.log)

수정 전 QBox 기준은
[`yocto-apollo-qvp-20260717-091350`](../build/qbox-apollo-qvp/yocto-apollo-qvp-20260717-091350/),
수정 후 Yocto 기준은
[`pfdi-requester-context-yocto-20260717-r1`](../build/qbox-apollo-qvp/pfdi-requester-context-yocto-20260717-r1/)이다.
에뮬레이터별 절대 시간은 성능 기준으로 비교하지 않고, boot milestone, register
값, protocol 상태 전이와 오류 유무만 비교했다.

## 2. 결론

| 도메인 | 수정 전 차이 | 원인 | 수정 후 판정 |
| --- | --- | --- | --- |
| RSE | CC3XX `PIDR0`가 BL2 이후 `0x0` | read-only identification register에 대한 firmware write가 backing을 변경 | 모든 단계에서 FVP와 같은 `0xc1` |
| SI0 | PFDI monitor는 정상이나 CMN discovery node 수가 FVP보다 적음 | QBox CMN은 boot용 축약 discovery model | PFDI 동작은 일치, CMN topology는 명시적 잔여 부채 |
| SI1 | core 1/3 `PFDI status timed out`, `ret=-116` | 서로 다른 QEMU instance 사이에서 requester의 virtual deadline이 SI0 응답보다 먼저 진행 | local 반복 및 Yocto 부팅에서 timeout 4종 미검출 |

PFDI 응답은 QBox가 합성하지 않는다. 실제 SI0 SCP-firmware가 기존 MHU/shared
memory 경로로 요청을 처리하는 동안 요청한 SI1 vCPU의 실행 시간만 정지하고,
SCMI channel이 `FREE`가 되면 해당 vCPU를 다시 실행한다. 따라서 firmware,
register, IRQ와 protocol owner는 바뀌지 않는다.

## 3. 도메인별 분석

### 3.1 RSE

FVP는 BL1_1, BL2와 runtime에서 모두 다음 값을 출력한다.

```text
[CC3XX] Init OK PIDR0: 0xc1
```

수정 전 QBox는 최초 접근만 `0xc1`이고 BL2 이후 두 번은 `0x0`이었다. CC3XX
model이 identification 영역 write를 일반 register write로 처리해 PIDR/CIDR
backing을 덮어쓴 것이 원인이었다. PIDR0~PIDR3와 CIDR0~CIDR1에 겹치는 write를
무시하도록 수정했고, 수정 후 Yocto 로그의 세 값은 모두 `0xc1`이다.

다음 warning은 FVP와 QBox 양쪽에 동일하므로 QBox 고유 오류가 아니다.

```text
tfm_builtin_key_loader_init: Skipping key_id 7fff816f ...
due to 40000015 platform error
```

### 3.2 Safety Island CL0

두 플랫폼 모두 SI1 core 0~3과 AP core 0~3에 대해 PFDI monitor를 시작하고,
power 상태 변화에 따라 monitoring을 전환한다. SI1 timeout의 원인은 SI0의 PFDI
module 미기동이나 MHU 주소 누락이 아니었다.

CMN discovery 결과는 다음과 같이 다르다.

| node | FVP | QBox |
| --- | ---: | ---: |
| RN-SAM | 21 | 1 |
| HN-S | 8 | 8 |
| RN-D | 3 | 0 |
| RN-F | 8 | 1 |
| RN-I | 8 | 0 |
| CCG Request Agent | 2 | 0 |
| CCG Home Agent | 2 | 0 |
| CCG Link Agent | 2 | 0 |

QBox의 `host_cmn_cyprus`는 boot에 필요한 discovery/register subset이며 실제
RD-Aspen mesh topology를 모두 표현하지 않는다. 다만 SI0는 이 결과로 초기화를
완료하고 PFDI monitor를 정상 실행하므로 이번 SI1 PFDI timeout의 직접 원인은
아니다. 정확한 node graph와 revision 정합은 별도 fidelity 부채로 유지한다.

### 3.3 Safety Island CL1

FVP는 다음 순서로 오류 없이 완료한다.

```text
Out of Reset (OoR) completed on CPU: 0..3
PFDI Agent setup complete
PFDI service ready (4 CPUs)
Network interface configured
```

수정 전 QBox도 초기 milestone은 도달하지만 guest time 1.160초에 다음 오류가
발생했다.

```text
PFDI status timed out (core=1)
PFDI status timed out (core=3)
Failed to send PFDI status (... ret=-116)
```

Apollo QBox는 SI0와 SI1을 별도 QEMU instance로 실행한다. 10 ms global quantum
안에서 SI1 requester가 PFDI doorbell을 보낸 뒤 SI0가 SystemC/TLM 경로로 요청을
처리하기 전에 SI1 guest deadline이 진행할 수 있었다. firmware timeout은 실제
wall-clock 지연이 아니라 이 virtual-time 선행 때문에 발생했다.

Focused MHU trace에서 초기 protocol setup은 channel 2, 3, 4, 5를 모두 실제
requester CPU0가 발행했다. 이후 steady-state status 요청만 channel 2→CPU0,
3→CPU1, 4→CPU2, 5→CPU3 관계를 보였다. 따라서 channel slot을 CPU 번호로
간주해 정지시키면 초기화 단계에서 잘못된 vCPU를 정지하게 된다.

대표 trace는 다음과 같다.

```text
channel=2 requester=0
channel=3 requester=0
channel=4 requester=0
channel=5 requester=0

channel=2 requester=0
channel=3 requester=1
channel=4 requester=2
channel=5 requester=3
```

## 4. 수정 아키텍처

```text
SI1 Cortex-R82 vCPU
  -> QEMU/TLM request context(requester_id)
  -> SI1 PFDI PBX doorbell
       1. paired SI0 MBX에 실제 doorbell 전달
       2. 요청한 vCPU의 sync_hold assert
  -> SI0 SCP-firmware가 MHU/shared memory 요청 처리
  -> shared-memory SCMI channel status = FREE
  -> PBX worker가 같은 requester의 sync_hold deassert
  -> SI1 vCPU와 quantum keeper 재개
```

설계 불변 조건은 다음과 같다.

1. `requester_id`는 QEMU CPU에서 TLM payload까지 전달되는 실제 vCPU identity다.
2. MHU channel은 service slot이며 CPU identity로 사용하지 않는다.
3. `sync_hold`는 guest가 관찰하는 halt/reset/power 신호가 아니라 QEMU/SystemC
   co-simulation scheduler 경계다.
4. 정지된 vCPU의 quantum keeper도 함께 중지해 guest timeout deadline이 진행하지
   않게 한다.
5. SI0 SCP-firmware가 channel을 `FREE`로 바꾼 경우에만 requester를 재개한다.
6. 기존 MHU doorbell, IRQ, shared memory와 firmware response를 그대로 사용한다.
7. 기능은 Apollo SI1 PFDI PBX에서만 opt-in하며 다른 MHU transport에 자동 적용하지
   않는다.

이 구조는 global quantum을 1 ms로 줄이거나 PFDI response를 host model에서
합성하는 방식보다 범위가 작다. 또한 architectural halt/reset을 사용하지 않아
RSE power-on과 SI1 firmware lifecycle 의미를 변경하지 않는다.

## 5. 구현 범위

| owning repository | 파일 | 변경 내용 |
| --- | --- | --- |
| QBox core | `qemu-components/common/include/cpu.h` | per-vCPU `sync_hold`, quantum keeper 정지/재개와 종료 시 unblock |
| QBox platform | `systemc-components/mhu320ae/include/mhu320ae.h` | TLM request context 기반 requester 선택, channel FREE 감시와 hold 해제 |
| QBox platform | `platforms/apollo/hw-block/si_cl1.lua` | SI1 PFDI PBX opt-in과 CPU0~CPU3 `sync_hold` 연결 |
| QBox platform | `systemc-components/cc3xx/include/cc3xx_core.h` | PIDR/CIDR write-ignore |
| QBox platform tests | `tests/components/mhu320ae/mhu320ae-tests.cc`, `tests/components/cc3xx/cc3xx_core-tests.cc` | channel과 requester 불일치, hold/release, identification write 보호 회귀 |
| top-level runner | `scripts/run/run_qbox_apollo_fvp_full.py` | SI1 로그의 PFDI timeout 4종 negative gate |
| top-level tests | `tests/test_run_qbox_apollo_fvp_full.py` | 오류 marker 및 초기화 실패 판정 회귀 |

`hsoc-stack/components/**` firmware와 OS 소스는 수정하지 않았다.

## 6. 검증 결과

### 6.1 정적 검사와 단위 시험

```text
cmake --build build/local-apollo-qvp/work/qbox-platform \
  --target mhu320ae-tests apollo_fvp_full_system --parallel 16
  -> pass

ctest --test-dir build/local-apollo-qvp/work/qbox-platform \
  -R '^mhu320ae-tests$'
  -> pass

/usr/bin/python3 -m pytest -q tests/test_run_qbox_apollo_fvp_full.py
  -> 33 passed

/usr/bin/python3 scripts/test/validate_qbox_apollo_fvp_full_map.py
  -> passed

/usr/bin/python3 scripts/test/audit_qbox_core_boundary.py
  -> passed
```

### 6.2 QBox local build와 runtime

```text
./local_build.sh qbox --qbox-unit-tests --no-package --jobs 16
  -> build pass
  -> QBox-platform component tests 33/33 passed

python3 scripts/run/run_qbox_apollo_fvp_full.py \
  --si-mode live-cl0-cl1 --timeout 600 \
  --out-dir build/qbox-apollo-qvp/pfdi-requester-context-local-20260717-r3
  -> passed: true
```

trace-off runtime `r2`, `r3`이 연속 통과했고 `r3` coverage audit도 통과했다.
두 실행에서 다음 오류 gate는 모두 `false`였다.

- `PFDI status timed out`
- `ret=-116`
- `PROTOCOL_VERSION timed out`
- `PFDI Agent device not ready`

요청자 identity 근거 trace는
[`pfdi-requester-context-local-20260717-r1/si-cl1-mhuv3-trace.log`](../build/qbox-apollo-qvp/pfdi-requester-context-local-20260717-r1/si-cl1-mhuv3-trace.log)에
기록했다.

### 6.3 Yocto provider와 이미지 runtime

```text
source layers/poky/oe-init-build-env build
bitbake qbox-apollo-qvp-native
  -> 1,056 tasks attempted, 1,048 cached, all succeeded
  -> do_check passed

./run_qbox_yocto.sh --machine apollo-qvp --headless \
  --exit-after-pass --timeout 600 \
  --out-dir build/qbox-apollo-qvp/pfdi-requester-context-yocto-20260717-r1 \
  --no-copy-disks
  -> passed: true
```

Yocto 실행은 sysroot의 `qbox-apollo-qvp-native` provider executable/Lua와 배포된
`nexios-image` WIC를 사용했다. 결과는
[`result.json`](../build/qbox-apollo-qvp/pfdi-requester-context-yocto-20260717-r1/result.json),
coverage는
[`full-coverage-audit.json`](../build/qbox-apollo-qvp/pfdi-requester-context-yocto-20260717-r1/full-coverage-audit.json)에
있으며 둘 다 `passed: true`다. RSE, SI0, SI1과 Linux login marker가 확인됐고
SI1 PFDI 오류 gate 4종은 모두 `false`다.

## 7. 남은 fidelity 부채

1. SI0 CMN Cyprus node graph와 revision은 FVP r3p0 topology와 같지 않다.
2. PFDI peer-offline, SI0 reset 도중 cancellation과 fault injection 조합은 extended
   validation으로 남아 있다.
3. 이번 결과는 사용자 지정 비-AP 로그의 focused differential이다. AP 비교는
   의도적으로 제외했고 전체 동일-artifact 자동 FVP/QBox differential은 후속이다.
4. emulator 성능과 absolute timestamp는 acceptance 기준에 포함하지 않는다.

이번 범위의 RSE identification 차이와 SI1 PFDI timeout은 수정됐으며, 실제
SI0 firmware가 service owner인 구조를 유지한 채 local 및 Yocto 이미지에서
재현되지 않음을 확인했다.
