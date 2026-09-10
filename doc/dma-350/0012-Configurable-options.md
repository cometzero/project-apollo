# Configurable options

Source: <https://developer.arm.com/documentation/102482/0000/DMA-350-overview/Configurable-options>

### Configurable options

The DMA-350 can be configured with the following options to meet specific design requirements:

> ### Note
>
> The parentheses contain the relevant configuration parameter. These are described in the Arm® CoreLink™ DMA-350 Controller Configuration and Integration Manual.

- AXI5 address width 32-bit or 64-bit (ADDR\_WIDTH)
- AXI5 data width of 32-bit, 64-bit, or 128-bit (DATA\_WIDTH)
- Channel identification register width between 0-bit and 16-bit (CHID\_WIDTH)
- General Purpose Output (GPO) width of the channels between 0-bit and 32-bit (GPO\_WIDTH)
- GPO support of a channel (CH\_GPO\_MASK)
- Stream support of a channel (CH\_STREAM\_MASK)
- FIFO depth of every channel separately to 1,2,4,8,16,32,64 (CH\_<N>\_FIFO\_DEPTH)
- Extended feature support (2D, wrapping, template) of a channel(CH\_EXT\_FEAT\_MASK)
- Number of DMA channels between 1 and 8 (NUM\_CHANNELS)
- Number of trigger input ports between 0 and 32 (NUM\_TRIGGER\_IN)
- Number of trigger output ports between 0 and 32 (NUM\_TRIGGER\_OUT)
- Trigger input port synchronization (TRIG\_IN\_SYNC\_EN\_MASK)
- Trigger output port synchronization (TRIG\_OUT\_SYNC\_EN\_MASK)
- Presence of secondary AXI5 manager port (AXI5\_M1\_PRESENT)
- Presence of Security Extension for TrustZone® support (SECEXT\_PRESENT)
