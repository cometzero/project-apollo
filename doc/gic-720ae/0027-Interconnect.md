# Interconnect

Source: <https://developer.arm.com/documentation/102666/0201/Components-in-GIC-720AE/Interconnect>

### Interconnect

The GIC-720AE uses AXI5-Stream interfaces for communication between some blocks.

These blocks are:

- Distributor to, and from, ITS
- Distributor to, and from, Redistributors
- Distributor to Distributor for cross-chip communications
- Distributor to, and from, an SPI Collator
- Distributor to the Wake Request block

All these interfaces use fully credited schemes where all messages are guaranteed to be accepted without dependency on any other port.

Apart from the cross-chip communications, GIC-720AE provides an AXI5-Stream interconnect for transporting messages. However, messages can be sent over an existing interconnect provided the interconnect is free-flowing.
