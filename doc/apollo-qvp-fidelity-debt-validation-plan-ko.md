# Apollo QVP 잔여 Fidelity 부채 검증 계획

- 상태: 구현 착수 전 검증 계약
- 기준일: 2026-07-16
- 대상: `apollo-qvp`, RD-Aspen CFG2, AP 4 CPU
- 상위 설계: [Fidelity 부채 아키텍처 설계](apollo-qvp-fidelity-debt-architecture-design-ko.md)
- 구현 계획: [Fidelity 부채 구현 계획](apollo-qvp-fidelity-debt-implementation-plan-ko.md)

## 1. 목적과 범위

이 문서는 잔여 fidelity 구현을 빠르게 통합하기 위한 최소 검증 gate와 evidence
형식을 고정한다. 각 구현 slice는 대표 정상 경로 하나와 대표 오류 경로 하나만
필수로 검증한다. 조합 행렬, 반복 stress와 soak는 extended validation으로
분리한다. emulator 성능 기준은 별도 acceptance로 추가하지 않는다.

이번 단계의 AP topology는 CPU0–CPU3, 총 4 CPU로 고정한다. 16 CPU enablement와
CPU4–CPU15 lifecycle은 후속 단계다. 다음 중 하나라도 관찰되면
이번 검증은 실패한다.

- runtime manifest의 resolved AP CPU 수가 4가 아님
- DT의 enabled CPU node와 GIC redistributor 수가 4 CPU 계약과 다름
- Linux에서 CPU4 이상이 online됨
- CPU4–CPU15에 대한 PSCI release 또는 interrupt delivery가 발생함
- 16 CPU 결과를 4 CPU acceptance에 혼합함

## 2. 검증 원칙

1. static, targeted unit, local full-system, Yocto 순서로 한 번씩 확대한다.
2. 변경한 data path마다 대표 allow 하나와 deny/fault 하나만 필수로 둔다.
3. deny/fault는 downstream side effect가 없어야 하며 다음 정상 request가 성공해야
   한다.
4. request identity는 ingress, policy, fault record와 guest log에서 동일해야 한다.
5. DMI 최적화, exhaustive negative matrix와 FVP 전체 differential은 후속이다.
6. 성능 수치는 합격 기준으로 사용하지 않는다. simulated/wall time은 hang 진단용
   telemetry로만 기록할 수 있다.
7. 실행 결과는 화면 출력이 아니라 result JSON과 UART log로 판정한다.

## 3. Evidence 계약

### 3.1 표준 경로

각 실행은 다음 root 아래에 독립 bundle을 만든다.

```text
build/qbox-apollo-qvp/fidelity-4cpu-<profile>-<timestamp>/
```

필수 파일은 다음과 같다.

| 파일 | 필수 내용 |
| --- | --- |
| `manifest.json` | source/submodule revision, command, backend, artifact path/hash와 resolved 4 CPU topology |
| `result.json` | gate별 pass/fail/skip, 최초 실패, 종료 사유와 핵심 milestone |
| `events.jsonl` | 변경한 request/fault 경로의 최소 event; 해당 경로가 있을 때만 필수 |
| `full-coverage-audit.json` | 기존 full-system coverage 결과 |
| `uart/` | RSE, SI CL0/CL1, TF-A, U-Boot/Linux domain별 원본 log |

`metrics.json`, exhaustive event trace와 전체 FVP comparison bundle은 선택
telemetry 또는 후속 산출물이다. `result.json`은 실행하지 않은 항목을 pass로
기록하지 않는다. `skip`에는 사유와 후속 검증 항목을 기록한다.

### 3.2 공통 식별자

`events.jsonl`의 관련 event는 다음 공통 키를 가진다.

- `run_id`, `sequence`, `sim_time_ns`, `wall_time_ns`
- `origin_id`, `domain_id`, `requester_id`, `substream_id`
- `access_path`, `secure`, `privileged`, `instruction`, `ats`
- `address`, `size`, `command`, `response`
- `policy_id`, `fault_id`, `irq_id`, `cpu_id`

주소나 SID가 보안상 가려져야 하는 외부 공유 bundle은 원본을 보존한 채 별도
redaction 사본을 만든다. 검증용 원본을 redaction 결과로 대체하지 않는다.

## 4. Gate와 실행 순서

### V0. Provenance와 4 CPU 정적 계약

검증 항목:

- active machine, variant, `TMPDIR`, image와 CPU 수가 build config와 일치함
- topology/DT/GIC/runtime bootargs가 4 CPU로 resolve됨
- CPU4–CPU15 enable 경로가 acceptance profile에서 비활성임
- address/route/ABI contract와 source ownership 경계가 유효함
- artifact 및 source revision을 hash로 고정함

현재 존재하는 명령:

```bash
python3 scripts/test/validate_qbox_apollo_fvp_full_map.py
python3 scripts/test/validate_qbox_apollo_topology.py \
  --emit build/qbox-apollo-qvp/topology/topology.json
python3 scripts/test/audit_qbox_core_boundary.py
git -C hsoc-stack/tools/qbox diff --check
git -C hsoc-stack/tools/qbox-platform diff --check
```

신규 예정 명령:

```bash
python3 scripts/test/validate_qbox_apollo_fidelity_contract.py \
  --cpus 4 --fail-on-enabled-cpu-above 3 \
  --output build/qbox-apollo-qvp/fidelity-contract-4cpu.json
```

통과 조건: 모든 정적 검사가 pass이고 manifest, DT와 bootargs의 resolved CPU가
모두 4다.

### V1. Request context와 NI-710AE APU

최소 시험은 다음 네 개다.

1. AP request 하나가 router와 APU까지 같은 origin/security/SID를 보존한다.
2. reset 상태에서 RSE 접근 하나는 성공하고 AP 접근 하나는 side effect 없이
   실패한다.
3. RSE programming 뒤 같은 AP 접근이 성공한다.
4. lock 뒤 APU policy write 하나가 거부된다.

debug/direct/reentrant/DMI는 해당 path를 실제로 변경한 commit에서만 대표 allow와
deny를 각각 하나 추가한다. 공식 NI-710AE APU programming model이 없으면 APU
register acceptance를 `blocked`로 기록하고 request-context 구현만 진행한다.

### V2. MMU-720AE와 SystemC SMMUv3 translation

최소 시험은 다음 세 개다.

1. 4 KiB stage-1 mapping 하나로 GPEX DMA read/write가 성공한다.
2. unmapped IOVA 하나가 target side effect 없이 EVTQ와 SMMU IRQ를 만든다.
3. CMDQ/TLBI 한 번 뒤 이전 translation이 재사용되지 않는다.

SID, IOVA와 access type은 DMA ingress, EVTQ와 guest log에서 같아야 한다.
two-level STE, stage-2, queue overflow, permission 조합과 translated DMI matrix는
extended validation으로 미룬다.

### V3. PCIe MSI, ITS와 LPI

test endpoint 하나를 연결하고 MSI-X 하나가 ITS를 거쳐 CPU0의 LPI counter를
증가시키는지 확인한다. 같은 endpoint의 legacy INTx 하나도 기존 SPI route가
회귀하지 않았는지만 확인한다. CPU별 affinity, invalid DeviceID/EventID와 ITS
invalidation matrix는 후속이다.

### V4. Debug, direct, reentrant, DMI와 오류 변환

| 원인 | TLM 결과 | QEMU 결과 | guest 관찰 |
| --- | --- | --- | --- |
| unmapped address | address error | `MemTxDecodeError` | abort 또는 bus error |
| APU deny | command/generic error | `MemTxError` | permission/bus error |
| SMMU translation fault | engine fault | `MemTxError` | EVTQ와 driver fault |
| powered-off/reset-held target | 문서상 DECERR/SLVERR | 대응 `MemTxResult` | 유한 시간 안의 오류 |

이 gate는 해당 access path를 변경했을 때만 실행한다. 변경한 path에서 허용 주소
하나와 차단 주소 하나를 실행하고, 차단이 `MemTxError` 또는
`MemTxDecodeError`로 유한 시간 안에 끝나는지만 확인한다. DMI를 새로 열지 않는
MVP에서는 DMI matrix를 실행하지 않는다.

### V5. Fault, safety, watchdog와 lifecycle

구현한 수직 slice마다 source register에서 한 번 inject하고 IRQ 또는 reset sink,
clear/ack와 다음 정상 상태까지 한 번 확인한다.

| slice | source | 필수 sink와 recovery |
| --- | --- | --- |
| APU violation | NI-710AE APU deny | error record, FMU, GIC, clear |
| SMMU fault | LTI00 translation/permission | EVTQ, SMMU IRQ, FMU 연계 |
| SI DCLS | test-only DCLS force | FMU, SSU state, firmware clear |
| AP watchdog | secure watchdog WS0/WS1 | GIC/RGM, AP CPU reset/복구 |
| reset/power access | RGM/PPU transition | 유한 오류, 상태 전이 후 정상 접근 |

MVP 첫 대상은 SMMU fault 수직 경로다. APU, DCLS와 watchdog은 구현되는 순서대로
같은 smoke 형식을 적용한다. mask 조합, severity 조합과 reset stress는 후속이다.

### V6. System software ABI 오류와 recovery

변경한 protocol마다 대표 malformed 또는 denied request 하나와 그 다음 정상
request 하나만 실행한다. 우선순위는 SCMI/PFDI, MHU, PSCI다. HIPC/RPMsg와 FF-A
전체 오류 matrix는 후속이다. 오류는 유한 시간 안에 끝나고 mailbox/channel을
BUSY 상태로 남기지 않아야 한다.

### V7. Local 4 CPU full-system

선행 조건은 변경한 slice의 V0–V6 smoke 통과다.

현재 존재하는 build와 runtime 명령:

```bash
./local_build.sh qbox --qbox-unit-tests

python3 scripts/run/run_qbox_apollo_fvp_full.py \
  --si-mode live-cl0-cl1 --timeout 600

python3 scripts/test/audit_qbox_apollo_fvp_full_coverage.py \
  --result-json <runtime-result.json> \
  --output <evidence-root>/full-coverage-audit.json
```

신규 예정 profile runner:

```bash
python3 scripts/run/run_qbox_apollo_fidelity.py \
  --artifacts local --cpus 4 --profile smoke \
  --out-dir build/qbox-apollo-qvp/fidelity-4cpu-local-<timestamp>
```

필수 milestone:

- RSE boot와 APU/ATU 설정
- SI CL0/CL1 boot, PFDI ready와 AP release
- TF-A, U-Boot, Linux login
- Linux online CPU 4와 CPU0–CPU3 interrupt delivery
- 변경한 GIC/ITS, SMMU 또는 PCIe 경로의 대표 marker

필수 횟수는 한 번이다. 실패하면 원인을 수정한 뒤 V7과 그 이후 gate를 다시
실행한다.

### V8. Yocto `nexios-image` 4 CPU full-system

현재 active config를 다시 확인한 뒤 다음을 실행한다.

```bash
./yocto_build.sh

python3 scripts/run/run_qbox_apollo_fidelity.py \
  --artifacts yocto --cpus 4 --profile smoke \
  --out-dir build/qbox-apollo-qvp/fidelity-4cpu-yocto-<timestamp>
```

두 번째 명령은 I7에서 구현할 신규 예정 interface다. runner는 실제 Yocto deploy
artifact를 선택하고 local artifact와 혼합하지 않아야 한다. Yocto build 한 번과
V7의 boot milestone 한 번이 통과하면 된다. targeted negative test는 V1–V6에서
이미 수행하므로 full-system에서 반복하지 않는다.

### V9. 후속 focused FVP comparison

FVP reference boot의 현재 명령:

```bash
python3 scripts/run/runfvp_log_boot.py \
  --machine apollo-fvp \
  --fvpconf build/local-apollo-fvp/deploy/apollo-fvp-local.fvpconf \
  --out-dir build/local-apollo-fvp/fvp-boot \
  --timeout 900 --require all --min-runtime 70 --no-login
```

신규 예정 비교 명령은 MVP 구현 완료 뒤 한 번 실행한다.

```bash
python3 scripts/test/compare_qbox_fvp_fidelity.py \
  --qbox-result <qbox-result.json> \
  --fvp-result <fvp-result.json> \
  --cpus 4 --output <evidence-root>/fvp-comparison.json
```

비교는 boot milestone과 이번 구현에서 바뀐 대표 기능 marker만 대상으로 한다.
전체 memory/IRQ/fault/ABI differential과 동일 hash 강제는 extended validation으로
남긴다. artifact hash가 다르면 결과에 기록하되 MVP 구현을 막지 않는다.

FVP가 physical instance 수를 4로 줄일 수 없으면 CPU0–CPU3만 비교하고 제약을
기록한다. FVP 실행 환경이나 injection interface가 없으면 `deferred`와 사유를
남길 수 있으며 V0–V8 MVP 판정을 막지 않는다.

차이는 다음 중 하나로 분류한다.

- `equivalent`: software-visible 결과와 side effect가 허용 오차 안에서 같음
- `intentional-abstraction`: cycle/timing 등 명시적 비목표 차이
- `partial-model`: 알려진 기능 일부가 없고 영향/대체 계획이 있음
- `blocker`: 비교를 수행한 범위에서 boot, 보안, 데이터 무결성 또는 recovery 불일치

## 5. 최소 실행 횟수와 비필수 검증

| 검증 | 최소 처리 |
| --- | ---: |
| static/targeted unit | 변경 뒤 각 1회 |
| 대표 allow와 deny/fault | 변경한 slice별 각 1회 |
| local QBox build와 full-system smoke | 각 1회 |
| Yocto build와 full-system smoke | 각 1회 |
| focused FVP comparison | MVP 뒤 1회 권장, 환경이 없으면 `deferred` |

성능 budget과 RSS 합격 기준은 두지 않는다. 반복 stress, soak, fault 조합 matrix와
전체 FVP differential은 MVP 완료 조건이 아니다. wall time과 simulated time은 hang
여부를 판단하는 데만 사용한다. 실패가 발생하면 실패 evidence를 보존하고 수정 뒤
해당 gate와 downstream smoke만 다시 실행한다.

## 6. 단계별 승격 조건

| 다음 단계 | 필수 선행 결과 |
| --- | --- |
| I1/I2 integration | V0와 request-context unit pass |
| I3 Apollo binding | generic SMMUv3 qualification pass |
| I4 MSI profile | mapped GPEX DMA와 SMMU fault pass |
| I5 fault 연결 | event schema와 source/mask/clear unit pass |
| I6 ABI 오류 | bounded timeout과 mailbox recovery unit pass |
| V7 local full-system | V0–V6 targeted profile pass |
| V8 Yocto | local smoke 1회와 동일 source revision |
| V9 FVP 비교 | V0–V8 완료 뒤 가능한 범위의 focused comparison |

선행 결과가 `blocked` 또는 `skip`이면 다음 단계를 pass로 승격하지 않는다.

## 7. 실패 분류와 triage

1. `configuration`: CPU/DT/artifact/backend가 요구와 다름
2. `build`: compile, link, packaging 또는 provider 오류
3. `model-contract`: address, request context, policy나 route 불일치
4. `runtime-liveness`: simulated time, QEMU thread, WFI 또는 timeout 교착
5. `functional`: data, IRQ, fault, reset 또는 ABI 결과 불일치
6. `reference-gap`: FVP 제약, 문서 부족 또는 같은 artifact 실행 불가

runtime 실패는 최초 실패 domain과 event sequence를 먼저 확인한다. log로 원인
component를 좁힌 뒤에만 GDB/FVP Iris로 확대한다. evidence가 없는 화면 관찰은
판정 근거로 사용하지 않는다.

## 8. 최종 완료 체크리스트

- [ ] V0의 active 4 CPU contract와 provenance가 통과한다.
- [ ] request context 대표 경로가 target과 fault record까지 보존된다.
- [ ] NI-710AE APU가 공식 reset/program/lock semantics로 data path를 제어한다.
- [ ] MMU-720AE SystemC backend가 실제 STE/CD/page walk와 EVTQ를 수행한다.
- [ ] GPEX DMA와 MSI가 SID/SSID를 보존해 ITS/LPI까지 도달한다.
- [ ] 변경한 debug/direct/reentrant path의 대표 allow/deny가 통과한다.
- [ ] 구현한 fault slice의 source-to-sink와 clear/recovery가 한 번 통과한다.
- [ ] 변경한 software ABI의 대표 오류 뒤 정상 request가 성공한다.
- [ ] local build/boot와 Yocto build/boot가 각각 한 번 통과한다.
- [ ] focused FVP comparison을 수행하거나 `deferred` 사유를 기록한다.
- [ ] 모든 gap은 owner, 영향, 근거, 상태와 후속 완료 조건을 가진다.
- [ ] CPU4–CPU15, 성능 budget, stress와 soak가 MVP 완료 판정에 포함되지 않는다.
