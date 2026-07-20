# Apollo QVP Safety Island GIC multiview fidelity 부채

- 작성일: 2026-07-20
- 대상: `apollo-qvp`, RD-Aspen cfg2
- 상태: 설계 대기(16코어 4클러스터 지원 완료 후 착수)
- 구현 소유 후보: `hsoc-stack/tools/qbox-platform/` 우선
- 소스 변경 제한: `hsoc-stack/components/` 변경 금지

## 1. 결정 사항

Safety Island(SI) GIC-720AE multiview의 현재 QBox 구현은 SI CL0과 SI CL1의
부팅 및 주요 interrupt 전달에 필요한 기능을 제공하지만, FVP 하드웨어 계약을
그대로 모델링한 구조는 아니다. 현재 구조는 View 0 설정 register 일부와 서로
독립된 두 QEMU GIC를 조합한 기능적 근사다.

이 부채는 AP 16코어 4클러스터 지원과 분리한다.

- AP GIC multiview는 16코어 구현 범위에 유지한다. AP의 16개 redistributor와
  View 0 설정 경로를 검증하는 데 필요하다.
- SI GIC multiview 재설계와 구현은 16코어 지원이 완료된 뒤 시작한다.
- 16코어 단계에서는 SI GIC 구조를 확장하거나 QEMU GIC 내부를 변경하지 않는다.
- 후속 구현은 하나의 SI GIC 상태와 View 0/1/2 정책을 일관되게 제공하는 것을
  목표로 한다.

16코어 작업의 기준 문서는
`doc/apollo-qvp-16core-4cluster-fvp-qbox-support-plan-ko.md`다. 이 문서는 해당
작업이 끝난 뒤 진행할 SI 전용 fidelity 개선의 범위와 착수 조건을 기록한다.

## 2. Arm Zena CSS 하드웨어 계약

### 2.1 세 개의 programming view

RD-Aspen cfg2의 Safety Island에는 하나의 GIC-720AE와 세 개의 programming
view가 있다.

| View | 접근 주체 | 역할 | 주요 주소 |
| --- | --- | --- | --- |
| View 0 | SI CL0 SCP-firmware | 부팅 시 View 1/2의 redistributor 및 SPI 소유권 설정 | GICD `0x3000_0000`, GICR frames `0x3004_0000`부터 |
| View 1 | SI CL0 firmware/OS | SI CL0의 functional GIC view | GICD `0x3010_0000`, GICR `0x3014_0000` |
| View 2 | SI CL1 Zephyr | SI CL1의 functional GIC view | GICD `0x3020_0000`, GICR `0x3026_0000`부터 |

근거는 다음과 같다.

- `arm-zena-css/documentation/design/components.rst:110-128`은 View 0을 SI CL0의
  설정 view, View 1을 SI CL0 OS, View 2를 SI CL1 OS용으로 정의한다.
- 같은 파일 `:150`은 cfg2가 SI GIC multiview를 지원한다고 명시한다.
- `doc/arm_zena_css_dev_guide/09-programmers-model-for-zena-css.md:1203`은 SI
  CL0가 접근하는 GIC-720AE View 0 window를 `0x3000_0000`에 정의한다.
- `hsoc-stack/components/system_mgmt/scp-firmware/product/automotive-rd/apollo-qvp/si0_ramfw/include/si0_mmap.h:22-35`는 View 0과 View 1 주소를 정의한다.
- `hsoc-stack/components/system_mgmt/zephyrproject/zephyr_hsoc_src/boards/hsoc/apollo_qvp_safety_island_c1/apollo_qvp_safety_island_c1.dts:87-96`은
  View 2의 GICD/GICR 주소를 정의한다.

### 2.2 redistributor 소유권

SI CL0 SCP-firmware가 설정하는 redistributor mapping은 다음과 같다.

| PE | View 0 redistributor frame | 할당 view |
| --- | --- | --- |
| SI CL0 CPU0 | `0x3004_0000` | View 1 |
| SI CL1 CPU0 | `0x3006_0000` | View 2 |
| SI CL1 CPU1 | `0x3008_0000` | View 2 |
| SI CL1 CPU2 | `0x300a_0000` | View 2 |
| SI CL1 CPU3 | `0x300c_0000` | View 2 |

이 mapping은
`hsoc-stack/components/system_mgmt/scp-firmware/product/automotive-rd/apollo-qvp/si0_ramfw/config_gicx00_multiview.c:29-37`에 정의돼 있다.

### 2.3 SPI 소유권

같은 SCP-firmware 설정은 SPI를 view별로 분리한다.

- View 1: SI CL0 timer, watchdog, UART, CL0 대상 MHU, FMU, AP error와 SMCF
  interrupt
- View 2: SI CL1 timer, watchdog, UART, CL1 대상 MHU interrupt

정확한 목록은 `config_gicx00_multiview.c:39-73`의 `si_spi_map[]`이 기준이다.
구현 시 이 표를 별도 hard-coded 목록으로 복제하기보다 platform configuration에서
하나의 소유권 표로 관리해야 한다.

### 2.4 view 간 제어 의미

SCP-firmware의 multiview module은 다음 순서로 SI GIC를 설정한다.

1. `GICD_CFGID`로 multiview 지원 여부를 확인한다.
2. 각 View 0 redistributor의 `GICR_VIEWR`를 설정한다.
3. `GICD_IVIEWR`를 통해 SPI를 View 1 또는 View 2에 할당한다.
4. View 0의 `GICD_CTLR`를 초기화한다.

`mod_gicx00_multiview.c:115-161`의 주석에 따르면 각 functional view에서 보이는
최종 `GICD_CTLR` 값은 View 0 값과 해당 view 값의 logical AND다. 따라서 View 0
register read/write만 성공시키는 것으로는 충분하지 않다. 설정 결과가 실제
interrupt state, enable과 delivery에 반영돼야 한다.

## 3. 현재 QBox 구조

현재 `apollo-qvp`의 SI interrupt 구조는 다음과 같다.

```text
SI CL0 SCP-firmware
  |
  +-- View 0 config access
  |     `gicx00_multiview`
  |       - CFGID / IVIEWR
  |       - VIEWR / PWRR / FLUSHR
  |       - 일부 synthetic register state
  |       - SI canonical GIC backend 연결 없음
  |
  +-- View 1 functional access
        `si_cl0_gic` (QEMU arm_gicv3, 1 PE)

SI CL1 Zephyr
  |
  +-- View 2 functional access
        `si_cl1_gic` (별도 QEMU arm_gicv3, 4 PE)
```

구현 근거는 다음과 같다.

- `hsoc-stack/tools/qbox-platform/platforms/apollo/hw-block/si_cl0.lua:529-573`은
  `platform.si_gic_multiview`의 View 0 설정 register window를 노출한다.
- 같은 파일 `:990-1020`은 View 1 주소에 1-CPU `arm_gicv3`인
  `platform.si_cl0_gic`를 생성한다.
- `hsoc-stack/tools/qbox-platform/platforms/apollo/hw-block/si_cl1.lua:64-69,155-166`은
  View 2 주소에 4-CPU `arm_gicv3`인 `platform.si_cl1_gic`를 별도로 생성한다.
- `hsoc-stack/tools/qbox-platform/systemc-components/gicx00_multiview/include/gicx00_multiview.h`는
  backend forwarding 기능을 갖지만 현재 SI instance에는 View 1/2의 공유 상태를
  소유하는 canonical backend가 연결돼 있지 않다.

이 구조에서는 SI CL0과 SI CL1이 각각 독립된 distributor state를 가진다. 따라서
두 functional view가 하나의 GIC-720AE 상태를 정책에 따라 분할해 보는 FVP 계약과
차이가 있다.

## 4. 남은 fidelity 부채

| ID | 부채 | 현재 영향 | 완료 조건 |
| --- | --- | --- | --- |
| SI-GIC-01 | 하나의 canonical SI GIC state 부재 | View 1/2 distributor 상태가 독립 | 1 CL0 PE와 4 CL1 PE가 하나의 GIC 상태에 속함 |
| SI-GIC-02 | `GICR_VIEWR` mapping 미적용 | View 0 write는 가능하지만 PE ownership을 바꾸지 않음 | redistributor 접근과 IRQ delivery가 mapping을 따름 |
| SI-GIC-03 | `GICD_IVIEWR` mapping 미적용 | SPI ownership 설정이 실제 route를 제어하지 않음 | 허용 view에만 SPI state와 delivery가 보임 |
| SI-GIC-04 | `GICD_CTLR` logical-AND 의미 미구현 | View 0 policy가 functional enable을 제한하지 않음 | View 0과 View 1/2 조합 결과가 FVP와 일치 |
| SI-GIC-05 | 잘못된 view 접근의 격리 미검증 | mixed-criticality isolation을 증명하지 못함 | 다른 view 소유 interrupt/state의 접근 및 delivery가 차단됨 |
| SI-GIC-06 | 공통 reset/power lifecycle 부재 | 두 QEMU GIC가 독립적으로 reset될 수 있음 | reset 이후 세 view의 상태 관계가 FVP와 일치 |
| SI-GIC-07 | cross-view 회귀 검증 부재 | 부팅 성공만으로 mapping 정확성을 판단 | positive/negative IRQ 검증 자동화 |

현재 구조가 부팅에 유용하다는 사실과 위 fidelity 부채는 구분해야 한다. 후속 설계는
기존 부팅 경로를 유지하면서 정책과 상태 소유권을 교정해야 한다.

## 5. 목표 구조

### 5.1 원칙

1. SI GIC의 architectural state owner는 하나만 둔다.
2. View 0은 설정 plane이며 별도의 functional GIC state를 만들지 않는다.
3. View 1과 View 2는 동일한 underlying state를 소유권 정책에 따라 필터링해 본다.
4. 물리 interrupt input은 한 곳에만 연결한다. 같은 SPI를 여러 QEMU GIC에
   fan-out하지 않는다.
5. policy 변경은 register readback뿐 아니라 접근 권한과 IRQ delivery에 반영한다.
6. QEMU 변경은 최소화하고, 재사용 가능한 SystemC/TLM 계층과 qbox-platform
   wiring을 우선 검토한다.

### 5.2 개념 구조

```text
                         +--------------------------+
SI CL0 SCP -- View 0 --> | multiview policy/control |
                         | - redistributor owner    |
                         | - SPI owner              |
                         | - GICD_CTLR mask         |
                         +------------+-------------+
                                      |
                         +------------v-------------+
IRQ sources ------------>| canonical SI GIC state  |
                         | 1 x CL0 PE + 4 x CL1 PE  |
                         +------+------------+------+
                                |            |
                    View 1 filter|            |View 2 filter
                                |            |
                          SI CL0 CPU       SI CL1 CPUs
```

구체적인 구현 형태는 후속 상세 설계에서 결정한다. 특히 SI CL0과 SI CL1이 현재
서로 다른 `QemuInstance`에 속하므로, 하나의 QEMU `arm_gicv3`가 두 instance의
CPU interface를 직접 소유할 수 있다고 가정해서는 안 된다. 다음 후보를
prototype으로 비교한다.

- QBox/SystemC가 canonical interrupt 및 multiview state를 소유하고 각 CPU
  backend에 필요한 CPU interface를 연결하는 방식
- 한 QEMU GIC backend를 canonical owner로 사용하고 다른 instance에 최소한의
  외부 CPU-interface hook을 추가하는 방식
- upstream에서 재사용 가능한 GIC multiview 지원이 존재할 경우 이를 도입하는
  방식

선택 기준은 FVP 의미 일치, QEMU upstream 변경량, TLM 경계의 명확성, reset
일관성, 자동화 가능한 검증성이다. 단순 register stub 확대나 독립 GIC 간 상태
복제는 목표 구조로 인정하지 않는다.

## 6. 16코어 완료 후 실행 계획

### Stage SI-GIC-0: 착수 기준 확인

- 16코어 4클러스터 완료 보고서가 작성돼 있다.
- 동일 Yocto image로 FVP와 QBox에서 AP CPU 16개와 GICR 16개가 검증돼 있다.
- CPU power/reset 또는 AP GIC bring-up의 미해결 이슈가 없다.
- 비교에 사용할 SI CL0/CL1 FVP와 QBox baseline log를 보존한다.

위 조건이 충족되지 않으면 SI GIC 구현을 시작하지 않는다. AP 16코어 문제와 SI
multiview 문제를 동시에 디버깅하면 원인 분리가 어려워지기 때문이다.

### Stage SI-GIC-1: FVP observable contract 고정

- SCP-firmware의 View 0 초기화 register trace를 수집한다.
- View 0/1/2의 CFGID, VIEWR, IVIEWR, GICD_CTLR readback을 기록한다.
- CL0/CL1 timer, UART, watchdog과 MHU 중 최소 IRQ 집합의 delivery를 확인한다.
- 소유하지 않은 view에서 register 및 IRQ가 어떻게 보이는지 negative probe한다.
- 결과를 주소, access width, reset value, write/readback과 side effect 표로 만든다.

### Stage SI-GIC-2: 상세 설계와 architecture review

- canonical state owner와 CPU interface 경계를 결정한다.
- View 0 policy register와 functional register의 forwarding/filter 규칙을 정의한다.
- redistributor와 SPI ownership state machine을 정의한다.
- reset, power, pending/active interrupt와 `GICD_CTLR` 결합 의미를 정의한다.
- QBox core, qbox-platform, QEMU 중 각 변경의 소유 경계를 review한다.
- QEMU 수정이 필요하면 upstream 가능한 최소 hook인지 별도로 검토한다.

### Stage SI-GIC-3: 단위 구현과 정적 검증

- policy register reset/read/write test를 먼저 추가한다.
- redistributor View 1/2 mapping test를 추가한다.
- SPI View 1/2 ownership 및 잘못된 view 접근 test를 추가한다.
- `GICD_CTLR` logical-AND test와 reset lifecycle test를 추가한다.
- `./local_build.sh qbox`와 Apollo map validation을 수행한다.

### Stage SI-GIC-4: local full-system 검증

- `live-cl0-cl1` 모드로 SI CL0 SCP와 SI CL1 Zephyr를 함께 부팅한다.
- CL0 전용 IRQ와 CL1 전용 IRQ를 최소 하나씩 발생시킨다.
- 대상 view에서만 pending/active/delivery 상태가 관찰되는지 확인한다.
- RSE, SI CL0, SI CL1과 Primary Compute boot 회귀가 없는지 확인한다.

### Stage SI-GIC-5: 동일 Yocto image FVP/QBox 비교

- 같은 Yocto 산출물을 FVP와 QBox에서 실행한다.
- View 0 초기화 순서, register readback, IRQ 대상 CPU와 로그를 비교한다.
- 허용되지 않은 view delivery가 0건인지 확인한다.
- 차이가 남으면 기능 차이와 의도된 timing 차이를 분리해 기록한다.
- 완료 결과를 이 문서와 별도 검증 보고서에 반영한다.

## 7. 최소 검증 기준

후속 구현의 빠른 검증을 위해 pass/fail 기준은 다음 핵심 항목으로 제한한다.

| Gate | Pass 기준 |
| --- | --- |
| G0: build | `./local_build.sh qbox` 성공 |
| G1: boot | SI CL0 SCP와 SI CL1 Zephyr가 기존 정상 지점까지 부팅 |
| G2: mapping | 1개 CL0 GICR은 View 1, 4개 CL1 GICR은 View 2로 readback |
| G3: CL0 IRQ | 선택한 CL0 SPI가 CL0에만 전달 |
| G4: CL1 IRQ | 선택한 CL1 SPI가 CL1에만 전달 |
| G5: isolation | 반대 view에서 선택 IRQ가 보이거나 전달되지 않음 |
| G6: control | View 0 `GICD_CTLR` 제한과 functional view enable 조합이 FVP와 일치 |
| G7: parity | 동일 Yocto image의 FVP/QBox 핵심 결과가 일치 |

성능, cycle accuracy, 전체 GIC architecture compliance suite와 모든 SPI의 개별
발생 시험은 이 단계의 완료 기준에 포함하지 않는다. 다만 대표 IRQ의 positive 및
negative isolation 검증은 생략할 수 없다.

## 8. 변경 소유권과 비범위

### 8.1 변경 소유권

- Apollo 주소, IRQ와 instance wiring: `hsoc-stack/tools/qbox-platform/`
- 일반화 가능한 multiview/SystemC 기능: `hsoc-stack/tools/qbox/` 또는
  qbox-platform의 reusable component
- libqemu에 꼭 필요한 최소 CPU-interface hook: `hsoc-stack/tools/qemu/`
- 계획, architecture와 결과: 최상위 `doc/`

### 8.2 비범위

- AP GIC multiview의 16 redistributor 구현과 검증
- AP 16코어 4클러스터 bring-up
- SI CPU 성능 또는 host resource 기준
- GIC, bus 또는 interrupt의 cycle-accurate timing
- firmware 동작을 우회하기 위한 SCP-firmware나 Zephyr source patch
- 부팅 로그만 맞추기 위한 register-only stub 확대

## 9. 현재 완료 상태

이 문서 작성 시점에는 분석과 후속 범위 분리만 완료됐다. SI GIC 관련 코드 변경,
build 및 runtime 검증은 수행하지 않았다. 다음 작업은 AP 16코어 4클러스터 지원과
그 완료 보고서 작성이며, 이후 Stage SI-GIC-0의 착수 기준부터 진행한다.
