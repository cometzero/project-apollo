# I4 - GPEX MSI/ITS/LPI 구현 계획

## 목적

하나의 QBox PCIe endpoint가 발생시킨 MSI-X를 GPEX, ITS, LPI 경로로 CPU0에
전달하는 최소 수직 slice를 검증한다.

## 구현 범위

- 소유 저장소는 QBox-platform이며 generic QEMU 결함만 local QEMU/QBox에서
  수정한다.
- 기본 플랫폼에는 endpoint를 추가하지 않고
  `QBOX_APOLLO_PCIE_IRQ_TEST=true`인 경우에만 `virtio-net-pci` 하나를
  `0000:00:01.0`에 생성한다.
- 로컬 커널에는 NVMe 드라이버가 없고 `virtio-net-pci` 드라이버가 있으므로
  별도 커널 변경이 필요 없는 네트워크 endpoint를 사용한다.
- test profile에서 DeviceID `0x0008`, EventID base `0`, SID `0x0040`,
  ITS translator `0x20850040`을 고정한다.
- endpoint DMA/MSI write가 LTI00/SMMU 경로와 ITS를 통과하게 한다.
- 같은 endpoint를 정상 부팅하면 MSI-X, `pci=nomsi`로 부팅하면
  GPEX swizzle 결과인 legacy INTx SPI 301을 사용한다.
- 기존 local-build DTB와 initramfs는 수정하지 않는다. QBox-platform 소유의
  DT overlay와 guest test script를 생성된 시험 디스크에만 주입한다.
- affinity matrix와 invalid ID 조합은 후속 검증으로 남긴다.

## 최소 검증

- MSI-X 하나가 CPU0 LPI counter를 증가시킴
- 같은 endpoint의 INTx 하나가 SPI 301 counter를 증가시킴
- 두 모드 모두 traffic 전에 해당 IRQ affinity를 CPU0으로 제한함
- 관련 unit target 후 `./local_build.sh qbox`

## 완료 조건과 보고서

endpoint interrupt count와 CPU0 LPI count가 모두 증가하고 ITS route 식별자가
계약 JSON과 일치해야 한다.

성능 수치, CPU1-CPU3 affinity matrix, 복수 endpoint, 잘못된 DeviceID/EventID
주입은 완료 기준에 포함하지 않는다.

- 보고서: `i4-gpex-msi-lpi-completion-2026-07-16-ko.md`
