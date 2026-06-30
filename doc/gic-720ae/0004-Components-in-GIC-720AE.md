# Components in GIC-720AE

Source: <https://developer.arm.com/documentation/102666/0201/Components-in-GIC-720AE>

### Components in GIC-720AE

The GIC-720AE contains several major components that use an internal GIC interconnect to route the AXI5-Stream interfaces between the different components. A configuration parameter controls the hierarchy of the GIC components.

The components are:

- Distributor
- GIC Cluster Interface (GCI)
- Interrupt Translation Service (ITS)
- MSI-64 Encapsulator
- SPI Collator
- Wake Request
- GIC interconnect

Each component is configurable so that it can be modified for the system requirements.

The hierarchy of the GIC components can be a single combined block that uses a dedicated 16-bit or 64-bit AXI5-Stream interconnect, or a set of individual blocks that are interconnected using your own transport layer.
