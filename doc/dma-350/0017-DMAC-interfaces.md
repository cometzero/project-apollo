# DMAC interfaces

Source: <https://developer.arm.com/documentation/102482/0000/DMAC-interfaces>

### DMAC interfaces

This section contains an overview of the CoreLink DMA-350 interfaces.

- **[Clock and reset](/documentation/102482/0000/DMAC-interfaces/Clock-and-reset?lang=en)**
   The DMA-350 is intended to be placed in a single clock and reset domain.
- **[APB4 subordinate interface](/documentation/102482/0000/DMAC-interfaces/APB4-subordinate-interface?lang=en)**
   The APB4 subordinate interface is for accessing the internal configuration registers of the DMA-350.
- **[AXI5 manager interfaces](/documentation/102482/0000/DMAC-interfaces/AXI5-manager-interfaces?lang=en)**
   The DMAC is an AXI5 manager that complies with AMBA AXI5 protocol with a reduced set of AXI5 features. For details on the protocol, see [AMBA® AXI and ACE Protocol Specification](https://developer.arm.com/documentation/ihi0022/).
- **[Trigger Interface](/documentation/102482/0000/DMAC-interfaces/Trigger-Interface?lang=en)**
   The Trigger Interfaces can be used to control the interaction of the DMA channel operation with other peripherals.
- **[AXI4 stream interface](/documentation/102482/0000/DMAC-interfaces/AXI4-stream-interface?lang=en)**
   Each DMA channel can have a dedicated AXI4 stream interface to enable an external engine to do manipulation on the data being transferred through the DMAC. When enabled, all the data read on the AXI is pushed out to the stream interface. The external engine is expected to do the data manipulation which can result in either consuming, keeping the same amount or even generating more data elements. After the conversion is done, the data is sent back to the DMAC on the stream in interface and it is ultimately written out on the AXI write side.
- **[LPI interfaces](/documentation/102482/0000/DMAC-interfaces/LPI-interfaces?lang=en)**
   The DMAC adds support for low-power integration through the LPI interfaces for both clock and power. The Q-Channel interface provides quiescence capability for the clock and the P-Channel interface allows power management when the DMAC is IDLE and has no activity ongoing. The DMAC can request for power and clock over activity indication signals. The DMAC either accepts or denies the power and clock controller requests based on its current internal state.
- **[DMA interrupts](/documentation/102482/0000/DMAC-interfaces/DMA-interrupts?lang=en)**
   Interrupts provide indication of internal state changes of the DMA channel and the DMA unit as well. Each channel has its own separate interrupt. One global Non-secure interrupt is always present and, in addition, one global Secure interrupt and one Secure violation interrupt also appear when TrustZone support is enabled. Interrupts are level-based signals.
- **[Control and status interface](/documentation/102482/0000/DMAC-interfaces/Control-and-status-interface?lang=en)**
   The control and status interface makes system control of the DMAC operation (stop and pause) possible and provides status information of the DMAC operation.
- **[Configuration interface](/documentation/102482/0000/DMAC-interfaces/Configuration-interface?lang=en)**
   The behavior of the DMAC can be configured through static input ports. Static input ports come from either tie-off signals or driven by configurable registers that are stable and contain a valid value when the DMAC is released from reset.
