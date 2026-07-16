# Apollo QVP 아키텍처 부채 구현·검증 계획

- 기준일: 2026-07-15, 완료일 2026-07-16
- 입력: 잔여 부채 설계 및 4관점 아키텍처 리뷰
- 원칙: test first, 좁은 검증부터 local/Yocto runtime으로 확장
- 상태: P1–P10 구현 및 검증 완료

## 1. 성공 조건

1. broad 1:1 bridge 3개가 source와 생성 topology에서 사라진다.
2. SMD runtime router와 실제 SI/AP/SMDEXP ATU 경로가 elaboration된다.
3. GPEX DMA가 선택한 SMMU backend의 올바른 requester 경로를 통과한다.
4. reset-state 및 미매핑 접근이 normal/debug/DMI에서 차단된다.
5. local QBox build와 local image full-system boot가 성공한다.
6. Yocto `nexios-image` build와 그 image를 사용한 QBox boot가 성공한다.
7. 검증 결과와 잔여 기능 충실도 부채가 재현 가능한 파일로 남는다.
8. local guest의 `maxcpus`가 resolved AP topology와 일치한다.
9. SMD가 초기화한 AP/SI SCMI mailbox가 AP reset 뒤에도 보존되고 Linux SCMI
   v2.0 probe가 FVP와 같은 marker로 성공한다.
10. SI CL1/AP의 secure request가 SI0 transport init보다 먼저 도착해도 유효한
    pending mailbox가 보존되고 trace-off 반복 부팅에서 PFDI가 준비된다.

## 2. 구현 단계

### P1. 계약 및 음성 테스트를 먼저 실패시킨다

- `tests/test_validate_qbox_apollo_topology.py`
  - phase `A4_policy_routing`
  - `forbid_broad_passthrough=true`
  - compatibility debt empty
  - broad bridge source 부재
  - SMD/ATU/SMMU wiring source 존재
- `rse_atu-tests`
  - reset 상태 normal/debug/DMI default-deny
  - region 경계 초과와 disabled region 유지
- 변경 전 targeted test를 실행해 의도한 red를 기록한다.

### P2. fabric/SMD 구조를 전환한다

- `fabric.lua`: `smd_router`, `system_to_smd_nci`
- `system_mgmt.lua`: SMD canonical target rebind, SMDEXP SRAM 추가
- `topology.lua`, `transaction_routes.lua`, `address_map.lua`: runtime과 contract 정렬
- SMD prefix 내부 미매핑 주소는 `smd_router`에서 종료한다.

### P3. AP/SI policy route를 전환한다

- `ap_compute.lua`
  - `ap_system_bridge` 제거
  - AP ATU만 cross-domain path로 유지
  - AP FMU fixed alias와 canonical target 정렬
- `si_cl0.lua`
  - broad bridge와 ATU-check placeholder 제거
  - SI/SMDEXP ATU translation socket 연결
  - translated peripheral을 firmware physical 주소로 이동
  - AP shared/GIC narrow bridge 추가
- `si_cl1.lua`
  - broad bridge 제거
  - SCMI/HIPC static path 유지

### P4. GPEX/SMMU 경로를 전환한다

- SystemC backend:
  `qemu_gpex.bus_master -> mmu720ae.tbu_lti00 -> ap_router`
- QEMU backend:
  QEMU-owned `arm_smmuv3`/GPEX 관계 유지, output만 AP view로 연결
- TBU 기본 SID, explicit SID extension 우선, fault event SID 시험을 유지한다.

### P5. 문서와 contract를 동기화한다

- `doc/apollo-qvp-machine-architecture-ko.md`
- `doc/apollo-qvp-machine-improvement-plan-ko.md`
- `doc/qbox-fvp-emulation-project.md`
- `hsoc-stack/tools/qbox-platform/platforms/apollo/README.md`
- 생성 topology JSON과 문서의 phase/잔여 부채를 일치시킨다.

### P6. 검증한다

#### 정적/단위

```bash
python3 -m pytest -q tests/test_validate_qbox_apollo_topology.py
python3 scripts/test/validate_qbox_apollo_fvp_full_map.py
python3 scripts/test/audit_qbox_core_boundary.py
git -C hsoc-stack/tools/qbox-platform diff --check
```

QBox component build tree에서 `rse_atu-tests`, `mmu720ae-*`와
`platforms-vp`를 실행한다.

#### local build/runtime

```bash
./local_build.sh qbox
python3 scripts/run/run_qbox_apollo_fvp_full.py \
  --si-mode live-cl0-cl1 --timeout 600
python3 scripts/test/audit_qbox_apollo_fvp_full_coverage.py \
  --result-json <result.json> \
  --output build/qbox-apollo-fvp/full-coverage-audit.json
```

#### Yocto build/runtime

빌드 전 `build/conf/local.conf`, `bblayers.conf`, `templateconf.cfg`를 다시
확인한다.

```bash
./yocto_build.sh
python3 scripts/run/run_qbox_apollo_fvp_full.py \
  --si-mode live-cl0-cl1 --timeout 600 \
  <Yocto deploy artifact 선택 옵션>
```

runner의 실제 CLI를 `--help`로 확인한 뒤 Yocto artifact override를 적용한다.

#### FVP 비교

동일 firmware/image hash를 사용할 수 있을 때 비대화형 FVP boot를 실행하고
RSE/SI/AP boot marker, ATU programming, memory/IRQ/DT를 비교한다. FVP binary,
license 또는 artifact가 없으면 그 사실과 사전 조건을 blocker로 기록한다.

### P7. 반복 부팅에서 발견한 QEMU/SystemC lifecycle 교착을 닫는다

- 변경 전 local full-system을 반복해 5회 중 2회 simulated-time 정지를
  재현한다.
- host GDB로 SystemC suspend owner와 reset-held vCPU 상태를 함께 기록한다.
- reset-held CPU가 quantum keeper를 시작하지 않도록 하고, target-vCPU의
  tracked async reset release가 완료된 뒤 runnable 상태로 전환한다.
- start-in-reset release test를 50회 반복한다.
- 수정 후 local image 5회, Yocto image 3회와 각 coverage audit를 연속
  통과시킨다.

### P8. 구현 후 코드·runtime 리뷰 지적을 닫는다

- full-system runner가 lower-level rootfs patcher에 resolved AP CPU 수를
  `--rootfs-maxcpus`로 전달한다.
- 기본 4 CPU와 `QBOX_APOLLO_NUM_CPUS=8` override를 unit test로 고정한다.
- 제거한 broad bridge와 `*_atu_check_*` placeholder의 shadow warning은 더 이상
  허용 목록에 두지 않고 runtime failure로 처리한다.
- local image로 Linux가 정확히 4 CPU를 online하고 CPU4–15 PSCI failure가 없는
  acceptance boot 및 coverage audit를 수행한다.

### P9. SMD-owned SCMI mailbox reset ownership을 정렬한다

- 수정 전 Linux `shmem_tx_prepare` warning과 SCMI response timeout을 기록한다.
- SI ATU trace로 region 14의 `0xe01b_0000 -> 0x0018_0000` translation이
  성공함을 확인해 routing과 reset 문제를 분리한다.
- `host_ap_mhu_ns_shared_sram`을 AP reset fan-out에서 제외하고 address/software
  contract에 `owner=smd`, `reset_policy=preserve_on_ap_reset`을 기록한다.
- post-fix local boot에서 Linux SCMI v2.0 marker, login, 49/49 coverage를
  확인하고 기존 FVP Linux log의 동일 protocol/firmware marker와 대조한다.

### P10. SI0 secure transport startup race를 닫는다

- 새 Yocto image를 trace 없이 실행해 SI CL1의 첫 PFDI `PROTOCOL_VERSION`
  timeout을 보존한다.
- 동일 image의 `--live-trace` 통과와 1 ms global quantum의 비결정적 결과를
  비교해 trace/quantum을 근본 원인에서 배제한다.
- SI0 transport channel별 init policy를 대조해 RSE SCMI만 pending mailbox를
  보존하고 AP/CL1 PFDI 공통 secure channel은 보존하지 않는 차이를 확인한다.
- `TRANSPORT_CH_SEC_MBX_INIT`에
  `MOD_TRANSPORT_POLICY_PRESERVE_PENDING_MAILBOX`를 적용하고 RSE 전용 중복 flag를
  제거한다.
- source topology test로 AP/CL1 PFDI가 공통 secure policy를 사용하는지 고정하고
  SCP 전체 module unit, local SCP build, local full-system 3회, 새 Yocto build와
  full-system 3회 및 각 coverage audit를 통과시킨다.

## 3. 실패 시 triage 순서

1. topology validator 및 Lua elaboration
2. RSE UART에서 ATU programming/read-back
3. SI CL0 UART에서 최초 실패 physical target
4. AP TF-A/U-Boot/Linux handoff
5. SMMU EVTQ/IRQ와 GPEX DMA
6. 필요한 경우에만 symbols manifest와 GDB/Iris 사용

## 4. 완료 산출물

- 구현 diff와 unit/static 결과
- local/Yocto runtime의 timestamped result JSON과 UART log
- coverage audit JSON
- `doc/apollo-qvp-architecture-debt-validation-2026-07-16.md`
- 기능 충실도 잔여 항목과 후속 gate

## 5. 완료 결과

| 단계 | 결과 | 핵심 증거 |
| --- | --- | --- |
| P1 | 완료 | phase/debt/broad bridge 음성 검사와 ATU reset default-deny test |
| P2 | 완료 | `smd_router`, `system_to_smd_nci`, canonical SMD target |
| P3 | 완료 | AP/SI broad bridge 제거, SI/AP/SMDEXP ATU 및 static HIPC/SCMI route |
| P4 | 완료 | GPEX→MMU-720AE LTI00와 backend 상호 배타 wiring |
| P5 | 완료 | architecture, plan, project roadmap와 Apollo README 동기화 |
| P6 | 완료 | QBox component 33/33, local 5/5, Yocto 3/3, coverage 8/8 |
| P7 | 완료 | reset release 50/50, reset-held QK suspend-owner 교착 미재현 |
| P8 | 완료 | resolved 4-CPU `maxcpus`, stale shadow-warning 실패 처리, local acceptance/coverage 통과 |
| P9 | 완료 | SMD-owned SCMI SRAM AP-reset 보존, QVP/FVP SCMI v2.0 focused differential 통과 |
| P10 | 완료 | secure pending mailbox 공통 보존, SCP module 77/77, trace-off local/Yocto 각 3/3과 49/49 coverage |

최종 `./yocto_build.sh`는 7,290 task 중 7,259 task를 재사용하고 전체 성공했다.
Yocto runtime은 native provider와 `nexios-image` WIC를 명시적으로 주입했다.
post-review local acceptance 두 번과 pending-mailbox 수정 후 local/Yocto 각 3회도
full boot 및 49/49 coverage를 통과했다.
기존 FVP log와 secondary SCMI protocol marker는 일치했지만 동일 artifact 전체
FVP differential은 이번 완료 범위에서 실행하지 않았으므로 G7은 열린 상태다.
상세 command, 입력 경로, timing과 blocker 분류는
[2026-07-16 구현·검증 보고서](apollo-qvp-architecture-debt-validation-2026-07-16.md)를
기준으로 한다.
