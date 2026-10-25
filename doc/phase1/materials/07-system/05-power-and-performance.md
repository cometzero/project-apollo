# 07.5 Power와 performance — PSCI, SCMI, PPU, DVFS

[전체 목차](../README.md) · [상위 장](../07-system-software-core.md) · [이전: 07.4 Watchdog과 AP recovery](04-watchdog-and-recovery.md) · [다음: 07.6 PFDI와 core별 monitoring](06-pfdi-and-monitoring.md)

**이 문서의 질문:** OS의 policy가 실제 resource state로 바뀌려면 어떤 firmware가 협력하는가? CPU state transition과 operating point 변경을 서로 다른 요청 흐름으로 읽는다.

## 1. Power management: 정책과 실행 주체를 분리하기

![Arm Power and performance control](../figures/reference/power_and_performance_control.drawio.svg)

[draw.io 편집 원본](../figures/reference/power_and_performance_control.drawio)

[Arm 원본 SVG](../../../../arm-zena-css/documentation/images/power_and_performance_control.svg)

*출처: Arm [power_and_performance_control.rst — Architecture, CPUIdle Design, CPUFreq Design](../../../../arm-zena-css/documentation/design/power_and_performance_control.rst).*

**그림 읽는 순서:** Linux에서 시작하는 두 경로를 따로 따라간다. CPUIdle·CPU hotplug는 PSCI를 통해 CPU 실행 상태를 바꾸고, CPUFreq는 SCMI Performance protocol로 실행 중인 cluster의 operating point를 바꾼다. 두 경로 모두 최종 platform 제어를 SCP가 맡지만 entry point와 완료 조건이 다르다.

### 1.1 CPU power state와 performance level의 차이

| 항목 | CPUIdle / CPU hotplug | CPUFreq / DVFS |
|---|---|---|
| Linux의 판단 | 언제 CPU를 쉬게 하거나 offline으로 둘 것인가 | 현재 workload에 어느 frequency가 필요한가 |
| firmware interface | PSCI → TF-A → SCMI Power Domain | Linux SCMI → SCMI Performance |
| SCP 실행 | power-domain state machine → PPU | `scmi_perf` → `dvfs` → clock·PSU |
| 완료 의미 | 해당 CPU/cluster 상태 전환·wakeup 조건 | target operating point 전환·응답 |
| 타이밍 관련 항목 | entry/exit latency, wake source, timer retention | voltage settling, clock change, retry alarm |

CPU를 끈 상태에서 단순 register read가 성공한다고 CPU_ON이 완료된 것은 아니다. Reset vector, boot mailbox, interrupt controller 상태, secondary entry 실행까지 맞아야 한다. 반대로 CPUFreq는 CPU를 다시 boot하는 작업이 아니며 SCMI domain ID와 Linux policy에 속한 CPU 집합이 맞아야 한다.

PSCI CPU_ON 요청의 책임은 다음처럼 나뉜다.

1. Linux가 대상 MPIDR과 entry context를 PSCI로 요청한다.
2. TF-A는 허용되는 CPU 상태인지 검사하고 secondary warm entry를 준비한다.
3. [TF-A SCMI power backend](../../../../hsoc-stack/components/primary_compute/trusted-firmware-a/drivers/arm/css/scp/css_pm_scmi.c)가 SCP에 power-domain 전환을 요청한다.
4. SCP의 [power-domain configuration](../../../../hsoc-stack/components/system_mgmt/scp-firmware/product/automotive-rd/apollo-qvp/si0_ramfw/config_power_domain.c)과 platform driver가 parent/child 순서 및 PPU 제어를 수행한다.
5. 대상 core가 TF-A warm path를 거쳐 Linux secondary entry에 진입한다. 이후 PFDI monitor도 해당 core의 새로운 boot 상태를 추적한다.

### 1.2 DVFS 요청 한 번이 통과하는 계층

예를 들어 Linux governor가 2.0 GHz를 요청하면 kernel은 policy limit와 지원 operating point를 확인하고 SCMI Performance level을 보낸다. SCP는 domain을 DVFS element에 연결하고 clock·PSU API를 호출한다. Frequency를 올리는 방향에서는 충분한 voltage를 먼저 확보해야 하며, 낮추는 방향에서는 frequency를 먼저 낮추는 것이 일반적인 sequencing 요구다. 구체적인 순서는 [SCP DVFS module](../../../../hsoc-stack/components/system_mgmt/scp-firmware/module/dvfs/src/mod_dvfs.c)이 담당한다.

[Apollo `config_dvfs.c`](../../../../hsoc-stack/components/system_mgmt/scp-firmware/product/automotive-rd/apollo-qvp/si0_ramfw/config_dvfs.c)는 1.8/2.0/2.5 GHz와 750/850/950 mV를 선언하고, 각 domain에 `clock_id`, `psu_id`, `alarm_id`를 연결한다. 이 수치는 reference demonstration용이며 silicon 전력·주파수 특성을 측정한 결과가 아니다. Timer alarm은 clock/PSU 완료를 기다리거나 재시도하는 과정에도 쓰인다.

**Apollo에서의 적용 범위:** [현재 Linux DTS](../../../../hsoc-stack/components/primary_compute/linux/arch/arm64/boot/dts/hsoc/apollo-qvp.dtsi)는 architectural WFI를 기본으로 하고 PSCI CPU/cluster idle을 opt-in으로 둔다. 따라서 reference 그림에 deep idle 경로가 있다는 사실만으로 현재 실행에서 power-down/wakeup이 수행되었다고 해석하지 않는다. [SCMI performance configuration](../../../../hsoc-stack/components/system_mgmt/scp-firmware/product/automotive-rd/apollo-qvp/si0_ramfw/config_scmi_perf.c)의 fast-channel 항목도 build option 조건부이다.

## 2. DVFS의 synchronous API와 asynchronous completion

[SCP `mod_dvfs.c`](../../../../hsoc-stack/components/system_mgmt/scp-firmware/module/dvfs/src/mod_dvfs.c)의 `dvfs_handle_set_opp()`는 현재 voltage와 요청 OPP를 비교한다. 상승은 PSU voltage를 먼저 바꾸고 clock rate를 올리며, 하강은 clock rate를 먼저 낮추고 voltage를 내린다. Platform API가 즉시 완료하면 같은 경로에서 다음 단계로 진행하지만, `FWK_PENDING`이면 response event 이후 계속한다.

`dvfs_handle_psu_set_voltage_resp()`와 clock response 처리 함수는 이러한 중간 상태를 이어받는다. `mod_dvfs_process_event()`는 요청 event와 PSU/clock response event를 분리해 dispatch한다. 따라서 `set_rate()` 호출 로그만으로 request 전체가 완료되었다고 판단할 수 없다.

| 시나리오 | 먼저 끝나야 하는 작업 | 다음 작업 | 관측할 실패 |
|---|---|---|---|
| 낮은 OPP → 높은 OPP | voltage 확보 | clock 상승 | PSU failure/pending 미완료 |
| 높은 OPP → 낮은 OPP | clock 하강 | voltage 감소 | clock failure/pending 미완료 |
| Startup OPP 동기화 | 실제 voltage 확인 | 알맞은 frequency 설정 | cached OPP와 실제 resource 차이 |
| 새 요청과 진행 중 요청 | request/pending state 확인 | 허용되는 다음 transition | busy·지연 response·잘못된 domain |

OPP의 frequency unit과 clock API unit도 중요하다. 현재 code는 OPP frequency를 `FWK_KHZ`로 곱해 clock API에 전달한다. MHz로 읽은 문서 숫자를 그대로 register/API 인자로 쓰지 않고 source의 단위 계약을 확인한다.

## 3. Power transition이 Timer·PFDI와 공유하는 state

CPU OFF에서는 그 CPU의 Online report가 멈추는 것이 정상이다. PFDI monitor가 OFF notification을 받아 alarm을 중지하지 않으면 정상 hotplug를 fault로 판단할 수 있다. ON에서는 새 boot timeout과 report가 필요하다. CPUIdle에서도 선택 state가 timer와 interrupt context를 보존하는지에 따라 wakeup 준비가 달라진다.

현재 QVP 기본 WFI와 opt-in PSCI idle을 분리해 시험해야 하는 이유다. `cpufreq` policy 값, SCMI response, SCP resource state, 실제 model 동작은 서로 다른 관측값이다. 이 문서는 software control 계약을 설명하며 실제 전압·주파수에 따른 전력/성능 수치를 검증하지 않는다.

---

[전체 목차](../README.md) · [상위 장](../07-system-software-core.md) · [이전: 07.4 Watchdog과 AP recovery](04-watchdog-and-recovery.md) · [다음: 07.6 PFDI와 core별 monitoring](06-pfdi-and-monitoring.md)
