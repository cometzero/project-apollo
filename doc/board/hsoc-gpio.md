# HSOC GPIO / pinctrl register contract

`hsoc_gpio` replaces the previous `hsoc_pinctrl` SystemC register ABI.
Linux uses `hsoc,peri0-gpio` / `hsoc,peri1-gpio`; the existing
`pinctrl_peri0` and `pinctrl_peri1` instance/DT labels remain stable.
Controller resources stay in `apollo-qvp.dts`, banks and pin states in
`pinctrl.dtsi`.

## Bank topology

PERI0: `0x301e0000`, 6 eight-pin banks and 8 one-pin banks (56 pins).
PERI1: `0x301f0000`, 4 eight-pin banks and 4 one-pin banks (36 pins).
The MMIO windows remain `0x10000` bytes; GIC SPIs remain 334–347 / 348–355.

Bank N starts at **controller base + N * 0x1000**. Bank0 has no preceding
global header page. No register reports bank/pin counts or a model ID/version.
The model's `bank_sizes` CCI parameter and DT `hsoc,npins` declarations
define the matching topology. Linux pin IDs stay dense (0–55 / 0–35),
while SystemC socket indices and `HSOC_PINMUX(bank,pin,function)` retain
the hardware selector `bank * 8 + pin`.

## Registers

All offsets below are bank-relative, 32-bit little-endian. For pin N,
one-bit fields use bit N, two-bit fields use bits `2*N+1:2*N`, and
four-bit fields use bits `4*N+3:4*N`. Bits for unimplemented pins read zero.

| Offset | Register | Bits/pin | Meaning |
| --- | --- | --- | --- |
| 0x000 | PROT | — | Permission Chip ID, unused; reads zero, writes ignored |
| 0x100 | SEL | 4 | 0 input, 1 output, 2–15 alternate function |
| 0x104 | DAT | 1 | Read input or output latch according to SEL; write output latch |
| 0x108 | PS | 1 | 0 pull-down, 1 pull-up |
| 0x10c | PE | 1 | 0 pull enabled, 1 disabled |
| 0x110 | DS | 2 | 0/1/2/3 = 1x/2x/3x/4x |
| 0x114 | IS | 1 | 1 enables input Schmitt configuration |
| 0x118 | IE | 1 | 1 enables input buffer |
| 0x200 | INTR_CON | 4 | 0 high, 1 low, 2 falling, 3 rising, 4 both edges |
| 0x204 | INTR_PEND | 1 | Pending status; write 1 to clear |
| 0x208 | INTR_MIRR_PEND | 1 | Read-only mirror of pending status |
| 0x20c | INTR_MASK | 1 | 1 masks bank IRQ contribution |
| 0x210 | INTR_FLT_TYP | 1 | 0 logic filter, 1 time filter |
| 0x214 | INTR_FLT_DEPTH | 4 | 0 bypass, 1–15 filter depth |

The field packing not explicitly supplied in the request uses the above
model contract. Reset selects GPIO input with input buffer disabled, output
latch zero, DS=1x, pulls disabled, interrupts masked and filters bypassed.
PROT is not an access-control mechanism in this implementation.

Pending state is separate from interrupt masking. W1C clears the selected
pending bits; an active level condition may reassert subsequently. Interrupt
detection uses GPIO input mode and an enabled input buffer.

Pulls provide a digital default only until a pin has an external driver write.
A driven low is not overridden by a pull-up. The bool signal interface has
no high-impedance/electrical resolution. DS and Schmitt settings are register
configuration metadata; analog drive current and hysteresis are not modeled.
The filter clock period is an explicit simulation parameter, not a measured
silicon timing specification.

CCI `filter_clock_period` defaults to 10ns. Logic filtering requires the
configured number of consecutive equal samples on that clock grid; raw
glitches between sample ticks do not restart its counter. Time filtering
requires the raw input to remain stable for `depth * filter_clock_period`
from its last transition. Filters affect interrupt detection, not DAT reads.
Reset and filter reconfiguration cancel pending filter decisions.

## Linux pin configuration

Use `hsoc,drive-strength = <0..3>` for the raw DS multiplier encoding.
The old mA `drive-strength` and `slew-rate` properties are not used by this ABI.
I2C/UART default to DS=1 (2x), SPI to DS=3 (4x), with `input-enable`.
Standard bias and input-buffer/Schmitt properties configure PS/PE/IE/IS.
`hsoc,interrupt-filter-type` (0/1) and `hsoc,interrupt-filter-depth` (0–15)
configure per-pin interrupt filtering. Current DWC routes use SEL=2;
other alternate selectors are register-configurable but have no additional
board peripheral assignment.

```dts
i2c0_pins: i2c0-pins {
    pinmux = <HSOC_PINMUX(0, 0, 2)>, <HSOC_PINMUX(0, 1, 2)>;
    hsoc,drive-strength = <1>;
    input-enable;
};
```

## Validation

```bash
./yocto_build.sh --keep-conf --bsp
./scripts/run/ssh_run.sh scripts/test/verify_qbox_hsoc_pinctrl.sh
./scripts/run/ssh_run.sh scripts/test/verify_qbox_hsoc_peripherals.sh
```

The guest tests run on a dedicated QBox BSP session. They check dense IDs,
packed SEL/DS/IE, pull selection, GPIO/DAT, IRQ type/mask/pending mirror,
I2C mux gating and serial peripheral traffic. Component tests cover register
validation, reset, level/edge IRQ semantics and filtering.

Historical validation of the replaced ABI is retained in
[hsoc-pinctrl.md](hsoc-pinctrl.md).

### 2026-09-09 evidence

Artifacts: `build/qbox-apollo-qvp/hsoc-gpio-20260909/`.

- BSP build: PASS (`bsp-build.log`, `kernel-compile.log`).
- Provider tests: 51/51 PASS, including `hsoc_gpio-tests`
  (`provider-tests.log`). The temporary unit-test setting was restored.
- BSP boot: PASS (`runtime/result.json`, with hashed launch inputs).
- Linux GPIO qualification: PASS (`guest-gpio.log`): dense pin IDs,
  SEL/DS/IE defaults, pull-up/down/disable on a single-pin bank,
  GPIO high/low loopbacks, IRQ type/mask, pending clear and mirror,
  six I2C EEPROM reads, and I2C5 mux gating/recovery.
- SPI0–3 16-byte loopback and UART0/1, UART2/3 bidirectional 32-byte
  transfers: PASS (`guest-peripherals-final.log`,
  `runtime-regression/result.json`). The first guest had reached its
  run timeout before this separate test, so a fresh BSP guest was used.
- Full platform coverage retains the existing `G1: not_run` and
  `ap_9_1_1_memory_map: not_available` gaps (`full-coverage-audit.json`).

The component tests include all five interrupt modes, reserved-bit masks,
reset, synchronous DAT, and filter reconfiguration. With a 10ns period,
an input transition at grid+5ns and depth 2 is accepted at grid+20ns by
the logic filter and at grid+25ns by the time filter.

Static checks include DT compilation, arm64 driver object compilation,
ShellCheck, map/boundary checks and whitespace checks. Full DT schema
validation remains unavailable because the host lacks the required
`dtschema` module. This does not qualify analog electrical behavior or
full FVP equivalence.
