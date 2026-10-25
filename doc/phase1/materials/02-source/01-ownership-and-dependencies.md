# 02.1 Repository ownership과 domain dependency

[상위 장](../02-project-source-architecture.md) · [← 이전](../02-project-source-architecture.md) · [다음 →](02-build-source-contracts.md)

> 목적: source의 Git owner, 실행 domain, product 구성의 관계를 구분하고 기능 조사 시작점을 정한다.
> 기준: 2026-10-25 checkout의 source·metadata 정적 추적. 새 BitBake 실행이나 runtime 검증 결과를 의미하지 않는다.

## 1. Workspace와 hardware domain

| 구역 | 무엇을 소유하는가 | 처음 읽을 곳 |
|---|---|---|
| Root repository | source revision pin, build/run wrapper, 통합 test와 문서 | [.gitmodules](../../../../.gitmodules), [AGENTS.md](../../../../AGENTS.md), [scripts/](../../../../scripts/) |
| `arm-zena-css/` | RD-Aspen reference BSP, SI module, boot/hardware 계약 | [documentation/design/](../../../../arm-zena-css/documentation/design/) |
| `sw-ref-stack/` | Automotive software stack, 공통 image/demo/test metadata | [yocto/meta-arm-auto-solutions/](../../../../sw-ref-stack/yocto/meta-arm-auto-solutions/) |
| `hsoc-stack/components/` | AP/RSE/SI에서 실행할 firmware와 OS | [primary_compute/](../../../../hsoc-stack/components/primary_compute/), [system_mgmt/](../../../../hsoc-stack/components/system_mgmt/) |
| `hsoc-stack/tools/` | 개발 host에서 실행할 simulator와 model | [qbox/](../../../../hsoc-stack/tools/qbox/), [qbox-platform/](../../../../hsoc-stack/tools/qbox-platform/), [qemu/](../../../../hsoc-stack/tools/qemu/) |
| `hsoc-stack/yocto/` | Apollo BSP·source 연결 및 Nexios 제품 정책 | [meta-hsoc-bsp/](../../../../hsoc-stack/yocto/meta-hsoc-bsp/), [meta-hsoc-auto-solutions/](../../../../hsoc-stack/yocto/meta-hsoc-auto-solutions/) |
| `layers/` | Poky와 외부 Yocto layer | [poky/](../../../../layers/poky/), [meta-arm/](../../../../layers/meta-arm/) |
| `build/` | local configuration, generated binary/log/runtime state | `conf/`, `tmp_baremetal/`, `qbox-apollo-qvp/` |

**발표 포인트:** top-level checkout은 실행 바이너리 하나의 source tree가 아니다. 여러 CPU의 software와 host simulator를 맞춰 놓는 통합 workspace다.

### Hardware 그림에서 source 영역을 찾기

![Arm reference Compute Complex — native draw.io 재작성](../figures/reference/aspen_compute_complex.drawio.svg)

[draw.io 편집 원본](../figures/reference/aspen_compute_complex.drawio)

*그림 2-1. Native draw.io 재작성. 기준: Arm [원본 PNG](../../../../arm-zena-css/documentation/images/aspen_compute_complex.png) — [Components / System Block Diagram](../../../../arm-zena-css/documentation/design/components.rst). AP의 CPU/GIC/CMN, RSE, Safety Island가 별도 block으로 배치된 이유를 먼저 본다. 이 그림은 reference hardware decomposition이며, Apollo QVP가 모든 회로·debug block을 같은 fidelity로 구현했다는 의미는 아니다.*

AP의 Linux만 실행해도 플랫폼 전체가 동작하는 것은 아니다. AP의 전원과 reset을 제어하는 CL0, AP보다 먼저 boot하는 RSE, 독립 RTOS를 실행하는 CL1이 각각 살아 있어야 한다.
그 결과 source tree도 AP OS와 system-management firmware를 분리한다. `primary_compute/`와 `system_mgmt/`는 이 실행 책임을 드러내는 구분이다.

반면 그림의 GIC·MHU·timer 같은 IP 하나가 Git repository 하나와 대응하지는 않는다.
동일 IP에 대해 guest driver는 Linux/firmware에, register와 IRQ 동작은 QEMU/SystemC model에, 주소와 연결은 Lua/DTS에 존재한다.
**Hardware block의 기능을 바꾸는 작업은 여러 source의 계약을 맞추는 작업**이 된다.

| 그림의 대상 | Guest-side 구현 | Host/model-side 구현 | 양쪽이 맞춰야 할 계약 |
|---|---|---|---|
| AP CPU·GIC | Linux IRQ/CPU 코드, TF-A EL3 | QEMU CPU/GIC, QBox CPU bridge | Architecture, CPU population, INTID |
| RSE | TF-M boot/runtime | RSE CPU, crypto·OTP·memory model | Image layout, MMIO, secure service transport |
| Safety Island | SCP CL0 + Zephyr CL1 | SI CPU/GIC/PPU/MHU | Boot entry, GIC view, IRQ, shared memory |
| Interconnect / memory | Firmware memory map, DTS, linker script | Lua map, router, memory/ATU model | Address space, region size, access permission |

Arm [Overview / Software components·Platform IP](../../../../arm-zena-css/documentation/overview.rst)는 이 구분의 출발점이다.
Apollo는 이를 유지하면서 `qbox-platform/`에 QVP 구현, HSOC layer에 local source와 product 선택을 추가한다.

## 2. Git 경계와 directory 경계는 다르다

| 구분 | 관리되는 정보 | 변경 시 작업 위치 |
|---|---|---|
| Component repository | 해당 component의 실제 source commit | Linux/QBox/SCP 등 소유 repository |
| Root gitlink | 조합에 사용할 component commit SHA | root repository |
| `.gitmodules` | submodule 경로·remote·추적 branch 설정 | root repository |
| Generated artifact | 특정 설정에서 만들어진 결과 | rebuild/deploy 대상; 일반 source commit 대상 아님 |

`.gitmodules`의 `branch`는 현재 checkout commit의 증거가 아니다. 고정 조합은 root gitlink와 실제 nested `HEAD`를 함께 확인한다.

```bash
git status --short
git submodule status
git -C hsoc-stack/tools/qbox-platform rev-parse --show-toplevel
git -C hsoc-stack/tools/qbox-platform rev-parse HEAD
```

`arm-zena-css/`는 externally managed reference다. Apollo 변경은 소유 source와 HSOC metadata에서 처리한다.
`layers/`의 외부 layer를 직접 수정하기 전에는 HSOC `.bbappend` 또는 component 수정으로 표현할 수 있는지 확인한다.
관련 정책의 근거는 [root AGENTS.md](../../../../AGENTS.md)의 `Ownership`이다.

## 3. Guest software source: 실행 domain으로 찾는다

| 실행 domain | Component repository | 내부에서 먼저 볼 영역 | 대표 소비자 |
|---|---|---|---|
| AP Normal world | [Linux](../../../../hsoc-stack/components/primary_compute/linux/) | `arch/arm64/boot/dts/hsoc/`, `drivers/`, `arch/arm64/configs/` | Kernel/DTB/modules, UKI와 rootfs |
| AP boot | [U-Boot](../../../../hsoc-stack/components/primary_compute/u-boot/) | `configs/`, `board/`, `drivers/`, boot environment | TF-A의 BL33/FIP |
| AP EL3 / early boot | [TF-A](../../../../hsoc-stack/components/primary_compute/trusted-firmware-a/) | `plat/arm/board/automotive_rd/`, `services/`, `drivers/` | AP BL2, BL31, FIP |
| AP Secure world | [OP-TEE](../../../../hsoc-stack/components/primary_compute/optee_os/) | `core/`, platform와 SPMC 구성 | TF-A BL32, Trusted Services SP |
| RSE | [TF-M](../../../../hsoc-stack/components/system_mgmt/trusted-firmware-m/) | `platform/ext/target/arm/rse/automotive_rd/`, `secure_fw/`, `bl2/` | RSE boot/runtime image |
| SI CL0 | [SCP-firmware](../../../../hsoc-stack/components/system_mgmt/scp-firmware/) | `product/automotive-rd/`, `module/`, `framework/` | SI0 firmware, SCMI·power·fault service |
| SI CL1 | [Zephyr](../../../../hsoc-stack/components/system_mgmt/zephyrproject/zephyr/) | `kernel/`, `arch/arm64/`, `drivers/`, `subsys/` | CL1 integrated Zephyr image |
| SI CL1 board/module | [zephyr_hsoc_src](../../../../hsoc-stack/components/system_mgmt/zephyrproject/zephyr_hsoc_src/) | `boards/hsoc/`, module/driver 설정 | Apollo board, overlay, HIPC/PFDI 연결 |
| Board vMCU companion | [zephyr_vmcu_src](../../../../hsoc-stack/components/system_mgmt/zephyrproject/zephyr_vmcu_src/) | vMCU application과 board 설정 | 외부 companion image |

Source directory와 실행 domain을 1:1로 고정하지 않는다. TF-A처럼 여러 boot stage를 만드는 component가 있고, CL1처럼 여러 source tree를 조합해 하나의 image를 만드는 경우도 있다.

### System Management를 TF-M 하나로 묶을 수 없는 이유

![Arm reference System Management Block — native draw.io 재작성](../figures/reference/aspen_system_management_block.drawio.svg)

[draw.io 편집 원본](../figures/reference/aspen_system_management_block.drawio)

*그림 2-2. Native draw.io 재작성. 기준: Arm [원본 PNG](../../../../arm-zena-css/documentation/images/aspen_system_management_block.png) — [Components / System Management Block](../../../../arm-zena-css/documentation/design/components.rst). RSE와 Safety Island는 같은 management 영역 안에 있지만 CPU architecture와 실행 책임이 다르다. 그림의 CC-315·debug 회로 등은 reference IP이며, Apollo의 model 구현 범위는 별도로 확인한다.*

RSE의 TF-M은 Root of Trust와 secure service를 담당한다. SI CL0의 SCP는 CMN·power·clock을 제어하며 다른 domain을 기동한다.
SI CL1의 Zephyr는 SMP RTOS와 HIPC/PFDI application을 실행한다. 같은 management block 안에서도 **security service, platform control, real-time service**가 다른 runtime에 배치된다.
따라서 공통 `system_mgmt/` 아래에 두더라도 세 firmware를 같은 library처럼 link하지 않는다. MHU/SCMI/shared memory로 연결한다.

| Component | Generic framework | Apollo-specific 시작점 | Framework와 platform의 결합 |
|---|---|---|---|
| TF-M | `secure_fw/`의 SPM/partition | [apollo-qvp target](../../../../hsoc-stack/components/system_mgmt/trusted-firmware-m/platform/ext/target/arm/rse/automotive_rd/apollo-qvp/) | Target CMake/config, memory map, manifest와 platform driver |
| SCP | `framework/`, reusable `module/` | [apollo-qvp product](../../../../hsoc-stack/components/system_mgmt/scp-firmware/product/automotive-rd/apollo-qvp/) | `Firmware.cmake`가 module 집합, `config_*.c`가 instance와 binding 선택 |
| Zephyr | `kernel/`, common driver/subsystem | [Apollo CL1 board](../../../../hsoc-stack/components/system_mgmt/zephyrproject/zephyr_hsoc_src/boards/hsoc/apollo_qvp_safety_island_c1/) | Board DTS/Kconfig + external module + application CMake |

예를 들어 SCP의 SCMI channel을 조사할 때 generic `module/scmi/`만 읽으면 실제 agent 구성을 알 수 없다.
Product의 [config_scmi.c](../../../../hsoc-stack/components/system_mgmt/scp-firmware/product/automotive-rd/apollo-qvp/si0_ramfw/config_scmi.c), [config_transport.c](../../../../hsoc-stack/components/system_mgmt/scp-firmware/product/automotive-rd/apollo-qvp/si0_ramfw/config_transport.c), [config_mhu3.c](../../../../hsoc-stack/components/system_mgmt/scp-firmware/product/automotive-rd/apollo-qvp/si0_ramfw/config_mhu3.c)를 함께 읽어야 protocol→shared memory→doorbell의 실제 경로가 보인다.

## 4. Host simulator source: QEMU, QBox, Apollo overlay를 구분한다

| Source | 맡는 책임 | 대표 변경 |
|---|---|---|
| [QEMU/libqemu](../../../../hsoc-stack/tools/qemu/) | CPU execution, QEMU device, MemoryRegion, QOM | CPU/GIC/QEMU device 동작 |
| [QBox core](../../../../hsoc-stack/tools/qbox/) | SystemC/TLM 연계, QEMU bridge, 공통 component·실행 infrastructure | transport, DMI, synchronization, reusable model |
| [QBox Apollo overlay](../../../../hsoc-stack/tools/qbox-platform/) | Apollo model, Lua composition, board wiring, platform tests | GIC/MHU/PPU/fault 연결, SoC/VP/board 구성 |
| [Root runtime tooling](../../../../scripts/run/) | deploy 선택, process 관리, runtime 관측·결과 수집 | launcher, image mapping, boot/probe policy |

[Overlay CMakeLists.txt](../../../../hsoc-stack/tools/qbox-platform/CMakeLists.txt)는 `QBOX_CORE_SOURCE_DIR`를 통해 core를 `add_subdirectory`로 연결한다.
Yocto provider는 `QBOX_USE_SYSTEM_LIBQEMU=ON`으로 별도 native recipe가 준비한 libqemu를 사용한다.
이때 “system libqemu”는 개발 PC에 임의 설치한 binary를 뜻하지 않고 **Yocto dependency sysroot에 제공된 package**를 가리킨다.

| Overlay 내부 | 의미 | 세미나에서 연결할 질문 |
|---|---|---|
| `systemc-components/` | SystemC/TLM model | MMIO·IRQ·reset 동작은 어디에 구현되는가? |
| `qemu-components/` | QEMU-backed component 연결 | QEMU model을 platform에 어떻게 노출하는가? |
| `platforms/apollo/soc/` | SoC/domain 구성과 hardware contract | 어떤 domain과 address/IRQ 구조인가? |
| `platforms/apollo/vp/` | Virtual platform 구현·backend 연결 | host resource와 loader는 어떻게 붙는가? |
| `platforms/apollo/board/` | Board 주변 연결 | SoC 밖의 device와 companion은 무엇인가? |
| `patch-qbox/` | Archived patch candidates | 현재 build가 자동 적용하는 source로 취급하지 않음 |

세부 runtime composition은 [04. QBox 실행 구조](../04-qbox-runtime-and-lua.md)에서 이어서 설명한다.


## 5. Repository를 찾은 다음 interface owner를 찾는다

하나의 기능에는 **구현 owner**와 **구성 owner**가 함께 있다. Linux driver는 Linux API를 구현하지만, 같은 IP의 address·IRQ는 DTS와 Lua에서 선택되고, firmware service는 다른 CPU의 source에서 제공될 수 있다. 따라서 directory 검색의 결과를 바로 수정 대상 목록으로 쓰지 않는다. 먼저 실행 위치와 consumer를 적는다.

| 조사 단계 | 확인할 내용 | Apollo 사례 |
|---|---|---|
| 실행 주체 | Host process인가, AP/RSE/CL0/CL1인가? | `platforms-vp`는 host, `si0_ramfw.bin`은 CL0 |
| Generic 구현 | Protocol·driver·framework의 재사용 부분 | SCP `module/scmi/`, Linux mailbox framework |
| Product/board 구성 | 실제 instance·channel·CPU·memory 선택 | SCP `si0_ramfw/config_*.c`, CL1 board DTS |
| Integration | 선택한 source·config·binary를 연결 | HSOC `.bbappend`, QVP Lua, `.qboxconf` |
| 소비 지점 | Binary 또는 API를 실제 읽는 다음 단계 | TF-A가 BL32/BL33, launcher가 installed Lua 소비 |

예를 들어 SCP [config_scmi.c](../../../../hsoc-stack/components/system_mgmt/scp-firmware/product/automotive-rd/apollo-qvp/si0_ramfw/config_scmi.c)의 `service_table`은 각 service에 `transport_id`, `transport_api_id`, `scmi_agent_id`를 지정한다. 이 table의 index는 MMIO address가 아니다. 다음 [config_transport.c](../../../../hsoc-stack/components/system_mgmt/scp-firmware/product/automotive-rd/apollo-qvp/si0_ramfw/config_transport.c)의 `element_table`에서 shared-memory address와 MHU `driver_id`를 찾고, `config_mhu3.c`에서 endpoint를 따라가야 한다.

```text
SCMI service / agent
  config_scmi.c: service_table[].transport_id
    → config_transport.c: element_table[].out_band_mailbox_address
    → element_table[].driver_id (module / element / subelement)
    → config_mhu3.c: MHU instance와 doorbell
    → 상대 domain의 driver + Lua MMIO/IRQ 연결
```

이 읽기 순서는 header의 enum 값, protocol ID, MHU channel, interrupt number를 혼동하지 않게 한다. 이름이 같은 `SCMI` 파일이라도 generic message 처리와 product binding은 서로 다른 책임이다.

## 6. Source tree를 읽을 때 자주 생기는 진단 오류

| 보이는 상황 | 먼저 나눌 경계 | 확인할 근거 |
|---|---|---|
| `hsoc-stack/`에서 수정했는데 root diff가 gitlink만 보임 | Nested repository source와 root pin | `git -C <component> rev-parse --show-toplevel`, 해당 repo diff |
| Generic module은 있는데 기능이 동작하지 않음 | Module 존재와 product 포함·binding | `Firmware.cmake`, `config_*.c`, generated module list |
| Linux tree에서 `arm,si-rproc` driver를 찾지 못함 | In-tree driver와 외부 kernel module | [arm-si-rproc-mod.bb](../../../../sw-ref-stack/yocto/meta-arm-auto-solutions/recipes-kernel/hipc-mod/arm-si-rproc-mod.bb)의 `file://src` |
| QBox model 수정 후 실행이 그대로임 | Checkout과 native provider install | Provider `.env`, installed module/Lua 경로 |
| Reference 그림에 있는 IP의 source가 없음 | Reference hardware와 QVP 구현 범위 | Apollo Lua instance와 model registration |

`sw-ref-stack/components/primary_compute/linux_drivers/`는 마지막 사례와 함께 기억할 예외다. `arm_si_rproc_mod`와 `rpmsg_net_mod`는 AP Linux에서 실행되지만 local Linux repository 밖의 source를 `inherit module` recipe로 build한다. Guest domain만 보고 Git owner를 결정할 수 없다는 실제 예다.

## 7. Source 읽기 순서

1. [Root .gitmodules](../../../../.gitmodules)로 repository 경계와 pin 대상을 확인한다.
2. [BSP layer.conf](../../../../hsoc-stack/yocto/meta-hsoc-bsp/conf/layer.conf)의 `HSOC_APOLLO_*_SRC`로 active local path를 찾는다.
3. Guest는 domain의 platform/product/board부터, host는 [overlay CMakeLists.txt](../../../../hsoc-stack/tools/qbox-platform/CMakeLists.txt)의 `QBOX_CORE_SOURCE_DIR`와 required targets부터 읽는다.
4. Framework 구현으로 내려가기 전에 config가 지정한 endpoint·API·artifact consumer를 적는다.

세미나에서는 “SCMI 기능을 바꾸려면 어느 repository인가?”에 한 파일만 답하지 말고, **SCP product → transport → 상대 client → model wiring**까지 설명해 본다.

## 다음 읽기

[02.2. Build source contract](02-build-source-contracts.md)에서 이 directory 중 실제 build input으로 선택되는 source와 생성물을 구분한다.

[상위 장](../02-project-source-architecture.md) · [← 이전](../02-project-source-architecture.md) · [다음 →](02-build-source-contracts.md)
