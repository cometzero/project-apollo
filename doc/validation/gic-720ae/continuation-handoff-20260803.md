# Apollo GIC-720AE 작업 재개 인계서

작성일: 2026-08-03 KST

## 1. 목적과 현재 판정

이 문서는 사용자의 명시적 요청으로 Task 15 실행을 중단한 시점의 구현,
검증, blocker, 남은 계획을 다른 PC와 Agent가 재탐색 없이 이어서 수행할 수
있도록 고정한다.

현재 결과는 **checkpoint publish**이며 GIC-720AE FVP parity 완료가 아니다.
Prometheus plan의 완료 항목은 21개, 미완료 top-level 항목은 29개다. Task
15, 27 및 최종 qualification이 닫히지 않았으므로 plan의 Task 45/46도 최종
완료로 체크하지 않는다. 이번 signed commit과 push는 사용자가 별도로 승인한
중간 인계용 publication이다.

Task 15의 제품 실행, GDB inferior, QBox/QEMU/SystemC process, task-owned
tmux, FIFO, socket, shared memory와 port 12339-12343은 모두 중단·정리했다.

## 2. 재현 기준

### 2.1 활성 제품 구성

| 항목 | 값 |
| --- | --- |
| top branch | `feature/qbox-rebase` |
| machine | `apollo-qvp` |
| RD-Aspen variant | `cfg2` |
| Primary Compute CPU | 4 |
| Yocto TMPDIR | `build/tmp_baremetal` |
| QBox mode | single-SI opt-in, split-SI rollback 유지 |
| active config | `build/conf/local.conf`, `bblayers.conf`, `templateconf.cfg` |

### 2.2 checkpoint source commit

| 저장소 | branch | commit |
| --- | --- | --- |
| Linux | `apollo-fvp-linux-6.18-rt` | `45d9702fbbf0f3a24435d110367c0a37eac51efc` |
| SCP-firmware | `apollo-fvp-scp-2.16` | `8287715ab995cdfe01a54b11910d3e96a9f6ac38` |
| QBox core | `qbox-timer` | `a6ac4fe75d167bcd42e85a73c8fddc61cec7f366` |
| QBox platform | `qbox-timer` | `a0b173437a9d3c6b9ddc2f4aa37070106100ded7` |
| QEMU/libqemu | `qbox-timer` | `a676da8bd0d9c870dece59cd1d69968abddcdb08` |
| meta-hsoc-bsp | `work/apollo-qvp-yocto-qbox` | `036d1d084c4cc0754bdbdbfc54b2ff59398ae325` |
| top | `feature/qbox-rebase` | 이 문서를 포함한 branch HEAD |

top repository가 위 commit을 submodule pointer로 고정한다. 다른 PC에서는
개별 nested branch를 추측해 조합하지 말고 top branch를 먼저 checkout한 뒤
submodule pointer를 적용한다.

```bash
git clone --recurse-submodules \
  git@github.com:cometzero/project-apollo.git arm-auto-solutions
cd arm-auto-solutions
git checkout feature/qbox-rebase
git submodule sync --recursive
git submodule update --init --recursive
git submodule status --recursive
```

## 3. 완료된 구현 범위

plan에서 완료된 항목은 다음과 같다.

```text
1-14, 20-23, 29-31
```

주요 구현은 다음과 같다.

- QEMU가 GICD/GICR/CPU interface/ITS 상태의 canonical owner다.
- SI CL0 1 PE와 CL1 4 PE를 한 QemuInstance와 하나의 5-PE GIC로 묶었다.
- single/split topology 선택과 split rollback 경로를 유지한다.
- SystemC multiview access policy, atomic reset, message register reset을
  구현했다.
- SGI/PPI/SPI ownership route와 QBox BQL shutdown 문제를 수정했다.
- hole-aware ESPI/EPPI state, CPU interface, versioned VMState를 구현했다.
- DirectLPI와 GICv4.1 RVPEID/VPENDBASER/VMAPP/VMOVP qtest를 추가했다.
- Linux, SCP-firmware, QBox, QEMU, QBox platform의 opt-in 검증 surface를
  추가했다.

완료 표시는 각 task 당시의 독립 evidence에 대한 표시다. 현재 전체 tree의
final qualification 또는 FVP parity를 뜻하지 않는다.

## 4. Task 15 중단점

### 4.1 해결된 첫 번째 문제: QBox 시작 SIGSEGV

수정 전 single-SI module 생성 순서는 CPU0 뒤에 GIC를 만들고 CPU1-4를
나중에 만들었다. QEMU GIC realize가 두 번째 CPU interface를 초기화할 때
`qemu_get_cpu(1)`이 NULL이어서 `gicv3_set_gicv3state()`에서 역참조했다.

GDB에서 확인한 핵심 값:

```text
arm_gicv3_common_realize: i=1
qemu_get_cpu(0)=non-NULL
qemu_get_cpu(1..4)=NULL
$rdi=0, $rax=0
```

최소 수정은 기존 `construction_priority`를 사용해 single mode 생성 순서를
다음과 같이 고정한 것이다.

```text
manager -300 -> instance -299 -> CPU0-4 -200..-196 -> GIC 0
```

split mode의 default priority는 바꾸지 않았다. focused test, QBox build,
동일 provider의 bounded native run과 독립 검증이 PASS했고 SIGSEGV는 이후
재발하지 않았다.

로컬 원본 evidence:

- `.omo/evidence/task-15-apollo-gic720ae-implementation/authorized-debug-20260803/qbox-sigsegv-fix/`
- `.omo/evidence/task-15-apollo-gic720ae-implementation/authorized-debug-20260803/qbox-order-independent/`

### 4.2 해결된 두 번째 문제: SCP Test Driver가 실제 API를 검증하지 않음

초기 test는 QBox/SystemC 모델만 실행했고 SCP framework bind와 실제
production power API를 통과하지 않았다. 이를 다음과 같이 보완했다.

- production `mod_gicx00_multiview_power_api` bind
- opt-in `test_gic_power` module
- `GIC_POWER_TEST START/READY/DONE` lifecycle
- invalid power-off ordering의 실제 `FWK_E_TIMEOUT`
- QVP/FVP default image 제외와 opt-in image 포함 검증

보존 실행 파일은 production driver와 Test Driver를 framework로 bind하며,
독립 검증에서 39 lifecycle record, 28 state record와 exact timeout을
재측정했다.

로컬 원본 evidence:

- `.omo/evidence/task-15-apollo-gic720ae-implementation/authorized-debug-20260803/scp-driver-fix-remediation/`
- `.omo/evidence/task-15-apollo-gic720ae-implementation/authorized-debug-20260803/scp-driver-fix-remediation-independent/`

### 4.3 현재 blocker: SCMI request는 도달하지만 SI0가 응답하지 않음

fresh SCP opt-in, Zephyr CL1, QBox provider build는 모두 RC 0이었다. 그러나
canonical 3-cycle runtime은 cycle 1에서 종료했고 결과는 다음과 같다.

```text
runner RC                         1
cycles_verified                   0
verdict                           NOT_QUALIFIED
blocker                           qbox_post_login_probe_not_reached
GIC_POWER_TEST lifecycle          없음
CL1 log                           0 bytes
SIGSEGV/SIGABRT/BQL assertion     없음
```

RSE는 SI image 4와 3을 검증·적재한 뒤 SCMI power-domain protocol version을
세 번 요청했지만 응답을 받지 못해 `SCP is not ready. Abort`로 끝났다.

추가 SystemC trace는 단순한 SCP readiness race 가설을 반박했다. 요청은 SI0
framework 완료 뒤 SystemC time `19.162251998s`에 발생했고 RSE PBX에서 SI0
MBX까지 도달해 combined IRQ를 assert했다. 그러나 SI0가 IRQ를 clear하거나
SCMI response를 돌려주지 않았다. 남은 최초 의심 경계는 다음 순서다.

```text
SI0 MBX combined IRQ
  -> multiview/GIC SPI INTID 105
  -> SI CPU0 GIC CPU interface
  -> SCP mhu3_isr
  -> SCMI response
```

따라서 RSE retry 횟수 확대나 임의 sleep은 해결책으로 채택하면 안 된다.
먼저 INTID 105의 pending/enable/group/priority/target과 CPU0 IRQ mask/PC,
`mhu3_isr` 진입 여부를 같은 timestamp에서 확인해야 한다.

로컬 통합 evidence:

- `.omo/evidence/task-15-apollo-gic720ae-implementation/authorized-debug-20260803/integration-3cycle/AdversarialVerify.md`
- manifest SHA-256:
  `8666ac7a4d1394a571ebfae61780ea734a11dbb602f551d68f88ab6d87633017`

### 4.4 마지막 GDB 문제와 정확한 다음 방법

세 host-GDB 시도는 isolated libqemu가 `/tmp/qbox_lib.*`에 복사된 뒤
`dlopen()` 직후 unlink되어 symbol file을 유지하지 못했다. 세 번째 시도는
x86-64 syscall catch에서 `$rax`를 검사했지만 syscall entry 번호는
`$orig_rax=263`에 있으므로 unlinkat을 놓쳤다.

같은 세 방법을 반복하지 말고 다음 `gdb-red-04`를 사용한다.

1. exact current `platforms-vp`와 provider hash를 기록한다.
2. pwndbg/GDB에서 `catch syscall unlink unlinkat`을 설정한다.
3. syscall entry는 `$orig_rax`로 판별한다.
4. `/tmp/qbox_lib.*` 대상 unlink/unlinkat만 suppress한다.
5. Python `FinishBreakpoint`로 libc return `$rax=0`을 만들고 inferior가
   성공으로 인식하게 한다.
6. `sharedlibrary`를 갱신하고 retained SI libqemu ELF 두 개와 build-id를
   기록한다.
7. `gicv3_dist_set_irq`와 `gicv3_cpuif_update`를 symbol로 resolve한다.
8. INTID 105 assert 시 GIC distributor/redistributor/CPU0 state와 guest
   CPU0 PC/PSTATE를 캡처한다.
9. guest GDB를 병행하면 RSE, SI, SystemC의 active domain을 함께 pause한 뒤
   `continue`한다. GDB port에 TCP health-check를 보내면 안 된다.
10. `mhu3_isr` breakpoint 진입/미진입으로 소유 경계를 확정한 다음에만
    production patch를 만든다.

중단 시점에는 `gdb-red-04`가 시작되기 전에 사용자 요청으로 agent를
interrupt했다. 이 method의 PASS나 product root cause 확정은 아직 없다.

검토 evidence:

- `.omo/evidence/task-15-apollo-gic720ae-implementation/authorized-debug-20260803/scmi-readiness-fix/DiagnosticClaim.md`
- `.omo/evidence/task-15-apollo-gic720ae-implementation/authorized-debug-20260803/scmi-readiness-fix/gdb-symbol-review/Review.md`

## 5. Task 27 환경 blocker

Task 27의 host tool, Linux selftest, Yocto profile 구현 lane은 작성됐지만
통합 image를 만들지 못했다.

```text
failed task      key-store-0.1:do_unpack
host error       PermissionError: /proc/self/uid_map, EPERM
control          unshare -Ur true도 동일 EPERM
runtime          시작하지 않음
```

AppArmor/user namespace policy를 code나 BitBake 설정으로 우회하면 안 된다.
unprivileged user namespace를 허용하는 host/container에서 isolated profile을
다시 빌드하거나, host policy 변경을 별도로 승인받아야 한다.

## 6. 현재 root test 상태

커밋 직전 검증:

```text
git diff --check                      PASS, 7 repositories
changed Python py_compile             PASS
pytest -q tests                       182 passed, 11 failed, 1 xfailed
```

11개 실패는 인계 시점에 숨기지 않고 다음 세 그룹으로 보존한다.

| 수 | 원인 | 다음 조치 |
| ---: | --- | --- |
| 2 | controller의 `/tmp/gic720ae-pristine-*` snapshot이 없어 source-state test가 `missing_input` | tmp 경로가 아닌 repo-portable pristine fixture/producer 계약으로 바꾼다. |
| 7 | Task 14가 reset fanout에 multiview/messreg를 추가했지만 `test_gic720ae_runner_topology.py`의 expected reset list가 이전 값 | current Lua/source graph를 다시 읽고 single/split expected를 갱신한 뒤 negative rollback을 재실행한다. |
| 2 | `validation-surfaces.yaml` source hash/line evidence가 현재 source와 달라 `stale-source-evidence` | current published commit SHA와 line span으로 ledger를 재생성하고 out-of-range negative를 다시 실행한다. |

첫 `pytest -q`는 경로를 지정하지 않아 nested Linux selftest까지 수집했고
독립 CLI parser와 충돌했다. 이는 제품 test 결과가 아니며 올바른 root 명령은
반드시 `pytest -q tests`다.

## 7. 남은 29개 항목과 실행 순서

### 7.1 P0 blocker closure

| 순서 | Task | 목적 | 선행/현재 이슈 | 완료 gate |
| ---: | --- | --- | --- | --- |
| 1 | 15 | GICR_PWRR/WAKER power bridge | INTID 105에서 SI0 응답 단절, 4.4절 GDB 필요 | 3-cycle real lifecycle/state/timeout/reset PASS |
| 2 | 16 | 단일 SI GDB endpoint/selector | Task 15 debug workflow와 결합 | CL0/CL1 selector, 5 threads, two targets, non-debug regression |
| 3 | 17 | SCP CL0 controlled IRQ/FMU | 15/16 필요 | actual CLI command와 handler delta, negative isolation |
| 4 | 18 | Zephyr CL1 SMP/IPI/timer | 15/16 필요 | directed/broadcast IPI, timer PPI, cross-view negative |
| 5 | 19 | single-SI default 전환 | 15-18 모두 필요 | same-SHA single default와 split rollback soak |

### 7.2 identity, extended range, Primary Compute

| 순서 | Task | 목적 | 선행/현재 이슈 | 완료 gate |
| ---: | --- | --- | --- | --- |
| 6 | 24 | QEMU-owned GIC-720AE IIDR | generic identity 과장 금지 | AP/SI IIDR qtest와 readback |
| 7 | 25 | `spi/espi/ppi/eppi` QBox socket ABI | Task 24 이후 | socket family별 bounds/delivery CTest |
| 8 | 26 | Apollo SI extended capacity runtime | 19/25 필요 | Zephyr/SCP actual ESPI/EPPI delivery |
| 9 | 27 | Linux controlled GIC probe | user namespace EPERM | opt-in image + Linux runtime delta/affinity/hotplug |
| 10 | 28 | PCI MSI-X/ITS/LPI vs INTx | 27 필요 | physical LPI counter delta와 INTx control |
| 11 | 32 | opt-in KVM software-vLPI | hardware VFIO gap 분리 | software probe PASS, hardware gap truthful BLOCKED/P2 |

### 7.3 safety product 기능과 differential

| 순서 | Task | 목적 | 선행/현재 이슈 | 완료 gate |
| ---: | --- | --- | --- | --- |
| 12 | 33 | SPI collator preflight/message path | 13/17 필요 | active preflight 후에만 message delivery |
| 13 | 34 | GIC FMU SystemC model | 33 필요 | GIC-specific fault/status CTest |
| 14 | 35 | SCP production FMU end-to-end | 17/34 필요 | production driver/CLI counter와 negative |
| 15 | 36 | 공개 RAS/GSPV error record | 17/18/26/35 필요 | 공개 범위 correction/flush, 비공개 safety 과장 금지 |
| 16 | 37 | low-power/hotplug/reset | 15/19 필요 | repeated recovery와 stale IRQ 부재 |
| 17 | 38 | SI FVP/QBox differential | 17/18/26/33-37 필요 | same stimulus/input SHA differential |

### 7.4 freeze, final qualification, review

| 순서 | Task | 목적 | 완료 조건 |
| ---: | --- | --- | --- |
| 18 | 39 | source/commit/input freeze | Task 1-38 closure와 immutable manifest |
| 19 | 40 | Primary Compute Linux final | fresh Linux qualification |
| 20 | 41 | SI CL0/CL1 final | fresh SCP/Zephyr qualification |
| 21 | 42 | FVP differential/full coverage | fresh FVP comparison과 coverage audit |
| 22 | 43 | 한글 문서 동기화 | final SHA와 실제 PASS/BLOCKED 일치 |
| 23 | 44 | release exit gate | repository/pointer/rollback read-only audit |
| 24 | F1 | plan compliance | exact freeze SHA review |
| 25 | F2 | code quality | full diff review |
| 26 | F3 | real manual QA | Linux/SCP/Zephyr/FVP surface 실행 |
| 27 | F4 | scope fidelity | mirrored GIC/permanent test ABI/과장 방지 |
| 28 | 45 | final atomic commit closure | 44와 F1-F4 PASS 후 수행 |
| 29 | 46 | final GitHub publish | Task 45 후 nested-first/top-last remote SHA 일치 |

상세 acceptance command와 deferred 위험은
[`deferred-tasks-todo.md`](deferred-tasks-todo.md)에 있다. 그 문서의 seq 94
분류 숫자는 과거 snapshot이므로 task 상태는 본 문서를 우선하고, 개별 task의
명령/위험 설명만 참고한다.

## 8. 재개 직후 권장 명령

```bash
git status --short --branch
git submodule foreach --recursive 'git status --short --branch'
sed -n '1,220p' build/conf/local.conf
sed -n '1,220p' build/conf/bblayers.conf
cat build/conf/templateconf.cfg
pytest -q tests
./local_build.sh qbox
```

Task 15는 먼저 component/build green을 반복하지 말고 4.4절의 GDB 캡처로
INTID 105 소유 경계를 확정한다. 수정 후 좁은 one-cycle surface가 실제
`GIC_POWER_TEST` lifecycle과 `FWK_E_TIMEOUT`을 통과한 경우에만 fresh
3-cycle qualification을 재실행한다.

canonical 최종 명령의 옵션은 source에서 다시 확인한 뒤 다음 entrypoint를
사용한다.

```bash
python3 scripts/test/run_gic720ae_p0_power_reset.py --help
python3 scripts/test/run_gic720ae_p0_power_reset.py \
  --si-single-gic --cycles 3 --timeout 600 \
  --record-artifact-hashes --si0-command 'test gic_power' \
  --out-dir build/qbox-apollo-qvp/gic720ae-task15-resume
```

ELF와 image 인자는 fresh build 경로를 명시하고 result JSON에 hash가 묶였는지
확인해야 한다. `--dry-run`, marker-only, TCP connect, boot 문자열만으로 PASS를
기록하면 안 된다.

## 9. portable evidence 경계

`.omo/evidence/`는 local 실행 artifact이며 GitHub checkpoint에 포함되지 않을
수 있다. 다른 PC에서는 이 문서의 source commit과 명령을 기준으로 evidence를
fresh 생성해야 한다. 로컬 artifact가 복사 가능한 경우 각 디렉터리의
`SHA256SUMS`를 먼저 검증하고, source/image/provider hash가 다르면 PASS를
재사용하지 않는다.

현재 handoff에서 재사용 가능한 것은 문제 가설과 재현 절차이며, runtime PASS
판정이 아니다.
