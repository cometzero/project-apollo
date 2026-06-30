# Other power management

Source: <https://developer.arm.com/documentation/102666/0201/Getting-started-with-GIC-720AE/Other-power-management>

### Other power management

The GIC-720AE can be powered up and powered down using non-architectural protocols.

When powering up GIC-720AE, then software must program registers in the following sequence:

1. If using programmable core removal, program [GICD\_RDOFFRn](https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-RDOFFR-n---Redistributor-Off-Registers?lang=en "Each register allows Secure software to remove up to 64 cores from the GIC.") and then [GICR\_MPIDR](https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Redistributor-registers-for-control-and-physical-LPIs-summary/GICR-MPIDR--MPIDR-Register?lang=en "This register allows Secure software to write the affinity values of a Redistributor.").
2. If using multi view, program [GICR\_VIEWR](https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Redistributor-registers-for-control-and-physical-LPIs-summary/GICR-VIEWR--View-Register?lang=en "This register controls the view that this Redistributor belongs to.").
3. Any other registers.

When powering down GIC-720AE, software must preserve the state of the GIC-720AE, except for any LPI pending interrupts that are preserved in pending tables, as defined in the [Arm® Generic Interrupt Controller Architecture Specification, GIC architecture version 3 and version 4](https://developer.arm.com/documentation/ihi0069/hb).

You can preserve the LPI pending bits by using an implementation-defined powerdown sequence, which ensures that the memory pointed to by each GICR\_PENDBASER contains the updated pending information for the LPIs. The implementation-defined powerdown sequence must:

1. Complete the powerdown sequence for all cores.
2. Set [GICR\_WAKER](https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Redistributor-registers-for-control-and-physical-LPIs-summary/GICR-WAKER--Power-Management-Control-Register?lang=en "This register controls whether the GIC-720AE can be powered down.").Sleep to 1.
3. If [GICD\_TYPER](https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-TYPER--Interrupt-Controller-Type-Register?lang=en "This register returns information about the configuration of the GIC-720AE. You can use this register to determine the number of Security states, the number of INTIDs, and the number of processor cores that the GIC supports.").LPIS==1, poll GICR\_WAKER until [GICR\_WAKER](https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Redistributor-registers-for-control-and-physical-LPIs-summary/GICR-WAKER--Power-Management-Control-Register?lang=en "This register controls whether the GIC-720AE can be powered down.").Quiescent is set.
   > ### Note
   >
   > - [GICR\_WAKER](https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Redistributor-registers-for-control-and-physical-LPIs-summary/GICR-WAKER--Power-Management-Control-Register?lang=en "This register controls whether the GIC-720AE can be powered down.").Sleep can only be set to 1 when:
   >   - All Redistributors have [GICR\_WAKER](https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Redistributor-registers-for-control-and-physical-LPIs-summary/GICR-WAKER--Power-Management-Control-Register?lang=en "This register controls whether the GIC-720AE can be powered down.").ProcessorSleep == 1.
   >   - All Redistributors have [GICR\_WAKER](https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Redistributor-registers-for-control-and-physical-LPIs-summary/GICR-WAKER--Power-Management-Control-Register?lang=en "This register controls whether the GIC-720AE can be powered down.").ChildrenAsleep == 1.
   > - [GICR\_WAKER](https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Redistributor-registers-for-control-and-physical-LPIs-summary/GICR-WAKER--Power-Management-Control-Register?lang=en "This register controls whether the GIC-720AE can be powered down.").ProcessorSleep can only be set to 0 when:
   >   - [GICR\_WAKER](https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Redistributor-registers-for-control-and-physical-LPIs-summary/GICR-WAKER--Power-Management-Control-Register?lang=en "This register controls whether the GIC-720AE can be powered down.").Sleep == 0.
   >   - [GICR\_WAKER](https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Redistributor-registers-for-control-and-physical-LPIs-summary/GICR-WAKER--Power-Management-Control-Register?lang=en "This register controls whether the GIC-720AE can be powered down.").Quiescent == 0.
   > - If software decides to abort a sleep request due to an external wake request, it can do so by clearing [GICR\_WAKER](https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Redistributor-registers-for-control-and-physical-LPIs-summary/GICR-WAKER--Power-Management-Control-Register?lang=en "This register controls whether the GIC-720AE can be powered down.").Sleep at any time. Software does not have to wait for [GICR\_WAKER](https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Redistributor-registers-for-control-and-physical-LPIs-summary/GICR-WAKER--Power-Management-Control-Register?lang=en "This register controls whether the GIC-720AE can be powered down.").Quiescent to be set.
   > - There is only one Sleep bit and one Quiescent bit, and these 2 bits can be read or written by using the [GICR\_WAKER](https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Redistributor-registers-for-control-and-physical-LPIs-summary/GICR-WAKER--Power-Management-Control-Register?lang=en "This register controls whether the GIC-720AE can be powered down.") register of any Redistributor.

The powerdown described sequence ensures that all LPIs that are acknowledged by a write response to the write GITS\_TRANSLATER are saved to the Pending tables. Any interrupt that arrives when the Sleep bit is set to 1 is ignored, and the ACE5-Lite transaction completes in accordance with the ACE protocol.

We recommend that you disable any interrupt sources before setting [GICR\_WAKER](https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Redistributor-registers-for-control-and-physical-LPIs-summary/GICR-WAKER--Power-Management-Control-Register?lang=en "This register controls whether the GIC-720AE can be powered down.").Sleep. However, if you require wake-on-interrupt behavior, the write to GITS\_TRANSLATER must be gated upstream at a location that enables software to reprogram and enable the GIC-720AE without deadlock.

When the [GICR\_WAKER](https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Redistributor-registers-for-control-and-physical-LPIs-summary/GICR-WAKER--Power-Management-Control-Register?lang=en "This register controls whether the GIC-720AE can be powered down.").Quiescent bit is set, it is safe to power down the GIC-720AE without losing LPI pending bits. Software must still perform other steps such as the save and restore of SPI state. However, you must provide custom mechanisms to wake the GIC-720AE if any interrupts arrive that must not be ignored.

When the GIC-720AE next powers up, you can program the GICR\_PENDBASER registers to point to the same memory to reload the LPI pending status. If there is no requirement to reload the pending LPIs, we recommend that you speed up the initialization of the GIC-720AE as follows:

1. Zero the Pending table.
2. Set GICR\_PENDBASER.PTZ to 1.

> ### Note
>
> GICR\_PENDBASER registers can only be modified before the
> [GICR\_CTLR](https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Redistributor-registers-for-control-and-physical-LPIs-summary/GICR-CTLR--Redistributor-Control-Register?lang=en "This register controls the operation of a Redistributor, and enables the signaling of LPIs by the Redistributor to the connected core.").EnableLPIs bit is set, or when the
> [GICR\_WAKER](https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Redistributor-registers-for-control-and-physical-LPIs-summary/GICR-WAKER--Power-Management-Control-Register?lang=en "This register controls whether the GIC-720AE can be powered down.").Sleep and
> [GICR\_WAKER](https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Redistributor-registers-for-control-and-physical-LPIs-summary/GICR-WAKER--Power-Management-Control-Register?lang=en "This register controls whether the GIC-720AE can be powered down.").Quiescent bits are both set.

For more information, see the [Learn the architecture - Generic Interrupt Controller v3 and v4, Overview](https://developer.arm.com/documentation/198123/latest).

### Related information

- [GICR\_WAKER, Power Management Control Register](https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Redistributor-registers-for-control-and-physical-LPIs-summary/GICR-WAKER--Power-Management-Control-Register?lang=en "This register controls whether the GIC-720AE can be powered down.")
