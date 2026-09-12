# Zena 물리 PCIe 모델 구현 전제와 확인 결과

**최신 결정:** 사용자가 Synopsys controller/PHY 대신 QEMU 기본 모델을 선택했다.
Gen5 x4 × 2 + x2 × 2 및 x1 bifurcation 요구는 유지한다.
현재 구현과 검증은 [QEMU Gen5 구성](qemu-gen5.md)에 기록한다.
아래의 PHY/PCS TRM 요구는 이전의 실제 Synopsys IP 재현 범위에 해당하며,
현재 QEMU 기능 모델 구현의 선행 조건이 아니다.

2026-09-12. 최초 요청은 Zena의 실제 구성을 재현하는 모델이었다.
이후 사용자 지정으로 Apollo 목표는 **Synopsys PCIe Gen5 x4 2개 + x2 2개,
Synopsys PCIe Gen5 PHY, x1 bifurcation 지원**으로 변경되었다.
아래 Zena 표는 비교 기준이며 Apollo의 새 포트 수/세대 설정을 대신하지 않는다.

## 사용자 지정 Apollo 목표

| Controller group | Controller | 기본 lane 폭 | PHY |
| --- | --- | --- | --- |
| 0 | Synopsys PCIe Gen5 | x4 | Synopsys PCIe Gen5 PHY |
| 1 | Synopsys PCIe Gen5 | x4 | Synopsys PCIe Gen5 PHY |
| 2 | Synopsys PCIe Gen5 | x2 | Synopsys PCIe Gen5 PHY |
| 3 | Synopsys PCIe Gen5 | x2 | Synopsys PCIe Gen5 PHY |

기본 구성은 총 12 lanes다. x1 bifurcation 요구는 기록했으며,
두 x2 group 모두를 각각 x1+x1로 분할할지, 한 group만 분할할지는 확인 중이다.
PHY lane 분할만으로 독립 root port가 생기지 않으므로 controller context,
ECAM/BDF domain, MMIO carveout, DMA SID 및 IRQ도 함께 구성해야 한다.

[Synopsys PCIe 5.0 PHY 제품 문서](https://www.synopsys.com/designware-ip/interface-ip/pci-express/pcie5-phy.html)는
x1/x2/x4/x8/x16 lane 구성과 bifurcation, PIPE 지원을 명시한다.
이는 해당 제품군의 기능 근거이며 특정 PHY/PCS revision의 register map과
초기화 firmware를 확정하는 자료는 아니다. Controller와 PHY의 vendor는 확정되었고,
세부 IP revision 및 programming specification은 아직 확보하지 못했다.

## 확인한 계약

| 항목 | 확인된 사실 | 근거 |
| --- | --- | --- |
| 물리 인터페이스 | PCIe Gen6 x8 1개, Gen3 x1 2개 | Developer Guide §1 Table 1-1 |
| ECAM | ECAM0 x8, ECAM1/2 x4, ECAM3/4 x1 경로 예시 | §9.1.5 Table 9-13 |
| MMIO 공유 | x4_0/1 영역을 x8 앞/뒤 절반으로도 사용 | 같은 표 |
| Controller/PHY 공간 | I/O Block 내부 확장 offset; 상세 IP register 정의와는 다름 | §9.1.6 Table 9-15 |
| SID 상위 비트 | SMD_CSR `IO_TBU_NS_SID`/`IO_TBU_S_SID`, interface별 3 bits | §9.3.5.2/3 |
| 현재 Apollo FVP CMN route | ECAM4, low MMIO, high MMIO4가 HN-P1으로 연결 | `scp-firmware/product/automotive-rd/apollo-fvp/si0_ramfw/config_cmn_cyprus.c` |

SCP 공통 `pcie_setup`/`pcie_discovery`는 ECAM bus walk, BAR 크기 탐색,
주소 자원 할당, NCI mapping 및 SDS 전달을 구현한다.
그 코드만으로 controller/PHY의 초기화 및 link 동작을 얻을 수는 없다.
`rd1ae/config_pcie_setup.c`에는 x8/x4/x2/x2/x1 구성도 있으므로,
다른 reference product의 설정을 Apollo의 실제 포트 구성으로 복사하면 안 된다.

## 재사용 모델 확인

- QBox `qemu_gpex`: 표준 PCI config/BAR/DMA/INTx용 기능 모델. Zena controller IP의
  고유 register 및 PHY 동작을 제공하지 않는다.
- QEMU `hw/pci-host/designware.c`: DesignWare 모델이 있지만 Zena가 해당 IP/revision을
  사용한다는 근거를 확인하지 못했다. 또한 link-control read는 `0xDEADBEEF`,
  PHY link-up과 speed-change는 고정값을 반환한다. 이 모델을 그대로 가져와
  실제 Zena link-training 구현이라고 판정할 수 없다.
- 현재 FVP `--list-params`에는 `pcie_group_0.pcie0..4`의 hierarchy 설정과 generic
  rootport/endpoint 설정이 보인다. Model parameter는 silicon controller TRM을
  대체하지 않으며 물리 인터페이스 다섯 개의 동시 활성 근거도 아니다.

FVP parameter 조회 증거:
`build/pcie-physical-intake/fvp-params.txt`.

[Arm reference stack release notes](https://arm-zena-css.docs.arm.com/en/latest/releasenotes.html)도
PCIe configuration 제외를 명시한다. FVP의 generic hierarchy parameter와
이전 ECAM SError 결과를 실제 controller/PHY의 register 동작 검증으로 사용할 수 없다.

## 구현에 필요한 추가 정보

1. Synopsys controller/PHY의 IP revision, DBI/APB/PHY control register map 및 reset 값.
2. 사용자 지정 x2/x1 분할 범위와 lane 배분, clock/reset/PERST/link-start 순서 및 상태 전이.
3. 각 포트의 NI-710AE/TBU 연결, RID→SID 생성 규칙, MSI DeviceID/INTx routing.
4. 실제 부품 또는 reference simulation에서 기대하는 enumeration/config/IRQ 결과.

Gen5 링크의 packet/PHY 시간 동작까지 요구하는지, CPU-visible register 및
transaction 수준을 요구하는지도 구분해야 한다. 현재 local guide와 generic
models만으로 실제 IP 전체의 register 동등성을 확정할 수 없다.

## 검증 완료 조건

- 선택한 물리 모드와 ECAM 경로가 일치하며 비활성 경로는 장치로 노출하지 않는다.
- 각 활성 root port의 Linux enumeration 및 BAR low/high MMIO 접근을 검증한다.
- 각 포트 endpoint의 실제 DMA data와 SMMU SID 격리/오류 경로를 확인한다.
- MSI-X→ITS/LPI와 지원되는 INTx의 raw interrupt delta를 확인한다.
- Link/reset/retrain/오류 기능은 실제 IP 계약에 따라 검증한다.
- 기존 FVP ECAM SError와 과거 QBox profile 결과를 신규 모델의 성공 증거로 사용하지 않는다.

이 문서는 이전 물리 IP 사양 조사 기록을 보존한다.
QEMU 기본 모델을 사용하는 후속 구현 상태는 위의 Gen5 문서를 참조한다.
