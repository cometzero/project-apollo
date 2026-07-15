# Apollo QVP Machine 구현·검증 보고서

작성일: 2026-07-15

대상: `apollo-qvp`, RD-Aspen CFG2, AP 4 CPU, live SI CL0/CL1

연계 문서:

- [Machine Architecture](apollo-qvp-machine-architecture-ko.md)
- [Machine Architecture 개선 계획](apollo-qvp-machine-improvement-plan-ko.md)

## 1. 판정

계획의 A0/A1 기반과 A2/A3 address-view 전환을 구현했고, local source image와
Yocto `nexios-image` 두 경로에서 full-system boot를 검증했다. 두 실행 모두
RSE, live SI CL0, 4-core SI CL1, 4-core AP firmware와 Linux login까지
`passed: true`로 종료됐으며 coverage audit도 통과했다.

현재 상태는 `A3_local_view_isolation`이다. AP와 SI local view는 실제 runtime
router로 분리됐지만 A4 정책 전환 전의 broad system compatibility bridge 세 개가
남아 있다. 따라서 SMD runtime view, APU/ATU reset default-deny, requester/StreamID,
negative access, 전체 IRQ/fault/ABI error path와 FVP differential은 완료로
판정하지 않는다.

## 2. 구현 내용

### 2.1 Machine contract와 정적 evidence

`hsoc-stack/tools/qbox-platform/platforms/apollo/hw-block/`에 다음 single-source
Lua contract와 loader/exporter를 추가했다.

| 파일 | 역할 |
| --- | --- |
| `topology.lua` | domain, 52/40/32-bit view, router, bridge, QEMU instance와 migration debt |
| `address_map.lua` | range, backing/view, owner, access와 scope |
| `transaction_routes.lua` | initiator, domain/requester/StreamID, bridge와 response contract |
| `signal_routes.lua` | IRQ, reset, power와 fault source-to-sink contract |
| `boot_control.lua` | RSE/SI/AP boot owner, dependency, read-back와 release 순서 |
| `software_contract.lua` | DT, SCMI/PSCI/MHU/PFDI/HIPC/FF-A/RAS ABI |
| `machine_contract.lua` | contract 적재, 참조 검증과 정렬된 JSON encoding |
| `export_machine_contract.lua` | validator가 사용하는 JSON exporter |

`scripts/test/validate_qbox_apollo_topology.py`는 contract에서 다음 9개 파일을
`build/qbox-apollo-qvp/topology/`에 생성한다.

```text
topology.json
address-routes.json
transaction-routes.json
irq-routes.json
reset-routes.json
boot-routes.json
software-routes.json
artifacts.json
validation.json
```

검사는 schema/reference, view width, range overflow/overlap, backing identity,
cross-domain bridge, transaction route, signal endpoint, boot dependency와 software
ABI 참조를 포함한다.

### 2.2 Runtime router 전환

- root `host_router`를 52-bit `system_router`로 변경했다.
- AP CPU/GPEX/loader/target을 52-bit `ap_router`에 연결했다.
- SI CL0 CPU/loader/local target을 40-bit `si_cl0_router`에 연결했다.
- SI CL1 CPU/loader/local target을 40-bit `si_cl1_router`에 연결했다.
- RSE는 기존 32-bit `rse_router`와 ATU 경로를 유지했다.
- AP↔SI HIPC 512 KiB view와 SI CL0→SI CL1 SCMI 4 KiB view를 explicit
  `addrtr` bridge로 연결했다.
- live CL0 조립 시 다른 block의 decode priority를 일괄 변경하던 경로를
  제거했다.
- full-system AP CPU 기본값을 active Yocto와 같은 4로 변경했다.

아래 broad bridge는 A4 전환 부채다. local target보다 낮은 priority 100을
사용하며 contract에서 허용 목록으로 관리한다.

```text
ap_system_bridge_1_to_1
si_cl0_system_bridge_1_to_1
si_cl1_system_bridge_1_to_1
```

### 2.3 QBox `addrtr` DMI 수정

SI local router 전환 중 source address가 downstream의 더 낮은 주소로 변환될 때
DMI end-range 판정이 변환된 start를 다시 사용해 abort하는 결함을 재현했다.
`addrtr.h`가 원래 mapped start를 보존해 end를 비교·보고하도록 수정했고,
source `0x1000` → mapped `0x100` 및 invalidate 역변환을 component test에
추가했다.

### 2.4 Runner와 audit 정합

- full-system local build와 output 기본값을 `local-apollo-qvp` 및
  `build/qbox-apollo-qvp/`로 정렬했다.
- full-system AP CPU 기본값과 login prompt를 4 및 `apollo-qvp login:`으로
  정렬했다.
- 새 AP/SI migration bridge만 예상 shadow range로 허용하고 그 밖의 shadow는
  계속 실패 처리한다.
- installed libqemu뿐 아니라 libjpeg/libslirp가 있는 Yocto native sysroot를
  loader search path에 포함했다.
- AP memory-map audit를 `ap_router`와 단일 Arm MMIO generic timer의 secure/NS
  frame 구조에 맞췄다.
- headless Yocto 검증은 guest UART에 명령을 주입하지 않으므로 login prompt 또는
  root shell 중 하나를 Linux 완료 조건으로 사용한다.

## 3. Local build 및 검증

### 3.1 정적·단위 검증

실행 명령과 결과:

```text
python3 scripts/test/validate_qbox_apollo_fvp_full_map.py
  -> passed: true

python3 scripts/test/validate_qbox_apollo_topology.py
  -> build/qbox-apollo-qvp/topology/validation.json: status=pass

python3 scripts/test/audit_qbox_core_boundary.py
  -> QBox core boundary audit passed

ctest --test-dir build/qbox-core-tests -R '^addrtr-tests$'
  -> 1/1 passed

pytest -q tests/test_run_qbox_apollo_fvp_full.py \
  tests/test_run_qbox_fvp_rd_aspen_rse.py \
  tests/test_validate_qbox_apollo_topology.py
  -> 44 passed

./local_build.sh qbox --qbox-unit-tests --no-package --jobs 6
  -> QBox/QBox-platform build passed
  -> SystemC component tests 33/33 passed
```

### 3.2 전체 local source build

```text
./local_build.sh --jobs 6
```

TF-M, SCP-firmware, SI CL1 Zephyr, OP-TEE, U-Boot, TF-A, Linux, Buildroot,
boot media와 debug manifest 생성이 모두 성공했다. 단계별 timing evidence는
`build/local-apollo-qvp/logs/local-build-timings.tsv`에 있다.

### 3.3 Local full-system runtime

최종 evidence root:

```text
build/qbox-apollo-qvp/local-20260715-1540/
```

주요 결과:

| 증거 | 판정 |
| --- | --- |
| `result.json` | `passed=true`, `verdict=pass`, `blocker=null` |
| safety mode | `live-cl0-cl1` |
| AP/CL1 QEMU | `MULTI`, CL1 `multithread-quantum` |
| AP firmware | BL2, BL31, OP-TEE, U-Boot marker 모두 true |
| RSE/SCP | BL1_1, image slot, SCMI handoff/notification marker 모두 true |
| SI CL0 | live SCP, module init, GIC multiview marker 모두 true |
| SI CL1 | Zephyr, 4-core release, PFDI와 network marker 모두 true |
| Linux | `apollo-qvp login:`과 root shell marker true |
| coverage | `full-coverage-audit.json`의 `passed=true` |

AP 9.1.1 map audit도
`build/qbox-apollo-qvp/ap-map-9-1-1/ap-map-audit.json`에서 통과했다.

## 4. Yocto `nexios-image` build 및 검증

### 4.1 Active configuration 확인

build 전 다음 값을 다시 확인했다.

| 항목 | 값 |
| --- | --- |
| `MACHINE` | `apollo-qvp` |
| `RD_ASPEN_VARIANT` | `cfg2` |
| `PC_CPUS_COUNT_DEFAULT` | `4` |
| image | `nexios-image` |
| `TMPDIR` | `build/tmp_baremetal` |
| template | `hsoc-stack/yocto/meta-hsoc-auto-solutions/conf/templates/apollo-qvp/` |

### 4.2 Image build

```text
./yocto_build.sh --machine apollo-qvp --keep-conf
  -> 7,290 tasks attempted
  -> 7,250 tasks restored from cache
  -> all tasks succeeded
```

QBox native recipe의 compile/check/install을 포함해 image가 성공했다. BitBake는
19개 taint warning을 보고했지만 task failure는 없었다.

사용한 WIC:

```text
build/tmp_baremetal/deploy/images/apollo-qvp/
  nexios-image-apollo-qvp-20260715064611.wic
size: 22,285,403,136 bytes
```

### 4.3 Yocto image runtime

```text
./run_qbox_yocto.sh --headless --exit-after-pass --copy-disks \
  --timeout 900 \
  --out-dir build/qbox-apollo-qvp/yocto-20260715-1550
  -> exit 0
```

주요 결과:

| 증거 | 판정 |
| --- | --- |
| `result.json` | `passed=true`, `verdict=pass`, `blocker=null` |
| RSE/SI/AP markers | local run과 같은 boot/handoff marker group 통과 |
| Linux | `apollo-qvp login:` true, headless이므로 root shell 주입 안 함 |
| coverage | `full-coverage-audit.json`의 `passed=true`, Linux는 `pass:headless_login` |

## 5. 검증 중 발견하고 수정한 문제

| 문제 | 원인 | 수정 및 회귀 방지 |
| --- | --- | --- |
| QBox 시작 전 generic CCI 오류 | installed libqemu와 libjpeg/libslirp dependency가 loader path에 없음 | local/Yocto native lib path를 계산하고 runner test 추가 |
| SI router 전환 시 `addrtr` abort | descending DMI range의 start/end 좌표계를 혼용 | QBox core 수정 및 component regression 추가 |
| SI local map에서 기존 system target 접근 실패 | A4 ATU/APU window가 아직 없음 | A3에서 명명된 40-bit low-priority compatibility bridge 사용 |
| SI CL0의 CL1 SCMI access 실패 | `0x48000000` cross-view route가 없음 | CL0→CL1 4 KiB explicit SCMI bridge 추가 |
| 정상 boot 후 runner가 shadow range 실패 판정 | 새 migration bridge가 예상 목록에 없음 | 세 bridge만 명시적으로 허용하고 나머지는 계속 실패 |
| AP map audit 실패 | 이전 AP router 이름과 timer placeholder 구조를 가정 | `ap_router`와 combined MMIO timer frame 기준으로 수정 |
| Yocto login 판정 실패 | `apollo-fvp` prompt와 root-shell 주입을 가정 | `apollo-qvp login:` 및 headless login-or-shell contract로 수정 |

## 6. 남은 fidelity gap

1. `smd_router`는 contract-only이고 SMD target은 아직 `system_router`에 있다.
2. AP/SI broad 1:1 bridge 세 개를 A4의 명시적 RSE-owned ATU/APU window와
   reset default-deny로 교체해야 한다.
3. CPU/GPEX requester, domain, StreamID와 SMMU/APU fault syndrome을 실제 TLM
   payload에서 end-to-end 보존해야 한다.
4. `transport_dbg`, direct/reentrant access와 DMI의 trusted capability, deny와
   invalidation 정책은 G1/G2/G3 negative test가 필요하다.
5. IRQ/reset/power/FMU/SSU/RAS signal contract는 선언됐지만 전체 injection 및
   lifecycle test가 필요하다.
6. SCMI/PSCI/MHU/PFDI/HIPC/FF-A/DT contract의 malformed, denied, peer-offline,
   timeout 및 recovery path는 미검증이다.
7. 16-core full-system, performance budget과 동일 hash artifact 기반 FVP/QVP
   differential G7은 이번 범위에서 실행하지 않았다.

따라서 이번 결과는 정상 boot와 A2/A3 router 전환의 회귀 안전성을 증명하지만,
Arm Zena CSS/FVP 전체 functional equivalence 또는 safety validation 완료를
의미하지 않는다.
