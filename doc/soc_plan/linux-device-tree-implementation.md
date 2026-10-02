# Apollo Linux Device Tree 구현·검증

작성일: 2026-10-02. 상태: **구조 전환·빌드·부팅 및 지정 검증 완료, 기존 실패/제한 유지**. [설계 계획](linux-device-tree.md)에 따라 Linux DT를 SoC·QVP·Saturn-V Board로 분리했다. 검증 기록은 `build/qbox-apollo-qvp/dt-refactor/`에 보존한다.

## 구현

Linux `arch/arm64/boot/dts/hsoc/`에서 다음 include 순서로 구성한다.

```text
apollo-qvp-saturn-v.dts
  -> apollo-qvp.dtsi
      -> apollo.dtsi
          -> apollo-pinctrl.dtsi
```

| 파일 | 책임 |
|---|---|
| [apollo.dtsi](../../hsoc-stack/components/primary_compute/linux/arch/arm64/boot/dts/hsoc/apollo.dtsi) | CPU/cache/topology, interrupt/timer, SCMI와 SI firmware ABI, SoC controller. Board 선택 peripheral은 기본 disabled |
| [apollo-pinctrl.dtsi](../../hsoc-stack/components/primary_compute/linux/arch/arm64/boot/dts/hsoc/apollo-pinctrl.dtsi) | PERI0/PERI1 controller와 전체 bank·pinmux. Parent만 기본 disabled |
| [apollo-qvp.dtsi](../../hsoc-stack/components/primary_compute/linux/arch/arm64/boot/dts/hsoc/apollo-qvp.dtsi) | VirtIO, 합성 ECAM/EPC, SPI loopback, audio clock/codec/card, illustrative cpuidle |
| [apollo-qvp-saturn-v.dts](../../hsoc-stack/components/primary_compute/linux/arch/arm64/boot/dts/hsoc/apollo-qvp-saturn-v.dts) | 기존 identity/aliases/chosen/DRAM, EEPROM 8개/PCA9539, pin 전기 설정·line name, controller와 SI 경로 활성화 |

`arm/apollo-qvp.dts`는 새 entry를 include하는 소스 호환 wrapper로 유지한다. 중복 정의였던 기존 `arm/apollo-qvp.dtsi`, `apollo-qvp-board.dtsi`, `pinctrl.dtsi`는 제거했다. FVP DTS, U-Boot control DT, TF-A firmware DT는 변경하지 않았다. Linux에 TPS6594를 추가하지 않았으며 SI CL0 소유권을 유지한다.

Kbuild는 기존 `CONFIG_ARCH_VEXPRESS`로 `hsoc/apollo-qvp-saturn-v.dtb`를 등록한다. BSP kernel recipe는 이 vendor 경로를 사용하고, image recipe와 `QBOX_IMAGES[dtb]`는 배포 basename `apollo-qvp-saturn-v.dtb`를 사용한다. 런처·audio/PCIe 검사기·provenance 수집도 전환했다. 명시적 인자 → manifest → 기본값 순서는 유지한다.

배포에는 새 이름 하나만 사용한다. 구 `apollo-qvp.dtb` 배포 alias는 추가하지 않는다. 과거 manifest/WIC는 새 빌드 결과로 교체해야 한다. 명시적 입력이나 manifest로 보존한 구 DTB를 선택하는 동작은 지원한다.

## 정적 계약

[apollo_dt_contract.py](../../scripts/test/apollo_dt_contract.py)는 compiled DT의 모든 node/property를 비교한다. Binding별 reference cell만 phandle target path로 변환하고 주소·IRQ·DMA argument 등 나머지 값은 그대로 비교한다. 승인된 선택 peripheral에서만 생략된 status와 `okay`를 동등하게 취급한다. CPU 선언 순서, bank topology, provider/ancestor 활성화도 검사한다.

- 배포 전후 197개 node의 의미가 동일하다. 기존 label 131개의 target path도 모두 보존했다.
- SoC 단독 컴파일과 기본 disabled 정책, Board 조립 의존성 검사 통과.
- PERI0 14 bank/56pin, PERI1 8 bank/36pin의 순서·폭·GPIO range·line name·전기 설정 보존.
- Lua descriptor와 AP I2C/SPI/UART/I2S/DMA MMIO·SPI IRQ·DMA request 및 PCA9539 주소의 19개 계약 대조 통과.
- CPP/DTC의 기존 remoteproc 경고 두 종류는 유지했다. `W=1 dtbs_check`도 실행했으며, 관련 binding 검사에서 HSOC pinctrl node 이름·pinmux 길이 진단 18개가 baseline과 동일하다. **Schema 전체 PASS는 아니다.**

원본 source·배포 DTB·UKI DT는 [baseline](../../build/qbox-apollo-qvp/dt-refactor/baseline/), 정적 결과는 [static](../../build/qbox-apollo-qvp/dt-refactor/static/) 아래에 있다.

## 빌드·부팅 검증

활성 구성은 `MACHINE=apollo-qvp`, `linux-yocto-rt 6.18.5+git`, AP CPU 4, `build/tmp_baremetal`이다. Image UKI의 `UEFI_SECURE_BOOT=0`이므로 이번 런타임은 unsigned BSP UKI 경로다.

```bash
./yocto_build.sh --keep-conf virtual/kernel
./yocto_build.sh --keep-conf nexios-bsp-initramfs
```

강제 task 또는 sstate 삭제 없이 실행한다. Full-system `--ap-dtb`는 identity 인자이므로 UKI/WIC에 포함된 `.dtb`와 guest live DT를 직접 수집한다. AP-only는 입력 DTB와 `prepare.py`가 만든 DTB를 구분한다.

| Gate | 결과와 근거 |
|---|---|
| Kernel 일반 빌드 | PASS, 1,121 tasks. `do_compile`에서 새 `hsoc/apollo-qvp-saturn-v.dtb`를 생성하고 deploy 완료. [로그](../../build/qbox-apollo-qvp/dt-refactor/kernel-build.log) |
| BSP 일반 빌드 | 첫 실행의 native CTest 종료 timeout 뒤, 소스·필터·timeout 변경 없이 재실행 PASS, 5,847 tasks. [성공 로그](../../build/qbox-apollo-qvp/dt-refactor/image-build-retry.log) |
| Native 검사 | 재실행 platform 64/64, core 61/61 PASS. 기존 core 제외 28개 정책 유지. 최초 4-CPU timer 두 phase의 종료 timeout은 미해결 불안정성으로 보존. [첫 실패](../../build/qbox-apollo-qvp/dt-refactor/native-check-initial-fail.log), [재실행](../../build/qbox-apollo-qvp/dt-refactor/native-check-retry.log) |
| 배포 → UKI → WIC | PASS. canonical DTB와 A/B UKI `.dtb`, WIC ESP A/B `.dtb`가 byte-identical. `.qboxconf`도 새 이름 선택. [manifest](../../build/qbox-apollo-qvp/dt-refactor/deploy/manifest.json) |
| Full-system boot | PASS. AP4/RSE/CL0/CL1, BSP READY, 표준 post-login·timer 검사, monitor/QMP 4 domain 정상. [runner](../../build/qbox-apollo-qvp/dt-refactor/full/result.json) |
| Full-system Board I/O | PASS. PCA9539 GPIO/IRQ/reset, I2C0 다중 EEPROM, I2C 6개 bus, SPI 4개 controller의 8-byte PIO. PMIC 검사는 Linux에 중복 PMIC가 없는 소유권·RTC·EEPROM 검사다. [결과](../../build/qbox-apollo-qvp/dt-refactor/full-qualification.json) |
| Full live DT | PASS. 변경 전 native boot의 live DT와 197개 node 비교. EFI pointer/size/seed 5개 값만 정규화하고 property 존재·길이·bootargs·descriptor ABI는 검증. [비교 결과](../../build/qbox-apollo-qvp/dt-refactor/full-live-comparison.json) |
| FVP 정적 회귀 | PASS. 보존한 source와 현 source hash 및 동일 CPP/DTC 결과 일치. FVP native boot는 수행하지 않음. [결과](../../build/qbox-apollo-qvp/dt-refactor/static/fvp-regression.json) |
| AP-only 파생 DT | PASS. CPU1/4/16 × disk 유무 6개 구성 비교. [matrix](../../build/qbox-apollo-qvp/dt-refactor/static/ap-prepare-matrix.json) |
| 소비자·검사기 pytest | 151 + 42 = 193 PASS. 확장 suite는 163 PASS와 기존 PFDI metadata exact-string assertion 1 FAIL. [소비자](../../build/qbox-apollo-qvp/dt-refactor/consumer-tests-focused.log), [validator](../../build/qbox-apollo-qvp/dt-refactor/static/validator-tests.log), [확장 검사](../../build/qbox-apollo-qvp/dt-refactor/consumer-tests.log) |

AP-only native CPU1/16은 각각 18.7초/26.0초에 부팅·요청 CPU 수·manifest DT 선택 검사를 통과했다. 생성 DT와 guest live DT는 byte 및 semantic 비교에서 일치했다. 런처는 검증 후 SIGTERM으로 정리했으므로 자연 종료 안정성을 증명하지 않는다. [AP smoke 결과](../../build/qbox-apollo-qvp/dt-refactor/ap-smoke-summary.json).

AP4 audio는 DMA/PIO 모두 PASS다. 각 모드에서 DMA350 두 controller의 memcpy/memset, 양방향·동시 PCM, 양방향 WAV의 byte 일치와 IRQ를 검사했다. PIO는 private DTB에서 I2S DMA property만 제거한 명시적 비교 profile이며 배포 DTB는 DMA를 유지한다. [audio 결과](../../build/qbox-apollo-qvp/dt-refactor/ap-only-audio/result.json).

AP-only BSP selftest는 FAIL을 유지한다. AP4 audio 실행에서는 기존 `pfdi_misc` 실패가 남고, AP1은 `pfdi_misc`·고정 expected=4 CPU 검사·disabled DSU PMU 검사, AP16은 `pfdi_misc`·고정 expected=4 CPU 검사가 실패했다. CPU1/16 smoke의 독립적인 실제 CPU 수 검사는 각각 요청값과 일치했다.

AP-only `prepare.py`는 CPU를 삭제하면서 disabled DSU PMU의 `cpus` 참조를 남기는 기존 동작이 있다. 기본 comparator는 dangling reference를 거부한다. 파생 DT 비교에는 변경 전후의 원본 DTB를 companion으로 제공하여 **disabled DSU PMU에서 삭제된 CPU만** 원래 node path로 복구했다. 다른 dangling reference를 허용하지 않으며 최초 NOT_COMPARABLE 결과도 보존했다.

이번 명령에는 `-f`/`-C`가 없고 sstate를 삭제하지 않았다. Build log의 tainted 경고는 작업 시작 전에 있던 forced-task 표시다. 첫 native timer timeout은 기능 PASS marker 뒤 종료 실패였고 bounded GDB 실행 및 일반 재빌드는 정상 종료했다. 재시도 성공으로 안정성 문제가 해결됐다고 판정하지 않는다.

이 실행에서 재생성·부팅한 것은 `nexios-bsp-initramfs`다. `nexios-image` product WIC 및 Secure Boot signing 경로의 새 런타임 검증은 수행하지 않았다.

## 남은 실패와 제한

| 항목 | 이번 실행의 판정 |
|---|---|
| Full SPI DMA | FAIL. 기본 SPI probe에서 `d350_irq()`의 synchronous external abort. QEMU가 channel 3 `CH_STATUS`(offset `0x1304`)의 re-entrant I/O를 차단. [결과](../../build/qbox-apollo-qvp/dt-refactor/full-spi-dma-qualification.json) |
| Full UART DMA | FAIL. UART probe에서 `d350_pause()`의 synchronous external abort. QEMU가 channel 5 `CH_CMD`(offset `0x1500`)를 차단. [결과](../../build/qbox-apollo-qvp/dt-refactor/full-uart-dma-qualification.json) |
| AP-only BSP selftest | 위에 기재한 PFDI 및 CPU profile별 검사 FAIL. 별도 boot/audio PASS로 대체하지 않음 |
| DT schema | 기존 HSOC pinctrl 진단 18개 유지. Node 경로 보존이 이번 refactor의 계약이므로 rename이나 binding 변경을 섞지 않음 |
| Native timer 종료 | 첫 BSP build의 4-CPU timer 두 테스트 timeout 보존. 재빌드 PASS는 종료 안정성 해결의 증거가 아님 |
| 확장 pytest | 기존 PFDI recipe `SRC_URI` 전체를 고정 문자열로 비교하는 assertion 1개 FAIL. 현재 recipe의 기존 veth patch 추가분과 불일치하며 DT 변경과 무관 |

SPI/UART는 [앞선 Lua 검증](implementation.md#실행-중-확인한-dma-실패)에서도 실패한 경로다. 이번에 같은 exception handler/re-entrancy 차단을 재현했지만 실패 채널은 이전 SPI channel 1/UART channel 7과 달랐다. 이를 정확히 같은 채널의 재현이라고 주장하지 않는다. 새 DTB의 주소·IRQ·DMA 계약과 변경 전후 live DT는 별도로 동등성을 확인했다. DMA property 제거 또는 peripheral 비활성화로 이 실패를 숨기지 않았다.

## 판정 범위

실물 Saturn-V schematic/BOM 일치, physical timing, 전체 power/reset, FVP/RTL parity는 검증 범위가 아니다. 기존 SPI/UART DMA 및 AP-only PFDI selftest 문제는 별도로 기록하며, PIO나 AP-only 성공을 full-system DMA 성공으로 해석하지 않는다.
