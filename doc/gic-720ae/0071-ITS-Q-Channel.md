# ITS Q-Channel

Source: <https://developer.arm.com/documentation/102666/0201/Components-in-GIC-720AE/Interrupt-Translation-Service/ITS-Q-Channel>

### ITS Q-Channel

The ITS has a Q-Channel interface which controls requests from an external clock gating source.

If the ITS is busy, the Q-Channel interface asserts the qdeny signal to deny an external request to gate its clock. When an external request occurs, the interface requests a wakeup by asserting the qactive signal.

The qreqn input signal is synchronized to the ITS.
