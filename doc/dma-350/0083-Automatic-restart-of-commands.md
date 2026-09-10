# Automatic restart of commands

Source: <https://developer.arm.com/documentation/102482/0000/DMAC-operation/DMA-Channel-lifecycle/Automatic-restart-of-commands>

### Automatic restart of commands

The auto restart feature improves the efficiency when a single command must be repeated many times in a loop, by eliminating unnecessary reloading of the same command.

Auto restart can be enabled by setting the CMDRESTARTINFEN or CMDRESTARTCNT fields to a nonzero value. The number of iterations depends on the settings of these fields:

- CMDRESTARTINFEN is set: The automatic restarting keeps occurring in an infinite loop until the channel is disabled or stopped.
- CMDRESTARTINFEN is not set: The automatic restarting occurs for the number of times that is configured in CMDRESTARTCNT field. If it is configured to zero, the auto restart feature is not enabled.

If the auto restart feature is enabled, the destination and source addresses and the transfer size settings are reloaded with their original value depending on the setting of the REGRELOADTYPE field. If an address is not reloaded, the starting address of the next iteration of command execution is defined based on the operation type.
