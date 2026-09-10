# Command linking

Source: <https://developer.arm.com/documentation/102482/0000/DMAC-operation/Command-linking>

### Command linking

The command linking feature enables the DMA channels to execute more operations by automatically loading the next commands from the system memory to its configuration registers. This feature makes the DMAC versatile in combining multiple commands in a DMAC transaction.

Each command can define new transfer parameters, triggering behavior, and interrupt settings. This provides great flexibility in the possible usage of the DMA unit and makes it possible to implement complex data transfer tasks by properly designing command chains. The commands are defined by descriptors stored in memory. The channel fetches the descriptors by using the pointer address stored in the link register (LINKADDR). The first command must be set directly in the channel registers to start the linked command chain. If required, the first command can be an empty command which only points to a memory location with the first non-empty command.

Certain commands might only change some of the configuration registers, for example, the destination address or the number of transfers, but keep all other registers the same for the next command. To do this, the command descriptors in the memory have a header part that specifies what registers to update in the channel register bank. This reduces the number of bus transfers executed during command fetching.

The command link chain finishes when a command in the chain does not have the LINKADDREN bit set. This can be achieved by not setting this LINKADDR register bit in the descriptor of the last command in the chain.

The new command is fetched after the DONE state when a command is finished, see [Channel lifecycle](/documentation/102482/0000/DMAC-operation/DMA-Channel-lifecycle?lang=en "The operation of a DMA channel is shown in the following figure:"). The register values are read and updated according to the header word.

Execution of a command chain can be stopped by setting the DISABLECMD bit in the channel command register (CH<x>\_CMD). It can be used to stop an endless looped command link. The disable stops the command chain cleanly; the command being executed currently is finished but the next one is not loaded.

When a command in a command link is paused it behaves just like pausing a single command, see [Stop and pause control](/documentation/102482/0000/DMAC-interfaces/Control-and-status-interface/Stop-and-pause-control?lang=en "The allch_stop signals can be used to stop the operation of all the active channels of the DMAC by an external hardware unit. The stop function can be useful when dealing with error scenarios in the system and immediate action must clear the DMAC tasks."). After resuming, the execution of the command is resumed and the command link is continued.

When a command in the command link stopped, the remaining part of the command and the remaining part of the command link are canceled. The stop waits for all the outstanding responses from read and write transactions but it tries to finish the channel operation as soon as possible. For more information, see [Stop and pause control](/documentation/102482/0000/DMAC-interfaces/Control-and-status-interface/Stop-and-pause-control?lang=en "The allch_stop signals can be used to stop the operation of all the active channels of the DMAC by an external hardware unit. The stop function can be useful when dealing with error scenarios in the system and immediate action must clear the DMAC tasks.").

- **[Command structure](/documentation/102482/0000/DMAC-operation/Command-linking/Command-structure?lang=en)**
   The commands are stored in the system memory within a linked list data structure. Each command has information on what DMA channel configuration registers must be updated and a pointer to the next command.
- **[Loading commands](/documentation/102482/0000/DMAC-operation/Command-linking/Loading-commands?lang=en)**
   The command linking feature loads commands from the system memory using the same AXI bus manager interfaces that are used for data transferring.
- **[Automatic boot feature](/documentation/102482/0000/DMAC-operation/Command-linking/Automatic-boot-feature?lang=en)**
   The DMA unit implements an automatic boot feature called autoboot to speed up the bootup of the system. The autoboot can load the first DMA command into channel 0 and start executing it. Autoboot is implemented with the command-link feature and it can be configured with dedicated input signals.
