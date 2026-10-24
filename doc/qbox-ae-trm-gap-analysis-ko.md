# GIC-720AE / MHU-320AE TRM 대비 추가 구현 조사

조사일: 2026-10-23. 대상: Apollo QVP의 현재 작업 트리, QBox/SystemC 모델,
libqemu 연결 및 실제 사용하는 SCP/OS 드라이버.
이 문서의 표와 소스 행 번호는 **후속 구현 전 조사 시점**을 보존한다.
추가 구현은 착수했으며, 현재 변경·검증 상태는
[후속 구현 및 런타임 기록](qbox-ae-followup-validation-ko.md)을 기준으로 한다.
조사 당시에는 모델이나 firmware를 변경하거나 게스트를 다시 실행하지 않았다.

현재 구현은 doorbell/FCE 통신, 일부 GIC 오류 격리, FMU 소프트웨어 주입과
복구를 검증할 수 있다. **두 IP의 AE 기능 또는 MHU FMU 전체 구현으로
판정할 수는 없다.** 먼저 재현된 FMU 결함 두 개를 수정하고, 이미 노출한
접근·기능 지원 계약을 바로잡은 뒤, 실제 오류 검출→격리→RAS/FMU→ISR→복구
경로를 연결해야 한다.

## 기준 판본과 판정 방법

| 대상 | 조사 기준 | 주의점 |
| --- | --- | --- |
| GIC-720AE | [Arm 공식 TRM r2p1](https://developer.arm.com/documentation/102666/0201), 로컬 [Issue 0201-12, 2026-01-30 REL](gic-720ae/0001-Arm-CoreLink-GIC-720AE-Generic-Interrupt-Controller-Technical-Reference-Manual.md) | 로컬 Operation 장의 일부 하위 본문은 수집되어 있지 않다. 해당 상세 규칙은 [이전 Issue 11 공식 PDF](https://documentation-service.arm.com/static/681dc5f30aae2a5d8f0441dc)를 보조로 사용하고 판본 재확인 대상으로 표시했다. |
| MHU-320AE | [Arm 공식 TRM r0p1](https://developer.arm.com/documentation/107612/0001), 로컬 [107612_0001_06_en, 2026-01-31](mhu-320ae/0001-Arm-CoreLink-MHU-320AE-Message-Handling-Unit-Technical-Reference-Manual.md) | 현재 QVP의 채널 수·보안·RAS 구성과 실리콘 synthesis 구성을 동일시하지 않는다. |

`재현 FAIL`은 보존된 실행에서 요구값과 다른 동작을 관측한 결함이다.
`소스 결함`은 TRM과 코드의 불일치를 확인했지만 이번에 실행하지 않은 항목이다.
`부분/미구현`, `미배선`, `조건부`는 각각 동작 일부/전체 부재, 활성 연결 부재,
특정 구성을 켤 때 필요한 기능을 뜻한다. `후보`는 판본 또는 해석 확인이 남았다.

P0는 다음 수정에서 먼저 고칠 재현 결함, P1은 이미 광고한 기능·접근 계약과
활성 경로, P2는 오류 복구·저전력·진단 범위를 확장하는 기능, P3는 선택 구성을
추가할 때의 작업이다. 이는 ASIL 등급이나 실리콘 위험도 평가가 아니다.

관계 검색용 QBox platform 인덱스는 2026-09-30 상태이며 핵심 헤더 세 개가
`metadata_changed`였다. 따라서 판정은 현재 파일을 직접 읽은 결과에 근거한다.
[조사 시작 스냅샷][snapshot]에서 기존 구현 manifest의 소스 46개가 모두 일치했다.
TRM Markdown 파일 217개/301개의 해시도 보존했다. 파일 수는 전 레지스터의
모든 조합을 검토했다는 coverage 수치가 아니다.

## 조사 당시 구현과 실행 증거

| 영역 | 현재 동작 | 증거의 한계 |
| --- | --- | --- |
| AP GIC | View0/View1 MMIO wrapper, SPI/SGI/PPI ISERR/ICERR 일부, backend enable 차단, 재설정 후 enable | 실제 A720AE 1 PE에서 SPI 105→1023→105 PASS. 다중 PE 목적지 격리나 SI 증거는 아니다. |
| SI GIC | CL0/CL1의 독립 libqemu GIC 두 개와 공용 multiview metadata overlay | overlay의 backend가 연결되지 않아 실제 SI IRQ containment는 미지원. |
| MHU FCE | 15 pair/30 endpoint, 활성 구성 64×32-bit·32채널/group; latest-value, pending/read-clear, combined IRQ | SI0 채널 32 IRQ echo PASS. 재사용 모델의 64-bit/split32는 component 범위이며 전체 채널 guest 검증은 아니다. |
| MHU local RAS | AP↔SI0 NS 네 endpoint의 SRAS/RRAS, CE/UC ERRINS, counter/overflow/W1C | guest polling PASS. FHI/ERI 출력은 component 검사만 했고 실제 CPU에 미배선. |
| leaf FMU | GIC 12/MHU 6 records, page0, KEY, SMEN/SMCR/SMERR, ACK/ERRUPDATE 일부 | GIC 1개와 MHU 10개의 leaf→System FMU→SI0 IRQ/SSU 연결. 검출기에서 leaf로 들어오는 활성 연결은 없다. |
| 시스템 | AP4 full-system boot/post-login, SSU 1/1, FMU 20/20, provider CTest 70/70 | 선택된 소프트웨어 주입 시나리오의 PASS다. 추가 FMU probe에서 2 FAIL이 있으므로 FMU 전체 PASS가 아니다. AP16은 정적 구성 검사만 수행했다. |

원 실행 및 명령은 [AE 구현·검증 기록](qbox-ae-gic720-mhu320-validation-ko.md),
[기존 결과 JSON][baseline], [FMU 추가 감사 결과][audit]에 있다.
실패 증거는 기존 PASS 결과와 함께 보존하며 덮어쓰지 않는다.

GIC FMU의 활성 인스턴스는 SI의 `0x32020000`이 명확하다. AP 측
`0x02_0000_D250_0000`은 [개발 가이드](arm_zena_css_dev_guide/09-programmers-model-for-zena-css.md)에서
`FMU_GIC`, SCP에서는 `NI710AE_FMU_GIC`로 명명한다. 이를 AP GIC-720AE 내장
FMU로 단정할 근거는 부족하다. AP GIC 자체 FMU 주소·소유자는 integration
자료로 확정할 항목이며, 이번에는 특정 주소의 미배선 결함으로 등록하지 않는다.

## 재현된 FMU 결함 두 개

### F01 — 정상 byte strobe를 가진 KEY 쓰기 거부 · P0 · 재현 FAIL

TRM의 KEY unlock 조건은 Secure 32-bit write, 하위 8-bit `0xBE`, 네 byte
strobe 모두 활성이다. [공유 FMU 헤더][fmu] `access():474–480`은 byte-enable
포인터가 있으면 내용과 관계없이 거부한다. 네 값이 모두 `0xFF`인 정상 TLM
트랜잭션도 `TLM_BYTE_ENABLE_ERROR_RESPONSE(-5)`가 되고 KEY는 잠긴 채 남는다.

필요한 수정은 반복 byte-enable 패턴까지 평가해 유효한 전체 strobe를
수락하고, 부분 strobe·잘못된 폭/정렬·보안 상태의 처리와 one-shot 소비 규칙을
유지하는 것이다. GIC/MHU가 같은 경로를 쓰지만 **실행 재현은 MHU profile**에서
했다. 두 profile을 영구 회귀검사에 넣어야 한다.

근거: [MHU KEY](mhu-320ae/0058-FMU_KEY-FMU-Key-Register.md),
[MHU lock/key 절차](mhu-320ae/0288-Lock-and-key-mechanism.md),
[GIC KEY](gic-720ae/0205-FMU_KEY-FMU-Key-register.md).
실패 test: `AllEnabledByteStrobesMustUnlock`, [probe.log][probe-log].

### F02 — 서로 다른 MHU 보호 오류의 OF 누락 · P0 · 재현 FAIL

Receiver의 같은 critical record에 SMID 1, SMID 2를 순서대로 주입하면
첫 IERR=1과 OFB는 유지되지만 OF[27]=0이다. MHU의
[Software interaction](mhu-320ae/0289-Software-interaction.md) 31행은 같은
criticality/block type의 여러 오류를 해당 record가 받으면 OF=1로 규정한다.
[ERRSTATUS](mhu-320ae/0047-FMU_ERR-n-STATUS-Error-Record-n-Status-Register-n-0-5.md)의
overflow 정의도 대조해야 한다. 현재 [FMU][fmu] `record_fault():203–232`는 같은
SMID의 반복에만 overflow를 저장하고, `record_status():119–149`는 다른 SMID에
OFB만 붙인다.

**수정은 MHU profile의 규칙으로 한정해야 한다.**
[GIC ERRSTATUS](gic-720ae/0194-FMU_ERR-n-STATUS-Error-Record-n-Primary-Status-register.md)는
현재 PROTID의 반복 오류를 OF, 다른 PROTID를 OFB로 구별한다. 공유 코드에
무조건 OF를 추가하면 GIC 동작을 바꾸는 회귀가 된다.

최소 검증은 MHU의 동일/상이 SMID, criticality별 동시 오류, 첫 syndrome 보존,
OF 없는 ACK의 거부 및 OF 포함 ACK/후속 오류 재보고, GIC의 OF/OFB/OFX 독립
동작이다. 실패 test: `DifferentMechanismsMustSetOverflow`, [probe.xml][probe-xml].

### KEY의 현재 정상 동작과 남은 검사

KEY는 비밀값이나 암호 인증 키가 아니라 잘못된 쓰기를 줄이는 공개된
one-shot write guard다. 현재 구현은 `m_unlocked` 상태 하나로 동작한다.

1. reset 후 잠긴다. Secure 32-bit KEY 쓰기의 하위 byte가 `0xBE`이면 열린다.
2. KEY read는 `0xBE`/`0`을 돌려주며 unlock을 소비하지 않는다.
3. 다음 Secure write가 unlock을 소비한다. KEY 자체와 64-bit CTLR/STATUS의
   상위 32-bit write에는 예외가 있다. 잘못된 KEY 값은 다시 잠근다.
4. 명시적 Non-secure 접근은 보호 상태를 수정하지 않는다. 실제 bus의 보안
   attribute 전달까지 포함해야 하며, KEY만으로 접근 권한이 생기지는 않는다.

`MhuKeyLifecycle` probe는 PASS했다. 상위 byte가 비영인 `0x123456BE`, read의
비소비, 재잠금, CTLR 상위 절반 예외 등을 포함한다. F01은 이 정상
수명주기와 별개인 전송 strobe 처리 결함이다. 근거는 [probe 소스][probe-source]와
[공유 FMU][fmu] `access():433–510`이다.

## 공유 FMU의 추가 구현

| ID / 우선순위 / 상태 | 부족한 동작과 변경 지점 | 완료 기준 및 TRM 근거 |
| --- | --- | --- |
| F03 / P1 / 미구현 | 명령을 `command():280–357`에서 즉시 처리한다. BUSY 진행, 응답 timeout, 늦은 응답의 UNEXP_RESP, powered-off block 상태가 없다. `FMU_TIMEOUT`은 저장값이다. 기능 수준의 요청/완료/실패 상태와 시간 기준을 추가한다. | 정상 완료, timeout 직전/직후, 늦은 응답, busy 중 새 명령, reset cancellation 검사. [MHU STATUS](mhu-320ae/0057-FMU_STATUS-FMU-Status-Register.md), [GIC STATUS](gic-720ae/0204-FMU_STATUS-FMU-Status-Register.md), [GIC TIMEOUT](gic-720ae/0206-FMU_TIMEOUT-Timeout-duration-register.md). |
| F04 / P1 / 미구현·미배선 | 오류 packet과 critical/noncritical wire가 독립 상태가 아니다. `record_status():136–138`은 pending record와 enable 값으로 W를 합성한다. `error_socket`은 있지만 active producer가 없다. wire 선행/packet 지연·유실·stuck 상태와 source clear를 표현해야 한다. | `V=1,W=1,IERR=0`→syndrome 도착, packet-only, W_EN disable, source 재assert, 부모 먼저 ACK 시 relatch를 검사. [MHU error signaling](mhu-320ae/0277-Error-signaling-from-a-MHU-320AE-block-to-the-FMU.md), [wire-only recovery](mhu-320ae/0282-Error-recovery-procedures.md). GIC의 clear 조건인 `IERR!=0`이며 (`W=1` 또는 `W_EN=0`) 자체는 TRM상 정상이다. |
| F05 / P1 / 부분 구현 | ERRUPDATE는 두 record를 visible로 만들 뿐 시작 BLKID부터의 탐색·MODE·전원 상태·OFX clear 선택을 처리하지 않는다. OFX는 queue 비교로 계산되어 독립 sticky 상태가 아니다(`command():292–299`). | GCI BLKID 0/1에 pending을 두고 시작 ID, MODE, CLR_CR/CLR_NCR_OFX, 종료 ID/실패를 검사. [MHU ERRUPDATE](mhu-320ae/0060-FMU_ERRUPDATE-FMU-Error-Update-Register.md), [GIC ERRUPDATE](gic-720ae/0207-FMU_ERRUPDATE-Error-Update-register.md). bits2/1은 critical/noncritical **OFX clear**이며 업데이트할 한쪽 record 선택 비트가 아니다. |
| F06 / P2 / 부분 구현·조건부 | MHU CRC page1은 timeout 값 저장/조회만 있고 page2 오류 상태가 없다. GIC page1 이상은 모두 0이다(`command():321–348`). CRC/PING/ACK 누락·손상·중복, 보호 페이지의 설정/오류 상태가 필요하다. | 정상/유실/중복/bad CRC/ACK timeout, power-stop 중 ping 정지, 상태 clear 검사. [MHU PING](mhu-320ae/0287-Ping-mechanisms.md), [MHU SMRDATA](mhu-320ae/0056-FMU_SMRDATA-Safety-Mechanism-Page-Read-Data-Register.md), [GIC SMRDATA](gic-720ae/0203-FMU_SMRDATA-Safety-Mechanism-Read-Data-register.md). GIC의 보호장치 없는 구성에서는 page1+ read0이 합법적이므로 활성 protection 옵션부터 명시해야 한다. |
| F07 / P2 / 부분 구현 | FMU_FCTLR의 clock-enable/QDENY 비트는 저장만 한다. block power 상태와 명령·quiesce·별도 FMU reset을 연결하지 않는다. endpoint/GIC functional reset과 FMU reset을 구분하는 retention 검증도 부족하다. | 기능 reset 후 syndrome 유지, FMU reset 후 clear, 진행 중 명령/IRQ reset, powerdown deny/accept. [MHU FCTLR](mhu-320ae/0061-FMU_FCTLR-FMU-Feature-Control-Register.md), [MHU resets](mhu-320ae/0293-Resets.md), [GIC resets](gic-720ae/0045-Resets.md). 현재 별도 객체 구조를 곧바로 retention 위반으로 판정하지는 않는다. |
| F08 / P2 / 구성 명세 부족 | GIC Wake Request 통합 여부, block 수, 보호 종류 및 실제 source-SMID 연결을 명시적으로 대응시켜야 한다. page0 성공/SMID 수용이 detector 구현을 뜻하지 않는다. | 구현/합법적 stub/미지원 조합을 discovery·Lua·software·tests가 동일하게 사용. [GIC ERRCTLR](gic-720ae/0193-FMU_ERR-n-CTLR-Error-Record-n-Control-Register.md)의 wake_local record 생략 규칙과 [MHU protection IDs](mhu-320ae/0281-Protection-mechanism-IDs.md) 기준으로 대조. |

FMU 제어 응답의 `FMU_TIMEOUT`과 CRC protection page의 ping 송신/응답 간격은
다른 계약이다. 둘을 하나의 저장 레지스터로 대체하면 timeout 복구를 검증할
수 없다. 최소 기능 모델은 SystemC event와 정해진 clock/time 기준으로 충분하며,
물리 AXI 파형을 재현해야만 이 소프트웨어 계약을 구현할 수 있는 것은 아니다.

## GIC-720AE 추가 항목

아래 소스 위치는 [gicx00_multiview.h][gic] 기준이다. 상세 근거/줄번호와
backend 비교는 [GIC 조사 노트][gic-notes]에 보존했다.

| ID / 우선순위 / 상태 | 현재 차이 및 필요한 구현 | 최소 검증 / 근거 |
| --- | --- | --- |
| G01 / P1 / 미배선 | SI CL0/CL1 raw GIC에 오류 containment가 연결되지 않았다. 공유 metadata wrapper는 backend_socket이 없다. 두 backend의 SPI/PE 공간과 view0 관리 소유권을 보존해 연결한다. | CL0/CL1 각각 실제 CPU에서 정상→차단→복구, 상대 도메인의 IRQ 유지. [ISERR](gic-720ae/0106-GICD_ISERRRn-Interrupt-Set-Error-Registers.md), [SI0 wiring][si0], [SI1 wiring][si1]. AP 결과로 대체 불가. |
| G02 / P1 / 부분 구현 | SPI 소유권/MMIO 필드 검사는 있지만 IROUTER 목적지 PE의 view, 1-of-N 후보, CPU interface SGI 생성 경로와 연결되지 않는다(`access_dist_view():1028`, QEMU `arm_gicv3_cpuif.c`). | 2 PE/view1·2에서 SPI unicast/1-of-N 및 SGI cross-view 차단, same-view 전달. [behavioral separation](gic-720ae/0007-Functional-safety-in-GIC-720AE.md); 상세 routing 규칙은 Issue11 §4.5 보조 근거로 **Issue12 대조 필요**. |
| G03 / P1 / 소스 결함 | `access_viewr():578–599` 등에 Secure 검사가 없다. 명시적 NS View0 접근이 ownership을 바꿀 수 있는 component 경로다. 공통 입구와 좁은 alias 모두 접근 검사를 통일한다. | NS View0 write 후 상태 불변, Secure 정상, View1 NS 정상 접근 회귀. [VIEWR](gic-720ae/0133-GICR_VIEWR-View-Register.md) 106행은 Secure View0 전용. 활성 상위 버스에서 차단되는지와 모든 View0 레지스터에 대한 일반화는 별도 확인. |
| G04 / P1/P2 / 부분 구현 | GCI priority RAM 복구의 DPRIR·priority rewrite 연동이 없다. 현재 PPI ICERR clear는 group/config를 바꾸지만 priority를 처리하지 않는다(`access_redist_safety():923–970`). | 그룹별 default priority, priority byte rewrite와 ICERR 각각의 clear, 실제 PPI 수신. [DPRIR](gic-720ae/0140-GICR_DPRIR-Default-Priority-Register.md); 상세 복구는 Issue11 §4.10.5와 Issue12 대조. 오류 RAM 종류별 전달/차단 차이를 먼저 확정. |
| G05 / P1 / 후보 | `spi_fault_defaults():794–823`는 clear 때도 FCTLR.NSACR의 error-time 값을 사용한다. clear-time default와 구별해야 할 가능성이 있다. | FCTLR.NSACR=1/2/3에서 ISERR→ICERR/ICGERR readback. [FCTLR](gic-720ae/0088-GICD_FCTLR-Function-Control-Register.md), Issue11 §4.11.7의 defaults를 Issue12와 대조 후 확정. 아직 세 번째 재현 결함이 아니다. |
| G06 / P1 / 소스 결함 | `access_redist_safety():935`가 Secure owning view1/2의 GICR_FCTLR까지 RAZ/WI한다. GICD의 view0 제한을 GICR에도 적용한다. | Secure owner view1/2 RW, NS/wrong-view 거부, Secure view0 정상. [GICR_FCTLR](gic-720ae/0130-GICR_FCTLR-Function-Control-Register.md) 215행은 Secure-only로 명시. |
| G07 / P2 / 미구현 | GICD/GICR/GITS RAM ERRINS의 address/bit/VALID/STATUS/RAM geometry가 없다. FMU_SMERR로 대체할 수 없다. | SEC/DED, 잘못된 bit/address, 완료·충돌, ECC/RAM 없는 구성, reset. [GICD ERRINS](gic-720ae/0107-GICD_ERRINSRn-Error-Insertion-Registers.md), [GICR ERRINS](gic-720ae/0147-GICR_ERRINSR-Error-Insertion-Register.md), ITS ERRINS 세 종류. |
| G08 / P2 / 미구현 | GICT RAS bank, CE count/threshold, syndrome/address/misc, UE/FI/UI, ERRIRQCR 및 fault_int/err_int가 없다. FMU record와 별도다. | counter 경계, illegal access/ITS error, W1C/overflow, security, IRQ route→ACK deassert. [GICT summary](gic-720ae/0038-GICT-register-summary.md), [recovery options](gic-720ae/0052-Setting-error-recovery-and-fault-handling-options.md), [ERRIRQCR](gic-720ae/0173-GICT_ERRIRQCR-n-Error-Interrupt-Configuration-Registers.md). |
| G09 / P2/조건부 / 미구현 | SGI distribution RAM의 ICDERRR/SGIDR 복구와 vPE VERRR의 RD/SET/CLR/FIND/response가 없다. vLPI frame도 wrapper에서 reserved 처리된다. | distribution/GCI 오류 구별, SGIDR 복구; vPE 구현 시 FIND wrap/no-match·64-bit 접근·실제 vLPI/vSGI 복구. [ICDERRR](gic-720ae/0138-GICR_ICDERRR-Interrupt-Clear-Distribution-Error-Register.md), [VERRR](gic-720ae/0151-GICR_VERRR-vICM-vPE-Error-Register.md). backend v4.1 설정만으로 virtual AE 동작이 완성되지는 않는다. |
| G10 / P2 / 부분 구현 | GICD/R FCTLR 일부 bit 저장과 scrub 즉시 완료만 있다. 대상 RAM 검사·abort·fault 발견, QD/CGO와 실제 power state 연결, GITS_FCTLR 동작이 없다. | start/abort/complete/reset, latent SEC/DED, quiescence deny, ITS non-quiescent write-ignore. [GICD FCTLR](gic-720ae/0088-GICD_FCTLR-Function-Control-Register.md), [GICR FCTLR](gic-720ae/0130-GICR_FCTLR-Function-Control-Register.md), [GITS FCTLR](gic-720ae/0157-GITS_FCTLR-Function-Control-Register.md). 기존 host_ppu/WAKER 전원 경로는 별도로 존재한다. |
| G11 / P2/조건부 / 미구현 | F06과 연계하여 interrupt-protection BISTBusy/error_BIST_valid/DetectionPaused, per-INTID control 및 GSPV/CPUIF page 상태를 구현한다. SCP 초기화도 성공/실패를 확인해야 한다. | protection 없는 구성의 합법적 read0, 있는 구성의 BIST 성공/실패/timeout/paused 해제. [BIST 초기화](gic-720ae/0049-Interrupt-protection-initialization.md), [SMRDATA](gic-720ae/0203-FMU_SMRDATA-Safety-Mechanism-Read-Data-register.md). |
| G12 / P1/P2 / 미구현·미배선 | source parity, protocol/CRC, external error, RAM fault→GIC leaf FMU가 연결되지 않았다. F04 공통 입력에 block/SMID·INJ=0·source ACK를 연결한다. | source event→정확한 syndrome→부모 CRI/ERI/SSU→clear/reassert. [FuSa I/O](gic-720ae/0043-FuSa-I-O.md), [external inputs](gic-720ae/0044-External-error-inputs.md), [RAM protection](gic-720ae/0047-RAM-protection.md). AP GIC FMU와 NI-710AE의 이름에 GIC가 붙은 FMU를 혼동하지 않는다. |
| G13 / P3 / 조건부 | view3, extended SPI/PPI error registers, real-time 구성, multi-chip, virtual AE의 지원 조합을 먼저 정한다. 현재 wrapper는 view0..2와 960 SPI 범위다. | 옵션 off discovery/RAZ-WI 및 on 경계 INTID·view 격리·chip routing. [Features](gic-720ae/0017-Features.md). 현재 Apollo에 모든 최대 구성을 즉시 추가해야 한다는 뜻은 아니다. |

## MHU-320AE 추가 항목

아래 소스 위치는 [mhu320ae.h][mhu] 기준이다. 세부 TRM·코드 위치는
[MHU 조사 노트][mhu-notes]에 있다. **RAM ERRINS의 비파괴 동작은 정상**이다.
[RAM error simulation](mhu-320ae/0024-RAM-error-simulation.md)은 진단 중 실제
RAM 내용 보존과 실제 오류 우선 처리를 구분한다. M04를 구현하면서 기존
ERRINS를 파괴적인 오류로 바꾸면 안 된다.

| ID / 우선순위 / 상태 | 현재 차이 및 필요한 구현 | 최소 검증 / 근거 |
| --- | --- | --- |
| M01 / P1 / 소스 결함 | RAS가 UE control을 광고·저장하지만 illegal access의 오류 응답은 UE와 무관하고 STATUS.ER도 기록하지 않는다(`ras_features():2989`, `record_error():3044`, `b_transport():3273`). host malformed payload와 architected bus error를 구별한다. | 유효 payload의 잘못된 PAY 폭을 UE=0/1, DAE 조합으로 접근하여 response/ER/syndrome 확인. [Bus errors](mhu-320ae/0039-Bus-errors.md), [RRAS CTLR](mhu-320ae/0249-RRAS_ERR-n-CTLR-Error-Record-n-Control-Register-n-0-9.md), [RRAS STATUS](mhu-320ae/0250-RRAS_ERR-n-STATUS-Error-Record-n-Status-Register-n-0-9.md). |
| M02 / P1 / 소스 결함 | FE_SPT=0인데 FIFO CFG/PAY가 generic backing storage로 read/write된다(`write32():2935`, `read32():391`, non32 copy_write). 비활성 window를 RAZ/WI로 decode해야 한다. | PBX/MBX FIFO CFG/PAY/FLG/CTRL/ACK/INT/ERRINS의 32/64-bit 접근. [FIFO CFG](mhu-320ae/0105-PBX_FFCH_CFG0-Postbox-FIFO-Channel-Configuration-0-Register.md), [FIFO PAY](mhu-320ae/0130-PFFCW-n-_PAY64-Postbox-FIFO-Channel-Window-n-Payload-Register-64bit-access-n-0-63.md). FIFO 전체 구현 M12와 독립적인 현재 구성 결함이다. |
| M03 / P1 / 광고 불일치 | FCGI_SPT=1인데 group별 출력 socket 없이 combined IRQ만 있다(`fast_ras_access():3249`, public sockets:3409). group 출력/동작을 구현하거나 capability와 관련 register 존재 조건을 함께 정합화한다. | group0/1 독립 IRQ, FCG_INT_EN=0이어도 group IRQ/pending 유지·combined만 해제. [FCH_CFG0](mhu-320ae/0200-MBX_FCH_CFG0-Mailbox-Fast-Channel-Configuration-0-Register.md), [FCG_INT_EN](mhu-320ae/0203-MBX_FCG_INT_EN-Mailbox-Fast-Channel-Group-Interrupt-Enable-Register.md). |
| M04 / P1 / 미구현·미배선 | 실제 SEC-data/SEC-address/DED fault state와 containment가 없다. ERRINS와 분리된 event를 만들고 channel 데이터/구성·TL·pending·RRAS·상대 SRAS·FMU를 일관되게 갱신한다. | 진행 DB/FCE traffic에서 SECD 데이터 유지, SECA/DED의 손실/복구 및 peer 보고, 실제 FMU IRQ/SSU, reset. [DB recovery](mhu-320ae/0013-Doorbell-channel-error-recovery-procedure.md), [FC recovery](mhu-320ae/0015-Fast-channel-error-recovery-procedure.md), [RAM/FMU recovery](mhu-320ae/0282-Error-recovery-procedures.md). 물리 ECC 회로 없이도 기능 수준 복구는 구현할 수 있다. |
| M05 / P2 / 부분 구현 | ERRINS의 DWC encoder mode를 무시하고 success/range error만 만든다. 실제 오류와의 overlap 및 encoder mismatch 결과가 없다(`insert_ram_error():3143–3168`). | DWC0/1, status00/01/10/11, invalid bit/address, split32 VALID 마지막, actual fault 우선순위. [FST_ERRINS](mhu-320ae/0244-MBX_FST_ERRINS-Mailbox-fast-channel-RAM-ECC-Error-Insertion-Register.md). 즉시 완료 자체와 결과 종류의 누락은 구별한다. |
| M06 / P2 / 미구현 | MBX_FCTRL.SIP는 backing store 비트로 남아 scrub start/abort/completion이나 오류 발견이 없다. | start→완료, abort/reset, latent SEC/UC, traffic 유지/필요한 recovery. [RAM scrub](mhu-320ae/0025-RAM-scrub.md), [FCTRL](mhu-320ae/0242-MBX_FCTRL-Mailbox-Feature-Control-Register.md). |
| M07 / P2 / 미배선 | FHI/ERI socket과 local RAS interrupt logic은 이미 있지만 활성 Lua와 guest ISR이 없다. 통합 interrupt map을 근거로 route와 handler를 추가한다. | 실제 CPU ISR→syndrome→ACK→deassert→재발. [RAS interrupts](mhu-320ae/0029-Error-recovery-and-fault-handling-interrupts.md). polling PASS와 socket PASS를 guest IRQ 증거로 사용하지 않으며 임의 SPI 번호를 만들지 않는다. |
| M08 / P2 / 미구현 | OP_REQ/CH_OP_MSK는 저장 중심이며 Q-channel/non-operational/Auto Op state가 없다. idle 조건·독립 sender/receiver power·in-flight message·quiesce와 연결한다. | unread DB/FCE, OP_REQ/CH_OP_MSK, powerdown deny, peer offline/restart, reset quiesce. [Power management](mhu-320ae/0026-Power-management.md). OP_REQ=0만으로 즉시 전송을 금지하는 구현은 잘못이다. |
| M09 / P2/P3 / 조건부 | 현재 TZE/RME=0은 합법적 축소 구성이다. 하지만 feat_spt0 override로 미구현 옵션을 광고할 수 있고 security banking/ACR/ERRINS trusted checks가 없다. 미지원 override를 방어하고 필요할 때 bank·권한을 함께 구현한다. | 현재 지원 조합 검사, 옵션 추가 시 NS/Secure/Realm/Root의 bank·alias·권한·reset. [Register pages](mhu-320ae/0041-Register-map-pages.md), [SRAS ACR](mhu-320ae/0155-SRAS_ERRACR-Access-Configuration-Register.md). 현재 NS ERRINS를 곧바로 보안 결함으로 해석하지 않는다. |
| M10 / P2 / 소스 결함·일부 후보 | PBX doorbell INT_EN은 bit0만 정의되지만 모든 bit를 저장/반환한다(`set_int_enable():308–311`). CTRL RES0 및 generic non32 접근도 전용 decode가 필요하다. | INT_EN=0xffffffff→1, RES0/RO 쓰기, 지원 폭의 SET/CLR/ACK side effect. [DB INT_EN](mhu-320ae/0128-PDBCW-n-_INT_EN-Postbox-Doorbell-Channel-Window-n-Interrupt-Enable-Register-n-0-127.md). non32 허용 폭은 MHU architecture 접근 규칙까지 확정 후 처리. |
| M11 / P2/P3 / 검증 공백 | 현재 endpoint 단일 reset과 peer reset 중 전달 방지는 구현되었다. endpoint-only reset의 FMU retention, 진행 event 취소, duplicated FuSa reset 오류 검사는 별도다. | PBX-only/MBX-only/동시 reset과 IRQ/fault, FMU retention/독립 clear. [Resets](mhu-320ae/0293-Resets.md), [cold reset](mhu-320ae/0294-Cold-reset-sequence.md). 물리 reset skew 정확도는 별도 범위. |
| M12 / P3 / 조건부 미구현 | FIFO extension 전체: queue, full/empty, SOT/EOT/ACK/TDM, tide/flush, FIFO RAS/recovery. 현재 FE=0이므로 옵션 도입 때 묶어 구현한다. | variable-length transfer, backpressure, flags/ack/tide/flush, reset, CE/UC/recovery. [FIFO](mhu-320ae/0016-FIFO-channels.md), [FIFO recovery](mhu-320ae/0018-FIFO-channel-error-recovery-procedure.md). M02는 옵션 도입을 기다리지 않고 수정. |

## 소프트웨어 및 활성 연결 변경

하드웨어 모델과 소비자가 함께 바뀌어야 하는 항목이다. 상세 호출 경로와
테스트 위치는 [소프트웨어 조사 노트][sw-notes]에 보존한다.

| ID / 우선순위 / 판정 | 필요한 변경 | 검증 |
| --- | --- | --- |
| S01 / P1 / 소스상 오류 처리 누락 | QVP `fmu_gic_mhu.c`의 `fault_ack():190,203`이 wait/update 실패를 무시하고 내부 API도 void다. 반환값을 내부 ops→`mod_fmu.c`로 전달해 실패 정책을 정한다. 현재 `next_fault()` drain에는 횟수 제한이 없으므로 record가 남으면 ISR 반복·중복 통지가 가능하다. | BUSY stuck/timeout/ACK 실패를 주입하고 ISR 종료·상위 오류 전달·record 보존을 확인. F03 구현과 함께 회귀. 실제 무한 반복은 아직 재현하지 않았다. |
| S02 / P1 / 소스상 계약 위험 | `next_fault(bool critical)`의 인자를 peek/ack 선택에 쓰지 않고 모든 notification에 복사한다. system/leaf peek는 criticality와 무관한 최하위 GSR를 고른다. 동시 pending이면 실제 record와 notification criticality가 달라질 수 있다. | critical/noncritical 동시 및 leaf 혼합 주입→각 fault의 실제 criticality·SSU 상태·중복 여부 확인. 기존 순차 20 tests로는 판정할 수 없다. |
| S03 / P1 / 정보 손실 | fault descriptor는 device/node/SMID뿐이며 GIC BLKID[43:32]를 버린다. SMEN/SMCR/SMERR도 BLKID=0으로 만든다. 활성 GIC FMU의 gci_count=2에서 block1을 구별·제어하도록 descriptor와 command encoding을 확장한다. | GCI0/1 동일 SMID 동시 fault의 식별/개별 ACK/enable/inject. 공개 event 소비자인 SSU/SBISTC/test와 호환성 점검. 단순 ACK 반환 변경과 descriptor 확장은 별도 작업으로 나눈다. |
| S04 / P1 / 소스상 IRQ 정체 위험 | MHU3 `start():635–642`는 소유 group bit를 OR할 뿐 reset 시 켜진 나머지 group을 끄지 않는다. ISR은 등록된 IN channel만 읽는다. group/channel ownership과 미등록 pending 정책이 필요하다. | 채널31/32/33 및 다른 group의 미등록 traffic을 넣어 정상채널 유지·IRQ deassert·폭주 방지를 검사. 실제 폭주는 미재현. 같은 group에 미등록 channel이 있으면 group mask만으로 충분하지 않다. |
| S05 / P2/조건부 / 소비자 미구현 | Linux의 active mailbox와 Zephyr의 실제 `mbox_mhuv3.c`는 doorbell 중심이며 FCE/local RAS 복구 API가 없다. 필요한 제품 경로에 kernel mailbox FCE 또는 진단 소비자, local RAS handler, reset/power 복구를 추가한다. SCP BIST/wire-only/timeout 처리도 F03/F04/G11과 연계한다. | AP IRQ 기반 FCE 32/64-bit, guest RAS ISR, 손실/재전송·power/reset 복구. 지금의 AP polling echo와 SCMI performance fast-channel 프로토콜은 별도이며, 후자를 자동으로 켜지 않는다. |
| S06 / P2 / 진단 관찰·실패 처리 부족 | SI0 `test_mhu_fce`의 irq_count는 첫 accepted callback 수다. 후속 payload는 ACK하지만 count에 포함하지 않고 event enqueue 실패는 로그만 남긴다. 총 handler entry/accepted/dropped를 구분하고 실패 완료·재실행 cleanup을 추가한다. | back-to-back traffic, enqueue 실패, 반복 실행에서 종료가 보장되고 추가/spurious IRQ와 데이터 누락을 식별. 기존 irq_count=1을 전체 IRQ 진입 1회로 해석하지 않는다. |

변경 소유권은 다음과 같다.

| 소유 저장소 | 대상·소비자 |
| --- | --- |
| `hsoc-stack/tools/qbox-platform` | GIC/MHU/shared leaf FMU/System FMU, Apollo Lua, component tests, 실제 CPU fixture. 기존 object/CCI/IRQ domain과 parent record 번호 유지. |
| `hsoc-stack/tools/qemu` 및 필요 시 `qbox` | 실제 GIC CPU interface/SGI/ITS routing에 view 정보와 오류 상태를 연결할 때 변경. wrapper의 readback만으로 G02를 해결하지 않는다. |
| `hsoc-stack/components/system_mgmt/scp-firmware` | 활성 `product/automotive-rd/apollo-qvp/module/fmu/`, `module/mhu3/`, SI0 config/진단. 내부 FMU ops와 system/NI/GIC-MHU 구현·unit fixture를 함께 수정. descriptor/event 변경 시 shared SSU/SBISTC/test 소비자도 점검. |
| `hsoc-stack/components/primary_compute/linux` | Linux 소비자가 필요한 범위의 mailbox/RAS/IRQ 및 DTS. DT 주소는 AP local 주소와 ATU 뒤 시스템 주소를 구별한다. |
| owned `meta-hsoc-bsp`/system_mgmt 경로 | 실제 Zephyr 빌드는 staging된 `apollo-safety-island/drivers/mbox/mbox_mhuv3.c`를 사용한다. 수정은 owned patch/module 경로에 두며 `arm-zena-css` reference를 직접 편집하지 않는다. |
| root `tests/`, `scripts/`, `doc/` | Lua/address 계약, 실행 시나리오·결과 판정, TRM 추적과 구현 범위 문서. |

Linux의 현재 소비자는 `drivers/mailbox/arm_mhuv3.c`다. TF-M/TF-A의 기존
doorbell transport는 유지하며, FCE 사용이나 secure local RAS 소유권이 필요한
경우에만 확장한다. ACK 반환형 수정만으로 OS ABI를 바꿀 필요는 없다.

## 권장 구현 순서와 완료 조건

1. **노출 계약 수정:** F01/F02의 실패 probe를 기존 leaf suite에 편입하고
   GIC/MHU 차이를 고친다. G03/G06, M01/M02/M03/M10, S01/S02/S04의 작은
   회귀검사를 먼저 만들어 현상을 확정한다. capability를 낮추는 선택은
   관련 register와 consumer 계약도 함께 바꾼다.
2. **실제 시스템 경로:** G01 SI 양쪽 containment, G02 다중 PE view 격리,
   F03/F04/F05와 S01/S03, M04의 실제 fault containment를 연결한다.
   source fault→local RAS/leaf→System FMU→CPU ISR/SSU→복구→정상 traffic을
   하나의 시나리오로 확인한다. wire-only/packet-only·동시 fault·오류 중 reset을 포함한다.
3. **진단 범위 확장:** G07/G08/G09 및 M05/M06의 RAM 진단·복구,
   F06/G11의 보호 페이지/BIST, F07/G10/M08/M11의 quiesce·scrub·reset을 추가한다.
   optional FIFO/TZE/RME/view3/multi-chip은 필요한 구성을 선택한 뒤 확장한다.

검증 수준별 완료 기준:

| 수준 | 필수 증거 |
| --- | --- |
| component | KEY/strobe/overflow/profile 차이, 접근 보안/폭/RAZ-WI, command failure, source fault·IRQ level·ACK·reset의 전후 값. 매크로/컴파일만 PASS 처리하지 않는다. |
| firmware unit | 실제 활성 QVP 사본의 ACK 실패, BLKID, criticality 동시 처리, 등록/미등록 FCE traffic. 공통/FVP의 별도 사본은 변경 필요성을 따로 판정한다. |
| 실제 CPU | AP 최소2 PE의 view isolation, SI CL0/CL1 실제 IAR, GICT/MHU RAS handler의 IRQ 및 복구. 기존 1 PE SPI test와 구별한다. |
| full-system AP4 | 기존 boot/post-login/FMU/FCE를 회귀한 뒤 새 fault→복구 시나리오를 실행. 원 이미지/flash와 실행 로그를 분리하고 실패·timeout을 보존한다. |
| AP16/선택 구성 | AP16 runtime, 64-bit FCE guest, vLPI/vSGI, security/FIFO/multi-chip은 각각 별도 완료 기준. 켜지 않은 옵션은 `UNSUPPORTED`, 실행하지 않은 것은 `UNVERIFIED`로 남긴다. |

재사용할 suite는 `tests/components/zena_leaf_fmu/`, `gicx00_multiview/`,
`mhu320ae/`, `tests/platforms/apollo-gic-ae-containment-test.cc`와 SCP의 기존
MHU3/QVP FMU unit tests다. full-system 실행은 post-login 판정을 포함하는
`scripts/run/run_qbox_apollo_fvp_full.py`를 사용한다. 공유 BitBake 작업은 순차로
실행하며 현재 machine/provider 및 배포 binary와 소스 해시를 다시 고정한다.

## 조사 한계와 유지해야 할 구분

- 이번 결과는 TRM과 현재 소스에 대한 gap 조사다. F01/F02 이외 신규 후보의
  실행 재현 및 수정 검증은 하지 않았다. 위 표의 검증안은 새 PASS 결과가 아니다.
- GIC G02/G04/G05의 일부 상세 동작은 Issue11 PDF 보조 근거다. 로컬 Issue12의
  빠진 Operation 본문을 확보해 수정 전에 대조해야 한다. 최신 웹 문서 전체를
  확인했다는 뜻은 아니다.
- MHU SMRDATA page2 표는 CRC timeout/checksum에 같은 bit 번호를 표기한 부분이
  있어, 해당 상태 비트 구현 전에 공식 PDF/후속 정정과 대조해야 한다.
- local RAS ERRINS, FMU SMERR, 실제 detector event, GIC software ISERR는 각각
  목적과 부수효과가 다르다. 같은 fault 주입 기능으로 통합하지 않는다.
- 실제 lockstep 이중 연산·두 cycle 지연, SECDED 회로/주소 parity, AMBA parity,
  clock/reset skew, MBIST/DFT 오류 감지 및 물리 CRC timing은 구현·검증되지 않았다.
  기능 fault 모델의 성공으로 ASIL 진단 coverage, FVP parity 또는 실리콘 정확도를
  주장하지 않는다. 그 범위에는 Safety Manual·integration 자료와 별도 검증이 필요하다.

[fmu]: ../hsoc-stack/tools/qbox-platform/systemc-components/zena_device_fmu/include/zena_device_fmu.h
[gic]: ../hsoc-stack/tools/qbox-platform/systemc-components/gicx00_multiview/include/gicx00_multiview.h
[mhu]: ../hsoc-stack/tools/qbox-platform/systemc-components/mhu320ae/include/mhu320ae.h
[si0]: ../hsoc-stack/tools/qbox-platform/platforms/apollo/soc/hw-block/si_cl0/system.lua
[si1]: ../hsoc-stack/tools/qbox-platform/platforms/apollo/soc/hw-block/si_cl1/system.lua
[baseline]: ../build/qbox-apollo-qvp/ae-20261023/verification-summary.json
[audit]: ../build/qbox-apollo-qvp/ae-fmu-audit-20261023/audit-summary.json
[probe-log]: ../build/qbox-apollo-qvp/ae-fmu-audit-20261023/probe.log
[probe-xml]: ../build/qbox-apollo-qvp/ae-fmu-audit-20261023/probe.xml
[probe-source]: ../build/qbox-apollo-qvp/ae-fmu-audit-20261023/probe.cc
[snapshot]: ../build/qbox-apollo-qvp/ae-gap-research-20261023/source-snapshot.json
[gic-notes]: ../build/qbox-apollo-qvp/ae-gap-research-20261023/gic-findings.md
[mhu-notes]: ../build/qbox-apollo-qvp/ae-gap-research-20261023/mhu-findings.md
[sw-notes]: ../build/qbox-apollo-qvp/ae-gap-research-20261023/software-findings.md
