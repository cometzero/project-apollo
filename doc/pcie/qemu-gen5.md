# Apollo QVP QEMU Gen5 포트 구성

사용자 지정 목표는 QEMU 기본 PCIe 모델을 이용한 Gen5 x4 두 개와 x2 두 개다.
Synopsys controller/PHY의 register 모델을 요구했던 이전 전제는 이 구성으로 대체한다.
QEMU GPEX host 아래에 native `pcie-root-port`를 연결하며 PHY 아날로그 동작은 모델링하지 않는다.

## 포트와 bifurcation

| Group | 기본 root slot | 기본 폭 | x1 분할 시 root slots |
| --- | --- | --- | --- |
| 0 | 01.0 | x4 | 분할하지 않음 |
| 1 | 02.0 | x4 | 분할하지 않음 |
| 2 | 03.0 | x2 | 03.0 + 05.0, 각각 x1 |
| 3 | 04.0 | x2 | 분할하지 않음 |

최종 사용자 확인에 따라 x2 controller 중 group 2 하나만 x1+x1 분할을 지원한다.
`QBOX_APOLLO_PCIE_BIFURCATION`은 `none`(기본), `port2` 중 하나다.
두 모드에서 총 12 lanes를 유지하며, root port 수는 각각 4/5개다.
이전 `port3`, `both` 옵션은 제거했으며 지정하면 오류로 처리한다.
분할은 부팅 시 platform 구성 선택이며 실행 중 lane 재배치 register는 제공하지 않는다.

각 root port의 native QEMU property는 `x-speed=32`, `x-width=4/2/1`이다.
이는 PCIe Link Capabilities의 Gen5(32GT/s)와 최대 폭으로 노출된다.
검증용 `virtio-net-pci` endpoint의 link capability가 더 낮을 수 있으므로,
Link Status의 협상 속도/폭과 root port의 최대 설정은 구분한다.
Link Status를 강제로 수정하여 Gen5 트래픽이라고 표시하지 않는다.

## 주소, DMA와 interrupt

GPEX의 기존 QVP 주소를 유지한다: ECAM `0x43b50000`/256MiB,
PIO `0x60200000`/1MiB, low MMIO `0x60300000`/509MiB,
high MMIO `0x400000000`/8GiB. Linux QVP DTS에 generic ECAM host를 추가하고
`CONFIG_PCIEPORTBUS`를 활성화한다. PCI port/endpoint는 Linux가 enumerate한다.

새 구성은 PCI RID를 SMMU SID와 ITS DeviceID에 identity mapping한다.
기존 GPEX는 DMA address space 하나와 고정 SID `0x40`을 사용했지만,
여러 endpoint의 독립 DMA를 위해 opt-in `x-pci-requester-id` 경로를 추가한다.

- GPEX는 `(PCI bus object, devfn)`별 DMA proxy address space를 생성한다.
- 접근 시 현재 bus 번호로 RID를 계산하여 일반 DMA와 MSI에 전달한다.
- QBox `pci_requester_id=true`는 이 RID를 SystemC RequestContext의 SID로 전달한다.
- 공유 initiator의 RID별 DMI cache가 없으므로 이 모드에서는 DMI/MR shortcut을 사용하지 않는다.
- 각 endpoint DMA는 기존 SystemC SMMUv3 LTI00 경로를 통과한다.
- LTI00 TBU의 `requester_id_from_context=true`는 고정 `topology_id=0x40`
  대신 전달된 RID를 SID로 사용한다. 다른 TBU와 legacy profile은 기존 고정 설정을 유지한다.
- 검증용 virtio endpoint는 `iommu_platform=true`로 PCI DMA address space와
  guest DMA API 사용을 활성화한다. 옵션이 꺼지면 QEMU virtio는 이 경로를 사용하지 않는다.
- 검증용 endpoint 활성화 시 native QEMU의
  `-global virtio-net-pci.x-max-bounce-buffer-size=1048576`도 자동 추가한다.
  IO proxy의 DMA mapping은 bounce buffer를 사용하며 기본 4KiB는 부족하다.
  한도는 endpoint당 1MiB이고 필요할 때 할당된다. 관리용 virtio-mmio NIC에는 적용하지 않는다.
- MSI는 RID→ITS identity map, INTx는 root slot swizzle→GIC SPI300~303을 사용한다.

기존 `QBOX_APOLLO_PCIE_IRQ_TEST=true`는 단일 endpoint의 과거 profile 선택으로
남아 있으며 새 root ports를 생성하지 않는다. 신규 검증은 그 profile의 누락된
`.omo` gate에 의존하지 않는다.

## 실행과 검증

빌드:

```bash
./yocto_build.sh --machine apollo-qvp --keep-conf --bsp
```

검증용 endpoint는 `QBOX_APOLLO_PCIE_TEST_ENDPOINTS=true`로 활성화한다.
각 활성 root port마다 `virtio-net-pci` 한 개를 연결한다. 일반 부팅은 빈 root ports를 제공한다.

```bash
QBOX_APOLLO_PCIE_TEST_ENDPOINTS=true QBOX_APOLLO_PCIE_BIFURCATION=none \
./run_qbox_yocto.sh --machine apollo-qvp --bsp --headless --multi-session \
  --copy-disks --no-persistent-rse-state --record-initial-state \
  --out-dir build/pcie-gen5/default --timeout 600 --keep-running-after-pass

ssh -o BatchMode=yes -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null \
  -p 8022 root@127.0.0.1 sh -s default < scripts/test/test_apollo_pcie_lanes.sh
```

`port2`도 별도 출력 디렉터리에서 같은 방식으로 실행한다.
Guest script는 LinkCap, PCI parent/driver, IOMMU group, interface-bound ping,
TX/RX packet delta와 MSI IRQ delta를 확인한다. 임시 주소와 interface 상태를 복구한다.
기본 관리용 `eth0`나 이미 IPv4를 가진 PCI interface는 변경하지 않는다.

## 수정 과정에서 확인한 실패

실패 로그는 `build/pcie-gen5/` 아래에 보존한다. 부팅 PASS와 endpoint 기능 PASS는 다르다.

| 실행 디렉터리 | 관찰 | 수정 |
| --- | --- | --- |
| `default` | 포트 열거 성공, ping 실패, ACCESS_PLATFORM=0 | virtio endpoint에 `iommu_platform=true` 설정 |
| `default-final` | ACCESS_PLATFORM=1, `ip link up` timeout, `Blocked re-entrant IO` | GPEX forwarding proxy만 reentrancy guard 제외 |
| `default-proxy` | reentrancy 경고 해소, `ip link up`은 여전히 timeout | TBU의 고정 SID 대신 opt-in RequestContext SID 사용 |
| `default-sid` | `virtio: bogus descriptor or out of resources` | 검증용 PCI NIC의 native bounce buffer 한도를 1MiB로 설정 |
| `default-bounce`, `default-capture` | link-up/ping 불안정, RX/MSI 미완료 | 아래 IOTLB 주소 offset 오류 조사·수정 |
| `default-smmu` | 서로 다른 IOVA가 같은 PA로 변환됨 | IOTLB에 PA page/block base만 저장하고 실제 granule의 offset 합성 |

마지막 문제는 GPEX의 RID 전달만으로 해결되지 않았다. 기존 TBU가 모든 DMA를
`topology_id=0x40`으로 번역하여 Linux가 RID별로 만든 stream table과 일치하지 않았다.
`RequestContextSelectsStreamId` unit test는 SID `0x100`과 `0x200`이 각각 다른
물리 page로 변환되고, context가 없을 때 고정 SID로 돌아가는 것을 검사한다.

`default-smmu/qbox-platform.log`에서 `0xffffb240`과 이후 `0xffffb000`이
모두 `0x20008368240`으로 변환됐다. page table walk 결과의 offset을 제거하지 않고
IOTLB에 캐시했기 때문이다. 캐시 PA를 `req.pa & ~ret.addr_mask`로 정규화하고,
일반/debug 전송에서도 고정 4KiB mask 대신 `te.addr_mask`로 offset을 합성한다.
4KiB page와 2MiB block 테스트는 각각 offset `0x80`, `0x123000`을 먼저 접근한 뒤
base offset 0에 다시 접근하여 물리 주소가 구분되는지 검사한다.

별도 계측 실행 `default-trace`는 TF-A PFDI 초기화 중 정지해 종료했다.
`default-trace-retry`는 remoteproc/RPMsg BSP 검사에 실패했다.
두 실행은 PCIe 기능 PASS나 정상 부팅 증거에 포함하지 않는다.

## 정정 전 모델의 검증 이력

이 절은 x2 두 개 모두 분할 가능하다고 가정했던 이전 실행 기록이다.
현재 코드의 검증은 [RC–EP 및 단일 bifurcation 검증](rc-ep-loopback.md)을 참조한다.

검증일: 2026-09-12. `apollo-qvp`, cfg2/AP 4 CPU, `systemc-mmu720ae` backend.
로컬 기본 MACHINE은 `apollo-fvp`였으므로 모든 빌드/실행에서 QVP를 명시했고
`--keep-conf`로 기존 설정을 유지했다.

| 검사 | 결과 | 근거 |
| --- | --- | --- |
| BSP 빌드 | PASS, 5775 task 성공 | `build/pcie-gen5/bsp-offset.log` |
| QBox-platform recipe tests | 60/60 PASS, 6.72초 | `build/pcie-gen5/provider-check-qualified.log` |
| QBox core recipe 선택 tests | 60/60 PASS, 18.62초 | 같은 로그, `core-last-test-qualified.log` |
| RID/4KiB/2MiB SMMU 회귀 검사 | 각각 PASS, 각 3ms | `core-last-test-qualified.log` |
| Runner Python tests | 18/18 PASS | `build/pcie-gen5/runner-pytest.log` |
| map validator, core boundary audit, diff-check, shellcheck | PASS | 아래 재현 명령 |
| full-platform coverage audit | FAIL: `ap_9_1_1_memory_map=not_available`, `gate:G1=not_run` | `build/pcie-gen5/full-coverage-audit.json` |

빌드 경고 5개는 이전 forced task의 taint 경고다. 이번 작업에서 기존 테스트 제외
목록이나 timeout 정책은 변경하지 않았다. 초기 Linux DTS 검사에는 기존
`si_remoteproc` 경고 2개가 있었고 generic PCI binding 검사는 통과했다.
이번 launcher는 BSP login gate를 사용하고 post-login 전체 qualification을 실행하지 않는다.
따라서 PCIe guest test PASS를 전체 플랫폼 coverage PASS로 확대하지 않는다.

```bash
python3 -m pytest -q tests/test_gic720ae_full_runner_si0.py
python3 -m py_compile scripts/run/run_qbox_apollo_fvp_full.py
shellcheck -s sh scripts/test/test_apollo_pcie_lanes.sh
python3 scripts/test/validate_qbox_apollo_fvp_full_map.py
python3 scripts/test/audit_qbox_core_boundary.py
```

Runtime 결과는 각 `<mode>-qualified/result.json`의 부팅 PASS와 별도의
`guest-test.log` 최종 PASS를 함께 확인한다. `initial-state.json`은 입력 이미지
hash를 기록하며, `qualified-models.sha256`은 실행에 사용된 native 모델과 Lua의 hash다.

아래는 x2 두 개 모두 분할 가능하다고 가정했던 **정정 전 모델의 과거 실행 기록**이다.
`port3`, `both` PASS는 현재 지원 기능이 아니다. 최신 RC/EP 및 bifurcation 검증은
[RC–EP 문서](rc-ep-loopback.md)를 참조한다.

| 과거 모드 | root/endpoint 수 | 최대 lane 폭 (root slot 순) | 부팅/통신 | endpoint별 MSI 증가 |
| --- | --- | --- | --- | --- |
| `default` (`none`) | 4/4 | x4,x4,x2,x2 | PASS/PASS | 14,15,15,15 |
| `port2` | 5/5 | x4,x4,x1,x2,x1 | PASS/PASS | 15,15,14,14,15 |
| `port3` | 5/5 | x4,x4,x2,x1,x1 (slot 6) | PASS/PASS | 13,15,15,14,14 |
| `both` | 6/6 | x4,x4,x1,x1,x1,x1 | PASS/PASS | 12,15,15,14,15,13 |

총 20개 endpoint 검사에서 각각 ping 3/3 성공, TX 9~11 packet 증가,
RX 5 packet 증가, MSI 12~15회 증가를 확인했다. 모든 root의 최대 speed code는
5(32GT/s)였다. 모든 임시 주소와 link 상태를 복구했고, 마지막 검사 후 이번 작업의
QBox 프로세스만 종료했다. 로그 위치는 `build/pcie-gen5/{default,port2,port3,both}-qualified/`다.

## 변경 위치와 검증 범위

- QBox core: `qemu_pcie_root_port`, GPEX/virtio PCI 연결, RequestContext 전달,
  `smmuv3` TBU SID 및 IOTLB offset 처리와 회귀 테스트.
- QEMU: GPEX의 opt-in per-RID DMA address-space proxy와 안전한 해제 처리.
- QBox-platform: `ap_compute.lua`의 root ports, bifurcation, 검증용 endpoint와
  기존 native 모듈을 aggregate target에 포함하는 CMake 설정.
- Linux: `apollo-qvp.dts` generic ECAM host와 `apollo_qvp_defconfig`의 PCIEPORTBUS.
  Synopsys 전용 Linux driver는 추가하지 않는다.
- Root tooling: `scripts/test/test_apollo_pcie_lanes.sh`와 runner의 PCI 환경변수 기록.

이 검증은 QEMU 기능 모델의 PCI enumeration, Linux driver, SMMU DMA 및 MSI 통신을
대상으로 한다. Gen5 PHY 전기 특성, lane별 serial traffic, 32GT/s throughput은 모델링하거나
측정하지 않는다. 테스트 endpoint의 실제 Link Status는 Gen1 x1이며, Gen5 최대
Link Capability와 구분한다. 새 다중 root-port 구성의 INTx runtime, hotplug와
실행 중 bifurcation은 이번 검증 범위가 아니다. FVP PCIe parity도 주장하지 않는다.
