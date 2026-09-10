# General purpose outputs

Source: <https://developer.arm.com/documentation/102482/0000/DMAC-interfaces/Control-and-status-interface/General-purpose-outputs>

### General purpose outputs

The General Purpose Output (GPO) ports provide extra bits that you can set to a stable value throughout a DMAC operation.

You can use the GPO ports for multiple purposes:

- Selecting memory banks
- Indicating a channel operation on a debug pin
- Controlling the external data manipulation engine, and more.

GPOs are driven per channel so each channel has its own ports.

The value of the GPO is SW controlled. The value on the output becomes active when the ENABLE register bit is set and remains stable while the DMA channel is active. The GPO stays on the last value set by the command when the channel stops driving the GPO.

> ### Note
>
> The GPO can be set back to the initial value by running an empty command that selects all GPOs and clears them to 0.
