# Apollo-QVP QBox 하드웨어 상세 다이어그램

이 문서는 현재 `apollo-qvp.lua`가 조립하는 QBox 하드웨어 토폴로지를
Lua 하드웨어 블록 단위로 나눈 상세 다이어그램의 목차이다. 이상적인
FVP 구조가 아니라 현재 QBox 구현을 나타내며, AP CPU 수는 활성 설정인
4개를 기준으로 한다.

## 다이어그램

| Hardware block | 상세도 | 주요 내용 |
| --- | --- | --- |
| 전체 시스템 | [전체 토폴로지](apollo-qvp-qbox-hardware-topology.html) | AP, RSE, SMD, SI0, SI1의 전체 연결 |
| `fabric.lua` | [Fabric 상세도](apollo-qvp-qbox-hardware-topology-details/fabric-detail.html) | 주소 뷰, router, NCI, ATU/APU bridge |
| `ap_compute.lua` | [AP Compute 상세도](apollo-qvp-qbox-hardware-topology-details/ap-compute-detail.html) | A720AE, GICv3/ITS, SMMUv3, PCIe, 메모리, 주변장치 |
| `ros.lua` | [RoS 상세도](apollo-qvp-qbox-hardware-topology-details/ros-detail.html) | virtio-blk/net/rng, PL031, AP GIC IRQ |
| `rse.lua` | [RSE 상세도](apollo-qvp-qbox-hardware-topology-details/rse-detail.html) | M55/NVIC, TCM/VM/flash, 보안 IP, MHU |
| `system_mgmt.lua` | [System Management/SMD 상세도](apollo-qvp-qbox-hardware-topology-details/system-management-detail.html) | ATU, reset, REFCLK, 공유 SRAM, 도메인 간 MHU |
| `si_cl0.lua` | [Safety Island CL0 상세도](apollo-qvp-qbox-hardware-topology-details/si-cl0-detail.html) | R82, GIC, NI-710AE, FMU/SSU, PPU, MHU |
| `si_cl1.lua` | [Safety Island CL1 상세도](apollo-qvp-qbox-hardware-topology-details/si-cl1-detail.html) | R82 4코어, GIC, HIPC/RPMsg, PFDI |

## 표현 규칙

- 실선은 MMIO/TLM 또는 직접 제어 연결이다.
- 점선은 IRQ, doorbell, reset 또는 비동기 신호 경로이다.
- 보안 색상은 ATU/APU, interrupt controller, fault/safety 경계를 뜻한다.
- 동일한 역할과 연결을 가진 반복 인스턴스는 `×N`으로 묶었다.
- 상자 안의 주소와 IRQ 번호는 `address_map.lua`, `config.lua`,
  `signal_routes.lua` 및 각 하드웨어 블록 Lua의 현재 값을 사용했다.

## 소스 기준

- 조립 순서: `platforms/apollo/apollo-qvp.lua`
- 도메인과 bridge 계약: `platforms/apollo/hw-block/topology.lua`
- 주소 범위: `platforms/apollo/hw-block/address_map.lua`
- 트랜잭션 경로: `platforms/apollo/hw-block/transaction_routes.lua`
- IRQ/reset/fault 경로: `platforms/apollo/hw-block/signal_routes.lua`
