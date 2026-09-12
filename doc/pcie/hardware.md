# Arm Zena CSS PCIe 하드웨어 구성

작성일: 2026-09-12. 기준 문서는 Arm Zena CSS Software Developer Guide r0p1,
`110125_0001_01_en`(2026-01-27)이다. 이 문서는 하드웨어 programmer model의
주소 예시를 정리한 것이며, QBox 주소와의 일대일 대응을 뜻하지 않는다.

## 구성

Zena CSS의 제품 구성은 **PCIe Gen6 x8 한 개와 Gen3 x1 두 개**다.
근거는 [product highlights의 Interfaces 항목](../arm_zena_css_dev_guide/01-zena-css-product-highlights.md)이다.
ECAM 주소 경로 다섯 개를 다섯 개의 동시 활성 물리 포트로 해석해서는 안 된다.

Zena CSS는 NI-710AE 및 외부 I/O controller용 확장 경로를 제공한다. Linux가
PCIe configuration space에 접근하는 ECAM 영역은 controller register 영역과
다르다. controller/PHY configuration은 I/O Block configuration space에 있고,
ECAM은 PCIe MMIO memory map에 있다.

`Table 9-13`은 다섯 ECAM path를 예시로 정의한다. ECAM0은 x8 CFG,
ECAM1/2는 x4_0/x4_1 CFG, ECAM3/4는 x1_0/x1_1 CFG path다. 각 ECAM window는
256MiB이므로 bus 0~255의 1MiB configuration space를 수용한다.
같은 표에서 x4_0/x4_1 MMIO 영역을 x8의 앞/뒤 절반으로도 설명한다.
하지만 이 정보만으로 bifurcation 선택 레지스터나 reset 시 활성 모드를 확정할 수 없다.

| Path | ECAM (Memory space 2) | High MMIO (Memory space 3) | 연결 path |
| --- | --- | --- | --- |
| 0 | `0x100_0000_0000`–`0x100_0fff_ffff` | x8과 공유 | x8 CFG |
| 1 | `0x100_1000_0000`–`0x100_1fff_ffff` | `0x101_0000_0000`–`0x101_1fff_ffff` | x4_0 |
| 2 | `0x100_2000_0000`–`0x100_2fff_ffff` | `0x101_2000_0000`–`0x101_3fff_ffff` | x4_1 |
| 3 | `0x100_3000_0000`–`0x100_3fff_ffff` | `0x101_4000_0000`–`0x101_5fff_ffff` | x1_0 |
| 4 | `0x100_4000_0000`–`0x100_4fff_ffff` | `0x101_6000_0000`–`0x101_7fff_ffff` | x1_1 |

모든 high MMIO window는 512MiB다. low PCIe Memory space 1은
`0x00_6000_0000`–`0x00_7fff_ffff`(512MiB)다. I/O Block configuration space의
PCIe PHY offset은 `0x05c0_0000`–`0x05ff_ffff`, bifurcation/controller register
offset은 `0x0600_0000`–`0x07ff_ffff`다. I/O Block base `0x1_c000_0000`를 적용하면
각각 AP physical `0x1_c5c0_0000`–`0x1_c5ff_ffff`,
`0x1_c600_0000`–`0x1_c7ff_ffff`가 된다. 이 영역은 ECAM root-port
configuration space가 아니며, guide는 내부 IP register의 세부 동작을 정의하지 않는다.

근거: [programmer model PCIe MMIO table](../arm_zena_css_dev_guide/09-programmers-model-for-zena-css.md#programmer-s-model-for-zena-css-memory-maps-pcie-mmio-memory-map),
[I/O Block table](../arm_zena_css_dev_guide/09-programmers-model-for-zena-css.md#md532-io-block-configuration-space-memory-map__tbl_globalioblockmemorymap),
[FVP map](../arm_zena_css_dev_guide/08-fixed-virtual-platform.md).

## FVP reference 경계

현 FVP용 Linux/TF-A DT는 x1_1에 대응하는 `pcie4` ECAM
`0x1004_0000_0000`를 정의하지만 기본 `status = "disabled"`다. enabled 상태의
첫 AP ECAM read가 EL3 SError를 유발했기 때문이다. 이 조치로 FVP BSP는
부팅하지만 FVP PCIe enumeration, endpoint traffic, MSI/ITS 전달은 검증되지
않았다. 재활성화에는 Linux DTS와 TF-A HW_CONFIG/FIP을 함께 재빌드해야 한다.

Arm Zena CSS release note의 “PCIe configuration is excluded”도 이 FVP
제한과 함께 해석해야 한다. 이는 Zena CSS 하드웨어가 PCIe path를 갖지 않는다는
뜻이 아니다. 자세한 재현과 검증은
[FVP boot recovery](../qbox/fvp-pcie-boot-recovery-2026-09-11.md)를 참조한다.

## QBox 비교 기준

QBox는 Zena의 Gen6 x8 + Gen3 x1 두 개의 물리 인터페이스 구성을 재현하지 않는다.
Apollo QVP에는 하나의 QEMU GPEX generic root host를 두고, IRQ/ITS/SMMU와
Linux driver 경로를 검증하기 위한 별도 가상 address map을 사용한다. 이 차이는
기능 검증의 범위와 hardware fidelity 범위를 나누는 핵심 경계다.

| 항목 | Zena hardware/FVP map | Apollo QVP GPEX |
| --- | --- | --- |
| 포트/주소 경로 | Gen6 x8 + Gen3 x1 두 개; ECAM 경로 예시는 5개 | GPEX host 1개; 사용자 지정 Gen5 root port 구성은 후속 문서 참조 |
| ECAM | `0x100_0000_0000` 계열 | `0x43b5_0000` |
| Low MMIO | `0x6000_0000`–`0x7fff_ffff` | `0x6030_0000`–`0x7fff_ffff` |
| High MMIO | `0x101_0000_0000` 계열 | `0x4_0000_0000`–`0x5_ffff_ffff` |
| PHY/controller registers | I/O Block에 존재 | 모델링하지 않음 |
| Link training/AER/hot-plug | physical integration 책임 | generic QEMU GPEX의 범위를 넘음 |

사용자 지정 Gen5 x4/x2 모델은 [QEMU Gen5 구성](qemu-gen5.md),
기존 IRQ profile은 [QBox status](qbox-status.md)를 참조한다.
