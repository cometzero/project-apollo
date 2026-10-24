# Apollo QVP AE 추가 구현과 런타임 검증

2026-10-23. [TRM 조사](qbox-ae-trm-gap-analysis-ko.md)의 F/G/M/S 식별자를
유지한 후속 구현 기록이다. `MACHINE=apollo-qvp`, `TMPDIR=build/tmp_baremetal`,
설치된 QBox provider와 `si0_ramfw`를 대상으로 한다.
증거 루트는 [`ae-followup-20261023`](../build/qbox-apollo-qvp/ae-followup-20261023/)이다.

**후속 구현과 지정 시나리오 검증 PASS:** provider CTest 73/73, SCP host
94개 검사, AP 4코어와 SI CL1 4코어의 full-system 실행을 확인했다.
`guest-7`에서 SSU 1개, FMU 20개, 혼합 오류/복구 3개, 실제 RAM 오류 3개와
복구 전후 FCE 왕복 8회를 통과했다. FMU 진단 중 SCMI 조회 31회도 오류 없이
완료했다. [실행 결과](../build/qbox-apollo-qvp/ae-followup-20261023/guest-7/ae-result.json)와
[최종 검증 요약](../build/qbox-apollo-qvp/ae-followup-20261023/verification-summary.json)에
판정 범위를 기록했다. 물리 ECC, lockstep, 오류율 또는 ASIL 진단 coverage를
입증하는 작업은 아니다. 미구현 기능은 마지막 표에 남긴다.

기준은 Arm GIC-720AE r2p1 Issue 0201-12와 MHU-320AE r0p1 Issue 0001-06이다.
이전 조사에서 빠져 있던 GIC Operation의 view/SPI/PPI/SGI/RAM 본문과
protection ID 표는 공식 Issue12 API에서 추가 확인했고 증거 루트의
`gic/trm-issue12-*.{json,txt}`에 보존했다. PPI의 오류 종류별 delivery 규칙과
software ISERR의 containment 규칙은 서로 구분한다.

## FMU 수정과 KEY 동작

- **F01:** KEY를 포함한 MMIO는 모든 실제 byte lane이 활성인 TLM byte-enable
  배열을 수락한다. 반복되는 배열도 평가하며 부분 strobe는 거부한다.
- **F02:** MHU는 같은 block type/criticality record에 다른 SMID가 추가되어도
  OF를 설정한다. GIC는 같은 PROTID 반복의 OF와 다른 PROTID의 OFB를 구별한다.
  두 profile의 첫 syndrome 보존, ACK 및 후속 오류를 각각 회귀검사한다.
- **F03:** 명령 요청과 완료를 SystemC event로 분리했다. BUSY 중 추가 명령은
  폐기하며 오류를 기록한다. TIMEOUT, 늦은 응답의 UNEXP_RESP, 전원이 꺼진
  block, reset 취소를 처리한다. 성공한 응답 시점에 명령의 효과를 적용한다.
  timeout된 ACK가 늦게 도착하여 오류 record를 지우지 않는다.
  늦은 응답도 STATUS의 BLKTYPE/BLKID/SMID를 갱신하지만 진행 중인 새 명령의
  BUSY는 해제하지 않는다.
- **F04:** packet과 error wire를 독립 입력으로 받는다. wire-only의
  `V=1,W=1,IERR=0`, packet-only, W_EN 및 재assert를 표현한다. MHU 검출기는
  실제 오류 event를 leaf에 전달한다. 모든 물리 보호 회로를 연결한 것은 아니다.
- **F05:** ERRUPDATE의 시작 BLKID, 전원 경계의 MODE, 종료 BLKID,
  critical/noncritical OFX clear를 구현했다. SMID255 재전송은 지정 block만
  다시 보이게 한다.

KEY는 암호 키가 아니라 공개된 **one-shot 쓰기 보호**다. reset 후 잠긴다.
Secure 32-bit write의 하위 8-bit가 `0xBE`이고 네 byte strobe가 모두 활성일 때
열린다. read는 unlock을 소비하지 않는다. 다음 보호 대상 Secure write가
unlock을 소비하며, KEY 자체와 허용된 64-bit register의 상위 32-bit write에는
TRM의 예외가 적용된다. 잘못된 KEY 값은 다시 잠근다. 명시적 Non-secure
접근은 보호 상태를 수정하지 않는다. KEY로 bus의 security 권한을 얻지는 않는다.

활성 11개 leaf FMU는 `clock_period_ns=8`을 사용한다. 이는 응답/timeout 검사를
위한 기능 모델의 clock 기준이며 실제 interconnect 지연이라는 주장이 아니다.
재사용 모델의 기본값 0은 기존 즉시 완료 방식을 유지한다.
Timed MMIO는 호출자의 annotated delay를 대기 가능한 SystemC thread에서 소비한
뒤 해당 시각의 완료/timeout 상태를 읽는다. 미래 명령을 예약한 뒤 과거의
BUSY를 계속 반환하던 문제를 수정했다. nonzero delay를 가진 비대기 context는
오류 응답으로 거부하며 debug와 detector 입력은 대기시키지 않는다.
대기 가능한 thread의 BUSY read는 읽은 값은 유지하면서 한 FMU clock의 응답
시간을 소비한다. zero-delay poll이 SystemC delta만 반복하여 완료 event를
굶기지 않게 하며, 긴 명령 전체가 끝날 때까지 read를 막지는 않는다.

소스: [shared FMU](../hsoc-stack/tools/qbox-platform/systemc-components/zena_device_fmu/include/zena_device_fmu.h),
[회귀검사](../hsoc-stack/tools/qbox-platform/tests/components/zena_leaf_fmu/zena_leaf_fmu-tests.cc),
[활성 배선](../hsoc-stack/tools/qbox-platform/platforms/apollo/soc/hw-block/si_cl0/safety.lua).

## GIC 전달 경로와 진단

GIC view 정보가 실제 libqemu GIC의 SPI 목적지 선택, 1-of-N 후보,
SGI unicast/broadcast 및 deactivation 검사에 사용되도록 연결했다.
`has-multi-view`는 기본 off이고 Apollo에서 켠다. 기존 CPU/GIC object와 IRQ
socket 번호를 유지한다. AP의 공개 View0/View1 주소는 각각 `0x20000000`,
`0x20800000`이다. raw distributor/redistributor는 private router의
`0x60000000`/`0x61000000`으로 옮겼고 ITS도 wrapper를 통과한다.
MemoryRegion hint가 public alias를 만들어 검사를 우회하지 못하도록 처리한다.
ITS 상대 `0x30000–0x3ffff`의 Reserved page는 wrapper에서 RAZ/WI로 종결한다.
마지막 word를 읽는 SI ATU 검사가 backend 범위 밖으로 전달되지 않는다.
상대 `0x20000`의 vSGI page는 미지원 범위에 남아 있다.

SI는 기존 CL0 1 PE와 CL1 4 PE의 독립 backend를 공용 wrapper에 연결한다.
View1은 CL0, View2는 CL1이고 View0의 register 접근은 소유 view에 맞게
분기·병합한다. view별 enable과 source ownership을 실제 backend에 전달한다.
이 배선의 존재와 두 SI 도메인의 모든 오류 복구를 런타임에서 검사했다는
판정은 구분한다.
두 QEMU instance와 A720AE CPU 5개(CL0 1개/CL1 4개)를 사용하는 별도 fixture는 각 view의
SPI105/106 격리 중 IAR1023, 상대 view의 정상 delivery, ICERR 및 명시적
재설정 후 105/106 복구를 검사한다. 실제 SI firmware를 실행하는 검사는 아니다.
CL1의 MPIDR `0x10000/0x10100/0x10200/0x10300`에 맞는 GICR_TYPER 검색과
64-bit/분할 32-bit read 결과의 일치도 검사한다.

G03/G06의 Secure 접근 제한, G04의 DPRIR/priority rewrite,
G05의 error-time/clear-time default 구분을 보강했다. GICD/GICR/ITS ERRINS는
주소·bit 범위와 완료 결과를 검사하고 별도 GICT RAS bank에 진단 결과를
기록한다. ERRINS로 정상 interrupt 상태를 손상시키지 않는다. GICT의
CE/UE record, counter/overflow, W1C, ERRIRQCR 선택 SPI의 assert/deassert를
검사한다. RAM geometry는 명시적인 기능 모델 값이며 silicon RAM 조직과
동일하다는 주장이 아니다. SGIDR/ICDERRR와 독립 SGI RAM fault 입력도 추가했다.
SGI RAM DED는 같은 RAM row를 공유하는 PE의 해당 SGI를 격리하고
GICD `BLKTYPE=0, BLKID=0, PROTID=50`을 SI GIC leaf에 전달한다.
GICT의 aggregate fault/error IRQ를 임의의 하나의 보호 ID로 변환하지 않는다.

소스: [GIC wrapper](../hsoc-stack/tools/qbox-platform/systemc-components/gicx00_multiview/include/gicx00_multiview.h),
[libqemu routing](../hsoc-stack/tools/qemu/hw/intc/arm_gicv3.c),
[실제 두 PE 검사](../hsoc-stack/tools/qbox-platform/tests/platforms/apollo-gic-ae-view-isolation-test.cc),
[containment/GICT IRQ 검사](../hsoc-stack/tools/qbox-platform/tests/platforms/apollo-gic-ae-containment-test.cc).

## MHU 실제 RAM 오류와 fast channel

현재 구성은 15 pair/30 endpoint의 64×32-bit FCE이며 32개 channel마다
한 group이다. AP↔SI0 NS 네 endpoint만 local RAS를 켠다.

M01/M02/M09/M10은 illegal access의 CTLR.UE/ER, 미구현 FIFO window의 RAZ/WI,
미지원 feature 광고 방지, RES0/RO 및 접근 폭을 수정했다. M03은 각 group의
IRQ 출력을 추가했고 combined IRQ mask와 독립 동작하도록 했다.
활성 platform은 기존 combined IRQ를 사용한다.

`runtime_inject_ram_fault(fast, channel, kind, bit)`는 latent fault를 arm한다.
다음 수신 transfer, 해당 channel read 또는 scrub이 실제 검출을 일으킨다.
Monitor의 `inject-ram-fault` 성공 결과 `ram-fault-armed`는 검출 완료를 뜻하지
않는다. 잘못된 타입/범위, reset/power 상태 및 중복 arm은 거부한다.

| FCE 실제 오류 | Local RAS | channel 결과 | FMU receiver SMID |
| --- | --- | --- | --- |
| SEC-data, kind0 | RRAS4 CE | payload 보존 | 20 |
| SEC-address, kind1 | RRAS4 CE + TL | payload/pending reset | 21 |
| DED, kind2 | RRAS5 UC + TL, peer SRAS1 | payload/pending reset | 22 |

Doorbell은 같은 분류를 RRAS2/3 및 SMID17/18/19에 대응한다.
검출 event는 `BLKTYPE=1, BLKID=0, INJ=0`이다. 아래 연결은 개발 가이드의
sender-side FMU와 receiver domain0 대응에 근거한다.

| 실제 receiver | leaf |
| --- | --- |
| `si_cl0_ap_ns_mhu_mbx` | `si_cl0_pc0_cl0_mhu_fmu` |
| `host_ap_si_ns_scmi_mhu_mbx` | `si_cl0_cl0_pc0_mhu_fmu` |

M05/M06은 ERRINS DWC encoder/decoder 진단 결과와 실제 오류 우선순위,
FCTRL.SIP scrub 시작·완료·abort/reset을 구현한다. scrub은 delta-cycle scan이다.
M08의 기능 Q-channel은 OP_REQ, CH_OP_MSK, pending과 scrub을 보고
powerdown deny/accept를 결정하고 offline 접근/전송을 거부한다.
기능 socket/API 검사는 물리 clock/power controller 배선의 증거가 아니다.

소스: [MHU](../hsoc-stack/tools/qbox-platform/systemc-components/mhu320ae/include/mhu320ae.h),
[Monitor adapter](../hsoc-stack/tools/qbox-platform/systemc-components/apollo_runtime_injection/src/apollo_runtime_injection.cc),
[구현 계약과 경계](../build/qbox-apollo-qvp/ae-followup-20261023/mhu/implementation.md).

## Firmware 변경

QVP FMU driver는 criticality별로 peek/ACK하고 descriptor에 BLKID를 보존한다.
ISR은 IRQ를 mask하고 framework event를 예약한다. event는 한 번에 제한된
16개만 drain한 뒤 level IRQ를 다시 활성화한다. 남은 fault는 다음 ISR을 통해
ISR queue 뒤에 들어가므로 이미 대기 중인 SCMI event가 먼저 처리될 수 있다.
재진입 전 상태를 먼저 게시하여 즉시 발생한 ISR의 masked 상태를 덮어쓰지 않는다.
ACK/queue 실패 시 mask와 오류
정보를 유지하며 명시적 recover로 재시도한다. 처리 중 오류를 무조건 ACK하거나
긴 drain loop를 ISR에서 실행하지 않는다.

ACK 뒤 notification queue가 부족한 경우 class별 fault 값을 보존한다.
`fwk_notification_notify_atomic()`은 필요한 event pool 용량을 먼저 확인하고
전체 subscriber에 전달하거나 아무것도 전달하지 않는다. 기존 notify API는
변경하지 않는다. 재시도 시 같은 fault를 다시 ACK하거나 일부 subscriber에
중복 전달하지 않는다.
leaf ACK 성공 뒤 ERRUPDATE 또는 ancestor ACK가 실패해도 최대 4단계의
경로·완료 상태를 보존한다. recover는 미완료 단계부터 재개하며 지워진
leaf record를 다시 읽어 식별자를 잃지 않는다.

혼합 오류에서 SSU가 ERRC→ERRN으로 내려가던 결함도 수정했다.
[SSU FSM 설계](../arm-zena-css/documentation/design/ssu.rst)의 전이 조건에 따라
critical 상태를 유지한다. 기존 명시적 clear/reset 경로는 별도로 검사한다.

MHU3는 소유 FCE group만 combined IRQ에 포함하고 같은 group의 미등록
channel을 drain/report한다. `test mhu_fce`는 총 4개 payload, channel31의
masked pending과 channel33의 미등록 traffic을 검사한다. handler 진입 수,
callback 수, 수락한 payload 수를 별도로 기록하며 timeout과 cleanup이 있다.
`test ae`는 혼합 criticality/SMID/BLKID, invalid ID와 ACK timeout/recover를
검사한다. 실제 RAM 검출 경로는 별도 `test ae_ram`에서 확인한다.

Linux/TF-M/TF-A/Zephyr의 기존 doorbell 소비자 ABI는 이 경로에서 바꿀 필요가
없다. AP FCE 응답은 `/dev/mem` polling, SI0 수신은 실제 MHU3 IRQ callback이다.
따라서 이를 Linux FCE mailbox driver 또는 AP local RAS ISR 검증으로 부르지 않는다.

## 실행과 증거

다음 BitBake 명령은 공유 build에서 순차로 실행한다.

```sh
./yocto_build.sh qbox-libqemu-native -c populate_sysroot
./yocto_build.sh scp-firmware -c deploy
./yocto_build.sh qbox-apollo-qvp-native -c check
./yocto_build.sh qbox-apollo-qvp-native -c populate_sysroot
python3 build/qbox-apollo-qvp/ae-followup-20261023/guest-check.py guest-recheck
```

Harness는 canonical `run_qbox_apollo_fvp_full.py --post-login-probe`를 사용한다.
rootfs/EFI/RSE flash state를 실행별로 분리하고 AP/SI0 UART 입력 및
loopback Monitor API를 사용한다. `invocation.json`, `commands.json`,
`actions.json`, UART 원본, `ae-result.json`을 함께 남긴다.
SI CL1의 4개 CPU 초기화·timer/PFDI ready와 heartbeat timeout 부재도 확인한다.
재실행 때는 사용하지 않은 디렉터리 이름을 지정한다. 기존 실행 디렉터리의
재사용은 거부하여 이전 로그를 읽거나 덮어쓰지 않는다.

| 검사 | 현재 증거 |
| --- | --- |
| libqemu native build/install | `libqemu-build-3.log` PASS |
| shared FMU와 MHU 집중 검사 | `runtime-components-tests-1.log` 두 suite PASS |
| Monitor와 FMU 지연 응답 | `fmu-late-tests-1.log` 2/2 PASS; 앞선 CCI fixture 실패는 보존 |
| SCP host / 배포 | 94 PASS (`software/notes.md`), `scp-build-4.log` deploy PASS |
| GIC component/source/실제 CPU 집중 검사 | `gic/native-tests-3.log` 5/5 PASS; source 테스트는 독립 SystemC process |
| Lua AP4/AP16 / Linux 구성 | `lua-tests-its-fix.log` 29 PASS |
| 전체 주소 계약 | `full-map-its-fix.json` PASS |
| provider CTest | `provider-ctest-poll-adapter-fix.log` 73/73 PASS; 4PE discovery, timed FMU 및 실제 Lua CCI 변환 포함 |
| provider 설치 / source 대조 | `provider-install-6.log` PASS; `installed-source-match-guest-7.json` 114/114 일치 |
| 소스 / runtime 파일 고정 | `implementation-manifest-guest-7.json`: 4개 nested repository의 변경 파일 83개, runtime artifact 11개 SHA-256; 실행 종료 후에도 일치 |
| full-system | `guest-7/ae-result.json` PASS, canonical runner `result.json` PASS, 종료 code 0 |

### 최종 full-system 실행

`guest-7`은 설치된 provider와 배포된 SI0 firmware를 사용한 실행이다.
전체 실행의 host 경과 시간은 약 268초이며 모델 지연이나 실리콘 성능으로
해석하지 않는다. 각 검사의 원본은 다음과 같다.

| 시나리오 | 실제 관측 결과 |
| --- | --- |
| Boot/post-login | AP online `0-3`, 8개 driver pattern, systemd failed unit 0개 |
| SI CL1 | 실제 R82 4개 CPU 기동, 125 MHz timer, PFDI 4 CPU ready, 전체 로그에 heartbeat timeout 없음 |
| SSU/FMU | `test ssu` 1/1, `test fmu` 20/20; critical 뒤 noncritical 오류에도 ERRC 유지 |
| 혼합 오류 및 실패 복구 | `test ae` 3/3; 서로 다른 MHU SMID/GIC BLKID 5개 notification, invalid ID 거부, 의도한 ACK timeout 뒤 IRQ unmask·GSR clear·notification 1회 |
| Doorbell SCMI 공존 | 진단 시작 전 첫 성공 조회를 확인하고 `cpuinfo_cur_freq` 반복 조회; 31 sample, 2500000 kHz, read error 0, SCMI timeout/잘못된 응답 경고 `0→0` |
| FCE 정상/복구 후 | 실제 SI0 IRQ callback으로 4회씩 총 8회 왕복, AP payload/read-clear 확인; masked channel31 보존, 미등록 channel33 drain |
| Local RAS 진단 | CE/UC ERRINS의 payload 보존, RRAS 기록 및 W1C clear; 미구현 FIFO RAZ/WI |
| 실제 FCE RAM 오류 | SEC-data/SEC-address/DED 3/3; receiver SMID20/21/22, `device=8,type=1,block=0,INJ=0`, criticality 0/0/1, 복구 뒤 leaf GSR 0 |
| RAM containment | SEC-data payload `0xae320100` 보존; SEC-address/DED의 TL=1과 payload 0; DED peer SRAS1 `0xe4300006` 및 W1C clear |
| Monitor 연결 | 실제 capability에 두 MBX target 존재; SI0 receiver 주입 3회 모두 HTTP202/`ram-fault-armed`, 이후 firmware가 검출·복구를 별도로 확인 |

[SI0 UART](../build/qbox-apollo-qvp/ae-followup-20261023/guest-7/qbox-safety-island-cl0.log),
[SI1 UART](../build/qbox-apollo-qvp/ae-followup-20261023/guest-7/qbox-safety-island-cl1.log),
[AP UART](../build/qbox-apollo-qvp/ae-followup-20261023/guest-7/qbox-primary-console.log),
[Monitor 요청/응답](../build/qbox-apollo-qvp/ae-followup-20261023/guest-7/actions.json)을
함께 보존했다. Monitor 결과만으로 오류가 검출됐다고 판정하지 않는다.
`FMU_DRAIN_FAIL status=-7`은 의도한 timeout 시험에서 한 번 발생하며,
그 뒤의 `AE_RECOVERY_PASS`와 notification 개수로 복구를 확인한다.

canonical runner의 `safety_diagnostics_probe.requested=false` 하위 필드는
미실행 상태다. 이 실행에서는 별도 harness가 진단을 수행하므로 실제 SSU/FMU
판정은 `ae-result.json`과 SI0 원본을 사용한다. FW update, secure-service 및
별도 peripheral profile은 요청하지 않았다.

성공 범위 밖의 관측도 남긴다. post-login의 `/dev/mem` resource-table dump는
`dd_rc=1`이며 `od_rc=0`만으로 dump 검증 성공으로 보지 않는다. remoteproc attach,
RPMsg/ethsi1 및 PFDI 확인과 구별한다. FF-A notification 미지원, SPI DMA 초기화
경고와 Monitor 초기화 구간의 `asio.system:32` 송신 오류 1건도 원본에 남아 있다.
후속 Monitor 요청 3건은 모두 완료됐지만 이 송신 오류의 원인은 별도로 분석하지 않았다.

### 실패 원본과 수정

실패 원본은 성공 결과와 함께 보존한다. `libqemu-build-1.log`의 shadow 변수
빌드 오류, `runtime-components-tests-1.log`의 CCI originator 오류,
`provider-check-1/2.log`의 signal fixture 타입 오류를 수정했다.
GIC native 검사에서 확인한 pre-elaboration notification/소멸 module의 callback과
CPU polling 종료 문제는 독립 SystemC process 및 마지막 handshake 후 WFI로
수정했다. 정상 전달 marker만 찍고 종료가 timeout된 실행을 PASS로 사용하지 않는다.

`guest-1`은 부팅 전 `ap_gic_multiview.internal_spi`의 64-bit signal binding에서
실패했다. Container가 bool/32-bit만 지원하던 지점을 64-bit로 확장하고,
일반/optional port 및 역방향 binding에서 상위 비트가 보존되는 회귀를
기존 FMU Container 검사에 추가했다. 일반 typed signal의 초기값도 0으로
정의했다. `wide-signal-tests-1.log`는 수정 후 PASS이며 guest 재검증은 별도다.

`guest-2`는 `ae_ram` element 초기화에서 assert로 중단됐다. framework가
요구하는 `element_init`과 non-null element data를 추가하고, 실제 module
descriptor를 순회하는 host 회귀로 확인했다. 같은 실행에서 발견한 ITS 창의
router 연결도 AP router의 wrapper socket으로 수정했다. Lua 수정 후 29개
검사를 통과했으며, 이 한 파일의 설치와 source hash는 `its-lua-install.json`에
기록했다. 이후 C++ provider를 다시 빌드했다는 의미는 아니다.

`guest-3`은 위 초기화를 통과했지만 AP 전원 인가 뒤 SI0 `verify_atu_cfg()`의
`0xd07efffc` read에서 data abort가 발생했다. 그 뒤의 RSE AP state read 실패는
후속 증상이다. 첫 실패의 UART 원본과 source/runtime manifest를 보존했다.
해당 주소는 AP master `0x2007fffc`, ITS 상대 `0x3fffc`로 변환된다.
Issue12 Register-map-pages의 Reserved page를 wrapper에서 종결하도록 수정했고,
두 public aperture의 끝부분·64-bit/debug 접근·backend 미전달 회귀를 추가했다.
수정 후 `gic/native-tests-its-tail-1.log`의 2개 suite(33개 component case 및
독립 FMU source 검사)가 통과했다.

`guest-4`는 AP Linux 로그인까지 성공했으나 SI CL1 UART 출력이 없고
4개 코어의 PFDI heartbeat가 timeout됐다. post-login의 remoteproc/`ethsi1`
검사가 실패하여 full-system FAIL로 보존했다. SI CL1 ELF/bin hash와 entry는
이전 성공 기준 `ae-20261023/guest-9`와 동일했다.
`guest-si1-debug-1`의 trace에서 view2의 4개 GICR_TYPER의 상위 affinity가
모두 0으로 읽히는 것을 확인했다. libqemu에서 LPIS/VLPIS를 지울 때 사용한
32-bit complement가 64-bit register의 상위 비트까지 지운 것이 원인이었다.
명시적 64-bit mask와 위 4PE discovery 회귀를 추가했다. 이 진단 실행의
`debug-result.json` PASS는 실패 재현과 trace 수집 성공이며 정상 부팅 PASS가 아니다.

`guest-5`는 boot/post-login, SSU/FMU/AE, FCE와 local RAS까지 통과했으나
RAM 주입 HTTP 요청에서 `schema_version` 누락으로 400 응답을 받았다.
harness에 필수 필드를 추가했다. 같은 실행의 SCMI timeout 2건과 SSU downgrade
로그를 추적하여 위 FMU 시간 처리, batch 재개 및 SSU 상태 보존을 보강했다.
`fmu-ssu-timing-tests-2.log`의 2개 suite가 통과했다. 시간 회귀는 실제 SC_THREAD로
100 ns 뒤의 명령 도착, 도착 전 상태, 8 ns 완료 경계, IRQ assert/ACK/deassert를
관측하며, 오류를 보고하는 비대기 호출 경로도 검사한다.

`guest-6`은 같은 기본 진단을 통과했으나 Monitor allow-list가 비어 있어
RAM 요청이 404로 거부됐다. Lua 배열이 `.0/.1` CCI preset으로 변환되는 실제
경로를 adapter가 읽도록 수정하고 Lua 변환을 직접 사용하는 회귀를 추가했다.
SCMI 경고 1건은 남아 있어 BUSY polling 시간 진전을 보강했다. 당시 동시 조회
프로세스는 Python 초기화 전에 종료 요청을 받아 sample 0개였으므로 공존 PASS로
사용하지 않는다. 다음 harness는 첫 조회 완료를 확인한 뒤 진단을 시작한다.

## 남은 기능과 판정 경계

조사 ID별 소스 변경 범위는 다음과 같다. `부분`은 남은 동작이 있다는 뜻이며,
실행 완료 여부는 위 실행 표를 함께 확인해야 한다.

| 조사 ID | 후속 구현 범위 |
| --- | --- |
| F01, F02 | 수정 및 두 profile 회귀 |
| F03 | BUSY/timeout/late response/power-off/reset 기능 모델 |
| F04 | 독립 wire/packet 입력과 MHU producer 연결; 모든 source 및 wire-only firmware 복구는 부분 |
| F05 | BLKID/MODE/OFX/지정 block resend |
| F06 | CRC/PING 보호 페이지 미구현 |
| F07, F08 | 기능 command 전원 상태·활성 clock 명시; physical clock/reset 및 모든 보호 source 구성은 부분 |
| G01, G02 | SI backend 연결, 실제 libqemu view routing/SGI/deactivation |
| G03, G05, G06 | Secure 접근, error/clear default, owning-view FCTLR 수정 |
| G04 | DPRIR/priority rewrite 복구; 모든 PPI RAM 오류 종류의 CPU 전달 검증은 부분 |
| G07, G08 | 기능 ERRINS/GICT/IRQ; 모든 CPU/ITS protocol 오류 producer는 부분 |
| G09 | SGIDR/ICDERRR 및 SGI DED; vPE VERRR는 미구현 |
| G10, G11 | 전체 GIC scrub/power quiescence 및 protection BIST는 미구현 |
| G12 | SGI RAM DED ID50→SI leaf→parent 연결; 나머지 검출기 부분 |
| G13 | 선택 view3/extended interrupt/multi-chip AE 미지원 |
| M01, M02, M03, M10 | register 계약 및 group IRQ 수정 |
| M04 | DB/FCE latent fault 검출·containment; 두 receiver의 FMU 활성 연결 |
| M05, M06 | ERRINS diagnostic 결과와 실제 오류 우선순위, 기능 scrub |
| M07 | FHI/ERI 제품 배선·guest ISR 미구현 |
| M08 | 기능 Q-channel API/socket; 실제 controller 배선·Auto Op 미구현 |
| M09, M12 | 미지원 광고 방어; TZE/RME/FIFO 전체 기능 미지원 |
| M11 | reset 취소/peer boundary 회귀; physical duplicated reset 및 retention 검증 부분 |
| S01, S02, S03 | bounded drain/실패 복구/criticality/BLKID/INJ 보존 |
| S04, S06 | group ownership·미등록 channel drain·반복 FCE 진단 |
| S05 | SCP 진단 소비자 추가; Linux/Zephyr FCE/local RAS 소비자는 미구현 |

FMU 전체 또는 두 IP의 AE 전체 준수를 선언하지 않는다. 아래는 구현되지 않았거나
별도 runtime 검증이 필요한 항목이며, 단순 register read/write 성공으로 대체하지 않는다.

- F06/G11: CRC/PING/ACK protocol 보호와 interrupt-protection BIST/protection pages.
- F07/F08: physical clock/reset retention 및 모든 source-SMID 통합 구성의 완전한 대조.
- G09/G13: vPE VERRR와 실제 vLPI/vSGI 오류 격리, view3, extended interrupt,
  real-time/multi-chip의 AE 기능. 기존 GICv4.1 capability와 구별한다.
- G10/G12: 모든 GIC RAM의 latent fault scrub, 전원 quiescence 및
  parity/protocol/외부 검출기에서 GIC leaf FMU까지의 완전한 활성 연결.
- M07/M08/M11: MHU FHI/ERI·개별 group IRQ의 제품 배선과 guest ISR,
  power controller Q-channel 연결, Auto Op 및 duplicated physical reset skew.
- M09/M12: FIFO, TZE/RME 보안 banking은 현재 미광고하는 선택 구성이다.
- S05: Linux/Zephyr FCE 및 local RAS 복구 소비자, wire-only 오류의 제품 복구 정책.
- AP16 full-system, guest 64-bit FCE 및 실리콘/FVP timing parity는 별도 증거가 필요하다.
