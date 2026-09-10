# ID generation

Source: <https://developer.arm.com/documentation/102482/0000/DMAC-interfaces/AXI5-manager-interfaces/ID-generation>

### ID generation

The AxID generation is automatically done by the DMAC on channel basis. Read and write transfers use an AxID that identifies the channel. The command linking also uses the channel’s own ID for fetching the commands from memory but with an extra sideband signal indicating the command access. SW-based channel ID setting can be added by using the CHID registers to aid memory mapping outside the DMAC. These registers are present on the bus as User signals, the DMAC does not use them internally.
