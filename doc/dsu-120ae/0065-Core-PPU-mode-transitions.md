# Core PPU mode transitions

Source: <https://developer.arm.com/documentation/107721/0001/Power-management/Core-PPU-modes/Core-PPU-mode-transitions>

### Core PPU mode transitions

Each core supports a set of Power Policy Unit (PPU) mode transitions. These transitions are controlled by their respective core PPU. Therefore, a System Control Processor (SCP) can program a core PPU to go to any allowed PPU mode, and the PPU automatically makes the necessary transitions to reach the requested PPU mode.

> ### Note
>
> The
> core PPU controls which
> PPU mode the
> core enters at reset deassertion.

The following figure shows the permitted core PPU mode transitions.

Figure 1. Permitted core PPU mode transitions

![Permitted core PPU mode transitions](images/0065-Core-PPU-mode-transitions-img01.svg)

### On mode (ON)

In the On core PPU mode, the core is on and fully operational.

The core can be initialized into the On mode. When a transition to the On mode completes, all caches are accessible and coherent. Other than the normal architectural steps to enable caches, no additional software configuration is required.

### Off mode (OFF)

In the Off core PPU mode, all core logic and RAMs are powered down. The domain is inoperable and all core state is lost.

The core L1 and L2 caches are disabled, cleaned and invalidated and the core is removed from coherency automatically on transition to an Off mode.

Any attempted debug access when the core domain is off returns an error response on the internal debug interface, indicating that the core is not available.

### Functional retention (FUNC\_RET) mode

In the Functional retention core PPU mode, a portion of the core, typically the Single Instruction Multiple Data (SIMD) and floating-point logic, is powered down while the remainder of the core is fully powered and operational.

If an instruction needs the logic that is powered down to complete execution, then the instruction is stalled until the core has transitioned to the On mode.

### Full retention mode (FULL\_RET)

In the Full retention core PPU mode, all core logic, and core cache RAMs are placed in retention. The core is non-operational but retains its state.

Full retention mode is typically used when the core is in Wait for Interrupt (WFI) or Wait for Event (WFE) state for an extended time. If a snoop, L1 or L2 cache maintenance operation or debug access occurs, then the core transitions to the On mode to process the access. Then it can transition back to Full retention mode without the core leaving corresponding WFI or WFE state.

### Debug recovery mode (DBG\_RECOV)

Debug recovery core PPU mode can be used to assist debug of external reset events such as watchdog timeout. It allows contents of the core L1 data and L2 caches that were present before the reset to be observable after reset. The contents of the caches are retained and are not invalidated on the transition back to the On mode.

> ### Note
>
> - You must only use Debug recovery mode for debug purposes. You must not use it for functional purposes as correct operation of the caches are not guaranteed when entering this mode.
> - Debug recovery mode can occur at any time with no guarantee of the state of the core, therefore its effects on the core, cluster, or the wider system are UNPREDICTABLE and a wider system reset might be required. In particular, if there were outstanding memory system transactions at the time of the reset, then these might complete after the reset when the core is not expecting them and therefore might cause a system deadlock.

### Emulated off mode (OFF\_EMU)

In Emulated off mode core PPU mode, all core domain logic, and core RAMs are kept physically powered up. However, the functional logic is reset to emulate a powerdown scenario while keeping core Debug state and allowing debug access.

All Debug registers must retain their state and are accessible from the external debug interface. All other functional interfaces behave as if the core was in the Off mode.

### Warm reset mode (WARM\_RST)

Warm reset mode applies a Warm reset to the core logic. When in Warm reset, the following applies:

- If any core is put into Warm reset mode, then the cluster must also be put into Warm reset mode and the other cores must go into Warm reset mode or OFF mode.
- To apply a Warm reset to an individual core, you must program the corresponding Power Policy Unit (PPU) for the core.
- Warm reset mode is only expected to be used for resets triggered by a system-level issue, such as a watchdog timeout.
