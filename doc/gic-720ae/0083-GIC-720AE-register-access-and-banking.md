# GIC-720AE register access and banking

Source: <https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Register-map-pages/GIC-720AE-register-access-and-banking>

### GIC-720AE register access and banking

The GIC-720AE uses an access and banking scheme for its registers.

For more information about the register access and banking scheme, see the [Arm® Generic Interrupt Controller Architecture Specification, GIC architecture version 3 and version 4](https://developer.arm.com/documentation/ihi0069/hb).

The key characteristics of the scheme are:

- Some registers such as the Distributor Control Register, [GICD\_CTLR](https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-CTLR--Distributor-Control-Register?lang=en "This register enables interrupts for Group 0 and Group 1. It also indicates whether the Distributor supports 1 or 2 security states, and whether a register write is in progress."), and the Redistributor Control Register, [GICR\_CTLR](https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Redistributor-registers-for-control-and-physical-LPIs-summary/GICR-CTLR--Redistributor-Control-Register?lang=en "This register controls the operation of a Redistributor, and enables the signaling of LPIs by the Redistributor to the connected core."), are banked by security that provides separate Secure and Non-secure copies of the registers. A Secure access to the address, accesses the Secure copy of the register. A Non-secure access to the address, accesses the Non-secure copy.
- Some registers, such as the Interrupt Group Registers, GICD\_IGROUPRn, are only accessible using Secure accesses.
- Non-secure accesses to registers, or parts of a register, which are only accessible to Secure accesses are Read-As-Zero and Writes Ignored (RAZ/WI).
