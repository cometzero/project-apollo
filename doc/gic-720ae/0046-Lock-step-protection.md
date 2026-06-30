# Lock-step protection

Source: <https://developer.arm.com/documentation/102666/0201/Functional-safety-in-GIC-720AE/Lock-step-protection>

### Lock-step protection

The GIC-720AE logic is protected by redundant lock-step checking.

The exceptions to this are:

- The RAMs, which are shared.
- The internal AXI5-Stream interconnect, which uses CRC for end-to-end protection.
- Real-time interrupts.

Lock-step has a temporal delay of two cycles.

The entire `noram` hierarchy is duplicated, with the comparators instanced in the block top level. The clock gate and reset synchronizers are also duplicated in the top level.

The clocking is also duplicated. To provide redundancy in the reset and clock trees, the primary and secondary logic are clocked by a separate clock and have a separate reset. In the clock tree, if a branch of the reset fails in the primary domain, then the secondary domain detects the failure. Similarly, if a branch of the reset fails in the secondary domain, then the primary domain detects the failure.

Lock-step protection is distributed into all protection mechanisms that connect to primary and secondary GIC `noram` output ports. Therefore, all outputs from the `noram` that become outputs of the GIC block, are checked using local lock-step checkers within the associated interface protection mechanism. The lock-step checking logic consists of a 2-cycle delay stage for the primary signals followed by duplicated comparators for latent fault protection. The lock-step comparison is performed per input bit in all checker instances, except for the MBIST read data checker that performs a comparison of an 8-bit CRC checksum of the incoming wide data.
