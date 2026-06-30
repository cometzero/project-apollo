# Isolating a chip from the system

Source: <https://developer.arm.com/documentation/102666/0201/Getting-started-with-GIC-720AE/Isolating-a-chip-from-the-system>

### Isolating a chip from the system

In a multichip system, you can isolate a chip from the system.

### About this task

To isolate a chip from the system, use the following procedure:

### Procedure

1. Ensure that all cores on the chip are asleep by setting [GICR\_WAKER](https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Redistributor-registers-for-control-and-physical-LPIs-summary/GICR-WAKER--Power-Management-Control-Register?lang=en "This register controls whether the GIC-720AE can be powered down.").ProcessorSleep.
2. Ensure all ITS blocks on the chip are disabled and the buses are quiesced by using the qreqn\_its<n> Q-Channel interfaces.

   Before isolating the chip, the ITSs must be powered off because the Routing table is invalid when the GIC P-Channel is in the OFF state.
3. Ensure that LPIs from other chips are not routed to this chip.
4. Attempt to enter the CONFIG state (pstate signal = 0x9).

   If the GIC is idle and all credits are returned, it accepts the request to go into CONFIG state, otherwise it denies the request and remains in RUN state.
   > ### Note
   >
   > All SPIs must return to their own chip before a request is accepted. This means that SPIs that are enabled and pending, but targeting a core on a remote chip where the relevant CPU group is disabled, prevent transition into the CONFIG state.

   When in the CONFIG state, any cross-chip messages that change the internal state are held in the cross-chip interface, and all messages assert the
   pactive signal. If the
   pactive signal asserts while attempting to enter a lower power state, you must return to RUN (
   pstate signal ==
   0x0).
5. When in CONFIG state, any required state can be saved.

   Writing to
   [GICD\_CHIPRn](https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-CHIPR-n---Chip-Registers?lang=en "Each register controls the configuration of the chip in a multichip system. This register exists on each chip in a multichip configuration and is identified by the chip number.") or
   [GICD\_DCHIPR](https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-DCHIPR--Default-Chip-Register?lang=en "This register allows Secure software to access the status of a chip in a multichip system. A single copy of this register exists on each chip in a multichip configuration.") for any purpose other than to restore saved values after a hardware reset is unpredictable.
6. If using GICv4.1, then software must write and poll the [GICR\_VINVCHIPR](https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/vLPI-register-summary/GICR-VINVCHIPR--vPE-Invalidate-Chip-Register?lang=en "This register can invalidate the vICM RAM in selected chips.") register on at least one PE from all the other chips. This check ensures that no stale cached vPE routing information exists that would unnecessarily wake the chip that is being powered down.
7. Power down the Redistributors using the [GICR\_PWRR](https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Redistributor-registers-for-control-and-physical-LPIs-summary/GICR-PWRR--Power-Register?lang=en "This register controls the powerup sequence of the Redistributors. Software must write to this register during the powerup sequence.") registers.
8. **Optional:** Flush the LPI cache using [GICR\_WAKER](https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Redistributor-registers-for-control-and-physical-LPIs-summary/GICR-WAKER--Power-Management-Control-Register?lang=en "This register controls whether the GIC-720AE can be powered down.").Sleep.

   We recommend that if wake-on-interrupt is required, LPIs from other chips do not target this chip while the chip is being powered down (step
   [3](https://developer.arm.com/documentation/102666/0201/Getting-started-with-GIC-720AE/Isolating-a-chip-from-the-system?lang=en#mby1502100160744__step_3)). Also, LPIs from other chips must be routed back while the chip is in the OFF state.

   If LPIs arrive after sleep is set in the CONFIG state, then the LPIs are dropped.
9. Attempt to enter the OFF state.

   If the
   pactive signal is HIGH, return to the CONFIG state.
10. Use the Q-Channel to put the GIC into a safe mode to reset.

    If the SPI Collator is in a different domain to the Distributor and only one of the domains is being reset, then the power Q-Channel must have also accepted before the reset can occur. This might require masking interrupts outside of the GIC to ensure that all interrupt lines have reached their idle state.

    Power up is the reverse of the powerdown sequence. However, you must ensure that the Routing table is restored before other registers, else the behavior is unpredictable. If CRC protection is enabled on the cross-chip interface, use the following restore process:
    1. Program [GICD\_DCHIPR](https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-DCHIPR--Default-Chip-Register?lang=en "This register allows Secure software to access the status of a chip in a multichip system. A single copy of this register exists on each chip in a multichip configuration.").rt\_owner to the chip\_id of the chip to restore.
    2. Restore all [GICD\_CHIPRn](https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-CHIPR-n---Chip-Registers?lang=en "Each register controls the configuration of the chip in a multichip system. This register exists on each chip in a multichip configuration and is identified by the chip number.") registers to their previous saved values.
    3. Program [GICD\_DCHIPR](https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-DCHIPR--Default-Chip-Register?lang=en "This register allows Secure software to access the status of a chip in a multichip system. A single copy of this register exists on each chip in a multichip configuration.").rt\_owner to its previous saved value.Restoring values to the Routing table that are not exactly the same as those values read out before a reset, can cause unpredictable behavior.
    > ### Note
    >
    > Accesses to
    > [GICD\_CTLR](https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-CTLR--Distributor-Control-Register?lang=en "This register enables interrupts for Group 0 and Group 1. It also indicates whether the Distributor supports 1 or 2 security states, and whether a register write is in progress.") continue to be broadcast to the isolated chip, which requests wakeup.

### Related reference

- [Power control and P-Channel](https://developer.arm.com/documentation/102666/0201/Operation-of-GIC-720AE/Power-management/Power-control-and-P-Channel?lang=en "You can use the P-Channel to isolate a chip from the system.")
