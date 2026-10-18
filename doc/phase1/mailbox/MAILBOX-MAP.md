# Mailbox 주소·채널·구현 상세표

[세미나 본문](README.md) · [소스 근거](SOURCES.md)

기준: `apollo-qvp-saturn-v.lua`, 환경 override 없는 full 기본 descriptor. AP×4·CL0×1·CL1×4·RSE×1이다. 실제 실행 process나 배포 firmware의 설정을 측정한 결과가 아니다.

<a id="pairs"></a>

## 1. 방향별 PBX / MBX 연결

**PBX는 송신 측, MBX는 수신 측이다.** 표의 IRQ는 PBX에서는 transfer ACK, MBX에서는 receive를 뜻한다. `—`는 해당 frame의 IRQ socket 미연결이다. `SPI`는 QBox/GIC input index이며 `INTID=SPI+32`; NVIC는 external IRQ 번호다.

아래 주소는 **각 모델이 연결된 router의 decode 주소**다. AP가 사용하는 낮은 logical alias는 다음 표에 별도로 정리했다. [Lua 근거](SOURCES.md#platform)

| Pair key | PBX: 송신 view / ACK IRQ | MBX: 수신 view / RX IRQ | DBCH |
|---|---|---|---:|
| `ap_s_to_rse` | `host_ap_rse_mhu_pbx`<br>`0x300001b600000` / — | `rse_mhu2_receiver_s`<br>`0x501b0000` / RSE NVIC 45 | 128 |
| `ap_to_si_cl0_ns` | `host_ap_si_ns_scmi_mhu_pbx`<br>`0x400003b000000` / ap_gic:SPI112/INTID144 | `si_cl0_ap_ns_mhu_mbx`<br>`0x38040000` / si_cl0_gic:SPI65/INTID97 | 128 |
| `ap_to_si_cl0_pfdi` | `host_ap_si_pfdi_monitor_mhu_pbx`<br>`0x400003b380000` / ap_gic:SPI118/INTID150 | `si_cl0_ap_pfdi_monitor_mhu_mbx`<br>`0x383c0000` / si_cl0_gic:SPI71/INTID103 | 128 |
| `ap_to_si_cl0_scmi` | `host_ap_si_scmi_mhu_pbx`<br>`0x400003b080000` / ap_gic:SPI114/INTID146 | `si_cl0_ap_scmi_mhu_mbx`<br>`0x380c0000` / si_cl0_gic:SPI67/INTID99 | 128 |
| `apollo_ap_to_si_cl1` | `host_ap_si_cl1_mhu_pbx`<br>`0x400003b100000` / ap_gic:SPI120/INTID152 | `si_cl1_hipc_mhu_mbx`<br>`0x39040000` / si_cl1_gic:SPI41/INTID73 | 32 |
| `apollo_si_cl0_pfdi_reply` | `si_cl0_pfdi_mhu_pbx`<br>`0x38200000` / — | `si_cl1_pfdi_reply_mhu_mbx`<br>`0x39240000` / — | 32 |
| `apollo_si_cl1_pfdi` | `si_cl1_pfdi_mhu_pbx`<br>`0x39200000` / si_cl1_gic:SPI50/INTID82 | `si_cl0_pfdi_mhu_mbx`<br>`0x38240000` / si_cl0_gic:SPI75/INTID107 | 32 |
| `apollo_si_cl1_to_ap` | `si_cl1_hipc_mhu_pbx`<br>`0x39000000` / si_cl1_gic:SPI40/INTID72 | `host_ap_si_cl1_mhu_mbx`<br>`0x400003b140000` / ap_gic:SPI121/INTID153 | 32 |
| `rse_ap_monitor_local` | `rse_mhu0_sender_s`<br>`0x50160000` / — | `rse_mhu0_receiver_s`<br>`0x50170000` / RSE NVIC 41 | 128 |
| `rse_to_ap_s` | `rse_mhu2_sender_s`<br>`0x501a0000` / — | `host_ap_rse_mhu_mbx`<br>`0x300001b630000` / — | 128 |
| `rse_to_si_cl0` | `host_rse_si_mhu_pbx`<br>`0x400003c000000` / — | `si_cl0_rse_mhu_mbx`<br>`0x38140000` / si_cl0_gic:SPI73/INTID105 | 128 |
| `si_cl0_to_ap_ns` | `si_cl0_ap_ns_mhu_pbx`<br>`0x38000000` / si_cl0_gic:SPI64/INTID96 | `host_ap_si_ns_scmi_mhu_mbx`<br>`0x400003b040000` / ap_gic:SPI113/INTID145 | 128 |
| `si_cl0_to_ap_pfdi` | `si_cl0_ap_pfdi_monitor_mhu_pbx`<br>`0x38380000` / si_cl0_gic:SPI70/INTID102 | `host_ap_si_pfdi_monitor_mhu_mbx`<br>`0x400003b3c0000` / ap_gic:SPI119/INTID151 | 128 |
| `si_cl0_to_ap_scmi` | `si_cl0_ap_scmi_mhu_pbx`<br>`0x38080000` / si_cl0_gic:SPI66/INTID98 | `host_ap_si_scmi_mhu_mbx`<br>`0x400003b0c0000` / ap_gic:SPI115/INTID147 | 128 |
| `si_cl0_to_rse` | `si_cl0_rse_mhu_pbx`<br>`0x38100000` / — | `host_rse_si_mhu_mbx`<br>`0x400003c020000` / RSE NVIC 139 | 128 |

`rse_ap_monitor_local`은 `protocol="doorbell"`이며 기본 설정에서 peer 전달·자동 응답을 선택하지 않는다. TF-M에 AP monitor link 정의가 있어도 현재 QVP의 활성 AP 통신 경로로 간주하지 않는다. 실제 AP Secure 서비스는 MHU2 pair를 사용한다.

AP/SI 방향의 aperture는 대체로 192KiB, RSE–CL0 및 CL0–CL1 PFDI는 128KiB, RSE local은 64KiB다. Aperture 전체가 payload buffer이거나 모두 구현된 register라는 뜻은 아니다.

### AP guest logical alias → system-global

| 용도 | AP logical base | System-global base | 변환 경로 |
|---|---|---|---|
| NS SCMI PBX | `0x40020000` | `0x400003B000000` | AP ATU |
| NS SCMI MBX | `0x40050000` | `0x400003B040000` | AP ATU |
| Secure SCMI PBX | `0x40080000` | `0x400003B080000` | AP ATU |
| HIPC PBX | `0x400B0000` | `0x400003B100000` | AP ATU |
| HIPC MBX | `0x400E0000` | `0x400003B140000` | AP ATU |
| AP PFDI PBX | `0x40110000` | `0x400003B380000` | QVP static bridge가 우선 |
| AP–RSE S PBX | `0x40680000` | `0x300001B600000` | AP ATU |
| AP–RSE S MBX | `0x406B0000` | `0x300001B630000` | AP ATU |

Firmware ATU 설정과 QVP decode를 함께 확인했다. 과거 patch에 나오는 PFDI `0x403A0000`은 최종 주소가 아니다. 현재 secure SCMI/PFDI의 reverse MBX가 모델에 존재한다고 AP guest alias나 active IRQ consumer까지 있다고 가정하지 않는다.

<a id="channels"></a>

## 2. 실제 SW channel / flag 배정

| 경로 | Physical DBCH / flag | 데이터 / 완료 |
|---|---|---|
| Linux NS SCMI | ch0 bit0 request·reply, bit2 notification | request slot response/FREE; 필요 시 reverse IRQ |
| TF-A PSCI | Secure D1 ch0 bit0 | shared response/FREE polling |
| AP PFDI | Secure D3 ch0..15 bit0 | CPU별 40B slot; FREE polling |
| CL1 PFDI | ch2..5 bit0 | CPU0..3 slot; flattened ID 64/96/128/160 |
| RSE SCMI command | ch0 bit1 | shared command page; BL2는 polling |
| SCP→RSE notification | ch0 bit2 | shared notification page; runtime IRQ |
| RSE AP reload ACK | ch0 bit3 | **payload 없는 전용 doorbell**, SCMI transport NONE |
| HIPC vq0 / vq1 | 양방향 ch0 bit0 / bit1 | vring0 CL1→AP / vring1 AP→CL1 |
| HIPC detach / attach | AP→CL1 ch0 bit2 / bit3 | lifecycle event |
| HIPC software ACK | CL1→AP ch0 bit2 | resource 준비; endpoint ready는 별도 |
| AP-S↔RSE stream | 첫 batch ch0 길이, ch1..126 data, ch127 notify | 후속 batch data는 ch0부터; clear polling 후 다음 batch |

Linux DT의 MHU specifier `<0 n b>`에서 0은 DBE extension, n은 window, b는 flag다. Zephyr의 channel ID는 `32×n+b`다. SCMI protocol ID `0x90`이나 GIC INTID를 이 번호에 대입하면 안 된다. [SW 설정 근거](SOURCES.md#scp)

<a id="memory"></a>

## 3. Shared memory와 CPU view

| Payload | Backing / AP 또는 global view | 다른 CPU view | 크기·소유 |
|---|---|---|---|
| AP NS SCMI | `host_ap_mhu_ns_shared_sram`, AP `0x00180000` | SI0 `0xE01B0000` | SRAM 4KiB; request 256B, notification +0x100 |
| AP Secure SCMI | `host_ap_shared_sram`, AP `0xDC0` | SI0 `0xE0030DC0` | 256B; 앞 0xDC0는 SDS |
| AP PFDI | 같은 SRAM, AP `0xEC0+40×n` | SI0 `0xE0030EC0+40×n` | 최대 16 slot; protocol은 선택된 CPU 사용 |
| HIPC | `host_ap_bl2_header_sram`, AP `0x100000` | CL1 `0xE0130000` | 512KiB; AP에도 높은 alias 존재 |
| CL1 PFDI | `si_cl1_scmi_shmem`, `0x48000000` | SI0/CL1 동일 주소 | backing 4KiB; 4×40B 사용 |
| RSE SCMI | `host_rse_si_ssram`, global `0x4000040000000` | SI0 `0x40000000`; RSE runtime ATU | backing 256KiB; command/notification 각 256B |
| RSE pointer payload | `host_ap_rse_mailbox`, AP/global `0xFFFE0000` | RSE permission 검사 후 ATU | 128KiB; mailbox parameter `0xFFFFC000` 포함 |

RSE AP_S pointer-access는 위 DRAM carveout 외 AP SRAM `0..0xFFFFF`도 허용한다. 임의 AP 주소를 전달할 수 있다는 뜻은 아니다.

### HIPC 512KiB 배치

| 영역 | AP physical | CL1 view | 크기 |
|---|---|---|---|
| Resource table | `0x00100000` | `0xE0130000` | 128KiB |
| vring0 · CL1→AP | `0x00120000` | `0xE0150000` | 128KiB |
| vring1 · AP→CL1 | `0x00140000` | `0xE0170000` | 128KiB |
| Packet buffers | `0x00160000` | `0xE0190000` | 128KiB |

Linux는 reserved-memory / remoteproc로 영역을 획득한다. Zephyr는 Normal-NC mapping과 bus-address delta `0xE0030000`을 사용한다. QVP `addrtr`가 같은 backing으로 연결하지만 CPU cache의 coherence를 구현하는 것은 아니다. [메모리 소스](SOURCES.md#platform)

<a id="registers"></a>

## 4. QVP register 계약

| Block / offset | 기능 | 현재 구현에서 확인할 점 |
|---|---|---|
| `BLK_ID +0x000` | PBX/MBX 구분 | PBX=0, MBX=1 |
| `FEAT_SPT0 +0x010` | 확장 기능 | 기본 1: DBE |
| `DBCH_CFG0 +0x020` | channel 개수 | `channel_count−1` |
| `DBCH_INT_ST[0..3] +0x400` | combined source bitmap | channel당 1 bit; flag는 해당 channel에서 재확인 |
| PBX `ST / SET` | channel +0x00 / +0x0C | SET은 OR; queue 없음 |
| PBX `INT_ST / INT_CLR / INT_EN` | +0x10 / +0x14 / +0x18 | transfer ACK pending / W1C / enable |
| MBX `ST / ST_MSK / CLR` | +0x00 / +0x04 / +0x08 | 상태 / mask 적용 상태 / 선택 bit clear |
| MBX `MSK_ST / MSK_SET / MSK_CLR` | +0x10 / +0x14 / +0x18 | flag별 수신 IRQ masking |
| PBX/MBX `CTRL` | channel +0x1C | bit0: combined IRQ 참여 |
| `CTRL_OP` | controller operation | 저장·읽기 지원; complete OP_REQ/OP_ACK gating engine은 아님 |

Channel stride는 32B, 시작은 frame+0x1000이다. Reset은 status/mask/interrupt-enable을 0, channel CTRL을 1로 초기화한다. Bridge의 MBX CLR은 이전 pending 유무와 관계없이 PBX ACK 상태를 설정할 수 있으므로 “새 요청을 실제로 처리했다”는 증거로 사용할 수 없다.

MMIO transport는 1/2/4/8-byte를 받지만 register 부작용은 4-byte 경로에 구현된다. DMI는 제공하지 않고 delay를 소비하지 않는다. Alignment·byte-enable·streaming validation도 완전한 HW access 검증으로 취급하지 않는다. [C++ 근거](SOURCES.md#models)

<a id="reset"></a>

## 5. Reset·재접속·오류 경계

| Event | 실제 범위 | SW가 처리할 부분 |
|---|---|---|
| AP cold reset | AP-facing PBX/MBX 10개 reset | 원격 peer·shared slot·endpoint 상태 재협상 |
| 전체 Apollo reset | MHU frame 30개 reset | 각 firmware가 transport/IRQ 초기화 |
| RSE local SYS/RSS reset | 현재 local reset fanout에 MHU frame 없음 | CPU reset과 MHU reset을 같은 것으로 가정 금지 |
| Peer reset 중 SET | peer lookup 실패; sender pending 유지 가능 | 자동 replay/ACK 없음; timeout·재초기화 정책 |
| AP 재접속 | HIPC backing은 `init_mem=false`로 보존 | Zephyr가 resource-table template 재발행, ring/endpoint 재생성 |

SCP는 CLR **후** transport를 호출한다. Linux·Zephyr MHU RX driver는 callback **후** CLR한다. 어느 쪽도 HW ACK만으로 상위 서비스 성공을 판정하지 않는다. HIPC attach ACK 이후에도 VirtIO negotiation과 RPMsg ready가 필요하다.

<a id="limits"></a>

## 6. 구현과 검증의 경계

- **Full:** 실제 SCP/Zephyr/TF-M이 protocol 처리. **Linux-direct:** SCMI BASE mock, HIPC SI stub, RSE unsupported 응답.
- **DBE 기능 모델:** FIFO/FastChannel engine, 물리 CDC·clock/power handshake·지연 동등성 미구현.
- **Security:** 주소/PAS 정책과 MHU 모델의 access filtering은 별개다.
- **Safety:** 별도 `zena_device_fmu` 노드가 존재하지만 `mhu320ae`가 자율 전송 오류를 검출·주입하는 경로는 아니다.
- **Evidence:** 현재 소스·정적 descriptor·문서 렌더링 확인. 실제 왕복 payload/IRQ, concurrent flag, peer reset/retry, 재접속, FVP 비교는 미실행.

## 7. 정적 descriptor 재현

저장소 루트에서 실행한다. QBox·guest를 기동하거나 image를 수정하지 않는다.

```python
from pathlib import Path
import sys
sys.path.insert(0, "scripts/test")
from apollo_lua_descriptor import read_sources, evaluate_modules, plain_descriptor

sources = read_sources(Path("hsoc-stack/tools/qbox-platform/platforms/apollo"))
platform = plain_descriptor(evaluate_modules(
    sources, entrypoint="apollo-qvp-saturn-v.lua", environment={}
)["descriptor"])
# platform에서 moduletype="mhu320ae"인 frame의 pair, target_socket, irq를 비교한다.
```
