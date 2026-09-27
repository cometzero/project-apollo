# Controlling PD_CPU0RAM power states

Source: <https://developer.arm.com/documentation/102803/latest/Functional-Description/Power-Control-Infrastructure/Basic-level-power-infrastructure/BR-SYS-power-modes/Controlling-PD-CPU0RAM-power-states>

### Controlling PD\_CPU0RAM power states

The BR\_SYS bounded region uses operating modes to support the ability to turn on or off the cache RAMs in modes other than the OFF mode.

- Power modes with cache RAMs disabled, called the NOCACHE operating modes, are suffixed with NOCACHE.
- Power modes with cache RAMs enabled, called the CACHE operating modes, are the modes without the NOCACHE suffix.

To select the use of the NONCACHE operating modes, the following registers must be configured:

- Set CPDLPSTATE.RLPSTATE register in the CPU to OFF which is 0b11,
- Set MSCR.DCACTIVE register in the CPU to 0b0 to disable Data Cache,
- Set MSCR.ICACTIVE register in the CPU set to 0b0 to disable Instruction Cache.

Transitions between the two operating modes can only occur between the ON and ON\_NOCACHE power modes.

When in the NOCACHE operating modes, the PD\_CPU0RAM is always turned off. When operating in the CACHE operating modes, PD\_CPU0RAM enters RAM retention when entering MEM\_RET, LOGIC\_RET or FULL\_RET power modes.
