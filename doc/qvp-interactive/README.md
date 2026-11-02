# Apollo QVP Interactive — Process View 구현 및 설계

2026-11-01 · 상태: **Process View 구현 / 정적 구조 + snapshot import**

## 목표와 범위

QBox 프로세스 안의 SystemC component와 QEMU instance/vCPU가 어떻게 연결되고,
한 번의 memory access, IRQ, mailbox notification이 어디를 통과하는지 탐색한다.
대상 독자는 embedded software engineer이며 한국어 설명에 실제 C++/Lua 식별자를 유지한다.
이번 산출물은 설계안과 조작 가능한 시안이다. 실제 QVP 실행, trace 연결, 성능 계측은 포함하지 않는다.
변경 소유자는 root repository이며 `doc/qvp-interactive/`만 추가한다.

## 실행과 MacBook 접속

현재 서버 LAN 주소는 `192.168.0.13/24` (`enp3s0`)이다. 같은 서브넷 MacBook에서:

**http://192.168.0.13:8765/**

재실행은 서버에서 다음 명령을 사용한다. 기본 Python 외 추가 설치가 없다.

```sh
cd /build/arm/arm-auto-solutions
python3 -m http.server 8765 --bind 0.0.0.0 --directory doc/qvp-interactive
```

foreground 실행은 Ctrl-C로 종료한다. 현재 임시 서버의 PID/log는
`build/qbox-apollo-qvp/qvp-interactive-preview/`에 기록한다. 재부팅 자동 시작은 구성하지 않는다.
HTTP root는 이 문서 디렉터리다. repository 전체를 HTTP root로 노출할 필요가 없다.
주소는 DHCP 변경 시 다시 확인한다. MacBook 실제 접속 여부는 해당 기기에서 확인해야 한다.

## Process View 사용법

1. `View`에서 **Component + Process 경계**, **전체 Process Map**, **Process별 실행 문맥** 중 선택한다.
2. Process Map의 process 또는 instance를 클릭/Enter하면 해당 process 상세로 이동한다. `Process` 선택창으로도 전환한다.
3. 기존 단계 선택/재생은 유지된다. process 상세는 현재 step의 관련 연결만 표시하며, 전체 socket 배선은 Component view에서 확인한다.
4. `지원 도구 표시`로 HTTP/browser/launcher를 펼친다. static 지원 process는 실제 실행 존재를 보증하지 않는다.
5. 노드 inspector에서 host/PID, instance, 실행 문맥, SystemC process, instance에 매핑된 후보 TID를 확인한다. 후보 TID는 해당 node의 현재 실행 TID가 아니다.
6. `현재 view .drawio`로 process 경계가 포함된 현재 화면을 export한다. 기존 `layout.drawio` 5개 page에도 process 테두리를 추가했다.

### Runtime snapshot 가져오기

수집은 QVP 실행 host에서 수행하고, JSON 파일을 MacBook으로 복사한 뒤 **Snapshot 가져오기**로 선택한다.
브라우저 내부에서만 읽으며 서버에 upload하거나 QVP를 제어하지 않는다.

```sh
# PID는 실행 중인 대상에서 확인한 값으로 지정한다. qbox는 논리 role 이름이다.
python3 doc/qvp-interactive/collect_snapshot.py \
  --process qbox=12345 --process http=12346 \
  --output build/qbox-apollo-qvp/qvp-interactive-preview/process-snapshot.json

# 이미 켜진 managed monitor가 있는 경우에만 QMP CPU/TID 매핑을 보강한다.
python3 doc/qvp-interactive/collect_snapshot.py \
  --process qbox=12345 \
  --monitor-manifest /path/to/monitor-runtime.json \
  --output build/qbox-apollo-qvp/qvp-interactive-preview/process-snapshot.json
```

`12345/12346`은 사용 예시이며 실제 PID가 아니다. logical role을 PID에 연결하는 책임은 호출자에게 있다.
collector는 `/proc`의 executable/cmdline, PPID, boot ID+start ticks, thread identity를 수집한다.
프로젝트의 기존 `QBoxDiagnostics`/monitor ownership 검증을 재사용하여 `query-cpus-fast`만 요청한다.
QMP 미연결/미지원은 부분 오류로 남기고, 확인되지 않은 thread role은 UNKNOWN이다.
TCG mode와 binary revision은 직접 확인되지 않아 UNKNOWN이며 source Git revision과 혼동하지 않는다.
현재 collector는 IPC endpoint를 자동 추론하지 않는다. 확인된 IPC는 아래 schema의 `links`에 근거와 함께 제공해야 한다.

Snapshot schema v1:

- `schema_version: 1`, ISO `collected_at`, `processes`, `links`.
- process: `id`, `host`, `executable`, `status`, `pid`, `ppid`, `start_time`, `evidence`, `binary_revision`, `tcg_mode`, `threads`.
- observed identity: `host / pid / boot-id:start-ticks`. `status`는 OBSERVED/UNKNOWN/EXITED/ERROR. 미관측 상태의 PID/PPID/start_time은 null, threads는 빈 배열.
- thread: `tid`, `name`, `start_time`, `role`, `cpus`. CPU mapping은 `instance`, `index`, `evidence: "QMP query-cpus-fast"`.
- link: `from`, `to` (process ID), `transport`, `endpoint`, `evidence`. 가져온 process 간 연결만 허용한다.
- 선택적 `source_revisions`, process `errors`, `cmdline`, snapshot `notes`.

화면은 **수집 시점 snapshot / NOT LIVE**를 표시한다. 종료/부분 실패/역할 미확인을 inspector에 남긴다.
invalid JSON/schema, 중복 ID/상충 PID, 잘못된 TID/mapping/IPC 참조는 거절하고 이전 유효 view를 유지한다.
`Evidence → Static source`로 복귀하면 runtime PID/TID가 사라진다. 다른 snapshot을 가져오면 기존 snapshot 전체를 대체한다.
파일 import는 evidence 내용의 진위를 인증하지 않으며, 수집 이후 process 생존 여부도 실시간 검사하지 않는다.

### 구현 파일과 검사

`process-model.js`는 process 소속/문맥과 snapshot validation, `process-view.js`는 view/inspector/경계 이동,
`process-sources.js`는 SystemC registration 근거, `export-view.js`는 현재 view의 draw.io export를 담당한다.
`collect_snapshot.py`는 root의 기존 read-only monitor 코드를 재사용한다. 새 package를 추가하지 않았다.

```sh
node doc/qvp-interactive/test-diagrams.cjs
node doc/qvp-interactive/test-processes.cjs
python3 doc/qvp-interactive/test_snapshot.py
```

`browser-check.js`는 Playwright의 `async page => ...` 형태의 browser 검증 시나리오다.
테스트에만 TEST_ONLY PID/IPC fixture를 사용하며 production 초기 화면에 넣지 않는다.
검증 결과는 [VERIFICATION.md](VERIFICATION.md)에 기록한다.

## 화면 설계

산업용 logic analyzer처럼 어두운 canvas, 밝은 글자, cyan=data, amber=control,
보라색=DMI로 구분한다. 색과 함께 선 종류/텍스트 label을 사용한다.

| 화면 | 보여줄 핵심 | 완성본의 조작 |
|---|---|---|
| 01 구조 | QBox process → SystemC modules / QemuInstanceManager → domain QemuInstance → vCPU wrappers | AP/RSE/SI0/SI1 확장, instance 소속과 socket 연결 선택 |
| 02 Memory | initiator → router → gs_memory backing | DRAM/SRAM 선택, guest PA → target offset 변환, read/write와 payload 크기 |
| 03 DMI | 최초 transport, DMI grant, QEMU alias, 후속 직접 접근, invalidate | 일반 경로/허용/거절/무효화 비교 |
| 04 Interrupt | component 상태 → signal socket → GIC/NVIC → vCPU → ISR → clear/EOI | mask/pending/level과 INTID 표시, assert/deassert 재생 |
| 05 Mailbox | payload data path와 PBX/MBX notification control path | AP↔SI CL1 우선, 이후 AP↔RSE/SCMI 확장 |

화면은 좌측 chapter 선택, 중앙 topology, 우측 source inspector, 아래 sequence player로 구성한다.
node를 선택하면 경로/소속/소스가 표시되고, step을 선택하면 같은 topology의 active node/edge가 강조된다.
주소·register·상태 변화는 side panel에 before/after로 표시한다.
Play/Pause, 이전/다음, 처음으로, 속도, timeline scrub을 제공한다.
시안은 chapter 선택, 단계 선택, 이전/다음, 재생/정지, 소스 위치 설명까지 구현한다.
중앙은 실제 object 이름과 socket 경로를 표시하는 SVG 상세도이며, 기존 단계 카드는 하단 sequence 선택기로 축소했다.
현재 5개 상세도에 총 **70개 object/설명 노드, 57개 연결**을 제공한다. 이 수는 실제 QVP 전체 component 수가 아니다.
전체 object inventory가 아니라 학습 시나리오에 필요한 경로를 선별했다.

### 2차 설계: 실제 구조에 가까운 다이어그램

- **구조도**: QBox process의 AP/RSE/SI CL0/SI CL1을 구획한다. Manager → Instance → CPU wrapper 참조와 최종 memory binding을 표시한다. AP 기본 16 CPUs, SI CL0 Cortex-R82, SI CL1 Cortex-R82 4개를 표시한다. RSE의 `platform.qemu_inst`와 `rse_cpu_pass.qemu_inst`는 별개다. SI CL0는 `si_cl0_ni710ae_primary_nci.protected_target_socket`을 통과한다. 하단에는 AP ATU → system_router → system_to_smd_nci → smd_router 경로를 둔다.
- **Memory 확대도**: CPU callback/bridge, SystemC bus master `ap_pcie_epc.local_master`, ap_router, DRAM1/2와 SRAM target, host backing을 표시한다. transport response와 CPU local time 복귀도 분리한다.
- **DMI 확대도**: 일반 access, hint, get_direct_mem_ptr negotiation, 거절, instance DMI manager, MemoryRegion alias, 동일 backing, invalidation 경로를 그린다. `host_memory_dmi=false`는 현재 SoC default이며 활성 runtime의 override를 확인한 결과는 아니다.
- **IRQ 확대도**: mailbox status → update_combined_irq → async event → emit_combined_irq → GIC SPI → CPU irq_in과 receiver clear/IRQ deassert를 그린다. ISR/EOI는 조건부 설명 노드이며 firmware trace가 아니다.
- **Mailbox 확대도**: data / notification / ack의 3개 lane을 둔다. AP alias와 SI1 bridge가 같은 `host_ap_bl2_header_sram` backing으로 향한다. `0xE0130000 → 0x00100000`, 크기 `0x80000`을 표시한다. PBX→MBX는 `paired_mbx()` 내부 호출, 수신 clear→PBX는 `paired_pbx()` 호출로 표시한다. 역방향 reply pair는 별도로 표시한다.

실선 TLM, 보라색 DMI, amber IRQ, 파란색 C++ 호출, 회색 점선 참조 관계,
분홍색 반환/무효화로 구분한다. 노드는 색만이 아니라 실제 이름과 socket/function label을 가진다.
확대/축소/맞춤과 스크롤을 지원한다. node 클릭 또는 keyboard Enter/Space로 소스 발췌를 연다.
step 재생 시 관련 node/edge를 강조하고 선의 dash animation으로 방향을 보여준다.
reduced-motion 설정에서는 animation을 멈춘다.
소스 발췌는 정적 snapshot으로 bundle하므로 MacBook에서 서버 파일 경로를 직접 열 필요가 없다.

### 실제 구현 추가 요구: Process View와 실행 경계

상태: **구현 완료 — 정적 Process View 및 선택적 snapshot import**. domain 구획과 OS process 경계를 구분한다.
기존 5개 상세도에 공통 **Process View**를 제공하며, 선택한 주제와 step을 유지한 채 view를 전환한다.
아래 항목은 구현 계약이다. 실제 QBox의 runtime PID/TID/QMP 연결은 별도 검증 대상이다.

#### 경계의 의미

| 계층 | 표시할 내용 | 구분 규칙 |
|---|---|---|
| Host / machine | QVP 실행 Linux host, 문서 열람 MacBook | 서로 다른 host를 최외곽 구획으로 표시 |
| OS process | executable, PID, PPID, 시작 시각, 실행 상태 | 굵은 실선 테두리 + `OS PROCESS` label; 독립 address space 경계 |
| Host thread | TID, 이름, 역할, 해당 PID | process 내부 swimlane; vCPU/SystemC 실행 문맥의 전환 표시 |
| SystemC process | SC_THREAD / SC_METHOD 이름과 관련 module | `SYSTEMC PROCESS` label; OS process/TID와 동일시하지 않음 |
| QEMU instance | instance 이름, manager 참조, CPU/device 소속 | process 내부 점선 구획; instance만으로 별도 PID를 만들지 않음 |
| Guest execution | guest vCPU, ISR, 필요 시 guest OS task | `GUEST` label; guest PID와 host PID를 별도 namespace로 표시 |

QBox와 in-process libqemu/SystemC component는 같은 OS process 안에 배치하는 구조를 기본으로 설명한다.
AP/RSE/SI domain이나 QemuInstance마다 독립 host process가 있다고 추정하지 않는다.
실행 구성이 달라질 수 있는 외부 backend/helper는 소스 또는 runtime 근거가 있을 때만 별도 process로 배치한다.
QBox 밖의 launcher, console client, dashboard/HTTP server, MacBook browser는
`지원 도구 표시` 옵션으로 펼친다. 이들을 emulated memory/IRQ data path에 포함하지 않는다.
HTTP server는 문서 제공 경로이지 QBox memory access를 중계하는 process가 아니다.

#### 화면과 상호작용

- **전체 Process Map**: host별 process box와 확인된 IPC 연결을 보여준다. process를 선택하면 해당 process의 instance/component/thread view로 확대한다.
- **Process별 확대 View**: PID별로 해당 object와 실행 lane을 표시한다. 다른 process에 속한 endpoint는 boundary port로 축약하고 클릭하면 상대 process로 이동한다.
- **경계 overlay**: memory/DMI/IRQ/mailbox 상세도에서도 process 테두리를 유지한다. 하나의 process 안에서 끝나는 경로는 `동일 PID 내부`라고 표시한다.
- **Sequence 연동**: 각 step에 `host / PID / TID 또는 실행 문맥 / SystemC process / instance / component`를 표시한다. 이전 step과 비교해 thread handoff와 process crossing을 서로 다른 badge로 표시한다.
- **Inspector**: node의 소속 process, 참조 instance, 실행 가능한 문맥과 근거를 보여준다. 여러 문맥에서 호출되는 component에 고정 TID 하나를 임의로 할당하지 않는다.
- **Static / Runtime snapshot 전환**: 정적 view는 논리 process ID와 `PID 미확인`을 표시한다. runtime snapshot에서만 확인된 PID/TID와 수집 시각을 표시한다. snapshot을 실시간 상태처럼 표현하지 않는다.

#### 경계별 화살표와 시나리오

| 시나리오 | 표시할 경계/전환 | 금지할 오해 |
|---|---|---|
| CPU 일반 memory access | QEMU callback → `run_on_sysc` 실행 문맥 → router → gs_memory | 함수 호출 또는 thread handoff를 OS IPC로 표현하지 않음 |
| DMI | 같은 process의 QEMU alias와 gs_memory backing, negotiation/무효화 | pointer를 다른 process에서 그대로 사용할 수 있는 것으로 표현하지 않음 |
| IRQ | SystemC event/signal → GIC → vCPU 실행 문맥 | event notify가 곧 context switch 또는 ISR 실행 완료라는 의미가 아님 |
| Mailbox | PBX→MBX의 내부 C++ 호출, 관련 IRQ/guest 실행 | 서로 다른 guest domain이라는 이유로 host process 경계를 만들지 않음 |
| 실제 외부 통신 | 확인된 socket/pipe/shared-memory 등 IPC와 양쪽 endpoint | IPC 종류/방향/동기화 방식을 근거 없이 추정하지 않음 |

Process crossing은 일반 TLM/IRQ 화살표와 별도로 경계 통과 지점에 `IPC` marker를 붙인다.
외부 shared-memory 경로가 확인되는 경우 backing identity와 process별 mapping을 구분한다.
실제 경로가 모두 같은 PID라면 이를 그대로 보여주는 것이 완료 기준이며,
시각적 다양성을 위해 불필요한 process box를 생성하지 않는다.

#### 근거 수집과 데이터 표현

첫 구현은 **정적 구조 + 선택적 read-only snapshot import**로 한다. 문서 서버에 process 제어 API를 추가하지 않는다.
런처 및 QBox instance/thread 생성 코드를 확인하고, 실행 중인 대상이 있을 때
`/proc/<pid>/{cmdline,status,stat,task}`와 thread 목록을 수집한다.
사용 가능한 QMP의 `query-cpus-fast` 결과를 instance/CPU index와 매칭하여 host TID를 확인한다.
QMP 미지원/미연결 또는 thread 역할을 판별할 수 없으면 `미확인`으로 남긴다.
수집 때문에 QVP를 재시작하거나 실행 옵션을 바꾸지 않는다.
SystemC process 이름/등록 함수는 source 기반으로 연결하고, 현재 실행 중인 SC process까지
확정하려면 별도 instrumentation/trace가 필요하다는 경계를 둔다.

현재 graph 데이터에 필요한 항목만 확장한다:

- process: 논리 ID, host ID, executable, 선택적 PID/PPID/start time, evidence, collected_at.
- node: process 참조, 선택적 instance 참조와 execution-context 목록; context별 확인 수준.
- edge/step: source/target context, 전송 수단, 동기/비동기 여부와 근거. 양 끝 소속에서 process crossing을 판정한다.

PID 재사용을 피하기 위해 runtime identity는 host/PID/start time으로 구분한다.
수집할 수 없는 항목은 빈칸 대신 `UNKNOWN` 또는 `NOT_RUN`을 표시한다.
source/실행 파일 revision, TCG mode와 관련 실행 정책도 snapshot에 기록하여
vCPU와 host thread의 관계를 고정된 1:1로 가정하지 않는다.

#### Process View 완료 기준

1. 기존 5개 상세도에서 같은 node가 같은 process identity에 연결되고, view 전환 후 선택 step이 유지된다.
2. 같은 PID 내부의 DMI/TLM/mailbox 호출이 process crossing으로 잘못 표시되지 않는다.
3. 별도 PID 연결은 근거와 IPC endpoint를 표시하고, 정적 view에서는 가짜 PID/TID가 나타나지 않는다.
4. thread handoff와 OS IPC, SystemC process와 host thread, guest task와 host process를 구별한다.
5. snapshot 미제공/일부 실패/대상 종료/PID 재사용 시에도 설명용 static view를 열 수 있고 미확인 상태가 유지된다.
6. 확대도와 draw.io 산출물 모두 process 테두리/범례를 포함하고, keyboard로 process 전환과 node 선택이 가능하다.

### 상세도 범위와 다음 보강

현재 group은 domain/실행 계층을 설명하는 논리 구획이다. 모든 wrapper가 C++ instance의 자식 object라는 의미가 아니다.
router는 논리 decode 모델이며 physical CMN/NI topology나 cycle timing을 재현한 그림이 아니다.
GIC 일부 연결, SystemC helper, firmware 처리 단계는 확대도에서 선별 표시한다.
다음 보강은 Process View와 경계 overlay를 먼저 구현하고, 이어 port-level drill-down, ATU region 상태, guest PA/offset,
DMI grant/deny/invalidate 선택 및 실제 firmware ISR/vring source 추적을 우선한다.

## 소스 기준과 중요한 표현 규칙

기준 root `fd97f9a08f37`, QBox `5fc8c389f5f3`, qbox-platform `e301c1a17e0a`.
작업 트리 기준으로 아래 파일을 확인했다. 다른 경로의 기존 수정은 보존한다.
`build/conf/local.conf`의 MACHINE 기본값은 `apollo-qvp`, template은 `apollo-qvp`다.
`run_qbox_yocto.sh:1323`의 기본 진입점은 `apollo-qvp-saturn-v.lua`다.
이는 파일 확인 결과이며 `bitbake -e` 또는 실행 중인 QVP의 effective configuration 검증은 아니다.

이하 P = `hsoc-stack/tools/qbox-platform`, Q = `hsoc-stack/tools/qbox`.

| 주제 | 현재 소스 근거 | 설계에 반영할 사실 |
|---|---|---|
| instance/vCPU | P/platforms/apollo/soc/hw-block/ap_compute/cpu.lua:27,89 | 여러 AP CPU wrapper가 같은 AP instance를 참조한다. instance를 vCPU 하나 또는 독립 OS process 하나로 그리지 않는다. |
| 최종 binding | P/platforms/apollo/soc/hw-block/ap_compute/interconnect.lua:158,202 | define 시 system_router 연결이 있어도 최종 CPU mem은 ap_router에 연결된다. 메모리 target도 재배선된다. |
| backing | P/platforms/apollo/soc/hw-block/ap_compute/memory.lua:1 | DRAM1 0x80000000 / 0x7f000000, DRAM2 0x20000000000 / 0x80000000. SRAM은 여러 객체로 분할되므로 hardware aperture와 backing 크기를 혼동하지 않는다. |
| 일반 접근 | Q/qemu-components/common/include/ports/initiator.h:658 | do_regular_access → run_on_sysc → b_transport; 반환 후 주소 복원, DMI hint 검사, local time 반영. |
| DMI 제공 | Q/systemc-components/gs_memory/include/gs_memory.h:247,301 | dmi_allow, 범위/권한, backing pointer를 확인한다. 모든 SystemC initiator가 자동으로 DMI를 쓰는 것은 아니다. |
| DMI 매핑 | Q/qemu-components/common/include/ports/initiator.h:448,620 | get_direct_mem_ptr 결과로 instance DMI manager의 alias를 추가한다. 최초 negotiation과 후속 direct access를 분리한다. |
| GIC 출력 | P/platforms/apollo/soc/hw-block/ap_compute/cpu.lua:77 | irq_out_i/fiq_out_i → ap_cpu_i.irq_in/fiq_in. SPI socket index와 architectural INTID를 구분한다. |
| AP→SI1 pair | P/platforms/apollo/soc/hw-block/system_mgmt/ap_si_mailbox.lua:145 및 si_cl1/mailbox.lua:54 | pair=apollo_ap_to_si_cl1, protocol=doorbell-bridge. SI1 MBX SPI index=41, INTID=73. |
| 모델 내부 notification | P/systemc-components/mhu320ae/include/mhu320ae.h:2183 | write_postbox_doorbell → paired_mbx → signal_doorbell_channel. 이 peer 호출을 TLM payload 전송으로 그리지 않는다. |
| IRQ scheduling | P/systemc-components/mhu320ae/include/mhu320ae.h:1059,1101 | update_combined_irq / emit_combined_irq와 event, deassert 처리를 표시한다. |

### 시나리오별 설명 범위

1. **CPU와 instance**: Lua 생성 관계와 실행 관계를 나눈다. wrapper/guest vCPU/host thread는 서로 다른 개념이다. TCG mode와 quantum/synchronization policy는 runtime 확인 전 고정된 thread 수로 표현하지 않는다.
2. **Memory**: 먼저 AP CPU read를 설명하고, 이어 SystemC bus master의 initiator_socket → router → gs_memory.target_socket 접근을 설명한다. b_transport는 data_length를 가진 transaction이며 항상 1 byte가 아니다. address decode, 상대주소, response status, delay를 표시한다. 오류는 성공 흐름과 다른 branch로 표현한다.
3. **DMI**: CPU→bridge→router→memory의 negotiation 왕복 후 host backing alias를 보여준다. grant 거절 시 일반 경로 유지, invalidate 시 alias 제거/재획득을 보여준다. DMI는 물리 cache coherence나 DRAM latency 모델이 아니며 속도 향상 수치를 임의로 넣지 않는다.
4. **IRQ**: source mask/status → signal → interrupt controller pending/enabled/routing → CPU exception → guest handler를 분리한다. device clear와 GIC EOI는 서로 다른 단계다. PPI timer와 RSE NVIC는 별도 예제로 추가한다. mask 상태에 따라 바로 ISR로 진입하지 않을 수 있다.
5. **Mailbox**: 먼저 현재 pair의 실제 C++ peer notification을 보여준다. shared-memory payload/vring은 별도 data lane으로 표시한다. `doorbell-bridge`, fast-channel payload, SCMI shared-memory helper, synthetic proxy/auto-ack는 각각 다른 구현 경로로 구분한다. 모든 mailbox가 payload를 복사한다고 표현하지 않는다. firmware barrier/cache maintenance/ack 순서는 firmware와 driver를 추가 추적한 후 확정한다.

## 구현 방식과 파일 구성

정적 HTML + CSS + JavaScript + SVG를 사용한다. framework, npm build, backend API, DB는 필요 없다.
GIF보다 SVG/DOM animation을 우선한다. 단계 이동, 확대, text 검색과 reduced-motion 대응이 가능하기 때문이다.
GIF는 완성 후 발표용 선택 산출물이며 핵심 UI로 사용하지 않는다.

현재 파일:

- `index.html`: 브라우저 시안과 offline CSS.
- `app.js`: 설명용 scenario data와 player.
- `diagrams.js`: 5개 상세도의 object/edge/source excerpt snapshot.
- `diagram-view.js`: SVG renderer, node inspector, zoom.
- `test-diagrams.cjs`: source snapshot 및 graph integrity 검사.
- `layout.drawio`: SVG와 같은 object/edge 데이터를 담은 5-page 편집 가능한 상세도.
- `README.md`: 설계, 근거, 실행 및 구현 순서.

본 구현에서는 데이터가 커질 때만 `scenarios.js`, `sources/`를 분리한다.
source inspector는 file/line 및 짧은 source excerpt를 bundle했다. revision은 페이지 footer에 표시한다.
MacBook에서 `/build/...` filesystem 링크를 열도록 요구하지 않는다.
기존 `doc/apollo-qvp-qbox-hardware-topology.html`과 dashboard topology는 용어/구조 참고로 재사용한다.
기존 runtime dashboard에 player를 결합하지 않는다. 실시간 제어 기능은 요청 범위에 없다.

## 구현 순서와 완료 기준

1. **현재 단계 — 2차 상세 시안**: 5개 SVG 상세도, 단계 player와 경로 강조, node source excerpt, zoom/scroll, LAN HTTP 제공. 구조도는 STATIC_SOURCE, animation은 ILLUSTRATIVE로 구분한다.
2. **완료 — Process View / 경계 overlay**: 3개 view, 5개 상세도 overlay, 실행 문맥/SC process 구획, snapshot import/validation, read-only collector, draw.io export 구현. 실제 QBox/QMP runtime 매핑은 NOT_RUN이며 HTTP process 수집과 UI/fixture 검증을 수행했다.
3. **첫 완성 단위 — AP memory/DMI**: 최종 Lua binding과 router 주소 변환을 추적하여 SVG topology + transaction inspector + 일반/DMI/실패/무효화 경로 완성. 같은 backing을 두 경로가 참조하는지 검토한다.
4. **IRQ/mailbox**: AP→SI CL1 한 쌍부터 driver→model→receiver→clear까지 추적. payload storage identity, mask/ack, event scheduling을 검증한 뒤 AP↔RSE/SCMI로 확대한다.
5. **검증/배포 정리**: source reference 존재/line/revision 확인, scenario transition assertion, Play/Pause/end/reset와 keyboard 테스트, 1440/1280/768px overflow 확인, reduced-motion 확인, Mac Safari 수동 확인.

완성본의 각 step은 source reference를 가져야 한다. 확인하지 않은 firmware 동작은 `추가 확인`으로 남긴다.
`STATIC_SOURCE`, `ILLUSTRATIVE`, `RUNTIME_TRACE`, `NOT_RUN`을 구분한다.
향후 trace를 붙이면 binary/Lua revision, CCI override, input image, command와 timestamp를 함께 기록한다.
애니메이션 재생 시간은 교육용이며 SystemC 시간이나 실제 latency가 아니다.

## 이번 단계의 제한

runtime/guest boot/traffic/IRQ qualification은 NOT_RUN. BitBake build도 수행하지 않는다.
시안의 IRQ/ISR/EOI와 mailbox 수신 firmware 처리 순서는 조건을 단순화한 설명이다.
정적 연결 검증은 guest protocol의 ordering/cache/barrier 정확성 검증을 대신하지 않는다.
외부 library/font/CDN은 사용하지 않으며 HTTPS/인증/상시 서비스는 추가하지 않는다.
