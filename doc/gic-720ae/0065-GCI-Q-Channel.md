# GCI Q-Channel

Source: <https://developer.arm.com/documentation/102666/0201/Components-in-GIC-720AE/GIC-Cluster-Interface/GCI-Q-Channel>

### GCI Q-Channel

The GCI has a single Q-Channel interface that is used to ensure that the GCI can be safely clock gated hierarchically.

If the GCI is busy, actively processing interrupts or sending messages upstream or downstream, the Q-Channel denies a quiescence request that it receives on the qreqn signal, by asserting the qdeny signal. For more information, see the [AMBA® Low Power Interface Specification](https://developer.arm.com/documentation/ihi0068/d).

The qreqn input signal is synchronized inside the GCI. The qactive signal is connected to the PPI wires directly, and must be considered as an asynchronous output.

If Q-Channels are configured to support AMBA parity, then parity is both generated and checked. Changes in qreqn are not forwarded until it observes consistency for qreqn and qreqn\_chk.
