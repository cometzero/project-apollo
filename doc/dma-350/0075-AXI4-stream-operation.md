# AXI4 stream operation

Source: <https://developer.arm.com/documentation/102482/0000/DMAC-operation/AXI4-stream-operation>

### AXI4 stream operation

To offer flexible data manipulation, the DMA-350 can include an external engine in the dataflow. The data read by the AXI5 manager interface can be sent out through the AXI4 stream interface to, for example, a filter unit. The unit sends back the corrected data to the DMAC and the DMAC writes the modified data to memory through the AXI5.

- **[Packet boundaries on stream in interface](/documentation/102482/0000/DMAC-operation/AXI4-stream-operation/Packet-boundaries-on-stream-in-interface?lang=en)**
   The stream in interface expects a single packet for the whole DMA command. When the tlast is received from the external engine, it means that it has no more data to receive and the DMA command is finished.
- **[Packet boundaries on stream out interface](/documentation/102482/0000/DMAC-operation/AXI4-stream-operation/Packet-boundaries-on-stream-out-interface?lang=en)**
   The stream out interface sends a single packet in AXI4 stream terms to the external engine for the whole DMA command. This packet can contain multiple transfers (beats). Since the interface does not have TID, all transfers are within one packet.
- **[Stream interworking with other modes](/documentation/102482/0000/DMAC-operation/AXI4-stream-operation/Stream-interworking-with-other-modes?lang=en)**
   The operation of the stream interface can be enabled in parallel with other features of the DMAC. However, some restrictions apply when using the stream interface for the command.
