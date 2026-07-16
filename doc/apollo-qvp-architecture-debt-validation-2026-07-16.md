# Apollo QVP 잔여 아키텍처 부채 구현·검증 보고서

- 작성일: 2026-07-16
- 대상: `apollo-qvp`, RD-Aspen CFG2, AP 4 CPU, live SI CL0/CL1
- 결론: A4 구조적 policy-routing 부채 폐쇄 및 반복 부팅 검증 통과

연계 문서:

- [Machine Architecture](apollo-qvp-machine-architecture-ko.md)
- [Machine Architecture 개선 계획](apollo-qvp-machine-improvement-plan-ko.md)
- [잔여 아키텍처 부채 설계](apollo-qvp-remaining-architecture-debt-design-ko.md)
- [아키텍처 리뷰](apollo-qvp-remaining-architecture-review-2026-07-15.md)
- [구현·검증 계획](apollo-qvp-architecture-debt-implementation-plan-ko.md)

## 1. 최종 판정

`A4_policy_routing` 구조 전환을 완료했다. runtime topology에 `smd_router`와
`system_to_smd_nci`를 생성하고, AP/SI CL0/SI CL1의 broad 1:1 system bridge
세 개를 제거했다. AP/SI/SMDEXP ATU translation socket, canonical backing,
GPEX→MMU-720AE LTI00 TBU 경로를 실제 graph에 연결했다. 생성 contract의
`forbid_broad_passthrough`는 `true`, `compatibility_debt`는 빈 목록이다.

검증 중 간헐적으로 전체 simulated time이 정지하는 별도 lifecycle 결함을
재현했다. reset-held AP CPU2의 timehandler가 SystemC global suspend owner가 된
상태에서 guest가 이를 해제할 수 없었던 것이 원인이었다. reset-held CPU는
quantum keeper에 참여하지 않고 reset release가 완료될 때만 다시 시작하도록
QBox CPU lifecycle을 수정했다. 수정 후 기준 반복은 local source image 5회와
Yocto image 3회, 총 8회 연속 full-system boot 및 각 49항목 coverage audit가
모두 통과했다. 구현 후 리뷰 지적을 반영한 `maxcpus` 정합과 SMD-owned SCMI
mailbox reset ownership acceptance도 local image로 각각 추가 통과했다. 최종
Yocto 재검증에서 확인한 SI CL1 PFDI startup race는 공통 secure transport가
유효한 pending mailbox를 보존하도록 수정했다. 수정 뒤 trace-off local/Yocto
image를 각각 3회 실행했고 6회 모두 full boot와 49/49 coverage를 통과했다.

이 판정은 구조적 address-policy 경계와 정상 boot 회귀 안전성에 대한 것이다.
완전한 NI-710AE APU 권한표, MMU-720AE page-table walk, MSI→ITS→LPI, 모든
fault/timeout ABI 및 동일 artifact FVP differential은 잔여 기능 충실도 부채다.

## 2. 구현 범위

### 2.1 QBox/SystemC 및 machine topology

- 52-bit `system_router` 아래 SMD high-nibble decode 전용 `smd_router`를 구성했다.
- AP/SI CL0/SI CL1 broad system bridge와 SI ATU probe용 `gs_memory` placeholder를
  제거했다.
- AP/SI/SMDEXP ATU를 firmware가 programming하는 실제 transaction 경로에
  연결하고 reset-state default-deny를 normal/debug/DMI test로 고정했다.
- AP shared SRAM, GIC, HIPC, CSS timer, SMCF 및 NI-710AE 관련 target을 하나의
  canonical owner에 두고 다른 view는 ATU 또는 좁은 static window로 연결했다.
- AP 주소 view의 non-secure MHU SRAM은 lifecycle owner를 SMD로 명시하고
  `preserve_on_ap_reset` 정책으로 AP reset fan-out에서 제외했다.
- GPEX SystemC backend DMA를 `ap_smmu_0.tbu_lti00_socket`으로 연결했다.
- GIC multi-view의 allocated frame tail, 비활성 redistributor aperture,
  PPU reset/power sequence, MHU combined IRQ와 directional doorbell pair를
  component test로 보강했다.

### 2.2 System software

- SCP-firmware AArch64 FIQ save/restore가 기존 DAIF 상태를 보존하도록 수정했다.
- SI0 transport consumer 초기화 뒤 MHU를 시작하고, 먼저 도착한 유효 secure
  mailbox request를 completer 초기화가 지우지 않도록 transport core policy와
  unit test를 추가했다.
- RSE SCMI channel에만 적용돼 있던 pending-mailbox 보존 flag를 AP PFDI,
  SI CL1 PFDI, PSCI를 포함한 공통 secure init policy로 승격했다.
- TF-M BL2가 지연된 SI0 SCMI 응답을 bounded polling하고 protocol-version retry를
  늘려 QBox의 실제 동시 실행 순서를 허용했다.
- AP/SI MHU 방향, interrupt ID와 PFDI reply frame을 firmware-visible map에 맞췄다.
- full-system local rootfs patch가 resolved AP CPU 수를 `maxcpus=`에 반영하도록
  해 active 4-CPU topology와 guest online CPU 수를 일치시켰다.

### 2.3 QEMU 및 CPU lifecycle

- target-vCPU exclusive context에서 reset release 시 이미 소비된 wakeup 뒤에
  stale `exit_request`가 남지 않도록 libqemu CPU wrapper를 수정했다.
- reset signal이 simulation start 전에 들어오는 경우를 보존하고, managed reset
  release를 target vCPU의 tracked async job으로 완료한 뒤 SystemC가 진행하도록
  했다.
- reset-held CPU는 quantum keeper를 시작하거나 global suspend owner가 되지
  않는다. release 시 time sync와 wake 상태를 재설정한다.
- QEMU GPIO write는 BQL 아래 수행하고 Cortex-R82의 IRQ/FIQ/VIRQ/VFIQ 이벤트를
  외부 wake 조건에 포함했다.

## 3. 간헐 결함 진단 근거

### 3.1 reset-held CPU quantum keeper 교착

수정 전 동일 local runtime 5회 반복 결과는 3회 통과, 2회 blocked였다.

```text
build/qbox-apollo-fvp/architecture-debt-baseline-repeat2-r1-20260716  pass
build/qbox-apollo-fvp/architecture-debt-baseline-repeat2-r2-20260716  pass
build/qbox-apollo-fvp/architecture-debt-baseline-repeat2-r3-20260716  pass
build/qbox-apollo-fvp/architecture-debt-baseline-repeat2-r4-20260716  blocked
build/qbox-apollo-fvp/architecture-debt-baseline-repeat2-r5-20260716  blocked
```

blocked 실행은 SI0 UART가 시작되지 않고 SystemC time이 0에서 진행하지 않았다.
host GDB로 supervisor 아래 `platforms-vp`를 attach한 evidence는 다음 상태를
기록했다.

```text
architecture-debt-parent-attach-v13-20260716:
  m_suspend = 1, m_unsuspendable = 0
  AP CPU2: QemuCpu::wait_for_work

architecture-debt-parent-attach-v19-20260716:
  SUSPEND_OWNER = platform.ap_cpu_2.timehandler
  unsuspendable = false
```

AP CPU2는 reset-held 상태라 guest time을 소비할 수 없었지만 quantum keeper는
global suspend에 참여했다. 따라서 generic quantum policy를 약화하지 않고
reset-held CPU의 QK 참여만 차단하는 수정으로 범위를 제한했다.

### 3.2 SI CL1 PFDI startup race

최종 Yocto image의 trace-off 실행
`architecture-debt-final-yocto-r4b-20260716`에서 AP/SI0/RSE/Linux login과
SCMI v2.0은 정상인데 SI CL1의 첫 PFDI `PROTOCOL_VERSION`만 timeout했다. 같은
image에 `--live-trace`를 추가한
`architecture-debt-final-yocto-pfdi-trace-r1-20260716`은 통과해 scheduling에
민감한 startup race임을 확인했다.

global quantum을 1 ms로 낮춘 첫 실행은 통과했지만
`architecture-debt-final-yocto-quantum-contract-r2-20260716`은 동일 timeout으로
실패했다. 따라서 quantum 변경은 증상 노출 확률만 바꾸며 lifecycle contract의
해결책이 아니다.

source 대조 결과 RSE→SI0 SCMI channel에는
`MOD_TRANSPORT_POLICY_PRESERVE_PENDING_MAILBOX`가 있었지만, CL1→SI0와
AP→SI0 PFDI가 공유하는 `TRANSPORT_CH_SEC_MBX_INIT`에는 없었다. CL1이 SI0
transport init보다 먼저 BUSY/status와 payload를 게시하면 init이 mailbox를
FREE로 덮어썼고, doorbell만 남아 응답할 request가 사라졌다. 공통 secure init
policy가 유효한 pending request를 보존하도록 수정해 requester가 게시한
message를 SI0가 소비할 때까지 유지했다.

## 4. 정적·단위·빌드 검증

### 4.1 QBox CPU reset 회귀

```text
cmake --build build/qbox-core-tests \
  --target aarch64-start-in-reset-release-test --parallel 8
  -> succeeded

LD_LIBRARY_PATH=<Yocto native provider paths> \
ctest --test-dir build/qbox-core-tests \
  -R '^aarch64-start-in-reset-release-test$' \
  --repeat until-fail:50 --output-on-failure
  -> 50/50 passed
```

test 자체도 네 CPU를 8회 assert/release해 각 release 뒤 guest write가 정확히 한
번씩 진행하는지 검사한다.

### 4.2 QBox overlay build와 component test

```text
./local_build.sh qbox --qbox-unit-tests
  -> QBox/QBox-platform build succeeded
  -> component tests 33/33 passed
```

증거:

- `build/local-apollo-qvp/logs/qbox-build.log`
- `build/local-apollo-qvp/logs/qbox-unit-tests.log`
- `build/local-apollo-qvp/logs/local-build-timings.tsv`

### 4.3 SCP transport unit test

```text
make -f Makefile.cmake mod_test \
  BUILD_PATH=/build/arm/arm-auto-solutions/build/tests/scp-firmware-unit
  -> SCP module tests 77/77 passed
  -> mod_transport_unit_test 24 tests, 0 failures

./local_build.sh scp-firmware
  -> apollo-qvp-si0-bl2.bin rebuilt and deployed
```

`mod_transport_unit_test`에는 유효한 pending request 보존과 잘못된 pending
status 재초기화가 모두 포함된다. source topology test는 AP PFDI와 SI CL1 PFDI
channel이 공통 secure preserve policy를 사용하는지도 확인한다.

### 4.4 최종 정적 검사

```text
python3 -m py_compile <변경 Python helper 5개>
  -> passed

/usr/bin/python3 -m pytest -q \
  tests/test_probe_qemu_cortex_r82.py \
  tests/test_run_qbox_apollo_fvp_full.py \
  tests/test_run_qbox_fvp_rd_aspen_rse.py \
  tests/test_validate_qbox_apollo_topology.py
  -> 64 passed

python3 scripts/test/validate_qbox_apollo_fvp_full_map.py
  -> passed: true

python3 scripts/test/validate_qbox_apollo_topology.py
  -> validation.json status: pass

python3 scripts/test/audit_qbox_core_boundary.py
  -> QBox core boundary audit passed

git diff --check 및 각 owning repository의 git diff --check
  -> top/QBox/QBox-platform/QEMU/SCP/TF-M/meta-hsoc-bsp 모두 통과

markdown-diagram-validator --strict <변경 architecture 문서>
  -> hard_failures=0, viewer_required=0
  -> Mermaid/PlantUML/draw.io record=0; 구조도는 fenced text/기존 PNG 링크
```

## 5. Local source image 반복 검증

수정 후 같은 명령 계열로 5회 연속 실행했다.

```text
python3 scripts/run/run_qbox_apollo_fvp_full.py \
  --si-mode live-cl0-cl1 --timeout 180 --skip-build \
  --out-dir build/qbox-apollo-fvp/architecture-debt-qk-fix-local-rN-20260716
```

| 실행 | `passed` | Linux login 시각 | coverage |
| --- | --- | ---: | --- |
| local r1 | true | 39.139 s | 49/49, pass |
| local r2 | true | 38.233 s | 49/49, pass |
| local r3 | true | 39.859 s | 49/49, pass |
| local r4 | true | 38.343 s | 49/49, pass |
| local r5 | true | 39.242 s | 49/49, pass |

각 directory의 `result.json`, `summary.txt`, domain별 UART log와
`full-coverage-audit.json`이 증거다. 모든 실행에서 RSE BL1/BL2/runtime,
live SI CL0 SCP-firmware, 4-core SI CL1 Zephyr/PFDI/network, AP
TF-A/OP-TEE/U-Boot와 Linux login/root shell marker를 확인했다.

### 5.1 구현 후 리뷰 acceptance

기준 5회 반복 뒤 코드 품질과 FVP software-contract 재리뷰에서 찾은 두 항목을
수정하고 별도 acceptance를 수행했다.

| 항목 | evidence root | 판정 |
| --- | --- | --- |
| resolved CPU 수/bootargs | `build/qbox-apollo-fvp/architecture-debt-qk-fix-local-maxcpus-r1-20260716/` | pass, Linux `Brought up 1 node, 4 CPUs`, 49/49 coverage |
| SMD-owned SCMI SRAM reset | `build/qbox-apollo-fvp/architecture-debt-review-scmi-reset-owner-r1-20260716/` | pass, login 39.061 s, SCMI v2.0, 49/49 coverage |

SCMI 결함 수정 전 진단 run은
`architecture-debt-review-scmi-atu-mailbox-trace-20260716`에 남겼다. SI ATU는
region 14에서 `0xe01b_0000`을 `0x0018_0000`으로 정상 변환했지만, 이후 AP reset
fan-out이 SI0가 설정한 mailbox free bit를 지웠다. 이 때문에 Linux에서
`shmem_tx_prepare()` warning과 response timeout이 발생했다.

`host_ap_mhu_ns_shared_sram`을 AP reset 대상에서 제외한 뒤 QVP log에는 다음
marker가 나타났고 해당 warning/timeout은 사라졌다.

```text
arm-scmi arm-scmi.1.auto: SCMI Protocol v2.0 'arm:arm' Firmware version 0x2100000
```

기존 FVP evidence
`build/tests/verify-login-basic-20260712/fvp/terminal_ns_uart0_5004.log`에도 같은
protocol, vendor와 firmware version이 기록돼 있다. 이는 secondary SCMI
software contract의 focused differential 통과 증거이며, 동일 artifact 전체
FVP/QVP G7 differential을 대신하지 않는다.

### 5.2 secure pending-mailbox 수정 후 최종 local 반복

최종 SCP image를 deploy한 뒤 trace 없이 세 번 실행했다.

```text
build/qbox-apollo-fvp/architecture-debt-final-pfdi-preserve-local-r1-20260716/
build/qbox-apollo-fvp/architecture-debt-final-pfdi-preserve-local-r2-20260716/
build/qbox-apollo-fvp/architecture-debt-final-pfdi-preserve-local-r3-20260716/
```

세 `result.json` 모두 `passed: true`, `blocker: null`이고 각
`full-coverage-audit.json`은 49/49 pass다. 모든 실행에서 다음 marker를 함께
확인했다.

```text
PFDI Agent setup complete
PFDI service ready (4 CPUs)
SMP: Total of 4 processors activated.
SCMI Protocol v2.0 'arm:arm' Firmware version 0x2100000
apollo-qvp login:
```

## 6. Yocto build와 image 반복 검증

### 6.1 Active configuration

빌드 직전 확인한 값은 다음과 같다.

| 항목 | 값 |
| --- | --- |
| `MACHINE` | `apollo-qvp` |
| image | `nexios-image` |
| `TMPDIR` | `build/tmp_baremetal` |
| `RD_ASPEN_VARIANT` | `cfg2` |
| `PC_CPUS_COUNT_DEFAULT` | `4` |
| template | `hsoc-stack/yocto/meta-hsoc-auto-solutions/conf/templates/apollo-qvp/` |

### 6.2 Image build

```text
./yocto_build.sh
  -> Attempted 7,290 tasks
  -> 7,259 tasks did not need rerun
  -> all tasks succeeded
  -> 20 forced-task taint warnings, task failure 0
```

BitBake cooker 증거는
`build/tmp_baremetal/log/cooker/apollo-qvp/20260716025559.log`다.
`qbox-apollo-qvp-native`의 externalsrc configure/compile/check/install과
SCP-firmware externalsrc compile/deploy, firmware 재서명 및 `nexios-image` 완료가
모두 기록돼 있다.

사용한 주요 산출물:

```text
QBox provider:
  build/tmp_baremetal/sysroots-components/x86_64/
    qbox-apollo-qvp-native/usr/bin/platforms-vp

WIC:
  build/tmp_baremetal/deploy/images/apollo-qvp/
    nexios-image-apollo-qvp-20260716025610.wic
  size: 22,285,403,136 bytes

SI0 firmware:
  build/tmp_baremetal/deploy/images/apollo-qvp/si0_ramfw.bin
  sha256: 99e04a35967cd43d25dd1b3727da620e57938e0f92c0a8bd657f9d15fd0394f6
```

### 6.3 Yocto image runtime

Yocto systemd-boot WIC는 local Buildroot boot-entry patch를 사용하지 않으므로
`--rootfs-bootargs-profile none`을 사용했다. QBox provider, RSE/AP flash와 ROM,
TF-M ELF, SI0/CL1 image, DTB, provisioning bundle 및 WIC를 모두
`build/tmp_baremetal` 아래 산출물로 명시했다.

| 실행 | `passed` | Linux login 시각 | coverage |
| --- | --- | ---: | --- |
| Yocto r1 | true | 64.578 s | 49/49, pass |
| Yocto r2 | true | 63.747 s | 49/49, pass |
| Yocto r3 | true | 62.030 s | 49/49, pass |

증거 root:

```text
build/qbox-apollo-fvp/architecture-debt-qk-fix-yocto-r1b-20260716/
build/qbox-apollo-fvp/architecture-debt-qk-fix-yocto-r2-20260716/
build/qbox-apollo-fvp/architecture-debt-qk-fix-yocto-r3-20260716/
```

각 `result.json`은 `qbox_executable`, 모든 input artifact의 절대 경로와 크기,
실제 command, boot marker와 `blocker: null`을 기록한다.

첫 Yocto 시도 `architecture-debt-qk-fix-yocto-r1-20260716`은 product 실행 전에
`uboot_script_missing_bootargs_line` preflight로 종료됐다. 이는 local-image용
`quiet-console` profile을 Yocto WIC에 적용한 runner 선택 오류였고, image 또는
QBox boot 실패가 아니다. profile을 `none`으로 명시한 뒤 세 번 모두 통과했다.

### 6.4 secure pending-mailbox 수정 후 최종 Yocto 반복

새 SCP firmware와 WIC를 명시해 trace 없이 세 번 실행했다.

```text
build/qbox-apollo-fvp/architecture-debt-final-pfdi-preserve-yocto-r1-20260716/
build/qbox-apollo-fvp/architecture-debt-final-pfdi-preserve-yocto-r2-20260716/
build/qbox-apollo-fvp/architecture-debt-final-pfdi-preserve-yocto-r3-20260716/
```

세 실행 모두 `passed: true`, `blocker: null`, coverage 49/49다. SI CL1에서
`PFDI Agent setup complete`와 `PFDI service ready (4 CPUs)`, AP에서 정확히
4 CPU, SCMI v2.0과 `apollo-qvp login:`을 관찰했다. local과 Yocto의
`si0_ramfw.bin` SHA-256도 동일해 최종 반복이 같은 SCP payload를 사용했음을
확인했다.

## 7. 구현 후 4관점 아키텍처 리뷰

| 관점 | 판정 | 근거 및 잔여 조건 |
| --- | --- | --- |
| QBox/SystemC | A4 구조 승인 | broad bridge 제거, SMD/ATU 실제 graph, reset QK 교착 회귀 50회와 기준 full boot 8회, 최종 trace-off 6회 통과. 전 access-kind request context는 후속 |
| system hardware | A4 구조 승인 | Arm Zena CSS의 AP/SMD/RSE/SI view, GIC multi-view, MHU 방향, PPU reset 순서와 SMD-owned mailbox reset policy 반영. cycle-accurate NCI/APU는 후속 |
| system software | 정상 boot 계약 승인 | TF-M/SCP/TF-A/OP-TEE/U-Boot/Linux/Zephyr marker, 4-CPU bootargs, SCMI v2.0과 secure pending-mailbox startup invariant 확인. malformed/timeout/recovery ABI는 후속 |
| QEMU | lifecycle 수정 승인 | BQL, target-vCPU reset completion, stale exit request와 reset-held QK 소유권을 분리. KVM 및 16 CPU matrix는 후속 |

### 7.1 최종 5-lane 품질 리뷰

| lane | 결과 | 근거 |
| --- | --- | --- |
| 목표·제약 | pass | A4 default-deny/canonical owner/4-CPU CFG2 계약 유지, 사용자 OP-TEE diff 제외 |
| QA·회귀 | pass | 정적·단위·build, 50회 reset, SCP 77/77, 기준 8회와 최종 local/Yocto 6회 runtime/coverage |
| 코드 품질 | pass | resolved CPU 수 단일 전달, 제거된 bridge/ATU-check shadow warning 예외 삭제, reset policy contract화 |
| 보안 | pass | 권한 확대나 secret/dependency 추가 없음, broad access 재도입 없음 |
| context/FVP | pass | Zena CSS hardware/software 문서와 FVP SCMI log 대조로 reset owner 및 PFDI mailbox startup 소유권 수정 |

## 8. 명시적 잔여 부채와 blocker

1. 완전한 NI-710AE APU programming model과 secure/domain별 deny matrix.
2. MMU-720AE page-table walk, IOVA map/unmap, EVTQ/IRQ 및 backend 동등성.
3. GPEX requester/StreamID의 모든 payload 종류와 MSI→ITS→LPI end-to-end 검증.
4. debug/direct/reentrant/DMI capability 및 invalidation의 전체 negative matrix.
5. FMU/SSU/RAS/DCLS fault injection, power/reset recovery와 safety timing.
6. SCMI/PSCI/MHU/PFDI/HIPC/FF-A의 malformed, denied, peer-offline, timeout과
   recovery side effect.
7. 16 CPU 성능/RSS budget 및 동일 hash artifact 기반 FVP/QVP G7 differential.

이번 실행에서는 FVP binary를 이용한 동일 artifact differential을 수행하지
않았다. 따라서 Arm 문서와 source-level 구조 비교는 완료했지만 FVP functional
parity는 완료로 판정하지 않는다.

검증 workspace의 OP-TEE submodule에는 본 작업 시작 전부터 존재한 사용자
수정이 남아 있다. 이를 수정하거나 커밋하지 않으며, 이번 변경의 정적 topology
test도 해당 dirty file에 의존하지 않게 유지한다. runtime artifact는 실제
workspace provenance를 result와 build log로 보존한다.
