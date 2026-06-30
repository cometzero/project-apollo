# Lock and key mechanism

Source: <https://developer.arm.com/documentation/107612/0001/Functional-safety-features-of-MHU-320AE/Fault-management-unit/Lock-and-key-mechanism>

### Lock and key mechanism

The FMU registers are protected against inadvertent writes by a lock and key mechanism.

The FMU registers are in a locked state after reset. If the register file is locked, then any write access to any register other than the FMU\_KEY register is ignored.

The register file is unlocked when a write to FMU\_KEY occurs that satisfies all of the following conditions:

- Is Secure.
- Is for 32 bits. That is, all write strobes are set.
- The bottom 8 bits are 0xBE.

The register file is locked again when a write occurs that satisfies all of the following conditions:

- Is a Secure write.
- Is any width and any write strobes.
- Write to any register except for FMU\_KEY.
- The write is not to the upper 32-bits of the 64-bit RAS registers, FMU\_ERR<n>CTLR and FMU\_ERR<n>STATUS

After a write to FMU\_KEY successfully unlocks the register file, if the next access writes to FMU\_KEY and:

- Does not satisfy the unlock requirements, then the register file locks.
- Satisfies the unlock requirements, then the register file remains unlocked.

If the register file is unlocked, then FMU\_KEY reads as 0x000000BE. Otherwise, FMU\_KEY reads as 0x00000000.

Non-secure accesses never succeed and never affect the locked state of the register file.

### Accessing 64-bit FMU registers

Some of the FMU registers are 64-bit registers, but the APB interface width is 32 bits. When in unlocked state, the FMU allows for two consecutive writes, in any order, to update the same 64- bit register without requiring unlocking again before the second write. In this sequence, the Secure write to the upper 32 bits of the 64-bit register does not lock the FMU key, so the upper 32-bit write can either occur first or second.

For example, the following sequence is successful in updating the register contents:

1. Secure write of 0xBE to FMU\_KEY, with all write strobes asserted.
2. 32-bit Secure write to FMU\_ERR0CTLR[63:32] at address offset 0x0C, all write strobes asserted.
3. 32-bit Secure write to FMU\_ERR0CTLR[31:0] at address offset 0x08, all write strobes asserted.

This behavior is permitted to allow for the case when the APB interconnect splits a single 64-bit register access and presents it to the FMU in any order.
