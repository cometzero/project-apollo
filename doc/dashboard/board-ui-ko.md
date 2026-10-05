# 보드 그림과 화면 설계

상태: **설계안**. [화면 배치 원본](assets/dashboard-board-wireframe.drawio)은 UI 구조를
설명하는 wireframe이다. 실제 데이터 없이 RUN/PASS를 연출하는 runtime 화면으로 쓰지 않는다.

## 1. 화면 구성

| 영역 | 내용과 동작 |
|---|---|
| 상단 | Saturn-V QVP, image/profile, run ID, elapsed, lifecycle, 관측 신선도, 접속 권한 |
| 부하 요약 | `--stats` 사용 시 QBox CPU total/main/vCPU/other, AP/RSE/SI0/SI1, RSS MiB, `threads=N`, 수집 간격·age |
| 좌측 navigation | Board / UART / Scenarios / Control / Evidence |
| Board 중앙 | **보드 그림 ↔ 블록도** 전환, subsystem 펼치기, link filter, 검색·zoom·fit |
| 우측 Inspector | 선택 부품/연결의 출처·모델·주소 공간·현재 상태·관련 log/시나리오 |
| 하단 접이식 dock | 선택 UART tail + 이벤트 timeline; 전체 UART 페이지로 확대 |
| Control | 동작 범위와 선행 조건, 실행 결과 및 수동 복구. 실행 중 다른 mutation 비활성 |
| Evidence | run/profile별 판정과 원본 로그·manifest·편집 가능한 topology export |

1440px 화면은 board와 Inspector를 함께 표시하고, 1024px 이하는 Inspector를 drawer로
전환한다. 휴대 화면은 목록/상태를 우선하며 graph는 pan/zoom한다. 부품은 Tab·Enter로
선택 가능하고 색상과 함께 상태명/아이콘을 표시한다. 자동 log scroll은 사용자가 과거
행을 선택하면 멈춘다. 전체 multi-UART 화면은 domain별 split과 filter를 제공한다.

부하 요약을 펼치면 최근 120개 표본의 CPU/RSS 추이와 domain별 vCPU 그래프를 보인다.
기본 5초는 최근 10분이며 host 시간 축을 사용한다. 단위는 `host CPU %`, `RSS MiB`로
명시하고 100% 초과 값을 허용한다. Domain은 vCPU 세부 값이므로 total과 누적 합산하지 않는다.
`--stats`가 없으면 `부하 수집 꺼짐 — 다음 실행에 --stats 사용`을 표시한다. WARMING_UP,
STALE, N/A, 측정 barrier gap을 0으로 대체하지 않는다. Apollo node Inspector에도 같은
cache를 연결하고 별도 TC397/SIL Kit 부하는 현재 QBox 값에 포함하지 않는다.

## 2. 보드처럼 보이는 논리적 배치

Board view는 짙은 녹색 PCB 바탕, 칩 외곽과 pin 표시, connector 형태, 얇은 bus trace를
사용한다. 그림 위에 **QVP 논리 보드 · 실물 배치 UNVERIFIED**를 항상 표시한다.
장식용 trace나 pin count를 실제 electrical net/패키지 pinout으로 해석하지 않는다.

| 배치 | 표시할 대상 | 실제 존재·연결의 기준 |
|---|---|---|
| 중앙 큰 package | Apollo SoC | `soc/apollo.lua` 아래 AP/RSE/SI/ROS/Fabric 그룹 |
| SoC 내부 drill-down | AP cluster, RSE, SI CL0, SI CL1, fabric/memory/controller | evaluated CCI path와 모델 유형 |
| 좌측 package | TC397 vMCU + Zephyr | launcher manifest attachment; 독립 process 표시 |
| 우측 상단 | TPS6594 | SI CL0 I2C0, address 0x48, int_n→PMIC GPIO |
| 우측 하단 | PCA9539와 EEPROM bank | AP I2C bus의 slave와 reset/IRQ |
| 보드 가장자리 | UART, CAN, Ethernet/PCIe 등 connector badge | 활성 backend/route가 있을 때만 실제 연결로 표시 |
| 보드 외부 | SIL Kit VehicleCAN/VehicleRestbus | participant manifest; registry는 데이터 통과 bus로 그리지 않음 |
| 접이식 VP 영역 | loader, QEMU instance, chardev, QMP, monitor, loopback | host/VP 지원 요소; 실물 PCB 부품처럼 표현하지 않음 |

현재 board Lua에는 EEPROM 8개(AP I2C0의 0x50/51/52, I2C1~5의 0x50 각 하나),
I2C bus 2개, PCA9539, TPS6594가 있다. EEPROM은 bank로 접고 펼치면 각 CCI node를
보인다. 주소가 같은 EEPROM도 bus가 다르면 다른 장치다. DRAM/SRAM/flash decode
window는 메모리 영역으로 표현하며 Lua 근거 없이 별도 실물 DRAM package를 만들지 않는다.

Presentation rule은 chip class/group, 우선 배치, 색/아이콘만 지정한다. Component 목록,
enabled 여부, 주소, 연결 edge를 별도 하드코딩하지 않는다. 새 Lua 장치가 추가되면
generic block으로라도 나타나야 한다. 수동 배치가 없는 노드는 자동 layout한다.

## 3. Lua에서 두 화면을 만드는 과정

1. 선택된 `.qboxconf`의 `provider.data_dir/config`와 explicit `--conf` 우선순위를 그대로
   적용한다. Startup의 effective entrypoint, 포함 소스, 환경·CCI override를 snapshot한다.
2. 기존 [topology extractor](../../scripts/autosd_dashboard/topology.py)와
   [Lua evaluator](../../scripts/test/apollo_lua_descriptor.py)를 일반화한다. 임의 browser
   Lua upload/경로 선택은 받지 않는다. include allowlist·평가 timeout·resource 상한을 유지한다.
3. Final table/binding 결과를 추출한다. CLI CCI override가 topology에 영향을 주면 동일
   precedence를 적용한다. 해석하지 못하는 override는 `unresolved_override`로 남기고
   `run-exact`라고 표시하지 않는다. 모르는 조건을 기본값으로 대체하지 않는다.
4. Stable node ID는 기존 `platform.*` CCI path다. 소스 디렉터리를 맞추기 위해 live CCI
   hierarchy를 rename하지 않는다. 양 끝 port, 원래 binding, 방향 판정 근거를 보존한다.
5. TC397 status/launch manifest로 `external.tc397`, `external.silkit.*`를 결합한다.
   endpoint와 방향이 양쪽에서 일치할 때 UART/GPIO/CAN semantic edge를 만든다.
   미확인 링크는 `UNCONFIRMED`, 비활성 endpoint는 disconnected로 표시한다.
6. 하나의 normalized graph로 Board와 Block layout을 생성한다. 선택 node와 filter를
   보기 전환 시 유지한다. Runtime overlay는 graph 존재 여부와 별도 필드로 합성한다.

Cache key에는 schema version, entrypoint, 모든 source SHA, effective env, CCI override,
attachment manifest를 포함한다. 부팅 후 checkout 변경은 **새 static preview**에만 반영한다.
현재 run의 frozen topology를 덮어쓰지 않는다. 분석 실패 시 error를 표시하며 이전
graph를 현재 정상 구성인 것처럼 유지하지 않는다. 이전 snapshot은 날짜·run을 붙여 조회한다.

## 4. 데이터 출처와 주소

| provenance | 표시 의미 |
|---|---|
| `lua-configured` | 선택 profile을 평가한 구성. 실제 object 존재/traffic 성공과 별개 |
| `launcher-attached` | launcher가 시작·연결하도록 지정한 외부 process |
| `runtime-observed` | 소유 listener/QMP/로그/firmware 응답에서 관찰; source·age 필요 |
| `presentation-only` | package 모양·위치·grouping; electrical net 근거 아님 |

Node Inspector는 `id`, `moduletype`, group, QemuInstance, source path/SHA,
ports/binding, memory windows, capability, last observation, 연결된 log를 제공한다.
Lua source line은 extractor가 관찰한 함수/호출 위치이며 정확한 대입문 위치로 단정하지 않는다.

주소는 JSON hex string과 browser BigInt로 보존한다. 0을 absent로 해석하지 않고,
size가 없거나 0이면 end를 계산하지 않는다. `relative_addresses`, `mapped_base_addr`,
priority와 **어느 router 주소 공간인지**를 함께 표시한다. Bus decode를 AP guest PA로
자동 환산하지 않는다. IRQ는 AP/SI GIC INTID와 TC397 SRC 번호를 별도 namespace로 표시한다.

## 5. vMCU 링크의 표현

| Link | label/방향 | 상태를 얻는 근거 |
|---|---|---|
| AP management | ASCLIN0 ↔ DW UART2 (`0x301C0000`, AP INTID364) | 명시적 ping/status 응답 |
| Safety channel | ASCLIN2 ↔ SI PL011 (`0x2A820000`, SI INTID41) | PFDI epoch/sequence/age, 5초 보고 |
| GPIO bundle | PORT0 ↔ SI PL061 (`0x2A830000`, SI INTID42) | MCU GPIO snapshot; 실제 source clock 명시 |
| PMIC | vMCU RPC → SI CL0 I2C (`0x2A800000`) → TPS6594 | rail 설정 readback/STAT; 측정 전압 아님 |
| CAN | M_CAN ↔ TC397CanBridge ↔ VehicleRestbus | 실제 SIL Kit TX result, CAN 0x510/600/601 |

GPIO 펼침은 SOC_ERROR, SOC_PWR_REQ, IST_DONE_N(SI→MCU), SOC_RESET_N,
MCU_SOC_WAKE(MCU→SI/board reset)의 방향·극성을 보인다.
현재 default static profile의 UART2↔3 loopback과 SI dummy sink를 활성 vMCU 연결과
동시에 그리지 않는다. Endpoint 선택 결과가 연결의 기준이다.

SI CL0 PFDI의 monitored/online/fault/off mask를 AP core 표시와 연결한다.
수집 지연은 STALE, firmware fault는 FAULT, 의도된 AP off는 AP_OFF로 구분한다.
SIL Kit가 없으면 CAN DISABLED를 표시하며 SI/UART 관측을 계속 사용할 수 있다.
Link의 작은 event 표시는 실제 event가 있을 때만 사용하고 지속 흐름 animation으로
가상 대역폭이나 실시간 성공을 암시하지 않는다.

## 6. Inspector에서 바로 할 수 있는 일

- AP: 관련 UART, PFDI core mask, boot epoch, 사용 가능한 검사·복구 job으로 이동.
- SI CL0: PFDI/Safety 보고, PMIC ownership, firmware log, 검증된 safety scenario 선택.
- TC397: shell log, firmware hash, SI epoch/MCU cookie, CAN counter, typed CLI action.
  CAN 미사용/초기화 실패 시 cookie는 unavailable로 표시한다.
- TPS6594: rail 0..8 설정값과 live STAT 0..10 조회. Enable toggle/voltage slider는 제공하지 않음.
- Bus/IRQ: 구성된 route와 capability, 검증 증거. 빈번한 MMIO read로 상태를 만들지 않음.
- Host/VP: process CPU/RSS, QK/MCIPS, QMP read-only query. Guest CPU와 host CPU를 별도 표시.

Block view에는 전체 subsystem 집계와 선택 group 상세를 제공한다. 루트에 수백 개
node/천 개 edge를 한꺼번에 펼치지 않는다. Group edge는 실제 edge 집계이며 클릭하면
원래 bind 목록으로 내려간다. Draw.io export에는 현재 profile/provenance/한계를 포함한다.
