# Apollo timer 소프트웨어 구성

조사일: 2026-09-11. [하드웨어 구성](hardware.md),
[테스트 결과](test-results-2026-09-11.md)와 함께 읽는다.

후속 변경에서는 기본 OFF인 `APOLLO_TIMER_TEST` 옵션으로 네 firmware 단계의
timer 검사를 추가했다. [구현·검증 문서](implementation-2026-09-12.md)를 참조한다.

## RSE TF-M 결론

현재 FVP/QVP 정상 이미지의 TF-M은 RSE clock을 초기화하지만,
SysTick이나 RSE TIMER0~3을 주기적 timer로 초기화·사용하지 않는다.
이 결론은 소스 호출 경로, 최종 ELF, 빌드 설정 및 부팅 후 레지스터 관측에 근거한다.
드라이버 파일이나 interrupt vector가 존재한다는 것만으로 사용 중이라고 판정하지 않았다.

TF-M 소스 revision은 `c4d3bf96349c392c18570dfd39c87c7a56a42bc5`다.
두 machine 모두 `RSE_DEFAULT_CLOCK_CONFIG=ON`, `TEST_S=OFF`, `TEST_NS=OFF`,
`TFM_FIH_PROFILE=OFF`, `MCUBOOT_FIH_PROFILE=OFF`인 산출물을 조사했다.
SLIH/FLIH timer 테스트 partition은 활성화되어 있지 않다.

| Stage | 실제 clock/timer 경로 |
| --- | --- |
| BL1_1 | `SystemInit`/기본 clock 정의. 최종 ELF에 `rse_clock_config`, `SystemCoreClockUpdate` 없음 |
| BL1_2 | `boot_platform_init()` → `rse_clock_config()` → `SystemCoreClockUpdate()` |
| BL2 | BL1_2가 설정한 clock을 상속. 최종 ELF에 위 clock 설정 함수 없음 |
| TF-M secure runtime | `tfm_hal_platform_init()` → `rse_clock_config()` → `SystemCoreClockUpdate()` |

`rse_clock_config()`는 SYSCTRL `CLK_CFG1`을 설정한다.
`SystemCoreClockUpdate()`가 부르는 `rse_get_sysclk()`는
`SysTick->CALIB`의 TENMS를 읽어 `100*TENMS`를 사용하고,
TENMS가 0이면 기본 SYSCLK 100MHz로 돌아간다.
CTRL/LOAD/VAL을 쓰지 않으므로 이 경로는 SysTick 시작이 아니다.
QVP의 SysTick 미구현과 CALIB read=0은 기본값 사용으로 가려질 수 있다.

## 빌드에 있는 코드와 실행되는 코드

RSE common의 `device_cfg.h`는 secure TIMER0 장치를 정의하며 기본 주파수는
32MHz다. `systimer_armv8-m_drv.c`는 `libplatform_s.a`에 포함되지만,
정상 이미지에서 참조되지 않는 초기화 함수와 장치 객체는 최종 링크에서 제거된다.

| 심볼 | 두 machine의 최종 `tfm_s` ELF |
| --- | --- |
| `systimer_armv8_m_init` | 없음 |
| `SYSTIMER0_ARMV8_M_DEV_S` | 없음 |
| `tfm_plat_test_secure_timer_start` | 없음 |
| `tfm_timer0_irq_init` | 없음 |
| `TFM_TIMER0_IRQ_Handler` | vector 참조로 남음; 등록/enable 증거가 아님 |
| `SysTick_Handler` | weak handler가 남음; tick 설정 증거가 아님 |

테스트 전용 `tfm_plat_test_secure_timer_start()`는 TIMER0을 초기화하고,
32,000 tick auto-increment와 interrupt를 활성화한다.
현재 두 빌드에서 이 함수가 있는 `plat_test.c`의 compile entry는 0개다.
향후 SLIH/FLIH 테스트를 켤 경우 **32MHz 상수와 실측 125MHz count의 차이**를
먼저 검토해야 한다. 125MHz에서 32,000 tick은 1ms가 아니라 256µs다.
`CNTFRQ`에 주파수를 쓰는 것만으로 실제 count source의 주파수가 바뀌지는 않는다.

부팅 후 두 플랫폼의 관측은 TIMER0~3 `CTL=0`, `CVAL=0`, `CNTFRQ=0`,
NVIC `ISER0=0x600`이었다. IRQ9/10만 enable되어 있고 timer IRQ3/4/5/27은
disable되어 있었다. Counter는 이 상태에서도 증가했다.
두 시점의 레지스터 관측만으로 과거의 모든 실행을 부정할 수는 없으나,
최종 ELF와 호출 경로도 정상 firmware의 timer 미사용 결론을 뒷받침한다.

## AP, SI 및 firmware 소비자

| 실행 주체 | 구성과 소비 경로 | 이번 확인 수준 |
| --- | --- | --- |
| AP TF-A/U-Boot | architectural counter를 delay/timeout에 사용; TF-A가 HW_CONFIG DT 전달 | 소스/구성 조사. 각 delay call의 runtime 측정은 하지 않음 |
| AP Linux | `arm_arch_timer` clocksource/clockevent; 각 CPU의 comparator 및 PPI | FVP/QVP 모두 125MHz 표시, `arch_sys_counter`, 4코어 IRQ 증가 실측 |
| AP MMIO timer | secure/NS frame은 CPU-internal timer와 별도 comparator | QVP component test에서 frame0 SPI49와 WFI wake 검증; full boot 시 사용 여부와 구분 |
| SI CL0 SCP | `config_gtimer`의 `hw_timer=0x2A720000`, `hw_counter=0x2A6F0000`, REFCLK control, 125MHz; `config_timer`에서 INTID34 (SPI2)와 alarm 연결 | FVP/QVP 최종 ELF에 gtimer, timer start/isr/wait/alarm 함수 연결 확인 |
| SI CL1 Zephyr | `arm,armv8-timer`, `CONFIG_ARM_ARCH_TIMER=y`, 100 ticks/s, tickless; `sys_clock_driver_init`, compare ISR, `sys_clock_set_timeout` | 양쪽 최종 ELF 연결 확인. tickless이므로 100Hz 고정 IRQ라고 해석하지 않음 |

SCP는 RSE sync 등에 `timer_api->wait()`를 사용하며 설정된 PFDI 경로가 alarm API를
소비한다. CL0/CL1 firmware는 RSE TF-M과 별개이므로 SI의 timer 사용이 TF-M의
SysTick 사용을 의미하지 않는다. CL1의 실제 count rate와 OS의 주파수 계약 차이는
[검증 문서](test-results-2026-09-11.md)의 미해결 항목으로 관리한다.

## 추적할 소스와 산출물

TF-M 기준 디렉터리: `hsoc-stack/components/system_mgmt/trusted-firmware-m/`.

- `platform/ext/target/arm/rse/common/bl1/boot_hal_bl1_2.c`: BL1_2 platform init.
- `platform/ext/target/arm/rse/common/tfm_hal_platform.c`: runtime platform init.
- `platform/ext/target/arm/rse/common/device/source/rse_clocks.c`: CALIB read와 clock 설정.
- `platform/ext/target/arm/rse/common/CMakeLists.txt`: timer driver/test 빌드 조건.
- `platform/ext/target/arm/rse/common/plat_test.c`: 테스트 전용 TIMER0 시작.
- `platform/ext/target/arm/rse/common/tfm_interrupts.c`: IRQ handler/등록 함수.
- `platform/ext/target/arm/rse/common/device/config/device_cfg.h`: 32MHz 테스트 계약.

SCP는 `hsoc-stack/components/system_mgmt/scp-firmware/product/automotive-rd/`
하위 `apollo-fvp/si0_ramfw/`와 `apollo-qvp/si0_ramfw/`의
`config_gtimer.c`, `config_timer.c`를 확인했다.
CL1 board DTS는 `hsoc-stack/components/system_mgmt/zephyrproject/zephyr_hsoc_src/boards/hsoc/`
하위 두 machine의 `*_safety_island_c1.dts`다.

빌드별 증거는 `build/timer-audit/software/`의 `tfm-symbols.tsv`, `artifacts.tsv`,
`tfm-timer-analysis.md`에 보존했다. TF-M link map의 discarded section을 실제 연결된
함수로 세지 않고 최종 ELF symbol table과 compile commands를 대조했다.
