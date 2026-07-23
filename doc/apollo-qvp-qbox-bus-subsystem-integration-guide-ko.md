# Apollo QVP QBox Bus 및 Subsystem 연결 가이드

Updated: 2026-07-23

이 문서는 현재 Apollo QVP full-system 진입점인
`hsoc-stack/tools/qbox-platform/platforms/apollo/apollo-qvp.lua`에 새로운
bus, peripheral 또는 subsystem을 연결하는 방법을 설명한다. 분석 기준은
qbox-platform 커밋 `14b73e8e95582eec665814fb492d7ae49bc5b34a`이다.

`apollo-pc.lua`와 `apollo-si-cl1.lua`는 각각 AP와 SI CL1의 독립 실행
경로이다. 이 문서에서 별도 언급이 없으면 모든 절차는 full-system
`apollo-qvp.lua` 경로를 뜻한다.

## 1. 핵심 원칙

Apollo QVP의 연결은 다음 두 층을 항상 일치시켜야 한다.

1. `machine contract`: 허용할 domain, address view, bridge, transaction,
   IRQ, reset, boot 및 software 관계를 선언한다.
2. `platform assembly`: 실제 QBox `moduletype`, TLM socket, signal socket,
   QEMU instance와 CCI parameter를 Lua object로 조립한다.

contract에만 추가하면 실제 hardware object가 만들어지지 않는다. 반대로
실제 Lua object만 추가하면 설계 의도, 보안 정책 및 검증 기준에서 누락된
숨은 경로가 된다.

현재 contract는 다음 정책을 명시한다.

- 각 address view는 전용 router를 사용한다.
- 하나의 socket은 하나의 의도된 경로에 연결한다.
- 서로 다른 domain 사이에는 명시적인 ATU/APU, NCI 또는 정적
  allow-list bridge를 둔다.
- 넓은 주소 범위를 다른 router로 그대로 넘기는 broad passthrough를
  금지한다.
- runtime에서 decode priority를 임의로 바꾸지 않는다.
- CPU가 사용하는 RAM의 주인은 QEMU가 아니라 SystemC이다.

Arm Zena CSS programmer's model도 unmapped interconnect access는 DECERR로
종료하고, 보안 속성이 맞지 않는 access는 DECERR 또는 SLVERR로
종료하도록 정의한다. 따라서 “일단 모든 주소를 system router로
전달한다”는 연결은 Apollo hardware 구조와 현재 QVP contract 모두에
맞지 않는다.

## 2. 현재 구조

```text
                         apollo-qvp.lua
                                |
                  machine_contract.load(hw-block)
                                |
        +-----------------------+-----------------------+
        |                       |                       |
   contract layer          shared context        assembly layer
   topology.lua            config.lua            fabric.lua
   address_map.lua              |                rse.lua
   transaction_routes.lua       |                ap_compute.lua
   signal_routes.lua            |                ros.lua
   boot_control.lua             |                system_mgmt.lua
   software_contract.lua        |                si_cl0.lua
                                                 si_cl1.lua
                                                        |
        +-----------------------+------------------------+
        |                       |                        |
   system_router           ap_router                smd_router
   52-bit system view      52-bit AP view           52-bit SMD view
        |                       |                        |
        +-- NCI/ATU/APU --------+------------------------+
        |
        +-- rse_router       : 32-bit RSE view
        +-- si_cl0_router    : 40-bit SI CL0 view
        +-- si_cl1_router    : 40-bit SI CL1 view

QEMU instances
  ap_qemu_inst     -> Cortex-A720AE CPUs and AP QEMU-backed devices
  rse_qemu_inst    -> Cortex-M55
  si_cl0_qemu_inst -> Cortex-R82 CL0
  si_cl1_qemu_inst -> Cortex-R82 CL1

Memory and inter-domain policy
  RAM/backing      -> SystemC object
  same-domain MMIO -> domain router
  cross-domain     -> explicit NCI, ATU/APU, or static allow-list bridge
```

`router` socket의 관점에서 연결 방향은 다음과 같다.

```text
CPU / DMA / loader
  initiator_socket
          |
          v
  <domain>_router.target_socket
  <domain>_router.initiator_socket
          |
          v
peripheral / memory
  target_socket
```

즉, peripheral의 `target_socket.bind`는 router의
`initiator_socket`을 가리킨다. CPU, DMA 또는 loader와 같은 master의
`initiator_socket.bind`는 router의 `target_socket`을 가리킨다. 이름이
서로 반대로 보일 수 있으므로 새 연결에서 가장 자주 실수하는 부분이다.

## 3. 어떤 종류의 변경인지 먼저 결정

| 추가 대상 | 기존 domain router | 새 bridge | 새 QEMU instance |
| --- | --- | --- | --- |
| 기존 bus의 MMIO peripheral | 사용 | 불필요 | 보통 불필요 |
| 기존 bus의 DMA master | 사용 | DMA가 다른 view를 볼 때만 필요 | 보통 불필요 |
| 두 기존 domain 사이의 window | 양쪽 사용 | 필수 | 불필요 |
| CPU가 없는 새 SystemC subsystem | 새 address view가 있으면 추가 | domain 경계를 넘으면 필수 | 불필요 |
| 독립 CPU, reset, timer를 갖는 subsystem | 보통 전용 router 추가 | 필수 | 보통 필요 |
| 기존 QEMU instance에 속하는 QEMU device | 기존 router 사용 | 필요할 때만 추가 | 추가하지 않음 |

새 QEMU-backed peripheral이라는 이유만으로 QEMU instance를 새로 만들면
안 된다. 같은 CPU domain, address space, reset 및 시간 동기화 정책에
속하면 기존 domain의 QEMU instance를 사용한다.

## 4. 현재 Lua 파일의 역할

### 4.1 진입점

| 파일 | 역할 | 수정하는 경우 |
| --- | --- | --- |
| `apollo-qvp.lua` | full-system 최상위 조립 순서와 live SI mode를 결정한다. contract를 읽고 각 subsystem의 `define()`/`enable()`을 호출한다. | 새 subsystem module을 full-system에 넣거나 subsystem 간 생성 순서를 바꿀 때 |
| `apollo-pc.lua` | `primary_compute.lua`를 실행하는 AP 독립 실행 진입점이다. | AP 단독 실행 경로도 같은 장치를 가져야 할 때 |
| `apollo-si-cl1.lua` | `si_cl1_isolated.lua`를 실행하는 SI CL1 독립 실행 진입점이다. | SI CL1 독립 실행 경로도 같은 장치를 가져야 할 때 |

### 4.2 Machine contract

contract 파일은 현재 별도 directory가 아니라 모두 `hw-block/`에 있다.

| 파일 | 역할 |
| --- | --- |
| `machine_contract.lua` | 아래 여섯 contract를 load하고 domain, view, router, bridge 및 route reference를 교차 검증한다. JSON export 기능도 제공한다. |
| `topology.lua` | domain, address view 폭, router, cross-domain bridge, QEMU instance와 topology validation 정책을 정의한다. |
| `address_map.lua` | 각 range의 base, size, view, target, owner, access, backing, alias, bridge, reset 정책과 근거 문서를 정의한다. |
| `transaction_routes.lua` | CPU, loader, DMA 등의 initiator identity와 domain 간 transaction 경로, access 종류, 오류 응답 정책을 정의한다. |
| `signal_routes.lua` | IRQ/PPI/SPI/MSI, reset, fault 전달 경로와 소유자를 정의한다. |
| `boot_control.lua` | secure boot, ATU/APU 설정, subsystem release 순서와 reset default를 정의한다. |
| `software_contract.lua` | SCMI, PSCI, PFDI, HIPC, FF-A, DTB 등 firmware/software interface와 shared-memory 계약을 정의한다. |
| `export_machine_contract.lua` | contract를 topology, address, transaction, IRQ/reset, boot 및 software JSON 파일로 내보내는 CLI이다. |

### 4.3 실제 platform 조립

| 파일 | 역할 | 주요 object |
| --- | --- | --- |
| `config.lua` | 환경변수, artifact 경로, CPU 수, backend 선택 및 `request_context` ID를 읽어 공통 `ctx`를 만든다. | `config.create()` |
| `fabric.lua` | root fabric과 가장 먼저 필요한 system/SMD router 및 NCI decode를 만든다. | `system_router`, `smd_router`, `system_to_smd_nci` |
| `ap_compute.lua` | AP QEMU instance, CPU, GIC, timer, memory, PCIe/SMMU와 AP view router/bridge를 만든다. | `define()`, `enable_ap_router()` |
| `ros.lua` | Linux가 사용하는 virtio block/network/RNG 등 Rich OS peripheral을 만든다. | `define()`, AP view bind helper |
| `system_mgmt.lua` | SMD/system-owned SRAM, ATU/APU, MHU, counter, reset/power/safety control block을 만든다. | `define()` |
| `rse.lua` | RSE router, M55 QEMU instance, TCM/flash, NVIC, MHU, timer, watchdog 및 system access path를 만든다. | `define()` |
| `si_cl0.lua` | SI CL0의 host-visible object를 먼저 정의하고, live mode에서 R82, GIC, UART, MHU, NCI/APU 및 loader를 활성화한다. | `define()`, `enable()` |
| `si_cl1.lua` | SI CL1의 host-visible object를 먼저 정의하고, live mode에서 R82, GIC, UART, HIPC/PFDI MHU와 loader를 활성화한다. | `define()`, `enable()` |
| `primary_compute.lua` | `apollo-pc.lua`용 독립 AP platform 전체를 한 파일에서 만든다. full-system AP 구현의 원본으로 사용하면 안 된다. | standalone `platform` |
| `si_cl1_isolated.lua` | `apollo-si-cl1.lua`용 독립 SI CL1 platform을 만든다. full-system CL1 경로와 별도이다. | standalone `platform` |

full-system 기능은 subsystem 소유 파일에 추가한다. 예를 들어 AP device는
`ap_compute.lua` 또는 `ros.lua`, SMD control block은 `system_mgmt.lua`,
SI CL0 device는 `si_cl0.lua`가 기본 소유 위치이다. standalone 경로의
파일을 먼저 수정하면 `apollo-qvp.lua`에는 반영되지 않는다.

## 5. 기존 bus에 peripheral 연결

### 5.1 Architecture contract 결정

코드를 쓰기 전에 다음을 확정한다.

- 어느 domain과 address view에서 보이는가
- base, aperture size, register 구현 범위
- Secure/Non-secure 및 owner
- reset 중 access 결과와 reset 이후 보존 여부
- IRQ controller, 종류와 ID
- clock/counter source
- DMA를 수행하는 bus master인지
- firmware, DTB 또는 ACPI가 기대하는 compatible과 주소

근거는 우선 다음 순서로 확인한다.

1. `doc/arm_zena_css_dev_guide/`
2. `arm-zena-css/documentation/`과 FVP 설정
3. firmware, DTS 및 driver source
4. 현재 FVP/QBox boot log

### 5.2 Contract 추가

기존 AP bus에 `example_dev`를 붙이는 최소 contract는 다음과 같다.

1. `address_map.lua`

```lua
{
    name = "ap_example_dev";
    base = 0x...;
    size = 0x...;
    view = "ap";
    target = "ap_example_dev";
    owner = "ap";
    access = "rw";
    scope = architecture;
    source = guide;
};
```

2. device가 interrupt를 발생시키면 `signal_routes.lua`

```lua
{
    name = "ap_example_dev_irq";
    source = "ap_example_dev.irq";
    sink = "ap_gic.spi";
    controller = "ap_gic";
    kind = "SPI";
    id = <architected INTID>;
    owner = "ap";
    scope = "zena_css_architecture";
};
```

3. device가 DMA master이면 `transaction_routes.lua`의 `initiators`와
   `routes`에 identity, requester/stream ID 및 실제 target path를
   추가한다.

MMIO target만 추가하면서 새 domain, router 또는 bridge를
`topology.lua`에 추가할 필요는 없다.

### 5.3 실제 target socket 연결

주소는 가능하면 contract에서 읽어 중복 상수를 줄인다.

```lua
local range = ctx.machine_contract_module.range(
    ctx.machine_contract, "ap_example_dev")

platform.ap_example_dev = {
    moduletype = "example_dev";
    target_socket = {
        address = range.base;
        size = range.size;
        bind = "&ap_router.initiator_socket";
        relative_addresses = false;
    };
    irq = {bind = "&ap_gic.spi_in_<SPI number>"};
}
```

QEMU-backed device가 `ap_qemu_inst`에 속하면 해당 wrapper가 요구하는
`args`도 지정한다.

```lua
args = {"&platform.ap_qemu_inst"};
```

QEMU wrapper마다 MMIO socket 이름이 `target_socket`, `mem` 또는
device-specific 이름일 수 있다. 비슷해 보이는 component의 이름을
추측하지 말고 해당 component의 CCI declaration과 현재 사용 예를
확인한다.

### 5.4 DMA 또는 다른 bus master 연결

master가 AP address view를 사용한다면 master의 initiator를 AP router
입력에 연결한다.

```lua
platform.ap_example_dma = {
    moduletype = "example_dma";
    request_origin_id = ctx.request_context.origin.ap_example_dma;
    request_domain_id = ctx.request_context.domain.ap;
    requester_id = <architected requester ID>;
    initiator_socket = {bind = "&ap_router.target_socket"};
}
```

동시에 `config.lua`의 `request_context.origin`에 충돌하지 않는 origin
ID를 넣고, `transaction_routes.lua`에 같은 identity와 route를
선언한다. SMMU를 통과하는 DMA라면 requester/stream ID, SMMU upstream
socket, event IRQ까지 하나의 경로로 검증해야 한다. 현재 PCIe GPEX DMA
경로가 이 유형의 기준 예이다.

## 6. 기존 domain 사이에 새 bus/window 연결

두 address view가 다르면 router끼리 직접 묶지 않는다. 먼저
`topology.lua`에 bridge의 방향, 종류, owner, width, reset policy를
선언한다.

```lua
{
    name = "source_to_dest_atu_apu";
    from = "source";
    to = "dest";
    kind = "atu_apu";
    owner = "rse";
    width = 40;
    reset_policy = "deny_until_rse_programmed";
    scope = "zena_css_architecture";
};
```

그 후 다음을 함께 추가한다.

- `address_map.lua`: source view의 aperture와 destination target
- `transaction_routes.lua`: initiator, from/to, target, bridge, reset 및
  programmed access 정책
- `boot_control.lua`: 누가 bridge를 설정하고 언제 source subsystem을
  release하는지
- 실제 owning module: ATU/APU/NCI/`addrtr` object와 양쪽 socket

정적인 주소 변환의 기본 socket 형태는 다음과 같다.

```lua
platform.source_to_dest_bridge = {
    moduletype = "addrtr";
    mapped_base_addr = DEST_BASE;
    target_socket = {
        address = SOURCE_APERTURE_BASE;
        size = SOURCE_APERTURE_SIZE;
        bind = "&source_router.initiator_socket";
        relative_addresses = false;
    };
    initiator_socket = {bind = "&dest_router.target_socket"};
}
```

현재 `fabric.lua`의 `system_to_smd_nci`가 이 방향의 간단한 예이다.
보안 및 runtime programming이 필요한 실제 ATU/APU 경로는 단순
`addrtr`로 대체하지 말고 `system_mgmt.lua`의 `host_ap_atu`처럼 정책
component와 request context를 사용한다.

다음 형태는 금지한다.

```lua
-- 잘못된 예: source의 거의 모든 주소를 destination에 넘긴다.
target_socket = {
    address = 0x0;
    size = 0x10000000000;
    bind = "&source_router.initiator_socket";
};
initiator_socket = {bind = "&dest_router.target_socket"};
```

이 방식은 unmapped access의 DECERR, security ownership, reset-time deny
정책 및 address-view 격리를 모두 무너뜨릴 수 있다.

## 7. 새 subsystem 연결

독립 CPU, address space, reset 및 timer 정책을 가진 subsystem은 다음
순서로 추가한다.

### 7.1 Domain과 view

`topology.lua`에 다음을 정의한다.

- `domains`: subsystem owner
- `views`: 물리 주소 폭
- `routers`: 전용 router와 CCI path
- `bridges`: 기존 system/SMD/AP와 연결되는 허용 경로
- `qemu_instances`: CPU가 QEMU-backed일 때 architecture, CPU, TCG,
  sync policy 및 RAM owner

CPU가 없고 기존 system view 안의 peripheral group일 뿐이면 새 domain과
QEMU instance를 만들지 않는다.

### 7.2 Subsystem module

새 `hw-block/<subsystem>.lua`는 다음 형태를 권장한다.

```lua
local subsystem = {}

function subsystem.define(ctx, platform)
    -- 다른 domain에서도 보여야 하며 CPU 실행 전부터 존재해야 하는
    -- SRAM, power/reset control, mailbox frame 등을 정의한다.
end

function subsystem.enable(ctx, platform)
    -- live CPU mode에서만 필요한 router, QEMU instance, CPU, GIC/NVIC,
    -- local peripheral와 loader를 정의한다.
end

return subsystem
```

SI CL0/CL1처럼 reset-held 상태에서도 다른 firmware가 control/status
register 또는 shared memory를 읽어야 하면 그 object는 `define()`에
둔다. CPU와 local GIC처럼 live 실행에만 필요한 object는 `enable()`에
둔다.

### 7.3 최상위 조립

`apollo-qvp.lua`에서 module을 load하고 `ctx.modules`에 등록한 뒤,
dependency가 준비되는 순서로 조립한다.

```lua
local subsystem = dofile(apollo_dir.."hw-block/subsystem.lua")

ctx.modules.subsystem = subsystem

subsystem.define(ctx, platform)
if ctx.subsystem_live then
    subsystem.enable(ctx, platform)
end
```

순서는 단순한 파일 정리가 아니다. Lua `bind`가 참조하는 object와
firmware boot owner가 먼저 정의되어야 한다. 현재 full-system은 root
fabric, RSE/AP/RoS/SMD, AP router, SI host-visible block, SI live CPU
순으로 조립한다.

### 7.4 QEMU instance와 시간

새 QEMU instance를 추가할 때는 다음을 반드시 함께 검토한다.

- domain별 CPU model과 architecture
- single/multi-thread TCG mode
- QBox/SystemC quantum과 sync policy
- generic timer 또는 local counter source
- reset assert/release owner
- interrupt controller와 CPU IRQ/FIQ/VIRQ/VFIQ 연결
- SystemC RAM의 target socket

QEMU instance 사이에서 RAM을 QEMU 내부 RAM으로 복제하면 shared-memory
일관성이 깨진다. 현재 contract처럼 SystemC memory를 단일 backing으로
두고 각 domain은 허용된 bridge를 통해 접근한다.

### 7.5 Firmware와 software 계약

hardware 연결만으로 완료되지 않는다.

- DTB/DTS 또는 firmware platform address와 IRQ가 contract와 일치해야
  한다.
- SCP/TF-M/TF-A/Zephyr/Linux 중 실제 owner와 초기화 주체를
  `boot_control.lua`에 반영한다.
- SCMI, PFDI, HIPC, RPMsg 같은 protocol 또는 shared memory가 추가되면
  `software_contract.lua`에 producer, consumer, transport, reset 및
  error recovery를 기록한다.
- reset 중 request, malformed descriptor, timeout 및 peer offline 경로를
  정의한다.

## 8. Component를 어디에 구현할지

연결 전에 기존 `moduletype`을 먼저 찾는다.

- 이미 있는 component: qbox-platform Lua에서 재사용한다.
- Apollo 전용 SystemC/TLM component: 우선
  `hsoc-stack/tools/qbox-platform/`에 구현하고 component test를 둔다.
- 여러 platform에서 재사용 가능한 일반 component: QBox core
  `hsoc-stack/tools/qbox/`의 기존 component 구조와 upstream 가능성을
  검토한다.
- 기존 QEMU device를 사용하는 wrapper: 기존 QBox QEMU wrapper를
  재사용한다.
- QEMU 자체에 없는 device behavior: libqemu/QEMU 변경이 정말 필요한지
  확인한 뒤 `hsoc-stack/tools/qemu/`를 수정한다.

새 build target이 필요하면 qbox-platform `CMakeLists.txt`의
`QBOX_APOLLO_REQUIRED_TARGETS`와 `apollo_fvp_full_system` dependency에
포함되는지 확인한다. Lua의 `moduletype` 문자열만 추가하고 shared
library가 build/package되지 않으면 runtime에서 module load가 실패한다.

## 9. Contract export와 검증

### 9.1 Contract load 및 JSON export

Lua interpreter가 있는 환경에서 다음과 같이 contract를 load하고
JSON을 생성한다.

```bash
mkdir -p build/qbox-apollo-contract

lua \
  hsoc-stack/tools/qbox-platform/platforms/apollo/hw-block/export_machine_contract.lua \
  --contract-dir \
  hsoc-stack/tools/qbox-platform/platforms/apollo/hw-block \
  --out-dir build/qbox-apollo-contract
```

`apollo-qvp.lua`는 `machine_contract.load()`를 validation 활성 상태로
호출한다. export script는 직렬화용이므로 `load(..., false)`를
사용한다. 따라서 export 성공만으로 cross-reference validation이
완료됐다고 판단하지 않는다.

### 9.2 정적 검사

```bash
python3 scripts/test/validate_qbox_apollo_fvp_full_map.py
python3 scripts/test/validate_qbox_apollo_topology.py
python3 scripts/test/audit_qbox_core_boundary.py
git -C hsoc-stack/tools/qbox-platform diff --check
```

다음도 사람이 확인한다.

- contract range와 실제 Lua socket의 base/size가 같은가
- target socket은 올바른 domain router의 `initiator_socket`에
  연결됐는가
- master socket은 올바른 router의 `target_socket`에 연결됐는가
- cross-domain access가 명시된 bridge를 통과하는가
- IRQ source, controller, kind, INTID와 실제 signal bind가 같은가
- request origin/domain/requester/stream ID가 충돌하지 않는가
- reset 전 access가 contract의 allow/deny 정책과 같은가

### 9.3 Build 및 component test

```bash
./local_build.sh qbox --qbox-unit-tests
```

targeted build가 필요하면 active QBox platform build directory에서
다음 형태를 사용한다.

```bash
cmake --build build/local-apollo-qvp/work/qbox-platform \
  --target apollo_fvp_full_system \
  --parallel "$(nproc)"
```

### 9.4 Full-system runtime

```bash
python3 scripts/run/run_qbox_apollo_fvp_full.py \
  --si-mode live-cl0-cl1 \
  --timeout 600 \
  --out-dir build/qbox-apollo-fvp/<run-id>

python3 scripts/test/audit_qbox_apollo_fvp_full_coverage.py \
  --result-json build/qbox-apollo-fvp/<run-id>/result.json \
  --output build/qbox-apollo-fvp/<run-id>/full-coverage-audit.json
```

새 device는 단순 boot 성공 외에도 다음 증거를 남겨야 한다.

- firmware 또는 Linux driver probe
- register read/write와 reset value
- IRQ delivery 및 clear
- DMA라면 data 이동, requester/stream ID와 SMMU fault 경로
- cross-domain이면 reset-time deny와 programmed allow
- reset 후 preserved/cleared state
- unmapped 또는 권한 없는 access의 bounded error response

## 10. 연결 완료 체크리스트

- [ ] Arm guide/FVP/firmware/DTS 근거로 address, IRQ, owner를 확정했다.
- [ ] 기존 domain에 붙일지 새 domain을 만들지 결정했다.
- [ ] `topology.lua`의 domain/view/router/bridge가 실제 구조와 일치한다.
- [ ] `address_map.lua`의 base/size/view/target/backing이 실제 Lua와 같다.
- [ ] 모든 master가 `transaction_routes.lua`와 `request_context` identity를
      가진다.
- [ ] IRQ, reset 및 fault가 `signal_routes.lua`와 실제 bind에서 같다.
- [ ] boot/release owner를 `boot_control.lua`에 반영했다.
- [ ] firmware interface와 shared memory를 `software_contract.lua`에
      반영했다.
- [ ] subsystem 소유 module에 실제 object와 socket을 구현했다.
- [ ] 필요한 component target이 build와 package에 포함된다.
- [ ] static map/topology/boundary 검사가 통과한다.
- [ ] component test와 full-system runtime evidence가 통과한다.

가장 중요한 판정 기준은 “guest가 우연히 boot하는가”가 아니라, 올바른
address view와 policy bridge를 통해 요청이 전달되고 잘못된 요청은
hardware contract에 맞게 거부되는가이다.
