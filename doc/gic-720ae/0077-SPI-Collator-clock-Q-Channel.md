# SPI Collator clock Q-Channel

Source: <https://developer.arm.com/documentation/102666/0201/Components-in-GIC-720AE/SPI-Collator/SPI-Collator-clock-Q-Channel>

### SPI Collator clock Q-Channel

The SPI Collator has a clock Q-Channel interface that accepts requests from an external clock gating source, such as the system clock controller.

When the qactive\_col\_clk signal is LOW, it indicates that all SPI toggles and level transitions have been passed to the Distributor, and that the SPI Collator does not require the clock.

If the qactive\_col\_clk signal is HIGH, the SPI Collator rejects any attempt to enter a low-power mode.

If the qreqn\_col\_clk signal is LOW and is accepted, the SPI Collator enters low-power mode and no new messages are sent to the Distributor until it enters low-power mode. If any interrupt line changes state, the qactive\_col\_clk signal is asserted.

In low-power mode, it is only safe to stop the SPI Collator clock if all edge-triggered interrupts into the SPI Collator are pulse extended so that edges are not missed.
