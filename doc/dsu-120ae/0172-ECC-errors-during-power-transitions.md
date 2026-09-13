# ECC errors during power transitions

Source: <https://developer.arm.com/documentation/107721/0001/RAS-extension-support/ECC-errors-during-power-transitions>

### ECC errors during power transitions

If an error in a RAS register occurs while the cluster is powering down then the cluster is prevented from powering down in OFF or MEM\_RET power modes.

It is possible for Error Correcting Code (ECC) errors to occur in the RAMs during a power transition to OFF or MEM\_RET power modes. For example, this could happen during the software sequence shortly before the hardware sequence starts. Another example of where errors could occur is during the powerdown sequence when the L3 cache is cleaned and invalidated. Although these errors are reported in the RAS error record registers, once the cluster or core is powered down the RAS registers are no longer accessible.

If the RAS registers are reporting an error, the following sequence happens:

1. The RAS interrupt signals for the appropriate core or cluster are asserted. The RAS interrupt signals are n<type>ERRIRQ, n<type>FAULTIRQ, and n<type>CTITIRQ, where type can be CORE, CLUSTER, or COMPLEX. For example, nCLUSTERFAULTIRQ,  nCOREFAULTIRQ[CN:0], and nCOMPLEXFAULTIRQ[CX:0].
2. If the Power Policy Unit (PPU) is currently transitioning to an OFF or MEM\_RET power modes, then these requests to the OFF or MEM\_RET power modes are denied.
3. If the error is detected in a core RAM, then the core wakes up from the powerdown `WFI` instruction.
4. If the error is detected in the shared L2 cache of a complex after the last core in that complex has completed its powerdown sequence, then that core will wake up and start executing code from the reset vector.

The error record registers must be read and cleared before the power domain will accept the power domain request from the PPU. This can be done by either using software running on the core, or accesses through the utility bus.

For more information about numbering conventions, see [Core, complex, and processing element numbering](/documentation/107721/0001/The-DynamIQ-Shared-Unit-120AE/Core--complex--and-processing-element-numbering?lang=en "A cluster contains two or more cores. The cluster can also contain two or more complexes which can be made up of either a single core or two cores. Because certain parts of the design, such as signal names and register bit values, depend on the number of cores and complexes within the cluster, a numbering system has been created.")
