# Setting error recovery and fault handling options

Source: <https://developer.arm.com/documentation/102666/0201/Getting-started-with-GIC-720AE/Setting-error-recovery-and-fault-handling-options>

### Setting error recovery and fault handling options

Use the following procedures to set the error recovery and fault handling option.

### About this task

### Procedure

1. Write to [GICT\_ERR<n>MISC0](https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/GICT-register-summary/GICT-ERR-n-MISC0--Error-Record-Miscellaneous-Register-0?lang=en "This register contains the corrected error counter and information that assists with identifying the RAM in which the error was detected.").Count to preset the counter to any value.

   For example, to fire an interrupt on any correctable error, write
   0xFF, or to fire an interrupt on every second correctable error, write
   0xFE.
2. Assign a recorded uncorrectable ECC error to one of these options:
   - The fault-handling interrupt, fault\_int signal, by setting [GICT\_ERR<n>CTLR](https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/GICT-register-summary/GICT-ERR-n-CTLR--Error-Record-Control-Register?lang=en "This register controls how interrupts are handled.").FI.
   - The error recovery interrupt, err\_int signal, by setting [GICT\_ERR<n>CTLR](https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/GICT-register-summary/GICT-ERR-n-CTLR--Error-Record-Control-Register?lang=en "This register controls how interrupts are handled.").UI. The interrupt fires on every uncorrectable interrupt occurrence irrespective of the counter value.

   We recommend that if the
   err\_int and
   fault\_int signals are internally routed, the target interrupts must not have SPI
   Collator wires, or if they are present, are tied off. This prevents software checking for the same ID at multiple destinations. The
   err\_int and
   fault\_int signals do not have direct test enable registers. You can test connectivity using error record 0 and triggering an error, such as an illegal AXI access to a nonexistent register.
3. Route the fault\_int and err\_int output signals as either:
   - Interrupt wires for situations where error recovery is handled by a core that does not receive interrupts directly from the GIC, such as a central system control processor.
   - Drive each interrupt internally by programming the associated [GICT\_ERRIRQCR<n>](https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/GICT-register-summary/GICT-ERRIRQCR-n---Error-Interrupt-Configuration-Registers?lang=en "GICT_ERRIRQCR0 controls which SPI is generated when a fault handling interrupt occurs. GICT_ERRIRQCR1 controls which SPI is generated when an error recovery interrupt occurs.") register. Each [GICT\_ERRIRQCR<n>](https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/GICT-register-summary/GICT-ERRIRQCR-n---Error-Interrupt-Configuration-Registers?lang=en "GICT_ERRIRQCR0 controls which SPI is generated when a fault handling interrupt occurs. GICT_ERRIRQCR1 controls which SPI is generated when an error recovery interrupt occurs.") register contains an ID field that must be programmed to 0 if internal routing is not required, or if internal routing is required, to a legally supported SPI ID.
     > ### Note
     >
     > If the programmed ID value is less than 32, out of range, or not owned on chip for multichip configurations, the register updates to 0 and no internal delivery occurs.
