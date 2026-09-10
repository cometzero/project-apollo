# Stream interworking with other modes

Source: <https://developer.arm.com/documentation/102482/0000/DMAC-operation/AXI4-stream-operation/Stream-interworking-with-other-modes>

### Stream interworking with other modes

The operation of the stream interface can be enabled in parallel with other features of the DMAC. However, some restrictions apply when using the stream interface for the command.

- **[Interworking with 1D and 2D types](/documentation/102482/0000/DMAC-operation/AXI4-stream-operation/Stream-interworking-with-other-modes/Interworking-with-1D-and-2D-types?lang=en)**
   The 1D and 2D modes the XTYPE and YTYPE settings are constrained when using stream interface. This constriction is because the stream interface cannot use wrap modes and fill in some cases. The following table summarizes the allowed configuration settings:
- **[Interworking with Trigger Interface](/documentation/102482/0000/DMAC-operation/AXI4-stream-operation/Stream-interworking-with-other-modes/Interworking-with-Trigger-Interface?lang=en)**
   The stream interface usage has some restrictions on the trigger input interface as the block-based transfers might behave improperly when converting them to stream output transfers.
