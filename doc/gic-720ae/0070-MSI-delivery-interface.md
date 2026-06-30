# MSI delivery interface

Source: <https://developer.arm.com/documentation/102666/0201/Components-in-GIC-720AE/Interrupt-Translation-Service/MSI-delivery-interface>

### MSI delivery interface

The MSI delivery interface is a bidirectional AXI5-Stream interface for passing MSIs to an ITS for translation.

The data format on the msitdata signal is {DeviceID[31:0], EventID[31:0]}.

When the ITS accepts the request, it sets the msirtvalid signal HIGH.

The GIC decodes the entire 32 bits of DeviceID and EventID. Bits above the configured widths must be zero, otherwise the GIC generates out-of-range errors and the expected translation does not occur.

The msitid signal value that the ITS receives, is sent out on the msirtdest signal. This behavior enables multiple sources to connect to the ITS using a standard AXI5-Stream infrastructure.

The MSI delivery interface can apply back pressure if the ITS or Distributor resources become busy, and can be dependent on the Distributor ACE-Lite manager interface, for both reads and writes.
