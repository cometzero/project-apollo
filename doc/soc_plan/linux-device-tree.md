# Apollo Linux Device Tree 분리 계획

작성일: 2026-10-02. 상태: **구현 적용**. 빌드·부팅과 gate별 결과는 [구현·검증 기록](linux-device-tree-implementation.md)을 참조한다. 아래 분석·예제는 변경 전 source를 기준으로 작성한 설계 기록이다.
대상 Linux revision: `29f64112e551761cbaf84b31ebfc79b5ffa4c26d`.

요청한 네 파일로 분리한다. `apollo.dtsi`는 AP Linux가 보는 SoC 자원과 공통 firmware 인터페이스, `apollo-pinctrl.dtsi`는 pin controller와 bank/mux 정의, `apollo-qvp.dtsi`는 QBox가 제공하는 가상 장치·실행 profile, `apollo-qvp-saturn-v.dts`는 board population과 최종 활성화를 소유한다. 파일 이동으로 최종 장치 주소·IRQ·DMA 연결·노드 경로를 바꾸지 않는 것이 첫 구현의 기준이다.

SoC의 board 선택 peripheral은 기본 `status = "disabled"`로 둔다. CPU/GIC/timer와 부팅에 필요한 SCMI 경로 등 공통 기반 자원은 유지한다. 여기서 “항상 켜짐”은 DT의 기본 가용성 정책이며 실제 clock·power domain이 항상 켜져 있다는 뜻이 아니다.

앞선 [Lua 구조 분리](implementation.md)와 같은 책임 구분을 사용하되, Lua component와 Linux DT node를 일대일 대응시키지는 않는다. 예를 들어 SoC PCIe IP의 QBox 구현이 Linux에는 합성 ECAM host로 노출되는 경우, 그 가상 host 설명은 QVP 파일이 소유한다.

## 1. 현재 구조와 확인한 문제

현재 파일은 모두 Linux `arch/arm64/boot/dts/arm/` 아래에 있다.

| 파일 | 행 수 | 현재 내용 |
|---|---:|---|
| [apollo-qvp.dtsi](../../build/qbox-apollo-qvp/dt-refactor/baseline/apollo-qvp.dtsi) | 868 | 16 CPU/cache/topology, GIC/ITS, timer, SCMI/MHU/SRAM, UART/watchdog/RTC/GPIO, SI remoteproc 및 reserved memory |
| [apollo-qvp.dts](../../build/qbox-apollo-qvp/dt-refactor/baseline/apollo-qvp.dts) | 638 | Board identity/aliases/memory, PCIe/SMMU/VirtIO, DMA/I2C/SPI/UART/I2S, pin controller, audio card/가상 codec, EEPROM, SPI loopback, SI 활성화 |
| [pinctrl.dtsi](../../build/qbox-apollo-qvp/dt-refactor/baseline/pinctrl.dtsi) | 374 | PERI0/PERI1 bank, GPIO range/name, mux group와 전기적 설정 |
| [apollo-qvp-board.dtsi](../../build/qbox-apollo-qvp/dt-refactor/baseline/apollo-qvp-board.dtsi) | 46 | RTC alias, I2C0 EEPROM 2개 추가, PCA9539 IRQ/reset/line name |

현재 include는 `apollo-qvp.dts` → `apollo-qvp.dtsi`, `pinctrl.dtsi`, `apollo-qvp-board.dtsi`다. 이름과 달리 대부분의 SoC peripheral이 최상위 `.dts`에 있으며, EEPROM도 controller 안에 섞여 있다. SI 관련 8개 node는 base에서 disabled, 최상위에서 okay로 바꾸지만 다른 board peripheral은 대체로 `status`가 없어 기본 활성 상태다.

계획 작성 과정에서 변경하지 않은 source를 CPP와 DTC로 컴파일했다. 컴파일은 성공했고 기존 경고는 2종이다: `/soc/si_remoteproc`의 `simple_bus_reg`, 그 하위 `si-cl1`의 `unit_address_vs_reg`. 명령·source SHA-256·DTB hash·경고는 [baseline 기록](../../build/qbox-apollo-qvp/dt-refactor-plan/baseline.json)에 있다. 이는 source 문법 확인이며 Yocto 배포본 또는 부팅 검증이 아니다. 경고를 없애기 위해 이 작업에서 remoteproc 경로를 임의로 바꾸지 않는다.

## 2. 목표 파일과 include 순서

사용자가 지정한 경로의 kernel source 기준 전체 이름은 `arch/arm64/boot/dts/hsoc/`다.

```text
arch/arm64/boot/dts/
  Makefile                         # subdir-y += hsoc
  hsoc/
    Makefile                       # canonical DTB 등록
    apollo.dtsi                    # SoC + 공통 firmware 인터페이스
    apollo-pinctrl.dtsi             # SoC pin controller/bank/mux
    apollo-qvp.dtsi                 # QBox 가상 장치와 profile
    apollo-qvp-saturn-v.dts         # 최종 Board entry
```

Include는 한 방향으로 구성한다.

```text
apollo-qvp-saturn-v.dts
  includes apollo-qvp.dtsi
    includes apollo.dtsi
      includes apollo-pinctrl.dtsi
```

- Board는 `apollo-qvp.dtsi` 하나만 include한다. 같은 SoC/pinctrl 파일을 다시 include하지 않는다.
- `apollo.dtsi`가 `soc` label과 공통 provider를 정의한 뒤 끝에서 pinctrl 파일을 include한다.
- `apollo-pinctrl.dtsi`가 `&soc` 아래 두 controller를 정의한다. 현재 DTS의 controller 본체와 기존 `pinctrl.dtsi`의 bank/mux를 이 파일로 모아 이중 소유를 피한다.
- `.dtsi`에는 `/dts-v1/;`, board `model`, root board `compatible`, `chosen`, board population을 넣지 않는다.
- `apollo.dtsi`만 include한 임시 검사용 DTS도 unresolved phandle 없이 컴파일되어야 한다. VP가 공급하는 I2S clock 참조는 QVP 파일에서 연결한다.
- `/soc`, `/cpus`, `/reserved-memory` 같은 **최종 node hierarchy는 그대로 둔다**. 파일을 나눴다는 이유로 domain bus나 node 중간 계층을 추가하지 않는다.

이는 SoC `.dtsi`와 Board `.dts`를 재사용 가능한 hardware 단위로 나누라는 [Linux DTS 작성 지침](https://docs.kernel.org/devicetree/bindings/dts-coding-style.html#organizing-dtsi-and-dts)에 맞춘 프로젝트 설계다. QVP 계층은 현재 가상 platform의 예외를 공통 SoC 정의에서 분리하기 위한 것이다.

## 3. 노드별 소유권과 status 정책

### 3.1 SoC와 pinctrl

| Node/기능 | 새 소유 파일 | 기본 상태 | 최종 Saturn-V profile |
|---|---|---|---|
| CPU 0–15, cache, `cpu-map` | `apollo.dtsi` | 기존 CPU topology 유지 | CPU 수를 Board 이름에 고정하지 않고 기존 build/runtime 조정 유지 |
| GIC/ITS, architectural timer, MMIO REFCLK timer | `apollo.dtsi` | 가용, status 생략 가능 | 주소·GICR view·PPI/SPI·timer frame 유지 |
| 공통 24 MHz clock | `apollo.dtsi` | 가용 | 기존 `/clock-24000000`, 이름·주파수 유지 |
| PSCI, SCMI/DVFS, `sram`/SCMI shmem, `mbox_db_tx/rx` | `apollo.dtsi` | 가용 | 하나의 boot-critical 의존성 집합으로 유지 |
| DSU PMU 4개 | `apollo.dtsi` | 기존 가용성 유지 | CPU 축소 시 기존 PMU 처리와 함께 검증 |
| SBSA watchdog, PL031 RTC | `apollo.dtsi` | 공통 내부 장치로 가용 유지 | 현재 항상 제공되는 profile 기준; board RTC alias는 Board 소유 |
| `soc_serial0` PL011 | `apollo.dtsi` | **disabled** | Board에서 enable하고 `chosen.stdout-path`로 선택 |
| `smd_gpio` PL061 | `apollo.dtsi` | **disabled** | PCA9539 reset/IRQ provider로 Board에서 enable |
| `smmu` | `apollo.dtsi` | **disabled** | PCIe와 함께 Board에서 enable; 기존 reg/IRQ/MSI 계약 보존 |
| `dma350_0/1` | `apollo.dtsi` | **disabled** | DMA consumer를 사용하는 Board에서 두 controller enable |
| `dw_i2c0..5`, `dw_spi0..3`, `dw_uart0..3`, `dw_i2s0..1` | `apollo.dtsi` | **disabled** | Board에서 기존 전체 population을 명시적으로 enable |
| `pinctrl_peri0/1`, bank와 mux group | `apollo-pinctrl.dtsi` | controller **disabled** | Board에서 controller enable, peripheral별 pinctrl state 선택 |
| SI remoteproc parent/CL1, MHU TX/RX, reserved-memory 4개 | `apollo.dtsi` | 기존 **disabled** 유지 | Board에서 8개 node 모두 enable |

`smmu`는 QEMU model로 구현된다는 이유만으로 가상 장치로 분류하지 않는다. 현재 FVP와 QVP DTS 모두 같은 SoC SMMU register/interrupt/MSI 계약을 사용한다. 반면 아래의 QBox EPC와 relocated ECAM host는 현재 가상 노출 방식으로 한정한다. 판단 근거는 [기존 FVP SMMU](../../hsoc-stack/components/primary_compute/linux/arch/arm64/boot/dts/arm/apollo-fvp.dts#L49), [QVP SMMU](../../build/qbox-apollo-qvp/dt-refactor/baseline/apollo-qvp.dts#L218), [계약 테스트](../../tests/test_apollo_fvp_pcie_dts_contract.py#L122)다.

SI reserved-memory의 주소와 `memory-region`/MHU 채널 번호는 현재 firmware ABI로 보존한다. 향후 다른 firmware layout을 지원할 때 layout 소유권을 재검토하며, 이번에 단순 board RAM 크기 설정처럼 변경하지 않는다.

### 3.2 QVP 전용 구성

| 현재 구성 | 배치와 이유 |
|---|---|
| `virtio@30020000`/`30030000`/`30040000`/`30050000`/`30060000`/`30080000` | 모두 `apollo-qvp.dtsi`. QBox가 제공하는 virtual transport이며 기존 기본 가용성 유지 |
| `pcie@43b50000` generic ECAM host | `apollo-qvp.dtsi`. QVP host의 ECAM/ranges/INTx swizzle/RID→ITS/SMMU map을 함께 보존. 기본 disabled, Board에서 enable |
| `pcie_epc` / `qbox,pcie-epc` | `apollo-qvp.dtsi`. [Binding 자체가 virtual EPC](../../hsoc-stack/components/primary_compute/linux/Documentation/devicetree/bindings/pci/qbox,pcie-epc.yaml#L7). 기본 disabled, Board에서 기존처럼 enable |
| 4개 `linux,spi-loopback-test` child | QVP 파일의 `&dw_spiN` 확장으로 이동. controller가 활성화되면 현재 시험 profile에 그대로 존재 |
| `i2s_clk` 1.536 MHz fixed clock, `linux,spdif-dit/dir` 4개, simple-audio-card 2개 | QVP 파일. 현재 가상 loopback endpoint를 실물 codec으로 설명하지 않는다. `dw_i2sN`의 VP clock 연결도 여기서 수행 |
| Audio card 최종 활성화 | QVP에서 card 기본 disabled, Board에서 `dw_i2s0/1`, `dma350_1`, `i2s0_sound/1_sound`를 함께 enable |
| 예시 cpuidle latency/residency | 현재 base source가 illustrative라고 명시한 값은 QVP profile로 이동. `cpu_sleep`/`cluster_sleep` label과 각 CPU의 참조는 보존 |

DMA 채널 번호와 consumer `dmas`는 현재 SoC 연결 계약이므로 `apollo.dtsi`에 둔다. VP 실행을 위한 정책을 추가로 발견한 경우만 QVP override로 분리한다. 현재 source에는 과거의 `cyclic_done_pause` property가 없으므로 refactor 과정에서 다시 도입하지 않는다.

현재 기본 QVP DT가 시험용 SPI/audio 구성을 포함한다는 사실도 유지한다. 이들을 opt-in overlay로 바꾸는 일은 별도의 동작 변경이다. 파일 분리만으로 장치를 지우거나 활성화 기본값을 바꾸지 않는다.

### 3.3 Saturn-V Board

`apollo-qvp-saturn-v.dts`는 다음 내용을 소유한다.

- Root identity, aliases, `chosen`, memory population. 첫 전환에서는 `model = "Apollo QVP"`와 기존 `compatible` 배열을 그대로 유지해 이름 변경과 machine 매칭 변경을 분리한다.
- DRAM의 두 `reg` tuple: `0x80000000 / 0x7f000000`, `0x20000000000 / 0x80000000`. 주소와 크기를 다른 단위로 재해석하거나 RAM hole을 채우지 않는다.
- I2C 0–5의 `eeprom@50` 6개, I2C0의 `eeprom@51/52`, PCA9539 `gpio@74`.
- I2C bus 속도, chip-select 수, peripheral의 `pinctrl-names`/`pinctrl-0`, pin group의 전기적 설정과 GPIO line-name policy.
- 위 표의 optional controller와 SI firmware interface 활성화.

Board 이름을 위한 새로운 root compatible은 이번에 만들지 않는다. 필요하면 vendor-prefix와 board binding을 검토하는 별도 변경에서 추가한다. 현재 Saturn-V schematic/BOM 대응은 Lua 계획과 마찬가지로 **UNVERIFIED**다. 기존 QVP population을 이 이름의 profile로 옮기는 것이며 새 실물 부품·regulator·LED를 추정해서 추가하지 않는다.

TPS6594는 현재 SI CL0 firmware가 소유한다. Linux Board DT에 PMIC나 그 regulator/GPIO controller를 중복 생성하지 않는다. 근거는 [현재 Board DTSI의 ownership 주석](../../build/qbox-apollo-qvp/dt-refactor/baseline/apollo-qvp-board.dtsi#L5)이다.

## 4. Disabled 정책에서 반드시 지킬 의존성

Linux는 `status`가 없거나 `okay`/`ok`인 node를 가용으로 판단한다. Board가 사용 여부를 정할 node는 base에 명시적으로 `disabled`를 넣는다. [DTSpec status](https://devicetree-specification.readthedocs.io/en/stable/devicetree-basics.html#status), [현재 Linux 구현](../../hsoc-stack/components/primary_compute/linux/drivers/of/base.c#L469).

| Consumer | 함께 필요한 활성 provider/ancestor |
|---|---|
| I2C0 EEPROM/PCA9539 | `dw_i2c0`, `pinctrl_peri0`, pin state; PCA9539에는 `smd_gpio`도 필요 |
| SPI0/1 DMA | 해당 SPI, PERI0 pinctrl, `dma350_0` |
| UART0/1 DMA | 해당 UART, PERI0 pinctrl, `dma350_0` |
| I2S0/1 DMA audio | 해당 I2S, PERI0 pinctrl, `dma350_1`, QVP clock/codec/card |
| SPI2/3, UART2/3 | 해당 controller와 PERI1 pinctrl; 기존에 없는 DMA 연결을 추가하지 않음 |
| PCIe | `pcie`, `smmu`, 공통 `its`/`gic` |
| SI CL1 remoteproc | `si_remoteproc`, `si_cl1`, MHU TX/RX, resource table/vring/buffer 4개 |

`&dw_i2c0 { status = "okay"; };`만으로 disabled pinctrl/DMA/GPIO provider가 자동 활성화되지는 않는다. 마찬가지로 remoteproc child만 enable해도 disabled parent를 대체할 수 없다. 조립 검사는 이 의존성을 확인해야 한다.

**GPIO bank와 pin configuration group에는 controller와 같은 일괄 disabled 정책을 적용하지 않는다.** PERI0는 14 bank/56 pin, PERI1은 8 bank/36 pin이다. [pinctrl driver](../../hsoc-stack/components/primary_compute/linux/drivers/pinctrl/pinctrl-hsoc.c#L755)는 available bank를 읽고 index의 연속성을 검사한다. 사용하지 않는 중간 bank만 disabled로 만들면 전체 controller probe가 실패할 수 있다. Parent만 기본 disabled로 두고 전체 bank topology와 순서를 유지한다.

Pinmux의 bank stride 8과 `gpio-ranges`의 누적 pin offset은 서로 다른 값이다. `hsoc,npins`, bank별 IRQ 순서, `HSOC_PINMUX()` 값을 다시 계산하지 않고 보존한다. Pinmux 후보 group은 pinctrl 파일에, 해당 group을 선택하는 `pinctrl-0`과 drive/input 설정은 Board에 둔다. [HSOC binding](../../hsoc-stack/components/primary_compute/linux/Documentation/devicetree/bindings/pinctrl/hsoc,peri0-gpio.yaml#L12).

## 5. 작성 예제

아래는 책임 구분을 보여주는 발췌이며 그대로 빌드할 수 있는 전체 파일은 아니다.

```dts
/* apollo.dtsi: controller 고유 자원만 정의 */
dw_i2c0: i2c@30100000 {
	compatible = "snps,designware-i2c";
	reg = <0x0 0x30100000 0x0 0x10000>;
	interrupts = <GIC_SPI 320 IRQ_TYPE_LEVEL_HIGH>;
	clocks = <&soc_clk24mhz>, <&soc_clk24mhz>;
	clock-names = "ref", "pclk";
	#address-cells = <1>;
	#size-cells = <0>;

	status = "disabled";
};
```

```dts
/* apollo-qvp-saturn-v.dts: entry와 Board 선택의 발췌 */
/dts-v1/;
#include "apollo-qvp.dtsi"

/ {
	model = "Apollo QVP";
	compatible = "arm,apollo-qvp", "arm,zena-css", "arm,vexpress";

	chosen {
		stdout-path = &soc_serial0;
	};
};

&pinctrl_peri0 {
	status = "okay";
};

&i2c0_pins {
	hsoc,drive-strength = <1>;
	input-enable;
};

&soc_serial0 {
	status = "okay";
};

&dw_i2c0 {
	clock-frequency = <400000>;
	pinctrl-names = "default";
	pinctrl-0 = <&i2c0_pins>;

	status = "okay";

	eeprom@50 {
		compatible = "atmel,24c02";
		reg = <0x50>;
		pagesize = <8>;
	};
};
```

기존 SPDX/copyright를 보존한다. Linux DTS 관례의 tab 들여쓰기, lower-case hex, label은 underscore, node 이름은 기존 경로를 유지한다. `status`는 일반 property 뒤/child 앞에 두고 Board override는 같은 순서로 정렬한다. 주소·IRQ·DMA cell array의 값 순서를 formatting 대상으로 취급하지 않는다. [DTS 작성 지침](https://docs.kernel.org/devicetree/bindings/dts-coding-style.html#order-of-properties-in-device-node).

## 6. 보존할 DT 계약

파일과 label 추가는 가능하지만 다음의 의미는 그대로 유지한다.

- 모든 node의 절대 경로, `compatible`, `reg`, `ranges`, IRQ type/index, clock name/frequency, DMA request 번호, PCI domain과 MSI/IOMMU map.
- GICD `0x20800000`, ITS `0x20840000`, 16개 GICR region, architectural timer PPI와 REFCLK frame 0 SPI 49. SPI index를 INTID와 혼동해 32를 더하지 않는다.
- DMA0 SPI 279, DMA1 SPI 358의 채널별 8개 interrupt tuple. 중복처럼 보이는 IRQ를 하나로 줄이지 않는다.
- DMA0: SPI0 TX/RX 0/1, SPI1 2/3, UART0 4/5, UART1 6/7. DMA1: I2S0 0/1, I2S1 2/3.
- EEPROM 8개와 PCA9539 주소, IRQ의 SMD GPIO1/active-low, reset의 GPIO0/active-low.
- 현재 `serial0..3` alias는 DW UART이고 `chosen.stdout-path`는 PL011이다. 둘을 하나의 console alias로 정리하지 않는다.
- `/soc/si_remoteproc/si-cl1`, 4개 reserved-memory와 MHU 채널/순서, CPU/cache/PMU 참조.
- 기존 label은 가능한 한 유지한다. 새 Board override에 필요한 watchdog/RTC 등 label 추가는 DT node 이름 변경과 구분한다.

CPU node 선언 순서도 보존한다. [AP-only prepare.py](../../hsoc-stack/tools/qbox-platform/platforms/apollo/linux-boot/prepare.py#L82)는 `fdtget -l /cpus` 순서로 CPU를 선택·삭제한다. 단순 문자열 정렬로 `cpu@10000` 등을 앞당기면 같은 CPU 수를 선택해도 MPIDR 집합이 달라질 수 있다.

## 7. Kbuild·Yocto·배포 경로 전환

### Kbuild

```make
# arch/arm64/boot/dts/Makefile
subdir-y += hsoc

# arch/arm64/boot/dts/hsoc/Makefile
dtb-$(CONFIG_ARCH_VEXPRESS) += apollo-qvp-saturn-v.dtb
```

현재 [arm/Makefile](../../hsoc-stack/components/primary_compute/linux/arch/arm64/boot/dts/arm/Makefile#L8)은 FVP DTB만 등록하고 QVP는 recipe의 명시적 타깃으로 빌드한다. 이번에는 새 DTB를 정식 등록한다. `apollo_qvp_defconfig`의 기존 `CONFIG_ARCH_VEXPRESS=y`를 사용하고 파일 경로 이동만을 위해 새 `ARCH_HSOC`를 만들지 않는다.

### 경로는 세 단계로 구분

| 소유자 | 현재 값 | 목표 값 |
|---|---|---|
| Kernel recipe `KERNEL_DEVICETREE:apollo-qvp` | `arm/apollo-qvp.dtb` | `hsoc/apollo-qvp-saturn-v.dtb` |
| Deploy basename | `apollo-qvp.dtb` | `apollo-qvp-saturn-v.dtb` |
| Image recipe `KERNEL_DEVICETREE` / `QBOX_IMAGES[dtb]` | `apollo-qvp.dtb` | `apollo-qvp-saturn-v.dtb` |

Kernel 값은 [linux-yocto-apollo-qvp.inc](../../hsoc-stack/yocto/meta-hsoc-bsp/recipes-kernel/linux/linux-yocto-apollo-qvp.inc#L13), image 값은 [nexios-apollo-qboxboot.inc](../../hsoc-stack/yocto/meta-hsoc-auto-solutions/recipes-core/images/include/nexios-apollo-qboxboot.inc#L12)가 소유한다. 기본 `KERNEL_DTBVENDORED=0`인 [kernel-devicetree.bbclass](../../layers/poky/meta/classes-recipe/kernel-devicetree.bbclass#L85)는 vendor 경로를 제거해 배포한다. 따라서 image 쪽에 `hsoc/`를 그대로 넣으면 UKI 입력 파일을 찾지 못할 수 있다. 구현 시 실제 BitBake 최종 값을 다시 확인한다.

`MACHINE=apollo-qvp`, defconfig 이름, image 이름, QBox Lua entry는 변경하지 않는다. linux-yocto/RT provider 모두 같은 DT 선택 경로를 확인한다.

### 호환 기간

1. 새 canonical DTS를 추가하고 기존 `arm/apollo-qvp.dts`는 `#include "../hsoc/apollo-qvp-saturn-v.dts"`만 가진 임시 wrapper로 유지할 수 있다. `/dts-v1/;`를 중복 선언하지 않는다.
2. 호환 배포가 필요하면 owned BSP deploy 단계에서 `apollo-qvp.dtb`를 새 DTB의 alias로 제공한다. 두 이름의 hash가 같아야 하며 source를 두 벌 유지하지 않는다.
3. UKI의 `KERNEL_DEVICETREE`에는 **canonical basename 하나만** 지정한다. 호환용 DTB를 UKI 입력 목록에 추가하지 않는다.
4. 모든 소비자를 전환한 뒤 wrapper/alias와 더 이상 참조되지 않는 옛 QVP DTSI/board/pinctrl 파일을 제거한다. 현재 `arm/pinctrl.dtsi`의 include 사용자는 QVP 하나지만 삭제 시 다시 검색한다.

## 8. 런처·검사기와 firmware 경계

**Full-system의 `--ap-dtb`는 현재 Linux DTB를 주입하는 스위치가 아니다.** [runtime parser](../../scripts/run/qbox_apollo_runtime.py#L5381)는 이를 forwarded identity로 받고, 실제 Linux는 WIC의 UKI `.dtb`를 사용한다. 새 파일 경로를 이 인자에 전달했다는 사실만으로 새 DT로 부팅했다고 판정하지 않는다.

Full-system 검증은 kernel DTB → UKI A/B `.dtb` → WIC ESP → guest live DT까지 추적한다. [A/B UKI 생성](../../hsoc-stack/yocto/meta-hsoc-auto-solutions/classes/auto-ad-nexios-uki-ab.bbclass#L129)이 배포 DTB를 삽입하므로 DT 변경 후 UKI와 WIC를 재생성한다. Secure Boot를 사용하면 UKI 재서명도 검증한다. 현재 U-Boot의 FIT 지원 옵션이 켜져 있다는 이유로 Linux의 활성 포장 경로를 FIT라고 설명하지 않는다.

AP-only는 [run_qbox_linux.py](../../scripts/run/run_qbox_linux.py#L519)가 선택한 DTB를 [prepare.py](../../hsoc-stack/tools/qbox-platform/platforms/apollo/linux-boot/prepare.py#L54)로 복제·수정해 `QBOX_LINUX_DTB`로 전달한다. 입력 DTB와 생성된 `linux.dtb`를 모두 검사해야 한다. CPU 삭제, cpu-map 제거, PMU/VirtIO 조정, reserved memory/SCMI/RPMsg 경로의 기존 동작을 보존한다.

| 소비자 | 필요한 변경 |
|---|---|
| `run_qbox_yocto.sh`, `run_qbox_apollo_fvp_full.py` | 명시적 DTB/qboxconf 선택 우선순위 유지, `${MACHINE}.dtb` 등 fallback을 canonical 이름에 맞춤 |
| `run_qbox_linux.py`, QBox AutoSD | canonical basename 기본값, manifest 우선 선택, AP-only prepare 후 tree 검증 |
| `verify_qbox_linux_audio.py`, `prepare_qbox_apollo_pcie_irq_profile.py` | 기본 DTB 및 파생 profile 입력 변경 |
| `build_gic720ae_linux_probe_profile.py`, `capture_gic720ae_default_deploy_manifest.py` | kernel 타깃과 image basename 구분, artifact identity 갱신 |
| `gic720ae_pcie_irq_validation_inventory.py` | 새 DTS/DTSI source graph와 모든 include hash 수집 |
| `test_apollo_fvp_pcie_dts_contract.py`, `test_apollo_fvp_gpio.py` | 경로/CPP include 변경; 단일 source 문자열보다 compiled DT의 실제 property 검사 |
| `test_run_qbox_linux.py`, `test_run_qbox_yocto_*`, `nexios_bsp_workflow_support.py` | canonical DTB 및 구 alias 호환 fixture |

Standalone QEMU 기본 부팅은 machine-generated DT를 사용하고 외부 DTB는 `--dtb`를 명시할 때만 사용한다. AutoSD UKI adaptation도 `.dtb`를 제거해 firmware DT를 쓰는 별도 경로가 있다. 이 경로와 QBox AutoSD의 외부 Linux DTB 경로를 구분한다. 과거 `.omo/evidence/` 등 역사적 증거의 파일명을 일괄 치환하지 않는다.

다음은 이번 변경의 대상이 아니다.

- U-Boot 자체 `arch/arm/dts/apollo-qvp.dts`와 `CONFIG_DEFAULT_DEVICE_TREE`.
- TF-A의 `fdts/apollo_qvp*.dts*`, HW/FW/TOS config 및 FIP/certtool payload. TF-A의 `LINUX_DTS=1`도 별도 저장소의 source를 뜻한다.
- `apollo-fvp.dts/.dtsi`를 새 SoC 파일로 통합하는 작업. 먼저 QVP만 전환하며 FVP source/DTB 회귀를 확인한다.
- Linux driver 수정, peripheral 주소 재배치, 새로운 DMA 정책, 실물 Saturn-V population 추가.

## 9. 단계별 구현과 완료 조건

| 단계 | 작업 | 완료 조건 |
|---|---|---|
| 0. Baseline | 기존 4개 source, include graph, kernel/recipe SHA, 최종 BitBake 변수, 배포 DTB와 UKI/live DT 보존 | 원본 source와 동일 옵션의 산출물을 확보하고 기존 FAIL/경고 분리 |
| 1. SoC/pinctrl 추출 | 공통 node 이동, optional status disabled, pinctrl provider/bank/mux 분리 | SoC-only 임시 DTS 컴파일; virtual/board 장치 없음, 의도한 optional node만 disabled |
| 2. QVP/Board 조립 | 가상 transport/시험/audio profile, Board enable와 population 이동 | 새 Board의 effective DT가 baseline과 동등; dependency 누락 없음 |
| 3. 빌드·소비자 전환 | Kbuild, 두 Yocto layer, 런처/검사기/fixture 전환 | canonical DTB 배포·선택, alias 동일성, UKI 입력 한 개 |
| 4. 검증 | static/schema/negative, kernel+BSP build, full/AP-only runtime | 아래 gate별 결과 기록, 기존 실패와 신규 회귀 구분 |
| 5. 정리 | 구 wrapper/alias 사용처 확인 후 제거, 문서·검증 결과 갱신 | 중복 DTS 정의 없음, root gitlink는 owning repo 커밋을 가리킴 |

소유 repository별로 Linux DTS/Kbuild, BSP metadata, image metadata, root 소비자/테스트/문서를 구분한다. 외부 `layers/`와 read-only `arm-zena-css/`는 수정하지 않는다. 이 문서는 설계 기준을 보존하며 실제 수행 결과는 구현·검증 기록에서 관리한다.

## 10. 검증 설계

### Compiled DT 비교

단순 텍스트 diff나 DTB hash만으로 구조 이동의 동등성을 판정하지 않는다. Include 순서가 바뀌면 phandle 숫자나 property 저장 순서가 달라질 수 있다.

- 전체 node path와 property를 비교한다. Scalar/array/string, 빈 boolean property, 존재 여부를 보존한다.
- Phandle은 node path로 해석해 비교한다. `clocks`, `dmas`, `interrupt-parent`, `msi-parent`, `msi-map`, `iommu-map`, `interrupt-map`, `gpio-ranges`, `reset-gpios`, `sound-dai`, `memory-region`, `mboxes`, CPU/cache/pinctrl 참조를 provider의 `#*-cells`에 맞춰 해석한다. 모든 u32를 숫자가 같다는 이유로 phandle로 치환하지 않는다.
- 승인된 peripheral의 `status` 생략 ↔ `okay`만 동등하게 처리한다. `disabled`와 `okay`는 반드시 차이로 검출한다. 숫자/주소/IRQ 차이를 광범위한 allowlist로 무시하지 않는다.
- 기존 label을 사용하는 overlay가 있으면 `__symbols__`에서 label→path를 검증한다. 새 label 추가와 기존 label 제거를 구분한다.
- CPU node 순서를 별도로 확인하고, source DTB뿐 아니라 같은 옵션의 AP-only 변환 후 DTB와 full-system live DT도 비교한다. Initrd 주소·bootargs 등 동적 값은 이름과 이유가 정해진 항목만 따로 검증한다.

### Static / negative gate

1. 새 canonical과 임시 legacy entry를 CPP+DTC 및 `W=1` target build로 확인한다. 현재 2종 경고를 baseline으로 기록하며 신규 경고는 원인을 설명한다.
2. 관련 binding의 `dtbs_check`를 실행한다. 기존 Apollo root/custom binding의 문제와 이번 refactor가 추가한 문제를 분리하며, schema 실패를 단순 DTS compile PASS로 대체하지 않는다.
3. SoC-only 검사에서 board EEPROM/PCA9539, VirtIO, QBox EPC, SPI loopback, 가상 codec/card가 없어야 한다. Optional controller는 disabled여야 한다.
4. Board에서 pinctrl/DMA/GPIO/remoteproc parent enable 하나를 누락한 fixture를 만들어 dependency 검사가 실패하는지 확인한다.
5. GPIO bank 중간 누락, IRQ 또는 DMA request 한 개 변경, phandle target 변경, 높은 DRAM 주소 절단, baseline node 누락을 검출하는 mutation test를 둔다.

### Build / deploy gate

현재 machine은 `apollo-qvp`, template은 `meta-hsoc-auto-solutions/conf/templates/apollo-qvp`, TMPDIR은 `build/tmp_baremetal`이다. 구현 때 활성 설정과 provider를 다시 확인하고 shared BitBake는 직렬로 실행한다. 아래 명령의 실제 실행 결과는 구현·검증 기록에 정리한다.

```bash
./yocto_build.sh --keep-conf virtual/kernel
./yocto_build.sh --keep-conf nexios-bsp-initramfs
```

평범한 빌드가 DTS/DTSI 변경을 추적하는지 확인하고, 강제 task나 sstate 삭제로 의존성 누락을 숨기지 않는다. Image의 DTB basename, `.qboxconf`, UKI A/B에 삽입된 DTB, WIC ESP를 검증한다. 런처는 명시적 인자 → manifest → canonical fallback 순서를 유지한다.

현재 [Apollo kernel externalsrc 설정](../../hsoc-stack/yocto/meta-hsoc-bsp/recipes-kernel/linux/linux-yocto-apollo-common.inc#L5)은 [source-tree hash](../../layers/poky/meta/classes/externalsrc.bbclass#L203)를 통해 tracked 수정과 ignore되지 않은 새 source를 `do_compile` 입력으로 추적한다. [Kbuild DT depfile](../../hsoc-stack/components/primary_compute/linux/scripts/Makefile.dtbs#L119)은 include된 DTSI를 추적한다. DTS 변경 때문에 `do_configure`까지 반드시 재실행되어야 하는 것은 아니다. 현재 configure는 `.config`를 생성하며 CPU/SMMU를 위해 특정 DTS 파일을 직접 편집하는 경로는 발견하지 않았다. 실제 ordinary 재빌드와 DTB 갱신은 구현 단계에서 확인한다.

### Runtime gate

- Full-system 기본 AP 4/RSE/CL0/CL1 firmware 경로: Linux login, BSP READY, 표준 post-login, SCMI, GIC/ITS/SMMU, remoteproc/RPMsg/HIPC/PFDI, timer, watchdog/RTC.
- AP-only: CPU 1/4/16과 disk 유무의 파생 DT 정합성을 모두 확인하고, 기본 AP4 boot·audio DMA/PIO를 실행한다. AP1/AP16은 native smoke도 수행하거나 미실행을 명시한다.
- 활성 I/O: I2C 6개 bus와 I2C0 다중 EEPROM, PCA9539 GPIO/IRQ/reset, SPI PIO 4개 controller, UART/DMA와 audio의 기존 검사. GPIO bank/line numbering과 console alias도 확인한다.
- Linux DT와 대응 Lua에서 MMIO/IRQ/DMA request/board address가 일치하는지 확인한다. Lua 파일과 DTS label 이름이 같다는 것만으로 PASS하지 않는다.
- Full-system SPI/UART DMA, AP-only BSP `pfdi_misc`, FVP evidence 부재의 기존 FAIL은 [앞선 검증 기록](implementation.md#실행-중-확인한-dma-실패)과 대조한다. PIO fallback, node 비활성화, DMA property 제거로 실패를 숨기지 않는다.

증거는 `build/qbox-apollo-qvp/dt-refactor/` 아래 static/build/deploy/full/AP-only로 나누고 명령·source revision·입력/출력 DTB hash·실제 loaded DT를 함께 기록한다. 이 계획의 완료 판정은 구조 전환과 지정된 gate 검증이며 physical timing, 전체 power/reset 또는 FVP/RTL 동등성을 주장하지 않는다.
