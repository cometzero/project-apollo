# Apollo FVP PCIe 부팅 복구 (2026-09-11)

## 변경과 한계

FVP의 PCIe4 호스트를 기본 비활성화하여 ECAM 접근을 피한다.
PCIe 모델 자체를 수정하거나 RAS 예외를 무시하는 변경은 아니다.
QVP PCIe 구성, PCI/ITS 커널 설정, 외부 Arm 저장소는 변경하지 않는다.

다음 두 프로젝트 소유 DTS의 `pcie4`에 `status = "disabled"`를 추가했다.

- `hsoc-stack/components/primary_compute/linux/arch/arm64/boot/dts/arm/apollo-fvp.dts`
- `hsoc-stack/components/primary_compute/trusted-firmware-a/fdts/apollo_fvp_fvp.dts`

두 번째 파일은 TF-A `platform.mk`에서 cfg1/cfg2의 `HW_CONFIG`로 선택되어
FIP에 포함된다. 이번 FVP BSP의 A/B UKI에는 `.dtb` 섹션이 없다.
따라서 Linux 배포 DT만 변경하면 실제 부팅 DT에는 반영되지 않는다.
UKI의 DT 포함 여부를 QVP와 동일하다고 가정해서는 안 된다.

## 실패 근거

원본 로그는 `build/fvp-tmux/apollo-fvp-20260911-135205/`에 있다.
Linux는 `pci-host-generic 10040000000.pcie`의 ECAM 영역을 등록한 뒤 멈췄다.
TF-A는 `plat_handle_uncontainable_ea`에서 `PANIC in EL3`를 기록했다.

- `ESR_EL3 = 0xbe000211`
- `ELR_EL3 = 0xffff8000807d0c50`
- 해당 빌드 `vmlinux`의 주소 해석: `pci_bus_read_config_dword`

Linux DTS만 수정한 첫 재검증도 동일한 PCIe 호스트 접근 후 실패했다.
해당 로그는 `build/fvp-pcie-boot-recovery/runtime/`에 보존했다.
이는 배포 DT 검사만으로 실제 게스트 DT를 검증할 수 없음을 보여준다.

## 재현 명령

현재 설정은 `apollo-fvp`, cfg2, AP CPU 4개, `build/tmp_baremetal`이다.
공유 BitBake 작업은 병렬로 실행하지 않는다.

```bash
./yocto_build.sh --machine apollo-fvp --keep-conf --bsp
fdtget build/tmp_baremetal/deploy/images/apollo-fvp/apollo-fvp.dtb \
  /soc/pcie@10040000000 status
python3 scripts/run/runfvp_log_boot.py \
  --machine apollo-fvp \
  --fvpconf build/tmp_baremetal/deploy/images/apollo-fvp/nexios-bsp-initramfs-apollo-fvp.fvpconf \
  --out-dir build/fvp-pcie-boot-recovery/runtime-fip \
  --timeout 900 --require all --min-runtime 70 --no-login \
  --post-login-command 'if test "$(tr -d "\000" < /sys/firmware/devicetree/base/soc/pcie@10040000000/status)" = disabled && test ! -e /sys/bus/platform/devices/10040000000.pcie; then echo FVP_PCIE_DISABLED_PASS; else echo FVP_PCIE_DISABLED_FAIL; fi'
```

runner의 post-login 완료 표시는 명령 성공과 다르다.
게스트 로그의 독립된 `FVP_PCIE_DISABLED_PASS` 출력과 부팅 결과를 함께 확인한다.

## 최종 검증 결과

- BSP 빌드: PASS. 최종 `build-fip.log`에서 5,091개 task 중 5,064개 재사용,
  나머지 모두 성공했다. Linux 및 TF-A 저장소의 `git diff --check`도 통과했다.
- 생성된 Linux DT와 TF-A `debug/fdts/apollo_fvp_fvp.dtb`: 모두 `disabled`.
- FVP 부팅: PASS, runner 측정 **77.574초**. RSE, SI CL0/CL1, TF-A,
  U-Boot/Linux의 모든 필수 부팅 조건을 만족했다.
- 게스트: `NEXIOS_BSP_INITRAMFS_READY machine=apollo-fvp`, `nexios-bsp#`,
  독립된 `FVP_PCIE_DISABLED_PASS` 출력 확인. 실행 중 DT가 disabled이고
  `10040000000.pcie` platform device가 생성되지 않았음을 검사했다.

최종 증거는 `build/fvp-pcie-boot-recovery/runtime-fip/`의 `result.json`,
`summary.txt`, `initial-state.json` 및 UART 로그에 있다.
`initial-state.json`에는 AP flash와 WIC 등 실행 입력의 SHA-256이 기록되어 있다.
이 검증은 BSP 부팅 1회이며, full product 이미지와 QVP 런타임은 재검증하지 않았다.

## PCIe opt-in 검증

위 두 DTS에서 `pcie4`의 status를 명시적으로 `"okay"`로 바꾸고,
동일한 BSP 명령으로 커널 DT뿐 아니라 TF-A/FIP 및 부팅 이미지를 재빌드한다.
별도 출력 디렉터리에서 실패 로그를 수집한다. 검증 후 기본값은 복구한다.
ECAM SError가 다시 발생할 수 있으므로 일반 부팅용 기본값으로 사용하지 않는다.

PCIe/ITS 검증은 endpoint enumeration, 실제 장치 트래픽, MSI-X/LPI 전달을
별도로 입증해야 한다. PCIe를 비활성화한 부팅 성공은 그 증거가 아니다.
과거 QBox PCIe IRQ 결과는 QBox 전용이며 FVP 동등성을 입증하지 않는다.
현재 checkout에서 누락된 `.omo/evidence` 입력 때문에 실패하는 과거 검증도
이번 부팅 복구 결과와 구분한다.
