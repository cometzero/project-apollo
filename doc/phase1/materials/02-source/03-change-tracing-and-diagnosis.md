# 02.3 Change trace·HIPC 사례·실패 진단

[상위 장](../02-project-source-architecture.md) · [← 이전](02-build-source-contracts.md) · [다음 →](../03-project-build-architecture.md)

> 목적: 하나의 기능 변경을 source owner에서 실행 consumer와 검증 표면까지 추적한다.
> 기준: 2026-10-25 checkout의 source·metadata 정적 추적. 새 BitBake 실행이나 runtime 검증 결과를 의미하지 않는다.

## 1. 변경 요청을 source·consumer·test에 연결한다

| 요청 사례 | 1차 source owner | 함께 확인할 consumer/config | 검증 표면 |
|---|---|---|---|
| Linux에서 새 device 사용 | Linux driver/DTS | BSP kernel config, QBox MMIO/IRQ, UKI DTB | probe, 실제 traffic/IRQ, error path |
| MHU mailbox 동작 수정 | Model 또는 해당 firmware driver | 양쪽 endpoint, channel, IRQ, shared memory | 송수신/ACK/재시도, 상대 domain 관측 |
| SCMI service 확장 | SCP module/product | TF-A/Linux/Zephyr client와 MHU transport | 요청·응답·상태 변화 |
| QBox scheduling 수정 | QBox core | domain timing, WFI/timer/IRQ, runtime policy | unit test + 실제 boot/workload |
| Boot image 선택 변경 | HSOC metadata/root launcher | `.qboxconf`, loader, Flash·UKI consumer | 선택 artifact identity와 boot 단계 |
| 제품 package 추가 | Product layer | rootfs, initramfs, image manifest | package 포함 + service 동작 |

검증 코드도 소유권이 나뉜다.

| 검증 위치 | 주로 확인하는 것 | 주장할 수 없는 것 |
|---|---|---|
| [tests/](../../../../tests/) | Root script, configuration/contract, static integration | 모든 guest driver 동작 |
| QBox core/overlay test | Model API와 bounded behavior | 실제 hardware timing·safety qualification |
| [qa-tests/](../../../../qa-tests/) | Platform별 test automation와 runtime checks | 실행하지 않은 suite의 PASS |
| [BSP OEQA](../../../../hsoc-stack/yocto/meta-hsoc-bsp/lib/oeqa/) | Yocto target/test integration | QVP machine 이름만으로 QBox backend 사용 |
| `build/qbox-apollo-qvp/` | 실제 실행에서 생성된 log/report | 다른 source revision의 현재 동작 |

**발표 사례:** Linux MHU driver 변경은 Linux repository에서 시작하지만, DT의 `mboxes`, QBox endpoint wiring, CL1 callback, 해당 image의 실제 DTB까지 연결해야 끝난다.

### 사례 C. HIPC 기능을 따라 source를 읽는 방법

![Arm reference의 HIPC baremetal 구성](../figures/reference/hipc_baremetal_design.drawio.svg)

[draw.io 편집 원본](../figures/reference/hipc_baremetal_design.drawio)

*그림 2-4. Arm [원본 SVG](../../../../arm-zena-css/documentation/images/hipc_baremetal_design.svg) — [HIPC / HIPC Baremetal Architecture](../../../../arm-zena-css/documentation/design/hipc.rst). Linux와 Zephyr를 shared-memory data path와 MHU notification으로 연결한다. Apollo에서는 Linux remoteproc/RPMsg, HSOC CL1 board, Arm SI module의 generated copy, QVP MHU·memory wiring을 함께 추적한다.*

이 기능은 하나의 “HIPC library”만 찾으면 끝나지 않는다. Linux의 remoteproc은 이미 boot한 CL1에 attach하고, RPMsg/OpenAMP는 resource table과 vring을 해석하며, MHU는 data 자체 대신 알림을 전달한다.
Shared memory의 위치·크기·cache 속성과 mailbox channel이 맞아야 양쪽 driver가 같은 buffer를 볼 수 있다.

| 확인 순서 | 먼저 확인할 사실 | 다음 source로 넘어가는 기준 |
|---|---|---|
| 1. 상대 domain | CL1이 integrated image로 boot했는가? | Firmware/loader와 CL1 console |
| 2. Description | Linux DT와 CL1 DTS가 같은 memory/channel을 가리키는가? | Board DTS와 QVP Lua map |
| 3. Attach | Resource table/vring을 host가 인식하는가? | Linux remoteproc·RPMsg |
| 4. Notification | Doorbell IRQ와 ACK가 양쪽에서 발생하는가? | MHU model와 양쪽 mailbox driver |
| 5. Service | Endpoint 생성 후 application 메시지가 왕복하는가? | Zephyr SI application 및 Linux consumer |

현재 CL1 common include의 `0001-veth-restore-resource-table-on-reattach.patch`는 3번과 연결된 사례다.
Runtime reconnect 의미를 유지하려면 Arm module의 application state와 Linux attach consumer를 함께 봐야 하며, 이를 위해 reference를 직접 고치는 대신 generated module copy를 patch한다.

## 2. 재현할 때 기록할 최소 단위

| 기록 | 이유 |
|---|---|
| Root SHA + nested repository SHA | 통합 조합과 실제 구현 revision 식별 |
| Local diff / dirty 상태 | Commit에 없는 source 변경 식별 |
| MACHINE, DISTRO, variant, CPU count | Hardware/software configuration 일치 |
| Recipe·config·defconfig/fragment | 같은 source의 다른 build 결과 구분 |
| Deploy 경로와 artifact identity | 실제 실행한 image 식별 |
| Native provider와 installed Lua 경로 | 수정한 simulator가 실행됐는지 확인 |
| Command, timestamp, log/report | 검증 결과의 범위 추적 |

이 장의 확인은 현재 source·metadata의 **정적 추적**이다. Codebase index는 일부 경로가 partial/changed 상태여서 해당 파일을 직접 읽어 보완했다.
Runtime PASS, FVP parity 또는 hardware qualification을 새로 주장하지 않는다.


## 3. HIPC를 실제 함수까지 따라가는 사례

목표를 “CL1과 통신한다”로만 적으면 boot, attach, virtqueue, application의 실패를 구분하기 어렵다. 다음 trace는 **이미 boot한 CL1에 AP Linux가 attach한다**는 계약을 기준으로 source를 읽는다.

| 단계 | 실제 source·symbol | 수행하는 일 | 다음 단계가 요구하는 결과 |
|---|---|---|---|
| Module 공급 | [arm-si-rproc-mod.bb](../../../../sw-ref-stack/yocto/meta-arm-auto-solutions/recipes-kernel/hipc-mod/arm-si-rproc-mod.bb), `SRC_URI`, `inherit module` | `sw-ref-stack`의 외부 driver source를 kernel module로 build | 같은 kernel에 맞는 `.ko`와 package |
| Device 발견 | [arm_si_rproc.c](../../../../sw-ref-stack/components/primary_compute/linux_drivers/arm_si_rproc_mod/src/arm_si_rproc.c), `arm_si_rproc_probe()` / `arm_si_rproc_init()` | DT의 available SI channel을 열거 | Channel별 remoteproc instance |
| Attach handshake | 같은 파일, `arm_si_add_rproc_core()` | `RPROC_DETACHED` 설정, mailbox 확보, attach 송신, ACK 대기 | CL1이 resource를 준비했다는 ACK |
| Resource 해석 | `arm_si_rproc_prepare()`, `arm_si_rproc_get_loaded_rsc_table()` | Reserved memory와 이미 적재된 resource table 사용 | Virtio/RPMsg가 사용할 memory·vring |
| Data notification | `arm_si_rproc_kick()` | vqid에 대응하는 mailbox로 알림 | CL1 OpenAMP가 새 queue entry 처리 |
| Network consumer | [rpmsg-net-mod.bb](../../../../sw-ref-stack/yocto/meta-arm-auto-solutions/recipes-kernel/hipc-mod/rpmsg-net-mod.bb) | RPMsg transport 위 network driver 공급 | Endpoint와 packet 왕복 |

`arm_si_rproc_attach()` 자체는 성공을 반환하는 작은 callback이다. 실제 attach message와 ACK 대기는 `arm_si_add_rproc_core()`에 있으므로 함수 이름만 보고 전체 handshake가 없다고 판단하면 안 된다. 이 driver의 `rproc_ops`에는 일반 firmware download/start 대신 `attach`, `get_loaded_rsc_table`이 연결된다.

### AP와 CL1이 같은 buffer를 다른 address로 본다

[Linux apollo.dtsi](../../../../hsoc-stack/components/primary_compute/linux/arch/arm64/boot/dts/hsoc/apollo.dtsi)의 reserved-memory와 [CL1 board DTS](../../../../hsoc-stack/components/system_mgmt/zephyrproject/zephyr_hsoc_src/boards/hsoc/apollo_qvp_safety_island_c1/apollo_qvp_safety_island_c1.dts)의 `rsc_table`, `shared_data`는 domain별 address view다. 숫자가 다르다는 이유만으로 mismatch라고 판단하지 않고 변환 관계를 확인한다.

| 대상 | AP DT view | CL1 DT view | 확인 의미 |
|---|---|---|---|
| Resource table | `0x00100000`, size `0x20000` | `0xe0130000`, size `0x20000` | 같은 논리 resource table |
| Virtqueue/data 영역 | Vring0 `0x00120000`, vring1 `0x00140000`, buffer `0x00160000` | `shared_data` base `0xe0150000`, size `0x60000` | CL1의 `busaddr_delta_l=0xe0030000` 관계 |
| Notification 이름 | `vq0_rx`, `vq1_rx`, `vq0_tx`, `vq1_tx`, `detach`, `attach`, `ack` | 반대 endpoint 방향의 같은 protocol 역할 | TX/RX endpoint와 channel 일치 |

이 표는 DTS의 선언 관계다. 실제 QVP translation은 [04. Runtime/Lua](../04-qbox-runtime-and-lua.md)의 fabric map과 함께 확인해야 하며, 주소 선언만으로 active traffic을 입증하지는 않는다.

### Reattach patch가 보장하려는 실행 순서

AP만 reset하면 CL1 runtime은 남아 있지만 AP boot firmware가 shared resource를 초기화할 수 있다. 이때 CL1이 이전 state만 기억한 채 ACK하면 AP가 비어 있는 resource table을 해석하게 된다. [QVP reattach patch](../../../../hsoc-stack/yocto/meta-hsoc-bsp/recipes-kernel/zephyr-kernel/files/0001-veth-restore-resource-table-on-reattach.patch)는 다음 순서를 구현한다.

```text
MHU callback: event 기록, k_work_submit
  → notify_handler: lifecycle lock 획득
  → process_mbox_event: 기존 vdev teardown / detached 상태
  → restore_rsc_table: buffer clear + SI-owned template 복사
  → barrier_dmem_fence_full
  → attach ACK
  → 후속 notification에서 vdev와 RPMsg endpoint 구성
```

`restore_rsc_table()`은 source template가 공유 복사본과 다른지, version/size가 유효한지 검사한다. `notify_handler()`는 attach를 이전 VQ event보다 우선 처리한다. TX는 lifecycle lock을 오래 점유하며 remote buffer를 기다리지 않도록 `rpmsg_trysend()`와 `-EAGAIN` backpressure를 사용한다. 이는 성능 조정만이 아니라 reset/reattach 중 state 소유권을 명확히 하는 변경이다.

## 4. 실패 관측을 변경 범위로 바꾸기

| 최초 실패 | 먼저 볼 source / artifact | 다음 판단 |
|---|---|---|
| Module이 load되지 않음 | Image package, kernel ABI, module signature/loader log | HIPC protocol보다 packaging/ABI 문제부터 |
| `Cannot get ... mbox` | DT `mboxes`/`mbox-names`, mailbox provider | Channel 이름과 driver binding 확인 |
| Attach ACK timeout | CL1 integrated image, mailbox callback, IRQ·reset 상태 | Shared table 해석 전 단계임 |
| ACK 뒤 resource table 불일치 | Generated patch 적용, shared-memory alias, barrier/cache 속성 | publication-before-ACK 계약 확인 |
| Endpoint는 생겼으나 packet 실패 | RPMsg virtqueue와 network consumer | Control path와 data path를 분리해 관측 |
| 첫 boot는 되지만 AP reset 후 실패 | Retained CL1 state와 reattach event 순서 | Cold boot 성공을 reset 경로 근거로 사용하지 않음 |

관측할 log/marker를 source에서 먼저 고르면 불필요한 전체 rebuild를 줄일 수 있다. 예를 들어 mailbox callback에 도달하지 못했다면 network stack 변경보다 firmware image, IRQ wiring, endpoint binding을 먼저 조사한다.

## 5. 변경 요청을 리뷰 가능한 단위로 적는 방법

| 기록 항목 | HIPC 예시 |
|---|---|
| Trigger와 기대 동작 | AP reset 후 retained CL1에 다시 attach하고 packet 왕복 |
| 입력 source | 외부 Linux module, HSOC patch, CL1 board, Lua map |
| 변경 책임 | Lifecycle은 CL1 patch, mapping은 DTS/Lua, package는 metadata |
| 재생성 대상 | CL1 generated module → ELF/bin → firmware/loader input; 필요 시 AP module/rootfs |
| 실제 실행 identity | `.qboxconf`, installed provider, 선택 ELF/bin/WIC의 hash |
| 검증 경로 | Cold boot, detach/reattach, AP reset 뒤 ACK·endpoint·traffic |

이렇게 작성하면 “module build 성공”과 “reset 이후 통신 복구”가 서로 다른 검증 결과라는 점이 명확해진다. 새 기능의 완료 조건은 마지막 consumer의 관측으로 정의한다.

## 6. Reference에서 Apollo source로 넘어갈 때의 읽기 순서

| Arm 문서의 section | 얻을 정보 | Apollo에서 이어서 읽을 파일 |
|---|---|---|
| [Overview / Software components·Architectures](../../../../arm-zena-css/documentation/overview.rst) | Domain과 baremetal/virtualization의 목적 | Current template의 `baremetal`, Nexios image |
| [Components / System Management Block](../../../../arm-zena-css/documentation/design/components.rst) | RSE/SI/SMD 책임과 SCMI 관계 | TF-M target, SCP product, Zephyr board |
| [Components / Primary Compute](../../../../arm-zena-css/documentation/design/components.rst) | TF-A/OP-TEE/U-Boot boot·ABI 계약 | Local component와 `*-apollo-qvp.inc` |
| [Secure Services / Architecture](../../../../arm-zena-css/documentation/design/secure_services.rst) | FF-A와 SE Proxy/RSE data flow | TS recipe, OP-TEE `SP_PATHS`, TF-M service |
| [Integration / Yocto layers dependency](../../../../arm-zena-css/documentation/design/integration.rst) | Reference layer 조합 | `build/conf/bblayers.conf`와 HSOC layer |
| [HIPC](../../../../arm-zena-css/documentation/design/hipc.rst) | remoteproc/OpenAMP/shared-memory 계약 | Linux/CL1/QVP 세 쪽의 구현 |

Reference는 interface의 의도를 설명하고, Apollo source와 metadata는 그 interface를 현재 어떻게 구성했는지 보여준다.
두 정보를 연결하면 directory 이름이나 예전 patch 목록에 의존하지 않고 실제 실행 구성으로 들어갈 수 있다.

## 다음 읽기

[03. Build Architecture](../03-project-build-architecture.md)에서 이 source 조합이 task DAG와 실행 artifact로 바뀌는 과정을 읽는다. HIPC의 domain별 runtime은 [06-6. Zephyr와 HIPC](../06-software/06-zephyr-and-hipc.md), mailbox core는 [07-2. Mailbox와 IPC](../07-system/02-mailbox-and-ipc.md)에서 이어진다.

[상위 장](../02-project-source-architecture.md) · [← 이전](02-build-source-contracts.md) · [다음 →](../03-project-build-architecture.md)
