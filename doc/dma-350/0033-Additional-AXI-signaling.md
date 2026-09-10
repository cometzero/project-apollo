# Additional AXI signaling

Source: <https://developer.arm.com/documentation/102482/0000/DMAC-interfaces/AXI5-manager-interfaces/Additional-AXI-signaling>

### Additional AXI signaling

AXI supports multiple features that are optional for the DMAC to operate:

- The axsize signal is maximized by the data bus width so the MSB might not be used if 64-bit or narrower bus is driven by the DMAC.
- The axlock signals are not used as the DMAC does not generate exclusive or locked transfers.
- The axinner signal indicates inner domain cache attributes for read and write transactions.
- The axchid and axchidvalid signals indicate the software configurable channel ID.
- The arcmdlink signal indicates the current read operation is a command link read.
- The awakeup signals are driven from a register on both manager interfaces to wake the devices in the AXI data path.
- The axdomain signals add minimal ACE5-Lite compatibility.
