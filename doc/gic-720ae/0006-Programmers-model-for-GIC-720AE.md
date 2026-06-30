# Programmers model for GIC-720AE

Source: <https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE>

### Programmers model for GIC-720AE

All the GIC-720AE registers have names that are constructed of mnemonics that indicate the logical block that the register belongs to and the register function.

The following information applies to the GIC-720AE registers:

- The GIC-720AE implements only memory-mapped registers.
- The GIC-720AE has a single base address, except for the GITS\_TRANSLATER register. The base address is not fixed and can be different for each particular system implementation.
- The offset of each register from the base address is fixed.
- Accesses to reserved or unused address locations might result in a bus error, depending on the value of [GICT\_ERR0CTLR](https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/GICT-register-summary/GICT-ERR-n-CTLR--Error-Record-Control-Register?lang=en "This register controls how interrupts are handled.").UE and [GICT\_ERR0CTLR](https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/GICT-register-summary/GICT-ERR-n-CTLR--Error-Record-Control-Register?lang=en "This register controls how interrupts are handled.").DIS\_ACE.
- Unless otherwise stated in the accompanying text:
  - Do not modify reserved register bits.
  - Ignore reserved register bits on reads.
  - A system reset or a Cold reset, resets all register bits to zero.
- The GIC-720AE ACE5-Lite subordinate interface can be 64 bits, 128 bits, 256 bits, or 512 bits wide, depending on the configuration. The [Arm® Generic Interrupt Controller Architecture Specification, GIC architecture version 3 and version 4](https://developer.arm.com/documentation/ihi0069/hb) defines the permitted sizes of access.
  > ### Note
  >
  > The
  > GIC-720AE guarantees single-copy atomicity for doubleword accesses.
- The GIC-720AE supports data only in little-endian format.
- The access types for the GIC-720AE are as follows:

  RO
  :   Read-only

  RW
  :   Read and write

  WO
  :   Write-only, reads return as
      UNKNOWN.
- Unless specified otherwise, all Secure registers are accessible by Non-secure accesses when security is disabled, that is, [GICD\_CTLR](https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-CTLR--Distributor-Control-Register?lang=en "This register enables interrupts for Group 0 and Group 1. It also indicates whether the Distributor supports 1 or 2 security states, and whether a register write is in progress.").DS == 1.
