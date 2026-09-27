# Boot after reset

Source: <https://developer.arm.com/documentation/102803/latest/Functional-Description/Reset-infrastructure/CPU-Reset-Handling/Boot-after-reset>

### Boot after reset

After resets, including power-on reset, all processors boot using the values defined in the Initial Secure Reset Vector Registers [INITSVTOR<n>](/documentation/102803/0000/Programmers-model/System-Control-Peripheral-Region/System-Control-Register-Block/INITSVTOR-n-?lang=en "The INITSVTOR<n> register is used to define the CPU <n> Initial Secure Vector table offset (VTOR_S.TBLOFF[31:7]) out of reset.") in the System Control Registers as the boot address.

The default address is IMPLEMENTATION DEFINED, but we recommend that the default is set to 0x0100\_0000 which is mapped to code memory through the Manager Code Main Expansion Interface. These addresses can be modified by software before subsequent warm reboots of the processors.

The TrustZone for Armv8-M states that boot must start from a Secure memory space. At boot, all Volatile Memory is Secure only. Software must change or restore the settings in the MPC to release memory for Non-secure world use.

The CPUWAIT input to each core can force each processor to wait before executing the instruction. Each CPU in the system has an associated CPU<n>WAIT register that controls if it starts running its boot code when it wakes. There is also a CPU<n>WAITCLR input for each CPU<n> to allow an external entity to clear the associated CPU<n>WAIT register bit.

For more information, see [CPUWAIT](/documentation/102803/0000/Programmers-model/System-Control-Peripheral-Region/System-Control-Register-Block/CPUWAIT?lang=en "The CPUWAIT register provides controls to force each CPU to wait after reset rather than Boot Immediately. This allows another entity in the expansion system or the debugger to access the system prior to the CPU booting.").
