# LPI interfaces

Source: <https://developer.arm.com/documentation/102482/0000/DMAC-interfaces/LPI-interfaces>

### LPI interfaces

The DMAC adds support for low-power integration through the LPI interfaces for both clock and power. The Q-Channel interface provides quiescence capability for the clock and the P-Channel interface allows power management when the DMAC is IDLE and has no activity ongoing. The DMAC can request for power and clock over activity indication signals. The DMAC either accepts or denies the power and clock controller requests based on its current internal state.

- **[LPI power P-Channel](/documentation/102482/0000/DMAC-interfaces/LPI-interfaces/LPI-power-P-Channel?lang=en)**
   The power P-Channel interface is used to request power quiescence from the DMAC. A power controller drives the request while the DMAC either accepts or denies the request based on its current internal state. The DMAC can also request power for an activity over the pactive signal.
- **[LPI clock Q-Channel](/documentation/102482/0000/DMAC-interfaces/LPI-interfaces/LPI-clock-Q-Channel?lang=en)**
   The clock Q-Channel interface is used to request clock quiescence from the DMAC. A clock controller drives the request while the DMAC either accepts or denies the request based on its current internal state. The DMAC can also request clock for an activity over the qactive signal.
