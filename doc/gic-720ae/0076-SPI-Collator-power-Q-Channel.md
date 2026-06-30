# SPI Collator power Q-Channel

Source: <https://developer.arm.com/documentation/102666/0201/Components-in-GIC-720AE/SPI-Collator/SPI-Collator-power-Q-Channel>

### SPI Collator power Q-Channel

The SPI Collator has a power Q-Channel interface that accepts requests from an external source, such as the system power controller.

When the qactive\_col signal is LOW, it indicates that all SPIs to the SPI Collator are in their idle state of either 0 (active-HIGH) or 1 (active-LOW), so all messages are sent to the Distributor.

If the qactive\_col signal is HIGH, the SPI Collator rejects any attempt to enter a low-power mode.

If the qreqn\_col signal is LOW and is accepted, the SPI Collator enters low-power mode and the AXI5-Stream channels to the Distributor are flushed out to ensure that there are no messages in progress. When accepted, you can reset the SPI Collator safely without having to also reset the Distributor. You can also reset the Distributor, but you must first complete the instructions that are described in the subsections of section [Power management](https://developer.arm.com/documentation/102666/0201/Operation-of-GIC-720AE/Power-management?lang=en "The GIC-720AE can be powered down by the system power controller. The GIC also supports the power controller powering down the cores that the GIC services. The GICR_WAKER and the GICR_PWRR registers provide bits to control functions that are associated with power management.") before the Distributor can be powered down.

When the SPI Collator and Distributor are both in the same domain, the power Q-Channel interface is redundant and can be tied off.

In low-power mode, it is only safe to stop the SPI Collator clock if all edge-triggered interrupts into the SPI Collator are pulse extended so that edges are not missed.
