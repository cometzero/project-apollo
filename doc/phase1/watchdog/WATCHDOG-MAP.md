# Watchdog 주소·배선·구현 상세표

[세미나 본문](README.md) · [근거 소스](SOURCES.md)

기준은 현재 source의 **full-system 기본 Lua descriptor**다. AP 4 / SI CL0 1 / SI CL1 4 / RSE 1 CPU 구성이며, 실제 launcher override·guest 실행 결과와 구분한다. `SPI n`은 zero-based 소켓 번호, `INTID = n + 32`다. NVIC IRQ에는 이 변환을 적용하지 않는다.

## 1. Platform watchdog 5개

| Subsystem / object | Control base | Refresh base | Lua aperture / frame | Clock |
|---|---|---|---|---|
| AP NS / `ap_watchdog_0` | `0x1A420000` | `0x1A430000` | 각각 64KiB | 125MHz |
| AP S / `ap_secure_wdog` | `0x1A460000` | `0x1A470000` | 각각 64KiB | 125MHz |
| SI CL0 / `si_cl0_watchdog` | `0x2A700000` | `0x2A710000` | 각각 64KiB | 125MHz |
| RSE NS / `rse_watchdog_ns` | `0x48040000` | `0x48041000` | 각각 4KiB | 32MHz |
| RSE S / `rse_watchdog_s` | `0x58040000` | `0x58041000` | 각각 4KiB | 32MHz |

모두 SystemC `zena_watchdog`다. **모델이 수용하는 register frame은 각각 4KiB**이므로 AP/SI의 64KiB aperture 전체가 유효한 register 공간은 아니다. Frame-relative offset `0x1000` 이상 접근은 address error다. [Platform](SOURCES.md#platform) · [모델](SOURCES.md#models)

| Object | WS0 | WS1 | 최종 MMIO router |
|---|---|---|---|
| AP NS | AP SPI50 / **INTID82** | fanout → AP SPI51 / **INTID83** + SI0 SPI289 / **INTID321** | `ap_router` |
| AP S | AP SPI47 / **INTID79** | `host_reset_ctrl.ap_s_watchdog_reset` | `ap_router` |
| SI CL0 | SI0 SPI5 / **INTID37** | `host_reset_ctrl.si_watchdog_reset` | `si_cl0_router` |
| RSE NS | NVIC **IRQ1** | NVIC **IRQ0** | `rse_router` |
| RSE S | 미연결 | 미연결 | `rse_router` |

AP target은 생성 후 `interconnect.lua`에서 `system_router`에서 `ap_router`로 재지정된다. RSE IRQ는 `Container → LocalPass → NVIC`로 전달된다. IRQ0에는 host UART도 직접 연결되어 있으며, 명시적 OR 결합과 동시 source 동작은 별도 확인 대상이다.

**CPU 관계:** AP NS/S는 AP CPU들이 공유한다. SI1 전용 HW watchdog instance는 없으며, 코어별 PFDI alarm은 아래 별도 감시 계층이다.

## 2. Reset 연결과 범위

| Trigger | 현재 경로 | 끝까지 연결된 범위 |
|---|---|---|
| AP NS WS1 | SI0 INTID321 → SCP event → AP OFF → RSE reload ACK → CPU0 ON | firmware가 수행하는 AP 복구 |
| AP S WS1 | reset controller → `ap_reset` → AP cold-reset fanout | AP watchdog·주변장치·QEMU CPU reset |
| SI0 WS1 | reset controller → `RGM_RST_MASK[24]` gate → `si_reset` | **si_reset 출력 미연결** |
| RSE NS WS1 | NVIC IRQ0 | interrupt까지만; watchdog reset input 연결 없음 |
| RSE S WS0/1 | 모델 출력 | NMI·reset downstream 연결 없음 |
| RSE SWRESET write | `rse_sysctrl.system_reset` → Apollo system fanout | 별도 software reset 경로 |

- AP NS WS1은 controller의 `ap_ns_watchdog_reset` 입력에 직접 연결되지 않는다.
- AP S WS1→AP reset에는 RGM mask gate가 없다. SI0 경로의 bit24는 `EXP0RESETEN`이다.
- AP cold-reset fanout은 **AP NS/S watchdog clear → BL2 loader/header SRAM → AP reset_gpio** 순서로 reset을 전달한다. UART·DMA·mailbox 등도 포함한다.
- Apollo system fanout은 AP 경로에 RSE·SI0·SI1 reset을 더하고, watchdog 5개를 모두 clear한다.
- `rse_sys_rss_reset_fanout` 자체에는 RSE watchdog이 없다. 전체 Apollo fanout의 별도 target으로만 연결되므로 TRM의 SYS/RSS reset domain과 완전 일치를 주장하지 않는다.

Reset fanout의 1ps 이벤트 지연은 시뮬레이션 순서 제어다. 실제 reset pulse width·전원 유지·POR scope의 증거가 아니다. [Reset 소스](SOURCES.md#platform)

## 3. Profile별 차이와 reference 경계

| 항목 | Full-system | `linux-direct` |
|---|---|---|
| AP NS WS1 | AP INTID83 + SI0 INTID321 | AP INTID83만 |
| AP S WS1 | AP reset controller | 미연결 |
| SI firmware recovery | SCP·RSE 협력 | 제거 |
| AP cold / Apollo system fanout | 존재 | 제거 |
| AP SBISTC instance | 4개 cluster register 모델 | 제거 |

| Zena reference 계약 | 현재 QVP에서의 경계 |
|---|---|
| SI AP watchdog 입력 INTID320–323 | NS WS1 **321만** 연결 |
| SI0 Secure alias `0x170700000` / `0x170710000` | 해당 target 없음 |
| RSE Secure/SLOWCLK watchdog → combined NMI | Secure 출력 미연결, SLOWCLK device 없음 |
| RSE NS reset mask `NSWDRSTREQEN` | NS WS1→reset gate 연결 없음 |
| RSE watchdog PPC0·PD_AON·SYS/RSS reset | watchdog PPC filter 없음; reset fanout 범위 차이 |

FVP 설정에서 watchdog clock/reset override는 확인되지 않았다. FVP 실제 주파수·만료 파형·reset 범위는 미측정이다. [참조 근거](SOURCES.md#reference)

<a id="registers"></a>

## 4. Register와 모델 동작

| Frame | Offset | Register | 구현 |
|---|---|---|---|
| Control | `0x000` | WCS | bit0 EN, bit1 WS0, bit2 WS1; write는 EN만 저장하고 두 stage clear |
| Control | `0x008` | WOR | offset 하위 32-bit; write 시 clear·rearm |
| Control | `0x00C` | WORU | offset 상위 16-bit만 저장; write 시 clear·rearm |
| Control | `0x010` / `0x014` | WCV / WCVU | 64-bit deadline 표시; **write는 저장만**, 예약 변경 없음 |
| Refresh | `0x000` | WRR | write data 무관; 두 stage clear·rearm |
| 양쪽 | `0xFCC` | IIDR | `0x0001043B`, write 무시 |

- MMIO는 **32-bit·4-byte aligned** 접근만 허용한다. 다른 폭/정렬/frame 경계 초과는 address error다.
- 유효 4KiB 내부의 미구현 offset은 read-zero/write-ignore다. DMI·MMIO latency는 모델링하지 않는다.
- `O = ((WORU & 0xffff) << 32) | WOR`, 한 구간은 `O / clock_frequency`다.
- 시간은 `sc_time_stamp() × clock_frequency`에서 계산한다. CSS counter mirror나 CPU CNTFRQ를 직접 참조하지 않는다.
- Reset assert는 register·출력을 clear하고 이전 wait generation을 무효화한다. Reset 유지 중 write는 무시한다.
- Offset 또는 clock이 0이면 delta-cycle 만료한다. 동적 clock 변경에 따른 기존 wait 재예약은 없다.

[모델·QEMU bridge 근거](SOURCES.md#models)

<a id="monitoring"></a>

## 5. 코어별·진단용 감시 계층

| 감시 종류 | 주소 / 단위 | Reference 또는 SW 역할 | 현재 QVP |
|---|---|---|---|
| E_CPU_CSR WDT | `0x142000000 + cluster × 0x04000000` | core별 WDT clear·timeout status | 64KiB `gs_memory`; 능동 countdown·IRQ 없음 |
| E_CPU_CSR registers | `+0x200/204/208/20C`, `+0xF24` | core0–3 clear bit0, timeout bits[3:0] | register 저장 공간과 HW 기능을 구분 |
| SBISTC | `0x140100000 + cluster × 0x04000000` | chunk별 `FCTLR.FREQ × 32 cycles` timeout → DEADLOCK → FMU | 4개 cluster 모델; FAIL 명시적 주입만, countdown 없음 |
| RSE SLOWCLK WD | `0x5802E000`, 4KiB | Secure/Privileged, NMI·cold-reset source | device target 없음; 32MHz timestamp WD와 다른 IP |
| RSE SAM watchdog | SAM 내부 | NMI response 감시·cold-reset 정책 | 별도 IP; timestamp WD의 동작 근거로 사용하지 않음 |
| PFDI monitor | AP/SI1 CPU별 SW alarm | 진단 report 수신 기한 감시 | CL0 timer alarm → fault bitmap·log |

SBISTC의 일반 `FCTLR.FAIL` write는 FMU bank1의 `record 210 + CPU`에 fault를 주입한다. 이 경로는 자율 DEADLOCK 감지가 아니다. PFDI timeout handler도 직접 reset/FMU escalation을 호출하지 않는다. [모델](SOURCES.md#models) · [PFDI 소스](SOURCES.md#pfdi)

| QVP PFDI 정책 | AP | SI CL1 |
|---|---:|---:|
| 진단 interval | 3초 | 3초 |
| Out-of-reset 기한 | 10초 | 1초 |
| Boot 기한 | 180초 | 10초 |
| Online report 기한 | 60초 | 25초 |

`WAIT_FOR_OOR → WAIT_FOR_BOOT → WAIT_FOR_ONL`로 진행하며 정상 report가 deadline을 갱신한다. OFF/SLEEP은 alarm을 중지하고, timeout은 fault를 기록한다. 위 값은 QVP Yocto 정책 기본값이며 FTTI·실시간 보장이나 배포 바이너리의 실행 측정값이 아니다. Linux `/dev/watchdog` timeout과도 별개다.

## 6. 정적 descriptor 재현

프로젝트 root에서 실행한다. VM을 생성하지 않으며 host 환경변수 대신 source 기본 구성을 평가한다.

```sh
python3 - <<'PY'
from pathlib import Path
import json
from scripts.test.apollo_lua_descriptor import evaluated_platform
p, _ = evaluated_platform(Path('hsoc-stack/tools/qbox-platform/platforms/apollo'))
watchdogs = {k: v for k, v in p.items()
             if isinstance(v, dict) and v.get('moduletype') == 'zena_watchdog'}
assert len(watchdogs) == 5
print(json.dumps(watchdogs, indent=2))
PY
```

평가기는 `apollo-qvp-saturn-v.lua`를 우선 선택한다. 이 표는 source wiring 확인이며 guest expiry, 실제 IRQ 전달, 복구 완료·시간 정확도·FVP 동등성 검증을 대신하지 않는다.
