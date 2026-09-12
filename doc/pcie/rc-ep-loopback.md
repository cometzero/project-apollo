# Apollo QVP RC–EP Linux loopback

## 범위

단일 Apollo QVP의 Linux에서 port-group 0은 RC, port-group 1은 EP로 사용한다.
두 포트는 x4이며, group 2/3의 x2 RC 포트는 유지한다.
일반 RC 모드의 x1 bifurcation은 최종 사용자 확인에 따라 group 2 하나만 지원한다.
기존 QEMU GPEX/root port에 신규 가상 EPC를 연결하는 기능 모델이다.
QEMU 기본 root port를 EP로 바꾸거나 Synopsys EPC를 모델링한 것은 아니다.
서로 다른 두 Linux/보드 간 연결, 전기적 PHY 및 실제 Gen5 대역폭 검증도 아니다.

`QBOX_APOLLO_PCIE_EP_LOOPBACK=true`에서 root slot 2를 생성하지 않고,
root slot 1 아래에 EP PCI function을 연결한다. 기존 NIC/IRQ/bifurcation 테스트
옵션과 동시 사용하면 구성 오류로 처리한다. 일반 부팅의 RC 구성은 유지한다.

## 변경 위치

- QEMU: `hsoc-stack/tools/qemu/hw/pci/qbox-pcie-ep.c` 및 PCI Meson 등록.
- QBox: `hsoc-stack/tools/qbox/qemu-components/pci/qemu_pcie_epc/`,
  `qemu_pcie_test_ep/`의 libqemu-backed wrapper.
- Platform: `hsoc-stack/tools/qbox-platform/platforms/apollo/hw-block/ap_compute.lua`,
  `config.lua`, aggregate CMake 및 README.
- Linux: `drivers/pci/controller/pcie-qbox-ep.c`, Kconfig/Makefile, DT binding,
  `arch/arm64/boot/dts/arm/apollo-qvp.dts`, `arch/arm64/configs/apollo_qvp_defconfig`.
- Yocto: `meta-hsoc-bsp/recipes-test/pci-endpoint-selftest/` 및
  `meta-hsoc-auto-solutions`의 BSP package list.
- Root tooling: `scripts/test/test_apollo_pcie_endpoint.sh`,
  `test_apollo_pcie_lanes.sh`, runner 환경변수 기록,
  `tests/test_pcie_profile_contract.py`.

기존 upstream `pci_epf_test`, `pci_endpoint_test`, kselftest 데이터 검증 코드는 변경하지 않았다.

## 데이터 경로

RC의 `pci_endpoint_test`는 config space를 읽어 BAR0를 할당하고 MSI를 설정한다.
BAR0 접근은 신규 PCI function에서 EPC의 inbound 주소로 변환되어 SystemC의
AP RAM에 전달된다. EP Linux의 `pci_epf_test`가 이 RAM의 표준 test register를
읽고 처리한다. 테스트 결과를 hardware model에서 대신 계산하지 않는다.

EP가 RC memory에 접근할 때는 Linux EPC driver가 outbound window에 RC PCI/DMA
주소를 설정한다. EP의 `memcpy_fromio`/`memcpy_toio`는 PCI function의 native DMA
경로를 호출하고, GPEX의 RID와 SystemC SMMUv3 변환을 거쳐 RC 버퍼에 도달한다.
완료 시 EPF가 EPC driver를 통해 native MSI를 발생시키며 ITS/GIC가 RC driver에 전달한다.

두 Linux driver는 같은 kernel에서 실행하지만 BAR inbound와 outbound PCI 주소
변환은 서로 다른 경로를 통과한다. 단순 공유-memory 복사 테스트와 구분한다.

## EPC 인터페이스

| 항목 | 설정 |
| --- | --- |
| Device tree | `qbox,pcie-epc`, `30300000.pcie-epc` |
| Control MMIO | `0x30300000`, 4KiB |
| Outbound CPU aperture | `0x30400000`, 4MiB |
| EP function | PF 1개, VF 없음 |
| BAR | BAR0 64-bit, 고정 64KiB; 나머지 reserved |
| Interrupt | MSI 최대 32개; MSI-X/INTx 미지원 |
| Outbound mapping | 동시 2개, COPY의 source/destination 매핑 |

Control register는 little-endian 32-bit다.

| Offset | 용도 |
| --- | --- |
| `0x000`, `0x004` | ID `0x51455043`, version `0x00010000` |
| `0x008`, `0x00c` | 연결/시작/MSI/error 상태 및 START/STOP/CLEAR_ERROR |
| `0x020`–`0x028` | programmable PCI vendor/device, class/revision, subsystem ID |
| `0x100`–`0x10c` | BAR0 local physical address, size, enable |
| `0x200`–`0x208` | MSI requested/enabled count, 1-based vector 발생 |
| `0x300`, `0x320` | outbound slot별 local offset, PCI address, size, enable |
| `0x400` | 마지막 hardware error |

EPC의 MMIO 모델은 일반 부팅에도 존재한다. PCI function이 연결되지 않은 RC 모드에서는
LINK_PRESENT가 0이고 Linux EPC driver는 조용히 `-ENODEV`로 종료한다.
따라서 기본 DTS에 실제로 없는 MMIO 장치를 probe하는 구성이 아니다.

## 빌드 및 테스트

```bash
./yocto_build.sh --machine apollo-qvp --keep-conf --bsp

QBOX_APOLLO_PCIE_EP_LOOPBACK=true \
./run_qbox_yocto.sh --machine apollo-qvp --bsp --headless --multi-session \
  --copy-disks --no-persistent-rse-state --record-initial-state \
  --out-dir build/pcie-ep/loopback --timeout 600 --keep-running-after-pass

timeout 600 ssh -o BatchMode=yes -o StrictHostKeyChecking=no \
  -o UserKnownHostsFile=/dev/null -p 8022 root@127.0.0.1 sh -s \
  < scripts/test/test_apollo_pcie_endpoint.sh
```

Guest script는 configfs로 `pci_epf_test`를 생성하고 EPC를 시작한 뒤 RC를 rescan한다.
`16c3:edda`는 기존 Linux endpoint-test driver와 연결하기 위해 EPF가 프로그램하는
테스트 ID이며, Synopsys hardware 구현을 의미하지 않는다.
검증 도구는 BSP의 `/usr/bin/pci_endpoint_test`이고 upstream kselftest 원본을 빌드한다.

검사 항목은 BAR0, consecutive BAR, MSI, memcpy READ/WRITE/COPY다.
전송 크기는 각 방향에서 1, 1024, 1025, 1024000, 1024001 bytes다.
전용 DMA engine variant, BAR1–5, INTx, MSI-X는 실행하지 않는다.
CPU로 outbound window를 접근하더라도 RC 쪽에서는 실제 PCI bus-master transaction이다.

스크립트는 기존 endpoint/configfs 객체가 있으면 거부한다. 생성한 endpoint의
ID·parent를 확인한 뒤 제거하고 EPC 정지·configfs 정리를 수행한다.
정리까지 성공해야 최종 PASS를 출력한다. RC ioctl의 무한 대기를 막기 위해
host `timeout`을 사용하며, timeout은 PASS나 skip으로 처리하지 않는다.

## 검증 결과

검증일: 2026-09-12. QVP cfg2, AP 4 CPU, `systemc-mmu720ae` backend.
기존 `build/conf/`의 FVP 기본 설정을 유지하기 위해 빌드/실행에서 QVP를 명시했다.

| 검사 | 결과 | 근거 (`build/pcie-ep/` 아래) |
| --- | --- | --- |
| Linux kernel compile | PASS, 818 tasks | `kernel-compile.log` |
| kselftest recipe build/package QA | PASS, 926 tasks | `selftest-build.log` |
| QEMU/QBox provider compile | PASS, 902 tasks | `provider-compile.log` |
| BSP build | PASS, 5793 tasks | `bsp-build.log` |
| QBox-platform / core 선택 tests | 각각 60/60 PASS, 6.73초 / 19.00초 | `provider-check.log` |
| Host profile/runner tests | 25/25 PASS | `host-tests.log` |
| RC–EP 첫 정상 실행 | 6/6 PASS, skip 0, MSI 0→47, cleanup PASS | `loopback/endpoint-test-retry.log` |
| 같은 boot에서 제거 후 재구성 | 6/6 PASS, skip 0, MSI 0→47, cleanup PASS | `loopback/endpoint-test-cycle2.log` |
| 일반 RC 회귀 | boot PASS, NIC 4/4 ping·TX/RX·MSI PASS | `rc-default/result.json`, `rc-default/lanes-test.log` |
| 단일 x2 bifurcation 회귀 | boot PASS, NIC 5/5 ping·TX/RX·MSI PASS | `rc-port2/result.json`, `rc-port2/lanes-test.log` |

Endpoint는 `0000:01:00.0`, parent `0000:00:01.0`, RID `0x0100`, IOMMU group 4,
driver `pci-endpoint-test`로 확인했다. BAR0는 RC `0x60300000`에 할당됐다.
각 실행은 READ/WRITE/COPY에서 위 다섯 크기를 모두 검사한다. CRC/data 검증은
upstream driver가 수행한다. 총 두 실행에서 30개 전송-size 조합을 검증했다.
`loopback/qbox-primary-console.log`에 EPF의 크기별 완료 로그가 있다.

`loopback/pci-link-state.log`에서 RC slot 1의 reported link는 32GT/s x4이고,
EP로 전환한 slot 2는 RC 목록에 없다. 이는 QEMU functional link 상태이며
PHY training이나 실효 Gen5 대역폭 증거가 아니다.

첫 시도 `loopback/endpoint-test.log`는 `missing_msi_irqs`로 실패했다.
Linux 6.18 driver는 probe 시 IRQ를 할당하지 않고 `PCITEST_SET_IRQTYPE`에서 할당한다.
검증 스크립트가 이를 너무 일찍 확인한 것이 원인이었으며, MSI test 이후로 확인을
옮겼다. 모델·Linux test driver는 이 실패 때문에 수정하지 않았다.

입력 이미지 hash는 각 run의 `initial-state.json`, 모델/Lua hash는
`model-artifacts.sha256`에 보존한다. map validator, core boundary audit, Lua/shell
syntax, shellcheck, diff-check와 kernel strict checkpatch는 통과했다.
DT binding의 YAML lint는 통과했으나 host `dt-doc-validate`는 Python `dtschema`
모듈 부재로 실행하지 못했다. BSP의 경고 5개는 기존 forced-task taint 경고다.
검증 종료 후 이번 작업에서 실행한 QBox 프로세스만 종료했다.

회귀 검증은 `QBOX_APOLLO_PCIE_EP_LOOPBACK`을 설정하지 않고
`QBOX_APOLLO_PCIE_TEST_ENDPOINTS=true`와 `QBOX_APOLLO_PCIE_BIFURCATION=none` 또는
`port2`로 각각 부팅한 뒤 `test_apollo_pcie_lanes.sh default` 또는 `port2`를 실행했다.
정정된 구성의 유효한 모드는 이 두 가지이며, `port3`/`both` 거부는
`tests/test_pcie_profile_contract.py`에서 검사한다.

전체 플랫폼 coverage audit는 `ap_9_1_1_memory_map=not_available`, `gate:G1=not_run`으로
실패했다(`full-coverage-audit.json`). 이번 BSP login + PCI endpoint 검증을 전체
플랫폼 qualification 또는 FVP parity PASS로 확대하지 않는다.
