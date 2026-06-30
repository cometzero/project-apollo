# Distributor Q-Channels

Source: <https://developer.arm.com/documentation/102666/0201/Components-in-GIC-720AE/Distributor--GICD-/Distributor-Q-Channels>

### Distributor Q-Channels

There is a single Q-Channel for clock gating the GIC-720AE Distributor. The Q-Channel interface denies access when the Distributor is busy processing interrupts.

The Distributor also has a separate Q-Channel that enables power control for each configured ITS. The GIC only accepts a low-power request when GITS\_CTLR.Quiescent is set. If the Quiescent bit is set, the Q-Channel qacceptn\_its\_<n> signal is asserted, and the GIC guarantees that the bus to the relevant ITS is idle in both directions and that the ITS can be powered down. To perform wake-on-LPI functionality, you can use [GITS\_FCTLR](https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/ITS-control-register-summary/GITS-FCTLR--Function-Control-Register?lang=en "This register controls many functions in the ITS such as cache invalidation, clock gating, and the scrubbing of all RAMs. The register is not distributed and only acts on the local chip.").PWE to disable the bus while the ITS is still active and able to translate interrupts. If the bus is disabled, then when the qactive\_gicd signal asserts on the corresponding ITS, the system must re-enable the bus and program the GICD so that it is ready to receive LPIs. The system must route the qactive\_gicd signal to a power controller that implements the following sequence:

1. Power up the GICD.
2. Restore the GICD program state.
3. Turn on the associated ITS Q-Channel on the GICD, which allows the ITS to proceed.

The qreqn\* signals are synchronized internally, and can be driven asynchronously.

As the qactive output signal includes combinatorial and asynchronous inputs, then you must consider qactive as an asynchronous output.

For more information, see the [AMBA® Low Power Interface Specification](https://developer.arm.com/documentation/ihi0068/d).
