# I4 - GPEX MSI/ITS/LPI 완료 보고서

- 완료일: 2026-07-16
- 판정: `complete`
- 대상: Apollo CFG2, AP CPU0~CPU3, 단일 PCIe endpoint
- 성능 기준: 없음

## 구현 결과

기본 machine에는 시험 장치를 추가하지 않고
`QBOX_APOLLO_PCIE_IRQ_TEST=true`일 때만 `virtio-net-pci` 하나를
`0000:00:01.0`에 생성한다. 같은 endpoint와 같은 DMA 경로를 두 번 부팅해 다음
interrupt 경로를 실제 Linux traffic으로 검증했다.

1. MSI-X: GPEX -> SMMUv3/LTI00 -> ITS translator -> CPU0 LPI
2. `pci=nomsi`: GPEX INTx swizzle -> GIC SPI input 301 -> CPU0

시험 identity는 DeviceID/RID `0x0008`, SID `0x0040`, EventID base `0`, ITS
translator `0x20850040`으로 고정했다. DT overlay의 `iommu-map`은 RID `0x0008`
한 개만 SID `0x0040`에 매핑한다. 이 범위 제한은 host bridge RID가 endpoint와
같은 SID를 공유하는 alias를 방지한다.

## 구현 중 확인하고 수정한 구조 문제

- QBox libqemu C++ wrapper가 QEMU `MemTxAttrs.requester_id`를 버려 ITS가 모든
  MSI-X를 DeviceID 0으로 관찰했다. QEMU와 C++ 방향의 MemoryRegion 및
  AddressSpace read/write에서 requester ID를 보존하도록 수정했다.
- Apollo GICv4.1 collection table entry 크기가 2로 설정되어 있었지만 QEMU ITS
  모델의 단위는 byte이고 실제 entry content는 8 byte다. 겹치는 CTE 때문에
  RDBase가 손상되므로 AP 경로 두 곳의 `gicv4_1_cte_size`를 8로 수정했다.
- 초기 all-RID `iommu-map`은 PCI host bridge와 endpoint SID를 alias했다. 시험
  endpoint RID 하나만 포함하도록 축소했다.
- initramfs hook 삽입 여부를 검사하기 전에 시험 script 경로를 network skip
  목록에 추가해 hook이 삽입되지 않는 순서 오류를 수정했다.
- Linux `/proc/interrupts`는 GIC SPI input 301을 architectural INTID
  `32 + 301 = 333`으로 표시하므로 validator가 두 번호의 의미를 명시적으로
  구분한다.

## 변경 파일

QBox core:

- `qemu-components/common/include/libqemu-cxx/libqemu-cxx.h`
- `qemu-components/common/src/libqemu-cxx/memory.cc`
- `qemu-components/pci/virtio_net_pci/include/virtio_net_pci.h`
- `tests/components/request-context/request-context-tests.cc`

QBox platform:

- `CMakeLists.txt`
- `platforms/apollo/hw-block/ap_compute.lua`
- `platforms/apollo/hw-block/primary_compute.lua`
- `platforms/apollo/hw-block/signal_routes.lua`
- `platforms/apollo/test-profile/apollo-qvp-pcie-irq-overlay.dtso`
- `platforms/apollo/README.md`

최상위 실행·검증·문서:

- `scripts/run/run_qbox_apollo_fvp_linux.py`
- `scripts/test/prepare_qbox_apollo_pcie_irq_profile.py`
- `scripts/test/validate_qbox_apollo_pcie_irq_runtime.py`
- `tests/test_apollo_qvp_pcie_irq_profile.py`
- `tests/test_run_qbox_apollo_fvp_linux.py`
- fidelity contract, ledger, architecture 문서와 이 보고서

`hsoc-stack/components/**`와 QEMU 소스는 수정하지 않았다.

## 로컬 빌드와 단위 검증

```text
cmake --build build/qbox-core-tests \
  --target request-context-tests --parallel 8
ctest --test-dir build/qbox-core-tests \
  -R '^request-context-tests$' --output-on-failure
결과: PASS, 1/1

/usr/bin/python3 -m pytest -q \
  tests/test_apollo_qvp_pcie_irq_profile.py \
  tests/test_run_qbox_apollo_fvp_linux.py \
  tests/test_apollo_qvp_smmuv3_wiring.py
결과: PASS, 33 passed

/usr/bin/python3 scripts/test/validate_qbox_apollo_fvp_full_map.py
/usr/bin/python3 scripts/test/audit_qbox_core_boundary.py
git diff --check
git -C hsoc-stack/tools/qbox diff --check
git -C hsoc-stack/tools/qbox-platform diff --check
결과: PASS

./local_build.sh qbox
결과: PASS
  qbox-configure: 4초
  qbox-build: 1초
  최종 target: virtio_net_pci, smmuv3, arm_gicv3_its,
               platforms-vp, apollo_fvp_full_system
```

## 런타임 검증

MSI-X 실행:

- 증거: `build/qbox-apollo-fvp/i4-pcie-msix-direct-r7-20260716/`
- endpoint: `0000:00:01.0`, interface `eth1`
- DHCP: `10.0.2.15`, gateway ping 성공
- input LPI EventID 1: CPU0 증가 6
- output LPI EventID 2: CPU0 증가 10

INTx 실행:

- 증거: `build/qbox-apollo-fvp/i4-pcie-intx-direct-r1-20260716/`
- kernel command line: `pci=nomsi`
- 동일 endpoint/interface, DHCP와 gateway ping 성공
- GICv3 INTID 333(`virtio6`): CPU0 증가 8
- INTID 333은 GPEX legacy SPI input 301에 해당

두 실행을 다음 명령으로 함께 판정했다.

```text
/usr/bin/python3 scripts/test/validate_qbox_apollo_pcie_irq_runtime.py \
  --msix-log build/qbox-apollo-fvp/i4-pcie-msix-direct-r7-20260716/qbox-apollo-fvp.log \
  --intx-log build/qbox-apollo-fvp/i4-pcie-intx-direct-r1-20260716/qbox-apollo-fvp.log \
  --output build/qbox-apollo-fvp/i4-pcie-irq-runtime-validation.json
결과: PASS
  same_endpoint=true, DeviceID=8, SID=64
  msix CPU0 delta=10, intx CPU0 delta=8
```

## 판정 범위와 잔여 부채

이 결과는 direct AP boot에서 GPEX/SMMU/ITS/GIC interrupt 수직 경로를
qualification한 것이다. full-system RSE-first 실행은 이번 진단에서 AP release
전에 `SCP is not ready. Abort`로 멈췄으며, endpoint 경로와 무관한 RSE/SCP
통합 blocker로 I7에서 다시 다룬다.

CPU1~CPU3 affinity matrix, 복수 endpoint, 잘못된 DeviceID/EventID 주입,
interrupt 성능은 이번 최소 acceptance에서 제외했다. 다음 I5는 SMMU/APU fault
하나를 FMU/SSU record, IRQ, clear/recovery 경로로 연결한다.
