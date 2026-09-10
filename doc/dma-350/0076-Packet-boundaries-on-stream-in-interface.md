# Packet boundaries on stream in interface

Source: <https://developer.arm.com/documentation/102482/0000/DMAC-operation/AXI4-stream-operation/Packet-boundaries-on-stream-in-interface>

### Packet boundaries on stream in interface

The stream in interface expects a single packet for the whole DMA command. When the tlast is received from the external engine, it means that it has no more data to receive and the DMA command is finished.

When tlast is received while DESXSIZE or DESYSIZE is greater than 0, the command is finished and no more transfers are to be generated on the destination side when using the continue option after the data with tlast is sent out. This can be considered as a use case for compression, when an upper limit is set for the destination area but the compression resulted in less data for the destination side than originally expected. The fill settings add the FILLVALUE to the remaining area until the DESXSIZE is reduced to 0 for 1D transfers. For 2D transfers, the fill can only be set for YTYPE as the single-line width is not known and so XTYPE fill results in an error.

> ### Note
>
> The size of last beat must be TRANSIZE aligned, otherwise the AXI5 write side cannot process the data. If not, stream in error is generated and the DMAC job is stopped. TRANSIZE must be carefully chosen, which ultimately depends on the algorithm type running on the external stream engine. If it produces less outgoing data, then the question is how much less it can be. The smallest possible granularity should be the TRANSIZE.

When DESXSIZE and DESYSIZE are reduced to 0 without receiving tlast, the command stops sending out more data on AXI. This is considered a programming fault because the DMAC expected to finish the transfer earlier than it should. This is indicated to SW by asserting an error. The channel still receives but drops incoming stream in transfers until the tlast is received or the interface is reset.

### Stream in flush behavior

The FLUSH output signal is asserted when the DMA command must finish its operation before receiving a tlast on the stream in interface. This shows that the DMAC discards all data received with a TVALID/TREADY handshake while the FLUSH is asserted. The FLUSH is asserted until a TVALID / TREADY handshake is received on the stream in interface where tlast is also asserted. The DMA command cannot conclude until FLUSH is asserted.
