# AXI4 stream interface

Source: <https://developer.arm.com/documentation/102482/0000/DMAC-interfaces/AXI4-stream-interface>

### AXI4 stream interface

Each DMA channel can have a dedicated AXI4 stream interface to enable an external engine to do manipulation on the data being transferred through the DMAC. When enabled, all the data read on the AXI is pushed out to the stream interface. The external engine is expected to do the data manipulation which can result in either consuming, keeping the same amount or even generating more data elements. After the conversion is done, the data is sent back to the DMAC on the stream in interface and it is ultimately written out on the AXI write side.

The stream interface is expected to be simply connected to the external engine so no interconnect related sideband signals or null transfers are expected. The stream interface complies with the [AMBA® AXI-Stream Protocol Specification](https://developer.arm.com/documentation/ihi0051/) and uses a reduced set of AXI4 stream signals that are necessary for the data transfers.

### Limitations and extensions

The interface data width matches the AXI read and write channel data width, which means that conversion can be done outside the DMAC.

The stream interface also supports continuous aligned and unaligned streams. The DMAC does not send sparse streams and they are not accepted when received from the external engine. tstrb signals must be all `f`, except when tlast is asserted, which restricts unaligned streams to only have strobes at the end.

Null bytes are not supported, the tkeep signal is not present on the interface.

An additional flush sideband output signal is present on the stream\_in interface. This signal serves as a hint to ask for a TLAST from the external engine because of early command finish.
