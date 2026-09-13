# AXI configurations

Source: <https://developer.arm.com/documentation/107721/0001/AXI-manager-interface/AXI-configurations>

### AXI configurations

The AXI manager interface of the DynamIQ Shared Unit-120AE (DSU-120AE) by default supports the AXI5 protocol but you can configure it to support the AXI4 protocol.

To make the AXI manager interface compliant with AXI4, tie the signals BROADCASTMTE and BROADCASTATOMIC LOW.
