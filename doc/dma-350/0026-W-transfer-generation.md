# W transfer generation

Source: <https://developer.arm.com/documentation/102482/0000/DMAC-interfaces/AXI5-manager-interfaces/W-transfer-generation>

### W transfer generation

The WDATA is sent on the bus at the same time or after the AW channel transfer. The WDATA does not overtake the AW control information as it adds complexity to the arbitration logic.

Strobe signals are used if the transfer size is set to less than the bus data width.
