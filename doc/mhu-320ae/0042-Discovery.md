# Discovery

Source: <https://developer.arm.com/documentation/107612/0001/Programmers-model-for-MHU-320AE/Discovery>

### Discovery

Discovery is an algorithm that software can use to determine the structure of the MHU-320AE configuration as the system boots. Therefore, software can determine the structure of the MHU-320AE domains, components, and subfeatures without previous knowledge of the configuration.

To build the discovery tree, the discovery process starts at the base address of the configuration space. We recommend that the operating system is provided with pointers to the start of the MHU Sender and MHU Receiver memory maps. Then discovery uses pointer values to determine the number and type of each component, their attributes, and the location of the configuration registers. Software can use this information to access these registers for configuration purposes. For more information, see [Discovery flow](/documentation/107612/0001/Programmers-model-for-MHU-320AE/Discovery/Discovery-flow?lang=en "To verify that the pages relate to MHU-320AE registers, software can check these pointers against the discovery registers, which start at offset 0x0FD0 for each MHU page. These registers allow discovery of the MHU-320AE version as well as information whether the page contains MHU or FMU registers.").
