# Packet boundaries on stream out interface

Source: <https://developer.arm.com/documentation/102482/0000/DMAC-operation/AXI4-stream-operation/Packet-boundaries-on-stream-out-interface>

### Packet boundaries on stream out interface

The stream out interface sends a single packet in AXI4 stream terms to the external engine for the whole DMA command. This packet can contain multiple transfers (beats). Since the interface does not have TID, all transfers are within one packet.
