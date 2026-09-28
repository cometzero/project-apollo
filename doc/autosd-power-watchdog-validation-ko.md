# AutoSD full-system 전원 제어와 SBSA watchdog 검증

## 범위

`run_qbox_autosd.sh`의 실제 RSE → SI CL0/SI CL1 → AP 부팅 경로를 대상으로 한다.
Host 프로세스를 재실행하여 guest reboot처럼 보이게 하는 방식은 native reset
검증으로 인정하지 않는다. 수정한 full-system의 AP non-secure watchdog WS1은
SI CL0를 통한 coordinated AP standalone reset이며, 정상 PSCI system reset의
RSE/SI 전체 reset과 범위가 다르다.
이 연결을 TRM이 정한 watchdog reset 범위로 단정하지 않는다. 물리 전원 rail, ASIL 인증,
실제 하드웨어 latency는 이 검증의 범위가 아니다.

부팅 최적화 결과는 [부팅 성능 보고서](autosd-boot-performance-ko.md), watchdog
실행 명령은 [Guest Quick Guide](autosd-watchdog-guest-ko.md)를 참고한다.

## 검증 결과 요약 (잔여 항목 포함)

| 항목 | 판정 |
|---|---|
| 일반 shutdown / poweroff / native reboot | 실제 guest 경로 PASS; 최종 비-debug 실행에서 native reboot 2회 및 정상 shutdown PASS |
| AP non-secure SBSA WS1 반복 만료 | 동일 QBox PID에서 연속 2회 reset 및 복구 PASS |
| 반복 복구 후 서비스 | 매회 4 CPU, failed 0, Automotive health, PFDI startup PASS |
| 반복 복구 후 HIPC | 매회 AP→SI ICMP 3/3, 임시 VLAN 연결 정리 PASS |
| systemd RuntimeWatchdog | 별도 일회성 feeding/원복 PASS, 기본 비활성 유지 |
| canonical BSP / 모델 시험 | Zephyr 수정 포함 5,847 tasks PASS, platform 64/64, core 61/61 |
| SCP / TF-M / root focused 시험 | 101 / 17 native cases / 최종 139 focused cases PASS (서로 다른 시험군) |
| SI1 재부팅 로그 | Zephyr backend ID 초기화 경쟁 조건 수정 후 native reboot 2회 모두 새 SI 로그 PASS |
| SI1 재링크 호환 | 입력 ELF/bin/CRC 검사 및 ELF entry 기반 4 CPU RVBAR 자동 설정 PASS |
| 미해결·미검증 | 이전 별도 cold boot의 core2 OFF 경계 정지 1회; 추가 reset harness 종료 timeout; 장시간 stress, secure/SI watchdog 만료 및 물리 timing 미검증 |

아래 실패 이력은 수정 과정의 원본 증거이며 최종 연속 reset 성공으로 덮어쓰지 않는다.
성공한 두 cycle은 장시간 reset stress 또는 모든 스케줄링 순서의 검증이 아니다.

## AutoSD 문서와의 대응

기준 문서는 checkout된
[AutoSD Watchdogs](../autosd/sig-docs/docs/features-and-concepts/watchdogs.md)다.
문서의 i6300esb 예제는 특정 x86 장치의 구현 예이며, Apollo에서는 동일한 Linux
watchdog API를 SBSA driver에 적용한다. 장치별 레지스터를 i6300esb와 혼용하지 않는다.

| 기능 | 이번 구성 |
|---|---|
| 외부 timeout/multi-stage watchdog | SystemC SBSA 모델, WS0/WS1 관측 |
| userspace 장치 제어 | SETTIMEOUT / KEEPALIVE / GETTIMELEFT / DISABLECARD |
| systemd process monitor | 기존 서비스 Restart 정책 및 Safety Monitor와 별개 |
| systemd hardware feeding | RuntimeWatchdog 별도 opt-in, 데모 도구와 동시 소유 금지 |
| panic-on-oops | AutoSD kernel-automotive 정책과 Yocto BSP 정책을 동일하다고 가정하지 않음 |
| reboot를 넘어 유지되는 OTA watchdog | 이 SBSA reset 시험의 범위 아님 |

`not_in_nav/unattended_updates.md`의 `/dev/virtio-ports/watchdog.0` 외부 watchdog은
reboot를 넘어 OTA boot timeout을 감시하는 별도 방식이다. reset 시 초기화되는 SBSA
watchdog 시험을 그 기능 또는 OSTree 자동 rollback 검증으로 보고하지 않는다.

문서의 FDTI/FRTI/FHTI에 맞춰 feeding 중단, WS0, WS1, 새 boot ID, 서비스 정상화
시점을 분리한다. 이 데모의 timeout 20초는 기능 시험값이며 차량의 FTTI 요구사항이나
안전성 기준을 충족한다는 의미가 아니다. Host wall time, SystemC simulation time,
guest monotonic time도 서로 혼합해 latency 수치를 계산하지 않는다.

## 수정 전 native reboot 기준선

증거: `build/qbox-apollo-qvp/autosd-native-reboot-baseline-20260928/`와
`build/autosd/native-reboot-baseline-{request,after}-20260928/`.

| 관측 | 결과 |
|---|---|
| 요청 | `systemctl reboot --no-block` |
| QBox main/child PID | 583719 / 583776, 재부팅 전후 동일 |
| 이전 boot ID | `025568bd-dcd3-4351-b3e9-e9bb5f257c86` |
| 이후 boot ID | `fe243c6f-fc1b-4600-b171-b53f1fa6bb1c` |
| RSE | power state notification → Resetting system → 두 번째 TF-M 부팅 |
| SI CL0/SI CL1 | 두 번째 SCP/Zephyr 부팅, RPMsg endpoint 재연결 |
| AP | 두 번째 TF-A/OP-TEE/Linux/AutoSD login |
| guest 서비스 | failed 0, QM/ADAS/Safety Monitor active |

기존 firmware의 PSCI → SCMI → SCP notification → RSE reset 경로는 동작한다.
따라서 SCP의 WFI 코드를 임의로 대체하거나 별도 host 재시작으로 우회하지 않는다.
이 기준선은 한 번의 정상 reboot 증거이며 watchdog 만료나 반복 reset을 증명하지 않는다.

## reset 모델 변경

| AP non-secure watchdog 항목 | 설정/경로 |
|---|---|
| Linux DT | `arm,sbsa-gwdt`, control `0x1a420000`, refresh `0x1a430000` |
| WS0 | GIC SPI 50, Linux `action=0`에서는 첫 만료를 panic으로 처리하지 않음 |
| WS1 (full-system 수정) | AP SPI51 + SI CL0 INTID321(SPI289), SCP warm-reset event |
| Counter frequency | 125 MHz |
| Linux | `CONFIG_ARM_SBSA_WATCHDOG=y`, `CONFIG_WATCHDOG_SYSFS=y` |
| Guest 장치 | `/dev/watchdog0`, `SBSA Generic Watchdog` |
| 20초 timeout 예 | WOR 1,250,000,000 ticks, WS0 약 10초, WS1 약 20초 |

주파수와 시점은 가상 플랫폼의 counter/simulation-time 계약이며 host wall time
성능 보장은 아니다. 실제 만료 여부는 host trace로 확인한다.

- 공통 `MultiInitiatorSignalSocket`의 전달 완료 큐를 비워 과거 reset edge 재전달 방지.
- AP cold reset fanout에 NS/S watchdog reset을 연결해 WS1 원인 신호 해제.
- NS/S watchdog 입력을 독립 OR 처리하고 reset 출력은 실제 전이만 전달.
- reset 중 watchdog expiry 취소, 진행 중 MMIO write에 의한 재활성화 방지.
- WS0 진입 시 WCV를 두 번째 만료 시점으로 갱신하여 Linux timeleft 계산과 일치.
- `QBOX_APOLLO_RESET_TRACE=1`로 WS0/WS1 및 reset assert/release를 제한적으로 출력.

AP reset과 QEMU 비동기 reset completion handshake를 유지한다. 기능 변경의
단위 테스트, 실제 guest 만료, 재부팅 후 cross-domain 복구는 별도로 검증한다.
수정 모델의 runtime 결과는 검증 완료 후 아래에 기록한다.

### 모델 빌드 및 테스트 결과

`build/autosd/watchdog-model-*`에 로그/XML과 제외 목록을 보존했다.

| 검증 | 결과 |
|---|---|
| canonical provider compile | PASS |
| platform 기본 테스트 | 62/62 PASS |
| core 기본 테스트 | 60/60 PASS, 기본 제외 목록 별도 보존 |
| install / populate_sysroot | 905 tasks PASS |
| 추가 system-reset 1/2 CPU harness | 최종 reset 응답 후 sc_stop, 프로세스 종료 100초 TIMEOUT |
| 추가 CPU-reset 1 CPU harness | sc_stop 후 프로세스 종료 100초 TIMEOUT |
| 추가 system-reset 4 CPU / CPU-reset 2 CPU | 중단, PASS 아님 |
| 추가 CPU-reset 4 CPU / managed reset-release | 이번 추가 실행에서 미수행 |

추가 timeout 항목은 원래 기본 suite의 slow exclusion에 속한다. 동일한 provider
library와 test source에 **원본 HEAD 신호 header만 적용한 별도 binary**와 수정 binary를
비교했으며, system/CPU 1-CPU 두 종류 모두 sc_stop 이후 15초 종료 timeout이 재현됐다.
이는 전체 provider 원본 빌드 비교가 아니며, timeout을 PASS로 바꾸지 않는다.
Host ptrace attach는 정책상 거부되어 그 사실과 thread wait-channel 기록을 남겼다.
전역 ptrace 정책은 변경하지 않았다. 실제 AutoSD reset/recovery 결과와 구분한다.

`systemctl poweroff`/`shutdown -h now` 지원은 guest filesystem 정상 종료와
해당 런처가 소유한 QBox 프로세스 정리를 의미한다. 실제 보드의 전원 rail 제어나
SI/RSE 개별 watchdog reset qualification으로 확대 해석하지 않는다. 특히
reset controller의 별도 SI/RSE output binding과 domain별 firmware reset 정책은
AP watchdog 시험과 별개이며, 미연결 출력에 임의의 전체 reset 정책을 추가하지 않는다.

로컬 TRM의 AP WS1 interrupt는 AP SPI51 및 SI expansion ID321이다
(`doc/arm_zena_css_dev_guide/09-programmers-model-for-zena-css.md`). 기존 QVP에는
SI ID321 watchdog 전달/처리 경로가 없었다. EXTCOLDRESET bit5 설명만으로 전체
reset 범위를 결정할 수 없다. Reference `boot_process.rst`의 AP standalone reset은
SCP PPU power-cycle 및 RSE BL2 reload/ack을 거친다. 따라서 AP QEMU만 reset할 때
SCP cached power state와 PPU 상태가 유지되는 문제를 실제 WD03/WD04에서 확인해야 한다.

복구 경로(소스 구현 완료, runtime 재검증 진행 중): SI CL0의 architectural INTID321은
SCP ISR 인자도 321이며, QBox SPI socket은 `321 - 32 = 289`다. GIC multiview는
INTID를 재번호화하지 않는다. 신규 경로를 만들 경우 active-route 표와 SCP View1
소유 map에도 등록했다. 기존 SI0의 `mod_pd_restricted_api.system_shutdown(
MOD_PD_SYSTEM_WARM_RESET)`는 framework event/notification으로 AP core OFF 확인,
RSE BL2 reload, SCMI mailbox 정리, boot core ON 절차를 실행한다. CPU0 PPU의
`power_on_load`가 controller `ap_power_reset`과 AP cold fanout을 구동하므로 이번
모델의 watchdog reset 대상도 초기화된다. ISR 안에서 전체 절차를 직접 수행하지
않고 event로 넘겨야 하며, IRQ 재활성화는 실제 recovery 완료와 level 해제를 확인한
후 수행한다. CPU0 ON notification에서 pending clear/check 후 IRQ를 재활성화하며,
pending이 남아 있으면 fail-closed 처리한다. AP-only의 SPI51-only 정책은 유지한다.
`SYSTEM_COLD_RESET` API 호출만으로 RSE SCMI notification이
자동 발생한다고 가정하면 안 된다.

### 최초 실제 watchdog 만료 시험: 복구 FAIL

`build/autosd/watchdog-runtime-20260928/`에 WD01 inspect와 WD02 keepalive
증거를 보존했다. WD02는 timeout 20초, 약 10초 실행에서 feeding 전 timeleft
14/15초 → feeding 후 19/19초, disable 후 inactive를 확인했다. 최초 SSH 연결
오류는 별도로 보존했으며 실행 성공으로 계산하지 않았다.

WD03에서는 WS0 `402376665855 ns`, WS1 `412376665855 ns`와 AP reset
assert/release를 관측했지만, OS 복구는 **FAIL**이었다. 가장 먼저 실패한 지점은
secure console의 `ASSERT: lib/psci/psci_common.c:1063`이다. AP가 reset에서
빠져나와 실행했으나 유효한 PSCI warm-boot 상태 없이 재진입했고, 새 BL2/Linux
부팅은 시작하지 못했다. 이후 SI CL0가 AP 4개 core의 PFDI timeout을 보고했다.
따라서 reset 신호만으로 watchdog 복구 PASS를 선언하지 않는다.

- 증거: `build/qbox-apollo-qvp/autosd-watchdog-model-20260928/`
- 판정: `build/autosd/watchdog-runtime-20260928/expiry/host-verdict.json`
- guest boot ID: `f9673f81-e0f5-4d7b-a3f1-6d97a026e6b7` 이후 새 ID 없음
- 시험 VM은 소유 launcher에 종료 요청하여 정리했으며 디스크와 로그를 보존했다.
- SCP의 기존 standalone warm-reset 절차로 연결하는 수정을 반영했다.
  재검증 세션은 `build/qbox-apollo-qvp/autosd-watchdog-coordinated-20260928/`다.
- 수정 후 QBox compile, 플랫폼 62/62 및 core 60/60, SCP compile,
  BSP 5846 tasks(32 재실행)가 PASS다. 빌드 결과는 runtime 복구 증거와 구분한다.

### Coordinated 경로 첫 시험: ISR 계약 오류

`autosd-watchdog-coordinated-20260928` 시험에서는 WS0 `271599216131 ns`,
WS1 `281599216131 ns` 뒤 SI CL0의 ISR 진입까지 확인했다. 그러나 ISR 이벤트의
`source_id` 누락으로 `__fwk_put_event_light`가 `FWK_E_PARAM(-1)`을 반환하여
복구는 FAIL이었다. 일반 event 처리와 달리 interrupt context에서는 framework가
source ID를 자동 추론하지 않는다. 명시적 SI0 module source ID와 ISR 단위 검사를
추가했다. 실제 ISR을 호출해 source/target/event ID와 중복 enqueue 방지를 검사하는
14번째 단위 테스트를 포함하여 모두 통과했으며, BSP 5846 tasks(26 재실행)도 PASS다.
재시험 경로는 `build/qbox-apollo-qvp/autosd-watchdog-isr-fix-20260928/`다.
앞선 13개 SI0 단위 테스트는 handler/rearm 검증이었고,
실제 ISR 이벤트 생성 계약을 검증하지 않았다는 한계가 이 시험에서 드러났다.

기본 앱 건강 검사는 `AUTOMOTIVE_SCENARIO_HEALTHY_PASS`까지 통과했다.
뒤에 덧붙인 네트워크 진단은 guest에 `ip` 명령이 없어 exit 127이었으므로 해당
전체 명령을 PASS로 보고하지 않으며 HIPC 트래픽 성공을 추론하지 않는다.

ISR 수정 후 시험에서는 WS0 `209274765058 ns`, WS1 `219274765058 ns`,
SI CL0 event 처리와 AP core OFF까지 진행했다. 그러나 RSE BL2 reload 응답이
800000 us 내 오지 않아 복구는 FAIL이었다. `notify_rse_and_wait_for_response()`는
이름과 달리 전송 없이 응답 flag만 기다린다. 정상 SCMI 요청이 별도로 보내는
SYSTEM_POWER_STATE_NOTIFY를 watchdog의 직접 power-domain API 호출이 생략한
것이 원인이다. timeout을 늘리는 대신 기존 RSE 알림 절차와 연결해야 한다.
이후 SI CL1 PFDI timeout도 관측됐으며 이를 정상 상태로 숨기지 않는다.

이 경로는 watchdog에 한해 AP core OFF 확인 후 ACK flag를 먼저 초기화하고,
SCMI platform-agent(0)의 warm-reset 구독 알림을 보낸 뒤 기존 ACK를 기다리도록
보완했다. SI0만 새 알림 API에 bind할 수 있고 일반 SCMI 경로는 중복 통지하지
않는다. 전송 API는 `void`이므로 알림 dispatch 자체를 전송 완료로 간주하지 않으며
실제 ACK가 완료 증거다. 관련 native 5 target/44 case가 PASS다.

추가로 MHU3의 여러 logical channel이 같은 physical doorbell channel을 공유할 때,
channel pending만 보고 다른 flag의 callback까지 호출하는 결함을 수정한다.
masked flag 상태를 검사하고 지정 flag만 W1C로 지우는 회귀 검사를 수행한다.
SI CL1 timeout의 후속 분석에서는 800ms blocking wait가 SCP event 처리를 지연해
500ms online 감시의 timer 재설정도 늦추는 문제가 확인됐다. 실제 SI CL1 실행 중단을
증명한 것은 아니며, 정상 handshake와 이후 감시 복구는 별도로 검증해야 한다.

### 실제 RSE 응답 시간과 비동기 복구 필요성

`autosd-watchdog-notify-20260928`에서 RSE notification, AP_BL2 재적재·검증,
MHU ACK 전달은 성공했다. 그러나 동기 대기가 먼저 만료되어 OS 복구는 FAIL이었다.

| 단계 | 같은 시험의 simulation timestamp |
|---|---:|
| WS1 | 218.837027 s |
| SCP ACK 대기 시작 | 218.868927 s |
| 기존 800ms 제한 초과 | 219.672433 s |
| 실제 ACK 수신 | 222.310921 s |

측정된 응답 시간은 약 3.442초다. watchdog 경로만 비동기 ACK 대기로 바꾸고,
QVP용 reload deadline을 별도로 설정했다. 10초 recovery budget은
이번 simulation 측정의 여유를 둔 값이며 하드웨어 FTTI 충족 주장이 아니다.
SI CL1의 500ms 감시 기준은 유지한다. 응답 없는 경우 AP boot/IRQ rearm을 하지
않고 명시적으로 실패하며, 늦은 응답과 중복 이벤트도 검사한다.
10ms alarm은 실제 counter와 ACK 수신 timestamp를 비교한다. callback 횟수로
timeout을 추정하지 않으며 generation으로 이전 완료 이벤트의 재사용을 막는다.
관련 5 native target/50 case, MHU 30 case, BSP 5846 tasks가 PASS다.
런처는 SCP 복구 실패를 이전 boot marker로 덮지 않도록 판정하며 51개 회귀 검사를
통과했다. runtime 재시험은 `autosd-watchdog-async-20260928` 세션에서 수행한다.

비동기 시험에서 ACK는 3.335634초 후 도착했고, AP reset과 IRQ 재활성화
(`221.347507 s`)까지 성공했다. SI CL1 PFDI timeout은 발생하지 않았다.
그러나 AP는 다시 `psci_common.c:1063`에서 멈춰 OS 복구는 아직 FAIL이었다.
실제 BL2가 읽는 trusted mailbox `0x1ff8`에 이전 BL31 진입 주소가 남았다.
RSE의 wipe는 BL2 영역 `0x82000`부터이고 이 mailbox를 포함하지 않는다.
주소 alias 오류는 없으며, SCP `apcontext`가 소유하는 `0x1fc0–0x1fff` 64-byte
영역은 초기 부팅 때만 지워지고 있었다. AP가 OFF이고 RSE ACK를 받은 뒤에만
기존 apcontext 초기화를 재사용해야 한다. 일반 CPU hotplug마다 RAM을 지우거나
TF-A assertion을 우회하는 방식은 사용하지 않는다.

### AP context 초기화 보완: 구현·단위 테스트·빌드 경계

SCP의 기존 `module/apcontext`에 권한이 제한된 runtime reset API를 추가했다.
기본 설정은 비활성이고 Apollo QVP에서는 SI0 플랫폼만 bind할 수 있다.
초기 부팅의 알림·초기화 순서는 유지한다. Watchdog 복구에서는 모든 AP core가
OFF이고 RSE의 유효한 ACK를 받은 뒤, 기존 `apcontext_zero()`로 설정된 64바이트만
초기화한다. 이후 AP-facing SCMI mailbox 정리, SDS reset syndrome 기록,
boot CPU ON 순서로 진행한다. context 초기화가 실패하면 CPU ON으로 진행하지 않는다.

주소는 새 상수로 복제하지 않고 기존 `config_apcontext.c`와 `SI0_AP_CONTEXT_BASE`,
`SI0_AP_CONTEXT_SIZE`를 그대로 사용한다. TF-A의
`PLAT_ARM_TRUSTED_MAILBOX_BASE = ARM_SHARED_RAM_BASE + ARM_SHARED_RAM_SIZE - 8`
계약에 해당하는 `0x1ff8`이 이 영역에 포함된다. SDS와 SCMI의 다른 메모리는
context 초기화 대상이 아니며, 일반 CPU hotplug나 전체 SRAM에 적용하지 않는다.
RSE/TF-M의 매핑 변경 또는 TF-A assertion 우회도 없다.

| 검증 범위 | 결과와 증거 |
|---|---|
| Native 단위 테스트 | 6 target / 66 case PASS. context 영역 양옆 guard 보존, 초기화 준비 상태·접근 권한·기본 비활성, CPU ON 이전 초기화, 초기화 실패 시 중단 포함 |
| Native 로그 | `build/autosd/watchdog-scp-unit-20260928/build-context-fix.log`, `test-context-fix.log` |
| BSP 재빌드 | 5846 tasks 중 26 재실행, 모두 성공. 5개 warning은 빌드 요약에 보존 |
| BSP 로그 | `build/autosd/watchdog-context-bsp-20260928.log` |
| 새 이미지 runtime | `build/qbox-apollo-qvp/autosd-watchdog-context-20260928/`에서 검증 진행 중. 아직 PASS로 판정하지 않음 |

앞선 `async` 시험의 ACK·AP reset·IRQ rearm 성공은 OS 재부팅 성공을 뜻하지 않는다.
새 이미지에서 BL2/TF-A/Linux 재진입, 새 guest boot ID, AP 4 CPU와 앱 건강 상태,
재차 watchdog 만료·복구를 각각 확인해야 한다. 앞선 실패 세션과 로그는 유지한다.

## 종료 시 watchdog 경고 해석

기준선에는 `watchdog did not stop!`가 있지만 바로 뒤에 systemd-shutdown의
hardware watchdog 사용 및 10분 timeout 설정, 이후 정상 reboot가 기록됐다.
Linux `watchdog_release()`는 magic-close 없이 활성 장치를 닫으면 이 메시지를
출력하고 keepalive한다. SBSA driver는 `watchdog_stop_on_reboot()`도 등록한다.
따라서 이 문자열 하나만으로 reset 실패를 판정하거나 driver 경고를 숨기지 않는다.

systemd의 close 함수는 `disarm` 여부에 따라 disable/magic-close 수행을 구분한다.
[systemd v257 watchdog 구현](https://raw.githubusercontent.com/systemd/systemd/v257/src/shared/watchdog.c)
및 실제 guest shutdown 로그를 함께 확인해야 한다. RuntimeWatchdog 자동 활성화는
하지 않으며, 명시적인 설정과 단독 소유권 확인 후 사용한다.

## 데모 시나리오 및 판정

### Context 초기화 적용 후 실제 시험

`autosd-watchdog-context-20260928`에서 첫 만료 후 TF-A assertion이 사라지고
AP boot epoch가 1→2로 증가했다. QBox PID 709771/709793은 유지됐고 boot ID는
`9f8ab718-0cf9-4636-9581-f6e5bf556332`에서
`09770997-1b25-4682-9a2e-d1e06f24bd04`로 변경됐다. CPU 0–3, failed unit 0,
Root/QM/ADAS/BlueChi 및 Safety Monitor HEALTHY 검사는 통과했다.
다만 SCP가 이전 `WAIT_FOR_ONL`을 유지해 새 OoR status를 거부했으므로
cross-domain 상태 복구의 판정은 아직 PARTIAL이다.

후속 수정은 AP가 모두 OFF인 watchdog 복구에서만 PFDI monitor epoch를 새로
시작한다. 대기 중인 이전 epoch의 status/timeout 이벤트를 제외하고 일반 CPU
hotplug와 SI1 상태는 유지한다. 플랫폼 topology 16개와 실제 구성된 AP 감시 대상
4개를 구분하며, 실제 4개만 초기화하는 회귀 검사를 포함한 69개 native 테스트가
통과했다. 타임아웃 기준을 완화하거나 경고를 숨기지 않는다.

같은 VM에서 systemd RuntimeWatchdog=30s 시험은 약 32초 동안 7개 active 샘플과
timeleft 21–29초 갱신을 확인했다. 임시 `/run` 설정 제거 후 RuntimeWatchdog=0,
inactive, 동일 boot ID, failed unit 0으로 원복했다. 단독 건강 검사 재시험 후
`systemctl poweroff --no-block`도 전체 filesystem detach, `reboot: Power down`,
런처 `POWERED_OFF`/exit 0까지 통과했다. 첫 건강 검사는 daemon-reexec와 겹쳐
bus 연결 실패가 있었으며 단독 재시험과 구분해 보존했다.

증거: `build/autosd/watchdog-runtime-20260928/context-{expiry-1,systemd,health-final}/`.
최종 PFDI 수정 이미지의 반복 만료 및 native reboot 검증은 별도 기록한다.

### PFDI 수정 이미지: 첫 복구 PASS, 반복 IRQ와 HIPC 결함 발견

`autosd-watchdog-final-20260928` 첫 WS1은 `224318452231 ns`이며 새 boot ID
`2e30fb21-52bb-4316-a635-aba2b8d2d0ba`로 AP가 복귀했다. PFDI OoR/Onl 순서
오류는 사라졌다. 하지만 두 번째 WS1 `423157769872 ns`는 SI CL0에서 처리되지
않았다. Guest 도구는 timeout+grace 후 `NOT_OBSERVED`를 기록하고 disarm했다.
따라서 이 이미지의 반복 watchdog reset은 FAIL이다.

후속 소스 점검에서 AArch64 `arch_interrupt_is_pending()`가 pending을 읽지 않고
ICENABLER에 쓰던 오류와, IRQ enable 이후 recovery 플래그를 해제하던 경합을
수정했다. 재활성화 직후 enabled/pending/recovery를 읽기 전용 snapshot으로
기록한다. 실제 register 접근·동기 ISR 재진입을 포함한 74개 native 테스트 PASS다.
이 코드 결함들이 두 번째 WS1 실패의 직접 원인인지는 runtime 재시험으로 판단한다.

같은 AP 단독 reset 뒤 remoteproc attach는 기록됐지만 `ethsi1`이 없었다.
기존 모듈 load/PFDI startup PASS만으로 HIPC 복구를 주장할 수 없다. 실제 resource
table 및 RPMsg endpoint 재attach 상태를 추가 조사한다. Watchdog 강제 reset 뒤
journal/FAT unclean shutdown 경고도 관찰됐으며 정상 종료 시험과 구분한다.

반면 이후 native `systemctl reboot --no-block`은 동일 QBox PID 719832/719861에서
boot ID `79295c13-5025-48c1-95fa-aff99195a309`, RSE/SI CL0/SI CL1 epoch 2,
AP epoch 3, CPU 0–3, failed unit 0, 기본 앱 active, HEALTHY 및 `ethsi1` 생성까지
통과했다. 이어 `shutdown -h now`도 filesystem detach, Power down,
런처 `POWERED_OFF`/exit 0으로 종료했다.

증거: `build/autosd/watchdog-runtime-20260928/final-{expiry-2,native-reboot-after}/`.

### Rearm/HIPC 수정 이미지: 첫 AP 복구·왕복 통신 PASS, 반복 reset 미통과

`build/qbox-apollo-qvp/autosd-watchdog-rearm-20260928/`에서 첫 watchdog 만료 뒤
QBox PID 747088/747119를 유지하면서 AP boot ID가
`226072a4-0f48-4946-8f39-160a4d0fa885`에서
`6d5e2686-2799-451e-8653-e22fe7b35985`로 변경됐다.
Host 판정 파일 `rearm-after-1/host-verdict.json`의 종합 상태는 **PARTIAL**이다.

HIPC는 이전 실패와 달리 reset 후에도 resource table의 vdev entry 0,
RPMsg `virtio6.ethsi1.-1.1024` 및 `rpmsg_netdev` binding, `ethsi1` 생성을 확인했다.
QVP 전용 Zephyr 생성 모듈은 SI firmware 안의 원본 resource table을 사용하여
shared table/ring을 복구하고 memory barrier 뒤 AP attach ACK를 보낸다.
기존 worker에서 lifecycle/VQ 처리를 직렬화하고 TX와 mutex로 보호하며,
죽은 AP의 buffer를 기다리며 잠금을 유지하지 않도록 TX는 bounded trysend를 사용한다.
외부 참조 저장소 또는 FVP 원본 드라이버는 변경하지 않았다.

단순 endpoint 생성과 구분하여 실제 통신도 확인했다. 임시 VLAN 200에서
AP `192.168.1.2` → SI CL1 `192.168.1.1` ICMP request를 보내고,
checksum·주소·identifier·sequence·payload가 일치하는 reply **3/3**을 받았다.
이후 시험 UUID `0b7b10a7-89d8-42f6-bd82-a5273d84ddb7`의 임시 연결을 삭제했고,
poweroff 전 VLAN interface와 해당 profile의 부재를 다시 확인했다.
이는 **AP가 시작한 request/SI reply 왕복 PASS**이지 SI가 별도로 시작한 통신,
지속 부하 또는 반복 reset 전체 통과를 뜻하지 않는다.

원본 통신 로그의 `rtt_ms_host_monotonic` 키는 잘못된 이름이다.
30.446/14.571/4.392 ms는 **Guest Python monotonic clock** 기준으로 측정됐으며
Host/SystemC 시간이나 실제 하드웨어 latency가 아니다. 원본 로그는 보존하고,
재사용 도구 `scripts/autosd_demo/hipc_ping.py`는 `rtt_ms_guest_monotonic`으로 수정했다.
실행·임시 연결 정리 절차는 [Guest Quick Guide](autosd-watchdog-guest-ko.md)의
“Reset 이후 HIPC 왕복 통신 확인”을 따른다.

Watchdog 재활성화는 여전히 실패했다. SI0 로그의 첫 rearm attempt는
`235.754161 s`이며 `before=1 after=1 status=1`이었다. 다음 처리 이벤트는
`236.282186 s`에 도착하여 약 528.025 ms가 지났고, 기존 **100 ms** 제한을 넘겨
`Watchdog rearm FAILED after 1 attempts: -7`로 종료됐다. IRQ는 masked 상태로
남았다. SI0 GIC interrupt 321의 high/low 전달은 관찰했지만 이는 rearm 성공이
아니다. 두 번째 만료로 반복 reset PASS를 주장하지 않으며 timeout도 완화하지 않았다.

후속 모델 조사에서 CPU0 PPU의 zero-delay ON이 `+1 ps` cold-reset fanout보다
먼저 처리되는 순서 문제를 분리했다. 이전 zero-delay 설정을 그대로 실행한
negative control은 assertion failure를 재현했고, ON 처리를 **1 ns** 뒤로
순서화한 격리 회귀 시험은 두 cycle 모두 통과했다. 이 1 ns는 모델의 이벤트
순서를 보장하기 위한 값이지 물리 PPU latency 사양이 아니다. 보고서 갱신 시점에
수정 모델을 포함한 canonical BSP는 5,847 tasks(13 rerun), QBox platform
63/63 및 core 60/60 시험을 통과했다. 최종 full-system 재부팅과
반복 watchdog/HIPC 복구 결과는 아래 최종 실행 기록과 별도로 판단한다. 격리 모델 PASS로 runtime FAIL을
대체하지 않는다.

첫 `autosd-watchdog-sequence-20260928` 실행은 초기 BL31 core2 OoR 이후
core3 진입 전에 정지했다. SCP core2 OFF와 core3 PFDI timeout은 관찰했지만
TF-A affinity OFF 완료 여부는 확인하지 못했다. PPU OFF와 TF-A 상태 기록의
경쟁 가능성이 있으며, 1 ns 변경의 회귀라고 확정할 근거는 없다. 동일 산출물로
SI GIC trace 없이 재실행한 `autosd-watchdog-sequence-retry-20260928`은
4 CPU, failed unit 0, HIPC ICMP 3/3으로 초기 부팅했다. 이 실패 기록은 보존한다.
또한 1 ns 순서화는 비동기 QEMU reset 완료 handshake 자체를 증명하지 않는다.

### 최종 순서화 모델의 연속 만료 시험

실행 디렉터리: `build/qbox-apollo-qvp/autosd-watchdog-sequence-retry-20260928/`.
동일 QBox main/RSE child PID `765754 / 765775`를 유지하며 watchdog을 두 번 만료시켰다.
각 시험은 timeout 20초, `action=0`, descriptor를 열어 둔 상태에서 feeding을 중단했다.

| 항목 (SystemC 초) | 첫 만료 | 두 번째 만료 |
|---|---:|---:|
| WS0 | 221.333466790 | 477.204545378 |
| WS1 | 231.333466790 | 487.204545378 |
| watchdog reset 및 WS1 해제 | 234.657932976001 | 490.626494231001 |
| SCP IRQ321 재활성화 snapshot | 234.688004 | 490.652541 |
| snapshot | enabled=1, pending=0 | enabled=1, pending=0 |
| rearm attempt | 1회, before=0/after=0 | 1회, before=0/after=0 |

첫 reset의 boot ID는 `891c801b-d762-4df4-8908-3f6137149c53`에서
`59548459-e687-4ad1-bb06-116fa8444cb6`으로 바뀌었다. AP epoch 2에서
4 CPU, failed unit 0, Automotive health, PFDI startup 및 HIPC ICMP 3/3이
통과했다. 두 번째 reset은 AP epoch 3, boot ID
`ff965761-638d-4e32-bd9d-be504b1aef49`로 복귀했으며, 동일한 4 CPU/failed 0,
Automotive health, PFDI startup 및 HIPC ICMP 3/3을 통과했다.
따라서 **연속 2회 WS1 reset 및 AP 서비스·HIPC 복구는 PASS**다.
SSH 명령의 timeout은 reset 성공 판정값이
아니며, 위 host trace와 다음 부팅의 health를 함께 사용한다.

산출물 hash: `build/autosd/watchdog-runtime-20260928/sequence-retry-artifact-sha256.txt`.
Root focused regression은 `watchdog-final-focused-tests-20260928.log`의 96 PASS다.
Guest 검증은 `sequence-retry-{expiry-1,after-1,after-2}/console.log`에 보존했다.
두 번째 reset 후 journal의 unclean shutdown/FAT unmount 경고는 강제 reset의
결과이며 숨기지 않았다. 그 외 SMMU SID 폭, 의도적 cpuidle 비활성,
minimal initrd journal socket 부재, 외부 모듈 taint, BlueChi heartbeat 0은
부팅 성능 보고서의 기존 제한과 일치한다. failed unit과 Automotive failure는 0이었다.

이후 같은 PID에서 `systemctl reboot --no-block`를 실행하여 RSE/SI0/SI1 epoch 2,
AP epoch 4, 새 boot ID `9ab4865f-0dd9-40f5-8592-867538d8ff89`로 복귀했다.
4 CPU, failed 0, PFDI startup 및 별도 HIPC ICMP 3/3은 확인했으나,
SI1의 새 부팅에서 deferred `LOG_INF` 출력이 프롬프트 이후 나오지 않았다.
OoR/banner/timer 등 `printk` 출력은 존재하며, launcher의 SI1 marker 판정은
올바르게 WAITING을 유지했다. 따라서 이 실행의 **일반 reboot 종합 판정은 PARTIAL**이다.
단순히 이전 부팅 marker를 재사용하거나 필수 로그 검사를 제거하지 않는다.

조사에서 SI1의 SystemC PL011은 reset 입력이 없고, IRQ 갱신 함수가 mask=0일 때
기존 asserted 출력도 갱신하지 않는 것을 확인했다. GIC/CPU만 reset한 뒤 UART의
IRQ 상태가 남을 수 있으므로 UART IRQ 해제와 domain reset 연결을 추가 조사·수정한다.
증거: `sequence-retry-native-{request,si-check,health}/` 및 실행 디렉터리의 SI1 UART.
이 실행의 native reboot 후 Automotive health도 PASS였다. BlueChi agent의
controller 최초 연결 실패는 이후 자동 재연결되어 host/qm.host online으로 복구했다.
종료는 `sequence-retry-poweroff/`의 정상 poweroff 요청 후 모든 filesystem detach,
`reboot: Power down`, launcher `POWERED_OFF`, returncode 0을 확인했다.
SI1 로그 자격은 WAITING으로 남으므로 해당 이미지가 완전한 full-system PASS로
자동 선택되도록 결과를 조작하지 않는다.

### 후속 PL011 reset 수정

공통 SystemC `Pl011`에 optional reset 입력을 추가했다. assert 시 register/RX FIFO와
pending IRQ 갱신 이벤트를 초기화하고 IRQ를 내리며, reset 중 write/RX를 받지 않는다.
deassert 후 송수신을 다시 허용한다. 이미 host backend에 전달된 콘솔 출력과 로그 파일은
삭제하지 않는다. IMSC=0도 IRQ low를 구동하도록 기존 갱신 조건을 수정했다.

- AP primary/secure UART: AP cold reset(및 이를 포함하는 full reset).
- SI0/SI1 UART: full reset의 GIC/QEMU reset보다 앞.
- RSE host UART: full reset의 RSE system controller reset보다 앞.
- AP standalone watchdog reset은 SI UART를 reset하지 않는다.

`build/autosd/watchdog-uart-reset-20260928/`에 2-cycle 격리 시험과 Lua 매핑을 보존했다.
mask=0 IRQ 해제, reset 기본값/revision 보존, pending 갱신 취소, held-reset write 차단,
RX FIFO 폐기, fresh TX/RX IRQ 및 기존 backend 출력 보존을 통과했다.
이 격리 PASS는 실제 SI shell logger 복구를 뜻하지 않는다. canonical BSP와
native reboot 재검증은 후속 로그로 판정한다. PL011 포함 canonical BSP는
5,847 tasks(13 rerun), platform 64/64 및 core 61/61을 통과했다.
로그는 `build/autosd/watchdog-uart-{bsp,qbox-check,qbox-compile}-20260928.log`다.

첫 UART 수정 runtime `autosd-watchdog-uart-20260928`은 초기 4-domain 부팅과
4 CPU/failed 0을 통과했으나 native reboot에서 RSE가 protocol version 요청을
3회 실패한 뒤 `SCP is not ready. Abort`로 중단했다. SI0는 메모리 초기화 후
TPS6594 probe 진입까지 기록했다. 결과는 `UNEXPECTED_EXIT`, child SIGTERM(-15)다.
실행기는 `[ERR]` 감지 시 `stop_process()`를 호출한다
(`scripts/run/qbox_apollo_runtime.py`). 따라서 종료 시점의 `RunOnSysc unknown
exception`을 I2C/UART의 최초 원인으로 단정하지 않는다. RSE/SCP readiness와
reset 후 CPU release 순서는 추가 진단 대상이며 이 실행은 FAIL로 보존한다.

후속 소스 조사에서 BL2 version RPC가 응답을 한 번만 확인한 뒤 반환하고,
바깥의 3회 재시도가 미완료 RPC를 다시 보내려다가 BUSY로 실패하는 경로를 확인했다.
SCP transport 초기화는 RSE mailbox를 FREE/length=0으로 초기화하므로 이보다
먼저 보낸 요청도 유실될 수 있다. bulk SRAM clear와 이 mailbox 초기화는 구분한다.
QVP BL2에 한해 single-outstanding RPC를 실제 SYSTIMER0 counter 기준으로
기다리고, FREE/length=0 초기화가 확인될 때만 재전송하는 수정을 진행한다.
FREE/nonzero response와 doorbell 사이의 경합에서는 재전송하지 않는다.
10초 제한은 관찰된 수 초의 SCP 초기화를 포함하는 QVP 기능 시험용 준비 예산이며
물리 startup/FTTI 보장이 아니다. 기존 runtime SCMI와 다른 power RPC는 유지한다.

동일 UART 산출물의 `autosd-watchdog-uart-retry-20260928`은 초기 부팅 및 native
reboot의 RSE 준비 단계를 통과했다. boot ID는
`55d6dedd-e894-4c1b-8be5-5e9b25e90b76` → `38acc848-dd06-4751-a23a-8c7f904fadcb`다.
4 CPU, failed 0, Automotive health와 HIPC ICMP 3/3이 통과했지만 SI1 epoch 2의
deferred 로그는 다시 누락됐다. 즉 PL011 수정은 확인된 모델 결함을 고쳤으나
이 로그 증상의 충분한 해결책은 아니며 전체 marker 판정은 WAITING이다.
Zephyr logger는 초기 로그가 threshold 10개보다 적을 때 1초 timer로 깨어난다.
따라서 event-driven HIPC 성공만으로 SI1 tick/timer 생존을 증명하지 않는다.
현재는 타이머 ISR/지연 work 진행을 후속 진단 대상으로 좁혔다.

### readiness 수정 및 SI1 후속 진단

`watchdog-readiness-final-bsp-20260928.log`는 5,847 tasks(78 rerun) PASS다.
SCP는 mailbox 초기화에서 BUSY를 먼저 게시하고 내용을 초기화한 후 barrier와 함께
FREE를 마지막에 게시한다. TF-M QVP BL2는 실제 timer deadline 안에서 단일 RPC를
유지하며 시작 전 BUSY 경합과 초기화에 의한 요청 소실을 구분한다. SCP native
101 cases와 TF-M readiness 17 cases가 통과했다. 기존 강제 task에 관한 taint
경고 5개는 빌드 로그에 보존했다.

`autosd-watchdog-readiness-20260928`의 초기 부팅 및 native reboot는 모두 RSE
readiness를 통과했다. AP boot ID는 `133e99bf-8c38-4778-affa-000517441d6e`에서
`03b1c242-5352-467f-9cd3-87d81c0e4397`로 변경됐다. SI1 deferred 로그 누락은
남았으므로 전체 marker 판정은 WAITING을 유지한다.

후속 관측으로 **SI1 전체 timer 정지 가설은 배제**했다. 재부팅 뒤 네 CPU의
CNTV/PPI27 전환과 compare 갱신을 trace에서 확인했고, SI shell에서 1초 간격으로
시작한 두 ICMP 요청 모두 AP 응답을 받았다(guest RTT 42.40/4.67 ms). shell 및
타이머 기반 지연 작업이 동작한다는 증거이며 logger 정상화 증거는 아니다.
`watchdog-runtime-20260928/readiness-si1-timer.log` 및 해당 VM의 SI1 UART 로그에
보존했다.

실제 Zephyr bin(287,156 bytes)을 사용하는 격리 loader 시험에서도 semaphore,
filter, timestamp 영역을 오염시킨 후 두 번의 reload마다 전체 이미지가 복원됐다.
`watchdog-loader-reload-20260928/{run.sh,test.log,reload.cc}` 참조. 이는 실제
플랫폼에서 PPU가 올바른 순서로 loader를 호출했다는 증거까지는 아니므로 runtime
reload 순서와 logger 상태는 별도 확인 대상으로 남긴다.

최신 root focused 회귀는 `watchdog-readiness-focused-tests-20260928.log`의
114 PASS다. 기존 시험 96개와 겹치므로 합산하지 않는다. Paramiko의 TripleDES
deprecation 경고 2개는 host Python 의존성 경고이며 guest watchdog 실패가 아니다.

같은 readiness 실행에서 native reboot 뒤 두 번 연속 watchdog 만료도 확인했다.
QBox main/RSE PID는 828246/828265로 유지됐다.

| 단계 | AP boot ID | WS0 / WS1 (SystemC 초) | 결과 |
|---|---|---|---|
| native reboot 후 | `03b1c242-5352-467f-9cd3-87d81c0e4397` | — | 4 CPU, failed 0, Automotive health, HIPC 3/3 |
| watchdog 1회 후 | `bd40ab37-49d7-4580-9cb7-f4a96f11fdf6` | 968.253500274 / 978.253500274 | 동일 기능 검사 PASS; IRQ rearm before=0/after=0 |
| watchdog 2회 후 | `c040364e-39a0-4187-a0cf-d888ade4d191` | 1230.250855372 / 1240.250855372 | 동일 기능 검사 PASS; IRQ rearm before=0/after=0 |

마지막 `systemctl poweroff --no-block`에서 모든 filesystem/device detach와
`reboot: Power down`, launcher `POWERED_OFF`, exit 0을 확인했다. 전체 domain
marker는 SI1 로그 누락 때문에 WAITING으로 보존한다. 증거는
`watchdog-runtime-20260928/readiness-{expiry-1-retry,expiry-2,after-2-poweroff}`다.
expiry SSH timeout 124는 reset 후 연결 단절과 별개로 기록하며, reset 판정은
WS1/reset trace 및 이후 새 boot ID에 근거한다. 최초 `readiness-expiry-1`은
non-executable 임시 shell script 직접 호출 때문에 rc126으로 중단됐고 watchdog을
열지 않았다. 이후 `bash` 명시 호출로 재실행했다.

실행 도구의 추가 회귀는 `watchdog-readiness-final-tool-tests-20260928.log`의
132 PASS다. 연속 stdout 출력 시에도 deadline을 확인하고 SFTP 및 SSH channel
요청을 제한하며, HIPC 임시 UUID 삭제 오류는 명시적 실패로 반환한다.

### SI 외부 reset hold 순서 보강

소스상 QEMU instance reset 완료의 `resume_all_vcpus()`는 CPU의 stop/stopped를
해제한다. 외부 PPU가 유지하는 reset hold와 instance reset 완료를 구분하기 위해,
managed `start_in_reset` CPU의 reset assertion에서 BQL 보호 아래
`soft_stopped=true`를 확립하고 명시적인 release 경로에서만 해제하도록 보강했다.
SI reset fanout도 모든 SI PPU reset을 해당 QEMU instance reset보다 앞에 배치했다.
MMIO가 같은 QEMU에서 발생할 수 있으므로 assertion에서 async reset 완료를 기다리는
방식은 사용하지 않는다. managed=false인 기존 경로는 이 보강의 대상이 아니다.

실제 QEMU 4 CPU 진단에서는 3 CPU를 hold하고 나머지 witness CPU의 instance-reset
재진입을 관찰한 뒤 release하는 7회 기능 단계를 통과했다. 다만 **이전 header도
같은 기능 단계를 통과했고 양쪽 모두 sc_stop 후 teardown timeout(124)**이 발생했다.
따라서 결정적 음성 대조 또는 전체 프로세스 PASS로 보고하지 않는다. 새 진단 모드는
opt-in이며 기본 CTest에 추가하지 않았다. 증거는
`watchdog-si-held-reset-20260928/{fixed.log,old.log,run.sh}`다.
이 보강이 실제 SI1 deferred log 누락을 해결하는지는 후속 native reboot로 판정한다.

수정본 canonical BSP는 `watchdog-held-reset-bsp-20260928.log`에서 5,847 tasks
(13 rerun) PASS, platform 64/64 및 core 61/61 PASS다. 상세 테스트 로그는
`watchdog-held-reset-qbox-check-20260928.log`에 별도 보존했고 정적 매핑은
`watchdog-si-held-reset-20260928/full-map.json`의 95/95 PASS다.

디스크 여유 때문에 `autosd-watchdog-held-reset-20260928`은 정상 종료된 readiness
시험의 **동일한 가변 private disk inode를 hard link로 이어 사용**한다. 두 디스크
이름은 독립 snapshot이 아니다. 원본 nightly/prepared 이미지와 이전 로그는
변경하지 않는다. 재현용 continuation harness는
`watchdog-runtime-20260928/continue-private-runtime.py`이며 canonical
`run_qbox_yocto.sh` 및 기존 AutoSD epoch supervisor를 사용한다. 새 실행의
`launch.json`에 이 관계와 ESP 검사 receipt를 기록한다.

수정본의 첫 native reboot는 AP boot ID
`2ab2c78e-dccc-4fbc-b4b8-7bfbf391fa27` →
`6d6bb2c1-c27e-4a22-896a-5918fd51b189`로 전환됐고, RSE/SI0/SI1/AP epoch 2,
모든 domain marker 및 provisioning PASS를 확인했다. 이전에 누락된 SI1의
PFDI Agent/service, network 설정 및 RPMsg ATTACHED 로그가 모두 다시 출력됐다.
RSE/AP flash, SI0/Zephyr bin의 SHA-256은 readiness 시험과 동일하다. 이번 비교는
QBox CPU hold 및 reset 순서 보강을 함께 적용한 결과이며, 두 변경 각각의 독립적인
기여도 또는 모든 scheduling 순서의 안전성을 증명한 시험은 아니다.
`held-native-request`와 `held-expiry-1`에서 4 CPU, failed 0, Automotive HEALTHY,
HIPC ICMP 3/3도 확인했다. 프로세스 PID는 main 853354 / RSE 853379다.

추가 시험에서 watchdog WS1 두 번 모두 AP reset·IRQ rearm과 4 CPU, Automotive
health, HIPC 3/3 복구를 통과했다. AP boot ID는
`a09e4e01-9fcc-4873-aefc-f96ab2ddff9c`,
`ccb624bd-1ec2-456b-8576-ee729ecfb672`로 각각 변경됐다.
그러나 이후 두 번째 native reboot(SI epoch 3, AP epoch 5)에서 SI1 deferred
로그 누락이 다시 발생했다. shell `help`와 네 CPU OoR 출력은 살아 있고 loader는
1035.140847688 SystemC 초에 실제 reload를 기록했다. 따라서 CPU hold 보강을
로그 문제의 충분한 해결책으로 판정하지 않는다. 전체 domain PASS를 기다리던
자동 종료는 취소하고 AP provisioning 완료를 별도로 확인해 진단했다. AP epoch 5의
boot ID는 `c2a323a9-893b-4478-a6ed-13ff127bf4a8`이며, 4 CPU, failed unit 0,
Automotive HEALTHY 및 HIPC ICMP 3/3을 통과했다. `held-partial-shutdown/`에
journal과 SBSA inactive/RuntimeWatchdog=0 상태를 보존한 뒤 `shutdown -h now`로
정상 종료했다. launcher는 POWERED_OFF/returncode 0, SI1 marker는 WAITING이다.
내부 logger 상태 확인 전 전체 reboot qualification은 PARTIAL이다.

### SI1 로그 필터 초기화 경쟁 조건 확인

`autosd-watchdog-logger-live-20260928`에서 초기 부팅 후와 첫 native reboot 후를
bounded GDB로 비교했다. 초기 entry breakpoint 없이 loopback GDB server만 열고,
부팅 이후 전체 QEMU/SystemC pause 기능으로 짧게 읽은 뒤 detach했다. 이 실행은
debugger가 timing에 영향을 줄 수 있는 진단 증거이며 일반 부팅 성능 결과가 아니다.
앞선 `autosd-watchdog-logger-debug-20260928`은 부팅 중 attach 후 RSE readiness
실패로 종료됐으므로 정상 부팅 자격에 포함하지 않는다.

| 상태 | 정상 | 로그 누락 reboot |
|---|---|---|
| logger thread / semaphore | 정상 대기, buffered=0 | 정상 대기, buffered=0 |
| shell backend | active, level=4 | active, level=4 |
| PFDI/network runtime filters | `0x1b` | `0x0` |
| shell MPSC write/read index | 54/54 | 0/0 |

`logger-live-{healthy,reboot-early,reboot}.gdb.log`에 원본을 보존했다. 실패 상태에서
로그는 logger queue를 통과했지만 shell로 전달되지 않았다. Zephyr의 backend ID가
비동기 logger thread에서 할당되므로 shell이 먼저 실행되면 초기 ID 0(aggregate
filter slot)을 사용한다. 필터 계산이 backend slot 1부터 최대값을 검색해 aggregate를
0으로 다시 쓰며, 나중에 ID가 1이 되어도 autostart=false인 shell 필터는 복구되지 않는다.
정상/실패의 scheduling 차이와 위 snapshot이 일치한다. 실제 loader 재적재는 SI core
ON보다 12.46초 앞에 완료됐으며 OS 실행 후 추가 load는 없었다.

owned Zephyr submodule의 backend ID 할당을 동기식 `log_core_init()`으로 이동했다.
frontend-only 예외와 backend 개수 assertion을 보존하며 timer/priority 지연이나
필수 marker 삭제로 우회하지 않는다. `tests/test_zephyr_log_backend_init.py`는
실제 runtime filter 함수로 늦은 ID의 filters=0을 재현하고, 조기 ID의 shell-first와
logger-first 모두 `0x1b`, 다중 backend `0x9b`, frontend-only 미변경을 검사한다.
회귀 2 PASS이며 HIPC 관련 시험을 포함한 별도 묶음은 17 PASS다.

canonical BSP는 `watchdog-logger-fixed-bsp-20260928.log`에서 5,847 tasks
(35 rerun) PASS, 최종 소스 동결 후 같은 명령의 `watchdog-logger-fixed-stable-bsp-20260928.log`는
5,847 tasks 모두 재실행 불필요/PASS로 소스·signature 안정을 확인했다.
최종 root focused 묶음은 `watchdog-logger-final-focused-tests-20260928.log`의
122 PASS다(기존 132개 묶음과 다른 선택이며 합산하지 않음).
비-debug 반복 reboot 결과가 확인되기 전에는 해결 완료로 판정하지 않는다.

수정본 첫 비-debug 실행 `autosd-watchdog-logger-fixed-20260928`은 **FAIL**이다.
Zephyr 재링크로 `__start`가 `0x14000647c`에서 `0x1400064a4`로 이동했으나
SI CL1 Lua의 RVBAR가 이전 주소에 고정돼 있었다. SI OoR/banner는 없고 SCP는
SI PFDI timeout을 기록했다. AP 자체는 부팅해 정상 poweroff했다. watchdog 또는
native reboot 시험은 시작하지 않았다. launcher에서 입력 ELF를 기준으로 진입 주소를
결정하도록 수정한 뒤 새 실행에서 다시 검증하며, 이 실패를 logger 기능 PASS로
취급하지 않는다.

후속 full runner는 `--si-cl1-symbols` ELF64/AArch64의 `e_entry`를 읽어 네 SI CPU의
RVBAR 기본값에 적용한다. 명시적 CPU별 override는 보존하고 유효 범위/정렬을 검사한다.
ELF와 bin의 allocated section bytes를 대조하며 정상 objcopy gap padding은 제외한다.
Zephyr 후처리 `.image_crc`는 기존 patcher와 같은 CRC32 규칙으로 검증한다. 오류 시
옛 주소로 fallback하지 않고 부팅을 차단한다. 실행 전 `full-system/si-cl1-boot.json`과
최종 result에 주소·입력 SHA·override provenance를 기록한다. dry-run은 NOT_EVALUATED,
build-only는 SKIP이며 부팅 증거가 아니다.

실제 수정본은 entry `0x1400064a4`, 35 allocated sections, CRC 검사 PASS이고
ELF SHA-256 `6bd9ccbd4b43701ac1f6f99ee3774e1a90c7d68deadbcca7afe3c1bb0cdf524b`,
bin SHA-256 `fa2b9ce9661834a7bff2f3b7d12678ee4f5731e837f5b3a30c5d6ddedb95b6df`다.
entry focused 20개를 포함한 launcher 회귀 두 묶음은 76/78 PASS다. 이전 root 묶음과
일부 겹치므로 합산한 고유 테스트 개수로 보고하지 않는다.
`autosd-watchdog-entry-fixed-20260928`에서 새 비-debug 연속 시험을 수행했다.
CRC 정상/손상/필드 위치 회귀를 추가한 entry 전용 시험은 17 PASS다.
Zephyr logger·entry·AutoSD Guest 실행/재연결/watchdog/launcher를 묶은 최종 집중
시험은 `watchdog-entry-final-focused-tests-20260928.log`의 **139 PASS**다.

### 최종 비-debug 연속 시험: PASS

동일 QBox main/RSE PID `878747 / 878783`를 유지하며 다음 순서를 통과했다.
각 행에서 네 domain marker 및 해당 AP epoch provisioning PASS, AP 4 CPU,
failed unit 0, Automotive HEALTHY/failures=0, HIPC ICMP 3/3과 임시 VLAN 삭제를 확인했다.

| 단계 | AP / RSE·SI epoch | AP boot ID |
|---|---|---|
| 초기 부팅 | 1 / 1 | `126b62af-ed70-4b07-bc8c-ea78825d3c8c` |
| native reboot 1 | 2 / 2 | `957c4a58-84d2-4608-b513-46c524a1ffbe` |
| watchdog WS1 1 | 3 / 2 | `a7d65451-ed40-4850-8673-586ecf5ed0b1` |
| watchdog WS1 2 | 4 / 2 | `4c18d7c4-604f-4c51-aa56-8d2178287e3f` |
| native reboot 2 | 5 / 3 | `f1e9bc62-bfab-4b34-aae5-f9d9d230d654` |

| 실제 host trace (SystemC 초) | 만료 1 | 만료 2 |
|---|---:|---:|
| WS0 assert | 542.282409962 | 793.272159816 |
| WS1 assert | 552.282409962 | 803.272159816 |
| reset으로 WS0/WS1 clear | 555.803118200001 | 806.686396838001 |
| IRQ rearm snapshot | 555.834617 | 806.717784 |
| IRQ 상태 | enabled=1, pending=0 | enabled=1, pending=0 |
| 재활성화 | attempt=1, before=0, after=0 | attempt=1, before=0, after=0 |

마지막 `shutdown -h now`는 모든 filesystem/device detach, `reboot: Power down`,
launcher `POWERED_OFF`, returncode 0, 최종 domains PASS로 종료됐다. main/RSE PID가
사라지고 시험 SSH 2244 및 debugger 12342 listener가 없음을 확인했다.
최종 실행에는 debugger 연결이나 새 QBox process로의 대체 reboot가 없다.

증거 (`build/autosd/watchdog-runtime-20260928/` 기준):

- `logger-fixed-sequence-verdict.json`: 각 단계 및 정상 종료 종합 PASS.
- `logger-fixed-epoch-{1..5}.json`: 새 epoch별 domain/provision 판정.
- `logger-fixed-{native-1,expiry-1,expiry-2,native-2,final-shutdown}/`: Guest 원본 로그.
- `entry-fixed-{watchdog,rearm}-trace.txt`: 실제 WS0/WS1/reset/IRQ 증거.
- `entry-fixed-processes-after-{wd2,native2}.txt`: 동일 host PID 확인.
- `logger-fixed-artifacts.sha256`, `entry-fixed-source-sha256.txt`: 산출물과 핵심 소스 hash.

`watchdog-entry-fixed-sequence-20260928.log`는 전체 실행 로그다. expiry의 SSH rc124는
reset에 따른 연결 단절 후 deadline이며, 위 host trace 및 다음 부팅 검증을 합쳐 PASS로
판정한다. native reboot 뒤 SI1 로그 누락은 이번 두 차례 시험에서 재발하지 않았다.
이 결과는 장시간 stress나 모든 reset interleaving, 물리 timing/ASIL 자격은 아니다.

마지막 journal에는 기존 SMMU SID 폭, 의도적 cpuidle 비활성, 최소 initrd의 journal
socket 부재, 외부 모듈 taint, 강제 reset 이후 FAT unmount 경고, BlueChi 최초 연결
재시도/heartbeat 비활성 경고가 남아 있다. 이후 BlueChi host/qm.host online과 앱 HEALTHY를
확인했다. PFDI 주기 coalesced 경고도 UART에 보존하며 실시간 주기 보장으로 해석하지 않는다.
대시보드 서버는 별도 재시작 승인이 없어 기존 프로세스를 유지했다. 새 서버 API의 실제
재시작·브라우저 검증은 이 CLI/full-system 시험 결과에 포함하지 않는다.
최종 `./run_qbox_autosd.sh --dry-run`은 최신 전체 PASS 및 정상 poweroff 이미지로
`autosd-watchdog-entry-fixed-20260928/rootfs.wic`을 자동 선택했다. 증거는
`build/autosd/watchdog-default-launch-dry-run-20260928.json`이며, 이 dry-run을 추가
부팅 시험으로 세지 않는다.

재빌드 공간 확보를 위해 이번 작업의 종료된 실패 trial
`autosd-watchdog-uart-20260928/rootfs.wic`만 별도 filesystem의
`/tmp/apollo-autosd-watchdog-archive.Y23fKU/rootfs.wic`으로 이동하고 기존 위치에
symlink를 남겼다. 이동 전후 SHA-256은 `archived-uart-rootfs.sha256`으로 일치 확인했다.
원본 nightly/prepared 이미지와 로그는 변경하지 않았다. 이 보관 위치는 `/tmp`이므로
장기 보존 대상으로 간주하지 않으며, 복구가 필요하면 링크 대상 파일을 다시 옮길 수 있다.
최종 시험 후 같은 원칙으로 종료된 `autosd-watchdog-gic-20260928/rootfs.wic`도
같은 보관소의 `gic-rootfs.wic`으로 이동하고 `archived-gic-rootfs.sha256`으로 검증했다.
두 과거 trial의 데이터는 삭제하지 않았으며 최종 성공 디스크는 원래 위치에 유지한다.

| 증거 | 경로 (`build/autosd/` 기준) |
|---|---|
| 첫 reset 전후 boot ID·실제 resource table | `watchdog-runtime-20260928/rearm-{expiry-1,after-1}/console.log` |
| 종합 PARTIAL 및 rearm 시간 | `watchdog-runtime-20260928/rearm-after-1/host-verdict.json` |
| 3/3 ICMP·연결 삭제 | `watchdog-runtime-20260928/rearm-hipc-traffic/{console.log,result.json}` |
| cleanup 재확인·poweroff 명령 | `watchdog-runtime-20260928/rearm-poweroff/{console.log,result.json}` |
| SI0 interrupt high/low | `watchdog-runtime-20260928/rearm-si0-gic.log` |
| 실제 사용 artifact hash | `watchdog-runtime-20260928/rearm-artifact-sha256.txt` |
| zero-delay negative control FAIL | `watchdog-ppu-sequence-20260928/negative-control.log` |
| 1 ns 순서화 격리 2-cycle PASS | `watchdog-ppu-sequence-20260928/test.log` (`ClearsWs1BeforeCpuReleaseAndPowerOnTwice`) |
| 격리 시험 재현 명령·매핑 | `watchdog-ppu-sequence-20260928/{run.sh,full-map.json}` |

SI0 원본 시간 로그는 full-system runtime 디렉터리의
`full-system/qbox-safety-island-cl0.log`에 보존했다. 앞선 final/gic/rearm 실패
기록과 negative control은 삭제하거나 성공 결과로 덮어쓰지 않는다.

| ID | 실행 | 필요한 증거 |
|---|---|---|
| WD01 | `watchdog-guest.py inspect` | SBSA identity, inactive, nowayout=0; 장치를 열지 않음 |
| WD02 | `keepalive --timeout 20 --duration 30` | ioctl 성공, timeleft 범위, 종료 후 inactive, boot ID 유지 |
| WD03 | `expiry --timeout 20 --acknowledge-reset` | 실제 WS0/WS1 trace, AP reset assert/release, 새 boot ID |
| WD04 | WD03 후 상태 검사 | AP 4 CPU, QM/ADAS/Safety Monitor, HIPC/PFDI 재연결 |
| P01 | `systemctl reboot --no-block` 반복 | 동일 host PID, 새 boot ID, RSE/SI/AP 새 boot epoch |
| P02 | `systemctl poweroff --no-block` | filesystem unmount, Power down, 소유 QBox 정상 정리 |
| P03 | Power on 후 `shutdown -h now` | 기본 앱 자동 시작 및 정상 종료 경로 |

WD03은 guest 명령 종료 코드로 PASS를 결정하지 않는다. 실제 reset이면 SSH 연결이
끊기며 최종 guest result.json이 없을 수 있다. Host 로그와 다음 부팅 증거를 합쳐
판정한다. 디스크 쓰기를 중단하고 private 실행 복사본에서만 수행한다.

```sh
# Host: default prepared image의 private 복사본으로 부팅 및 reset trace 보존
./run_qbox_autosd.sh --reset-trace

# Guest: explicit diagnostics 설치 후, 각 output은 새 디렉터리를 지정
python3 /usr/libexec/apollo/watchdog-guest.py inspect --output /var/tmp/wd01
python3 /usr/libexec/apollo/watchdog-guest.py keepalive \
  --timeout 20 --duration 30 --output /var/tmp/wd02
# 작업/데이터 저장을 마친 뒤에만 실행: AP reset 및 SSH 단절 예상
sync
python3 /usr/libexec/apollo/watchdog-guest.py expiry \
  --timeout 20 --acknowledge-reset --output /var/tmp/wd03
```

기본 부팅에서 watchdog 만료 데모를 자동 실행하지 않는다. systemd와 데모 프로그램이
동시에 장치를 소유하지 않도록 한다. RuntimeWatchdog 설정은 Guest Quick Guide의
별도 opt-in 절차를 따르며, CPU 정지/Pause 중의 시간 모델을 실제 하드웨어 watchdog
동작으로 간주하지 않는다.
