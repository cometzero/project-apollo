# CPU Reset Handling

Source: <https://developer.arm.com/documentation/102803/latest/Functional-Description/Reset-infrastructure/CPU-Reset-Handling>

### CPU Reset Handling

Each CPU<n>’s nPORESET reset input is driven by the PPU that controls each CPU Core power domain, PD\_CPU<n>. This PPU itself is reset using nCOLDRESETMGMT.

A Warm reset mode is driven from Warm Reset Generation logic that resides in the PD\_AON domain. This, along with all PPUs in the system, is used to force the system to idle before driving Warm reset which includes the CPU<n>’s nSYSRESET input. The nSYSRESET signal of each CPU is generated when the system enters WARM\_RST state, ensuring the logic in PD\_CPU<n> power domain is quiescent when that occurs.

If the reset is the result of a Cold reset request from the nSRST input, after a momentary Cold reset, CPUWAIT input of all CPUs is forced HIGH as long as nSRST is held LOW to stop the processor from starting execution until nSRST is released. This allows a debugger to hold the CPU core from execution after reset while it uses the Debug Access Port to perform debug operations.

- **[Boot after reset](/documentation/102803/0000/Functional-Description/Reset-infrastructure/CPU-Reset-Handling/Boot-after-reset?lang=en)**
   After resets, including power-on reset, all processors boot using the values defined in the Initial Secure Reset Vector Registers [INITSVTOR<n>](/documentation/102803/0000/Programmers-model/System-Control-Peripheral-Region/System-Control-Register-Block/INITSVTOR-n-?lang=en "The INITSVTOR<n> register is used to define the CPU <n> Initial Secure Vector table offset (VTOR_S.TBLOFF[31:7]) out of reset.") in the System Control Registers as the boot address.
